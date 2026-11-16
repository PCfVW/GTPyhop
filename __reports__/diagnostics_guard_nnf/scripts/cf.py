import ast, sys, importlib.util
spec = importlib.util.spec_from_file_location("g", sys.argv[1]); g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
SHAPES = {
"elif_bails": """def a(s, x):
    if s.p[x]:
        return False
    elif s.q[x]:
        return False
    return s""",
"nested_bail_in_cond": """def a(s, x):
    if s.p[x]:
        if s.q[x]:
            return False
    return s""",
"alt_wrapping_branches": """def a(s, x):
    if s.p[x]:
        s.done[x] = 1
        return s
    if s.q[x]:
        s.done[x] = 2
        return s""",
"elif_wrapping": """def a(s, x):
    if s.p[x]:
        return s
    elif s.q[x]:
        return s
    return False""",
"bail_in_loop": """def a(s, x):
    for o in s.objs:
        if s.blocked[o]:
            return False
    return s""",
"bail_after_success_return": """def a(s, x):
    if s.p[x]:
        return s
    if s.q[x]:
        return False
    return s""",
"nested_wrap": """def a(s, x):
    if s.p[x]:
        if s.q[x]:
            return s""",
}
for name, src in SHAPES.items():
    fn = ast.parse(src).body[0]
    print(f"{name:28s}", g.extract_action_guards(fn, src).atoms)
