# ============================================================================
# IPC 2020 Total Order - Childsnack Domain
# ============================================================================

# ============================================================================
# FILE ORGANIZATION
# ----------------------------------------------------------------------------
# This file is organized into the following sections:
#   - Imports (with secure path handling)
#   - PROBLEMS (30)
#       - prob-snack from 10 (p01.hddl) to 500 (p30.hddl) children
# ============================================================================

# ============================================================================
# IMPORTS
# ============================================================================

# ------ Smart GTPyhop import strategy - tries PyPI first, falls back to local
try:
    from gtpyhop import State, Multigoal
except ImportError:
    # Fallback to local development
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
    from gtpyhop import State, Multigoal

# ============================================================================
# PROBLEMS (30)
# ============================================================================

# ===== prob-snack --------------------------------------------------- p01.hddl
state_childsnack_p01 = State("snack_p01_initial_state")

# types:
state_childsnack_p01.bread_portions = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7","bread8","bread9","bread10"}
state_childsnack_p01.children = {"child1","child2","child3","child4","child5","child6","child7","child8","child9","child10"}
state_childsnack_p01.content_portions = {"content1","content2","content3","content4","content5","content6","content7","content8","content9","content10"}
state_childsnack_p01.places = {"table1","table2","table3"}
state_childsnack_p01.sandwiches = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13"}
state_childsnack_p01.trays = {"tray1","tray2","tray3"}

# predicates:
state_childsnack_p01.allergic_gluten = {"child1","child10","child3","child4"}
state_childsnack_p01.at = {"tray1":"kitchen","tray2":"kitchen","tray3":"kitchen"}
state_childsnack_p01.at_kitchen_bread = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7",
                                    "bread8","bread9","bread10"}
state_childsnack_p01.at_kitchen_content = {"content1","content2","content3","content4","content5",
                                      "content6","content7","content8","content9","content10"}
state_childsnack_p01.at_kitchen_sandwich = set()
state_childsnack_p01.not_allergic_gluten = {"child2","child5","child6","child7","child8","child9"}
state_childsnack_p01.notexist = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13"}
state_childsnack_p01.no_gluten_bread = {"bread2","bread9","bread4","bread8"}
state_childsnack_p01.no_gluten_content = {"content2","content8","content4","content1"}
state_childsnack_p01.no_gluten_sandwich = set()
state_childsnack_p01.ontray = {}
state_childsnack_p01.served = {}
state_childsnack_p01.waiting = {"child1":"table2","child2":"table1","child3":"table1","child4":"table2",
                           "child5":"table3","child6":"table3","child7":"table3","child8":"table2",
                           "child9":"table1","child10":"table3"}

# Set goal from the :htn :ordered-subtasks in p01.hddl
htn_ordered_subtask_childsnack_p01 = Multigoal("goal_childsnack_p01",served=state_childsnack_p01.waiting)

# Set goal state from p01.hddl
# 	(:goal (and
# (served child1)
# (served child2)
# (served child3)
# (served child4)
# (served child5)
# (served child6)
# (served child7)
# (served child8)
# (served child9)
# (served child10)
# 	))
goal_childsnack_p01 = state_childsnack_p01.waiting

# ===== prob-snack --------------------------------------------------- p02.hddl
state_childsnack_p02 = State("snack_p02_initial_state")

# types:
state_childsnack_p02.bread_portions = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7","bread8","bread9","bread10"}
state_childsnack_p02.children = {"child1","child2","child3","child4","child5","child6","child7","child8","child9","child10"}
state_childsnack_p02.content_portions = {"content1","content2","content3","content4","content5","content6","content7","content8","content9","content10"}
state_childsnack_p02.places = {"table1","table2","table3"}
state_childsnack_p02.sandwiches = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13"}
state_childsnack_p02.trays = {"tray1","tray2","tray3"}

# predicates:
state_childsnack_p02.allergic_gluten = {"child9","child2","child3","child7"}
state_childsnack_p02.at = {"tray1":"kitchen","tray2":"kitchen","tray3":"kitchen"}
state_childsnack_p02.at_kitchen_bread = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7",
                                    "bread8","bread9","bread10"}
state_childsnack_p02.at_kitchen_content = {"content1","content2","content3","content4","content5",
                                      "content6","content7","content8","content9","content10"}
state_childsnack_p02.at_kitchen_sandwich = set()
state_childsnack_p02.not_allergic_gluten = {"child1","child10","child4","child5","child6","child8"}
state_childsnack_p02.notexist = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13"}
state_childsnack_p02.no_gluten_bread = {"bread6","bread2","bread8","bread7"}
state_childsnack_p02.no_gluten_content = {"content5","content6","content2","content8"}
state_childsnack_p02.no_gluten_sandwich = set()
state_childsnack_p02.ontray = {}
state_childsnack_p02.served = {}
state_childsnack_p02.waiting = {"child1":"table1","child2":"table1","child3":"table1","child4":"table3",
                           "child5":"table2","child6":"table2","child7":"table1","child8":"table2",
                           "child9":"table2","child10":"table1"}

# Set goal from the :htn :ordered-subtasks in p02.hddl
htn_ordered_subtask_childsnack_p02 = Multigoal("goal_childsnack_p02",served=state_childsnack_p02.waiting)

# Set goal state from p02.hddl
# 	(:goal (and
# (served child1)
# (served child2)
# (served child3)
# (served child4)
# (served child5)
# (served child6)
# (served child7)
# (served child8)
# (served child9)
# (served child10)
# 	))
goal_childsnack_p02 = state_childsnack_p02.waiting

# ===== prob-snack --------------------------------------------------- p03.hddl
state_childsnack_p03 = State("snack_p03_initial_state")

# types:
state_childsnack_p03.bread_portions = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7","bread8","bread9","bread10","bread11"}
state_childsnack_p03.children = {"child1","child2","child3","child4","child5","child6","child7","child8","child9","child10","child11"}
state_childsnack_p03.content_portions = {"content1","content2","content3","content4","content5","content6","content7","content8","content9","content10","content11"}
state_childsnack_p03.places = {"table1","table2","table3"}
state_childsnack_p03.sandwiches = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15"}
state_childsnack_p03.trays = {"tray1","tray2","tray3"}

# predicates:
state_childsnack_p03.allergic_gluten = {"child1","child3","child11","child5"}
state_childsnack_p03.at = {"tray1":"kitchen","tray2":"kitchen","tray3":"kitchen"}
state_childsnack_p03.at_kitchen_bread = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7",
                                    "bread8","bread9","bread10","bread11"}
state_childsnack_p03.at_kitchen_content = {"content1","content2","content3","content4","content5",
                                      "content6","content7","content8","content9","content10","content11"}
state_childsnack_p03.at_kitchen_sandwich = set()
state_childsnack_p03.not_allergic_gluten = {"child2","child4","child6","child7","child8","child9","child10"}
state_childsnack_p03.notexist = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15"}
state_childsnack_p03.no_gluten_bread = {"bread3","bread10","bread4","bread9"}
state_childsnack_p03.no_gluten_content = {"content2","content9","content5","content11"}
state_childsnack_p03.no_gluten_sandwich = set()
state_childsnack_p03.ontray = {}
state_childsnack_p03.served = {}
state_childsnack_p03.waiting = {"child1":"table2","child2":"table1","child3":"table1","child4":"table2",
                           "child5":"table3","child6":"table3","child7":"table3","child8":"table2",
                           "child9":"table1","child10":"table3","child11":"table1"}

# Set goal from the :htn :ordered-subtasks in p03.hddl
htn_ordered_subtask_childsnack_p03 = Multigoal("goal_childsnack_p03",served=state_childsnack_p03.waiting)

# Set goal state from p03.hddl
# 	(:goal (and
# (served child1)
# (served child2)
# (served child3)
# (served child4)
# (served child5)
# (served child6)
# (served child7)
# (served child8)
# (served child9)
# (served child10)
# (served child11)
# 	))
goal_childsnack_p03 = state_childsnack_p03.waiting

# ===== prob-snack --------------------------------------------------- p04.hddl
state_childsnack_p04 = State("snack_p04_initial_state")

# types:
state_childsnack_p04.bread_portions = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7","bread8","bread9","bread10","bread11","bread12"}
state_childsnack_p04.children = {"child1","child2","child3","child4","child5","child6","child7","child8","child9","child10","child11","child12"}
state_childsnack_p04.content_portions = {"content1","content2","content3","content4","content5","content6","content7","content8","content9","content10","content11","content12"}
state_childsnack_p04.places = {"table1","table2","table3"}
state_childsnack_p04.sandwiches = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16"}
state_childsnack_p04.trays = {"tray1","tray2","tray3"}

# predicates:
state_childsnack_p04.allergic_gluten = {"child12","child1","child3","child5"}
state_childsnack_p04.at = {"tray1":"kitchen","tray2":"kitchen","tray3":"kitchen"}
state_childsnack_p04.at_kitchen_bread = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7",
                                    "bread8","bread9","bread10","bread11","bread12"}
state_childsnack_p04.at_kitchen_content = {"content1","content2","content3","content4","content5",
                                      "content6","content7","content8","content9","content10","content11","content12"}
state_childsnack_p04.at_kitchen_sandwich = set()
state_childsnack_p04.not_allergic_gluten = {"child2","child11","child4","child6","child7","child8","child9","child10"}
state_childsnack_p04.notexist = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16"}
state_childsnack_p04.no_gluten_bread = {"bread3","bread11","bread4","bread5"}
state_childsnack_p04.no_gluten_content = {"content2","content9","content5","content12"}
state_childsnack_p04.no_gluten_sandwich = set()
state_childsnack_p04.ontray = {}
state_childsnack_p04.served = {}
state_childsnack_p04.waiting = {"child1":"table2","child2":"table1","child3":"table1","child4":"table2",
                           "child5":"table3","child6":"table3","child7":"table3","child8":"table2",
                           "child9":"table1","child10":"table3","child11":"table1","child12":"table1"}

# Set goal from the :htn :ordered-subtasks in p04.hddl
htn_ordered_subtask_childsnack_p04 = Multigoal("goal_childsnack_p04",served=state_childsnack_p04.waiting)

# Set goal state from p04.hddl
# 	(:goal (and
# (served child1)
# (served child2)
# (served child3)
# (served child4)
# (served child5)
# (served child6)
# (served child7)
# (served child8)
# (served child9)
# (served child10)
# (served child11)
# (served child12)
# 	))
goal_childsnack_p04 = state_childsnack_p04.waiting

# ===== prob-snack --------------------------------------------------- p05.hddl
state_childsnack_p05 = State("snack_p05_initial_state")

# types:
state_childsnack_p05.bread_portions = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7","bread8","bread9","bread10","bread11","bread12","bread13"}
state_childsnack_p05.children = {"child1","child2","child3","child4","child5","child6","child7","child8","child9","child10","child11","child12","child13"}
state_childsnack_p05.content_portions = {"content1","content2","content3","content4","content5","content6","content7","content8","content9","content10","content11","content12","content13"}
state_childsnack_p05.places = {"table1","table2","table3"}
state_childsnack_p05.sandwiches = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17"}
state_childsnack_p05.trays = {"tray1","tray2","tray3"}

# predicates:
state_childsnack_p05.allergic_gluten = {"child8","child1","child12","child4","child13"}
state_childsnack_p05.at = {"tray1":"kitchen","tray2":"kitchen","tray3":"kitchen"}
state_childsnack_p05.at_kitchen_bread = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7",
                                    "bread8","bread9","bread10","bread11","bread12","bread13"}
state_childsnack_p05.at_kitchen_content = {"content1","content2","content3","content4","content5",
                                      "content6","content7","content8","content9","content10","content11","content12","content13"}
state_childsnack_p05.at_kitchen_sandwich = set()
state_childsnack_p05.not_allergic_gluten = {"child2","child3","child5","child6","child7","child9","child10","child11"}
state_childsnack_p05.notexist = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17"}
state_childsnack_p05.no_gluten_bread = {"bread3","bread12","bread5","bread11","bread1"}
state_childsnack_p05.no_gluten_content = {"content11","content6","content2","content10","content4"}
state_childsnack_p05.no_gluten_sandwich = set()
state_childsnack_p05.ontray = {}
state_childsnack_p05.served = {}
state_childsnack_p05.waiting = {"child1":"table2","child2":"table3","child3":"table3","child4":"table3",
                           "child5":"table2","child6":"table1","child7":"table3","child8":"table1",
                           "child9":"table1","child10":"table3","child11":"table1","child12":"table1","child13":"table1"}

# Set goal from the :htn :ordered-subtasks in p05.hddl
htn_ordered_subtask_childsnack_p05 = Multigoal("goal_childsnack_p05",served=state_childsnack_p05.waiting)

# Set goal state from p05.hddl
# 	(:goal (and
# (served child1)
# (served child2)
# (served child3)
# (served child4)
# (served child5)
# (served child6)
# (served child7)
# (served child8)
# (served child9)
# (served child10)
# (served child11)
# (served child12)
# (served child13)
# 	))
goal_childsnack_p05 = state_childsnack_p05.waiting

# ===== prob-snack --------------------------------------------------- p06.hddl
state_childsnack_p06 = State("snack_p06_initial_state")

# types:
state_childsnack_p06.bread_portions = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7","bread8","bread9","bread10","bread11","bread12","bread13"}
state_childsnack_p06.children = {"child1","child2","child3","child4","child5","child6","child7","child8","child9","child10","child11","child12","child13"}
state_childsnack_p06.content_portions = {"content1","content2","content3","content4","content5","content6","content7","content8","content9","content10","content11","content12","content13"}
state_childsnack_p06.places = {"table1","table2","table3"}
state_childsnack_p06.sandwiches = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17"}
state_childsnack_p06.trays = {"tray1","tray2","tray3"}

# predicates:
state_childsnack_p06.allergic_gluten = {"child12","child1","child2","child3","child11"}
state_childsnack_p06.at = {"tray1":"kitchen","tray2":"kitchen","tray3":"kitchen"}
state_childsnack_p06.at_kitchen_bread = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7",
                                    "bread8","bread9","bread10","bread11","bread12","bread13"}
state_childsnack_p06.at_kitchen_content = {"content1","content2","content3","content4","content5",
                                      "content6","content7","content8","content9","content10","content11","content12","content13"}
state_childsnack_p06.at_kitchen_sandwich = set()
state_childsnack_p06.not_allergic_gluten = {"child13","child10","child4","child5","child6","child7","child8","child9"}
state_childsnack_p06.notexist = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17"}
state_childsnack_p06.no_gluten_bread = {"bread8","bread3","bread11","bread10","bread5"}
state_childsnack_p06.no_gluten_content = {"content9","content3","content12","content11","content7"}
state_childsnack_p06.no_gluten_sandwich = set()
state_childsnack_p06.ontray = {}
state_childsnack_p06.served = {}
state_childsnack_p06.waiting = {"child1":"table3","child2":"table2","child3":"table2","child4":"table1",
                           "child5":"table2","child6":"table2","child7":"table1","child8":"table2",
                           "child9":"table1","child10":"table1","child11":"table3","child12":"table3","child13":"table2"}

# Set goal from the :htn :ordered-subtasks in p06.hddl
htn_ordered_subtask_childsnack_p06 = Multigoal("goal_childsnack_p06",served=state_childsnack_p06.waiting)

# Set goal state from p06.hddl
# 	(:goal (and
# (served child1)
# (served child2)
# (served child3)
# (served child4)
# (served child5)
# (served child6)
# (served child7)
# (served child8)
# (served child9)
# (served child10)
# (served child11)
# (served child12)
# (served child13)
# 	))
goal_childsnack_p06 = state_childsnack_p06.waiting

# ===== prob-snack --------------------------------------------------- p07.hddl
state_childsnack_p07 = State("snack_p07_initial_state")

# types:
state_childsnack_p07.bread_portions = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7","bread8","bread9","bread10","bread11","bread12","bread13","bread14"}
state_childsnack_p07.children = {"child1","child2","child3","child4","child5","child6","child7","child8","child9","child10","child11","child12","child13","child14"}
state_childsnack_p07.content_portions = {"content1","content2","content3","content4","content5","content6","content7","content8","content9","content10","content11","content12","content13","content14"}
state_childsnack_p07.places = {"table1","table2","table3"}
state_childsnack_p07.sandwiches = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19"}
state_childsnack_p07.trays = {"tray1","tray2","tray3"}

# predicates:
state_childsnack_p07.allergic_gluten = {"child8","child1","child4","child5","child14"}
state_childsnack_p07.at = {"tray1":"kitchen","tray2":"kitchen","tray3":"kitchen"}
state_childsnack_p07.at_kitchen_bread = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7",
                                    "bread8","bread9","bread10","bread11","bread12","bread13","bread14"}
state_childsnack_p07.at_kitchen_content = {"content1","content2","content3","content4","content5",
                                      "content6","content7","content8","content9","content10","content11","content12","content13","content14"}
state_childsnack_p07.at_kitchen_sandwich = set()
state_childsnack_p07.not_allergic_gluten = {"child12","child13","child2","child3","child6","child7","child9","child10","child11"}
state_childsnack_p07.notexist = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19"}
state_childsnack_p07.no_gluten_bread = {"bread3","bread13","bread5","bread6","bread2"}
state_childsnack_p07.no_gluten_content = {"content12","content7","content2","content11","content5"}
state_childsnack_p07.no_gluten_sandwich = set()
state_childsnack_p07.ontray = {}
state_childsnack_p07.served = {}
state_childsnack_p07.waiting = {"child1":"table2","child2":"table3","child3":"table3","child4":"table3",
                           "child5":"table2","child6":"table1","child7":"table3","child8":"table1",
                           "child9":"table1","child10":"table3","child11":"table1","child12":"table1","child13":"table1","child14":"table2"}

# Set goal from the :htn :ordered-subtasks in p07.hddl
htn_ordered_subtask_childsnack_p07 = Multigoal("goal_childsnack_p07",served=state_childsnack_p07.waiting)

# Set goal state from p07.hddl
# 	(:goal (and
# (served child1)
# (served child2)
# (served child3)
# (served child4)
# (served child5)
# (served child6)
# (served child7)
# (served child8)
# (served child9)
# (served child10)
# (served child11)
# (served child12)
# (served child13)
# (served child14)
# 	))
goal_childsnack_p07 = state_childsnack_p07.waiting

# ===== prob-snack --------------------------------------------------- p08.hddl
state_childsnack_p08 = State("snack_p08_initial_state")

# types:
state_childsnack_p08.bread_portions = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7","bread8","bread9","bread10","bread11","bread12","bread13","bread14"}
state_childsnack_p08.children = {"child1","child2","child3","child4","child5","child6","child7","child8","child9","child10","child11","child12","child13","child14"}
state_childsnack_p08.content_portions = {"content1","content2","content3","content4","content5","content6","content7","content8","content9","content10","content11","content12","content13","content14"}
state_childsnack_p08.places = {"table1","table2","table3"}
state_childsnack_p08.sandwiches = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19"}
state_childsnack_p08.trays = {"tray1","tray2","tray3"}

# predicates:
state_childsnack_p08.allergic_gluten = {"child12","child13","child3","child14","child1"}
state_childsnack_p08.at = {"tray1":"kitchen","tray2":"kitchen","tray3":"kitchen"}
state_childsnack_p08.at_kitchen_bread = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7",
                                    "bread8","bread9","bread10","bread11","bread12","bread13","bread14"}
state_childsnack_p08.at_kitchen_content = {"content1","content2","content3","content4","content5",
                                      "content6","content7","content8","content9","content10","content11","content12","content13","content14"}
state_childsnack_p08.at_kitchen_sandwich = set()
state_childsnack_p08.not_allergic_gluten = {"child2","child11","child4","child5","child6","child7","child8","child9","child10"}
state_childsnack_p08.notexist = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19"}
state_childsnack_p08.no_gluten_bread = {"bread9","bread3","bread12","bread11","bread5"}
state_childsnack_p08.no_gluten_content = {"content10","content3","content13","content4","content7"}
state_childsnack_p08.no_gluten_sandwich = set()
state_childsnack_p08.ontray = {}
state_childsnack_p08.served = {}
state_childsnack_p08.waiting = {"child1":"table3","child2":"table2","child3":"table2","child4":"table1",
                           "child5":"table2","child6":"table2","child7":"table1","child8":"table2",
                           "child9":"table1","child10":"table1","child11":"table3","child12":"table3","child13":"table2","child14":"table3"}

# Set goal from the :htn :ordered-subtasks in p08.hddl
htn_ordered_subtask_childsnack_p08 = Multigoal("goal_childsnack_p08",served=state_childsnack_p08.waiting)

# Set goal state from p08.hddl
# 	(:goal (and
# (served child1)
# (served child2)
# (served child3)
# (served child4)
# (served child5)
# (served child6)
# (served child7)
# (served child8)
# (served child9)
# (served child10)
# (served child11)
# (served child12)
# (served child13)
# (served child14)
# 	))
goal_childsnack_p08 = state_childsnack_p08.waiting

# ===== prob-snack --------------------------------------------------- p09.hddl
state_childsnack_p09 = State("snack_p09_initial_state")

# types:
state_childsnack_p09.bread_portions = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7","bread8","bread9","bread10","bread11","bread12","bread13","bread14","bread15"}
state_childsnack_p09.children = {"child1","child2","child3","child4","child5","child6","child7","child8","child9","child10","child11","child12","child13","child14","child15"}
state_childsnack_p09.content_portions = {"content1","content2","content3","content4","content5","content6","content7","content8","content9","content10","content11","content12","content13","content14","content15"}
state_childsnack_p09.places = {"table1","table2","table3"}
state_childsnack_p09.sandwiches = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19","sandw20"}
state_childsnack_p09.trays = {"tray1","tray2","tray3"}

# predicates:
state_childsnack_p09.allergic_gluten = {"child1","child10","child5","child7","child8","child9"}
state_childsnack_p09.at = {"tray1":"kitchen","tray2":"kitchen","tray3":"kitchen"}
state_childsnack_p09.at_kitchen_bread = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7",
                                    "bread8","bread9","bread10","bread11","bread12","bread13","bread14","bread15"}
state_childsnack_p09.at_kitchen_content = {"content1","content2","content3","content4","content5",
                                      "content6","content7","content8","content9","content10","content11","content12","content13","content14","content15"}
state_childsnack_p09.at_kitchen_sandwich = set()
state_childsnack_p09.not_allergic_gluten = {"child12","child13","child2","child3","child4","child14","child6","child15","child11"}
state_childsnack_p09.notexist = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19","sandw20"}
state_childsnack_p09.no_gluten_bread = {"bread3","bread14","bread6","bread13","bread2","bread9"}
state_childsnack_p09.no_gluten_content = {"content8","content2","content13","content5","content1","content4"}
state_childsnack_p09.no_gluten_sandwich = set()
state_childsnack_p09.ontray = {}
state_childsnack_p09.served = {}
state_childsnack_p09.waiting = {"child1":"table3","child2":"table2","child3":"table1","child4":"table3",
                           "child5":"table1","child6":"table1","child7":"table3","child8":"table1",
                           "child9":"table1","child10":"table1","child11":"table2","child12":"table3","child13":"table1","child14":"table2","child15":"table2"}

# Set goal from the :htn :ordered-subtasks in p09.hddl
htn_ordered_subtask_childsnack_p09 = Multigoal("goal_childsnack_p09",served=state_childsnack_p09.waiting)

# Set goal state from p09.hddl
# 	(:goal (and
# (served child1)
# (served child2)
# (served child3)
# (served child4)
# (served child5)
# (served child6)
# (served child7)
# (served child8)
# (served child9)
# (served child10)
# (served child11)
# (served child12)
# (served child13)
# (served child14)
# (served child15)
# 	))
goal_childsnack_p09 = state_childsnack_p09.waiting

# ===== prob-snack --------------------------------------------------- p10.hddl
state_childsnack_p10 = State("snack_p10_initial_state")

# types:
state_childsnack_p10.bread_portions = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7","bread8","bread9","bread10","bread11","bread12","bread13","bread14","bread15"}
state_childsnack_p10.children = {"child1","child2","child3","child4","child5","child6","child7","child8","child9","child10","child11","child12","child13","child14","child15"}
state_childsnack_p10.content_portions = {"content1","content2","content3","content4","content5","content6","content7","content8","content9","content10","content11","content12","content13","content14","content15"}
state_childsnack_p10.places = {"table1","table2","table3"}
state_childsnack_p10.sandwiches = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19","sandw20"}
state_childsnack_p10.trays = {"tray1","tray2","tray3"}

# predicates:
state_childsnack_p10.allergic_gluten = {"child2","child11","child5","child15","child10","child3"}
state_childsnack_p10.at = {"tray1":"kitchen","tray2":"kitchen","tray3":"kitchen"}
state_childsnack_p10.at_kitchen_bread = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7",
                                    "bread8","bread9","bread10","bread11","bread12","bread13","bread14","bread15"}
state_childsnack_p10.at_kitchen_content = {"content1","content2","content3","content4","content5",
                                      "content6","content7","content8","content9","content10","content11","content12","content13","content14","content15"}
state_childsnack_p10.at_kitchen_sandwich = set()
state_childsnack_p10.not_allergic_gluten = {"child12","child1","child4","child14","child6","child7","child8","child9","child13"}
state_childsnack_p10.notexist = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19","sandw20"}
state_childsnack_p10.no_gluten_bread = {"bread9","bread3","bread13","bread12","bread6","bread7"}
state_childsnack_p10.no_gluten_content = {"content4","content15","content14","content9","content3","content10"}
state_childsnack_p10.no_gluten_sandwich = set()
state_childsnack_p10.ontray = {}
state_childsnack_p10.served = {}
state_childsnack_p10.waiting = {"child1":"table1","child2":"table2","child3":"table2","child4":"table1",
                           "child5":"table2","child6":"table1","child7":"table1","child8":"table3",
                           "child9":"table3","child10":"table2","child11":"table3","child12":"table2","child13":"table2","child14":"table2","child15":"table2"}

# Set goal from the :htn :ordered-subtasks in p10.hddl
htn_ordered_subtask_childsnack_p10 = Multigoal("goal_childsnack_p10",served=state_childsnack_p10.waiting)

# Set goal state from p10.hddl
# 	(:goal (and
# (served child1)
# (served child2)
# (served child3)
# (served child4)
# (served child5)
# (served child6)
# (served child7)
# (served child8)
# (served child9)
# (served child10)
# (served child11)
# (served child12)
# (served child13)
# (served child14)
# (served child15)
# 	))
goal_childsnack_p10 = state_childsnack_p10.waiting

# ===== prob-snack --------------------------------------------------- p11.hddl
state_childsnack_p11 = State("snack_p11_initial_state")

# types:
state_childsnack_p11.bread_portions = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7","bread8","bread9","bread10","bread11","bread12","bread13","bread14","bread15","bread16"}
state_childsnack_p11.children = {"child1","child2","child3","child4","child5","child6","child7","child8","child9","child10","child11","child12","child13","child14","child15","child16"}
state_childsnack_p11.content_portions = {"content1","content2","content3","content4","content5","content6","content7","content8","content9","content10","content11","content12","content13","content14","content15","content16"}
state_childsnack_p11.places = {"table1","table2","table3"}
state_childsnack_p11.sandwiches = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19","sandw20","sandw21"}
state_childsnack_p11.trays = {"tray1","tray2","tray3"}

# predicates:
state_childsnack_p11.allergic_gluten = {"child1","child10","child11","child5","child7","child9"}
state_childsnack_p11.at = {"tray1":"kitchen","tray2":"kitchen","tray3":"kitchen"}
state_childsnack_p11.at_kitchen_bread = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7",
                                    "bread8","bread9","bread10","bread11","bread12","bread13","bread14","bread15","bread16"}
state_childsnack_p11.at_kitchen_content = {"content1","content2","content3","content4","content5",
                                      "content6","content7","content8","content9","content10","content11","content12","content13","content14","content15","content16"}
state_childsnack_p11.at_kitchen_sandwich = set()
state_childsnack_p11.not_allergic_gluten = {"child12","child13","child2","child3","child4","child14","child6","child15","child8","child16"}
state_childsnack_p11.notexist = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19","sandw20","sandw21"}
state_childsnack_p11.no_gluten_bread = {"bread4","bread15","bread6","bread7","bread2","bread9"}
state_childsnack_p11.no_gluten_content = {"content8","content3","content14","content6","content1","content4"}
state_childsnack_p11.no_gluten_sandwich = set()
state_childsnack_p11.ontray = {}
state_childsnack_p11.served = {}
state_childsnack_p11.waiting = {"child1":"table3","child2":"table2","child3":"table1","child4":"table3",
                           "child5":"table1","child6":"table1","child7":"table3","child8":"table1",
                           "child9":"table1","child10":"table1","child11":"table2","child12":"table3","child13":"table1","child14":"table2","child15":"table2","child16":"table3"}

# Set goal from the :htn :ordered-subtasks in p11.hddl
htn_ordered_subtask_childsnack_p11 = Multigoal("goal_childsnack_p11",served=state_childsnack_p11.waiting)

# Set goal state from p11.hddl
# 	(:goal (and
# (served child1)
# (served child2)
# (served child3)
# (served child4)
# (served child5)
# (served child6)
# (served child7)
# (served child8)
# (served child9)
# (served child10)
# (served child11)
# (served child12)
# (served child13)
# (served child14)
# (served child15)
# (served child16)
# 	))
goal_childsnack_p11 = state_childsnack_p11.waiting

# ===== prob-snack --------------------------------------------------- p12.hddl
state_childsnack_p12 = State("snack_p12_initial_state")

# types:
state_childsnack_p12.bread_portions = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7","bread8","bread9","bread10","bread11","bread12","bread13","bread14","bread15","bread16"}
state_childsnack_p12.children = {"child1","child2","child3","child4","child5","child6","child7","child8","child9","child10","child11","child12","child13","child14","child15","child16"}
state_childsnack_p12.content_portions = {"content1","content2","content3","content4","content5","content6","content7","content8","content9","content10","content11","content12","content13","content14","content15","content16"}
state_childsnack_p12.places = {"table1","table2","table3"}
state_childsnack_p12.sandwiches = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19","sandw20","sandw21"}
state_childsnack_p12.trays = {"tray1","tray2","tray3"}

# predicates:
state_childsnack_p12.allergic_gluten = {"child2","child3","child16","child5","child6","child11"}
state_childsnack_p12.at = {"tray1":"kitchen","tray2":"kitchen","tray3":"kitchen"}
state_childsnack_p12.at_kitchen_bread = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7",
                                    "bread8","bread9","bread10","bread11","bread12","bread13","bread14","bread15","bread16"}
state_childsnack_p12.at_kitchen_content = {"content1","content2","content3","content4","content5",
                                      "content6","content7","content8","content9","content10","content11","content12","content13","content14","content15","content16"}
state_childsnack_p12.at_kitchen_sandwich = set()
state_childsnack_p12.not_allergic_gluten = {"child12","child1","child10","child4","child14","child7","child8","child9","child15","child13"}
state_childsnack_p12.notexist = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19","sandw20","sandw21"}
state_childsnack_p12.no_gluten_bread = {"bread10","bread3","bread14","bread13","bread6","bread8"}
state_childsnack_p12.no_gluten_content = {"content4","content16","content5","content10","content3","content11"}
state_childsnack_p12.no_gluten_sandwich = set()
state_childsnack_p12.ontray = {}
state_childsnack_p12.served = {}
state_childsnack_p12.waiting = {"child1":"table1","child2":"table2","child3":"table2","child4":"table1",
                           "child5":"table2","child6":"table1","child7":"table1","child8":"table3",
                           "child9":"table3","child10":"table2","child11":"table3","child12":"table2","child13":"table2","child14":"table2","child15":"table2","child16":"table3"}

# Set goal from the :htn :ordered-subtasks in p12.hddl
htn_ordered_subtask_childsnack_p12 = Multigoal("goal_childsnack_p12",served=state_childsnack_p12.waiting)

# Set goal state from p12.hddl
# 	(:goal (and
# (served child1)
# (served child2)
# (served child3)
# (served child4)
# (served child5)
# (served child6)
# (served child7)
# (served child8)
# (served child9)
# (served child10)
# (served child11)
# (served child12)
# (served child13)
# (served child14)
# (served child15)
# (served child16)
# 	))
goal_childsnack_p12 = state_childsnack_p12.waiting

# ===== prob-snack --------------------------------------------------- p13.hddl
state_childsnack_p13 = State("snack_p13_initial_state")

# types:
state_childsnack_p13.bread_portions = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7","bread8","bread9","bread10","bread11","bread12","bread13","bread14","bread15","bread16","bread17"}
state_childsnack_p13.children = {"child1","child2","child3","child4","child5","child6","child7","child8","child9","child10","child11","child12","child13","child14","child15","child16","child17"}
state_childsnack_p13.content_portions = {"content1","content2","content3","content4","content5","content6","content7","content8","content9","content10","content11","content12","content13","content14","content15","content16","content17"}
state_childsnack_p13.places = {"table1","table2","table3"}
state_childsnack_p13.sandwiches = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19","sandw20","sandw21","sandw22","sandw23"}
state_childsnack_p13.trays = {"tray1","tray2","tray3","tray4"}

# predicates:
state_childsnack_p13.allergic_gluten = {"child2","child11","child4","child17","child6","child5"}
state_childsnack_p13.at = {"tray1":"kitchen","tray2":"kitchen","tray3":"kitchen","tray4":"kitchen"}
state_childsnack_p13.at_kitchen_bread = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7",
                                    "bread8","bread9","bread10","bread11","bread12","bread13","bread14","bread15","bread16","bread17"}
state_childsnack_p13.at_kitchen_content = {"content1","content2","content3","content4","content5",
                                      "content6","content7","content8","content9","content10","content11","content12","content13","content14","content15","content16","content17"}
state_childsnack_p13.at_kitchen_sandwich = set()
state_childsnack_p13.not_allergic_gluten = {"child12","child1","child10","child3","child16","child14","child7","child8","child9","child15","child13"}
state_childsnack_p13.notexist = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19","sandw20","sandw21","sandw22","sandw23"}
state_childsnack_p13.no_gluten_bread = {"bread10","bread4","bread15","bread13","bread7","bread8"}
state_childsnack_p13.no_gluten_content = {"content4","content17","content5","content10","content3","content12"}
state_childsnack_p13.no_gluten_sandwich = set()
state_childsnack_p13.ontray = {}
state_childsnack_p13.served = {}
state_childsnack_p13.waiting = {"child1":"table1","child2":"table2","child3":"table2","child4":"table1",
                           "child5":"table2","child6":"table1","child7":"table1","child8":"table3",
                           "child9":"table3","child10":"table2","child11":"table3","child12":"table2","child13":"table2","child14":"table2","child15":"table2","child16":"table3","child17":"table1"}

# Set goal from the :htn :ordered-subtasks in p13.hddl
htn_ordered_subtask_childsnack_p13 = Multigoal("goal_childsnack_p13",served=state_childsnack_p13.waiting)

# Set goal state from p13.hddl
# 	(:goal (and
# (served child1)
# (served child2)
# (served child3)
# (served child4)
# (served child5)
# (served child6)
# (served child7)
# (served child8)
# (served child9)
# (served child10)
# (served child11)
# (served child12)
# (served child13)
# (served child14)
# (served child15)
# (served child16)
# (served child17)
# 	))
goal_childsnack_p13 = state_childsnack_p13.waiting

# ===== prob-snack --------------------------------------------------- p14.hddl
state_childsnack_p14 = State("snack_p14_initial_state")

# types:
state_childsnack_p14.bread_portions = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7","bread8","bread9","bread10","bread11","bread12","bread13","bread14","bread15","bread16","bread17","bread18"}
state_childsnack_p14.children = {"child1","child2","child3","child4","child5","child6","child7","child8","child9","child10","child11","child12","child13","child14","child15","child16","child17","child18"}
state_childsnack_p14.content_portions = {"content1","content2","content3","content4","content5","content6","content7","content8","content9","content10","content11","content12","content13","content14","content15","content16","content17","content18"}
state_childsnack_p14.places = {"table1","table2","table3"}
state_childsnack_p14.sandwiches = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19","sandw20","sandw21","sandw22","sandw23","sandw24"}
state_childsnack_p14.trays = {"tray1","tray2","tray3","tray4"}

# predicates:
state_childsnack_p14.allergic_gluten = {"child12","child1","child14","child13","child8","child9","child18"}
state_childsnack_p14.at = {"tray1":"kitchen","tray2":"kitchen","tray3":"kitchen","tray4":"kitchen"}
state_childsnack_p14.at_kitchen_bread = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7",
                                    "bread8","bread9","bread10","bread11","bread12","bread13","bread14","bread15","bread16","bread17","bread18"}
state_childsnack_p14.at_kitchen_content = {"content1","content2","content3","content4","content5",
                                      "content6","content7","content8","content9","content10","content11","content12","content13","content14","content15","content16","content17","content18"}
state_childsnack_p14.at_kitchen_sandwich = set()
state_childsnack_p14.not_allergic_gluten = {"child2","child3","child4","child5","child6","child7","child15","child10","child11","child16","child17"}
state_childsnack_p14.notexist = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19","sandw20","sandw21","sandw22","sandw23","sandw24"}
state_childsnack_p14.no_gluten_bread = {"bread4","bread17","bread7","bread8","bread2","bread11","bread6"}
state_childsnack_p14.no_gluten_content = {"content3","content17","content7","content1","content5","content9","content4"}
state_childsnack_p14.no_gluten_sandwich = set()
state_childsnack_p14.ontray = {}
state_childsnack_p14.served = {}
state_childsnack_p14.waiting = {"child1":"table3","child2":"table1","child3":"table1","child4":"table3",
                           "child5":"table1","child6":"table1","child7":"table1","child8":"table2",
                           "child9":"table3","child10":"table1","child11":"table2","child12":"table2","child13":"table3","child14":"table3","child15":"table1","child16":"table2","child17":"table2","child18":"table3"}

# Set goal from the :htn :ordered-subtasks in p14.hddl
htn_ordered_subtask_childsnack_p14 = Multigoal("goal_childsnack_p14",served=state_childsnack_p14.waiting)

# Set goal state from p14.hddl
# 	(:goal (and
# (served child1)
# (served child2)
# (served child3)
# (served child4)
# (served child5)
# (served child6)
# (served child7)
# (served child8)
# (served child9)
# (served child10)
# (served child11)
# (served child12)
# (served child13)
# (served child14)
# (served child15)
# (served child16)
# (served child17)
# (served child18)
# 	))
goal_childsnack_p14 = state_childsnack_p14.waiting

# ===== prob-snack --------------------------------------------------- p15.hddl
state_childsnack_p15 = State("snack_p15_initial_state")

# types:
state_childsnack_p15.bread_portions = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7","bread8","bread9","bread10","bread11","bread12","bread13","bread14","bread15","bread16","bread17","bread18"}
state_childsnack_p15.children = {"child1","child2","child3","child4","child5","child6","child7","child8","child9","child10","child11","child12","child13","child14","child15","child16","child17","child18"}
state_childsnack_p15.content_portions = {"content1","content2","content3","content4","content5","content6","content7","content8","content9","content10","content11","content12","content13","content14","content15","content16","content17","content18"}
state_childsnack_p15.places = {"table1","table2","table3"}
state_childsnack_p15.sandwiches = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19","sandw20","sandw21","sandw22","sandw23","sandw24"}
state_childsnack_p15.trays = {"tray1","tray2","tray3","tray4"}

# predicates:
state_childsnack_p15.allergic_gluten = {"child17","child2","child14","child6","child8","child9","child5"}
state_childsnack_p15.at = {"tray1":"kitchen","tray2":"kitchen","tray3":"kitchen","tray4":"kitchen"}
state_childsnack_p15.at_kitchen_bread = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7",
                                    "bread8","bread9","bread10","bread11","bread12","bread13","bread14","bread15","bread16","bread17","bread18"}
state_childsnack_p15.at_kitchen_content = {"content1","content2","content3","content4","content5",
                                      "content6","content7","content8","content9","content10","content11","content12","content13","content14","content15","content16","content17","content18"}
state_childsnack_p15.at_kitchen_sandwich = set()
state_childsnack_p15.not_allergic_gluten = {"child12","child1","child10","child3","child4","child7","child13","child18","child15","child11","child16"}
state_childsnack_p15.notexist = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19","sandw20","sandw21","sandw22","sandw23","sandw24"}
state_childsnack_p15.no_gluten_bread = {"bread11","bread4","bread16","bread14","bread7","bread9","bread3"}
state_childsnack_p15.no_gluten_content = {"content4","content5","content12","content18","content14","content1","content3"}
state_childsnack_p15.no_gluten_sandwich = set()
state_childsnack_p15.ontray = {}
state_childsnack_p15.served = {}
state_childsnack_p15.waiting = {"child1":"table1","child2":"table2","child3":"table1","child4":"table1",
                           "child5":"table3","child6":"table3","child7":"table2","child8":"table3",
                           "child9":"table2","child10":"table2","child11":"table2","child12":"table2","child13":"table3","child14":"table1","child15":"table2","child16":"table2","child17":"table2","child18":"table1"}

# Set goal from the :htn :ordered-subtasks in p15.hddl
htn_ordered_subtask_childsnack_p15 = Multigoal("goal_childsnack_p15",served=state_childsnack_p15.waiting)

# Set goal state from p15.hddl
# 	(:goal (and
# (served child1)
# (served child2)
# (served child3)
# (served child4)
# (served child5)
# (served child6)
# (served child7)
# (served child8)
# (served child9)
# (served child10)
# (served child11)
# (served child12)
# (served child13)
# (served child14)
# (served child15)
# (served child16)
# (served child17)
# (served child18)
# 	))
goal_childsnack_p15 = state_childsnack_p15.waiting

# ===== prob-snack --------------------------------------------------- p16.hddl
state_childsnack_p16 = State("snack_p16_initial_state")

# types:
state_childsnack_p16.bread_portions = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7","bread8","bread9","bread10","bread11","bread12","bread13","bread14","bread15","bread16","bread17","bread18","bread19"}
state_childsnack_p16.children = {"child1","child2","child3","child4","child5","child6","child7","child8","child9","child10","child11","child12","child13","child14","child15","child16","child17","child18","child19"}
state_childsnack_p16.content_portions = {"content1","content2","content3","content4","content5","content6","content7","content8","content9","content10","content11","content12","content13","content14","content15","content16","content17","content18","content19"}
state_childsnack_p16.places = {"table1","table2","table3"}
state_childsnack_p16.sandwiches = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19","sandw20","sandw21","sandw22","sandw23","sandw24","sandw25"}
state_childsnack_p16.trays = {"tray1","tray2","tray3","tray4"}

# predicates:
state_childsnack_p16.allergic_gluten = {"child2","child5","child14","child7","child8","child9","child6"}
state_childsnack_p16.at = {"tray1":"kitchen","tray2":"kitchen","tray3":"kitchen","tray4":"kitchen"}
state_childsnack_p16.at_kitchen_bread = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7",
                                    "bread8","bread9","bread10","bread11","bread12","bread13","bread14","bread15","bread16","bread17","bread18","bread19"}
state_childsnack_p16.at_kitchen_content = {"content1","content2","content3","content4","content5",
                                      "content6","content7","content8","content9","content10","content11","content12","content13","content14","content15","content16","content17","content18","content19"}
state_childsnack_p16.at_kitchen_sandwich = set()
state_childsnack_p16.not_allergic_gluten = {"child12","child1","child10","child3","child4","child17","child15","child13","child18","child19","child11","child16"}
state_childsnack_p16.notexist = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19","sandw20","sandw21","sandw22","sandw23","sandw24","sandw25"}
state_childsnack_p16.no_gluten_bread = {"bread12","bread4","bread17","bread15","bread8","bread10","bread3"}
state_childsnack_p16.no_gluten_content = {"content5","content6","content12","content4","content15","content1","content3"}
state_childsnack_p16.no_gluten_sandwich = set()
state_childsnack_p16.ontray = {}
state_childsnack_p16.served = {}
state_childsnack_p16.waiting = {"child1":"table1","child2":"table2","child3":"table1","child4":"table1",
                           "child5":"table3","child6":"table3","child7":"table2","child8":"table3",
                           "child9":"table2","child10":"table2","child11":"table2","child12":"table2","child13":"table3","child14":"table1","child15":"table2","child16":"table2","child17":"table2","child18":"table1","child19":"table3"}

# Set goal from the :htn :ordered-subtasks in p16.hddl
htn_ordered_subtask_childsnack_p16 = Multigoal("goal_childsnack_p16",served=state_childsnack_p16.waiting)

# Set goal state from p16.hddl
# 	(:goal (and
# (served child1)
# (served child2)
# (served child3)
# (served child4)
# (served child5)
# (served child6)
# (served child7)
# (served child8)
# (served child9)
# (served child10)
# (served child11)
# (served child12)
# (served child13)
# (served child14)
# (served child15)
# (served child16)
# (served child17)
# (served child18)
# (served child19)
# 	))
goal_childsnack_p16 = state_childsnack_p16.waiting

# ===== prob-snack --------------------------------------------------- p17.hddl
state_childsnack_p17 = State("snack_p17_initial_state")

# types:
state_childsnack_p17.bread_portions = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7","bread8","bread9","bread10","bread11","bread12","bread13","bread14","bread15","bread16","bread17","bread18","bread19","bread20"}
state_childsnack_p17.children = {"child1","child2","child3","child4","child5","child6","child7","child8","child9","child10","child11","child12","child13","child14","child15","child16","child17","child18","child19","child20"}
state_childsnack_p17.content_portions = {"content1","content2","content3","content4","content5","content6","content7","content8","content9","content10","content11","content12","content13","content14","content15","content16","content17","content18","content19","content20"}
state_childsnack_p17.places = {"table1","table2","table3"}
state_childsnack_p17.sandwiches = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19","sandw20","sandw21","sandw22","sandw23","sandw24","sandw25","sandw26"}
state_childsnack_p17.trays = {"tray1","tray2","tray3","tray4"}

# predicates:
state_childsnack_p17.allergic_gluten = {"child1","child2","child11","child16","child15","child18","child10","child20"}
state_childsnack_p17.at = {"tray1":"kitchen","tray2":"kitchen","tray3":"kitchen","tray4":"kitchen"}
state_childsnack_p17.at_kitchen_bread = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7",
                                    "bread8","bread9","bread10","bread11","bread12","bread13","bread14","bread15","bread16","bread17","bread18","bread19","bread20"}
state_childsnack_p17.at_kitchen_content = {"content1","content2","content3","content4","content5",
                                      "content6","content7","content8","content9","content10","content11","content12","content13","content14","content15","content16","content17","content18","content19","content20"}
state_childsnack_p17.at_kitchen_sandwich = set()
state_childsnack_p17.not_allergic_gluten = {"child12","child13","child3","child4","child5","child6","child7","child8","child9","child19","child14","child17"}
state_childsnack_p17.notexist = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19","sandw20","sandw21","sandw22","sandw23","sandw24","sandw25","sandw26"}
state_childsnack_p17.no_gluten_bread = {"bread4","bread19","bread8","bread9","bread2","bread13","bread7","bread16"}
state_childsnack_p17.no_gluten_content = {"content20","content8","content1","content6","content11","content5","content18","content7"}
state_childsnack_p17.no_gluten_sandwich = set()
state_childsnack_p17.ontray = {}
state_childsnack_p17.served = {}
state_childsnack_p17.waiting = {"child1":"table3","child2":"table1","child3":"table1","child4":"table1",
                           "child5":"table2","child6":"table3","child7":"table1","child8":"table2",
                           "child9":"table2","child10":"table3","child11":"table3","child12":"table1","child13":"table2","child14":"table2","child15":"table3","child16":"table1","child17":"table3","child18":"table2","child19":"table3","child20":"table1"}

# Set goal from the :htn :ordered-subtasks in p17.hddl
htn_ordered_subtask_childsnack_p17 = Multigoal("goal_childsnack_p17",served=state_childsnack_p17.waiting)

# Set goal state from p17.hddl
# 	(:goal (and
# (served child1)
# (served child2)
# (served child3)
# (served child4)
# (served child5)
# (served child6)
# (served child7)
# (served child8)
# (served child9)
# (served child10)
# (served child11)
# (served child12)
# (served child13)
# (served child14)
# (served child15)
# (served child16)
# (served child17)
# (served child18)
# (served child19)
# (served child20)
# 	))
goal_childsnack_p17 = state_childsnack_p17.waiting

# ===== prob-snack --------------------------------------------------- p18.hddl
state_childsnack_p18 = State("snack_p18_initial_state")

# types:
state_childsnack_p18.bread_portions = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7","bread8","bread9","bread10","bread11","bread12","bread13","bread14","bread15","bread16","bread17","bread18","bread19","bread20","bread21"}
state_childsnack_p18.children = {"child1","child2","child3","child4","child5","child6","child7","child8","child9","child10","child11","child12","child13","child14","child15","child16","child17","child18","child19","child20","child21"}
state_childsnack_p18.content_portions = {"content1","content2","content3","content4","content5","content6","content7","content8","content9","content10","content11","content12","content13","content14","content15","content16","content17","content18","content19","content20","content21"}
state_childsnack_p18.places = {"table1","table2","table3"}
state_childsnack_p18.sandwiches = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19","sandw20","sandw21","sandw22","sandw23","sandw24","sandw25","sandw26","sandw27","sandw28"}
state_childsnack_p18.trays = {"tray1","tray2","tray3","tray4"}

# predicates:
state_childsnack_p18.allergic_gluten = {"child12","child1","child2","child11","child16","child17","child19","child21"}
state_childsnack_p18.at = {"tray1":"kitchen","tray2":"kitchen","tray3":"kitchen","tray4":"kitchen"}
state_childsnack_p18.at_kitchen_bread = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7",
                                    "bread8","bread9","bread10","bread11","bread12","bread13","bread14","bread15","bread16","bread17","bread18","bread19","bread20","bread21"}
state_childsnack_p18.at_kitchen_content = {"content1","content2","content3","content4","content5",
                                      "content6","content7","content8","content9","content10","content11","content12","content13","content14","content15","content16","content17","content18","content19","content20","content21"}
state_childsnack_p18.at_kitchen_sandwich = set()
state_childsnack_p18.not_allergic_gluten = {"child13","child10","child3","child4","child5","child6","child7","child8","child9","child18","child15","child20","child14"}
state_childsnack_p18.notexist = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19","sandw20","sandw21","sandw22","sandw23","sandw24","sandw25","sandw26","sandw27","sandw28"}
state_childsnack_p18.no_gluten_bread = {"bread5","bread20","bread8","bread9","bread2","bread13","bread19","bread17"}
state_childsnack_p18.no_gluten_content = {"content21","content9","content2","content6","content12","content18","content1","content8"}
state_childsnack_p18.no_gluten_sandwich = set()
state_childsnack_p18.ontray = {}
state_childsnack_p18.served = {}
state_childsnack_p18.waiting = {"child1":"table3","child2":"table1","child3":"table1","child4":"table1",
                           "child5":"table2","child6":"table3","child7":"table1","child8":"table2",
                           "child9":"table2","child10":"table3","child11":"table3","child12":"table1","child13":"table2","child14":"table2","child15":"table3","child16":"table1","child17":"table3","child18":"table2","child19":"table3","child20":"table1","child21":"table2"}

# Set goal from the :htn :ordered-subtasks in p18.hddl
htn_ordered_subtask_childsnack_p18 = Multigoal("goal_childsnack_p18",served=state_childsnack_p18.waiting)

# Set goal state from p18.hddl
# 	(:goal (and
# (served child1)
# (served child2)
# (served child3)
# (served child4)
# (served child5)
# (served child6)
# (served child7)
# (served child8)
# (served child9)
# (served child10)
# (served child11)
# (served child12)
# (served child13)
# (served child14)
# (served child15)
# (served child16)
# (served child17)
# (served child18)
# (served child19)
# (served child20)
# (served child21)
# 	))
goal_childsnack_p18 = state_childsnack_p18.waiting

# ===== prob-snack --------------------------------------------------- p19.hddl
state_childsnack_p19 = State("snack_p19_initial_state")

# types:
state_childsnack_p19.bread_portions = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7","bread8","bread9","bread10","bread11","bread12","bread13","bread14","bread15","bread16","bread17","bread18","bread19","bread20","bread21","bread22","bread23","bread24"}
state_childsnack_p19.children = {"child1","child2","child3","child4","child5","child6","child7","child8","child9","child10","child11","child12","child13","child14","child15","child16","child17","child18","child19","child20","child21","child22","child23","child24"}
state_childsnack_p19.content_portions = {"content1","content2","content3","content4","content5","content6","content7","content8","content9","content10","content11","content12","content13","content14","content15","content16","content17","content18","content19","content20","content21","content22","content23","content24"}
state_childsnack_p19.places = {"table1","table2","table3"}
state_childsnack_p19.sandwiches = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19","sandw20","sandw21","sandw22","sandw23","sandw24","sandw25","sandw26","sandw27","sandw28","sandw29","sandw30","sandw31","sandw32"}
state_childsnack_p19.trays = {"tray1","tray2","tray3","tray4"}

# predicates:
state_childsnack_p19.allergic_gluten = {"child1","child2","child4","child17","child14","child15","child22","child6","child24"}
state_childsnack_p19.at = {"tray1":"kitchen","tray2":"kitchen","tray3":"kitchen","tray4":"kitchen"}
state_childsnack_p19.at_kitchen_bread = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7",
                                    "bread8","bread9","bread10","bread11","bread12","bread13","bread14","bread15","bread16","bread17","bread18","bread19","bread20","bread21","bread22","bread23","bread24"}
state_childsnack_p19.at_kitchen_content = {"content1","content2","content3","content4","content5",
                                      "content6","content7","content8","content9","content10","content11","content12","content13","content14","content15","content16","content17","content18","content19","content20","content21","content22","content23","content24"}
state_childsnack_p19.at_kitchen_sandwich = set()
state_childsnack_p19.not_allergic_gluten = {"child12","child13","child10","child11","child16","child5","child7","child8","child9","child18","child19","child3","child23","child21","child20"}
state_childsnack_p19.notexist = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19","sandw20","sandw21","sandw22","sandw23","sandw24","sandw25","sandw26","sandw27","sandw28","sandw29","sandw30","sandw31","sandw32"}
state_childsnack_p19.no_gluten_bread = {"bread5","bread23","bread9","bread11","bread3","bread16","bread22","bread20","bread19"}
state_childsnack_p19.no_gluten_content = {"content10","content2","content7","content14","content22","content1","content24","content13","content17"}
state_childsnack_p19.no_gluten_sandwich = set()
state_childsnack_p19.ontray = {}
state_childsnack_p19.served = {}
state_childsnack_p19.waiting = {"child1":"table1","child2":"table2","child3":"table3","child4":"table1",
                           "child5":"table2","child6":"table2","child7":"table3","child8":"table3",
                           "child9":"table1","child10":"table2","child11":"table2","child12":"table3","child13":"table1","child14":"table3","child15":"table2","child16":"table3","child17":"table1","child18":"table2","child19":"table3","child20":"table2","child21":"table1","child22":"table2","child23":"table2","child24":"table2"}

# Set goal from the :htn :ordered-subtasks in p19.hddl
htn_ordered_subtask_childsnack_p19 = Multigoal("goal_childsnack_p19",served=state_childsnack_p19.waiting)

# Set goal state from p19.hddl
# 	(:goal (and
# (served child1)
# (served child2)
# (served child3)
# (served child4)
# (served child5)
# (served child6)
# (served child7)
# (served child8)
# (served child9)
# (served child10)
# (served child11)
# (served child12)
# (served child13)
# (served child14)
# (served child15)
# (served child16)
# (served child17)
# (served child18)
# (served child19)
# (served child20)
# (served child21)
# (served child23)
# (served child24)
# 	))
goal_childsnack_p19 = state_childsnack_p19.waiting

# ===== prob-snack --------------------------------------------------- p20.hddl
state_childsnack_p20 = State("snack_p20_initial_state")

# types:
state_childsnack_p20.bread_portions = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7","bread8","bread9","bread10","bread11","bread12","bread13","bread14","bread15","bread16","bread17","bread18","bread19","bread20","bread21","bread22","bread23","bread24"}
state_childsnack_p20.children = {"child1","child2","child3","child4","child5","child6","child7","child8","child9","child10","child11","child12","child13","child14","child15","child16","child17","child18","child19","child20","child21","child22","child23","child24"}
state_childsnack_p20.content_portions = {"content1","content2","content3","content4","content5","content6","content7","content8","content9","content10","content11","content12","content13","content14","content15","content16","content17","content18","content19","content20","content21","content22","content23","content24"}
state_childsnack_p20.places = {"table1","table2","table3"}
state_childsnack_p20.sandwiches = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19","sandw20","sandw21","sandw22","sandw23","sandw24","sandw25","sandw26","sandw27","sandw28","sandw29","sandw30","sandw31","sandw32"}
state_childsnack_p20.trays = {"tray1","tray2","tray3","tray4"}

# predicates:
state_childsnack_p20.allergic_gluten = {"child2","child11","child5","child6","child15","child8","child9","child22","child14"}
state_childsnack_p20.at = {"tray1":"kitchen","tray2":"kitchen","tray3":"kitchen","tray4":"kitchen"}
state_childsnack_p20.at_kitchen_bread = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7",
                                    "bread8","bread9","bread10","bread11","bread12","bread13","bread14","bread15","bread16","bread17","bread18","bread19","bread20","bread21","bread22","bread23","bread24"}
state_childsnack_p20.at_kitchen_content = {"content1","content2","content3","content4","content5",
                                      "content6","content7","content8","content9","content10","content11","content12","content13","content14","content15","content16","content17","content18","content19","content20","content21","content22","content23","content24"}
state_childsnack_p20.at_kitchen_sandwich = set()
state_childsnack_p20.not_allergic_gluten = {"child12","child13","child10","child3","child16","child17","child1","child18","child19","child23","child4","child7","child20","child21","child24"}
state_childsnack_p20.notexist = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19","sandw20","sandw21","sandw22","sandw23","sandw24","sandw25","sandw26","sandw27","sandw28","sandw29","sandw30","sandw31","sandw32"}
state_childsnack_p20.no_gluten_bread = {"bread14","bread5","bread22","bread20","bread10","bread13","bread4","bread18","bread23"}
state_childsnack_p20.no_gluten_content = {"content17","content5","content22","content2","content4","content21","content14","content7","content8"}
state_childsnack_p20.no_gluten_sandwich = set()
state_childsnack_p20.ontray = {}
state_childsnack_p20.served = {}
state_childsnack_p20.waiting = {"child1":"table2","child2":"table3","child3":"table2","child4":"table2",
                           "child5":"table2","child6":"table2","child7":"table3","child8":"table1",
                           "child9":"table2","child10":"table2","child11":"table2","child12":"table1","child13":"table3","child14":"table1","child15":"table2","child16":"table1","child17":"table1","child18":"table1","child19":"table1","child20":"table1","child21":"table3","child22":"table3","child23":"table2","child24":"table2"}

# Set goal from the :htn :ordered-subtasks in p20.hddl
htn_ordered_subtask_childsnack_p20 = Multigoal("goal_childsnack_p20",served=state_childsnack_p20.waiting)

# Set goal state from p20.hddl
# 	(:goal (and
# (served child1)
# (served child2)
# (served child3)
# (served child4)
# (served child5)
# (served child6)
# (served child7)
# (served child8)
# (served child9)
# (served child10)
# (served child11)
# (served child12)
# (served child13)
# (served child14)
# (served child15)
# (served child16)
# (served child17)
# (served child18)
# (served child19)
# (served child20)
# (served child21)
# (served child22)
# (served child23)
# (served child24)
# 	))
goal_childsnack_p20 = state_childsnack_p20.waiting

# ===== prob-snack --------------------------------------------------- p21.hddl
state_childsnack_p21 = State("snack_p21_initial_state")

# types:
state_childsnack_p21.bread_portions = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7","bread8","bread9","bread10","bread11","bread12","bread13","bread14","bread15","bread16","bread17","bread18","bread19","bread20","bread21","bread22","bread23","bread24","bread25","bread26","bread27","bread28","bread29","bread30"}
state_childsnack_p21.children = {"child1","child2","child3","child4","child5","child6","child7","child8","child9","child10","child11","child12","child13","child14","child15","child16","child17","child18","child19","child20","child21","child22","child23","child24","child25","child26","child27","child28","child29","child30"}
state_childsnack_p21.content_portions = {"content1","content2","content3","content4","content5","content6","content7","content8","content9","content10","content11","content12","content13","content14","content15","content16","content17","content18","content19","content20","content21","content22","content23","content24","content25","content26","content27","content28","content29","content30"}
state_childsnack_p21.places = {"table1","table2","table3"}
state_childsnack_p21.sandwiches = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19","sandw20","sandw21","sandw22","sandw23","sandw24","sandw25","sandw26","sandw27","sandw28","sandw29","sandw30"}
state_childsnack_p21.trays = {"tray1","tray2","tray3","tray4","tray5"}

# predicates:
state_childsnack_p21.allergic_gluten = {"child4","child30","child3","child27","child12","child5","child9","child2","child13","child11","child22","child21","child28","child25","child18","child17","child7","child15"}
state_childsnack_p21.at = {"tray1":"kitchen","tray2":"kitchen","tray3":"kitchen","tray4":"kitchen","tray5":"kitchen"}
state_childsnack_p21.at_kitchen_bread = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7",
                                    "bread8","bread9","bread10","bread11","bread12","bread13","bread14","bread15","bread16","bread17","bread18","bread19","bread20","bread21","bread22","bread23","bread24","bread25","bread26","bread27","bread28","bread29","bread30"}
state_childsnack_p21.at_kitchen_content = {"content1","content2","content3","content4","content5",
                                      "content6","content7","content8","content9","content10","content11","content12","content13","content14","content15","content16","content17","content18","content19","content20","content21","content22","content23","content24","content25","content26","content27","content28","content29","content30"}
state_childsnack_p21.at_kitchen_sandwich = set()
state_childsnack_p21.not_allergic_gluten = {"child24","child23","child6","child19","child8","child10","child1","child20","child14","child26","child16","child29"}
state_childsnack_p21.notexist = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19","sandw20","sandw21","sandw22","sandw23","sandw24","sandw25","sandw26","sandw27","sandw28","sandw29","sandw30"}
state_childsnack_p21.no_gluten_bread = {"bread21","bread4","bread1","bread24","bread9","bread8","bread25","bread5","bread29","bread18","bread3","bread19","bread14","bread2","bread28","bread17","bread22","bread30"}
state_childsnack_p21.no_gluten_content = {"content17","content20","content1","content18","content7","content23","content21","content25","content27","content14","content8","content15","content9","content28","content6","content12","content26","content16"}
state_childsnack_p21.no_gluten_sandwich = set()
state_childsnack_p21.ontray = {}
state_childsnack_p21.served = {}
state_childsnack_p21.waiting = {"child1":"table3","child2":"table2","child3":"table3","child4":"table3",
                           "child5":"table2","child6":"table3","child7":"table1","child8":"table3",
                           "child9":"table1","child10":"table1","child11":"table3","child12":"table1","child13":"table2","child14":"table1","child15":"table1","child16":"table1","child17":"table2","child18":"table2","child19":"table2","child20":"table3","child21":"table2","child22":"table1","child23":"table2","child24":"table2","child25":"table1","child26":"table3","child27":"table2","child28":"table3","child29":"table3","child30":"table3"}

# Set goal from the :htn :ordered-subtasks in p21.hddl
htn_ordered_subtask_childsnack_p21 = Multigoal("goal_childsnack_p21",served=state_childsnack_p21.waiting)

# Set goal state from p21.hddl
# 	(:goal (and
# (served child1)
# (served child2)
# (served child3)
# (served child4)
# (served child5)
# (served child6)
# (served child7)
# (served child8)
# (served child9)
# (served child10)
# (served child11)
# (served child12)
# (served child13)
# (served child14)
# (served child15)
# (served child16)
# (served child17)
# (served child18)
# (served child19)
# (served child20)
# (served child21)
# (served child22)
# (served child23)
# (served child24)
# (served child25)
# (served child26)
# (served child27)
# (served child28)
# (served child29)
# (served child30)
# 	))
goal_childsnack_p21 = state_childsnack_p21.waiting

# ===== prob-snack --------------------------------------------------- p22.hddl
state_childsnack_p22 = State("snack_p22_initial_state")

# types:
state_childsnack_p22.bread_portions = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7","bread8","bread9","bread10","bread11","bread12","bread13","bread14","bread15","bread16","bread17","bread18","bread19","bread20","bread21","bread22","bread23","bread24","bread25","bread26","bread27","bread28","bread29","bread30","bread31","bread32","bread33","bread34","bread35","bread36","bread37","bread38","bread39","bread40"}
state_childsnack_p22.children = {"child1","child2","child3","child4","child5","child6","child7","child8","child9","child10","child11","child12","child13","child14","child15","child16","child17","child18","child19","child20","child21","child22","child23","child24","child25","child26","child27","child28","child29","child30","child31","child32","child33","child34","child35","child36","child37","child38","child39","child40"}
state_childsnack_p22.content_portions = {"content1","content2","content3","content4","content5","content6","content7","content8","content9","content10","content11","content12","content13","content14","content15","content16","content17","content18","content19","content20","content21","content22","content23","content24","content25","content26","content27","content28","content29","content30","content31","content32","content33","content34","content35","content36","content37","content38","content39","content40"}
state_childsnack_p22.places = {"table1","table2","table3"}
state_childsnack_p22.sandwiches = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19","sandw20","sandw21","sandw22","sandw23","sandw24","sandw25","sandw26","sandw27","sandw28","sandw29","sandw30","sandw31","sandw32","sandw33","sandw34","sandw35","sandw36","sandw37","sandw38","sandw39","sandw40"}
state_childsnack_p22.trays = {"tray1","tray2","tray3","tray4","tray5","tray6"}

# predicates:
state_childsnack_p22.allergic_gluten = {"child39","child28","child19","child3","child40","child25","child10","child6","child35","child8","child22","child13","child4","child24","child5","child37","child32","child7","child33","child36","child9","child21","child15","child12"}
state_childsnack_p22.at = {"tray1":"kitchen","tray2":"kitchen","tray3":"kitchen","tray4":"kitchen","tray5":"kitchen","tray6":"kitchen"}
state_childsnack_p22.at_kitchen_bread = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7",
                                    "bread8","bread9","bread10","bread11","bread12","bread13","bread14","bread15","bread16","bread17","bread18","bread19","bread20","bread21","bread22","bread23","bread24","bread25","bread26","bread27","bread28","bread29","bread30","bread31","bread32","bread33","bread34","bread35","bread36","bread37","bread38","bread39","bread40"}
state_childsnack_p22.at_kitchen_content = {"content1","content2","content3","content4","content5",
                                      "content6","content7","content8","content9","content10","content11","content12","content13","content14","content15","content16","content17","content18","content19","content20","content21","content22","content23","content24","content25","content26","content27","content28","content29","content30","content31","content32","content33","content34","content35","content36","content37","content38","content39","content40"}
state_childsnack_p22.at_kitchen_sandwich = set()
state_childsnack_p22.not_allergic_gluten = {"child27","child16","child2","child38","child23","child11","child34","child20","child26","child1","child18","child17","child29","child30","child31","child14"}
state_childsnack_p22.notexist = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19","sandw20","sandw21","sandw22","sandw23","sandw24","sandw25","sandw26","sandw27","sandw28","sandw29","sandw30","sandw31","sandw32","sandw33","sandw34","sandw35","sandw36","sandw37","sandw38","sandw39","sandw40"}
state_childsnack_p22.no_gluten_bread = {"bread8","bread2","bread18","bread16","bread15","bread9","bread7","bread6","bread28","bread39","bread1","bread3","bread34","bread40","bread17","bread20","bread30","bread38","bread32","bread21","bread23","bread14","bread27","bread36"}
state_childsnack_p22.no_gluten_content = {"content38","content18","content1","content11","content28","content22","content39","content10","content14","content31","content25","content37","content4","content3","content13","content36","content12","content24","content20","content9","content2","content15","content34","content30"}
state_childsnack_p22.no_gluten_sandwich = set()
state_childsnack_p22.ontray = {}
state_childsnack_p22.served = {}
state_childsnack_p22.waiting = {"child1":"table3","child2":"table2","child3":"table3","child4":"table3",
                           "child5":"table3","child6":"table1","child7":"table3","child8":"table3",
                           "child9":"table1","child10":"table3","child11":"table3","child12":"table1","child13":"table1","child14":"table2","child15":"table2","child16":"table2","child17":"table3","child18":"table3","child19":"table3","child20":"table1","child21":"table3","child22":"table2","child23":"table1","child24":"table1","child25":"table1","child26":"table2","child27":"table2","child28":"table2","child29":"table1","child30":"table1","child31":"table3","child32":"table3","child33":"table2","child34":"table1","child35":"table3","child36":"table2","child37":"table2","child38":"table3","child39":"table2","child40":"table1"}

# Set goal from the :htn :ordered-subtasks in p22.hddl
htn_ordered_subtask_childsnack_p22 = Multigoal("goal_childsnack_p22",served=state_childsnack_p22.waiting)

# Set goal state from p22.hddl
# 	(:goal (and
# (served child1)
# (served child2)
# (served child3)
# (served child4)
# (served child5)
# (served child6)
# (served child7)
# (served child8)
# (served child9)
# (served child10)
# (served child11)
# (served child12)
# (served child13)
# (served child14)
# (served child15)
# (served child16)
# (served child17)
# (served child18)
# (served child19)
# (served child20)
# (served child21)
# (served child22)
# (served child23)
# (served child24)
# (served child25)
# (served child26)
# (served child27)
# (served child28)
# (served child29)
# (served child30)
# (served child31)
# (served child32)
# (served child33)
# (served child34)
# (served child35)
# (served child36)
# (served child37)
# (served child38)
# (served child39)
# (served child40)
# 	))
goal_childsnack_p22 = state_childsnack_p22.waiting

# ===== prob-snack --------------------------------------------------- p23.hddl
state_childsnack_p23 = State("snack_p23_initial_state")

# types:
state_childsnack_p23.bread_portions = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7","bread8","bread9","bread10","bread11","bread12","bread13","bread14","bread15","bread16","bread17","bread18","bread19","bread20","bread21","bread22","bread23","bread24","bread25","bread26","bread27","bread28","bread29","bread30","bread31","bread32","bread33","bread34","bread35","bread36","bread37","bread38","bread39","bread40","bread41","bread42","bread43","bread44","bread45","bread46","bread47","bread48","bread49","bread50"}
state_childsnack_p23.children = {"child1","child2","child3","child4","child5","child6","child7","child8","child9","child10","child11","child12","child13","child14","child15","child16","child17","child18","child19","child20","child21","child22","child23","child24","child25","child26","child27","child28","child29","child30","child31","child32","child33","child34","child35","child36","child37","child38","child39","child40","child41","child42","child43","child44","child45","child46","child47","child48","child49","child50"}
state_childsnack_p23.content_portions = {"content1","content2","content3","content4","content5","content6","content7","content8","content9","content10","content11","content12","content13","content14","content15","content16","content17","content18","content19","content20","content21","content22","content23","content24","content25","content26","content27","content28","content29","content30","content31","content32","content33","content34","content35","content36","content37","content38","content39","content40","content41","content42","content43","content44","content45","content46","content47","content48","content49","content50"}
state_childsnack_p23.places = {"table1","table2","table3"}
state_childsnack_p23.sandwiches = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19","sandw20","sandw21","sandw22","sandw23","sandw24","sandw25","sandw26","sandw27","sandw28","sandw29","sandw30","sandw31","sandw32","sandw33","sandw34","sandw35","sandw36","sandw37","sandw38","sandw39","sandw40","sandw41","sandw42","sandw43","sandw44","sandw45","sandw46","sandw47","sandw48","sandw49","sandw50"}
state_childsnack_p23.trays = {"tray1","tray2","tray3","tray4","tray5","tray6","tray7"}

# predicates:
state_childsnack_p23.allergic_gluten = {"child8","child43","child18","child38","child36","child49","child3","child24","child39","child11","child23","child46","child19","child25","child47","child15","child44","child30","child50","child29","child14","child40","child7","child6","child13","child5","child9","child20","child21","child33"}
state_childsnack_p23.at = {"tray1":"kitchen","tray2":"kitchen","tray3":"kitchen","tray4":"kitchen","tray5":"kitchen","tray6":"kitchen","tray7":"kitchen"}
state_childsnack_p23.at_kitchen_bread = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7",
                                    "bread8","bread9","bread10","bread11","bread12","bread13","bread14","bread15","bread16","bread17","bread18","bread19","bread20","bread21","bread22","bread23","bread24","bread25","bread26","bread27","bread28","bread29","bread30","bread31","bread32","bread33","bread34","bread35","bread36","bread37","bread38","bread39","bread40","bread41","bread42","bread43","bread44","bread45","bread46","bread47","bread48","bread49","bread50"}
state_childsnack_p23.at_kitchen_content = {"content1","content2","content3","content4","content5",
                                      "content6","content7","content8","content9","content10","content11","content12","content13","content14","content15","content16","content17","content18","content19","content20","content21","content22","content23","content24","content25","content26","content27","content28","content29","content30","content31","content32","content33","content34","content35","content36","content37","content38","content39","content40","content41","content42","content43","content44","content45","content46","content47","content48","content49","content50"}
state_childsnack_p23.at_kitchen_sandwich = set()
state_childsnack_p23.not_allergic_gluten = {"child2","child12","child16","child34","child35","child22","child4","child37","child10","child32","child26","child48","child17","child31","child1","child45","child41","child28","child42","child27"}
state_childsnack_p23.notexist = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19","sandw20","sandw21","sandw22","sandw23","sandw24","sandw25","sandw26","sandw27","sandw28","sandw29","sandw30","sandw31","sandw32","sandw33","sandw34","sandw35","sandw36","sandw37","sandw38","sandw39","sandw40","sandw41","sandw42","sandw43","sandw44","sandw45","sandw46","sandw47","sandw48","sandw49","sandw50"}
state_childsnack_p23.no_gluten_bread = {"bread41","bread8","bread2","bread18","bread16","bread15","bread9","bread7","bread35","bread6","bread38","bread28","bread3","bread48","bread50","bread14","bread45","bread33","bread37","bread47","bread43","bread23","bread21","bread29","bread31","bread42","bread49","bread34","bread19","bread44"}
state_childsnack_p23.no_gluten_content = {"content1","content49","content11","content45","content28","content22","content18","content10","content14","content47","content7","content6","content25","content40","content23","content36","content17","content3","content30","content44","content4","content13","content33","content31","content43","content21","content20","content12","content19","content37"}
state_childsnack_p23.no_gluten_sandwich = set()
state_childsnack_p23.ontray = {}
state_childsnack_p23.served = {}
state_childsnack_p23.waiting = {"child1":"table3","child2":"table3","child3":"table1","child4":"table3",
                           "child5":"table2","child6":"table1","child7":"table1","child8":"table1",
                           "child9":"table2","child10":"table2","child11":"table2","child12":"table1","child13":"table1","child14":"table3","child15":"table3","child16":"table2","child17":"table1","child18":"table3","child19":"table2","child20":"table2","child21":"table3","child22":"table2","child23":"table1","child24":"table2","child25":"table1","child26":"table1","child27":"table3","child28":"table3","child29":"table3","child30":"table2","child31":"table3","child32":"table3","child33":"table2","child34":"table3","child35":"table2","child36":"table2","child37":"table1","child38":"table1","child39":"table3","child40":"table2","child41":"table1","child42":"table1","child43":"table1","child44":"table1","child45":"table3","child46":"table1","child47":"table3","child48":"table2","child49":"table3","child50":"table1"}

# Set goal from the :htn :ordered-subtasks in p23.hddl
htn_ordered_subtask_childsnack_p23 = Multigoal("goal_childsnack_p23",served=state_childsnack_p23.waiting)

# Set goal state from p23.hddl
# 	(:goal (and
# (served child1)
# (served child2)
# (served child3)
# (served child4)
# (served child5)
# (served child6)
# (served child7)
# (served child8)
# (served child9)
# (served child10)
# (served child11)
# (served child12)
# (served child13)
# (served child14)
# (served child15)
# (served child16)
# (served child17)
# (served child18)
# (served child19)
# (served child20)
# (served child21)
# (served child22)
# (served child23)
# (served child24)
# (served child25)
# (served child26)
# (served child27)
# (served child28)
# (served child29)
# (served child30)
# (served child31)
# (served child32)
# (served child33)
# (served child34)
# (served child35)
# (served child36)
# (served child37)
# (served child38)
# (served child39)
# (served child40)
# (served child41)
# (served child42)
# (served child43)
# (served child44)
# (served child45)
# (served child46)
# (served child47)
# (served child48)
# (served child49)
# (served child50)
# 	))
goal_childsnack_p23 = state_childsnack_p23.waiting

# ===== prob-snack --------------------------------------------------- p24.hddl
state_childsnack_p24 = State("snack_p24_initial_state")

# types:
state_childsnack_p24.bread_portions = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7","bread8","bread9","bread10","bread11","bread12","bread13","bread14","bread15","bread16","bread17","bread18","bread19","bread20","bread21","bread22","bread23","bread24","bread25","bread26","bread27","bread28","bread29","bread30","bread31","bread32","bread33","bread34","bread35","bread36","bread37","bread38","bread39","bread40","bread41","bread42","bread43","bread44","bread45","bread46","bread47","bread48","bread49","bread50","bread51","bread52","bread53","bread54","bread55","bread56","bread57","bread58","bread59","bread60","bread61","bread62","bread63","bread64","bread65","bread66","bread67","bread68","bread69","bread70"}
state_childsnack_p24.children = {"child1","child2","child3","child4","child5","child6","child7","child8","child9","child10","child11","child12","child13","child14","child15","child16","child17","child18","child19","child20","child21","child22","child23","child24","child25","child26","child27","child28","child29","child30","child31","child32","child33","child34","child35","child36","child37","child38","child39","child40","child41","child42","child43","child44","child45","child46","child47","child48","child49","child50","child51","child52","child53","child54","child55","child56","child57","child58","child59","child60","child61","child62","child63","child64","child65","child66","child67","child68","child69","child70"}
state_childsnack_p24.content_portions = {"content1","content2","content3","content4","content5","content6","content7","content8","content9","content10","content11","content12","content13","content14","content15","content16","content17","content18","content19","content20","content21","content22","content23","content24","content25","content26","content27","content28","content29","content30","content31","content32","content33","content34","content35","content36","content37","content38","content39","content40","content41","content42","content43","content44","content45","content46","content47","content48","content49","content50","content51","content52","content53","content54","content55","content56","content57","content58","content59","content60","content61","content62","content63","content64","content65","content66","content67","content68","content69","content70"}
state_childsnack_p24.places = {"table1","table2","table3"}
state_childsnack_p24.sandwiches = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19","sandw20","sandw21","sandw22","sandw23","sandw24","sandw25","sandw26","sandw27","sandw28","sandw29","sandw30","sandw31","sandw32","sandw33","sandw34","sandw35","sandw36","sandw37","sandw38","sandw39","sandw40","sandw41","sandw42","sandw43","sandw44","sandw45","sandw46","sandw47","sandw48","sandw49","sandw50","sandw51","sandw52","sandw53","sandw54","sandw55","sandw56","sandw57","sandw58","sandw59","sandw60","sandw61","sandw62","sandw63","sandw64","sandw65","sandw66","sandw67","sandw68","sandw69","sandw70"}
state_childsnack_p24.trays = {"tray1","tray2","tray3","tray4","tray5","tray6","tray7","tray8"}

# predicates:
state_childsnack_p24.allergic_gluten = {"child49","child55","child45","child70","child16","child14","child35","child56","child42","child40","child5","child4","child32","child67","child65","child41","child3","child60","child46","child54","child18","child68","child30","child12","child10","child15","child50","child66","child36","child9","child47","child21","child8","child59","child17","child61","child37","child22","child57","child44","child28","child26"}
state_childsnack_p24.at = {"tray1":"kitchen","tray2":"kitchen","tray3":"kitchen","tray4":"kitchen","tray5":"kitchen","tray6":"kitchen","tray7":"kitchen","tray8":"kitchen"}
state_childsnack_p24.at_kitchen_bread = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7",
                                    "bread8","bread9","bread10","bread11","bread12","bread13","bread14","bread15","bread16","bread17","bread18","bread19","bread20","bread21","bread22","bread23","bread24","bread25","bread26","bread27","bread28","bread29","bread30","bread31","bread32","bread33","bread34","bread35","bread36","bread37","bread38","bread39","bread40","bread41","bread42","bread43","bread44","bread45","bread46","bread47","bread48","bread49","bread50","bread51","bread52","bread53","bread54","bread55","bread56","bread57","bread58","bread59","bread60","bread61","bread62","bread63","bread64","bread65","bread66","bread67","bread68","bread69","bread70"}
state_childsnack_p24.at_kitchen_content = {"content1","content2","content3","content4","content5",
                                      "content6","content7","content8","content9","content10","content11","content12","content13","content14","content15","content16","content17","content18","content19","content20","content21","content22","content23","content24","content25","content26","content27","content28","content29","content30","content31","content32","content33","content34","content35","content36","content37","content38","content39","content40","content41","content42","content43","content44","content45","content46","content47","content48","content49","content50","content51","content52","content53","content54","content55","content56","content57","content58","content59","content60","content61","content62","content63","content64","content65","content66","content67","content68","content69","content70"}
state_childsnack_p24.at_kitchen_sandwich = set()
state_childsnack_p24.not_allergic_gluten = {"child19","child25","child53","child63","child69","child39","child52","child48","child51","child23","child1","child11","child29","child6","child64","child43","child13","child31","child27","child38","child2","child62","child20","child58","child24","child33","child7","child34"}
state_childsnack_p24.notexist = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19","sandw20","sandw21","sandw22","sandw23","sandw24","sandw25","sandw26","sandw27","sandw28","sandw29","sandw30","sandw31","sandw32","sandw33","sandw34","sandw35","sandw36","sandw37","sandw38","sandw39","sandw40","sandw41","sandw42","sandw43","sandw44","sandw45","sandw46","sandw47","sandw48","sandw49","sandw50","sandw51","sandw52","sandw53","sandw54","sandw55","sandw56","sandw57","sandw58","sandw59","sandw60","sandw61","sandw62","sandw63","sandw64","sandw65","sandw66","sandw67","sandw68","sandw69","sandw70"}
state_childsnack_p24.no_gluten_bread = {"bread15","bread4","bread36","bread32","bread29","bread18","bread14","bread44","bread48","bread58","bread35","bread6","bread38","bread28","bread3","bread2","bread59","bread64","bread70","bread33","bread39","bread55","bread68","bread13","bread46","bread42","bread60","bread27","bread52","bread66","bread61","bread65","bread1","bread11","bread57","bread22","bread50","bread10","bread53","bread31","bread25","bread37"}
state_childsnack_p24.no_gluten_content = {"content14","content12","content49","content13","content46","content45","content34","content52","content3","content47","content30","content35","content8","content25","content6","content36","content19","content41","content40","content24","content37","content67","content66","content5","content62","content43","content15","content54","content56","content44","content7","content57","content18","content60","content51","content11","content55","content23","content70","content22","content9","content33"}
state_childsnack_p24.no_gluten_sandwich = set()
state_childsnack_p24.ontray = {}
state_childsnack_p24.served = {}
state_childsnack_p24.waiting = {"child1":"table3","child2":"table2","child3":"table1","child4":"table1",
                           "child5":"table1","child6":"table1","child7":"table3","child8":"table1",
                           "child9":"table3","child10":"table2","child11":"table3","child12":"table1","child13":"table2","child14":"table2","child15":"table3","child16":"table2","child17":"table3","child18":"table2","child19":"table3","child20":"table1","child21":"table3","child22":"table3","child23":"table1","child24":"table3","child25":"table3","child26":"table2","child27":"table3","child28":"table2","child29":"table1","child30":"table2","child31":"table2","child32":"table1","child33":"table2","child34":"table1","child35":"table3","child36":"table3","child37":"table2","child38":"table3","child39":"table1","child40":"table3","child41":"table1","child42":"table3","child43":"table2","child44":"table3","child45":"table3","child46":"table3","child47":"table1","child48":"table1","child49":"table2","child50":"table1","child51":"table3","child52":"table3","child53":"table1","child54":"table3","child55":"table2","child56":"table2","child57":"table1","child58":"table1","child59":"table2","child60":"table2","child61":"table1","child62":"table1","child63":"table1","child64":"table3","child65":"table1","child66":"table1","child67":"table3","child68":"table2","child69":"table1","child70":"table3"}

# Set goal from the :htn :ordered-subtasks in p24.hddl
htn_ordered_subtask_childsnack_p24 = Multigoal("goal_childsnack_p24",served=state_childsnack_p24.waiting)

# Set goal state from p24.hddl
# 	(:goal (and
# (served child1)
# (served child2)
# (served child3)
# (served child4)
# (served child5)
# (served child6)
# (served child7)
# (served child8)
# (served child9)
# (served child10)
# (served child11)
# (served child12)
# (served child13)
# (served child14)
# (served child15)
# (served child16)
# (served child17)
# (served child18)
# (served child19)
# (served child20)
# (served child21)
# (served child22)
# (served child23)
# (served child24)
# (served child25)
# (served child26)
# (served child27)
# (served child28)
# (served child29)
# (served child30)
# (served child31)
# (served child32)
# (served child33)
# (served child34)
# (served child35)
# (served child36)
# (served child37)
# (served child38)
# (served child39)
# (served child40)
# (served child41)
# (served child42)
# (served child43)
# (served child44)
# (served child45)
# (served child46)
# (served child47)
# (served child48)
# (served child49)
# (served child50)
# (served child51)
# (served child52)
# (served child53)
# (served child54)
# (served child55)
# (served child56)
# (served child57)
# (served child58)
# (served child59)
# (served child60)
# (served child61)
# (served child62)
# (served child63)
# (served child64)
# (served child65)
# (served child66)
# (served child67)
# (served child68)
# (served child69)
# (served child70)
# 	))
goal_childsnack_p24 = state_childsnack_p24.waiting

# ===== prob-snack --------------------------------------------------- p25.hddl
state_childsnack_p25 = State("snack_p25_initial_state")

# types:
state_childsnack_p25.bread_portions = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7","bread8","bread9","bread10","bread11","bread12","bread13","bread14","bread15","bread16","bread17","bread18","bread19","bread20","bread21","bread22","bread23","bread24","bread25","bread26","bread27","bread28","bread29","bread30","bread31","bread32","bread33","bread34","bread35","bread36","bread37","bread38","bread39","bread40","bread41","bread42","bread43","bread44","bread45","bread46","bread47","bread48","bread49","bread50","bread51","bread52","bread53","bread54","bread55","bread56","bread57","bread58","bread59","bread60","bread61","bread62","bread63","bread64","bread65","bread66","bread67","bread68","bread69","bread70","bread71","bread72","bread73","bread74","bread75","bread76","bread77","bread78","bread79","bread80","bread81","bread82","bread83","bread84","bread85","bread86","bread87","bread88","bread89","bread90"}
state_childsnack_p25.children = {"child1","child2","child3","child4","child5","child6","child7","child8","child9","child10","child11","child12","child13","child14","child15","child16","child17","child18","child19","child20","child21","child22","child23","child24","child25","child26","child27","child28","child29","child30","child31","child32","child33","child34","child35","child36","child37","child38","child39","child40","child41","child42","child43","child44","child45","child46","child47","child48","child49","child50","child51","child52","child53","child54","child55","child56","child57","child58","child59","child60","child61","child62","child63","child64","child65","child66","child67","child68","child69","child70","child71","child72","child73","child74","child75","child76","child77","child78","child79","child80","child81","child82","child83","child84","child85","child86","child87","child88","child89","child90"}
state_childsnack_p25.content_portions = {"content1","content2","content3","content4","content5","content6","content7","content8","content9","content10","content11","content12","content13","content14","content15","content16","content17","content18","content19","content20","content21","content22","content23","content24","content25","content26","content27","content28","content29","content30","content31","content32","content33","content34","content35","content36","content37","content38","content39","content40","content41","content42","content43","content44","content45","content46","content47","content48","content49","content50","content51","content52","content53","content54","content55","content56","content57","content58","content59","content60","content61","content62","content63","content64","content65","content66","content67","content68","content69","content70","content71","content72","content73","content74","content75","content76","content77","content78","content79","content80","content81","content82","content83","content84","content85","content86","content87","content88","content89","content90"}
state_childsnack_p25.places = {"table1","table2","table3"}
state_childsnack_p25.sandwiches = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19","sandw20","sandw21","sandw22","sandw23","sandw24","sandw25","sandw26","sandw27","sandw28","sandw29","sandw30","sandw31","sandw32","sandw33","sandw34","sandw35","sandw36","sandw37","sandw38","sandw39","sandw40","sandw41","sandw42","sandw43","sandw44","sandw45","sandw46","sandw47","sandw48","sandw49","sandw50","sandw51","sandw52","sandw53","sandw54","sandw55","sandw56","sandw57","sandw58","sandw59","sandw60","sandw61","sandw62","sandw63","sandw64","sandw65","sandw66","sandw67","sandw68","sandw69","sandw70","sandw71","sandw72","sandw73","sandw74","sandw75","sandw76","sandw77","sandw78","sandw79","sandw80","sandw81","sandw82","sandw83","sandw84","sandw85","sandw86","sandw87","sandw88","sandw89","sandw90"}
state_childsnack_p25.trays = {"tray1","tray2","tray3","tray4","tray5","tray6","tray7","tray8","tray9"}

# predicates:
state_childsnack_p25.allergic_gluten = {"child77","child2","child88","child47","child17","child84","child90","child70","child57","child89","child64","child76","child78","child55","child30","child35","child12","child28","child87","child34","child53","child69","child8","child60","child1","child11","child49","child75","child54","child10","child7","child71","child86","child68","child29","child33","child24","child20","child52","child15","child39","child65","child41","child58","child66","child13","child9","child18","child44","child51","child50","child21","child79","child19"}
state_childsnack_p25.at = {"tray1":"kitchen","tray2":"kitchen","tray3":"kitchen","tray4":"kitchen","tray5":"kitchen","tray6":"kitchen","tray7":"kitchen","tray8":"kitchen","tray9":"kitchen"}
state_childsnack_p25.at_kitchen_bread = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7",
                                    "bread8","bread9","bread10","bread11","bread12","bread13","bread14","bread15","bread16","bread17","bread18","bread19","bread20","bread21","bread22","bread23","bread24","bread25","bread26","bread27","bread28","bread29","bread30","bread31","bread32","bread33","bread34","bread35","bread36","bread37","bread38","bread39","bread40","bread41","bread42","bread43","bread44","bread45","bread46","bread47","bread48","bread49","bread50","bread51","bread52","bread53","bread54","bread55","bread56","bread57","bread58","bread59","bread60","bread61","bread62","bread63","bread64","bread65","bread66","bread67","bread68","bread69","bread70","bread71","bread72","bread73","bread74","bread75","bread76","bread77","bread78","bread79","bread80","bread81","bread82","bread83","bread84","bread85","bread86","bread87","bread88","bread89","bread90"}
state_childsnack_p25.at_kitchen_content = {"content1","content2","content3","content4","content5",
                                      "content6","content7","content8","content9","content10","content11","content12","content13","content14","content15","content16","content17","content18","content19","content20","content21","content22","content23","content24","content25","content26","content27","content28","content29","content30","content31","content32","content33","content34","content35","content36","content37","content38","content39","content40","content41","content42","content43","content44","content45","content46","content47","content48","content49","content50","content51","content52","content53","content54","content55","content56","content57","content58","content59","content60","content61","content62","content63","content64","content65","content66","content67","content68","content69","content70","content71","content72","content73","content74","content75","content76","content77","content78","content79","content80","content81","content82","content83","content84","content85","content86","content87","content88","content89","content90"}
state_childsnack_p25.at_kitchen_sandwich = set()
state_childsnack_p25.not_allergic_gluten = {"child3","child36","child67","child22","child72","child37","child25","child45","child48","child5","child85","child80","child23","child43","child27","child40","child32","child16","child4","child38","child74","child59","child46","child82","child73","child61","child6","child56","child14","child83","child26","child63","child62","child42","child31","child81"}
state_childsnack_p25.notexist = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19","sandw20","sandw21","sandw22","sandw23","sandw24","sandw25","sandw26","sandw27","sandw28","sandw29","sandw30","sandw31","sandw32","sandw33","sandw34","sandw35","sandw36","sandw37","sandw38","sandw39","sandw40","sandw41","sandw42","sandw43","sandw44","sandw45","sandw46","sandw47","sandw48","sandw49","sandw50","sandw51","sandw52","sandw53","sandw54","sandw55","sandw56","sandw57","sandw58","sandw59","sandw60","sandw61","sandw62","sandw63","sandw64","sandw65","sandw66","sandw67","sandw68","sandw69","sandw70","sandw71","sandw72","sandw73","sandw74","sandw75","sandw76","sandw77","sandw78","sandw79","sandw80","sandw81","sandw82","sandw83","sandw84","sandw85","sandw86","sandw87","sandw88","sandw89","sandw90"}
state_childsnack_p25.no_gluten_bread = {"bread82","bread15","bread4","bread36","bread32","bread29","bread18","bread14","bread70","bread12","bread76","bread55","bread5","bread88","bread81","bread28","bread30","bread65","bread77","bread26","bread90","bread54","bread85","bread58","bread87","bread1","bread21","bread45","bread75","bread22","bread84","bread10","bread83","bread49","bread61","bread7","bread6","bread25","bread79","bread23","bread51","bread39","bread17","bread3","bread74","bread35","bread8","bread53","bread69","bread66","bread19","bread24","bread37","bread13"}
state_childsnack_p25.no_gluten_content = {"content9","content6","content85","content30","content38","content11","content87","content13","content49","content36","content59","content47","content21","content48","content46","content27","content35","content10","content22","content69","content32","content78","content60","content82","content74","content29","content42","content54","content50","content62","content4","content15","content53","content3","content52","content71","content26","content18","content5","content14","content37","content76","content55","content51","content64","content70","content63","content67","content84","content73","content17","content90","content16","content81"}
state_childsnack_p25.no_gluten_sandwich = set()
state_childsnack_p25.ontray = {}
state_childsnack_p25.served = {}
state_childsnack_p25.waiting = {"child1":"table2","child2":"table1","child3":"table1","child4":"table2",
                           "child5":"table2","child6":"table1","child7":"table1","child8":"table1",
                           "child9":"table3","child10":"table1","child11":"table1","child12":"table3","child13":"table2","child14":"table1","child15":"table3","child16":"table1","child17":"table1","child18":"table3","child19":"table2","child20":"table3","child21":"table1","child22":"table2","child23":"table3","child24":"table3","child25":"table2","child26":"table1","child27":"table3","child28":"table3","child29":"table3","child30":"table1","child31":"table3","child32":"table2","child33":"table2","child34":"table3","child35":"table3","child36":"table2","child37":"table2","child38":"table3","child39":"table2","child40":"table1","child41":"table1","child42":"table1","child43":"table1","child44":"table2","child45":"table1","child46":"table3","child47":"table3","child48":"table1","child49":"table3","child50":"table1","child51":"table1","child52":"table1","child53":"table3","child54":"table3","child55":"table1","child56":"table1","child57":"table1","child58":"table1","child59":"table2","child60":"table1","child61":"table3","child62":"table1","child63":"table2","child64":"table3","child65":"table2","child66":"table1","child67":"table3","child68":"table1","child69":"table3","child70":"table3","child71":"table3","child72":"table2","child73":"table1","child74":"table2","child75":"table2","child76":"table1","child77":"table1","child78":"table1","child79":"table3","child80":"table2","child81":"table2","child82":"table2","child83":"table2","child84":"table2","child85":"table3","child86":"table1","child87":"table3","child88":"table3","child89":"table3","child90":"table1"}

# Set goal from the :htn :ordered-subtasks in p25.hddl
htn_ordered_subtask_childsnack_p25 = Multigoal("goal_childsnack_p25",served=state_childsnack_p25.waiting)

# Set goal state from p25.hddl
# 	(:goal (and
# (served child1)
# (served child2)
# (served child3)
# (served child4)
# (served child5)
# (served child6)
# (served child7)
# (served child8)
# (served child9)
# (served child10)
# (served child11)
# (served child12)
# (served child13)
# (served child14)
# (served child15)
# (served child16)
# (served child17)
# (served child18)
# (served child19)
# (served child20)
# (served child21)
# (served child22)
# (served child23)
# (served child24)
# (served child25)
# (served child26)
# (served child27)
# (served child28)
# (served child29)
# (served child30)
# (served child31)
# (served child32)
# (served child33)
# (served child34)
# (served child35)
# (served child36)
# (served child37)
# (served child38)
# (served child39)
# (served child40)
# (served child41)
# (served child42)
# (served child43)
# (served child44)
# (served child45)
# (served child46)
# (served child47)
# (served child48)
# (served child49)
# (served child50)
# (served child51)
# (served child52)
# (served child53)
# (served child54)
# (served child55)
# (served child56)
# (served child57)
# (served child58)
# (served child59)
# (served child60)
# (served child61)
# (served child62)
# (served child63)
# (served child64)
# (served child65)
# (served child66)
# (served child67)
# (served child68)
# (served child69)
# (served child70)
# (served child71)
# (served child72)
# (served child73)
# (served child74)
# (served child75)
# (served child76)
# (served child77)
# (served child78)
# (served child79)
# (served child80)
# (served child81)
# (served child82)
# (served child83)
# (served child84)
# (served child85)
# (served child86)
# (served child87)
# (served child88)
# (served child89)
# (served child90)
# 	))
goal_childsnack_p25 = state_childsnack_p25.waiting

# ===== prob-snack --------------------------------------------------- p26.hddl
state_childsnack_p26 = State("snack_p26_initial_state")

# types:
state_childsnack_p26.bread_portions = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7","bread8","bread9","bread10","bread11","bread12","bread13","bread14","bread15","bread16","bread17","bread18","bread19","bread20","bread21","bread22","bread23","bread24","bread25","bread26","bread27","bread28","bread29","bread30","bread31","bread32","bread33","bread34","bread35","bread36","bread37","bread38","bread39","bread40","bread41","bread42","bread43","bread44","bread45","bread46","bread47","bread48","bread49","bread50","bread51","bread52","bread53","bread54","bread55","bread56","bread57","bread58","bread59","bread60","bread61","bread62","bread63","bread64","bread65","bread66","bread67","bread68","bread69","bread70","bread71","bread72","bread73","bread74","bread75","bread76","bread77","bread78","bread79","bread80","bread81","bread82","bread83","bread84","bread85","bread86","bread87","bread88","bread89","bread90","bread91","bread92","bread93","bread94","bread95","bread96","bread97","bread98","bread99","bread100","bread101","bread102","bread103","bread104","bread105","bread106","bread107","bread108","bread109","bread110"}
state_childsnack_p26.children = {"child1","child2","child3","child4","child5","child6","child7","child8","child9","child10","child11","child12","child13","child14","child15","child16","child17","child18","child19","child20","child21","child22","child23","child24","child25","child26","child27","child28","child29","child30","child31","child32","child33","child34","child35","child36","child37","child38","child39","child40","child41","child42","child43","child44","child45","child46","child47","child48","child49","child50","child51","child52","child53","child54","child55","child56","child57","child58","child59","child60","child61","child62","child63","child64","child65","child66","child67","child68","child69","child70","child71","child72","child73","child74","child75","child76","child77","child78","child79","child80","child81","child82","child83","child84","child85","child86","child87","child88","child89","child90","child91","child92","child93","child94","child95","child96","child97","child98","child99","child100","child101","child102","child103","child104","child105","child106","child107","child108","child109","child110"}
state_childsnack_p26.content_portions = {"content1","content2","content3","content4","content5","content6","content7","content8","content9","content10","content11","content12","content13","content14","content15","content16","content17","content18","content19","content20","content21","content22","content23","content24","content25","content26","content27","content28","content29","content30","content31","content32","content33","content34","content35","content36","content37","content38","content39","content40","content41","content42","content43","content44","content45","content46","content47","content48","content49","content50","content51","content52","content53","content54","content55","content56","content57","content58","content59","content60","content61","content62","content63","content64","content65","content66","content67","content68","content69","content70","content71","content72","content73","content74","content75","content76","content77","content78","content79","content80","content81","content82","content83","content84","content85","content86","content87","content88","content89","content90","content91","content92","content93","content94","content95","content96","content97","content98","content99","content100","content101","content102","content103","content104","content105","content106","content107","content108","content109","content110"}
state_childsnack_p26.places = {"table1","table2","table3"}
state_childsnack_p26.sandwiches = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19","sandw20","sandw21","sandw22","sandw23","sandw24","sandw25","sandw26","sandw27","sandw28","sandw29","sandw30","sandw31","sandw32","sandw33","sandw34","sandw35","sandw36","sandw37","sandw38","sandw39","sandw40","sandw41","sandw42","sandw43","sandw44","sandw45","sandw46","sandw47","sandw48","sandw49","sandw50","sandw51","sandw52","sandw53","sandw54","sandw55","sandw56","sandw57","sandw58","sandw59","sandw60","sandw61","sandw62","sandw63","sandw64","sandw65","sandw66","sandw67","sandw68","sandw69","sandw70","sandw71","sandw72","sandw73","sandw74","sandw75","sandw76","sandw77","sandw78","sandw79","sandw80","sandw81","sandw82","sandw83","sandw84","sandw85","sandw86","sandw87","sandw88","sandw89","sandw90","sandw91","sandw92","sandw93","sandw94","sandw95","sandw96","sandw97","sandw98","sandw99","sandw100","sandw101","sandw102","sandw103","sandw104","sandw105","sandw106","sandw107","sandw108","sandw109","sandw110"}
state_childsnack_p26.trays = {"tray1","tray2","tray3","tray4","tray5","tray6","tray7","tray8","tray9","tray10"}

# predicates:
state_childsnack_p26.allergic_gluten = {"child12","child64","child60","child97","child38","child39","child48","child100","child5","child75","child49","child94","child9","child14","child58","child85","child98","child56","child93","child26","child1","child88","child54","child16","child2","child71","child55","child92","child35","child33","child79","child42","child87","child7","child24","child66","child15","child44","child77","child20","child68","child63","child52","child37","child23","child4","child34","child32","child57","child6","child103","child83","child81","child104","child59","child89","child18","child73","child101","child8","child96","child69","child65","child21","child47","child50"}
state_childsnack_p26.at = {"tray1":"kitchen","tray2":"kitchen","tray3":"kitchen","tray4":"kitchen","tray5":"kitchen","tray6":"kitchen","tray7":"kitchen","tray8":"kitchen","tray9":"kitchen","tray10":"kitchen"}
state_childsnack_p26.at_kitchen_bread = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7",
                                    "bread8","bread9","bread10","bread11","bread12","bread13","bread14","bread15","bread16","bread17","bread18","bread19","bread20","bread21","bread22","bread23","bread24","bread25","bread26","bread27","bread28","bread29","bread30","bread31","bread32","bread33","bread34","bread35","bread36","bread37","bread38","bread39","bread40","bread41","bread42","bread43","bread44","bread45","bread46","bread47","bread48","bread49","bread50","bread51","bread52","bread53","bread54","bread55","bread56","bread57","bread58","bread59","bread60","bread61","bread62","bread63","bread64","bread65","bread66","bread67","bread68","bread69","bread70","bread71","bread72","bread73","bread74","bread75","bread76","bread77","bread78","bread79","bread80","bread81","bread82","bread83","bread84","bread85","bread86","bread87","bread88","bread89","bread90","bread91","bread92","bread93","bread94","bread95","bread96","bread97","bread98","bread99","bread100","bread101","bread102","bread103","bread104","bread105","bread106","bread107","bread108","bread109","bread110"}
state_childsnack_p26.at_kitchen_content = {"content1","content2","content3","content4","content5",
                                      "content6","content7","content8","content9","content10","content11","content12","content13","content14","content15","content16","content17","content18","content19","content20","content21","content22","content23","content24","content25","content26","content27","content28","content29","content30","content31","content32","content33","content34","content35","content36","content37","content38","content39","content40","content41","content42","content43","content44","content45","content46","content47","content48","content49","content50","content51","content52","content53","content54","content55","content56","content57","content58","content59","content60","content61","content62","content63","content64","content65","content66","content67","content68","content69","content70","content71","content72","content73","content74","content75","content76","content77","content78","content79","content80","content81","content82","content83","content84","content85","content86","content87","content88","content89","content90","content91","content92","content93","content94","content95","content96","content97","content98","content99","content100","content101","content102","content103","content104","content105","content106","content107","content108","content109","content110"}
state_childsnack_p26.at_kitchen_sandwich = set()
state_childsnack_p26.not_allergic_gluten = {"child108","child86","child82","child110","child72","child109","child13","child40","child67","child22","child28","child41","child46","child11","child27","child91","child70","child62","child105","child43","child51","child106","child36","child3","child80","child76","child53","child84","child74","child107","child61","child30","child17","child29","child31","child95","child19","child90","child10","child25","child45","child99","child78","child102"}
state_childsnack_p26.notexist = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19","sandw20","sandw21","sandw22","sandw23","sandw24","sandw25","sandw26","sandw27","sandw28","sandw29","sandw30","sandw31","sandw32","sandw33","sandw34","sandw35","sandw36","sandw37","sandw38","sandw39","sandw40","sandw41","sandw42","sandw43","sandw44","sandw45","sandw46","sandw47","sandw48","sandw49","sandw50","sandw51","sandw52","sandw53","sandw54","sandw55","sandw56","sandw57","sandw58","sandw59","sandw60","sandw61","sandw62","sandw63","sandw64","sandw65","sandw66","sandw67","sandw68","sandw69","sandw70","sandw71","sandw72","sandw73","sandw74","sandw75","sandw76","sandw77","sandw78","sandw79","sandw80","sandw81","sandw82","sandw83","sandw84","sandw85","sandw86","sandw87","sandw88","sandw89","sandw90","sandw91","sandw92","sandw93","sandw94","sandw95","sandw96","sandw97","sandw98","sandw99","sandw100","sandw101","sandw102","sandw103","sandw104","sandw105","sandw106","sandw107","sandw108","sandw109","sandw110"}
state_childsnack_p26.no_gluten_bread = {"bread82","bread15","bread4","bread95","bread36","bread32","bread29","bread18","bread107","bread14","bread87","bread102","bread70","bread12","bread76","bread55","bread5","bread108","bread97","bread28","bread30","bread65","bread78","bread93","bread72","bread26","bread84","bread98","bread54","bread104","bread58","bread96","bread106","bread1","bread21","bread99","bread44","bread88","bread20","bread91","bread74","bread101","bread92","bread49","bread13","bread46","bread45","bread39","bread17","bread52","bread3","bread47","bread90","bread35","bread8","bread25","bread6","bread73","bread19","bread41","bread40","bread24","bread37","bread66","bread89","bread94"}
state_childsnack_p26.no_gluten_content = {"content6","content85","content30","content99","content38","content11","content108","content13","content49","content36","content59","content82","content47","content21","content48","content46","content27","content86","content35","content90","content88","content83","content10","content78","content107","content22","content69","content32","content97","content60","content102","content92","content72","content29","content42","content8","content104","content5","content41","content52","content79","content9","content28","content87","content68","content64","content51","content57","content100","content76","content74","content91","content17","content84","content16","content96","content101","content70","content58","content55","content106","content66","content50","content26","content24","content15"}
state_childsnack_p26.no_gluten_sandwich = set()
state_childsnack_p26.ontray = {}
state_childsnack_p26.served = {}
state_childsnack_p26.waiting = {"child1":"table1","child2":"table1","child3":"table3","child4":"table2",
                           "child5":"table3","child6":"table1","child7":"table2","child8":"table3",
                           "child9":"table3","child10":"table2","child11":"table1","child12":"table3","child13":"table3","child14":"table3","child15":"table1","child16":"table3","child17":"table2","child18":"table2","child19":"table3","child20":"table3","child21":"table2","child22":"table2","child23":"table3","child24":"table2","child25":"table1","child26":"table1","child27":"table1","child28":"table1","child29":"table2","child30":"table1","child31":"table3","child32":"table3","child33":"table1","child34":"table3","child35":"table1","child36":"table1","child37":"table1","child38":"table3","child39":"table3","child40":"table1","child41":"table1","child42":"table1","child43":"table1","child44":"table2","child45":"table1","child46":"table3","child47":"table1","child48":"table2","child49":"table3","child50":"table2","child51":"table1","child52":"table3","child53":"table1","child54":"table3","child55":"table3","child56":"table3","child57":"table2","child58":"table1","child59":"table2","child60":"table2","child61":"table1","child62":"table1","child63":"table1","child64":"table3","child65":"table2","child66":"table2","child67":"table2","child68":"table2","child69":"table2","child70":"table3","child71":"table1","child72":"table3","child73":"table3","child74":"table3","child75":"table1","child76":"table1","child77":"table2","child78":"table3","child79":"table2","child80":"table1","child81":"table1","child82":"table1","child83":"table1","child84":"table3","child85":"table2","child86":"table1","child87":"table2","child88":"table1","child89":"table2","child90":"table2","child91":"table1","child92":"table1","child93":"table2","child94":"table3","child95":"table1","child96":"table1","child97":"table3","child98":"table3","child99":"table1","child100":"table1","child101":"table1","child102":"table1","child103":"table2","child104":"table2","child105":"table2","child106":"table1","child107":"table2","child108":"table1","child109":"table1","child110":"table2"}

# Set goal from the :htn :ordered-subtasks in p26.hddl
htn_ordered_subtask_childsnack_p26 = Multigoal("goal_childsnack_p26",served=state_childsnack_p26.waiting)

# Set goal state from p26.hddl
# 	(:goal (and
# (served child1)
# (served child2)
# (served child3)
# (served child4)
# (served child5)
# (served child6)
# (served child7)
# (served child8)
# (served child9)
# (served child10)
# (served child11)
# (served child12)
# (served child13)
# (served child14)
# (served child15)
# (served child16)
# (served child17)
# (served child18)
# (served child19)
# (served child20)
# (served child21)
# (served child22)
# (served child23)
# (served child24)
# (served child25)
# (served child26)
# (served child27)
# (served child28)
# (served child29)
# (served child30)
# (served child31)
# (served child32)
# (served child33)
# (served child34)
# (served child35)
# (served child36)
# (served child37)
# (served child38)
# (served child39)
# (served child40)
# (served child41)
# (served child42)
# (served child43)
# (served child44)
# (served child45)
# (served child46)
# (served child47)
# (served child48)
# (served child49)
# (served child50)
# (served child51)
# (served child52)
# (served child53)
# (served child54)
# (served child55)
# (served child56)
# (served child57)
# (served child58)
# (served child59)
# (served child60)
# (served child61)
# (served child62)
# (served child63)
# (served child64)
# (served child65)
# (served child66)
# (served child67)
# (served child68)
# (served child69)
# (served child70)
# (served child71)
# (served child72)
# (served child73)
# (served child74)
# (served child75)
# (served child76)
# (served child77)
# (served child78)
# (served child79)
# (served child80)
# (served child81)
# (served child82)
# (served child83)
# (served child84)
# (served child85)
# (served child86)
# (served child87)
# (served child88)
# (served child89)
# (served child90)
# (served child91)
# (served child92)
# (served child93)
# (served child94)
# (served child95)
# (served child96)
# (served child97)
# (served child98)
# (served child99)
# (served child100)
# (served child101)
# (served child102)
# (served child103)
# (served child104)
# (served child105)
# (served child106)
# (served child107)
# (served child108)
# (served child109)
# (served child110)
# 	))
goal_childsnack_p26 = state_childsnack_p26.waiting

# ===== prob-snack --------------------------------------------------- p27.hddl
state_childsnack_p27 = State("snack_p27_initial_state")

# types:
state_childsnack_p27.bread_portions = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7","bread8","bread9","bread10","bread11","bread12","bread13","bread14","bread15","bread16","bread17","bread18","bread19","bread20","bread21","bread22","bread23","bread24","bread25","bread26","bread27","bread28","bread29","bread30","bread31","bread32","bread33","bread34","bread35","bread36","bread37","bread38","bread39","bread40","bread41","bread42","bread43","bread44","bread45","bread46","bread47","bread48","bread49","bread50","bread51","bread52","bread53","bread54","bread55","bread56","bread57","bread58","bread59","bread60","bread61","bread62","bread63","bread64","bread65","bread66","bread67","bread68","bread69","bread70","bread71","bread72","bread73","bread74","bread75","bread76","bread77","bread78","bread79","bread80","bread81","bread82","bread83","bread84","bread85","bread86","bread87","bread88","bread89","bread90","bread91","bread92","bread93","bread94","bread95","bread96","bread97","bread98","bread99","bread100","bread101","bread102","bread103","bread104","bread105","bread106","bread107","bread108","bread109","bread110","bread111","bread112","bread113","bread114","bread115","bread116","bread117","bread118","bread119","bread120","bread121","bread122","bread123","bread124","bread125","bread126","bread127","bread128","bread129","bread130","bread131","bread132","bread133","bread134","bread135","bread136","bread137","bread138","bread139","bread140","bread141","bread142","bread143","bread144","bread145","bread146","bread147","bread148","bread149","bread150"}
state_childsnack_p27.children = {"child1","child2","child3","child4","child5","child6","child7","child8","child9","child10","child11","child12","child13","child14","child15","child16","child17","child18","child19","child20","child21","child22","child23","child24","child25","child26","child27","child28","child29","child30","child31","child32","child33","child34","child35","child36","child37","child38","child39","child40","child41","child42","child43","child44","child45","child46","child47","child48","child49","child50","child51","child52","child53","child54","child55","child56","child57","child58","child59","child60","child61","child62","child63","child64","child65","child66","child67","child68","child69","child70","child71","child72","child73","child74","child75","child76","child77","child78","child79","child80","child81","child82","child83","child84","child85","child86","child87","child88","child89","child90","child91","child92","child93","child94","child95","child96","child97","child98","child99","child100","child101","child102","child103","child104","child105","child106","child107","child108","child109","child110","child111","child112","child113","child114","child115","child116","child117","child118","child119","child120","child121","child122","child123","child124","child125","child126","child127","child128","child129","child130","child131","child132","child133","child134","child135","child136","child137","child138","child139","child140","child141","child142","child143","child144","child145","child146","child147","child148","child149","child150"}
state_childsnack_p27.content_portions = {"content1","content2","content3","content4","content5","content6","content7","content8","content9","content10","content11","content12","content13","content14","content15","content16","content17","content18","content19","content20","content21","content22","content23","content24","content25","content26","content27","content28","content29","content30","content31","content32","content33","content34","content35","content36","content37","content38","content39","content40","content41","content42","content43","content44","content45","content46","content47","content48","content49","content50","content51","content52","content53","content54","content55","content56","content57","content58","content59","content60","content61","content62","content63","content64","content65","content66","content67","content68","content69","content70","content71","content72","content73","content74","content75","content76","content77","content78","content79","content80","content81","content82","content83","content84","content85","content86","content87","content88","content89","content90","content91","content92","content93","content94","content95","content96","content97","content98","content99","content100","content101","content102","content103","content104","content105","content106","content107","content108","content109","content110","content111","content112","content113","content114","content115","content116","content117","content118","content119","content120","content121","content122","content123","content124","content125","content126","content127","content128","content129","content130","content131","content132","content133","content134","content135","content136","content137","content138","content139","content140","content141","content142","content143","content144","content145","content146","content147","content148","content149","content150"}
state_childsnack_p27.places = {"table1","table2","table3"}
state_childsnack_p27.sandwiches = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19","sandw20","sandw21","sandw22","sandw23","sandw24","sandw25","sandw26","sandw27","sandw28","sandw29","sandw30","sandw31","sandw32","sandw33","sandw34","sandw35","sandw36","sandw37","sandw38","sandw39","sandw40","sandw41","sandw42","sandw43","sandw44","sandw45","sandw46","sandw47","sandw48","sandw49","sandw50","sandw51","sandw52","sandw53","sandw54","sandw55","sandw56","sandw57","sandw58","sandw59","sandw60","sandw61","sandw62","sandw63","sandw64","sandw65","sandw66","sandw67","sandw68","sandw69","sandw70","sandw71","sandw72","sandw73","sandw74","sandw75","sandw76","sandw77","sandw78","sandw79","sandw80","sandw81","sandw82","sandw83","sandw84","sandw85","sandw86","sandw87","sandw88","sandw89","sandw90","sandw91","sandw92","sandw93","sandw94","sandw95","sandw96","sandw97","sandw98","sandw99","sandw100","sandw101","sandw102","sandw103","sandw104","sandw105","sandw106","sandw107","sandw108","sandw109","sandw110","sandw111","sandw112","sandw113","sandw114","sandw115","sandw116","sandw117","sandw118","sandw119","sandw120","sandw121","sandw122","sandw123","sandw124","sandw125","sandw126","sandw127","sandw128","sandw129","sandw130","sandw131","sandw132","sandw133","sandw134","sandw135","sandw136","sandw137","sandw138","sandw139","sandw140","sandw141","sandw142","sandw143","sandw144","sandw145","sandw146","sandw147","sandw148","sandw149","sandw150"}
state_childsnack_p27.trays = {"tray1","tray2","tray3","tray4","tray5","tray6","tray7","tray8","tray9","tray10","tray11","tray12","tray13","tray14","tray15"}

# predicates:
state_childsnack_p27.allergic_gluten = {"child141","child74","child54","child107","child3","child116","child96","child70","child77","child35","child69","child57","child80","child60","child109","child83","child31","child10","child99","child140","child135","child122","child89","child55","child111","child126","child84","child132","child9","child7","child137","child43","child28","child61","child25","child133","child17","child78","child124","child117","child86","child92","child113","child139","child143","child128","child149","child63","child91","child108","child32","child44","child68","child18","child29","child33","child36","child129","child56","child1","child66","child64","child94","child85","child52","child81","child95","child98","child102","child30","child8","child46","child136","child120","child5","child76","child58","child87","child53","child103","child146","child101","child14","child13","child24","child42","child71","child130","child145","child93"}
state_childsnack_p27.at = {"tray1":"kitchen","tray2":"kitchen","tray3":"kitchen","tray4":"kitchen","tray5":"kitchen","tray6":"kitchen","tray7":"kitchen","tray8":"kitchen","tray9":"kitchen","tray10":"kitchen","tray11":"kitchen","tray12":"kitchen","tray13":"kitchen","tray14":"kitchen","tray15":"kitchen"}
state_childsnack_p27.at_kitchen_bread = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7",
                                    "bread8","bread9","bread10","bread11","bread12","bread13","bread14","bread15","bread16","bread17","bread18","bread19","bread20","bread21","bread22","bread23","bread24","bread25","bread26","bread27","bread28","bread29","bread30","bread31","bread32","bread33","bread34","bread35","bread36","bread37","bread38","bread39","bread40","bread41","bread42","bread43","bread44","bread45","bread46","bread47","bread48","bread49","bread50","bread51","bread52","bread53","bread54","bread55","bread56","bread57","bread58","bread59","bread60","bread61","bread62","bread63","bread64","bread65","bread66","bread67","bread68","bread69","bread70","bread71","bread72","bread73","bread74","bread75","bread76","bread77","bread78","bread79","bread80","bread81","bread82","bread83","bread84","bread85","bread86","bread87","bread88","bread89","bread90","bread91","bread92","bread93","bread94","bread95","bread96","bread97","bread98","bread99","bread100","bread101","bread102","bread103","bread104","bread105","bread106","bread107","bread108","bread109","bread110","bread111","bread112","bread113","bread114","bread115","bread116","bread117","bread118","bread119","bread120","bread121","bread122","bread123","bread124","bread125","bread126","bread127","bread128","bread129","bread130","bread131","bread132","bread133","bread134","bread135","bread136","bread137","bread138","bread139","bread140","bread141","bread142","bread143","bread144","bread145","bread146","bread147","bread148","bread149","bread150"}
state_childsnack_p27.at_kitchen_content = {"content1","content2","content3","content4","content5",
                                      "content6","content7","content8","content9","content10","content11","content12","content13","content14","content15","content16","content17","content18","content19","content20","content21","content22","content23","content24","content25","content26","content27","content28","content29","content30","content31","content32","content33","content34","content35","content36","content37","content38","content39","content40","content41","content42","content43","content44","content45","content46","content47","content48","content49","content50","content51","content52","content53","content54","content55","content56","content57","content58","content59","content60","content61","content62","content63","content64","content65","content66","content67","content68","content69","content70","content71","content72","content73","content74","content75","content76","content77","content78","content79","content80","content81","content82","content83","content84","content85","content86","content87","content88","content89","content90","content91","content92","content93","content94","content95","content96","content97","content98","content99","content100","content101","content102","content103","content104","content105","content106","content107","content108","content109","content110","content111","content112","content113","content114","content115","content116","content117","content118","content119","content120","content121","content122","content123","content124","content125","content126","content127","content128","content129","content130","content131","content132","content133","content134","content135","content136","content137","content138","content139","content140","content141","content142","content143","content144","content145","content146","content147","content148","content149","content150"}
state_childsnack_p27.at_kitchen_sandwich = set()
state_childsnack_p27.not_allergic_gluten = {"child100","child82","child73","child45","child127","child97","child20","child72","child47","child62","child48","child38","child119","child50","child123","child51","child131","child6","child15","child112","child41","child115","child27","child40","child49","child118","child144","child125","child88","child26","child67","child104","child110","child16","child2","child90","child147","child75","child105","child22","child114","child4","child79","child21","child65","child59","child23","child12","child106","child19","child134","child142","child121","child37","child39","child148","child138","child150","child34","child11"}
state_childsnack_p27.notexist = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19","sandw20","sandw21","sandw22","sandw23","sandw24","sandw25","sandw26","sandw27","sandw28","sandw29","sandw30","sandw31","sandw32","sandw33","sandw34","sandw35","sandw36","sandw37","sandw38","sandw39","sandw40","sandw41","sandw42","sandw43","sandw44","sandw45","sandw46","sandw47","sandw48","sandw49","sandw50","sandw51","sandw52","sandw53","sandw54","sandw55","sandw56","sandw57","sandw58","sandw59","sandw60","sandw61","sandw62","sandw63","sandw64","sandw65","sandw66","sandw67","sandw68","sandw69","sandw70","sandw71","sandw72","sandw73","sandw74","sandw75","sandw76","sandw77","sandw78","sandw79","sandw80","sandw81","sandw82","sandw83","sandw84","sandw85","sandw86","sandw87","sandw88","sandw89","sandw90","sandw91","sandw92","sandw93","sandw94","sandw95","sandw96","sandw97","sandw98","sandw99","sandw100","sandw101","sandw102","sandw103","sandw104","sandw105","sandw106","sandw107","sandw108","sandw109","sandw110","sandw111","sandw112","sandw113","sandw114","sandw115","sandw116","sandw117","sandw118","sandw119","sandw120","sandw121","sandw122","sandw123","sandw124","sandw125","sandw126","sandw127","sandw128","sandw129","sandw130","sandw131","sandw132","sandw133","sandw134","sandw135","sandw136","sandw137","sandw138","sandw139","sandw140","sandw141","sandw142","sandw143","sandw144","sandw145","sandw146","sandw147","sandw148","sandw149","sandw150"}
state_childsnack_p27.no_gluten_bread = {"bread29","bread7","bread71","bread63","bread58","bread36","bread27","bread140","bread23","bread109","bread9","bread8","bread24","bread56","bread60","bread130","bread149","bread51","bread108","bread57","bread115","bread72","bread2","bread98","bread104","bread21","bread90","bread55","bread44","bread145","bread20","bread28","bread127","bread122","bread14","bread12","bread49","bread13","bread46","bread141","bread45","bread78","bread34","bread126","bread6","bread94","bread59","bread69","bread16","bread114","bread11","bread148","bread38","bread81","bread80","bread47","bread74","bread25","bread91","bread143","bread106","bread85","bread30","bread118","bread100","bread88","bread113","bread101","bread121","bread107","bread95","bread125","bread48","bread112","bread144","bread35","bread10","bread22","bread103","bread32","bread79","bread136","bread83","bread75","bread150","bread42","bread139","bread15","bread53","bread3"}
state_childsnack_p27.no_gluten_content = {"content81","content103","content69","content17","content55","content150","content146","content128","content102","content118","content37","content68","content36","content64","content139","content110","content149","content93","content57","content138","content127","content24","content13","content111","content15","content20","content145","content21","content142","content88","content144","content77","content9","content50","content49","content119","content60","content136","content33","content71","content2","content121","content133","content126","content109","content148","content97","content35","content99","content83","content44","content107","content38","content56","content123","content59","content1","content108","content34","content65","content23","content91","content14","content124","content39","content82","content89","content78","content26","content125","content48","content96","content70","content113","content94","content42","content63","content3","content122","content47","content40","content31","content8","content105","content11","content66","content74","content53","content5","content116"}
state_childsnack_p27.no_gluten_sandwich = set()
state_childsnack_p27.ontray = {}
state_childsnack_p27.served = {}
state_childsnack_p27.waiting = {"child1":"table1","child2":"table1","child3":"table1","child4":"table1",
                           "child5":"table2","child6":"table2","child7":"table2","child8":"table1",
                           "child9":"table2","child10":"table1","child11":"table1","child12":"table2","child13":"table1","child14":"table2","child15":"table2","child16":"table2","child17":"table2","child18":"table2","child19":"table3","child20":"table3","child21":"table3","child22":"table3","child23":"table3","child24":"table2","child25":"table1","child26":"table1","child27":"table2","child28":"table1","child29":"table1","child30":"table3","child31":"table3","child32":"table3","child33":"table1","child34":"table3","child35":"table2","child36":"table1","child37":"table1","child38":"table3","child39":"table2","child40":"table3","child41":"table3","child42":"table1","child43":"table1","child44":"table3","child45":"table1","child46":"table1","child47":"table1","child48":"table3","child49":"table1","child50":"table3","child51":"table1","child52":"table2","child53":"table1","child54":"table3","child55":"table1","child56":"table3","child57":"table3","child58":"table1","child59":"table3","child60":"table1","child61":"table2","child62":"table3","child63":"table3","child64":"table3","child65":"table3","child66":"table2","child67":"table2","child68":"table1","child69":"table3","child70":"table3","child71":"table2","child72":"table1","child73":"table2","child74":"table2","child75":"table1","child76":"table3","child77":"table3","child78":"table2","child79":"table2","child80":"table2","child81":"table1","child82":"table1","child83":"table2","child84":"table3","child85":"table3","child86":"table1","child87":"table1","child88":"table3","child89":"table1","child90":"table3","child91":"table2","child92":"table1","child93":"table2","child94":"table1","child95":"table1","child96":"table2","child97":"table2","child98":"table1","child99":"table2","child100":"table3","child101":"table3","child102":"table2","child103":"table3","child104":"table3","child105":"table3","child106":"table1","child107":"table3","child108":"table3","child109":"table2","child110":"table3","child111":"table1","child112":"table1","child113":"table2","child114":"table1","child115":"table1","child116":"table3","child117":"table3","child118":"table1","child119":"table2","child120":"table2","child121":"table3","child122":"table1","child123":"table3","child124":"table2","child125":"table1","child126":"table3","child127":"table3","child128":"table2","child129":"table3","child130":"table2","child131":"table2","child132":"table1","child133":"table1","child134":"table3","child135":"table2","child136":"table2","child137":"table1","child138":"table1","child139":"table2","child140":"table1","child141":"table3","child142":"table2","child143":"table1","child144":"table3","child145":"table2","child146":"table3","child147":"table3","child148":"table2","child149":"table3","child150":"table1"}

# Set goal from the :htn :ordered-subtasks in p27.hddl
htn_ordered_subtask_childsnack_p27 = Multigoal("goal_childsnack_p27",served=state_childsnack_p27.waiting)

# Set goal state from p27.hddl
# 	(:goal (and
# (served child1)
# (served child2)
# (served child3)
# (served child4)
# (served child5)
# (served child6)
# (served child7)
# (served child8)
# (served child9)
# (served child10)
# (served child11)
# (served child12)
# (served child13)
# (served child14)
# (served child15)
# (served child16)
# (served child17)
# (served child18)
# (served child19)
# (served child20)
# (served child21)
# (served child22)
# (served child23)
# (served child24)
# (served child25)
# (served child26)
# (served child27)
# (served child28)
# (served child29)
# (served child30)
# (served child31)
# (served child32)
# (served child33)
# (served child34)
# (served child35)
# (served child36)
# (served child37)
# (served child38)
# (served child39)
# (served child40)
# (served child41)
# (served child42)
# (served child43)
# (served child44)
# (served child45)
# (served child46)
# (served child47)
# (served child48)
# (served child49)
# (served child50)
# (served child51)
# (served child52)
# (served child53)
# (served child54)
# (served child55)
# (served child56)
# (served child57)
# (served child58)
# (served child59)
# (served child60)
# (served child61)
# (served child62)
# (served child63)
# (served child64)
# (served child65)
# (served child66)
# (served child67)
# (served child68)
# (served child69)
# (served child70)
# (served child71)
# (served child72)
# (served child73)
# (served child74)
# (served child75)
# (served child76)
# (served child77)
# (served child78)
# (served child79)
# (served child80)
# (served child81)
# (served child82)
# (served child83)
# (served child84)
# (served child85)
# (served child86)
# (served child87)
# (served child88)
# (served child89)
# (served child90)
# (served child91)
# (served child92)
# (served child93)
# (served child94)
# (served child95)
# (served child96)
# (served child97)
# (served child98)
# (served child99)
# (served child100)
# (served child101)
# (served child102)
# (served child103)
# (served child104)
# (served child105)
# (served child106)
# (served child107)
# (served child108)
# (served child109)
# (served child110)
# (served child111)
# (served child112)
# (served child113)
# (served child114)
# (served child115)
# (served child116)
# (served child117)
# (served child118)
# (served child119)
# (served child120)
# (served child121)
# (served child122)
# (served child123)
# (served child124)
# (served child125)
# (served child126)
# (served child127)
# (served child128)
# (served child129)
# (served child130)
# (served child131)
# (served child132)
# (served child133)
# (served child134)
# (served child135)
# (served child136)
# (served child137)
# (served child138)
# (served child139)
# (served child140)
# (served child141)
# (served child142)
# (served child143)
# (served child144)
# (served child145)
# (served child146)
# (served child147)
# (served child148)
# (served child149)
# (served child150)
# 	))
goal_childsnack_p27 = state_childsnack_p27.waiting

# ===== prob-snack --------------------------------------------------- p28.hddl
state_childsnack_p28 = State("snack_p28_initial_state")

# types:
state_childsnack_p28.bread_portions = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7","bread8","bread9","bread10","bread11","bread12","bread13","bread14","bread15","bread16","bread17","bread18","bread19","bread20","bread21","bread22","bread23","bread24","bread25","bread26","bread27","bread28","bread29","bread30","bread31","bread32","bread33","bread34","bread35","bread36","bread37","bread38","bread39","bread40","bread41","bread42","bread43","bread44","bread45","bread46","bread47","bread48","bread49","bread50","bread51","bread52","bread53","bread54","bread55","bread56","bread57","bread58","bread59","bread60","bread61","bread62","bread63","bread64","bread65","bread66","bread67","bread68","bread69","bread70","bread71","bread72","bread73","bread74","bread75","bread76","bread77","bread78","bread79","bread80","bread81","bread82","bread83","bread84","bread85","bread86","bread87","bread88","bread89","bread90","bread91","bread92","bread93","bread94","bread95","bread96","bread97","bread98","bread99","bread100","bread101","bread102","bread103","bread104","bread105","bread106","bread107","bread108","bread109","bread110","bread111","bread112","bread113","bread114","bread115","bread116","bread117","bread118","bread119","bread120","bread121","bread122","bread123","bread124","bread125","bread126","bread127","bread128","bread129","bread130","bread131","bread132","bread133","bread134","bread135","bread136","bread137","bread138","bread139","bread140","bread141","bread142","bread143","bread144","bread145","bread146","bread147","bread148","bread149","bread150","bread151","bread152","bread153","bread154","bread155","bread156","bread157","bread158","bread159","bread160","bread161","bread162","bread163","bread164","bread165","bread166","bread167","bread168","bread169","bread170","bread171","bread172","bread173","bread174","bread175","bread176","bread177","bread178","bread179","bread180","bread181","bread182","bread183","bread184","bread185","bread186","bread187","bread188","bread189","bread190","bread191","bread192","bread193","bread194","bread195","bread196","bread197","bread198","bread199","bread200"}
state_childsnack_p28.children = {"child1","child2","child3","child4","child5","child6","child7","child8","child9","child10","child11","child12","child13","child14","child15","child16","child17","child18","child19","child20","child21","child22","child23","child24","child25","child26","child27","child28","child29","child30","child31","child32","child33","child34","child35","child36","child37","child38","child39","child40","child41","child42","child43","child44","child45","child46","child47","child48","child49","child50","child51","child52","child53","child54","child55","child56","child57","child58","child59","child60","child61","child62","child63","child64","child65","child66","child67","child68","child69","child70","child71","child72","child73","child74","child75","child76","child77","child78","child79","child80","child81","child82","child83","child84","child85","child86","child87","child88","child89","child90","child91","child92","child93","child94","child95","child96","child97","child98","child99","child100","child101","child102","child103","child104","child105","child106","child107","child108","child109","child110","child111","child112","child113","child114","child115","child116","child117","child118","child119","child120","child121","child122","child123","child124","child125","child126","child127","child128","child129","child130","child131","child132","child133","child134","child135","child136","child137","child138","child139","child140","child141","child142","child143","child144","child145","child146","child147","child148","child149","child150","child151","child152","child153","child154","child155","child156","child157","child158","child159","child160","child161","child162","child163","child164","child165","child166","child167","child168","child169","child170","child171","child172","child173","child174","child175","child176","child177","child178","child179","child180","child181","child182","child183","child184","child185","child186","child187","child188","child189","child190","child191","child192","child193","child194","child195","child196","child197","child198","child199","child200"}
state_childsnack_p28.content_portions = {"content1","content2","content3","content4","content5","content6","content7","content8","content9","content10","content11","content12","content13","content14","content15","content16","content17","content18","content19","content20","content21","content22","content23","content24","content25","content26","content27","content28","content29","content30","content31","content32","content33","content34","content35","content36","content37","content38","content39","content40","content41","content42","content43","content44","content45","content46","content47","content48","content49","content50","content51","content52","content53","content54","content55","content56","content57","content58","content59","content60","content61","content62","content63","content64","content65","content66","content67","content68","content69","content70","content71","content72","content73","content74","content75","content76","content77","content78","content79","content80","content81","content82","content83","content84","content85","content86","content87","content88","content89","content90","content91","content92","content93","content94","content95","content96","content97","content98","content99","content100","content101","content102","content103","content104","content105","content106","content107","content108","content109","content110","content111","content112","content113","content114","content115","content116","content117","content118","content119","content120","content121","content122","content123","content124","content125","content126","content127","content128","content129","content130","content131","content132","content133","content134","content135","content136","content137","content138","content139","content140","content141","content142","content143","content144","content145","content146","content147","content148","content149","content150","content151","content152","content153","content154","content155","content156","content157","content158","content159","content160","content161","content162","content163","content164","content165","content166","content167","content168","content169","content170","content171","content172","content173","content174","content175","content176","content177","content178","content179","content180","content181","content182","content183","content184","content185","content186","content187","content188","content189","content190","content191","content192","content193","content194","content195","content196","content197","content198","content199","content200"}
state_childsnack_p28.places = {"table1","table2","table3"}
state_childsnack_p28.sandwiches = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19","sandw20","sandw21","sandw22","sandw23","sandw24","sandw25","sandw26","sandw27","sandw28","sandw29","sandw30","sandw31","sandw32","sandw33","sandw34","sandw35","sandw36","sandw37","sandw38","sandw39","sandw40","sandw41","sandw42","sandw43","sandw44","sandw45","sandw46","sandw47","sandw48","sandw49","sandw50","sandw51","sandw52","sandw53","sandw54","sandw55","sandw56","sandw57","sandw58","sandw59","sandw60","sandw61","sandw62","sandw63","sandw64","sandw65","sandw66","sandw67","sandw68","sandw69","sandw70","sandw71","sandw72","sandw73","sandw74","sandw75","sandw76","sandw77","sandw78","sandw79","sandw80","sandw81","sandw82","sandw83","sandw84","sandw85","sandw86","sandw87","sandw88","sandw89","sandw90","sandw91","sandw92","sandw93","sandw94","sandw95","sandw96","sandw97","sandw98","sandw99","sandw100","sandw101","sandw102","sandw103","sandw104","sandw105","sandw106","sandw107","sandw108","sandw109","sandw110","sandw111","sandw112","sandw113","sandw114","sandw115","sandw116","sandw117","sandw118","sandw119","sandw120","sandw121","sandw122","sandw123","sandw124","sandw125","sandw126","sandw127","sandw128","sandw129","sandw130","sandw131","sandw132","sandw133","sandw134","sandw135","sandw136","sandw137","sandw138","sandw139","sandw140","sandw141","sandw142","sandw143","sandw144","sandw145","sandw146","sandw147","sandw148","sandw149","sandw150","sandw151","sandw152","sandw153","sandw154","sandw155","sandw156","sandw157","sandw158","sandw159","sandw160","sandw161","sandw162","sandw163","sandw164","sandw165","sandw166","sandw167","sandw168","sandw169","sandw170","sandw171","sandw172","sandw173","sandw174","sandw175","sandw176","sandw177","sandw178","sandw179","sandw180","sandw181","sandw182","sandw183","sandw184","sandw185","sandw186","sandw187","sandw188","sandw189","sandw190","sandw191","sandw192","sandw193","sandw194","sandw195","sandw196","sandw197","sandw198","sandw199","sandw200"}
state_childsnack_p28.trays = {"tray1","tray2","tray3","tray4","tray5","tray6","tray7","tray8","tray9","tray10","tray11","tray12","tray13","tray14","tray15","tray16","tray17","tray18","tray19","tray20"}

# predicates:
state_childsnack_p28.allergic_gluten = {"child136","child198","child87","child172","child101","child89","child74","child114","child15","child43","child56","child14","child184","child91","child181","child50","child193","child190","child41","child106","child182","child156","child9","child47","child59","child123","child81","child4","child129","child61","child100","child197","child163","child2","child105","child52","child192","child119","child168","child109","child116","child103","child17","child153","child180","child138","child183","child115","child68","child85","child25","child73","child24","child130","child122","child146","child77","child141","child72","child54","child67","child32","child155","child111","child26","child98","child104","child13","child160","child21","child124","child169","child39","child143","child142","child51","child86","child63","child134","child120","child20","child189","child31","child83","child76","child191","child1","child36","child137","child75","child117","child133","child176","child34","child187","child139","child6","child166","child179","child144","child196","child80","child64","child27","child10","child11","child125","child99","child158","child28","child178","child40","child69","child92","child121","child49","child16","child55","child152","child173"}
state_childsnack_p28.at = {"tray1":"kitchen","tray2":"kitchen","tray3":"kitchen","tray4":"kitchen","tray5":"kitchen","tray6":"kitchen","tray7":"kitchen","tray8":"kitchen","tray9":"kitchen","tray10":"kitchen","tray11":"kitchen","tray12":"kitchen","tray13":"kitchen","tray14":"kitchen","tray15":"kitchen","tray16":"kitchen","tray17":"kitchen","tray18":"kitchen","tray19":"kitchen","tray20":"kitchen"}
state_childsnack_p28.at_kitchen_bread = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7",
                                    "bread8","bread9","bread10","bread11","bread12","bread13","bread14","bread15","bread16","bread17","bread18","bread19","bread20","bread21","bread22","bread23","bread24","bread25","bread26","bread27","bread28","bread29","bread30","bread31","bread32","bread33","bread34","bread35","bread36","bread37","bread38","bread39","bread40","bread41","bread42","bread43","bread44","bread45","bread46","bread47","bread48","bread49","bread50","bread51","bread52","bread53","bread54","bread55","bread56","bread57","bread58","bread59","bread60","bread61","bread62","bread63","bread64","bread65","bread66","bread67","bread68","bread69","bread70","bread71","bread72","bread73","bread74","bread75","bread76","bread77","bread78","bread79","bread80","bread81","bread82","bread83","bread84","bread85","bread86","bread87","bread88","bread89","bread90","bread91","bread92","bread93","bread94","bread95","bread96","bread97","bread98","bread99","bread100","bread101","bread102","bread103","bread104","bread105","bread106","bread107","bread108","bread109","bread110","bread111","bread112","bread113","bread114","bread115","bread116","bread117","bread118","bread119","bread120","bread121","bread122","bread123","bread124","bread125","bread126","bread127","bread128","bread129","bread130","bread131","bread132","bread133","bread134","bread135","bread136","bread137","bread138","bread139","bread140","bread141","bread142","bread143","bread144","bread145","bread146","bread147","bread148","bread149","bread150","bread151","bread152","bread153","bread154","bread155","bread156","bread157","bread158","bread159","bread160","bread161","bread162","bread163","bread164","bread165","bread166","bread167","bread168","bread169","bread170","bread171","bread172","bread173","bread174","bread175","bread176","bread177","bread178","bread179","bread180","bread181","bread182","bread183","bread184","bread185","bread186","bread187","bread188","bread189","bread190","bread191","bread192","bread193","bread194","bread195","bread196","bread197","bread198","bread199","bread200"}
state_childsnack_p28.at_kitchen_content = {"content1","content2","content3","content4","content5",
                                      "content6","content7","content8","content9","content10","content11","content12","content13","content14","content15","content16","content17","content18","content19","content20","content21","content22","content23","content24","content25","content26","content27","content28","content29","content30","content31","content32","content33","content34","content35","content36","content37","content38","content39","content40","content41","content42","content43","content44","content45","content46","content47","content48","content49","content50","content51","content52","content53","content54","content55","content56","content57","content58","content59","content60","content61","content62","content63","content64","content65","content66","content67","content68","content69","content70","content71","content72","content73","content74","content75","content76","content77","content78","content79","content80","content81","content82","content83","content84","content85","content86","content87","content88","content89","content90","content91","content92","content93","content94","content95","content96","content97","content98","content99","content100","content101","content102","content103","content104","content105","content106","content107","content108","content109","content110","content111","content112","content113","content114","content115","content116","content117","content118","content119","content120","content121","content122","content123","content124","content125","content126","content127","content128","content129","content130","content131","content132","content133","content134","content135","content136","content137","content138","content139","content140","content141","content142","content143","content144","content145","content146","content147","content148","content149","content150","content151","content152","content153","content154","content155","content156","content157","content158","content159","content160","content161","content162","content163","content164","content165","content166","content167","content168","content169","content170","content171","content172","content173","content174","content175","content176","content177","content178","content179","content180","content181","content182","content183","content184","content185","content186","content187","content188","content189","content190","content191","content192","content193","content194","content195","content196","content197","content198","content199","content200"}
state_childsnack_p28.at_kitchen_sandwich = set()
state_childsnack_p28.not_allergic_gluten = {"child113","child194","child110","child200","child70","child8","child78","child177","child135","child60","child65","child88","child58","child162","child37","child154","child188","child164","child84","child107","child149","child46","child171","child45","child62","child22","child82","child96","child161","child33","child48","child57","child3","child186","child66","child127","child97","child118","child53","child90","child170","child175","child148","child94","child79","child29","child5","child35","child38","child157","child23","child150","child12","child165","child7","child42","child112","child132","child19","child185","child195","child140","child147","child102","child95","child44","child145","child108","child167","child71","child199","child93","child126","child131","child174","child18","child128","child30","child159","child151"}
state_childsnack_p28.notexist = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19","sandw20","sandw21","sandw22","sandw23","sandw24","sandw25","sandw26","sandw27","sandw28","sandw29","sandw30","sandw31","sandw32","sandw33","sandw34","sandw35","sandw36","sandw37","sandw38","sandw39","sandw40","sandw41","sandw42","sandw43","sandw44","sandw45","sandw46","sandw47","sandw48","sandw49","sandw50","sandw51","sandw52","sandw53","sandw54","sandw55","sandw56","sandw57","sandw58","sandw59","sandw60","sandw61","sandw62","sandw63","sandw64","sandw65","sandw66","sandw67","sandw68","sandw69","sandw70","sandw71","sandw72","sandw73","sandw74","sandw75","sandw76","sandw77","sandw78","sandw79","sandw80","sandw81","sandw82","sandw83","sandw84","sandw85","sandw86","sandw87","sandw88","sandw89","sandw90","sandw91","sandw92","sandw93","sandw94","sandw95","sandw96","sandw97","sandw98","sandw99","sandw100","sandw101","sandw102","sandw103","sandw104","sandw105","sandw106","sandw107","sandw108","sandw109","sandw110","sandw111","sandw112","sandw113","sandw114","sandw115","sandw116","sandw117","sandw118","sandw119","sandw120","sandw121","sandw122","sandw123","sandw124","sandw125","sandw126","sandw127","sandw128","sandw129","sandw130","sandw131","sandw132","sandw133","sandw134","sandw135","sandw136","sandw137","sandw138","sandw139","sandw140","sandw141","sandw142","sandw143","sandw144","sandw145","sandw146","sandw147","sandw148","sandw149","sandw150","sandw151","sandw152","sandw153","sandw154","sandw155","sandw156","sandw157","sandw158","sandw159","sandw160","sandw161","sandw162","sandw163","sandw164","sandw165","sandw166","sandw167","sandw168","sandw169","sandw170","sandw171","sandw172","sandw173","sandw174","sandw175","sandw176","sandw177","sandw178","sandw179","sandw180","sandw181","sandw182","sandw183","sandw184","sandw185","sandw186","sandw187","sandw188","sandw189","sandw190","sandw191","sandw192","sandw193","sandw194","sandw195","sandw196","sandw197","sandw198","sandw199","sandw200"}
state_childsnack_p28.no_gluten_bread = {"bread164","bread29","bread7","bread190","bread71","bread63","bread58","bread36","bread189","bread27","bread174","bread140","bread23","bread152","bread109","bread9","bread8","bread24","bread56","bread60","bread130","bread155","bread198","bread144","bread51","bread167","bread192","bread108","bread57","bread115","bread151","bread72","bread2","bread41","bread186","bread88","bread169","bread40","bread182","bread87","bread191","bread183","bread98","bread25","bread92","bread89","bread68","bread12","bread118","bread138","bread32","bread97","bread21","bread142","bread76","bread93","bread50","bread18","bread153","bread59","bread75","bread148","bread181","bread26","bread158","bread200","bread117","bread94","bread42","bread95","bread91","bread54","bread69","bread90","bread120","bread165","bread83","bread10","bread78","bread82","bread22","bread128","bread133","bread150","bread139","bread170","bread49","bread35","bread121","bread179","bread135","bread199","bread125","bread132","bread99","bread100","bread184","bread30","bread5","bread175","bread52","bread113","bread185","bread28","bread73","bread156","bread101","bread149","bread84","bread64","bread176","bread124","bread141","bread19","bread34","bread143","bread134","bread110","bread119","bread86"}
state_childsnack_p28.no_gluten_content = {"content192","content150","content110","content199","content103","content93","content57","content36","content131","content127","content24","content13","content29","content40","content161","content41","content175","content109","content153","content17","content99","content98","content182","content120","content136","content65","content142","content3","content30","content138","content69","content165","content88","content188","content76","content112","content185","content117","content1","content68","content129","content46","content130","content28","content77","content158","content51","content187","content96","content42","content139","content176","content162","content83","content126","content5","content167","content195","content79","content62","content15","content141","content21","content22","content125","content18","content33","content134","content122","content43","content186","content183","content55","content119","content70","content97","content94","content89","content26","content92","content178","content52","content86","content84","content48","content194","content67","content58","content16","content32","content144","content9","content44","content173","content166","content71","content172","content106","content198","content148","content10","content91","content81","content8","content104","content160","content145","content200","content100","content66","content31","content193","content118","content63","content157","content146","content181","content74","content147","content61"}
state_childsnack_p28.no_gluten_sandwich = set()
state_childsnack_p28.ontray = {}
state_childsnack_p28.served = {}
state_childsnack_p28.waiting = {"child1":"table3","child2":"table2","child3":"table1","child4":"table2",
                           "child5":"table1","child6":"table1","child7":"table2","child8":"table2",
                           "child9":"table1","child10":"table2","child11":"table3","child12":"table3","child13":"table2","child14":"table3","child15":"table3","child16":"table3","child17":"table1","child18":"table3","child19":"table3","child20":"table2","child21":"table3","child22":"table1","child23":"table1","child24":"table2","child25":"table1","child26":"table1","child27":"table3","child28":"table3","child29":"table1","child30":"table2","child31":"table2","child32":"table3","child33":"table1","child34":"table3","child35":"table2","child36":"table1","child37":"table3","child38":"table3","child39":"table2","child40":"table3","child41":"table2","child42":"table2","child43":"table1","child44":"table1","child45":"table3","child46":"table2","child47":"table2","child48":"table1","child49":"table1","child50":"table2","child51":"table1","child52":"table3","child53":"table2","child54":"table1","child55":"table3","child56":"table2","child57":"table3","child58":"table3","child59":"table2","child60":"table3","child61":"table1","child62":"table1","child63":"table1","child64":"table3","child65":"table1","child66":"table3","child67":"table1","child68":"table2","child69":"table3","child70":"table3","child71":"table1","child72":"table2","child73":"table1","child74":"table1","child75":"table2","child76":"table2","child77":"table1","child78":"table2","child79":"table1","child80":"table3","child81":"table1","child82":"table3","child83":"table1","child84":"table2","child85":"table3","child86":"table2","child87":"table3","child88":"table3","child89":"table1","child90":"table1","child91":"table1","child92":"table1","child93":"table2","child94":"table1","child95":"table1","child96":"table3","child97":"table2","child98":"table2","child99":"table3","child100":"table3","child101":"table1","child102":"table2","child103":"table1","child104":"table3","child105":"table1","child106":"table2","child107":"table1","child108":"table2","child109":"table1","child110":"table1","child111":"table2","child112":"table2","child113":"table2","child114":"table1","child115":"table1","child116":"table1","child117":"table3","child118":"table1","child119":"table2","child120":"table2","child121":"table2","child122":"table1","child123":"table2","child124":"table2","child125":"table3","child126":"table3","child127":"table2","child128":"table3","child129":"table3","child130":"table2","child131":"table1","child132":"table1","child133":"table2","child134":"table1","child135":"table3","child136":"table2","child137":"table1","child138":"table1","child139":"table3","child140":"table2","child141":"table2","child142":"table3","child143":"table2","child144":"table2","child145":"table3","child146":"table3","child147":"table1","child148":"table2","child149":"table3","child150":"table1","child151":"table2","child152":"table1","child153":"table3","child154":"table2","child155":"table1","child156":"table3","child157":"table3","child158":"table3","child159":"table3","child160":"table3","child161":"table3","child162":"table3","child163":"table1","child164":"table2","child165":"table2","child166":"table1","child167":"table3","child168":"table2","child169":"table3","child170":"table2","child171":"table3","child172":"table1","child173":"table3","child174":"table2","child175":"table3","child176":"table2","child177":"table3","child178":"table2","child179":"table2","child180":"table2","child181":"table3","child182":"table2","child183":"table3","child184":"table1","child185":"table1","child186":"table2","child187":"table3","child188":"table2","child189":"table3","child190":"table3","child191":"table1","child192":"table3","child193":"table3","child194":"table2","child195":"table2","child196":"table3","child197":"table1","child198":"table2","child199":"table2","child200":"table1"}

# Set goal from the :htn :ordered-subtasks in p28.hddl
htn_ordered_subtask_childsnack_p28 = Multigoal("goal_childsnack_p28",served=state_childsnack_p28.waiting)

# Set goal state from p28.hddl
# 	(:goal (and
# (served child1)
# (served child2)
# (served child3)
# (served child4)
# (served child5)
# (served child6)
# (served child7)
# (served child8)
# (served child9)
# (served child10)
# (served child11)
# (served child12)
# (served child13)
# (served child14)
# (served child15)
# (served child16)
# (served child17)
# (served child18)
# (served child19)
# (served child20)
# (served child21)
# (served child22)
# (served child23)
# (served child24)
# (served child25)
# (served child26)
# (served child27)
# (served child28)
# (served child29)
# (served child30)
# (served child31)
# (served child32)
# (served child33)
# (served child34)
# (served child35)
# (served child36)
# (served child37)
# (served child38)
# (served child39)
# (served child40)
# (served child41)
# (served child42)
# (served child43)
# (served child44)
# (served child45)
# (served child46)
# (served child47)
# (served child48)
# (served child49)
# (served child50)
# (served child51)
# (served child52)
# (served child53)
# (served child54)
# (served child55)
# (served child56)
# (served child57)
# (served child58)
# (served child59)
# (served child60)
# (served child61)
# (served child62)
# (served child63)
# (served child64)
# (served child65)
# (served child66)
# (served child67)
# (served child68)
# (served child69)
# (served child70)
# (served child71)
# (served child72)
# (served child73)
# (served child74)
# (served child75)
# (served child76)
# (served child77)
# (served child78)
# (served child79)
# (served child80)
# (served child81)
# (served child82)
# (served child83)
# (served child84)
# (served child85)
# (served child86)
# (served child87)
# (served child88)
# (served child89)
# (served child90)
# (served child91)
# (served child92)
# (served child93)
# (served child94)
# (served child95)
# (served child96)
# (served child97)
# (served child98)
# (served child99)
# (served child100)
# (served child101)
# (served child102)
# (served child103)
# (served child104)
# (served child105)
# (served child106)
# (served child107)
# (served child108)
# (served child109)
# (served child110)
# (served child111)
# (served child112)
# (served child113)
# (served child114)
# (served child115)
# (served child116)
# (served child117)
# (served child118)
# (served child119)
# (served child120)
# (served child121)
# (served child122)
# (served child123)
# (served child124)
# (served child125)
# (served child126)
# (served child127)
# (served child128)
# (served child129)
# (served child130)
# (served child131)
# (served child132)
# (served child133)
# (served child134)
# (served child135)
# (served child136)
# (served child137)
# (served child138)
# (served child139)
# (served child140)
# (served child141)
# (served child142)
# (served child143)
# (served child144)
# (served child145)
# (served child146)
# (served child147)
# (served child148)
# (served child149)
# (served child150)
# (served child151)
# (served child152)
# (served child153)
# (served child154)
# (served child155)
# (served child156)
# (served child157)
# (served child158)
# (served child159)
# (served child160)
# (served child161)
# (served child162)
# (served child163)
# (served child164)
# (served child165)
# (served child166)
# (served child167)
# (served child168)
# (served child169)
# (served child170)
# (served child171)
# (served child172)
# (served child173)
# (served child174)
# (served child175)
# (served child176)
# (served child177)
# (served child178)
# (served child179)
# (served child180)
# (served child181)
# (served child182)
# (served child183)
# (served child184)
# (served child185)
# (served child186)
# (served child187)
# (served child188)
# (served child189)
# (served child190)
# (served child191)
# (served child192)
# (served child193)
# (served child194)
# (served child195)
# (served child196)
# (served child197)
# (served child198)
# (served child199)
# (served child200)
# 	))
goal_childsnack_p28 = state_childsnack_p28.waiting

# ===== prob-snack --------------------------------------------------- p29.hddl
state_childsnack_p29 = State("snack_p29_initial_state")

# types:
state_childsnack_p29.bread_portions = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7","bread8","bread9","bread10","bread11","bread12","bread13","bread14","bread15","bread16","bread17","bread18","bread19","bread20","bread21","bread22","bread23","bread24","bread25","bread26","bread27","bread28","bread29","bread30","bread31","bread32","bread33","bread34","bread35","bread36","bread37","bread38","bread39","bread40","bread41","bread42","bread43","bread44","bread45","bread46","bread47","bread48","bread49","bread50","bread51","bread52","bread53","bread54","bread55","bread56","bread57","bread58","bread59","bread60","bread61","bread62","bread63","bread64","bread65","bread66","bread67","bread68","bread69","bread70","bread71","bread72","bread73","bread74","bread75","bread76","bread77","bread78","bread79","bread80","bread81","bread82","bread83","bread84","bread85","bread86","bread87","bread88","bread89","bread90","bread91","bread92","bread93","bread94","bread95","bread96","bread97","bread98","bread99","bread100","bread101","bread102","bread103","bread104","bread105","bread106","bread107","bread108","bread109","bread110","bread111","bread112","bread113","bread114","bread115","bread116","bread117","bread118","bread119","bread120","bread121","bread122","bread123","bread124","bread125","bread126","bread127","bread128","bread129","bread130","bread131","bread132","bread133","bread134","bread135","bread136","bread137","bread138","bread139","bread140","bread141","bread142","bread143","bread144","bread145","bread146","bread147","bread148","bread149","bread150","bread151","bread152","bread153","bread154","bread155","bread156","bread157","bread158","bread159","bread160","bread161","bread162","bread163","bread164","bread165","bread166","bread167","bread168","bread169","bread170","bread171","bread172","bread173","bread174","bread175","bread176","bread177","bread178","bread179","bread180","bread181","bread182","bread183","bread184","bread185","bread186","bread187","bread188","bread189","bread190","bread191","bread192","bread193","bread194","bread195","bread196","bread197","bread198","bread199","bread200","bread201","bread202","bread203","bread204","bread205","bread206","bread207","bread208","bread209","bread210","bread211","bread212","bread213","bread214","bread215","bread216","bread217","bread218","bread219","bread220","bread221","bread222","bread223","bread224","bread225","bread226","bread227","bread228","bread229","bread230","bread231","bread232","bread233","bread234","bread235","bread236","bread237","bread238","bread239","bread240","bread241","bread242","bread243","bread244","bread245","bread246","bread247","bread248","bread249","bread250","bread251","bread252","bread253","bread254","bread255","bread256","bread257","bread258","bread259","bread260","bread261","bread262","bread263","bread264","bread265","bread266","bread267","bread268","bread269","bread270","bread271","bread272","bread273","bread274","bread275","bread276","bread277","bread278","bread279","bread280","bread281","bread282","bread283","bread284","bread285","bread286","bread287","bread288","bread289","bread290","bread291","bread292","bread293","bread294","bread295","bread296","bread297","bread298","bread299","bread300"}
state_childsnack_p29.children = {"child1","child2","child3","child4","child5","child6","child7","child8","child9","child10","child11","child12","child13","child14","child15","child16","child17","child18","child19","child20","child21","child22","child23","child24","child25","child26","child27","child28","child29","child30","child31","child32","child33","child34","child35","child36","child37","child38","child39","child40","child41","child42","child43","child44","child45","child46","child47","child48","child49","child50","child51","child52","child53","child54","child55","child56","child57","child58","child59","child60","child61","child62","child63","child64","child65","child66","child67","child68","child69","child70","child71","child72","child73","child74","child75","child76","child77","child78","child79","child80","child81","child82","child83","child84","child85","child86","child87","child88","child89","child90","child91","child92","child93","child94","child95","child96","child97","child98","child99","child100","child101","child102","child103","child104","child105","child106","child107","child108","child109","child110","child111","child112","child113","child114","child115","child116","child117","child118","child119","child120","child121","child122","child123","child124","child125","child126","child127","child128","child129","child130","child131","child132","child133","child134","child135","child136","child137","child138","child139","child140","child141","child142","child143","child144","child145","child146","child147","child148","child149","child150","child151","child152","child153","child154","child155","child156","child157","child158","child159","child160","child161","child162","child163","child164","child165","child166","child167","child168","child169","child170","child171","child172","child173","child174","child175","child176","child177","child178","child179","child180","child181","child182","child183","child184","child185","child186","child187","child188","child189","child190","child191","child192","child193","child194","child195","child196","child197","child198","child199","child200","child201","child202","child203","child204","child205","child206","child207","child208","child209","child210","child211","child212","child213","child214","child215","child216","child217","child218","child219","child220","child221","child222","child223","child224","child225","child226","child227","child228","child229","child230","child231","child232","child233","child234","child235","child236","child237","child238","child239","child240","child241","child242","child243","child244","child245","child246","child247","child248","child249","child250","child251","child252","child253","child254","child255","child256","child257","child258","child259","child260","child261","child262","child263","child264","child265","child266","child267","child268","child269","child270","child271","child272","child273","child274","child275","child276","child277","child278","child279","child280","child281","child282","child283","child284","child285","child286","child287","child288","child289","child290","child291","child292","child293","child294","child295","child296","child297","child298","child299","child300"}
state_childsnack_p29.content_portions = {"content1","content2","content3","content4","content5","content6","content7","content8","content9","content10","content11","content12","content13","content14","content15","content16","content17","content18","content19","content20","content21","content22","content23","content24","content25","content26","content27","content28","content29","content30","content31","content32","content33","content34","content35","content36","content37","content38","content39","content40","content41","content42","content43","content44","content45","content46","content47","content48","content49","content50","content51","content52","content53","content54","content55","content56","content57","content58","content59","content60","content61","content62","content63","content64","content65","content66","content67","content68","content69","content70","content71","content72","content73","content74","content75","content76","content77","content78","content79","content80","content81","content82","content83","content84","content85","content86","content87","content88","content89","content90","content91","content92","content93","content94","content95","content96","content97","content98","content99","content100","content101","content102","content103","content104","content105","content106","content107","content108","content109","content110","content111","content112","content113","content114","content115","content116","content117","content118","content119","content120","content121","content122","content123","content124","content125","content126","content127","content128","content129","content130","content131","content132","content133","content134","content135","content136","content137","content138","content139","content140","content141","content142","content143","content144","content145","content146","content147","content148","content149","content150","content151","content152","content153","content154","content155","content156","content157","content158","content159","content160","content161","content162","content163","content164","content165","content166","content167","content168","content169","content170","content171","content172","content173","content174","content175","content176","content177","content178","content179","content180","content181","content182","content183","content184","content185","content186","content187","content188","content189","content190","content191","content192","content193","content194","content195","content196","content197","content198","content199","content200","content201","content202","content203","content204","content205","content206","content207","content208","content209","content210","content211","content212","content213","content214","content215","content216","content217","content218","content219","content220","content221","content222","content223","content224","content225","content226","content227","content228","content229","content230","content231","content232","content233","content234","content235","content236","content237","content238","content239","content240","content241","content242","content243","content244","content245","content246","content247","content248","content249","content250","content251","content252","content253","content254","content255","content256","content257","content258","content259","content260","content261","content262","content263","content264","content265","content266","content267","content268","content269","content270","content271","content272","content273","content274","content275","content276","content277","content278","content279","content280","content281","content282","content283","content284","content285","content286","content287","content288","content289","content290","content291","content292","content293","content294","content295","content296","content297","content298","content299","content300"}
state_childsnack_p29.places = {"table1","table2","table3"}
state_childsnack_p29.sandwiches = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19","sandw20","sandw21","sandw22","sandw23","sandw24","sandw25","sandw26","sandw27","sandw28","sandw29","sandw30","sandw31","sandw32","sandw33","sandw34","sandw35","sandw36","sandw37","sandw38","sandw39","sandw40","sandw41","sandw42","sandw43","sandw44","sandw45","sandw46","sandw47","sandw48","sandw49","sandw50","sandw51","sandw52","sandw53","sandw54","sandw55","sandw56","sandw57","sandw58","sandw59","sandw60","sandw61","sandw62","sandw63","sandw64","sandw65","sandw66","sandw67","sandw68","sandw69","sandw70","sandw71","sandw72","sandw73","sandw74","sandw75","sandw76","sandw77","sandw78","sandw79","sandw80","sandw81","sandw82","sandw83","sandw84","sandw85","sandw86","sandw87","sandw88","sandw89","sandw90","sandw91","sandw92","sandw93","sandw94","sandw95","sandw96","sandw97","sandw98","sandw99","sandw100","sandw101","sandw102","sandw103","sandw104","sandw105","sandw106","sandw107","sandw108","sandw109","sandw110","sandw111","sandw112","sandw113","sandw114","sandw115","sandw116","sandw117","sandw118","sandw119","sandw120","sandw121","sandw122","sandw123","sandw124","sandw125","sandw126","sandw127","sandw128","sandw129","sandw130","sandw131","sandw132","sandw133","sandw134","sandw135","sandw136","sandw137","sandw138","sandw139","sandw140","sandw141","sandw142","sandw143","sandw144","sandw145","sandw146","sandw147","sandw148","sandw149","sandw150","sandw151","sandw152","sandw153","sandw154","sandw155","sandw156","sandw157","sandw158","sandw159","sandw160","sandw161","sandw162","sandw163","sandw164","sandw165","sandw166","sandw167","sandw168","sandw169","sandw170","sandw171","sandw172","sandw173","sandw174","sandw175","sandw176","sandw177","sandw178","sandw179","sandw180","sandw181","sandw182","sandw183","sandw184","sandw185","sandw186","sandw187","sandw188","sandw189","sandw190","sandw191","sandw192","sandw193","sandw194","sandw195","sandw196","sandw197","sandw198","sandw199","sandw200","sandw201","sandw202","sandw203","sandw204","sandw205","sandw206","sandw207","sandw208","sandw209","sandw210","sandw211","sandw212","sandw213","sandw214","sandw215","sandw216","sandw217","sandw218","sandw219","sandw220","sandw221","sandw222","sandw223","sandw224","sandw225","sandw226","sandw227","sandw228","sandw229","sandw230","sandw231","sandw232","sandw233","sandw234","sandw235","sandw236","sandw237","sandw238","sandw239","sandw240","sandw241","sandw242","sandw243","sandw244","sandw245","sandw246","sandw247","sandw248","sandw249","sandw250","sandw251","sandw252","sandw253","sandw254","sandw255","sandw256","sandw257","sandw258","sandw259","sandw260","sandw261","sandw262","sandw263","sandw264","sandw265","sandw266","sandw267","sandw268","sandw269","sandw270","sandw271","sandw272","sandw273","sandw274","sandw275","sandw276","sandw277","sandw278","sandw279","sandw280","sandw281","sandw282","sandw283","sandw284","sandw285","sandw286","sandw287","sandw288","sandw289","sandw290","sandw291","sandw292","sandw293","sandw294","sandw295","sandw296","sandw297","sandw298","sandw299","sandw300"}
state_childsnack_p29.trays = {"tray1","tray2","tray3","tray4","tray5","tray6","tray7","tray8","tray9","tray10","tray11","tray12","tray13","tray14","tray15","tray16","tray17","tray18","tray19","tray20","tray21","tray22","tray23","tray24","tray25"}

# predicates:
state_childsnack_p29.allergic_gluten = {"child10","child79","child98","child202","child130","child222","child200","child158","child169","child208","child135","child27","child86","child238","child233","child134","child172","child125","child192","child77","child78","child55","child226","child282","child42","child225","child155","child105","child57","child298","child286","child61","child18","child196","child162","child139","child95","child8","child46","child183","child106","child224","child175","child186","child48","child142","child51","child239","child174","child19","child254","child72","child112","child76","child85","child84","child259","child229","child277","child68","child30","child262","child193","child102","child131","child195","child94","child64","child219","child23","child149","child176","child67","child221","child173","child59","child194","child273","child210","child279","child201","child104","child270","child154","child92","child156","child237","child32","child190","child297","child80","child260","child231","child294","child2","child60","child203","child197","child218","child111","child39","child136","child147","child246","child209","child66","child187","child91","child291","child114","child284","child118","child295","child41","child204","child185","child165","child217","child269","child89","child249","child255","child7","child205","child266","child103","child251","child83","child180","child121","child271","child293","child69","child228","child108","child140","child81","child272","child216","child45","child138","child289","child245","child33","child52","child129","child58","child264","child12","child50","child157","child227","child144","child145","child247","child151","child159","child290","child223","child1","child5","child153","child49","child261","child90","child206","child148","child99","child54","child22","child40","child74","child123","child116","child28","child189","child11","child171","child276","child120"}
state_childsnack_p29.at = {"tray1":"kitchen","tray2":"kitchen","tray3":"kitchen","tray4":"kitchen","tray5":"kitchen","tray6":"kitchen","tray7":"kitchen","tray8":"kitchen","tray9":"kitchen","tray10":"kitchen","tray11":"kitchen","tray12":"kitchen","tray13":"kitchen","tray14":"kitchen","tray15":"kitchen","tray16":"kitchen","tray17":"kitchen","tray18":"kitchen","tray19":"kitchen","tray20":"kitchen","tray21":"kitchen","tray22":"kitchen","tray23":"kitchen","tray24":"kitchen","tray25":"kitchen"}
state_childsnack_p29.at_kitchen_bread = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7",
                                    "bread8","bread9","bread10","bread11","bread12","bread13","bread14","bread15","bread16","bread17","bread18","bread19","bread20","bread21","bread22","bread23","bread24","bread25","bread26","bread27","bread28","bread29","bread30","bread31","bread32","bread33","bread34","bread35","bread36","bread37","bread38","bread39","bread40","bread41","bread42","bread43","bread44","bread45","bread46","bread47","bread48","bread49","bread50","bread51","bread52","bread53","bread54","bread55","bread56","bread57","bread58","bread59","bread60","bread61","bread62","bread63","bread64","bread65","bread66","bread67","bread68","bread69","bread70","bread71","bread72","bread73","bread74","bread75","bread76","bread77","bread78","bread79","bread80","bread81","bread82","bread83","bread84","bread85","bread86","bread87","bread88","bread89","bread90","bread91","bread92","bread93","bread94","bread95","bread96","bread97","bread98","bread99","bread100","bread101","bread102","bread103","bread104","bread105","bread106","bread107","bread108","bread109","bread110","bread111","bread112","bread113","bread114","bread115","bread116","bread117","bread118","bread119","bread120","bread121","bread122","bread123","bread124","bread125","bread126","bread127","bread128","bread129","bread130","bread131","bread132","bread133","bread134","bread135","bread136","bread137","bread138","bread139","bread140","bread141","bread142","bread143","bread144","bread145","bread146","bread147","bread148","bread149","bread150","bread151","bread152","bread153","bread154","bread155","bread156","bread157","bread158","bread159","bread160","bread161","bread162","bread163","bread164","bread165","bread166","bread167","bread168","bread169","bread170","bread171","bread172","bread173","bread174","bread175","bread176","bread177","bread178","bread179","bread180","bread181","bread182","bread183","bread184","bread185","bread186","bread187","bread188","bread189","bread190","bread191","bread192","bread193","bread194","bread195","bread196","bread197","bread198","bread199","bread200","bread201","bread202","bread203","bread204","bread205","bread206","bread207","bread208","bread209","bread210","bread211","bread212","bread213","bread214","bread215","bread216","bread217","bread218","bread219","bread220","bread221","bread222","bread223","bread224","bread225","bread226","bread227","bread228","bread229","bread230","bread231","bread232","bread233","bread234","bread235","bread236","bread237","bread238","bread239","bread240","bread241","bread242","bread243","bread244","bread245","bread246","bread247","bread248","bread249","bread250","bread251","bread252","bread253","bread254","bread255","bread256","bread257","bread258","bread259","bread260","bread261","bread262","bread263","bread264","bread265","bread266","bread267","bread268","bread269","bread270","bread271","bread272","bread273","bread274","bread275","bread276","bread277","bread278","bread279","bread280","bread281","bread282","bread283","bread284","bread285","bread286","bread287","bread288","bread289","bread290","bread291","bread292","bread293","bread294","bread295","bread296","bread297","bread298","bread299","bread300"}
state_childsnack_p29.at_kitchen_content = {"content1","content2","content3","content4","content5",
                                      "content6","content7","content8","content9","content10","content11","content12","content13","content14","content15","content16","content17","content18","content19","content20","content21","content22","content23","content24","content25","content26","content27","content28","content29","content30","content31","content32","content33","content34","content35","content36","content37","content38","content39","content40","content41","content42","content43","content44","content45","content46","content47","content48","content49","content50","content51","content52","content53","content54","content55","content56","content57","content58","content59","content60","content61","content62","content63","content64","content65","content66","content67","content68","content69","content70","content71","content72","content73","content74","content75","content76","content77","content78","content79","content80","content81","content82","content83","content84","content85","content86","content87","content88","content89","content90","content91","content92","content93","content94","content95","content96","content97","content98","content99","content100","content101","content102","content103","content104","content105","content106","content107","content108","content109","content110","content111","content112","content113","content114","content115","content116","content117","content118","content119","content120","content121","content122","content123","content124","content125","content126","content127","content128","content129","content130","content131","content132","content133","content134","content135","content136","content137","content138","content139","content140","content141","content142","content143","content144","content145","content146","content147","content148","content149","content150","content151","content152","content153","content154","content155","content156","content157","content158","content159","content160","content161","content162","content163","content164","content165","content166","content167","content168","content169","content170","content171","content172","content173","content174","content175","content176","content177","content178","content179","content180","content181","content182","content183","content184","content185","content186","content187","content188","content189","content190","content191","content192","content193","content194","content195","content196","content197","content198","content199","content200","content201","content202","content203","content204","content205","content206","content207","content208","content209","content210","content211","content212","content213","content214","content215","content216","content217","content218","content219","content220","content221","content222","content223","content224","content225","content226","content227","content228","content229","content230","content231","content232","content233","content234","content235","content236","content237","content238","content239","content240","content241","content242","content243","content244","content245","content246","content247","content248","content249","content250","content251","content252","content253","content254","content255","content256","content257","content258","content259","content260","content261","content262","content263","content264","content265","content266","content267","content268","content269","content270","content271","content272","content273","content274","content275","content276","content277","content278","content279","content280","content281","content282","content283","content284","content285","content286","content287","content288","content289","content290","content291","content292","content293","content294","content295","content296","content297","content298","content299","content300"}
state_childsnack_p29.at_kitchen_sandwich = set()
state_childsnack_p29.not_allergic_gluten = {"child93","child44","child181","child141","child117","child122","child244","child56","child4","child63","child21","child170","child15","child263","child34","child152","child252","child70","child14","child166","child275","child300","child13","child214","child178","child31","child38","child47","child73","child167","child242","child299","child53","child265","child236","child82","child250","child220","child292","child88","child143","child288","child207","child278","child127","child17","child43","child168","child137","child16","child232","child274","child35","child107","child96","child253","child283","child230","child243","child257","child160","child29","child26","child20","child199","child100","child113","child119","child256","child161","child235","child191","child198","child115","child281","child37","child234","child126","child177","child9","child182","child240","child62","child132","child101","child24","child179","child110","child163","child188","child212","child124","child128","child296","child150","child248","child36","child71","child215","child133","child213","child184","child211","child146","child258","child280","child241","child25","child75","child164","child6","child267","child87","child287","child285","child268","child3","child65","child97","child109"}
state_childsnack_p29.notexist = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19","sandw20","sandw21","sandw22","sandw23","sandw24","sandw25","sandw26","sandw27","sandw28","sandw29","sandw30","sandw31","sandw32","sandw33","sandw34","sandw35","sandw36","sandw37","sandw38","sandw39","sandw40","sandw41","sandw42","sandw43","sandw44","sandw45","sandw46","sandw47","sandw48","sandw49","sandw50","sandw51","sandw52","sandw53","sandw54","sandw55","sandw56","sandw57","sandw58","sandw59","sandw60","sandw61","sandw62","sandw63","sandw64","sandw65","sandw66","sandw67","sandw68","sandw69","sandw70","sandw71","sandw72","sandw73","sandw74","sandw75","sandw76","sandw77","sandw78","sandw79","sandw80","sandw81","sandw82","sandw83","sandw84","sandw85","sandw86","sandw87","sandw88","sandw89","sandw90","sandw91","sandw92","sandw93","sandw94","sandw95","sandw96","sandw97","sandw98","sandw99","sandw100","sandw101","sandw102","sandw103","sandw104","sandw105","sandw106","sandw107","sandw108","sandw109","sandw110","sandw111","sandw112","sandw113","sandw114","sandw115","sandw116","sandw117","sandw118","sandw119","sandw120","sandw121","sandw122","sandw123","sandw124","sandw125","sandw126","sandw127","sandw128","sandw129","sandw130","sandw131","sandw132","sandw133","sandw134","sandw135","sandw136","sandw137","sandw138","sandw139","sandw140","sandw141","sandw142","sandw143","sandw144","sandw145","sandw146","sandw147","sandw148","sandw149","sandw150","sandw151","sandw152","sandw153","sandw154","sandw155","sandw156","sandw157","sandw158","sandw159","sandw160","sandw161","sandw162","sandw163","sandw164","sandw165","sandw166","sandw167","sandw168","sandw169","sandw170","sandw171","sandw172","sandw173","sandw174","sandw175","sandw176","sandw177","sandw178","sandw179","sandw180","sandw181","sandw182","sandw183","sandw184","sandw185","sandw186","sandw187","sandw188","sandw189","sandw190","sandw191","sandw192","sandw193","sandw194","sandw195","sandw196","sandw197","sandw198","sandw199","sandw200","sandw201","sandw202","sandw203","sandw204","sandw205","sandw206","sandw207","sandw208","sandw209","sandw210","sandw211","sandw212","sandw213","sandw214","sandw215","sandw216","sandw217","sandw218","sandw219","sandw220","sandw221","sandw222","sandw223","sandw224","sandw225","sandw226","sandw227","sandw228","sandw229","sandw230","sandw231","sandw232","sandw233","sandw234","sandw235","sandw236","sandw237","sandw238","sandw239","sandw240","sandw241","sandw242","sandw243","sandw244","sandw245","sandw246","sandw247","sandw248","sandw249","sandw250","sandw251","sandw252","sandw253","sandw254","sandw255","sandw256","sandw257","sandw258","sandw259","sandw260","sandw261","sandw262","sandw263","sandw264","sandw265","sandw266","sandw267","sandw268","sandw269","sandw270","sandw271","sandw272","sandw273","sandw274","sandw275","sandw276","sandw277","sandw278","sandw279","sandw280","sandw281","sandw282","sandw283","sandw284","sandw285","sandw286","sandw287","sandw288","sandw289","sandw290","sandw291","sandw292","sandw293","sandw294","sandw295","sandw296","sandw297","sandw298","sandw299","sandw300"}
state_childsnack_p29.no_gluten_bread = {"bread58","bread13","bread141","bread126","bread115","bread72","bread53","bread280","bread45","bread217","bread17","bread16","bread48","bread112","bread120","bread259","bread14","bread102","bread293","bread215","bread113","bread230","bread143","bread4","bread82","bread291","bread175","bread278","bread80","bread111","bread173","bread294","bread288","bread195","bread50","bread184","bread177","bread136","bread23","bread236","bread64","bread194","bread41","bread151","bread186","bread148","bread266","bread181","bread18","bread12","bread170","bread59","bread198","bread75","bread21","bread219","bread60","bread222","bread26","bread98","bread295","bread117","bread163","bread214","bread94","bread42","bread95","bread91","bread54","bread172","bread69","bread180","bread274","bread166","bread19","bread156","bread238","bread44","bread137","bread187","bread63","bread235","bread119","bread241","bread70","bread164","bread264","bread273","bread57","bread176","bread84","bread197","bread199","bread15","bread249","bread9","bread81","bread103","bread279","bread290","bread55","bread146","bread265","bread204","bread200","bread168","bread128","bread283","bread165","bread118","bread37","bread68","bread36","bread260","bread144","bread138","bread189","bread150","bread110","bread183","bread203","bread93","bread212","bread188","bread131","bread127","bread24","bread299","bread29","bread40","bread161","bread258","bread109","bread153","bread201","bread99","bread275","bread167","bread286","bread263","bread65","bread142","bread3","bread30","bread185","bread202","bread88","bread231","bread76","bread287","bread169","bread239","bread1","bread248","bread129","bread46","bread130","bread28","bread77","bread256","bread51","bread171","bread96","bread245","bread250","bread255","bread83","bread297","bread5","bread224","bread179","bread79","bread62","bread8","bread31","bread282","bread73","bread122","bread11","bread123"}
state_childsnack_p29.no_gluten_content = {"content249","content36","content273","content65","content66","content244","content282","content85","content136","content271","content217","content109","content277","content103","content160","content205","content192","content225","content265","content232","content62","content127","content116","content33","content174","content11","content118","content113","content4","content37","content31","content274","content35","content17","content170","content291","content264","content122","content143","content300","content110","content68","content243","content125","content258","content207","content105","content49","content25","content252","content169","content111","content91","content289","content106","content120","content222","content187","content14","content173","content168","content166","content26","content16","content104","content256","content87","content285","content221","content28","content64","content50","content253","content138","content115","content299","content247","content47","content72","content119","content230","content20","content114","content255","content141","content238","content13","content167","content139","content272","content24","content193","content61","content43","content254","content257","content124","content55","content287","content237","content290","content98","content1","content100","content259","content117","content74","content224","content179","content188","content262","content266","content184","content233","content40","content228","content76","content56","content15","content149","content212","content201","content81","content182","content214","content150","content123","content129","content292","content41","content177","content131","content21","content48","content18","content153","content239","content208","content236","content270","content146","content220","content181","content165","content275","content240","content108","content175","content145","content134","content178","content67","content53","content157","content280","content196","content102","content34","content77","content269","content147","content19","content3","content216","content215","content180","content203","content130","content152","content190","content90","content164","content63","content213","content294","content155","content57","content107","content70","content248"}
state_childsnack_p29.no_gluten_sandwich = set()
state_childsnack_p29.ontray = {}
state_childsnack_p29.served = {}
state_childsnack_p29.waiting = {"child1":"table1","child2":"table3","child3":"table1","child4":"table2",
                           "child5":"table3","child6":"table3","child7":"table3","child8":"table3",
                           "child9":"table2","child10":"table1","child11":"table1","child12":"table3","child13":"table2","child14":"table1","child15":"table1","child16":"table1","child17":"table1","child18":"table1","child19":"table1","child20":"table2","child21":"table3","child22":"table1","child23":"table2","child24":"table2","child25":"table3","child26":"table3","child27":"table1","child28":"table3","child29":"table3","child30":"table2","child31":"table2","child32":"table2","child33":"table1","child34":"table1","child35":"table3","child36":"table3","child37":"table1","child38":"table1","child39":"table2","child40":"table1","child41":"table1","child42":"table3","child43":"table3","child44":"table2","child45":"table1","child46":"table3","child47":"table1","child48":"table1","child49":"table2","child50":"table1","child51":"table2","child52":"table3","child53":"table3","child54":"table3","child55":"table3","child56":"table2","child57":"table2","child58":"table3","child59":"table3","child60":"table3","child61":"table2","child62":"table3","child63":"table2","child64":"table1","child65":"table3","child66":"table2","child67":"table2","child68":"table2","child69":"table1","child70":"table3","child71":"table2","child72":"table3","child73":"table2","child74":"table3","child75":"table1","child76":"table2","child77":"table2","child78":"table1","child79":"table3","child80":"table2","child81":"table1","child82":"table2","child83":"table2","child84":"table2","child85":"table3","child86":"table1","child87":"table1","child88":"table1","child89":"table1","child90":"table2","child91":"table3","child92":"table1","child93":"table3","child94":"table1","child95":"table1","child96":"table2","child97":"table2","child98":"table2","child99":"table3","child100":"table2","child101":"table2","child102":"table1","child103":"table1","child104":"table2","child105":"table2","child106":"table3","child107":"table3","child108":"table1","child109":"table3","child110":"table2","child111":"table2","child112":"table1","child113":"table2","child114":"table2","child115":"table2","child116":"table2","child117":"table3","child118":"table3","child119":"table3","child120":"table3","child121":"table3","child122":"table1","child123":"table2","child124":"table1","child125":"table2","child126":"table2","child127":"table2","child128":"table1","child129":"table2","child130":"table2","child131":"table3","child132":"table3","child133":"table2","child134":"table3","child135":"table1","child136":"table2","child137":"table1","child138":"table3","child139":"table3","child140":"table1","child141":"table2","child142":"table3","child143":"table3","child144":"table3","child145":"table1","child146":"table1","child147":"table3","child148":"table2","child149":"table1","child150":"table2","child151":"table1","child152":"table1","child153":"table2","child154":"table2","child155":"table2","child156":"table1","child157":"table2","child158":"table2","child159":"table2","child160":"table2","child161":"table2","child162":"table2","child163":"table2","child164":"table1","child165":"table2","child166":"table1","child167":"table3","child168":"table3","child169":"table1","child170":"table2","child171":"table1","child172":"table3","child173":"table1","child174":"table3","child175":"table1","child176":"table1","child177":"table1","child178":"table1","child179":"table1","child180":"table3","child181":"table1","child182":"table1","child183":"table1","child184":"table2","child185":"table3","child186":"table1","child187":"table3","child188":"table1","child189":"table2","child190":"table3","child191":"table2","child192":"table2","child193":"table1","child194":"table3","child195":"table3","child196":"table3","child197":"table3","child198":"table1","child199":"table1","child200":"table2","child201":"table1","child202":"table3","child203":"table1","child204":"table2","child205":"table3","child206":"table3","child207":"table2","child208":"table2","child209":"table3","child210":"table1","child211":"table1","child212":"table3","child213":"table3","child214":"table3","child215":"table1","child216":"table1","child217":"table3","child218":"table2","child219":"table3","child220":"table3","child221":"table1","child222":"table3","child223":"table1","child224":"table2","child225":"table3","child226":"table2","child227":"table3","child228":"table2","child229":"table1","child230":"table3","child231":"table3","child232":"table2","child233":"table1","child234":"table2","child235":"table2","child236":"table1","child237":"table2","child238":"table2","child239":"table3","child240":"table2","child241":"table3","child242":"table1","child243":"table2","child244":"table1","child245":"table3","child246":"table3","child247":"table3","child248":"table2","child249":"table3","child250":"table3","child251":"table2","child252":"table2","child253":"table2","child254":"table3","child255":"table3","child256":"table2","child257":"table2","child258":"table1","child259":"table1","child260":"table2","child261":"table2","child262":"table1","child263":"table2","child264":"table3","child265":"table3","child266":"table3","child267":"table2","child268":"table2","child269":"table1","child270":"table2","child271":"table2","child272":"table1","child273":"table2","child274":"table1","child275":"table2","child276":"table2","child277":"table2","child278":"table2","child279":"table3","child280":"table3","child281":"table2","child282":"table3","child283":"table1","child284":"table3","child285":"table1","child286":"table1","child287":"table1","child288":"table3","child289":"table2","child290":"table2","child291":"table3","child292":"table1","child293":"table3","child294":"table2","child295":"table3","child296":"table3","child297":"table2","child298":"table2","child299":"table1","child300":"table1"}

# Set goal from the :htn :ordered-subtasks in p29.hddl
htn_ordered_subtask_childsnack_p29 = Multigoal("goal_childsnack_p29",served=state_childsnack_p29.waiting)

# Set goal state from p29.hddl
# 	(:goal (and
# (served child1)
# (served child2)
# (served child3)
# (served child4)
# (served child5)
# (served child6)
# (served child7)
# (served child8)
# (served child9)
# (served child10)
# (served child11)
# (served child12)
# (served child13)
# (served child14)
# (served child15)
# (served child16)
# (served child17)
# (served child18)
# (served child19)
# (served child20)
# (served child21)
# (served child22)
# (served child23)
# (served child24)
# (served child25)
# (served child26)
# (served child27)
# (served child28)
# (served child29)
# (served child30)
# (served child31)
# (served child32)
# (served child33)
# (served child34)
# (served child35)
# (served child36)
# (served child37)
# (served child38)
# (served child39)
# (served child40)
# (served child41)
# (served child42)
# (served child43)
# (served child44)
# (served child45)
# (served child46)
# (served child47)
# (served child48)
# (served child49)
# (served child50)
# (served child51)
# (served child52)
# (served child53)
# (served child54)
# (served child55)
# (served child56)
# (served child57)
# (served child58)
# (served child59)
# (served child60)
# (served child61)
# (served child62)
# (served child63)
# (served child64)
# (served child65)
# (served child66)
# (served child67)
# (served child68)
# (served child69)
# (served child70)
# (served child71)
# (served child72)
# (served child73)
# (served child74)
# (served child75)
# (served child76)
# (served child77)
# (served child78)
# (served child79)
# (served child80)
# (served child81)
# (served child82)
# (served child83)
# (served child84)
# (served child85)
# (served child86)
# (served child87)
# (served child88)
# (served child89)
# (served child90)
# (served child91)
# (served child92)
# (served child93)
# (served child94)
# (served child95)
# (served child96)
# (served child97)
# (served child98)
# (served child99)
# (served child100)
# (served child101)
# (served child102)
# (served child103)
# (served child104)
# (served child105)
# (served child106)
# (served child107)
# (served child108)
# (served child109)
# (served child110)
# (served child111)
# (served child112)
# (served child113)
# (served child114)
# (served child115)
# (served child116)
# (served child117)
# (served child118)
# (served child119)
# (served child120)
# (served child121)
# (served child122)
# (served child123)
# (served child124)
# (served child125)
# (served child126)
# (served child127)
# (served child128)
# (served child129)
# (served child130)
# (served child131)
# (served child132)
# (served child133)
# (served child134)
# (served child135)
# (served child136)
# (served child137)
# (served child138)
# (served child139)
# (served child140)
# (served child141)
# (served child142)
# (served child143)
# (served child144)
# (served child145)
# (served child146)
# (served child147)
# (served child148)
# (served child149)
# (served child150)
# (served child151)
# (served child152)
# (served child153)
# (served child154)
# (served child155)
# (served child156)
# (served child157)
# (served child158)
# (served child159)
# (served child160)
# (served child161)
# (served child162)
# (served child163)
# (served child164)
# (served child165)
# (served child166)
# (served child167)
# (served child168)
# (served child169)
# (served child170)
# (served child171)
# (served child172)
# (served child173)
# (served child174)
# (served child175)
# (served child176)
# (served child177)
# (served child178)
# (served child179)
# (served child180)
# (served child181)
# (served child182)
# (served child183)
# (served child184)
# (served child185)
# (served child186)
# (served child187)
# (served child188)
# (served child189)
# (served child190)
# (served child191)
# (served child192)
# (served child193)
# (served child194)
# (served child195)
# (served child196)
# (served child197)
# (served child198)
# (served child199)
# (served child200)
# (served child201)
# (served child202)
# (served child203)
# (served child204)
# (served child205)
# (served child206)
# (served child207)
# (served child208)
# (served child209)
# (served child210)
# (served child211)
# (served child212)
# (served child213)
# (served child214)
# (served child215)
# (served child216)
# (served child217)
# (served child218)
# (served child219)
# (served child220)
# (served child221)
# (served child222)
# (served child223)
# (served child224)
# (served child225)
# (served child226)
# (served child227)
# (served child228)
# (served child229)
# (served child230)
# (served child231)
# (served child232)
# (served child233)
# (served child234)
# (served child235)
# (served child236)
# (served child237)
# (served child238)
# (served child239)
# (served child240)
# (served child241)
# (served child242)
# (served child243)
# (served child244)
# (served child245)
# (served child246)
# (served child247)
# (served child248)
# (served child249)
# (served child250)
# (served child251)
# (served child252)
# (served child253)
# (served child254)
# (served child255)
# (served child256)
# (served child257)
# (served child258)
# (served child259)
# (served child260)
# (served child261)
# (served child262)
# (served child263)
# (served child264)
# (served child265)
# (served child266)
# (served child267)
# (served child268)
# (served child269)
# (served child270)
# (served child271)
# (served child272)
# (served child273)
# (served child274)
# (served child275)
# (served child276)
# (served child277)
# (served child278)
# (served child279)
# (served child280)
# (served child281)
# (served child282)
# (served child283)
# (served child284)
# (served child285)
# (served child286)
# (served child287)
# (served child288)
# (served child289)
# (served child290)
# (served child291)
# (served child292)
# (served child293)
# (served child294)
# (served child295)
# (served child296)
# (served child297)
# (served child298)
# (served child299)
# (served child300)
# 	))
goal_childsnack_p29 = state_childsnack_p29.waiting

# ===== prob-snack --------------------------------------------------- p30.hddl
state_childsnack_p30 = State("snack_p30_initial_state")

# types:
state_childsnack_p30.bread_portions = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7","bread8","bread9","bread10","bread11","bread12","bread13","bread14","bread15","bread16","bread17","bread18","bread19","bread20","bread21","bread22","bread23","bread24","bread25","bread26","bread27","bread28","bread29","bread30","bread31","bread32","bread33","bread34","bread35","bread36","bread37","bread38","bread39","bread40","bread41","bread42","bread43","bread44","bread45","bread46","bread47","bread48","bread49","bread50","bread51","bread52","bread53","bread54","bread55","bread56","bread57","bread58","bread59","bread60","bread61","bread62","bread63","bread64","bread65","bread66","bread67","bread68","bread69","bread70","bread71","bread72","bread73","bread74","bread75","bread76","bread77","bread78","bread79","bread80","bread81","bread82","bread83","bread84","bread85","bread86","bread87","bread88","bread89","bread90","bread91","bread92","bread93","bread94","bread95","bread96","bread97","bread98","bread99","bread100","bread101","bread102","bread103","bread104","bread105","bread106","bread107","bread108","bread109","bread110","bread111","bread112","bread113","bread114","bread115","bread116","bread117","bread118","bread119","bread120","bread121","bread122","bread123","bread124","bread125","bread126","bread127","bread128","bread129","bread130","bread131","bread132","bread133","bread134","bread135","bread136","bread137","bread138","bread139","bread140","bread141","bread142","bread143","bread144","bread145","bread146","bread147","bread148","bread149","bread150","bread151","bread152","bread153","bread154","bread155","bread156","bread157","bread158","bread159","bread160","bread161","bread162","bread163","bread164","bread165","bread166","bread167","bread168","bread169","bread170","bread171","bread172","bread173","bread174","bread175","bread176","bread177","bread178","bread179","bread180","bread181","bread182","bread183","bread184","bread185","bread186","bread187","bread188","bread189","bread190","bread191","bread192","bread193","bread194","bread195","bread196","bread197","bread198","bread199","bread200","bread201","bread202","bread203","bread204","bread205","bread206","bread207","bread208","bread209","bread210","bread211","bread212","bread213","bread214","bread215","bread216","bread217","bread218","bread219","bread220","bread221","bread222","bread223","bread224","bread225","bread226","bread227","bread228","bread229","bread230","bread231","bread232","bread233","bread234","bread235","bread236","bread237","bread238","bread239","bread240","bread241","bread242","bread243","bread244","bread245","bread246","bread247","bread248","bread249","bread250","bread251","bread252","bread253","bread254","bread255","bread256","bread257","bread258","bread259","bread260","bread261","bread262","bread263","bread264","bread265","bread266","bread267","bread268","bread269","bread270","bread271","bread272","bread273","bread274","bread275","bread276","bread277","bread278","bread279","bread280","bread281","bread282","bread283","bread284","bread285","bread286","bread287","bread288","bread289","bread290","bread291","bread292","bread293","bread294","bread295","bread296","bread297","bread298","bread299","bread300","bread301","bread302","bread303","bread304","bread305","bread306","bread307","bread308","bread309","bread310","bread311","bread312","bread313","bread314","bread315","bread316","bread317","bread318","bread319","bread320","bread321","bread322","bread323","bread324","bread325","bread326","bread327","bread328","bread329","bread330","bread331","bread332","bread333","bread334","bread335","bread336","bread337","bread338","bread339","bread340","bread341","bread342","bread343","bread344","bread345","bread346","bread347","bread348","bread349","bread350","bread351","bread352","bread353","bread354","bread355","bread356","bread357","bread358","bread359","bread360","bread361","bread362","bread363","bread364","bread365","bread366","bread367","bread368","bread369","bread370","bread371","bread372","bread373","bread374","bread375","bread376","bread377","bread378","bread379","bread380","bread381","bread382","bread383","bread384","bread385","bread386","bread387","bread388","bread389","bread390","bread391","bread392","bread393","bread394","bread395","bread396","bread397","bread398","bread399","bread400","bread401","bread402","bread403","bread404","bread405","bread406","bread407","bread408","bread409","bread410","bread411","bread412","bread413","bread414","bread415","bread416","bread417","bread418","bread419","bread420","bread421","bread422","bread423","bread424","bread425","bread426","bread427","bread428","bread429","bread430","bread431","bread432","bread433","bread434","bread435","bread436","bread437","bread438","bread439","bread440","bread441","bread442","bread443","bread444","bread445","bread446","bread447","bread448","bread449","bread450","bread451","bread452","bread453","bread454","bread455","bread456","bread457","bread458","bread459","bread460","bread461","bread462","bread463","bread464","bread465","bread466","bread467","bread468","bread469","bread470","bread471","bread472","bread473","bread474","bread475","bread476","bread477","bread478","bread479","bread480","bread481","bread482","bread483","bread484","bread485","bread486","bread487","bread488","bread489","bread490","bread491","bread492","bread493","bread494","bread495","bread496","bread497","bread498","bread499","bread500"}
state_childsnack_p30.children = {"child1","child2","child3","child4","child5","child6","child7","child8","child9","child10","child11","child12","child13","child14","child15","child16","child17","child18","child19","child20","child21","child22","child23","child24","child25","child26","child27","child28","child29","child30","child31","child32","child33","child34","child35","child36","child37","child38","child39","child40","child41","child42","child43","child44","child45","child46","child47","child48","child49","child50","child51","child52","child53","child54","child55","child56","child57","child58","child59","child60","child61","child62","child63","child64","child65","child66","child67","child68","child69","child70","child71","child72","child73","child74","child75","child76","child77","child78","child79","child80","child81","child82","child83","child84","child85","child86","child87","child88","child89","child90","child91","child92","child93","child94","child95","child96","child97","child98","child99","child100","child101","child102","child103","child104","child105","child106","child107","child108","child109","child110","child111","child112","child113","child114","child115","child116","child117","child118","child119","child120","child121","child122","child123","child124","child125","child126","child127","child128","child129","child130","child131","child132","child133","child134","child135","child136","child137","child138","child139","child140","child141","child142","child143","child144","child145","child146","child147","child148","child149","child150","child151","child152","child153","child154","child155","child156","child157","child158","child159","child160","child161","child162","child163","child164","child165","child166","child167","child168","child169","child170","child171","child172","child173","child174","child175","child176","child177","child178","child179","child180","child181","child182","child183","child184","child185","child186","child187","child188","child189","child190","child191","child192","child193","child194","child195","child196","child197","child198","child199","child200","child201","child202","child203","child204","child205","child206","child207","child208","child209","child210","child211","child212","child213","child214","child215","child216","child217","child218","child219","child220","child221","child222","child223","child224","child225","child226","child227","child228","child229","child230","child231","child232","child233","child234","child235","child236","child237","child238","child239","child240","child241","child242","child243","child244","child245","child246","child247","child248","child249","child250","child251","child252","child253","child254","child255","child256","child257","child258","child259","child260","child261","child262","child263","child264","child265","child266","child267","child268","child269","child270","child271","child272","child273","child274","child275","child276","child277","child278","child279","child280","child281","child282","child283","child284","child285","child286","child287","child288","child289","child290","child291","child292","child293","child294","child295","child296","child297","child298","child299","child300","child301","child302","child303","child304","child305","child306","child307","child308","child309","child310","child311","child312","child313","child314","child315","child316","child317","child318","child319","child320","child321","child322","child323","child324","child325","child326","child327","child328","child329","child330","child331","child332","child333","child334","child335","child336","child337","child338","child339","child340","child341","child342","child343","child344","child345","child346","child347","child348","child349","child350","child351","child352","child353","child354","child355","child356","child357","child358","child359","child360","child361","child362","child363","child364","child365","child366","child367","child368","child369","child370","child371","child372","child373","child374","child375","child376","child377","child378","child379","child380","child381","child382","child383","child384","child385","child386","child387","child388","child389","child390","child391","child392","child393","child394","child395","child396","child397","child398","child399","child400","child401","child402","child403","child404","child405","child406","child407","child408","child409","child410","child411","child412","child413","child414","child415","child416","child417","child418","child419","child420","child421","child422","child423","child424","child425","child426","child427","child428","child429","child430","child431","child432","child433","child434","child435","child436","child437","child438","child439","child440","child441","child442","child443","child444","child445","child446","child447","child448","child449","child450","child451","child452","child453","child454","child455","child456","child457","child458","child459","child460","child461","child462","child463","child464","child465","child466","child467","child468","child469","child470","child471","child472","child473","child474","child475","child476","child477","child478","child479","child480","child481","child482","child483","child484","child485","child486","child487","child488","child489","child490","child491","child492","child493","child494","child495","child496","child497","child498","child499","child500"}
state_childsnack_p30.content_portions = {"content1","content2","content3","content4","content5","content6","content7","content8","content9","content10","content11","content12","content13","content14","content15","content16","content17","content18","content19","content20","content21","content22","content23","content24","content25","content26","content27","content28","content29","content30","content31","content32","content33","content34","content35","content36","content37","content38","content39","content40","content41","content42","content43","content44","content45","content46","content47","content48","content49","content50","content51","content52","content53","content54","content55","content56","content57","content58","content59","content60","content61","content62","content63","content64","content65","content66","content67","content68","content69","content70","content71","content72","content73","content74","content75","content76","content77","content78","content79","content80","content81","content82","content83","content84","content85","content86","content87","content88","content89","content90","content91","content92","content93","content94","content95","content96","content97","content98","content99","content100","content101","content102","content103","content104","content105","content106","content107","content108","content109","content110","content111","content112","content113","content114","content115","content116","content117","content118","content119","content120","content121","content122","content123","content124","content125","content126","content127","content128","content129","content130","content131","content132","content133","content134","content135","content136","content137","content138","content139","content140","content141","content142","content143","content144","content145","content146","content147","content148","content149","content150","content151","content152","content153","content154","content155","content156","content157","content158","content159","content160","content161","content162","content163","content164","content165","content166","content167","content168","content169","content170","content171","content172","content173","content174","content175","content176","content177","content178","content179","content180","content181","content182","content183","content184","content185","content186","content187","content188","content189","content190","content191","content192","content193","content194","content195","content196","content197","content198","content199","content200","content201","content202","content203","content204","content205","content206","content207","content208","content209","content210","content211","content212","content213","content214","content215","content216","content217","content218","content219","content220","content221","content222","content223","content224","content225","content226","content227","content228","content229","content230","content231","content232","content233","content234","content235","content236","content237","content238","content239","content240","content241","content242","content243","content244","content245","content246","content247","content248","content249","content250","content251","content252","content253","content254","content255","content256","content257","content258","content259","content260","content261","content262","content263","content264","content265","content266","content267","content268","content269","content270","content271","content272","content273","content274","content275","content276","content277","content278","content279","content280","content281","content282","content283","content284","content285","content286","content287","content288","content289","content290","content291","content292","content293","content294","content295","content296","content297","content298","content299","content300","content301","content302","content303","content304","content305","content306","content307","content308","content309","content310","content311","content312","content313","content314","content315","content316","content317","content318","content319","content320","content321","content322","content323","content324","content325","content326","content327","content328","content329","content330","content331","content332","content333","content334","content335","content336","content337","content338","content339","content340","content341","content342","content343","content344","content345","content346","content347","content348","content349","content350","content351","content352","content353","content354","content355","content356","content357","content358","content359","content360","content361","content362","content363","content364","content365","content366","content367","content368","content369","content370","content371","content372","content373","content374","content375","content376","content377","content378","content379","content380","content381","content382","content383","content384","content385","content386","content387","content388","content389","content390","content391","content392","content393","content394","content395","content396","content397","content398","content399","content400","content401","content402","content403","content404","content405","content406","content407","content408","content409","content410","content411","content412","content413","content414","content415","content416","content417","content418","content419","content420","content421","content422","content423","content424","content425","content426","content427","content428","content429","content430","content431","content432","content433","content434","content435","content436","content437","content438","content439","content440","content441","content442","content443","content444","content445","content446","content447","content448","content449","content450","content451","content452","content453","content454","content455","content456","content457","content458","content459","content460","content461","content462","content463","content464","content465","content466","content467","content468","content469","content470","content471","content472","content473","content474","content475","content476","content477","content478","content479","content480","content481","content482","content483","content484","content485","content486","content487","content488","content489","content490","content491","content492","content493","content494","content495","content496","content497","content498","content499","content500"}
state_childsnack_p30.places = {"table1","table2","table3"}
state_childsnack_p30.sandwiches = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19","sandw20","sandw21","sandw22","sandw23","sandw24","sandw25","sandw26","sandw27","sandw28","sandw29","sandw30","sandw31","sandw32","sandw33","sandw34","sandw35","sandw36","sandw37","sandw38","sandw39","sandw40","sandw41","sandw42","sandw43","sandw44","sandw45","sandw46","sandw47","sandw48","sandw49","sandw50","sandw51","sandw52","sandw53","sandw54","sandw55","sandw56","sandw57","sandw58","sandw59","sandw60","sandw61","sandw62","sandw63","sandw64","sandw65","sandw66","sandw67","sandw68","sandw69","sandw70","sandw71","sandw72","sandw73","sandw74","sandw75","sandw76","sandw77","sandw78","sandw79","sandw80","sandw81","sandw82","sandw83","sandw84","sandw85","sandw86","sandw87","sandw88","sandw89","sandw90","sandw91","sandw92","sandw93","sandw94","sandw95","sandw96","sandw97","sandw98","sandw99","sandw100","sandw101","sandw102","sandw103","sandw104","sandw105","sandw106","sandw107","sandw108","sandw109","sandw110","sandw111","sandw112","sandw113","sandw114","sandw115","sandw116","sandw117","sandw118","sandw119","sandw120","sandw121","sandw122","sandw123","sandw124","sandw125","sandw126","sandw127","sandw128","sandw129","sandw130","sandw131","sandw132","sandw133","sandw134","sandw135","sandw136","sandw137","sandw138","sandw139","sandw140","sandw141","sandw142","sandw143","sandw144","sandw145","sandw146","sandw147","sandw148","sandw149","sandw150","sandw151","sandw152","sandw153","sandw154","sandw155","sandw156","sandw157","sandw158","sandw159","sandw160","sandw161","sandw162","sandw163","sandw164","sandw165","sandw166","sandw167","sandw168","sandw169","sandw170","sandw171","sandw172","sandw173","sandw174","sandw175","sandw176","sandw177","sandw178","sandw179","sandw180","sandw181","sandw182","sandw183","sandw184","sandw185","sandw186","sandw187","sandw188","sandw189","sandw190","sandw191","sandw192","sandw193","sandw194","sandw195","sandw196","sandw197","sandw198","sandw199","sandw200","sandw201","sandw202","sandw203","sandw204","sandw205","sandw206","sandw207","sandw208","sandw209","sandw210","sandw211","sandw212","sandw213","sandw214","sandw215","sandw216","sandw217","sandw218","sandw219","sandw220","sandw221","sandw222","sandw223","sandw224","sandw225","sandw226","sandw227","sandw228","sandw229","sandw230","sandw231","sandw232","sandw233","sandw234","sandw235","sandw236","sandw237","sandw238","sandw239","sandw240","sandw241","sandw242","sandw243","sandw244","sandw245","sandw246","sandw247","sandw248","sandw249","sandw250","sandw251","sandw252","sandw253","sandw254","sandw255","sandw256","sandw257","sandw258","sandw259","sandw260","sandw261","sandw262","sandw263","sandw264","sandw265","sandw266","sandw267","sandw268","sandw269","sandw270","sandw271","sandw272","sandw273","sandw274","sandw275","sandw276","sandw277","sandw278","sandw279","sandw280","sandw281","sandw282","sandw283","sandw284","sandw285","sandw286","sandw287","sandw288","sandw289","sandw290","sandw291","sandw292","sandw293","sandw294","sandw295","sandw296","sandw297","sandw298","sandw299","sandw300","sandw301","sandw302","sandw303","sandw304","sandw305","sandw306","sandw307","sandw308","sandw309","sandw310","sandw311","sandw312","sandw313","sandw314","sandw315","sandw316","sandw317","sandw318","sandw319","sandw320","sandw321","sandw322","sandw323","sandw324","sandw325","sandw326","sandw327","sandw328","sandw329","sandw330","sandw331","sandw332","sandw333","sandw334","sandw335","sandw336","sandw337","sandw338","sandw339","sandw340","sandw341","sandw342","sandw343","sandw344","sandw345","sandw346","sandw347","sandw348","sandw349","sandw350","sandw351","sandw352","sandw353","sandw354","sandw355","sandw356","sandw357","sandw358","sandw359","sandw360","sandw361","sandw362","sandw363","sandw364","sandw365","sandw366","sandw367","sandw368","sandw369","sandw370","sandw371","sandw372","sandw373","sandw374","sandw375","sandw376","sandw377","sandw378","sandw379","sandw380","sandw381","sandw382","sandw383","sandw384","sandw385","sandw386","sandw387","sandw388","sandw389","sandw390","sandw391","sandw392","sandw393","sandw394","sandw395","sandw396","sandw397","sandw398","sandw399","sandw400","sandw401","sandw402","sandw403","sandw404","sandw405","sandw406","sandw407","sandw408","sandw409","sandw410","sandw411","sandw412","sandw413","sandw414","sandw415","sandw416","sandw417","sandw418","sandw419","sandw420","sandw421","sandw422","sandw423","sandw424","sandw425","sandw426","sandw427","sandw428","sandw429","sandw430","sandw431","sandw432","sandw433","sandw434","sandw435","sandw436","sandw437","sandw438","sandw439","sandw440","sandw441","sandw442","sandw443","sandw444","sandw445","sandw446","sandw447","sandw448","sandw449","sandw450","sandw451","sandw452","sandw453","sandw454","sandw455","sandw456","sandw457","sandw458","sandw459","sandw460","sandw461","sandw462","sandw463","sandw464","sandw465","sandw466","sandw467","sandw468","sandw469","sandw470","sandw471","sandw472","sandw473","sandw474","sandw475","sandw476","sandw477","sandw478","sandw479","sandw480","sandw481","sandw482","sandw483","sandw484","sandw485","sandw486","sandw487","sandw488","sandw489","sandw490","sandw491","sandw492","sandw493","sandw494","sandw495","sandw496","sandw497","sandw498","sandw499","sandw500"}
state_childsnack_p30.trays = {"tray1","tray2","tray3","tray4","tray5","tray6","tray7","tray8","tray9","tray10","tray11","tray12","tray13","tray14","tray15","tray16","tray17","tray18","tray19","tray20","tray21","tray22","tray23","tray24","tray25","tray26","tray27","tray28","tray29","tray30"}

# predicates:
state_childsnack_p30.allergic_gluten = {"child366","child402","child393","child466","child484","child374","child391","child323","child320","child468","child380","child390","child21","child236","child89","child327","child249","child227","child354","child469","child79","child472","child181","child494","child254","child300","child222","child495","child223","child112","child72","child250","child147","child185","child287","child15","child63","child103","child130","child110","child16","child155","child178","child352","child170","child285","child461","child115","child251","child364","child487","child449","child164","child403","child5","child218","child123","child359","child138","child122","child215","child33","child88","child197","child245","child125","child104","child43","child435","child82","child475","child240","child498","child499","child304","child368","child238","child422","child10","child312","child477","child309","child153","child3","child40","child342","child280","child330","child428","child247","child102","child395","child134","child266","child172","child295","child243","child22","child376","child394","child289","child160","child262","child84","child460","child437","child326","child459","child272","child479","child53","child423","child55","child175","child497","child177","child163","child353","child464","child32","child180","child86","child429","child186","child166","child244","child195","child202","child252","child297","child132","child224","child268","child424","child126","child191","child76","child71","child133","child397","child419","child267","child409","child66","child105","child116","child337","child481","child70","child233","child358","child203","child381","child486","child100","child314","child229","child69","child278","child411","child493","child365","child306","child208","child467","child42","child109","child370","child430","child264","child259","child142","child478","child113","child78","child189","child62","child91","child292","child420","child274","child231","child441","child59","child386","child14","child140","child216","child67","child219","child213","child47","child488","child296","child384","child328","child418","child24","child362","child190","child348","child340","child95","child450","child49","child413","child385","child377","child204","child319","child293","child27","child57","child286","child173","child431","child127","child335","child291","child471","child168","child242","child121","child378","child470","child426","child356","child139","child209","child45","child410","child239","child220","child119","child149","child183","child455","child241","child141","child463","child248","child234","child281","child85","child313","child26","child305","child143","child427","child341","child336","child237","child273","child128","child290","child38","child226","child94","child7","child482","child343","child167","child106","child473","child117","child193","child260","child277","child65","child39","child347","child338","child454","child56","child433","child476","child369","child387","child480","child349","child412","child416","child13","child321","child4","child276","child205","child399","child458","child357","child388","child36","child444","child200","child436","child408","child11","child453","child315","child136"}
state_childsnack_p30.at = {"tray1":"kitchen","tray2":"kitchen","tray3":"kitchen","tray4":"kitchen","tray5":"kitchen","tray6":"kitchen","tray7":"kitchen","tray8":"kitchen","tray9":"kitchen","tray10":"kitchen","tray11":"kitchen","tray12":"kitchen","tray13":"kitchen","tray14":"kitchen","tray15":"kitchen","tray16":"kitchen","tray17":"kitchen","tray18":"kitchen","tray19":"kitchen","tray20":"kitchen","tray21":"kitchen","tray22":"kitchen","tray23":"kitchen","tray24":"kitchen","tray25":"kitchen","tray26":"kitchen","tray27":"kitchen","tray28":"kitchen","tray29":"kitchen","tray30":"kitchen"}
state_childsnack_p30.at_kitchen_bread = {"bread1","bread2","bread3","bread4","bread5","bread6","bread7",
                                    "bread8","bread9","bread10","bread11","bread12","bread13","bread14","bread15","bread16","bread17","bread18","bread19","bread20","bread21","bread22","bread23","bread24","bread25","bread26","bread27","bread28","bread29","bread30","bread31","bread32","bread33","bread34","bread35","bread36","bread37","bread38","bread39","bread40","bread41","bread42","bread43","bread44","bread45","bread46","bread47","bread48","bread49","bread50","bread51","bread52","bread53","bread54","bread55","bread56","bread57","bread58","bread59","bread60","bread61","bread62","bread63","bread64","bread65","bread66","bread67","bread68","bread69","bread70","bread71","bread72","bread73","bread74","bread75","bread76","bread77","bread78","bread79","bread80","bread81","bread82","bread83","bread84","bread85","bread86","bread87","bread88","bread89","bread90","bread91","bread92","bread93","bread94","bread95","bread96","bread97","bread98","bread99","bread100","bread101","bread102","bread103","bread104","bread105","bread106","bread107","bread108","bread109","bread110","bread111","bread112","bread113","bread114","bread115","bread116","bread117","bread118","bread119","bread120","bread121","bread122","bread123","bread124","bread125","bread126","bread127","bread128","bread129","bread130","bread131","bread132","bread133","bread134","bread135","bread136","bread137","bread138","bread139","bread140","bread141","bread142","bread143","bread144","bread145","bread146","bread147","bread148","bread149","bread150","bread151","bread152","bread153","bread154","bread155","bread156","bread157","bread158","bread159","bread160","bread161","bread162","bread163","bread164","bread165","bread166","bread167","bread168","bread169","bread170","bread171","bread172","bread173","bread174","bread175","bread176","bread177","bread178","bread179","bread180","bread181","bread182","bread183","bread184","bread185","bread186","bread187","bread188","bread189","bread190","bread191","bread192","bread193","bread194","bread195","bread196","bread197","bread198","bread199","bread200","bread201","bread202","bread203","bread204","bread205","bread206","bread207","bread208","bread209","bread210","bread211","bread212","bread213","bread214","bread215","bread216","bread217","bread218","bread219","bread220","bread221","bread222","bread223","bread224","bread225","bread226","bread227","bread228","bread229","bread230","bread231","bread232","bread233","bread234","bread235","bread236","bread237","bread238","bread239","bread240","bread241","bread242","bread243","bread244","bread245","bread246","bread247","bread248","bread249","bread250","bread251","bread252","bread253","bread254","bread255","bread256","bread257","bread258","bread259","bread260","bread261","bread262","bread263","bread264","bread265","bread266","bread267","bread268","bread269","bread270","bread271","bread272","bread273","bread274","bread275","bread276","bread277","bread278","bread279","bread280","bread281","bread282","bread283","bread284","bread285","bread286","bread287","bread288","bread289","bread290","bread291","bread292","bread293","bread294","bread295","bread296","bread297","bread298","bread299","bread300","bread301","bread302","bread303","bread304","bread305","bread306","bread307","bread308","bread309","bread310","bread311","bread312","bread313","bread314","bread315","bread316","bread317","bread318","bread319","bread320","bread321","bread322","bread323","bread324","bread325","bread326","bread327","bread328","bread329","bread330","bread331","bread332","bread333","bread334","bread335","bread336","bread337","bread338","bread339","bread340","bread341","bread342","bread343","bread344","bread345","bread346","bread347","bread348","bread349","bread350","bread351","bread352","bread353","bread354","bread355","bread356","bread357","bread358","bread359","bread360","bread361","bread362","bread363","bread364","bread365","bread366","bread367","bread368","bread369","bread370","bread371","bread372","bread373","bread374","bread375","bread376","bread377","bread378","bread379","bread380","bread381","bread382","bread383","bread384","bread385","bread386","bread387","bread388","bread389","bread390","bread391","bread392","bread393","bread394","bread395","bread396","bread397","bread398","bread399","bread400","bread401","bread402","bread403","bread404","bread405","bread406","bread407","bread408","bread409","bread410","bread411","bread412","bread413","bread414","bread415","bread416","bread417","bread418","bread419","bread420","bread421","bread422","bread423","bread424","bread425","bread426","bread427","bread428","bread429","bread430","bread431","bread432","bread433","bread434","bread435","bread436","bread437","bread438","bread439","bread440","bread441","bread442","bread443","bread444","bread445","bread446","bread447","bread448","bread449","bread450","bread451","bread452","bread453","bread454","bread455","bread456","bread457","bread458","bread459","bread460","bread461","bread462","bread463","bread464","bread465","bread466","bread467","bread468","bread469","bread470","bread471","bread472","bread473","bread474","bread475","bread476","bread477","bread478","bread479","bread480","bread481","bread482","bread483","bread484","bread485","bread486","bread487","bread488","bread489","bread490","bread491","bread492","bread493","bread494","bread495","bread496","bread497","bread498","bread499","bread500"}
state_childsnack_p30.at_kitchen_content = {"content1","content2","content3","content4","content5",
                                      "content6","content7","content8","content9","content10","content11","content12","content13","content14","content15","content16","content17","content18","content19","content20","content21","content22","content23","content24","content25","content26","content27","content28","content29","content30","content31","content32","content33","content34","content35","content36","content37","content38","content39","content40","content41","content42","content43","content44","content45","content46","content47","content48","content49","content50","content51","content52","content53","content54","content55","content56","content57","content58","content59","content60","content61","content62","content63","content64","content65","content66","content67","content68","content69","content70","content71","content72","content73","content74","content75","content76","content77","content78","content79","content80","content81","content82","content83","content84","content85","content86","content87","content88","content89","content90","content91","content92","content93","content94","content95","content96","content97","content98","content99","content100","content101","content102","content103","content104","content105","content106","content107","content108","content109","content110","content111","content112","content113","content114","content115","content116","content117","content118","content119","content120","content121","content122","content123","content124","content125","content126","content127","content128","content129","content130","content131","content132","content133","content134","content135","content136","content137","content138","content139","content140","content141","content142","content143","content144","content145","content146","content147","content148","content149","content150","content151","content152","content153","content154","content155","content156","content157","content158","content159","content160","content161","content162","content163","content164","content165","content166","content167","content168","content169","content170","content171","content172","content173","content174","content175","content176","content177","content178","content179","content180","content181","content182","content183","content184","content185","content186","content187","content188","content189","content190","content191","content192","content193","content194","content195","content196","content197","content198","content199","content200","content201","content202","content203","content204","content205","content206","content207","content208","content209","content210","content211","content212","content213","content214","content215","content216","content217","content218","content219","content220","content221","content222","content223","content224","content225","content226","content227","content228","content229","content230","content231","content232","content233","content234","content235","content236","content237","content238","content239","content240","content241","content242","content243","content244","content245","content246","content247","content248","content249","content250","content251","content252","content253","content254","content255","content256","content257","content258","content259","content260","content261","content262","content263","content264","content265","content266","content267","content268","content269","content270","content271","content272","content273","content274","content275","content276","content277","content278","content279","content280","content281","content282","content283","content284","content285","content286","content287","content288","content289","content290","content291","content292","content293","content294","content295","content296","content297","content298","content299","content300","content301","content302","content303","content304","content305","content306","content307","content308","content309","content310","content311","content312","content313","content314","content315","content316","content317","content318","content319","content320","content321","content322","content323","content324","content325","content326","content327","content328","content329","content330","content331","content332","content333","content334","content335","content336","content337","content338","content339","content340","content341","content342","content343","content344","content345","content346","content347","content348","content349","content350","content351","content352","content353","content354","content355","content356","content357","content358","content359","content360","content361","content362","content363","content364","content365","content366","content367","content368","content369","content370","content371","content372","content373","content374","content375","content376","content377","content378","content379","content380","content381","content382","content383","content384","content385","content386","content387","content388","content389","content390","content391","content392","content393","content394","content395","content396","content397","content398","content399","content400","content401","content402","content403","content404","content405","content406","content407","content408","content409","content410","content411","content412","content413","content414","content415","content416","content417","content418","content419","content420","content421","content422","content423","content424","content425","content426","content427","content428","content429","content430","content431","content432","content433","content434","content435","content436","content437","content438","content439","content440","content441","content442","content443","content444","content445","content446","content447","content448","content449","content450","content451","content452","content453","content454","content455","content456","content457","content458","content459","content460","content461","content462","content463","content464","content465","content466","content467","content468","content469","content470","content471","content472","content473","content474","content475","content476","content477","content478","content479","content480","content481","content482","content483","content484","content485","content486","content487","content488","content489","content490","content491","content492","content493","content494","content495","content496","content497","content498","content499","content500"}
state_childsnack_p30.at_kitchen_sandwich = set()
state_childsnack_p30.not_allergic_gluten = {"child270","child74","child179","child235","child92","child288","child206","child442","child316","child75","child87","child307","child405","child489","child346","child232","child298","child201","child137","child64","child158","child474","child2","child114","child150","child151","child256","child184","child81","child447","child407","child317","child269","child329","child483","child60","child77","child308","child174","child37","child404","child144","child18","child17","child392","child98","child196","child406","child383","child225","child20","child457","child73","child48","child199","child445","child246","child25","child169","child462","child372","child29","child303","child146","child351","child34","child152","child263","child451","child41","child159","child425","child253","child68","child157","child255","child325","child23","child448","child28","child131","child438","child275","child58","child485","child97","child415","child258","child108","child279","child333","child432","child398","child52","child161","child363","child294","child261","child176","child322","child400","child230","child12","child1","child382","child282","child212","child188","child360","child355","child367","child465","child500","child118","child271","child54","child6","child93","child265","child99","child452","child101","child344","child440","child310","child332","child207","child192","child129","child90","child165","child283","child379","child257","child35","child171","child51","child135","child211","child8","child490","child46","child44","child299","child301","child456","child50","child417","child396","child401","child339","child311","child421","child61","child107","child446","child389","child361","child350","child162","child331","child187","child217","child111","child182","child124","child96","child194","child83","child210","child214","child198","child80","child492","child414","child302","child19","child324","child228","child443","child375","child439","child434","child148","child284","child334","child221","child30","child31","child345","child496","child373","child318","child145","child9","child120","child491","child156","child154","child371"}
state_childsnack_p30.notexist = {"sandw1","sandw2","sandw3" ,"sandw4","sandw5","sandw6","sandw7","sandw8","sandw9","sandw10","sandw11","sandw12","sandw13","sandw14","sandw15","sandw16","sandw17","sandw18","sandw19","sandw20","sandw21","sandw22","sandw23","sandw24","sandw25","sandw26","sandw27","sandw28","sandw29","sandw30","sandw31","sandw32","sandw33","sandw34","sandw35","sandw36","sandw37","sandw38","sandw39","sandw40","sandw41","sandw42","sandw43","sandw44","sandw45","sandw46","sandw47","sandw48","sandw49","sandw50","sandw51","sandw52","sandw53","sandw54","sandw55","sandw56","sandw57","sandw58","sandw59","sandw60","sandw61","sandw62","sandw63","sandw64","sandw65","sandw66","sandw67","sandw68","sandw69","sandw70","sandw71","sandw72","sandw73","sandw74","sandw75","sandw76","sandw77","sandw78","sandw79","sandw80","sandw81","sandw82","sandw83","sandw84","sandw85","sandw86","sandw87","sandw88","sandw89","sandw90","sandw91","sandw92","sandw93","sandw94","sandw95","sandw96","sandw97","sandw98","sandw99","sandw100","sandw101","sandw102","sandw103","sandw104","sandw105","sandw106","sandw107","sandw108","sandw109","sandw110","sandw111","sandw112","sandw113","sandw114","sandw115","sandw116","sandw117","sandw118","sandw119","sandw120","sandw121","sandw122","sandw123","sandw124","sandw125","sandw126","sandw127","sandw128","sandw129","sandw130","sandw131","sandw132","sandw133","sandw134","sandw135","sandw136","sandw137","sandw138","sandw139","sandw140","sandw141","sandw142","sandw143","sandw144","sandw145","sandw146","sandw147","sandw148","sandw149","sandw150","sandw151","sandw152","sandw153","sandw154","sandw155","sandw156","sandw157","sandw158","sandw159","sandw160","sandw161","sandw162","sandw163","sandw164","sandw165","sandw166","sandw167","sandw168","sandw169","sandw170","sandw171","sandw172","sandw173","sandw174","sandw175","sandw176","sandw177","sandw178","sandw179","sandw180","sandw181","sandw182","sandw183","sandw184","sandw185","sandw186","sandw187","sandw188","sandw189","sandw190","sandw191","sandw192","sandw193","sandw194","sandw195","sandw196","sandw197","sandw198","sandw199","sandw200","sandw201","sandw202","sandw203","sandw204","sandw205","sandw206","sandw207","sandw208","sandw209","sandw210","sandw211","sandw212","sandw213","sandw214","sandw215","sandw216","sandw217","sandw218","sandw219","sandw220","sandw221","sandw222","sandw223","sandw224","sandw225","sandw226","sandw227","sandw228","sandw229","sandw230","sandw231","sandw232","sandw233","sandw234","sandw235","sandw236","sandw237","sandw238","sandw239","sandw240","sandw241","sandw242","sandw243","sandw244","sandw245","sandw246","sandw247","sandw248","sandw249","sandw250","sandw251","sandw252","sandw253","sandw254","sandw255","sandw256","sandw257","sandw258","sandw259","sandw260","sandw261","sandw262","sandw263","sandw264","sandw265","sandw266","sandw267","sandw268","sandw269","sandw270","sandw271","sandw272","sandw273","sandw274","sandw275","sandw276","sandw277","sandw278","sandw279","sandw280","sandw281","sandw282","sandw283","sandw284","sandw285","sandw286","sandw287","sandw288","sandw289","sandw290","sandw291","sandw292","sandw293","sandw294","sandw295","sandw296","sandw297","sandw298","sandw299","sandw300","sandw301","sandw302","sandw303","sandw304","sandw305","sandw306","sandw307","sandw308","sandw309","sandw310","sandw311","sandw312","sandw313","sandw314","sandw315","sandw316","sandw317","sandw318","sandw319","sandw320","sandw321","sandw322","sandw323","sandw324","sandw325","sandw326","sandw327","sandw328","sandw329","sandw330","sandw331","sandw332","sandw333","sandw334","sandw335","sandw336","sandw337","sandw338","sandw339","sandw340","sandw341","sandw342","sandw343","sandw344","sandw345","sandw346","sandw347","sandw348","sandw349","sandw350","sandw351","sandw352","sandw353","sandw354","sandw355","sandw356","sandw357","sandw358","sandw359","sandw360","sandw361","sandw362","sandw363","sandw364","sandw365","sandw366","sandw367","sandw368","sandw369","sandw370","sandw371","sandw372","sandw373","sandw374","sandw375","sandw376","sandw377","sandw378","sandw379","sandw380","sandw381","sandw382","sandw383","sandw384","sandw385","sandw386","sandw387","sandw388","sandw389","sandw390","sandw391","sandw392","sandw393","sandw394","sandw395","sandw396","sandw397","sandw398","sandw399","sandw400","sandw401","sandw402","sandw403","sandw404","sandw405","sandw406","sandw407","sandw408","sandw409","sandw410","sandw411","sandw412","sandw413","sandw414","sandw415","sandw416","sandw417","sandw418","sandw419","sandw420","sandw421","sandw422","sandw423","sandw424","sandw425","sandw426","sandw427","sandw428","sandw429","sandw430","sandw431","sandw432","sandw433","sandw434","sandw435","sandw436","sandw437","sandw438","sandw439","sandw440","sandw441","sandw442","sandw443","sandw444","sandw445","sandw446","sandw447","sandw448","sandw449","sandw450","sandw451","sandw452","sandw453","sandw454","sandw455","sandw456","sandw457","sandw458","sandw459","sandw460","sandw461","sandw462","sandw463","sandw464","sandw465","sandw466","sandw467","sandw468","sandw469","sandw470","sandw471","sandw472","sandw473","sandw474","sandw475","sandw476","sandw477","sandw478","sandw479","sandw480","sandw481","sandw482","sandw483","sandw484","sandw485","sandw486","sandw487","sandw488","sandw489","sandw490","sandw491","sandw492","sandw493","sandw494","sandw495","sandw496","sandw497","sandw498","sandw499","sandw500"}
state_childsnack_p30.no_gluten_bread = {"bread328","bread58","bread13","bread380","bread141","bread126","bread115","bread72","bread378","bread53","bread347","bread497","bread457","bread280","bread45","bread303","bread217","bread17","bread16","bread48","bread112","bread120","bread259","bread309","bread14","bread288","bread102","bread367","bread333","bread360","bread487","bread215","bread113","bread230","bread302","bread143","bread415","bread446","bread4","bread389","bread413","bread82","bread358","bread484","bread175","bread465","bread80","bread111","bread391","bread173","bread491","bread481","bread195","bread50","bread184","bread434","bread177","bread310","bread136","bread414","bread23","bread374","bread236","bread275","bread64","bread194","bread41","bread283","bread151","bread425","bread322","bread317","bread186","bread296","bread99","bread361","bread36","bread24","bread339","bread117","bread396","bread149","bread445","bread479","bread52","bread448","bread455","bread233","bread326","bread187","bread84","bread190","bread182","bread108","bread344","bread137","bread471","bread350","bread332","bread37","bread312","bread412","bread88","bread274","bread439","bread495","bread410","bread237","bread464","bread139","bread500","bread353","bread286","bread468","bread351","bread167","bread29","bread118","bread483","bread162","bread206","bread138","bread34","bread109","bread291","bread368","bread381","bread377","bread336","bread256","bread203","bread330","bread235","bread74","bread442","bread493","bread127","bread475","bread276","bread135","bread300","bread220","bread299","bread205","bread428","bread387","bread71","bread261","bread253","bread47","bread25","bread57","bread79","bread430","bread459","bread488","bread306","bread33","bread198","bread196","bread406","bread240","bread271","bread129","bread284","bread6","bread59","bread437","bread405","bread329","bread456","bread499","bread432","bread223","bread81","bread460","bread2","bread431","bread257","bread92","bread260","bread55","bread153","bread320","bread400","bread474","bread348","bread192","bread83","bread277","bread272","bread1","bread307","bread166","bread251","bread10","bread331","bread356","bread158","bread123","bread30","bread124","bread376","bread418","bread44","bread249","bread424","bread273","bread65","bread66","bread244","bread282","bread85","bread366","bread338","bread345","bread373","bread311","bread103","bread160","bread357","bread313","bread225","bread265","bread232","bread62","bread364","bread116","bread343","bread174","bread11","bread383","bread355","bread462","bread401","bread31","bread269","bread35","bread382","bread170","bread266","bread122","bread441","bread295","bread110","bread452","bread492","bread485","bread422","bread226","bread147","bread148","bread478","bread63","bread201","bread248","bread207","bread105","bread49","bread403","bread241","bread169","bread453","bread91","bread372","bread106","bread417","bread222","bread411","bread476","bread451","bread168","bread308","bread26","bread482","bread104","bread362","bread87","bread470","bread221","bread28","bread436","bread447","bread242","bread379","bread494","bread294","bread438","bread386","bread365","bread119","bread219","bread20","bread114","bread496","bread227","bread498","bread385","bread255","bread267"}
state_childsnack_p30.no_gluten_content = {"content497","content48","content475","content386","content435","content122","content86","content209","content249","content247","content110","content443","content206","content463","content31","content85","content195","content2","content200","content136","content498","content402","content479","content233","content147","content217","content357","content375","content478","content285","content339","content368","content250","content80","content98","content152","content112","content30","content297","content377","content278","content32","content383","content161","content487","content26","content300","content245","content258","content437","content272","content81","content456","content261","content42","content436","content96","content36","content305","content35","content346","content121","content207","content62","content292","content127","content462","content442","content21","content318","content446","content215","content337","content299","content290","content268","content162","content134","content105","content343","content367","content457","content123","content481","content203","content68","content344","content331","content154","content235","content424","content385","content38","content5","content411","content319","content289","content52","content408","content276","content490","content260","content417","content415","content179","content489","content126","content190","content146","content449","content225","content279","content361","content155","content314","content335","content271","content407","content342","content284","content412","content340","content54","content69","content398","content60","content55","content381","content467","content140","content145","content310","content108","content176","content422","content352","content325","content376","content259","content251","content129","content27","content499","content364","content480","content142","content23","content483","content171","content67","content327","content135","content83","content227","content283","content219","content288","content458","content58","content39","content77","content280","content19","content393","content427","content440","content76","content221","content66","content22","content158","content187","content432","content184","content469","content128","content53","content182","content287","content493","content431","content372","content495","content84","content91","content212","content13","content92","content365","content211","content474","content137","content82","content56","content196","content20","content241","content114","content103","content236","content180","content157","content117","content115","content500","content99","content205","content169","content143","content395","content445","content454","content447","content294","content275","content170","content15","content473","content423","content313","content363","content433","content307","content223","content177","content419","content224","content262","content409","content198","content466","content131","content354","content274","content1","content101","content329","content333","content291","content471","content286","content64","content380","content159","content210","content317","content104","content396","content334","content355","content33","content50","content326","content312","content304","content270","content174","content192","content232","content45","content330","content392","content78","content254","content141","content214","content266","content238","content74","content378","content111","content202","content149","content156","content168","content348","content120","content303","content277","content173","content374","content269","content320","content204","content356","content189","content44","content293","content413","content73","content132","content414","content163","content257","content494","content24","content193","content61","content263","content405"}
state_childsnack_p30.no_gluten_sandwich = set()
state_childsnack_p30.ontray = {}
state_childsnack_p30.served = {}
state_childsnack_p30.waiting = {"child1":"table2","child2":"table2","child3":"table1","child4":"table1",
                           "child5":"table3","child6":"table1","child7":"table2","child8":"table1",
                           "child9":"table3","child10":"table3","child11":"table3","child12":"table1","child13":"table1","child14":"table1","child15":"table3","child16":"table2","child17":"table2","child18":"table3","child19":"table3","child20":"table3","child21":"table3","child22":"table2","child23":"table1","child24":"table1","child25":"table2","child26":"table1","child27":"table2","child28":"table1","child29":"table2","child30":"table1","child31":"table3","child32":"table3","child33":"table1","child34":"table2","child35":"table1","child36":"table1","child37":"table3","child38":"table2","child39":"table3","child40":"table1","child41":"table3","child42":"table2","child43":"table1","child44":"table1","child45":"table3","child46":"table2","child47":"table2","child48":"table2","child49":"table2","child50":"table2","child51":"table1","child52":"table1","child53":"table2","child54":"table2","child55":"table1","child56":"table1","child57":"table2","child58":"table2","child59":"table1","child60":"table3","child61":"table3","child62":"table3","child63":"table1","child64":"table1","child65":"table1","child66":"table3","child67":"table2","child68":"table1","child69":"table1","child70":"table1","child71":"table3","child72":"table2","child73":"table3","child74":"table3","child75":"table3","child76":"table1","child77":"table3","child78":"table2","child79":"table2","child80":"table2","child81":"table2","child82":"table3","child83":"table2","child84":"table2","child85":"table3","child86":"table3","child87":"table1","child88":"table3","child89":"table3","child90":"table1","child91":"table1","child92":"table3","child93":"table1","child94":"table2","child95":"table3","child96":"table1","child97":"table1","child98":"table1","child99":"table1","child100":"table3","child101":"table1","child102":"table1","child103":"table1","child104":"table2","child105":"table2","child106":"table3","child107":"table3","child108":"table2","child109":"table2","child110":"table1","child111":"table1","child112":"table2","child113":"table3","child114":"table2","child115":"table3","child116":"table2","child117":"table1","child118":"table3","child119":"table1","child120":"table2","child121":"table3","child122":"table3","child123":"table3","child124":"table1","child125":"table2","child126":"table1","child127":"table3","child128":"table1","child129":"table3","child130":"table1","child131":"table2","child132":"table1","child133":"table1","child134":"table1","child135":"table1","child136":"table2","child137":"table3","child138":"table3","child139":"table3","child140":"table2","child141":"table2","child142":"table1","child143":"table2","child144":"table3","child145":"table2","child146":"table3","child147":"table2","child148":"table2","child149":"table3","child150":"table3","child151":"table2","child152":"table2","child153":"table1","child154":"table3","child155":"table1","child156":"table2","child157":"table3","child158":"table2","child159":"table3","child160":"table2","child161":"table1","child162":"table1","child163":"table1","child164":"table3","child165":"table3","child166":"table3","child167":"table1","child168":"table3","child169":"table2","child170":"table3","child171":"table1","child172":"table1","child173":"table2","child174":"table3","child175":"table3","child176":"table2","child177":"table2","child178":"table1","child179":"table3","child180":"table2","child181":"table3","child182":"table2","child183":"table1","child184":"table2","child185":"table2","child186":"table2","child187":"table2","child188":"table2","child189":"table3","child190":"table1","child191":"table1","child192":"table2","child193":"table2","child194":"table3","child195":"table2","child196":"table2","child197":"table3","child198":"table2","child199":"table3","child200":"table1","child201":"table2","child202":"table1","child203":"table2","child204":"table2","child205":"table2","child206":"table1","child207":"table2","child208":"table3","child209":"table1","child210":"table3","child211":"table3","child212":"table2","child213":"table2","child214":"table1","child215":"table1","child216":"table3","child217":"table2","child218":"table3","child219":"table2","child220":"table3","child221":"table2","child222":"table1","child223":"table1","child224":"table2","child225":"table3","child226":"table1","child227":"table2","child228":"table2","child229":"table3","child230":"table2","child231":"table1","child232":"table1","child233":"table3","child234":"table3","child235":"table1","child236":"table3","child237":"table1","child238":"table2","child239":"table3","child240":"table1","child241":"table3","child242":"table2","child243":"table1","child244":"table1","child245":"table1","child246":"table2","child247":"table1","child248":"table3","child249":"table1","child250":"table2","child251":"table3","child252":"table2","child253":"table3","child254":"table3","child255":"table2","child256":"table2","child257":"table2","child258":"table2","child259":"table1","child260":"table2","child261":"table3","child262":"table1","child263":"table2","child264":"table1","child265":"table3","child266":"table3","child267":"table3","child268":"table1","child269":"table1","child270":"table2","child271":"table2","child272":"table2","child273":"table3","child274":"table2","child275":"table1","child276":"table2","child277":"table3","child278":"table2","child279":"table3","child280":"table3","child281":"table3","child282":"table2","child283":"table1","child284":"table2","child285":"table3","child286":"table2","child287":"table2","child288":"table2","child289":"table3","child290":"table3","child291":"table2","child292":"table2","child293":"table2","child294":"table1","child295":"table3","child296":"table1","child297":"table3","child298":"table2","child299":"table1","child300":"table2","child301":"table1","child302":"table2","child303":"table3","child304":"table2","child305":"table3","child306":"table2","child307":"table2","child308":"table3","child309":"table3","child310":"table1","child311":"table2","child312":"table1","child313":"table1","child314":"table3","child315":"table3","child316":"table2","child317":"table1","child318":"table2","child319":"table1","child320":"table3","child321":"table2","child322":"table1","child323":"table3","child324":"table1","child325":"table2","child326":"table3","child327":"table1","child328":"table1","child329":"table2","child330":"table2","child331":"table2","child332":"table3","child333":"table3","child334":"table2","child335":"table3","child336":"table1","child337":"table2","child338":"table3","child339":"table3","child340":"table2","child341":"table2","child342":"table3","child343":"table3","child344":"table2","child345":"table3","child346":"table1","child347":"table3","child348":"table1","child349":"table1","child350":"table3","child351":"table3","child352":"table2","child353":"table1","child354":"table3","child355":"table1","child356":"table2","child357":"table1","child358":"table3","child359":"table3","child360":"table1","child361":"table2","child362":"table1","child363":"table3","child364":"table2","child365":"table1","child366":"table1","child367":"table2","child368":"table1","child369":"table2","child370":"table2","child371":"table2","child372":"table2","child373":"table1","child374":"table1","child375":"table3","child376":"table2","child377":"table3","child378":"table3","child379":"table1","child380":"table1","child381":"table1","child382":"table1","child383":"table3","child384":"table2","child385":"table3","child386":"table3","child387":"table1","child388":"table2","child389":"table3","child390":"table1","child391":"table1","child392":"table2","child393":"table3","child394":"table2","child395":"table2","child396":"table2","child397":"table3","child398":"table1","child399":"table2","child400":"table2","child401":"table3","child402":"table3","child403":"table1","child404":"table1","child405":"table2","child406":"table2","child407":"table3","child408":"table2","child409":"table3","child410":"table2","child411":"table3","child412":"table2","child413":"table2","child414":"table2","child415":"table1","child416":"table2","child417":"table2","child418":"table1","child419":"table1","child420":"table2","child421":"table3","child422":"table2","child423":"table3","child424":"table2","child425":"table3","child426":"table2","child427":"table1","child428":"table3","child429":"table2","child430":"table2","child431":"table1","child432":"table3","child433":"table3","child434":"table3","child435":"table1","child436":"table3","child437":"table3","child438":"table2","child439":"table2","child440":"table1","child441":"table3","child442":"table2","child443":"table1","child444":"table3","child445":"table1","child446":"table3","child447":"table2","child448":"table3","child449":"table3","child450":"table3","child451":"table3","child452":"table1","child453":"table3","child454":"table1","child455":"table3","child456":"table3","child457":"table1","child458":"table2","child459":"table2","child460":"table1","child461":"table3","child462":"table2","child463":"table3","child464":"table1","child465":"table1","child466":"table2","child467":"table2","child468":"table3","child469":"table2","child470":"table1","child471":"table1","child472":"table1","child473":"table3","child474":"table2","child475":"table3","child476":"table3","child477":"table2","child478":"table1","child479":"table2","child480":"table2","child481":"table2","child482":"table3","child483":"table2","child484":"table1","child485":"table2","child486":"table1","child487":"table1","child488":"table1","child489":"table3","child490":"table3","child491":"table3","child492":"table2","child493":"table3","child494":"table2","child495":"table1","child496":"table2","child497":"table1","child498":"table2","child499":"table3","child500":"table1"}

# Set goal from the :htn :ordered-subtasks in p30.hddl
htn_ordered_subtask_childsnack_p30 = Multigoal("goal_childsnack_p30",served=state_childsnack_p30.waiting)

# Set goal state from p30.hddl
# 	(:goal (and
# (served child1)
# (served child2)
# (served child3)
# (served child4)
# (served child5)
# (served child6)
# (served child7)
# (served child8)
# (served child9)
# (served child10)
# (served child11)
# (served child12)
# (served child13)
# (served child14)
# (served child15)
# (served child16)
# (served child17)
# (served child18)
# (served child19)
# (served child20)
# (served child21)
# (served child22)
# (served child23)
# (served child24)
# (served child25)
# (served child26)
# (served child27)
# (served child28)
# (served child29)
# (served child30)
# (served child31)
# (served child32)
# (served child33)
# (served child34)
# (served child35)
# (served child36)
# (served child37)
# (served child38)
# (served child39)
# (served child40)
# (served child41)
# (served child42)
# (served child43)
# (served child44)
# (served child45)
# (served child46)
# (served child47)
# (served child48)
# (served child49)
# (served child50)
# (served child51)
# (served child52)
# (served child53)
# (served child54)
# (served child55)
# (served child56)
# (served child57)
# (served child58)
# (served child59)
# (served child60)
# (served child61)
# (served child62)
# (served child63)
# (served child64)
# (served child65)
# (served child66)
# (served child67)
# (served child68)
# (served child69)
# (served child70)
# (served child71)
# (served child72)
# (served child73)
# (served child74)
# (served child75)
# (served child76)
# (served child77)
# (served child78)
# (served child79)
# (served child80)
# (served child81)
# (served child82)
# (served child83)
# (served child84)
# (served child85)
# (served child86)
# (served child87)
# (served child88)
# (served child89)
# (served child90)
# (served child91)
# (served child92)
# (served child93)
# (served child94)
# (served child95)
# (served child96)
# (served child97)
# (served child98)
# (served child99)
# (served child100)
# (served child101)
# (served child102)
# (served child103)
# (served child104)
# (served child105)
# (served child106)
# (served child107)
# (served child108)
# (served child109)
# (served child110)
# (served child111)
# (served child112)
# (served child113)
# (served child114)
# (served child115)
# (served child116)
# (served child117)
# (served child118)
# (served child119)
# (served child120)
# (served child121)
# (served child122)
# (served child123)
# (served child124)
# (served child125)
# (served child126)
# (served child127)
# (served child128)
# (served child129)
# (served child130)
# (served child131)
# (served child132)
# (served child133)
# (served child134)
# (served child135)
# (served child136)
# (served child137)
# (served child138)
# (served child139)
# (served child140)
# (served child141)
# (served child142)
# (served child143)
# (served child144)
# (served child145)
# (served child146)
# (served child147)
# (served child148)
# (served child149)
# (served child150)
# (served child151)
# (served child152)
# (served child153)
# (served child154)
# (served child155)
# (served child156)
# (served child157)
# (served child158)
# (served child159)
# (served child160)
# (served child161)
# (served child162)
# (served child163)
# (served child164)
# (served child165)
# (served child166)
# (served child167)
# (served child168)
# (served child169)
# (served child170)
# (served child171)
# (served child172)
# (served child173)
# (served child174)
# (served child175)
# (served child176)
# (served child177)
# (served child178)
# (served child179)
# (served child180)
# (served child181)
# (served child182)
# (served child183)
# (served child184)
# (served child185)
# (served child186)
# (served child187)
# (served child188)
# (served child189)
# (served child190)
# (served child191)
# (served child192)
# (served child193)
# (served child194)
# (served child195)
# (served child196)
# (served child197)
# (served child198)
# (served child199)
# (served child200)
# (served child201)
# (served child202)
# (served child203)
# (served child204)
# (served child205)
# (served child206)
# (served child207)
# (served child208)
# (served child209)
# (served child210)
# (served child211)
# (served child212)
# (served child213)
# (served child214)
# (served child215)
# (served child216)
# (served child217)
# (served child218)
# (served child219)
# (served child220)
# (served child221)
# (served child222)
# (served child223)
# (served child224)
# (served child225)
# (served child226)
# (served child227)
# (served child228)
# (served child229)
# (served child230)
# (served child231)
# (served child232)
# (served child233)
# (served child234)
# (served child235)
# (served child236)
# (served child237)
# (served child238)
# (served child239)
# (served child240)
# (served child241)
# (served child242)
# (served child243)
# (served child244)
# (served child245)
# (served child246)
# (served child247)
# (served child248)
# (served child249)
# (served child250)
# (served child251)
# (served child252)
# (served child253)
# (served child254)
# (served child255)
# (served child256)
# (served child257)
# (served child258)
# (served child259)
# (served child260)
# (served child261)
# (served child262)
# (served child263)
# (served child264)
# (served child265)
# (served child266)
# (served child267)
# (served child268)
# (served child269)
# (served child270)
# (served child271)
# (served child272)
# (served child273)
# (served child274)
# (served child275)
# (served child276)
# (served child277)
# (served child278)
# (served child279)
# (served child280)
# (served child281)
# (served child282)
# (served child283)
# (served child284)
# (served child285)
# (served child286)
# (served child287)
# (served child288)
# (served child289)
# (served child290)
# (served child291)
# (served child292)
# (served child293)
# (served child294)
# (served child295)
# (served child296)
# (served child297)
# (served child298)
# (served child299)
# (served child300)
# (served child301)
# (served child302)
# (served child303)
# (served child304)
# (served child305)
# (served child306)
# (served child307)
# (served child308)
# (served child309)
# (served child310)
# (served child311)
# (served child312)
# (served child313)
# (served child314)
# (served child315)
# (served child316)
# (served child317)
# (served child318)
# (served child319)
# (served child320)
# (served child321)
# (served child322)
# (served child323)
# (served child324)
# (served child325)
# (served child326)
# (served child327)
# (served child328)
# (served child329)
# (served child330)
# (served child331)
# (served child332)
# (served child333)
# (served child334)
# (served child335)
# (served child336)
# (served child337)
# (served child338)
# (served child339)
# (served child340)
# (served child341)
# (served child342)
# (served child343)
# (served child344)
# (served child345)
# (served child346)
# (served child347)
# (served child348)
# (served child349)
# (served child350)
# (served child351)
# (served child352)
# (served child353)
# (served child354)
# (served child355)
# (served child356)
# (served child357)
# (served child358)
# (served child359)
# (served child360)
# (served child361)
# (served child362)
# (served child363)
# (served child364)
# (served child365)
# (served child366)
# (served child367)
# (served child368)
# (served child369)
# (served child370)
# (served child371)
# (served child372)
# (served child373)
# (served child374)
# (served child375)
# (served child376)
# (served child377)
# (served child378)
# (served child379)
# (served child380)
# (served child381)
# (served child382)
# (served child383)
# (served child384)
# (served child385)
# (served child386)
# (served child387)
# (served child388)
# (served child389)
# (served child390)
# (served child391)
# (served child392)
# (served child393)
# (served child394)
# (served child395)
# (served child396)
# (served child397)
# (served child398)
# (served child399)
# (served child400)
# (served child401)
# (served child402)
# (served child403)
# (served child404)
# (served child405)
# (served child406)
# (served child407)
# (served child408)
# (served child409)
# (served child410)
# (served child411)
# (served child412)
# (served child413)
# (served child414)
# (served child415)
# (served child416)
# (served child417)
# (served child418)
# (served child419)
# (served child420)
# (served child421)
# (served child422)
# (served child423)
# (served child424)
# (served child425)
# (served child426)
# (served child427)
# (served child428)
# (served child429)
# (served child430)
# (served child431)
# (served child432)
# (served child433)
# (served child434)
# (served child435)
# (served child436)
# (served child437)
# (served child438)
# (served child439)
# (served child440)
# (served child441)
# (served child442)
# (served child443)
# (served child444)
# (served child445)
# (served child446)
# (served child447)
# (served child448)
# (served child449)
# (served child450)
# (served child451)
# (served child452)
# (served child453)
# (served child454)
# (served child455)
# (served child456)
# (served child457)
# (served child458)
# (served child459)
# (served child460)
# (served child461)
# (served child462)
# (served child463)
# (served child464)
# (served child465)
# (served child466)
# (served child467)
# (served child468)
# (served child469)
# (served child470)
# (served child471)
# (served child472)
# (served child473)
# (served child474)
# (served child475)
# (served child476)
# (served child477)
# (served child478)
# (served child479)
# (served child480)
# (served child481)
# (served child482)
# (served child483)
# (served child484)
# (served child485)
# (served child486)
# (served child487)
# (served child488)
# (served child489)
# (served child490)
# (served child491)
# (served child492)
# (served child493)
# (served child494)
# (served child495)
# (served child496)
# (served child497)
# (served child498)
# (served child499)
# (served child500)
# 	))
goal_childsnack_p30 = state_childsnack_p30.waiting

# ============================================================================
# END OF FILE
# ============================================================================