"""Does guards.py compute what the Wolfram model says, on every enumerated program?

    python cf_agree.py OLD_GUARDS NEW_GUARDS programs.json

programs.json is exported by the notebook's build script: each program in the model's
syntax, with the (if id, negated) requirements the model predicts for the ast.walk reading
(old) and for the path-aware one (new). Each program is rendered as an action, both
extractors are run on it, and their atoms are mapped back to if ids by line number.
"""
import ast, json, sys, importlib.util


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def render(block, depth, lines, line_of):
    pad = "    " * depth
    if not block:
        lines.append(pad + "pass")
    for stmt in block:
        if stmt == "ok":
            lines.append(pad + "return state")
        elif stmt == "bail":
            lines.append(pad + "return False")
        elif stmt == "eff":
            lines.append(pad + "state.done[x] = 1")
        elif stmt[0] == "if":
            _, ident, test, body, orelse = stmt
            lines.append("{}if state.{}[x]:".format(pad, test))
            line_of[len(lines)] = ident
            render(body, depth + 1, lines, line_of)
            if orelse:
                lines.append(pad + "else:")
                render(orelse, depth + 1, lines, line_of)
        else:
            _, ident, body = stmt
            lines.append(pad + "for o in state.objs:")
            render(body, depth + 1, lines, line_of)


def main():
    old, new = load(sys.argv[1], "old_guards"), load(sys.argv[2], "new_guards")
    programs = json.load(open(sys.argv[3]))
    mismatches = {"old": [], "new": []}
    for entry in programs:
        lines, line_of = ["def a(state, x):"], {}
        render(entry["prog"], 1, lines, line_of)
        src = "\n".join(lines) + "\n"
        func = ast.parse(src).body[0]
        for label, module in (("old", old), ("new", new)):
            got = sorted([line_of[a.lineno], a.negated]
                         for a in module.extract_action_guards(func, src).atoms)
            want = sorted(entry[label])
            if got != want:
                mismatches[label].append((src, got, want))
    print("programs={} old_mismatches={} new_mismatches={}".format(
        len(programs), len(mismatches["old"]), len(mismatches["new"])))
    for label in ("old", "new"):
        for src, got, want in mismatches[label][:3]:
            print(label, "python", got, "model", want, "\n" + src)
    return 1 if any(mismatches.values()) else 0


if __name__ == "__main__":
    sys.exit(main())
