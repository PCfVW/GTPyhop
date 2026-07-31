# Tutorial: how to write a goal

Most GTPyhop examples ask the planner to perform a **task**: *"deliver this parcel"*.
But you can also ask it for a **goal**: *"box1 should end up in the kitchen"* — and let
the planner work out what that takes.

This tutorial shows every way GTPyhop lets you write a goal. It uses one small domain
throughout and asks for **the same thing** four different ways, so you can see exactly
what each form buys you.

Every snippet runs as written. No prior knowledge of goals is assumed.

## Table of Contents

- [Tasks and goals](#tasks-and-goals)
- [The domain](#the-domain)
- [Way 1: one unigoal](#way-1-one-unigoal)
- [Way 2: two unigoals, one after the other](#way-2-two-unigoals-one-after-the-other)
- [Way 3: one multigoal, split automatically](#way-3-one-multigoal-split-automatically)
- [Way 4: one multigoal, your own method](#way-4-one-multigoal-your-own-method)
- [What GTPyhop checks for you](#what-gtpyhop-checks-for-you)
- [Traps](#traps)
- [Summary](#summary)

## Tasks and goals

The difference is what you name:

- A **task** names *something to do*: `('deliver', 'parcel1', 'truck1', 'shop')`.
- A **goal** names *a state variable and the value you want it to have*:
  `('loc', 'box1', 'kitchen')` — "the `loc` of `box1` should be `kitchen`".

GTPyhop tells them apart by looking up the first element. `'deliver'` is a task because
you declared task methods for it; `'loc'` is a goal because you declared *unigoal*
methods for it. Same tuple shape, different registration.

There are exactly **two** kinds of goal:

| Kind | Written as | Means |
|---|---|---|
| **unigoal** | `('loc', 'box1', 'kitchen')` | one state variable, one value |
| **multigoal** | `Multigoal('g', loc={'box1': 'kitchen', 'box2': 'study'})` | several, all true *at the same time* |

## The domain

Two boxes start in the hall. One action moves a box to a room. Save this as `boxes.py`:

```python
import gtpyhop

domain = gtpyhop.Domain('boxes')

def move(state, box, room):
    if state.loc[box] != room:
        state.loc[box] = room
        return state

gtpyhop.declare_actions(move)

# A unigoal method. Note what it receives: (state, arg, value).
# NOT the goal tuple -- the state-variable name is already implied.
def m_move_it(state, box, room):
    return [('move', box, room)]

gtpyhop.declare_unigoal_methods('loc', m_move_it)

def initial_state():
    state = gtpyhop.State('s0')
    state.loc = {'box1': 'hall', 'box2': 'hall'}
    return state
```

Two lines deserve attention.

`declare_unigoal_methods('loc', m_move_it)` registers `m_move_it` for goals about the
`loc` state variable. That single call is what makes `('loc', …, …)` a goal rather than
a mistake.

`m_move_it(state, box, room)` shows the shape every unigoal method has: it is handed the
**argument** and the **wanted value** as separate parameters. Beginners often expect the
whole `('loc', 'box1', 'kitchen')` tuple; you never see it.

## Way 1: one unigoal

```python
import gtpyhop
from boxes import domain, initial_state

with gtpyhop.PlannerSession(domain=domain, verbose=0) as session:
    result = session.find_plan(initial_state(), [('loc', 'box1', 'kitchen')])

print(result.plan)
```

```
[('move', 'box1', 'kitchen')]
```

You never mentioned `move`. You said where the box should be, and the planner chose the
action.

**A goal that is already true costs nothing.** GTPyhop checks before doing any work:

```python
with gtpyhop.PlannerSession(domain=domain, verbose=0) as session:
    result = session.find_plan(initial_state(), [('loc', 'box1', 'hall')])

# result.plan -> []          result.success -> True
```

An empty plan here means "nothing needed doing", not failure — always check
`result.success`.

## Way 2: two unigoals, one after the other

Want both boxes placed? Put two goals in the list:

```python
with gtpyhop.PlannerSession(domain=domain, verbose=0) as session:
    result = session.find_plan(initial_state(),
                               [('loc', 'box1', 'kitchen'),
                                ('loc', 'box2', 'study')])
```

```
[('move', 'box1', 'kitchen'), ('move', 'box2', 'study')]
```

This says: *achieve the first, then achieve the second.* That is a real commitment —
GTPyhop achieves them **in the order you wrote**, and nothing checks at the end that the
first is still true. Here the boxes don't interfere, so it doesn't matter. In a domain
where achieving one goal can undo another, it matters a great deal, and that is what the
next form is for.

## Way 3: one multigoal, split automatically

A **multigoal** says "all of these, together":

```python
g = gtpyhop.Multigoal('both_boxes', loc={'box1': 'kitchen', 'box2': 'study'})
```

A `Multigoal` holds state variables exactly the way a `State` does, so there are three
equivalent ways to build one — pick whichever reads best:

```python
g = gtpyhop.Multigoal('both_boxes')                      # then fill it in
g.loc = {}
g.loc['box1'] = 'kitchen'
g.loc['box2'] = 'study'

g = gtpyhop.Multigoal('both_boxes', loc={})              # or start it empty
g.loc['box1'] = 'kitchen'

g = gtpyhop.Multigoal('both_boxes',                      # or all at once
                      loc={'box1': 'kitchen', 'box2': 'study'})
```

A multigoal needs a method, and GTPyhop ships exactly one. It is **opt-in** — you must
declare it yourself:

```python
gtpyhop.set_current_domain(domain)                   # declarations go to this domain
gtpyhop.declare_multigoal_methods(gtpyhop.m_split_multigoal)

with gtpyhop.PlannerSession(domain=domain, verbose=0) as session:
    result = session.find_plan(initial_state(), [g])
```

```
[('move', 'box1', 'kitchen'), ('move', 'box2', 'study')]
```

The same plan as Way 2 — but arrived at differently, and that difference is the point.
`m_split_multigoal` looks at which goals are **not yet true**, turns each into a unigoal,
and then puts *the multigoal back on the list*:

```
[('loc','box1','kitchen'), ('loc','box2','study'), <the multigoal again>]
```

So after achieving them one by one, GTPyhop re-checks that they are **all** true
together. If achieving the second undid the first, the multigoal is still unsatisfied,
and the planner tries again. Two unigoals in a row never notice; a multigoal does.

## Way 4: one multigoal, your own method

`m_split_multigoal` is deliberately simple — its own docstring admits it "isn't smart
about choosing the order". When order matters, write your own method. A multigoal method
receives `(state, multigoal)`:

```python
custom = gtpyhop.Domain('boxes_custom')     # a fresh domain, so the two don't mix
gtpyhop.declare_actions(move)
gtpyhop.declare_unigoal_methods('loc', m_move_it)

def m_farthest_first(state, multigoal):
    steps = []
    for box in sorted(multigoal.loc, reverse=True):     # box2 before box1
        if state.loc[box] != multigoal.loc[box]:
            steps.append(('move', box, multigoal.loc[box]))
    return steps

gtpyhop.declare_multigoal_methods(m_farthest_first)

with gtpyhop.PlannerSession(domain=custom, verbose=0) as session:
    result = session.find_plan(initial_state(), [g])
```

```
[('move', 'box2', 'study'), ('move', 'box1', 'kitchen')]
```

Same goal, same actions — a different order, because you chose it.

Note the asymmetry with unigoal methods: multigoal methods are **not** registered per
state variable. `declare_multigoal_methods` adds to one flat list, and every method in
it is tried for every multigoal. Your method has to decide for itself whether it applies.

## What GTPyhop checks for you

When a method claims to achieve a goal, GTPyhop verifies that it did. Suppose a unigoal
method that quietly does nothing:

```python
def m_does_nothing(state, box, room):
    return []                    # claims success, moves nothing
```

```
Planning error: ("depth 0: method m_does_nothing didn't achieve", 'goal loc[box1] = kitchen')
```

The planner caught the lie. This is on by default, and it is why a goal is often safer
to state than the equivalent task: a task method that does the wrong thing produces a
wrong plan, whereas a goal method that does the wrong thing is caught.

You can switch it off for speed once a domain is trusted — but note **where** the switch
lives:

```python
import gtpyhop.main
gtpyhop.main.verify_goals = False       # NOT gtpyhop.verify_goals
```

Setting `gtpyhop.verify_goals` appears to work and silently does nothing: the flag is
not re-exported at package level, so you would only be creating a new, unread attribute.
With verification genuinely off, the broken method above returns an empty plan and
reports success — wrong, and quietly so.

## Traps

**A goal whose state variable was never declared.** Forget
`declare_unigoal_methods` and GTPyhop says so, whichever strategy you are using:

```
('colour', 'box1', 'red') isn't an action, task, unigoal, or multigoal.
Nothing named 'colour' is declared in domain 'boxes'. Declare it with
declare_actions, declare_task_methods, or -- if it is meant to be a goal --
declare_unigoal_methods('colour', ...).
```

This is an error rather than a quiet planning failure on purpose: left silent, it is
indistinguishable from "this problem has no solution", which sends you looking in
entirely the wrong place.

**A goal on a state variable the state doesn't have.** Declaring methods is not enough —
the variable must also exist in the initial state:

```
goal ('height', 'box1', 3) is about state variable 'height', which does not
exist in state 's0'. Initialise it before planning -- state.height = {} is
enough, since GTPyhop state variables are dictionaries keyed by the goal's
argument.
```

So initialise every variable you intend to write goals about, even to an empty dict. The
same message appears for a multigoal naming a variable the state lacks.

**The two method signatures differ.** A frequent source of confusion:

```python
def m_unigoal(state, arg, value): ...     # unigoal:  the pieces
def m_multigoal(state, multigoal): ...    # multigoal: the object
```

**Names are looked up in one order: action, then task, then unigoal.** If a state
variable shares a name with an action or task, the action or task wins and your goal is
never seen. Keep the namespaces distinct.

## Summary

| You want | Write | Method signature | Declared with |
|---|---|---|---|
| One variable to have one value | `('loc', 'box1', 'kitchen')` | `m(state, arg, value)` | `declare_unigoal_methods('loc', m)` |
| Several, in an order you pick | several unigoals in the list | — | — |
| Several, all true together | `Multigoal('g', loc={...})` | `m(state, multigoal)` | `declare_multigoal_methods(m)` |
| Several, split for you | the same `Multigoal` | — | `declare_multigoal_methods(gtpyhop.m_split_multigoal)` |

Worked examples in the bundled collections, by what each one actually declares:

| Example | Task methods | Unigoal | Multigoal | Good for seeing |
|---|:---:|:---:|:---:|---|
| `simple_hgn` | — | 1 | 1 | goals in the familiar travel domain |
| `logistics_hgn` | — | 4 | — | unigoals over *several* state variables, no multigoals |
| `blocks_hgn` | — | 1 | 1 | a domain driven entirely by goals |
| `blocks_gtn` | 2 | — | 1 | tasks and multigoals side by side |
| `blocks_goal_splitting` | — | 2 | 1 | `m_split_multigoal` doing the work |

See [All Examples](all_examples.md) for what each collection teaches.

If a goal fails and you cannot see why, the
[diagnostics tutorial](diagnostics_tutorial.md) shows how to make GTPyhop tell you.
