(* Builds __reports__/diagnostics_guard_nnf/00-findings_guard_soundness_v0.nb.
   Every result cell is the input that was evaluated, followed by the output it produced. *)

ClearAll["Global`*"];
$out = FileNameJoin[{DirectoryName[$InputFileName], "00-findings_guard_soundness_v0.nb"}];

cells = {}; defcells = {};
add[c__] := (cells = Join[cells, {c}]);
title[s_] := add[Cell[s, "Title"]];
subtitle[s_] := add[Cell[s, "Subtitle"]];
sec[s_] := add[Cell[s, "Section"]];
subsec[s_] := add[Cell[s, "Subsection"]];
txt[s_] := add[Cell[s, "Text"]];
item[s_] := add[Cell[s, "Item"]];
prog[s_] := add[Cell[s, "Program"]];
SetAttributes[{inBoxes, def, run}, HoldAll];
inBoxes[e_] := BoxData[MakeBoxes[e, StandardForm]];
def[e_] := (e; defcells = Append[defcells, Cell[inBoxes[e], "Input", InitializationCell -> True]]);
run[e_] := Module[{v = e}, add[Cell[inBoxes[e], "Input"], Cell[BoxData[ToBoxes[v, StandardForm]], "Output"]]; v];

(* ---------------- definitions (appendix, initialization cells) ---------------- *)

def[vars = {p, q, r}];
def[toB[e_] := e /. {and -> And, or -> Or, not -> Not}];
def[req[e_, neg_] := If[neg, ! toB[e], toB[e]]];
def[lit[{e_, neg_}] := If[neg, ! toB[e], toB[e]]];
def[show[e_] := ToString[toB[e], InputForm]];
def[showAtom[at_] := ToString[lit[at], InputForm]];
(* fix + De Morgan split, commit 3948b54: guards._requirement_atoms *)
def[nnf[not[x_], neg_] := With[{in = nnf[x, ! neg]}, If[neg || Length[in] > 1, in, {{not[x], neg}}]]];
def[nnf[e_and, False] := Join @@ (nnf[#, False] & /@ List @@ e)];
def[nnf[e_or, True] := Join @@ (nnf[#, True] & /@ List @@ e)];
def[nnf[e_, neg_] := {{e, neg}}];
(* fix only, commit 185a327 *)
def[cons[not[x_], True] := cons[x, False]];
def[cons[e_, True] := {{e, True}}];
def[cons[e_and, False] := Join @@ (cons[#, False] & /@ List @@ e)];
def[cons[e_, False] := {{e, False}}];
(* 0.1.0 *)
def[split[e_and] := Join @@ (split /@ List @@ e)];
def[split[e_] := {e}];
def[old[not[x_], True] := {#, False} & /@ split[x]];
def[old[e_, True] := {#, True} & /@ split[e]];
def[old[e_, False] := {#, False} & /@ split[e]];
def[T[f_] := TautologyQ[f, vars]];
def[tt[f_] := BooleanTable[f, vars]];
def[check[rule_, e_, neg_] := Module[{R = tt[req[e, neg]], ats = rule[e, neg], A},
    A = tt[lit[#]] & /@ ats;
    {Length[ats],
     Count[A, col_ /; ! And @@ MapThread[Implies, {R, col}]],
     Boole[tt[And @@ (lit /@ ats)] =!= R],
     Boole[! AllTrue[ats, MemberQ[Level[{e}, {0, Infinity}, Heads -> False], #[[1]]] &]]}]];
def[ex2[1] = vars];
def[ex2[n_] := ex2[n] = DeleteDuplicates@Join[
     not /@ ex2[n - 1],
     Join @@ Table[Join @@ ({and @@ #, or @@ #} & /@ Tuples[{ex2[k], ex2[n - 1 - k]}]), {k, 1, n - 2}],
     If[n >= 4, Join @@ Flatten[Table[Join @@ ({and @@ #, or @@ #} & /@ Tuples[{ex2[i], ex2[j], ex2[n - 1 - i - j]}]),
          {i, 1, n - 3}, {j, 1, n - 2 - i}], 1], {}]]];
def[summ[rule_, exprs_] := summ[rule, exprs] = Module[{res = Flatten[Table[check[rule, e, neg], {e, exprs}, {neg, {True, False}}], 1]},
    {Length[res], Total[res[[All, 1]]], Total[res[[All, 2]]], Total[res[[All, 3]]], Total[res[[All, 4]]]}]];
def[subs[e_] := DeleteCases[DeleteDuplicates[Cases[{e}, _and | _or | _not | p | q | r, {2, Infinity}]], e]];
def[imprecise[rule_, exprs_] := Module[{n = 0},
    Do[Module[{ats = rule[e, neg], Rb = req[e, neg]},
       Do[Module[{ab = lit[at], ob = And @@ (lit /@ DeleteCases[ats, at, {1}, 1])},
          If[AnyTrue[Join @@ ({toB[#], ! toB[#]} & /@ subs[at[[1]]]),
             Function[L, T[Implies[Rb, L]] && ! T[Implies[ab, L]] && ! T[Implies[ob, L]]]], n++]],
        {at, ats}]], {e, exprs}, {neg, {True, False}}];
    n]];
def[tbl[headers_, rows_] := Grid[Prepend[rows, Style[#, Bold] & /@ headers], Frame -> All, Alignment -> Left,
    Background -> {None, {GrayLevel[0.9]}}, Spacings -> {1.2, 0.6}]];
def[pct[x_] := TextString[Round[100 x, 1/100] // N] <> " %"];
def[mark[b_] := If[TrueQ[b], Style["proved", Darker[Green]], Style["fails", Red]]];

(* ---------------- document ---------------- *)

title["Guard extraction soundness \[LongDash] Findings (v0)"];
subtitle["gtpyhop-diagnostics 0.1.0 \[RightArrow] 0.1.1: which atoms explain_dead_end may name as blockers"];
prog["type: findings
topic: diagnostics_guard_nnf
date: 2026-11-16
version: v0
prior-version: none
key-metric: unsound atoms over every guard tree of \[LessEqual] 7 nodes: 0 (prior: 28,833 with 0.1.0, delta: \[Minus]28,833)
decision-required: confirm"];

sec["Headline Result"];
prog["metric:    unsound atoms extracted, every guard expression tree of \[LessEqual] 7 nodes over 3 leaves, as a bail and as a wrapping guard
value:     0  (fix only, and fix + De Morgan split)
unit:      atoms
prior:     28,833 (0.1.0)
direction: down"];
txt["decision-required is confirm, for one item: whether to keep commit 3948b54, the De Morgan split. Unlike the fix, it changes atoms that were already sound (making them finer), so it is kept as a separate commit that can be dropped. Everything else is informational."];

sec["Model"];
txt["An action guard yields a requirement: the test T itself for a wrapping guard or an else that bails, and not T for a bail (if T: return False). explain_dead_end names as blockers the atoms that evaluate false. That is honest only if every atom is necessary, that is implied by the requirement. The fix splits the requirement only where it is a conjunction, read through negation (its negation normal form):"];
add[Cell[BoxData[ToBoxes[tbl[{"syntax", "requirement polarity", "atoms", "justification"},
    {{"not X", "either", "atoms of X, polarity flipped (kept as written if that splits nothing)", "double negation"},
     {"A and B and \[Ellipsis]", "positive", "atoms of each operand", "a conjunction: each conjunct is necessary"},
     {"A or B or \[Ellipsis]", "negated", "atoms of each operand, negated", "De Morgan: not (A or B) = not A and not B"},
     {"A and B", "negated", "kept whole", "not (A and B) = not A or not B: neither is necessary alone"},
     {"A or B", "positive", "kept whole", "a disjunction: no side is necessary alone"},
     {"anything else", "either", "kept whole", "a leaf"}}], StandardForm]], "Output"]];
txt["Worked examples, extracted live by the three rules (A=p, B=q, C=r). An atom printed in red is unsound."];
run[With[{cases = {{"bail", and[p, q], True}, {"bail", not[and[p, q]], True}, {"bail", or[p, q], True},
     {"bail", and[p, or[q, r]], True}, {"wrap", and[p, or[q, r]], False}, {"wrap", and[not[or[p, q]], not[r]], False}}},
   tbl[{"guard", "test", "requirement", "0.1.0", "fix (185a327)", "fix + De Morgan (3948b54)"},
    Table[With[{e = c[[2]], neg = c[[3]]},
      {c[[1]], show[e], ToString[BooleanMinimize[req[e, neg]], InputForm],
       Sequence @@ (Row[Riffle[If[T[Implies[req[e, neg], lit[#]]], showAtom[#], Style[showAtom[#], Red]] & /@ #, ",  "]] & /@
          {old[e, neg], cons[e, neg], nnf[e, neg]})}], {c, cases}]]]];

sec["Results Tables"];
subsec["R1. The root cause and the table rows of the issue draft"];
run[tbl[{"claim", "statement", "result"}, {
   {"L1 double negation", "!!a \[DoubleLongLeftRightArrow] a", mark[T[Equivalent[! ! p, p]]]},
   {"L2 De Morgan (and)", "!(a && b) \[DoubleLongLeftRightArrow] !a || !b", mark[T[Equivalent[! (p && q), ! p || ! q]]]},
   {"L3 De Morgan (or)", "!(a || b) \[DoubleLongLeftRightArrow] !a && !b", mark[T[Equivalent[! (p || q), ! p && ! q]]]},
   {"L4 n-ary De Morgan", "n = 1 \[Ellipsis] 10", mark[AllTrue[Range[10], With[{xs = Array[x, #]}, TautologyQ[Equivalent[! (Or @@ xs), And @@ (Not /@ xs)], xs]] &]]},
   {"root cause", "!(a && b) \[DoubleLongRightArrow] !a", mark[T[Implies[! (p && q), ! p]]]},
   {"  counterexample", "", FindInstance[! Implies[! (p && q), ! p], {p, q}, Booleans]},
   {"row 2: bail on a && b", "no single literal of a, b is necessary", mark[NoneTrue[{p, ! p, q, ! q}, T[Implies[! (p && q), #]] &]]},
   {"row 3: bail on a || b", "!a and !b each necessary, jointly sufficient", mark[T[Implies[! (p || q), ! p]] && T[Implies[! (p || q), ! q]] && T[Equivalent[! p && ! q, ! (p || q)]]]},
   {"row 4: wrap a && (b || c)", "b || c cannot be narrowed to b or c", mark[NoneTrue[{q, ! q, r, ! r}, T[Implies[p && (q || r), #]] &]]}}]];
txt["The \"fails\" on the root-cause line is the defect: a bail on a conjunction does not require the negation of either conjunct. The counterexample is the reproduction's own state."];

subsec["R2. Proof for every expression, by induction on the syntax tree"];
txt["Claim: for every test e and polarity, the conjunction of the extracted atoms is equivalent to the requirement. Each clause of the rule is shown to preserve this, assuming it for the children (IH: Ai \[DoubleLongLeftRightArrow] Ri). Equivalence then gives necessity of every atom by and-elimination."];
run[With[{step = Function[{n, comb}, With[{A = Array[Subscript[aa, #] &, n], R = Array[Subscript[rr, #] &, n]},
       TautologyQ[Implies[And @@ MapThread[Equivalent, {A, R}], Equivalent[And @@ A, comb[R]]], Join[A, R]]]]},
  tbl[{"clause of the rule", "obligation", "result"}, {
    {"not x, negated", "req(not x, True) \[DoubleLongLeftRightArrow] req(x, False)", mark[TautologyQ[Equivalent[! ! x, x], {x}]]},
    {"not x, positive", "req(not x, False) \[DoubleLongLeftRightArrow] req(x, True)", mark[TautologyQ[Equivalent[! x, ! x], {x}]]},
    {"and[v1..vn], positive", "AND(atoms of children) \[DoubleLongLeftRightArrow] And(vi), n = 2 \[Ellipsis] 7", mark[AllTrue[Range[2, 7], step[#, And @@ # &] &]]},
    {"or[v1..vn], negated", "AND(atoms of children, each req = !vi) \[DoubleLongLeftRightArrow] !Or(vi), n = 2 \[Ellipsis] 7",
     mark[AllTrue[Range[2, 7], With[{V = Array[Subscript[vv, #] &, #], A = Array[Subscript[aa, #] &, #]},
         TautologyQ[Implies[And @@ MapThread[Equivalent, {A, Not /@ V}], Equivalent[And @@ A, ! (Or @@ V)]], Join[A, V]]] &]]},
    {"kept whole", "the single atom is the requirement", mark[True]},
    {"necessity", "req \[DoubleLongLeftRightArrow] AND(atoms) \[DoubleLongRightArrow] each atom, n = 1 \[Ellipsis] 7",
     mark[AllTrue[Range[7], With[{A = Array[Subscript[aa, #] &, #]}, AllTrue[A, Function[ai, TautologyQ[Implies[And @@ A, ai], A]]]] &]]},
    {"0.1.0's bail clause", "AND(!a, !b) \[DoubleLongLeftRightArrow] !(a && b)", mark[T[Equivalent[! p && ! q, ! (p && q)]]]}}]]];
txt["The fix-only rule (185a327) uses a subset of these clauses (it never splits under negation except through not), so the same argument covers it. 0.1.0 fails exactly at its bail clause."];

subsec["R3. Exhaustive cross-check"];
run[all = Join @@ Table[ex2[n], {n, 1, 7}]; Length[all]];
run[tbl[{"extractor", "guards", "atoms", "unsound atoms", "guards where AND(atoms) \[NotEqual] requirement", "atoms not a sub-expression"},
   {Prepend[summ[old, all], "0.1.0"], Prepend[summ[cons, all], "fix (185a327)"], Prepend[summ[nnf, all], "fix + De Morgan (3948b54)"]}]];
txt["Every expression tree of up to 7 nodes over three leaves, binary and ternary and/or, each checked as a bail and as a wrapping guard over all 8 assignments."];

subsec["R4. Precision of the fix + De Morgan rule"];
txt["An atom counts as imprecise when a strictly stronger literal inside it (a sub-expression or its negation) is necessary and is not already implied by the sibling atoms: a sounder, more specific blocker the rule does not name."];
run[distinct = Select[all, DuplicateFreeQ[Cases[{#}, p | q | r, Infinity]] &]; Length[distinct]];
run[tbl[{"expressions", "atoms", "imprecise atoms", "share"},
   {{"all, \[LessEqual] 7 nodes", summ[nnf, all][[2]], #, pct[# / summ[nnf, all][[2]]]} &[imprecise[nnf, all]],
    {"no leaf repeated", summ[nnf, distinct][[2]], #, pct[# / summ[nnf, distinct][[2]]]} &[imprecise[nnf, distinct]]}]];
run[{T[Implies[! r && (r || q), q]], T[Implies[r || q, q]], showAtom /@ nnf[and[not[r], or[r, q]], False]}];
txt["The draft's example: the requirement implies q, but the atom (r || q) alone does not, so finding q takes reasoning across atoms."];

subsec["R5. The reported reproduction"];
txt["p = state.locked_a[x] = True, q = state.locked_b[x] = False, r = (state.fuel[x] > 0) = False; guards: bail on p && q, bail on !r."];
run[With[{s = {p -> True, q -> False, r -> False}},
  tbl[{"extractor", "atoms named as blockers"},
   {#[[1]], Row[Riffle[showAtom /@ Select[Join[#[[2]][and[p, q], True], #[[2]][not[r], True]], ! (lit[#] /. s) &], ",  "]]} & /@
    {{"0.1.0", old}, {"fix (185a327)", cons}, {"fix + De Morgan (3948b54)", nnf}}]]];

subsec["R6. The second source: control flow (not fixed)"];
txt["Each shape's success condition is written from the code; the atoms are what the ast.walk extractor yields for it."];
run[tbl[{"shape", "success condition", "extracted atoms", "unsound atoms"},
   With[{rows = {{"if a: if b: return False", ! (p && q), {! q}},
       {"if a: ...return s;  if b: ...return s", p || q, {p, q}},
       {"if a: return s;  if b: return False;  return s", p || ! q, {p, ! q}},
       {"if a: return False  elif b: return False", ! p && ! q, {! p, ! q}},
       {"if a: if b: return s", p && q, {p, q}}}},
    {#[[1]], ToString[#[[2]], InputForm], ToString[#[[3]], InputForm],
      ToString[Select[#[[3]], Function[at, ! T[Implies[#[[2]], at]]]], InputForm]} & /@ rows]]];
run[tbl[{"launcher", "bail fires (action blocked here)", "atom launcher != 'mpirun' reported failed"},
   Table[{If[l === None, "None", "'" <> l <> "'"], ! ! (l =!= None && l =!= "mpirun"), l =!= "mpirun"}, {l, {None, "mpirun", "srun"}}]]];
txt["rikyu_hpc a_submit_job: if launcher is not None: if launcher != 'mpirun': return False. With launcher = None nothing blocks, yet the atom is reported as failed."];

sec["Observations"];
add[Cell[BoxData[ToBoxes[tbl[{"Signal", "Baseline / Expected", "Observed [source]", "Interpretation"}, {
     {"unsound atoms", "0 for a correct extractor", "28,833 \[RightArrow] 0 [R3]", "the defect class is closed for every shape up to the bound, and for all sizes by R2"},
     {"atoms \[NotEqual] requirement", "0", "9,951 guards \[RightArrow] 0 [R3]", "no precondition is lost either: the atoms are exactly the requirement"},
     {"atoms per guard", "more atoms = finer blame", "73,671 (fix) \[RightArrow] 101,022 (+ De Morgan) [R3]", "the De Morgan commit only refines; it never adds an unsound atom"},
     {"imprecise atoms", "draft: 1.8 %, \"mostly where a leaf repeats\"", "1.5 %; 0 when no leaf repeats [R4]", "the remaining gap is semantic (cross-atom), not syntactic"},
     {"reproduction blockers", "only the fuel guard", "0.1.0: !p, !r; both fixes: !r [R5]", "the reported symptom is gone"},
     {"control-flow shapes", "atoms necessary", "3 of 5 shapes unsound [R6]", "a second root cause, outside expression splitting"}}], StandardForm]], "Output"]];
subsec["Scope: what this does not prove"];
item["The counts from files (11 and 17 bundled actions, 408, 865 and 1,072 in the corpus, recognition 330 and 5,808, the 13/11 and 53/27 bounds) are measurements, made with the Python scripts in scripts/ next to this notebook."];
item["The model is two-valued logic over the guard leaves. Python's truthiness agrees with it; a leaf that raises lands in unevaluated, which explain_dead_end never names as a blocker."];
item["Diagnostics run after find_plan returns; none of this changes which plans are found."];

sec["Charts & Visualizations"];
run[With[{d = {summ[old, all], summ[cons, all], summ[nnf, all]}},
  BarChart[{{d[[1, 2]] - d[[1, 3]], d[[1, 3]]}, {d[[2, 2]], 0}, {d[[3, 2]], 0}}, ChartLayout -> "Stacked",
   ChartLabels -> {{"0.1.0", "fix", "fix + De Morgan"}, None}, ChartLegends -> Placed[{"sound atoms", "unsound atoms"}, Below],
   ChartStyle -> {GrayLevel[0.65], Red}, AxesLabel -> {None, "atoms"}, LabelingFunction -> (If[#1 > 0, Placed[Style[#1, Black, 12], Center], None] &),
   PlotLabel -> "Atoms extracted from 49,146 guards (every tree \[LessEqual] 7 nodes, bail and wrap)", ImageSize -> 520]]];
txt["Caption: 0.1.0 extracts 28,833 unsound atoms (red); both fixes extract none, and the De Morgan split adds 27,351 sound atoms over the fix alone."];

sec["Contradictions & Surprises"];
item["The precision gap is sharper than the draft said: it occurs only where a leaf repeats, never otherwise (R4)."];
item["A bundled example carries the second root cause: rikyu_hpc a_submit_job blames launcher != 'mpirun' when launcher is None (R6)."];

sec["Steering Questions"];
item["[now] Keep commit 3948b54 (De Morgan split)? It changes only sound atoms, making 17 bundled and 1,072 corpus actions finer."];
item["[now] File the control-flow source as its own issue, with R6 as its evidence."];
item["[next run] Path-aware extraction: drop, or conjoin with their path condition, the atoms of ifs not reached on every successful path."];
item["[later] Refresh the README coverage claim: 285/293 predates collections added since; the current count is 330/335."];

sec["Pointers"];
item["Commits 185a327 (fix), 3948b54 (De Morgan split), 1e63e38 (release gtpyhop-diagnostics 0.1.1)"];
item["tools/diagnostics_guard_check.py (8 cases, in checks.yml)"];
item["scripts/ next to this notebook: prop.py, examples_diff.py, corpus.py, cf.py (the measurements behind the counts)"];

add[Cell[CellGroupData[Join[{Cell["Appendix: definitions (initialization cells)", "Section"],
      Cell["Inert syntax and[..], or[..], not[..] over leaves p, q, r, so that Wolfram does not simplify an expression before the rules see it. The notebook has its own context (CellContext -> Notebook), so a p, q or r defined elsewhere cannot leak into the leaves. nnf, cons and old mirror guards._requirement_atoms at 3948b54, at 185a327, and 0.1.0.", "Text"]}, defcells], Closed]]];

nb = Notebook[cells, CellContext -> Notebook, WindowTitle -> "Guard extraction soundness - Findings v0"];
Quiet@CreateDirectory[DirectoryName[$out]];
Export[$out, nb, "NB"]
