#!/usr/bin/env python3
"""
Audit a GTPyhop example against the style guides and against itself.

Every check here answers one question: **does this example still say what it
does?** Not "is it good" - "is it consistent". A domain drifts from its own
documentation silently, because nothing executes a docstring.

Three families of check, in increasing order of what they need:

  STRUCTURE   parses domain.py only. Docstring sections, BEGIN/END markers,
              type annotations, effect tags, task-name prefixes, and the
              counts quoted in section headers. This is the style guide,
              mechanised.

  SEMANTICS   parses domain.py and problems.py together. State variables
              written but never read, or read but never written. Attributes an
              action actually assigns that its docstring's Effects section
              never mentions. [ENABLER] tags on state no precondition tests.

  BEHAVIOUR   imports the example and plans (opt-in, --plan). Every problem in
              get_problems() must plan; every problem in get_trap_problems(),
              if present, must not; and a description claiming "-> N actions"
              must be telling the truth.

Why this exists. The rikyu_hpc example was written over several sessions, and
each session left the previous session's numbers behind: section headers still
said "Actions (32)" at 38 actions, seventeen docstrings had stopped listing
state their action assigns, a retired design flag was still being written by
a_get_facility with nothing left to read it, and one scenario advertised a
17-action plan that had become 18. None of it broke a single test. All of it
was wrong, and a reader would have believed every word. The first run of this
tool on that one example reported 38 defects.

The SEMANTICS family is where the surprises are. "Written but never read" finds
retired designs still being maintained; "[ENABLER] nothing tests" finds
workflow gates that were documented as load-bearing and are not, which is worse
than an undocumented gate because it misleads.

Exemptions. Some state is legitimately written and never read - a value a tool
genuinely returns, or bookkeeping kept for state dumps. Declare those in an
`_audit.json` beside domain.py, with a reason each, and the audit will also
tell you when an exemption goes stale. See README.md.

Usage:
    python -m gtpyhop.examples.audit PATH            # one example
    python -m gtpyhop.examples.audit --all           # every bundled example
    python -m gtpyhop.examples.audit PATH --plan     # add behaviour checks
    python -m gtpyhop.examples.audit --all --summary # one line per example

Exit status is 1 if anything is reported, so it works as a pre-commit or CI
check. Modelled on tools/link_audit.py, which does the same job for links.
"""

import ast
import json
import os
import re
from collections import defaultdict

__all__ = ['audit_example', 'find_examples', 'Finding']

# Attribute-mutating method calls: state.x.append(...) writes state.x
MUTATORS = {'append', 'extend', 'update', 'pop', 'setdefault', 'clear',
            'remove', 'insert', 'add', 'discard'}

ACTION_SECTIONS = ['Class:', 'MCP_Tool:', 'Action signature:',
                   'Action parameters:', 'Action purpose:', 'Preconditions:',
                   'Effects:', 'Returns:']
METHOD_SECTIONS = ['Class:', 'Method signature:', 'Method parameters:',
                   'Method purpose:', 'Preconditions:', 'Task decomposition:',
                   'Returns:']
ACTION_MARKERS = ['Type Checking', 'State-Type Checks', 'Preconditions', 'Effects']
METHOD_MARKERS = ['Type Checking', 'State-Type Checks', 'Preconditions',
                  'Task Decomposition']
EFFECT_TAGS = ('DATA', 'ENABLER', 'EXPECTED_EFFECT')


class Finding:
    """One reported problem: a family, a location and a message."""

    def __init__(self, family, where, message):
        self.family = family
        self.where = where
        self.message = message

    def __str__(self):
        return f"[{self.family}] {self.where}: {self.message}"

    def __repr__(self):
        return f"Finding({self.family!r}, {self.where!r}, {self.message!r})"


# ---------------------------------------------------------------------------
# Shared parsing helpers
# ---------------------------------------------------------------------------

def _base_attr(node):
    """state.X, state.X[k], state.X[k][j] -> 'X'; anything else -> None."""
    while isinstance(node, ast.Subscript):
        node = node.value
    if (isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name)
            and node.value.id == 'state'):
        return node.attr
    return None


def _written_attrs(node):
    """Attributes of `state` this AST subtree truly writes."""
    written = set()
    for sub in ast.walk(node):
        targets = []
        if isinstance(sub, ast.Assign):
            targets = sub.targets
        elif isinstance(sub, (ast.AugAssign, ast.AnnAssign)):
            targets = [sub.target]
        elif isinstance(sub, ast.For):
            targets = [sub.target]
        for t in targets:
            attr = _base_attr(t)
            if attr:
                written.add(attr)
        if (isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute)
                and sub.func.attr in MUTATORS):
            attr = _base_attr(sub.func.value)
            if attr:
                written.add(attr)
    return written


def _read_attrs(node, source):
    """Attributes of `state` this subtree reads, including getattr/hasattr."""
    read = set()
    for sub in ast.walk(node):
        if (isinstance(sub, ast.Attribute) and isinstance(sub.value, ast.Name)
                and sub.value.id == 'state' and isinstance(sub.ctx, ast.Load)):
            read.add(sub.attr)
    for m in re.finditer(r"(?:getattr|hasattr)\(\s*state\s*,\s*'(\w+)'", source):
        read.add(m.group(1))
    return read


def _span_ends(tree, n_lines):
    """Map each top-level node's start line to the line before the next one.

    ast stops a function at its last statement, so a trailing '# END: ...'
    comment falls outside node.end_lineno. Every marker check would fail.
    """
    tops = [n for n in tree.body if hasattr(n, 'lineno')]
    ends = {}
    for i, node in enumerate(tops):
        ends[node.lineno] = (tops[i + 1].lineno - 1) if i + 1 < len(tops) else n_lines
    return ends


def _block(source, name):
    """Text between '# BEGIN: name' and '# END: name', or ''."""
    m = re.search(rf'# BEGIN: {re.escape(name)}\n(.*?)# END: {re.escape(name)}',
                  source, re.S)
    return m.group(1) if m else ''


def _dedent(text):
    return '\n'.join(l[4:] if l.startswith('    ') else l for l in text.splitlines())


# ---------------------------------------------------------------------------
# STRUCTURE
# ---------------------------------------------------------------------------

def _check_structure(tree, lines, source, ends, findings):
    n_a = n_m = n_h = 0
    declared_actions, declared_tasks, referenced = set(), set(), set()

    # Parse the declarations rather than regex them: a comment inside the
    # argument list ("# Movement server (Server 1)") closes a naive
    # 'declare_actions\((.*?)\)' early and makes every later action look
    # undeclared. That false positive is why this is an AST walk.
    for call in (n for n in ast.walk(tree) if isinstance(n, ast.Call)):
        name = getattr(call.func, 'id', None) or getattr(call.func, 'attr', None)
        if name in ('declare_actions', 'declare_operators', 'declare_commands'):
            declared_actions |= {a.id for a in call.args if isinstance(a, ast.Name)}
        elif name in ('declare_task_methods', 'declare_methods'):
            if call.args and isinstance(call.args[0], ast.Constant) \
                    and isinstance(call.args[0].value, str):
                declared_tasks.add(call.args[0].value)

    # Task names appearing in decompositions, i.e. the first element of a tuple
    referenced |= {n for n in re.findall(r'\(\s*f?["\']([am]_\w+)["\']', source)}

    # Some bundled domains are translated from PDDL and legitimately keep the
    # source names (pick_up, unstack, ...). The style guide's a_/m_ convention
    # does not apply to them, and running the prefix-dependent checks anyway
    # would bury one honest observation under a cascade of noise.
    defined = {n.name for n in tree.body if isinstance(n, ast.FunctionDef)}
    if declared_actions and not any(n.startswith('a_') for n in defined):
        findings.append(Finding('INFO', 'domain.py',
                                f"actions are not named a_*, so this domain does "
                                f"not follow the style guide's naming convention "
                                f"({len(declared_actions)} actions, "
                                f"{len(declared_tasks)} task names declared). "
                                f"Structure checks skipped."))
        return {'actions': len(declared_actions), 'methods': 0,
                'helpers': 0, 'task_names': len(declared_tasks),
                'conforms': False}

    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        if node.name.startswith('h_'):
            n_h += 1
            continue
        if not node.name.startswith(('a_', 'm_')):
            continue
        is_action = node.name.startswith('a_')
        n_a += is_action
        n_m += not is_action
        where = f"{node.name}"
        body = '\n'.join(lines[node.lineno - 1:ends[node.lineno]])
        doc = ast.get_docstring(node) or ''

        for section in (ACTION_SECTIONS if is_action else METHOD_SECTIONS):
            if section not in doc:
                findings.append(Finding('STRUCTURE', where,
                                        f"docstring is missing '{section}'"))
        for marker in (ACTION_MARKERS if is_action else METHOD_MARKERS):
            for kw in ('BEGIN', 'END'):
                if f"# {kw}: {marker}" not in body:
                    findings.append(Finding('STRUCTURE', where,
                                            f"missing '# {kw}: {marker}' marker"))

        args = node.args.args
        if (not args or args[0].arg != 'state'
                or getattr(args[0].annotation, 'id', None) != 'State'):
            findings.append(Finding('STRUCTURE', where,
                                    "first parameter is not 'state: State'"))
        for arg in args:
            if arg.annotation is None:
                findings.append(Finding('STRUCTURE', where,
                                        f"parameter '{arg.arg}' has no type annotation"))
        if node.returns is None:
            findings.append(Finding('STRUCTURE', where, "missing return annotation"))
        else:
            got = ast.unparse(node.returns).replace(' ', '')
            want = 'Union[State,bool]' if is_action else 'Union[List[Tuple],bool]'
            if got != want:
                findings.append(Finding('STRUCTURE', where,
                                        f"returns {got}, expected {want}"))

        if is_action:
            effects = _block(body, 'Effects')
            # A block that assigns nothing has nothing to tag. Some actions
            # legitimately have empty Effects - a_pass_ice in android_netrunner
            # advances a pointer that is already advanced - and they say so in
            # a comment rather than with a tag.
            assigns = re.search(r'^\s*state\.\w+', effects, re.M)
            if assigns and not re.search(
                    rf'#\s*\[({"|".join(EFFECT_TAGS)})\]', effects):
                findings.append(Finding('STRUCTURE', where,
                                        "Effects block has no [DATA]/[ENABLER]/"
                                        "[EXPECTED_EFFECT] tag"))
            tag = re.search(r'MCP_Tool:\s*(\S+)', doc)
            if tag and tag.group(1) != 'None' and ':' not in tag.group(1):
                findings.append(Finding('STRUCTURE', where,
                                        f"MCP_Tool '{tag.group(1)}' is not "
                                        f"server:tool or None"))

    for name in sorted(referenced - declared_actions - declared_tasks):
        findings.append(Finding('STRUCTURE', 'decomposition',
                                f"task '{name}' is used but never declared"))
    for name in sorted(declared_actions - {n.name for n in tree.body
                                           if isinstance(n, ast.FunctionDef)}):
        findings.append(Finding('STRUCTURE', 'declare_actions',
                                f"'{name}' is declared but not defined here"))

    # counts quoted in section headers
    n_tasks = len(declared_tasks)
    for label, count, pattern in (
            ('actions', n_a, r'#\s*(?:-\s*)?(?:[Aa]ctions?|ACTIONS)\s*\((\d+)\)'),
            ('methods', n_m, r'#\s*(?:-\s*)?(?:[Mm]ethods?|METHODS)\s*\((\d+)\)'),
            ('helpers', n_h, r'#\s*(?:-\s*)?(?:[Hh]elper [Ff]unctions|HELPER FUNCTIONS)\s*\((\d+)\)')):
        for m in re.finditer(pattern, source):
            if int(m.group(1)) != count:
                findings.append(Finding('STRUCTURE', 'header',
                                        f"'{m.group(0).strip()}' but the file "
                                        f"has {count} {label}"))
    for m in re.finditer(r'\((\d+) functions over (\d+) task names\)', source):
        if (int(m.group(1)), int(m.group(2))) != (n_m, n_tasks):
            findings.append(Finding('STRUCTURE', 'header',
                                    f"'{m.group(0)}' but the file has {n_m} over "
                                    f"{n_tasks}"))
    return {'actions': n_a, 'methods': n_m, 'helpers': n_h, 'task_names': n_tasks}


# ---------------------------------------------------------------------------
# SEMANTICS
# ---------------------------------------------------------------------------

def _check_semantics(tree, lines, source, ends, problems_source, exempt, findings):
    writes, reads = defaultdict(set), defaultdict(set)

    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        if not node.name.startswith(('a_', 'm_', 'h_')):
            continue
        body = '\n'.join(lines[node.lineno - 1:ends[node.lineno]])
        for attr in _written_attrs(node):
            writes[attr].add(node.name)
        for attr in _read_attrs(node, body):
            reads[attr].add(node.name)

        if not node.name.startswith('a_'):
            continue
        effects = _block(body, 'Effects')
        if not effects.strip():
            continue
        try:
            eff_tree = ast.parse(_dedent(effects))
        except SyntaxError:
            continue
        doc = ast.get_docstring(node) or ''
        documented = (doc.split('Effects:', 1)[-1].split('Returns:', 1)[0]
                      if 'Effects:' in doc else '')
        for attr in sorted(_written_attrs(eff_tree)):
            if attr not in documented:
                findings.append(Finding('SEMANTICS', node.name,
                                        f"writes state.{attr}, but its docstring "
                                        f"Effects section never names it"))

    # problems.py sets a lot of state that the domain only reads
    set_in_problems = set(re.findall(r'\b\w*state\w*\.(\w+)\s*(?:=|\[)',
                                     problems_source, re.I))
    all_written = set(writes) | set_in_problems

    unread = exempt.get('intentionally_unread', {})
    for attr in sorted(set(writes) - set(reads) - set_in_problems):
        if attr in unread:
            continue
        # HYGIENE, not SEMANTICS. In a planning domain the majority of these
        # are *terminal effects*: state an action exists in order to change,
        # that no later precondition happens to read. state.grasp_force and
        # state.thermocycler_block_temp are the point of their actions, not
        # defects. The check still earns its place - it is what caught a
        # retired design flag still being written in rikyu_hpc - but it cannot
        # be part of the default failure set without crying wolf.
        findings.append(Finding('HYGIENE', 'state',
                                f"state.{attr} is written by "
                                f"{sorted(writes[attr])} but never read"))
    # An attribute read only behind a hasattr() guard is optional by design -
    # 'state.x if hasattr(state, "x") else <default>' is how a domain accepts
    # a scenario that did not set it. Reporting those as undefined would
    # punish exactly the defensive style the style guide encourages.
    optional = set(re.findall(r"hasattr\(\s*state\s*,\s*'(\w+)'\s*\)", source))
    for attr in sorted(set(reads) - all_written - optional):
        findings.append(Finding('SEMANTICS', 'state',
                                f"state.{attr} is read by {sorted(reads[attr])} "
                                f"but never written"))
    for attr in sorted(unread):
        if attr in reads:
            findings.append(Finding('SEMANTICS', '_audit.json',
                                    f"'{attr}' is exempted as intentionally "
                                    f"unread, but is now read by {sorted(reads[attr])}"))
        elif attr not in writes:
            findings.append(Finding('SEMANTICS', '_audit.json',
                                    f"'{attr}' is exempted as intentionally "
                                    f"unread, but is no longer written at all"))

    # [ENABLER] must gate something
    preconditions = '\n'.join(
        m.group(1) for m in re.finditer(
            r'# BEGIN: Preconditions\n(.*?)# END: Preconditions', source, re.S))
    for m in re.finditer(r'#\s*\[ENABLER\][^\n]*\n\s*state\.(\w+)', source):
        attr = m.group(1)
        if attr in exempt.get('enabler_without_gate', []):
            continue
        if not re.search(rf"state\.{attr}\b|'{attr}'", preconditions):
            findings.append(Finding('SEMANTICS', 'tags',
                                    f"state.{attr} is tagged [ENABLER] but no "
                                    f"precondition anywhere tests it - it is [DATA]"))


# ---------------------------------------------------------------------------
# BEHAVIOUR (opt-in: imports and plans)
# ---------------------------------------------------------------------------

def _check_behaviour(path, findings):
    import importlib
    import io
    import sys

    parent, name = os.path.dirname(os.path.abspath(path)), os.path.basename(path)
    if parent not in sys.path:
        sys.path.insert(0, parent)
    stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        import gtpyhop
        module = importlib.import_module(name)
    except Exception as exc:                                    # noqa: BLE001
        sys.stdout = stdout
        findings.append(Finding('BEHAVIOUR', name, f"cannot be imported: {exc!r}"))
        return
    finally:
        sys.stdout = stdout

    domain = getattr(module, 'the_domain', None)
    if domain is None:
        findings.append(Finding('BEHAVIOUR', name, "exports no 'the_domain'"))
        return
    if not hasattr(module, 'get_problems'):
        findings.append(Finding('BEHAVIOUR', name, "exports no 'get_problems()'"))
        return

    def plan(state, tasks):
        out = sys.stdout
        sys.stdout = io.StringIO()
        try:
            with gtpyhop.PlannerSession(domain=domain, verbose=0,
                                        strategy='iterative_greedy') as session:
                return session.find_plan(state, tasks)
        finally:
            sys.stdout = out

    for key, problem in module.get_problems().items():
        state, tasks = problem[0], problem[1]
        description = problem[2] if len(problem) > 2 else ''
        try:
            result = plan(state, tasks)
        except Exception as exc:                                # noqa: BLE001
            findings.append(Finding('BEHAVIOUR', key, f"raised {exc!r}"))
            continue
        if not result.success:
            findings.append(Finding('BEHAVIOUR', key, "does not plan"))
            continue
        claim = re.search(r'->\s*(\d+)\s*actions', description)
        if claim and int(claim.group(1)) != len(result.plan):
            findings.append(Finding('BEHAVIOUR', key,
                                    f"description claims {claim.group(1)} actions, "
                                    f"the plan has {len(result.plan)}"))

    if hasattr(module, 'get_trap_problems'):
        for key, problem in module.get_trap_problems().items():
            try:
                result = plan(problem[0], problem[1])
            except Exception as exc:                            # noqa: BLE001
                findings.append(Finding('BEHAVIOUR', key, f"raised {exc!r}"))
                continue
            if result.success:
                findings.append(Finding('BEHAVIOUR', key,
                                        f"is a trap but produced a "
                                        f"{len(result.plan)}-action plan"))


# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------

def audit_example(path, plan=False):
    """Audit one example directory. Returns (findings, counts)."""
    findings = []
    domain_path = os.path.join(path, 'domain.py')
    problems_path = os.path.join(path, 'problems.py')
    if not os.path.exists(domain_path):
        return [Finding('STRUCTURE', path, "no domain.py")], {}

    source = open(domain_path, encoding='utf-8-sig').read()
    problems_source = (open(problems_path, encoding='utf-8-sig').read()
                       if os.path.exists(problems_path) else '')
    if not problems_source:
        findings.append(Finding('STRUCTURE', path, "no problems.py"))

    exempt = {}
    config = os.path.join(path, '_audit.json')
    if os.path.exists(config):
        exempt = json.load(open(config, encoding='utf-8-sig'))

    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return [Finding('STRUCTURE', 'domain.py', f"does not parse: {exc}")], {}
    lines = source.splitlines()
    ends = _span_ends(tree, len(lines))

    counts = _check_structure(tree, lines, source, ends, findings)
    _check_semantics(tree, lines, source, ends, problems_source, exempt, findings)
    if plan:
        _check_behaviour(path, findings)
    return findings, counts


def find_examples(root=None):
    """Every directory under `root` holding a domain.py, sorted.

    Defaults to the bundled examples tree, which is this package's parent.
    """
    root = root or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != '__pycache__']
        if 'domain.py' in filenames:
            found.append(dirpath)
    return sorted(found)
