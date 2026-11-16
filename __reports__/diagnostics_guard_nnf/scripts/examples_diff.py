"""Per declared action in the bundled examples: recognition and old-vs-new atom sets."""
import ast, os, sys, importlib.util
def load(p, n):
    spec = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
old, new = load(sys.argv[1], "old"), load(sys.argv[2], "new")
root = sys.argv[3]
# collections: dirs containing a declare_actions call; actions resolved within the same collection dir (first def wins, like load_guards)
declared = {}   # (collection, name)
funcs = {}      # collection -> {name: (node, src)}
for dp, dn, fn in os.walk(root):
    if "__pycache__" in dp: continue
    for f in fn:
        if not f.endswith(".py"): continue
        p = os.path.join(dp, f); src = open(p, encoding="utf-8").read()
        try: tree = ast.parse(src)
        except SyntaxError: continue
        coll = os.path.relpath(dp, root)
        for n in ast.walk(tree):
            if isinstance(n, ast.FunctionDef): funcs.setdefault(coll, {}).setdefault(n.name, (n, src))
            if isinstance(n, ast.Call) and getattr(n.func, "attr", getattr(n.func, "id", None)) == "declare_actions":
                for a in n.args:
                    if isinstance(a, ast.Name): declared.setdefault((coll, a.id), None)
def key(atoms): return [(a.source, a.negated) for a in atoms]
total = rec_old = rec_new = 0; changed = []; missing = []
for coll, name in sorted(declared):
    hit = funcs.get(coll, {}).get(name)
    if hit is None:   # look in parent collection dirs
        c = coll
        while c and hit is None:
            c = os.path.dirname(c); hit = funcs.get(c, {}).get(name)
    total += 1
    if hit is None: missing.append((coll, name)); continue
    o = old.extract_action_guards(*hit); nw = new.extract_action_guards(*hit)
    rec_old += bool(o and o.atoms); rec_new += bool(nw and nw.atoms)
    if key(o.atoms) != key(nw.atoms): changed.append((coll, name, key(o.atoms), key(nw.atoms)))
print(f"declared actions={total} recognised old={rec_old} new={rec_new} unresolved={len(missing)} changed={len(changed)}")
for c in changed: print(" ", *c, sep="\n    ")
if missing: print("unresolved:", missing[:10])
