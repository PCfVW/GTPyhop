"""Truth-table soundness/precision check of extract_action_guards on generated guards."""
import ast, itertools, random, sys, importlib.util
spec = importlib.util.spec_from_file_location("g", sys.argv[1]); g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
LEAVES = ["state.p[x]", "state.q[x]", "state.r[x]", "state.s[x]"]
def gen(rng, d):
    if d == 0 or rng.random() < 0.3: return rng.choice(LEAVES)
    k = rng.random()
    if k < 0.25: return "not " + wrap(gen(rng, d-1))
    op = " and " if k < 0.62 else " or "
    return op.join(wrap(gen(rng, d-1)) for _ in range(rng.choice([2, 2, 3])))
def wrap(e): return e if e in LEAVES else "(" + e + ")"
FORMS = {
  "bail":      "def a(state, x):\n    if {T}:\n        return False\n    state.done[x] = True\n    return state\n",
  "bail_none": "def a(state, x):\n    if {T}:\n        return\n    state.done[x] = True\n    return state\n",
  "wrap":      "def a(state, x):\n    if {T}:\n        state.done[x] = True\n        return state\n",
  "else_bail": "def a(state, x):\n    if {T}:\n        state.done[x] = True\n    else:\n        return False\n    return state\n",
}
class S: pass
def ev(node, env):
    return bool(eval(compile(ast.Expression(body=node), "<a>", "eval"), env))
def envs():
    for bits in itertools.product([False, True], repeat=len(LEAVES)):
        st = S(); st.p, st.q, st.r, st.s = ({'x': b} for b in bits); yield {"state": st, "x": "x"}
def held(atom, env): v = ev(atom.node, env); return (not v) if atom.negated else v
def subexprs(node):
    for n in ast.walk(node):
        if isinstance(n, (ast.BoolOp, ast.UnaryOp, ast.Subscript)) and not isinstance(n.ctx if hasattr(n,'ctx') else None, ast.Store):
            if isinstance(n, ast.Subscript) and not isinstance(n.value, ast.Attribute): continue
            yield n
rng = random.Random(int(sys.argv[2]) if len(sys.argv) > 2 else 0)
N = int(sys.argv[3]) if len(sys.argv) > 3 else 2000
seen = set(); cases = unsound = atoms_total = not_equiv = imprecise = actions_unsound = 0
examples = []; pex = []
while len(seen) < N:
    T = gen(rng, rng.choice([1, 2, 3]))
    if T in seen: continue
    seen.add(T)
    for form, tpl in FORMS.items():
        src = tpl.format(T=T); fn = ast.parse(src).body[0]
        test = fn.body[0].test
        req_neg = form.startswith("bail")
        E = list(envs())
        req = [(not ev(test, e)) if req_neg else ev(test, e) for e in E]
        ag = g.extract_action_guards(fn, src); cases += 1
        bad = False
        for a in ag.atoms:
            atoms_total += 1
            hv = [held(a, e) for e in E]
            if any(r and not h for r, h in zip(req, hv)):
                unsound += 1; bad = True
                if len(examples) < 6: examples.append((form, T, a))
            else:
                # precision: a strictly stronger necessary literal (sub-expression, either polarity) exists inside this atom?
                for sub in subexprs(a.node):
                    if sub is a.node: continue
                    sv = [ev(sub, e) for e in E]
                    for lit in (sv, [not v for v in sv]):
                        others = [all(held(b, e) for b in ag.atoms if b is not a) for e in E]
                        if all(l or not r for r, l in zip(req, lit)) and any(h and not l for h, l in zip(hv, lit)) and any(o and not l for o, l in zip(others, lit)):
                            imprecise += 1; (len(pex)<3 and pex.append((form,T,a,ast.unparse(sub)))); break
                    else: continue
                    break
        conj = [all(held(a, e) for a in ag.atoms) for e in E]
        if conj != req: not_equiv += 1
        actions_unsound += bad
print(f"expressions={len(seen)} cases={cases} atoms={atoms_total} unsound_atoms={unsound} "
      f"cases_with_unsound={actions_unsound} conj_not_equiv_req={not_equiv} sound_atoms_with_stronger_necessary_subexpr={imprecise}")
for f, T, a in examples: print("  e.g.", f, "|", T, "->", a)
for e in pex: print("  imprecise:", *e)
