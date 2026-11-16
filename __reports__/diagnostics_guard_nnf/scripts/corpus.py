"""Read-only static diff of guard atoms over the consumer corpus: v0.1.0 vs conservative vs NNF."""
import ast, glob, os, sys, importlib.util, collections
def load(p, n):
    spec = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
V = {k: load(p, k) for k, p in zip(("old", "cons", "nnf"), sys.argv[2:5])}
roots = sys.argv[1].split(":")
files = []
for r in roots:
    files += glob.glob(os.path.join(r, "*", "_run_cache", "*", "run-*", "outputs", "**", "domain.py"), recursive=True) if "results" in r \
        else glob.glob(os.path.join(r, "**", "*.py"), recursive=True)
files = sorted(set(files))
def declared(tree):
    out = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            f = n.func; fn = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", None)
            if fn == "declare_actions":
                for a in n.args:
                    a = a.value if isinstance(a, ast.Starred) else a
                    if isinstance(a, ast.Name): out.append(a.id)
                    elif isinstance(a, ast.Attribute): out.append(a.attr)
                    elif isinstance(a, (ast.List, ast.Tuple)): out += [e.id for e in a.elts if isinstance(e, ast.Name)]
    return list(dict.fromkeys(out))
def returns_name(stmts, name):
    return any(isinstance(n, ast.Return) and isinstance(n.value, ast.Name) and n.value.id == name
               for s in stmts for n in ast.walk(s))
def spine_ifs(func):
    """Ifs reached on every successful path (approximation; see report)."""
    st = func.args.args[0].arg; on = set()
    def walk(stmts, ok):
        for s in stmts:
            if isinstance(s, ast.If):
                if ok: on.add(id(s))
                wraps = returns_name(s.body, st)
                walk(s.body, ok and wraps and not returns_name(s.orelse, st))
                walk(s.orelse, ok and not wraps)          # elif/else of a bail stays on the spine
            elif isinstance(s, (ast.With, ast.Try)):
                walk(s.body, ok)
            if returns_name([s], st) and not (isinstance(s, ast.If) and not s.orelse and False):
                if not isinstance(s, ast.Return): ok = False
    walk(func.body, True); return on
def key(atoms): return [(a.source, a.negated, a.lineno) for a in atoms]
C = collections.Counter(); bail_and_actions = []; rep = []
for p in files:
    try: text = open(p, encoding="utf-8", errors="replace").read(); tree = ast.parse(text)
    except (SyntaxError, ValueError): C["syntax_error"] += 1; continue
    C["files"] += 1
    funcs = {n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    for name in declared(tree):
        fn = funcs.get(name)
        if fn is None or not fn.args.args: continue
        C["actions"] += 1
        g = {k: m.extract_action_guards(fn, text) for k, m in V.items()}
        k = {kk: key(v.atoms) for kk, v in g.items()}
        for kk in k: C["recognised_" + kk] += bool(k[kk]); C["atoms_" + kk] += len(k[kk])
        if k["old"] != k["cons"]:
            C["changed_old_to_cons"] += 1
            removed = set(k["old"]) - set(k["cons"]); C["unsound_atoms_removed"] += len(removed)
        if k["cons"] != k["nnf"]: C["changed_cons_to_nnf"] += 1
        if k["old"] != k["nnf"]: C["changed_old_to_nnf"] += 1
        if "work_directory is not None" in text and any("work_directory is not None" == s for s, n, l in k["old"]):
            rep.append((p, name, [a for a in k["old"] if "work_directory" in a[0]], [a for a in k["nnf"] if "work_directory" in a[0]]))
        # control-flow class, on the NNF atoms
        on = spine_ifs(fn)
        ifs = {id(n): n for n in ast.walk(fn) if isinstance(n, ast.If)}
        off = 0
        for n in ast.walk(fn):
            if isinstance(n, ast.If) and id(n) not in on:
                off += sum(1 for a in g["nnf"].atoms if any(a.node is m for m in ast.walk(n.test)))
        if off: C["actions_with_offspine_atoms"] += 1; C["offspine_atoms"] += off; (os.environ.get("SHOW") and print("OFF", os.path.relpath(p), name, fn.lineno))
for kk, v in sorted(C.items()): print(f"{kk}={v}")
print("reported class (work_directory):", len(rep))
for r in rep[:3]: print(" ", os.path.basename(os.path.dirname(r[0])), r[1], "\n    old:", r[2], "\n    new:", r[3])
