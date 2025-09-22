# ============================================================================
# IPC 2020 Total Order - Blocksworld Domain
# ============================================================================

# ============================================================================
# FILE ORGANIZATION
# ----------------------------------------------------------------------------
# This file is organized into the following sections:
#   - Imports (with secure path handling)
#   - PROBLEMS (20)
#       - BW_rand from 5 (p01.hddl) to 43 (p20.hddl) blocks
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
# PROBLEMS (20)
# ============================================================================

# ===== BW_rand_5 --------------------------------------------------- p01.hddl
state_BW_rand_5 = State("BW-rand-5_initial_state")

# Define all blocks
state_BW_rand_5.blocks = {"b1", "b2", "b3", "b4", "b5"}

# Set initial state from p01.hddl
state_BW_rand_5.on = {"b2" : "b3", "b3" : "b5", "b4" : "b1", "b5" : "b4"}
print("BW-rand-5 Initial situation:")
print(" - table > b1 > b4 > b5 > b3 > b2")
print()
state_BW_rand_5.ontable = {"b1"}
state_BW_rand_5.clear = {"b2"}
state_BW_rand_5.handempty = True
state_BW_rand_5.holding = None
state_BW_rand_5.holding_size = None

# Set goal from the :htn :ordered-subtasks in p01.hddl
htn_ordered_subtask_BW_rand_5 = Multigoal("goal-BW-rand-5",on={"b4":"b2", "b1":"b4", "b3":"b1"})

# Set goal state from p01.hddl
# 	(:goal (and
#       (on b1 b4)
#       (on b3 b1)
# 	))
# htn_ordered_subtask_BW_5 = Multigoal("goal-BW-rand-5",on={"b1":"b4", "b3":"b1"})
goal_BW_rand_5 = {"b1":"b4", "b3":"b1"}

# ===== BW_rand_7 --------------------------------------------------- p02.hddl
state_BW_rand_7 = State("BW-rand-7_initial_state")

# Define all blocks
state_BW_rand_7.blocks = {"b1", "b2", "b3", "b4", "b5", "b6", "b7"}
# Set initial state from p02.hddl
print("BW-rand-7 Initial situation:")
print(" - table > b4")
print(" - table > b2")
print(" - table > b7 > b1 > b5 > b6 > b3")
print()
state_BW_rand_7.on = {"b1": "b7", "b3": "b6", "b5": "b1", "b6": "b5"}
state_BW_rand_7.ontable = {"b4", "b2", "b7"}
state_BW_rand_7.clear = {"b4", "b2", "b3"}
state_BW_rand_7.handempty = True
state_BW_rand_7.holding = None

# Set goal state from the :htn :ordered-subtasks in p02.hddl
htn_ordered_subtask_BW_rand_7 = Multigoal("goal-BW-rand-7",on={"b3":"b5", "b6":"b3", "b1":"b6", "b2":"b1", "b4":"b2", "b7":"b4"})

# Set goal state from p02.hddl
goal_BW_rand_7 = {"b1":"b6", "b2":"b1", "b3":"b5", "b4":"b2", "b6":"b3"}

# ===== BW_rand_9 --------------------------------------------------- p03.hddl
state_BW_rand_9 = State("BW-rand-9_initial_state")

# Define all blocks
state_BW_rand_9.blocks = {"b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8", "b9"}

# Set initial state from p03.hddl
print("BW-rand-9 Initial situation:")
print(" - table > b3 > b1 > b8 > b9 > b5 > b2 > b3")
print(" - table > b4 > b6")
state_BW_rand_9.on = {"b1": "b3","b2": "b5","b5": "b9","b6": "b4","b7": "b2","b8": "b1","b9": "b8"}
state_BW_rand_9.ontable = {"b4", "b3"}
state_BW_rand_9.clear = {"b6", "b7"}
state_BW_rand_9.handempty = True
state_BW_rand_9.holding = None

# Set goal state from the :htn :ordered-subtasks in p03.hddl
htn_ordered_subtask_BW_rand_9 = Multigoal("goal-BW-rand-9",on={"b3":"b4", "b6":"b3", "b2":"b6", "b1":"b2", "b5":"b1"})

# Set goal state from p03.hddl
goal_BW_rand_9 = {"b1":"b2", "b2":"b6", "b3":"b4", "b5":"b1"}


# ===== BW_rand_11 -------------------------------------------------- p04.hddl
state_BW_rand_11 = State("BW-rand-11_initial_state")

#  Define all blocks
state_BW_rand_11.blocks = {"b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8", "b9"}

# Set initial state from p04.hddl
print("BW-rand-11 Initial situation:")
print(" - table > b1 > b10 > b3 > b8 > b11 > b6 > b7")
print(" - table > b5 > b4 > b9 > b2")
# Define all blocks
state_BW_rand_11.blocks = {"b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8", "b9", "b10", "b11"}
state_BW_rand_11.on = {"b2": "b9", "b3": "b10", "b4": "b5", "b6": "b11", "b7": "b6",
            "b8": "b3", "b9": "b4", "b10": "b1", "b11": "b8"}
state_BW_rand_11.ontable = {"b1", "b5"}
state_BW_rand_11.clear = {"b2", "b7"}
state_BW_rand_11.handempty = True
state_BW_rand_11.holding = None

# Set goal state from the :htn :ordered-subtasks in p04.hddl
htn_ordered_subtask_BW_rand_11 = Multigoal("goal-BW-rand-11", on={"b10":"b6", "b5":"b10", "b2":"b5", "b9":"b2", "b1":"b9", "b11":"b1", "b10":"b6", "b5":"b10", "b2":"b5", "b9":"b2", "b1":"b9", "b11":"b1", "b4":"b11", "b7":"b4"})

# Set goal state from p04.hddl
goal_BW_rand_11 = {"b1":"b9", "b2":"b5", "b4":"b11", "b5":"b10", "b7":"b4", "b9":"b2", "b10":"b6"}


# ===== BW_rand_13 -------------------------------------------------- p05.hddl
state_BW_rand_13 = State("BW-rand-13_initial_state")

# Define all blocks
state_BW_rand_13.blocks = {"b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8", "b9", "b10", "b11", "b12", "b13"}

# Set initial state from p05.hddl
state_BW_rand_13.on = {"b1": "b5", "b3": "b10", "b5": "b9", "b7": "b1", "b8": "b3",
            "b9": "b13", "b13": "b12"}
state_BW_rand_13.ontable = {"b2", "b4", "b6", "b10", "b11", "b12"}
state_BW_rand_13.clear = {"b2", "b4", "b6", "b7", "b8", "b11"}
state_BW_rand_13.handempty = True
state_BW_rand_13.holding = None

# Set goal state from the :htn :ordered-subtasks in p05.hddl
htn_ordered_subtask_BW_rand_13 = Multigoal("goal-BW-rand-13", on= {"b4":"b13", "b8":"b4", "b11":"b8", "b10":"b11", "b5":"b10", "b6":"b5", "b12":"b6", "b2":"b12", "b9":"b2", "b7":"b9", "b3":"b7", "b1":"b3"})

# Set goal state from p05.hddl
goal_BW_rand_13 = {"b1":"b3", "b2":"b12", "b3":"b7", "b4":"b13", "b5":"b10", "b6":"b5", "b7":"b9",
"b8":"b4", "b9":"b2", "b10":"b11", "b11":"b8"}

# ===== BW_rand_15 -------------------------------------------------- p06.hddl
state_BW_rand_15 = State("BW-rand-15_initial_state")

# Define all blocks
state_BW_rand_15.blocks = {"b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8", "b9", "b10",
                "b11", "b12", "b13", "b14", "b15"}

# Set initial state from p06.hddl
state_BW_rand_15.on = {"b1": "b14", "b2": "b6", "b3": "b4", "b4": "b2", "b5": "b11",
            "b6": "b9", "b7": "b1", "b9": "b8", "b12": "b13", "b13": "b10",
            "b15": "b7"}
state_BW_rand_15.ontable = {"b8", "b10", "b11", "b14"}
state_BW_rand_15.clear = {"b3", "b5", "b12", "b15"}
state_BW_rand_15.handempty = True
state_BW_rand_15.holding = None

# Set goal state from the :htn :ordered-subtasks in p06.hddl
htn_ordered_subtask_BW_rand_15 = Multigoal("goal-BW-rand-15", on= {"b14":"b7", "b15":"b14","b5": "b15", "b1":"b5", "b8":"b1", "b2":"b13", "b9":"b2", "b12":"b6", "b3":"b12", "b4":"b3", "b11":"b4", "b10":"b11"})

# Set goal state from p06.hddl
goal_BW_rand_15 = {"b1":"b5", "b2":"b13", "b3":"b12", "b4":"b3", "b5":"b15", "b8":"b1", "b9":"b2", 
"b10":"b11", "b11":"b4", "b12":"b6", "b14":"b7"}

# ===== BW_rand_17 -------------------------------------------------- p07.hddl
state_BW_rand_17 = State("BW-rand-17_initial_state")

# Define all blocks
state_BW_rand_17.blocks = {"b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8", "b9", "b10",
                "b11", "b12", "b13", "b14", "b15", "b16", "b17"}

# Set initial state from p07.hddl
state_BW_rand_17.on = {"b1": "b13", "b2": "b10", "b4": "b3", "b5": "b15", "b6": "b14",
            "b7": "b12", "b8": "b9", "b11": "b6", "b12": "b4", "b13": "b8",
            "b15": "b7", "b16": "b2", "b17": "b5"}
state_BW_rand_17.ontable = {"b3", "b9", "b10", "b14"}
state_BW_rand_17.clear = {"b1", "b11", "b16", "b17"}
state_BW_rand_17.handempty = True
state_BW_rand_17.holding = None

# Set goal state from the :htn :ordered-subtasks in p07.hddl
htn_ordered_subtask_BW_rand_17 = Multigoal("goal-BW-rand-17", on= {"b8":"b9", "b15":"b8", "b13":"b15", "b1":"b13", "b11":"b1", "b3":"b10", "b4":"b3", "b12":"b4", "b2":"b12", "b5":"b11", "b6":"b16", "b7":"b14", "b17":"b7"})

# Set goal state from p07.hddl
goal_BW_rand_17 = {"b1":"b13", "b2":"b12", "b3":"b10", "b4":"b3", "b5":"b11", "b6":"b16", 
"b7":"b14", "b8":"b9", "b11":"b1", "b12":"b4", "b13":"b15", "b15":"b8"}

# ===== BW_rand_19 -------------------------------------------------- p08.hddl
state_BW_rand_19 = State("BW-rand-19_initial_state")

# Define all blocks
state_BW_rand_19.blocks = {"b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8", "b9", "b10",
                "b11", "b12", "b13", "b14", "b15", "b16", "b17", "b18", "b19"}

# Set initial state
state_BW_rand_19.on = {"b1": "b7", "b2": "b18", "b4": "b17", "b5": "b6", "b7": "b2",
            "b8": "b3", "b9": "b1", "b10": "b12", "b11": "b15", "b12": "b19",
            "b13": "b11", "b14": "b10", "b15": "b4", "b17": "b9", "b18": "b16",
            "b19": "b5"}
state_BW_rand_19.ontable = {"b3", "b6", "b16"}
state_BW_rand_19.clear = {"b8", "b13", "b14"}
state_BW_rand_19.handempty = True
state_BW_rand_19.holding = None

# Set goal state from the :htn :ordered-subtasks in p08.hddl
htn_ordered_subtask_BW_rand_19 = Multigoal("goal-BW-rand-19", on= {"b16":"b1", "b5": "b16", "b6": "b5", "b2":"b6", "b15":"b2", "b9":"b8", "b14":"b9", "b17":"b14", "b10":"b17", "b12":"b10", "b4":"b12", "b13":"b4", "b3":"b15", "b11":"b3", "b19":"b11", "b7":"b19", "b18":"b7"})

# Set goal state from p08.hddl
goal_BW_rand_19 = {"b2":"b6", "b3":"b15", "b4":"b12", "b5":"b16", "b6":"b5", "b7":"b19", "b9":"b8", 
"b10":"b17", "b11":"b3", "b12":"b10", "b13":"b4", "b14":"b9", "b15":"b2", 
"b16":"b1", "b17":"b14", "b18":"b7"}

# ===== BW_rand_21 -------------------------------------------------- p09.hddl
state_BW_rand_21 = State("BW-rand-21_initial_state")

# Define all blocks
state_BW_rand_21.blocks = {"b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8", "b9", "b10",
                "b11", "b12", "b13", "b14", "b15", "b16", "b17", "b18", "b19", "b20",
                "b21"}

# Set initial state from p09.hddl
state_BW_rand_21.on = {"b1": "b7", "b2": "b14", "b3": "b12", "b4": "b1", "b5": "b3",
            "b6": "b16", "b7": "b9", "b8": "b20", "b9": "b17", "b10": "b19",
            "b13": "b15", "b15": "b5", "b16": "b2", "b17": "b13", "b18": "b6",
            "b20": "b18", "b21": "b10"}
state_BW_rand_21.ontable = {"b11", "b12", "b14", "b19"}
state_BW_rand_21.clear = {"b4", "b8", "b11", "b21"}
state_BW_rand_21.handempty = True
state_BW_rand_21.holding = None

# Set goal state from the :htn :ordered-subtasks in p09.hddl
htn_ordered_subtask_BW_rand_21 = Multigoal("goal-BW-rand-21", on= {"b1":"b5", "b7":"b1", "b13":"b7", "b11":"b13", "b3":"b11", "b12":"b2", "b4":"b12", "b20":"b4", "b21":"b20", "b10":"b16", "b8":"b10", "b9":"b8", "b19":"b9", "b18":"b15", "b17":"b18"})

# Set goal state from p09.hddl
goal_BW_rand_21 = {"b1":"b5", "b3":"b11", "b4":"b12", "b7":"b1", "b8":"b10", "b9":"b8", 
"b10":"b16", "b11":"b13", "b12":"b2", "b13":"b7", "b17":"b18", "b18":"b15", 
"b19":"b9", "b20":"b4"}

# ===== BW_rand_23 -------------------------------------------------- p10.hddl
state_BW_rand_23 = State("BW-rand-23_initial_state")

# Define all blocks
state_BW_rand_23.blocks = {"b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8", "b9", "b10",
                    "b11", "b12", "b13", "b14", "b15", "b16", "b17", "b18", "b19", "b20",
                    "b21", "b22", "b23"}

# Set initial state from p10.hddl
state_BW_rand_23.on = {"b1": "b23", "b2": "b9", "b3": "b13", "b4": "b5", "b6": "b10",
            "b7": "b6", "b8": "b16", "b9": "b4", "b10": "b11", "b11": "b1",
            "b12": "b7", "b13": "b20", "b15": "b19", "b16": "b22", "b17": "b8",
            "b18": "b3", "b19": "b14", "b20": "b15", "b21": "b18", "b22": "b12",
            "b23": "b21"}
state_BW_rand_23.ontable = {"b5", "b14"}
state_BW_rand_23.clear = {"b2", "b17"}
state_BW_rand_23.handempty = True
state_BW_rand_23.holding = None

# Set goal state from the :htn :ordered-subtasks in p10.hddl
htn_ordered_subtask_BW_rand_23 = Multigoal("goal-BW-rand-23", on= {"b15":"b13", "b22":"b15", "b10":"b22", "b8":"b10", "b12":"b8", "b18":"b12", "b17":"b18", "b19":"b17", "b6":"b19", "b11":"b6", "b9":"b11", "b1":"b9", "b16":"b1", "b7":"b23", "b4":"b7", "b5":"b4", "b2":"b5", "b3":"b16", "b20":"b3", "b14":"b21"})

# Set goal state from p10.hddl
goal_BW_rand_23 = {"b1":"b9", "b2":"b5", "b3":"b16", "b4":"b7", "b5":"b4", "b6":"b19", "b7":"b23", 
"b8":"b10", "b9":"b11", "b10":"b22", "b11":"b6", "b12":"b8", "b14":"b21", 
"b15":"b13", "b16":"b1", "b17":"b18", "b18":"b12", "b19":"b17", "b20":"b3"}

# ===== BW_rand_25 -------------------------------------------------- p11.hddl
state_BW_rand_25 = State("BW-rand-25_initial_state")

# Define all blocks
state_BW_rand_25.blocks = {"b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8", "b9", "b10",
                "b11", "b12", "b13", "b14", "b15", "b16", "b17", "b18", "b19", "b20",
                "b21", "b22", "b23", "b24", "b25"}

# Set initial state from p11.hddl
state_BW_rand_25.on = {"b1": "b11", "b3": "b16", "b4": "b1", "b5": "b23", "b6": "b7",
            "b7": "b10", "b8": "b3", "b10": "b9", "b11": "b20", "b12": "b19",
            "b13": "b18", "b14": "b5", "b15": "b22", "b16": "b17", "b17": "b4",
            "b18": "b2", "b19": "b8", "b20": "b24", "b21": "b14", "b22": "b25",
            "b23": "b13", "b24": "b15", "b25": "b6"}
state_BW_rand_25.ontable = {"b2", "b9"}
state_BW_rand_25.clear = {"b12", "b21"}
state_BW_rand_25.handempty = True
state_BW_rand_25.holding = None

# Set goal state from the :htn :ordered-subtasks in p11.hddl
htn_ordered_subtask_BW_rand_25 = Multigoal("goal-BW-rand-25", on= {"b18":"b17", "b9":"b18", "b3":"b9", "b1":"b3", "b21":"b1",
                                                    "b18":"b17", "b5":"b21", "b19":"b5", "b8":"b15", "b23":"b10",
                                                    "b16":"b23", "b25":"b16", "b14":"b25", "b11":"b14", "b4":"b11",
                                                    "b6":"b4", "b24":"b6", "b13":"b24", "b7":"b12", "b2":"b7",
                                                    "b22":"b2", "b20":"b22"})

# Set goal state from p11.hddl
goal_BW_rand_25 = {"b1":"b3", "b2":"b7", "b3":"b9", "b4":"b11", "b5":"b21", "b6":"b4", "b7":"b12", 
"b8":"b15", "b9":"b18", "b11":"b14", "b13":"b24", "b14":"b25", "b16":"b23", 
"b18":"b17", "b19":"b5", "b20":"b22", "b21":"b1", "b22":"b2", "b23":"b10", "b24":"b6"}

# ===== BW_rand_27 -------------------------------------------------- p12.hddl
state_BW_rand_27 = State("BW-rand-27_initial_state")

# Define all blocks
state_BW_rand_27.blocks = {"b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8", "b9", "b10",
                "b11", "b12", "b13", "b14", "b15", "b16", "b17", "b18", "b19", "b20",
                "b21", "b22", "b23", "b24", "b25", "b26", "b27"}

# Set initial state from p12.hddl
state_BW_rand_27.on = {"b1": "b11", "b3": "b8", "b4": "b3", "b5": "b23", "b6": "b14",
            "b7": "b2", "b8": "b15", "b9": "b4", "b11": "b7", "b12": "b9",
            "b13": "b19", "b14": "b20", "b15": "b10", "b16": "b24", "b17": "b26",
            "b18": "b12", "b19": "b1", "b20": "b21", "b21": "b16", "b22": "b18",
            "b23": "b6", "b24": "b17", "b25": "b22", "b26": "b13"}
state_BW_rand_27.ontable = {"b2", "b10", "b27"}
state_BW_rand_27.clear = {"b5", "b25", "b27"}
state_BW_rand_27.handempty = True
state_BW_rand_27.holding = None

# Set goal state from the :htn :ordered-subtasks in p12.hddl
htn_ordered_subtask_BW_rand_27 = Multigoal("goal-BW-rand-27", on= {"b1":"b17", "b26":"b1", "b7":"b3", "b19":"b7", "b11":"b4",
                                                    "b5":"b11", "b10":"b5", "b8":"b10", "b12":"b8", "b16":"b12", 
                                                    "b9":"b16", "b23":"b9", "b6":"b15", "b24":"b6", 
                                                    "b13":"b24", "b2":"b25", "b22":"b2", "b14":"b22", 
                                                    "b18":"b27", "b21":"b18", "b1":"b17", "b26":"b1", 
                                                    "b20":"b26"})

# Set goal state from p12.hddl
goal_BW_rand_27 = {"b1":"b17", "b2":"b25", "b5":"b11", "b6":"b15", "b7":"b3", "b8":"b10", 
"b9":"b16", "b10":"b5", "b11":"b4", "b12":"b8", "b13":"b24", "b14":"b22", 
"b16":"b12", "b18":"b27", "b19":"b7", "b20":"b26", "b21":"b18", "b22":"b2", 
"b23":"b9", "b24":"b6"}

# ===== BW_rand_29 -------------------------------------------------- p13.hddl
state_BW_rand_29 = State("BW-rand-29_initial_state")

# Define all blocks
state_BW_rand_29.blocks = {"b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8", "b9", "b10",
                    "b11", "b12", "b13", "b14", "b15", "b16", "b17", "b18", "b19", "b20",
                    "b21", "b22", "b23", "b24", "b25", "b26", "b27", "b28", "b29"}

# Set initial state from p13.hddl
state_BW_rand_29.on = {"b2":"b14", "b3":"b10", "b4":"b17", "b6":"b4", "b7":"b21", "b8":"b9", "b9":"b16",
                       "b11":"b29", "b12":"b23", "b13":"b25", "b14":"b20", "b15":"b6", "b16":"b1",
                       "b17":"b22", "b20":"b28", "b23":"b13", "b24":"b3", "b25":"b15", "b26":"b24",
                       "b27":"b11", "b28":"b26", "b29":"b8"}
state_BW_rand_29.ontable = {"b1", "b5", "b10", "b18", "b19", "b21", "b22"}
state_BW_rand_29.clear = {"b2", "b5", "b7", "b12", "b18", "b19", "b27"}
state_BW_rand_29.handempty = True
state_BW_rand_29.holding = None

# Set goal state from the :htn :ordered-subtasks in p13.hddl
htn_ordered_subtask_BW_rand_29 = Multigoal("goal-BW-rand-29", on= {"b1":"b16", "b13":"b1", "b14":"b13", "b29":"b20", "b27":"b29",
                                                    "b2":"b27", "b5":"b2", "b8":"b14", "b9":"b8", "b10":"b28", 
                                                    "b17":"b4", "b15":"b17", "b6":"b15", "b18":"b6", "b19":"b18", 
                                                    "b11":"b19", "b24":"b12", "b21":"b24", "b25":"b21", "b23":"b26",
                                                    "b22":"b23"})

# Set goal state from p13.hddl
goal_BW_rand_29 = {"b1":"b16", "b2":"b27", "b5":"b2", "b6":"b15", "b8":"b14", "b9":"b8", 
"b10":"b28", "b11":"b19", "b13":"b1", "b14":"b13", "b15":"b17", "b17":"b4", 
"b18":"b6", "b19":"b18", "b21":"b24", "b22":"b23", "b23":"b26", "b24":"b12", 
"b25":"b21", "b27":"b29"}

# ===== BW_rand_31 -------------------------------------------------- p14.hddl
state_BW_rand_31 = State("BW-rand-31_initial_state")

# Define all blocks
state_BW_rand_31.blocks = {"b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8", "b9", "b10",
                "b11", "b12", "b13", "b14", "b15", "b16", "b17", "b18", "b19", "b20",
                "b21", "b22", "b23", "b24", "b25", "b26", "b27", "b28", "b29", "b30",
                "b31"}




# Set initial state from p14.hddl
state_BW_rand_31.on = {"b3": "b4", "b4": "b1", "b6": "b15", "b7": "b16", "b8": "b7",
            "b9": "b14", "b10": "b25", "b11": "b28", "b12": "b3", "b13": "b17",
            "b14": "b11", "b15": "b13", "b16": "b31", "b17": "b19", "b18": "b12",
            "b19": "b8", "b20": "b30", "b21": "b27", "b22": "b9", "b23": "b20",
            "b24": "b10", "b25": "b18", "b26": "b24", "b27": "b22", "b28": "b26",
            "b29": "b5", "b31": "b29"}
state_BW_rand_31.ontable = {"b1", "b2", "b5", "b30"}
state_BW_rand_31.clear = {"b2", "b6", "b21", "b23"}
state_BW_rand_31.handempty = True
state_BW_rand_31.holding = None

# Set goal state from the :htn :ordered-subtasks in p14.hddl
htn_ordered_subtask_BW_rand_31 = Multigoal("goal-BW-rand-31", on= {"b15": "b12", "b23": "b15", "b16": "b23", "b22": "b16", 
                                                    "b25": "b22", "b21": "b25", "b17": "b21", "b31": "b17", 
                                                    "b20": "b31", "b7": "b20", "b3": "b7", "b28": "b3", 
                                                    "b27": "b28", "b29": "b27", "b4": "b29", "b18": "b10", 
                                                    "b8": "b18", "b14": "b8", "b11": "b13", "b24": "b11", 
                                                    "b19": "b24", "b26": "b2", "b30": "b5"})

# Set goal state from p14.hddl
goal_BW_rand_31 = {"b3":"b7", "b4":"b29", "b7":"b20", "b8":"b18", "b11":"b13", "b14":"b8", 
"b15":"b12", "b16":"b23", "b17":"b21", "b18":"b10", "b19":"b24", "b20":"b31", 
"b21":"b25", "b22":"b16", "b23":"b15", "b24":"b11", "b25":"b22", "b26":"b2", 
"b27":"b28", "b28":"b3", "b29":"b27", "b30":"b5"}

# ===== BW_rand_33 -------------------------------------------------- p15.hddl
state_BW_rand_33 = State("BW-rand-33_initial_state")

# Define all blocks
state_BW_rand_33.blocks = {"b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8", "b9", "b10",
                "b11", "b12", "b13", "b14", "b15", "b16", "b17", "b18", "b19", "b20",
                "b21", "b22", "b23", "b24", "b25", "b26", "b27", "b28", "b29", "b30",
                "b31", "b32", "b33"}  

# Set initial state from p15.hddl
state_BW_rand_33.on = {"b1":"b5", "b2":"b6", "b3":"b28", "b5":"b31", "b7":"b13", 
                       "b8":"b26", "b9":"b30", "b10":"b25", "b12":"b18", "b13":"b14", 
                       "b14":"b11", "b15":"b16", "b16":"b7", "b18":"b4", "b19":"b8", 
                       "b20":"b1", "b21":"b19", "b22":"b29", "b23":"b21", "b24":"b17", 
                       "b25":"b24", "b26":"b9", "b27":"b33", "b28":"b22", "b29":"b20", 
                       "b32":"b15", "b33":"b10"}
state_BW_rand_33.ontable = {"b4", "b6", "b11", "b17", "b30", "b31"}
state_BW_rand_33.clear = {"b2", "b3", "b12", "b23", "b27", "b32"}
state_BW_rand_33.handempty = True
state_BW_rand_33.holding = None
    
# Set goal state from the :htn :ordered-subtasks in p15.hddl
htn_ordered_subtask_BW_rand_33 = Multigoal("goal-BW-rand-33", on= {"b31":"b5", "b15":"b31", "b23":"b15", "b1":"b23", "b20":"b1", 
                                                    "b26":"b20", "b3":"b2", "b14":"b3", "b24":"b14", "b31":"b5", 
                                                    "b15":"b31", "b23":"b15", "b19":"b26", "b12":"b19", "b32":"b12", 
                                                    "b18":"b32", "b10":"b18", "b29":"b10", "b30":"b29", "b7":"b30", 
                                                    "b13":"b17", "b9":"b13", "b11":"b9", "b33":"b11", "b6":"b33", 
                                                    "b28":"b6", "b25":"b28", "b21":"b25", "b22":"b4", "b27":"b8"})

# Set goal state from p15.hddl
goal_BW_rand_33 = {"b1":"b23", "b3":"b2", "b6":"b33", "b7":"b30", "b9":"b13", "b10":"b18", 
"b11":"b9", "b12":"b19", "b13":"b17", "b14":"b3", "b15":"b31", "b18":"b32", 
"b19":"b26", "b20":"b1", "b21":"b25", "b22":"b4", "b23":"b15", "b24":"b14", 
"b25":"b28", "b26":"b20", "b27":"b8", "b28":"b6", "b29":"b10", "b30":"b29", 
"b31":"b5", "b32":"b12"}

# ===== BW_rand_35 -------------------------------------------------- p16.hddl
state_BW_rand_35 = State("BW-rand-35_initial_state")

# Define all blocks
state_BW_rand_35.blocks = {"b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8", "b9", "b10",
                "b11", "b12", "b13", "b14", "b15", "b16", "b17", "b18", "b19", "b20",
                "b21", "b22", "b23", "b24", "b25", "b26", "b27", "b28", "b29", "b30",
                "b31", "b32", "b33", "b34", "b35"}

# Set initial state from p16.hddl
state_BW_rand_35.on = {"b1":"b35", "b2":"b22", "b3":"b23", "b4":"b20", "b7":"b11",
                       "b8":"b6", "b10":"b3", "b11":"b21", "b12":"b27", "b13":"b26",
                       "b14":"b31", "b15":"b29", "b17":"b19", "b18":"b5", "b20":"b10",
                       "b21":"b18", "b22":"b30", "b23":"b34", "b24":"b4", "b25":"b12",
                       "b26":"b33", "b27":"b28", "b28":"b14", "b29":"b32", "b30":"b13",
                       "b31":"b8", "b32":"b25", "b33":"b15", "b34":"b16", "b35":"b9"}
state_BW_rand_35.ontable = {"b5", "b6", "b9", "b16", "b19"}
state_BW_rand_35.clear = {"b1", "b2", "b7", "b17", "b24"}
state_BW_rand_35.handempty = True
state_BW_rand_35.holding = None

# Set goal state from the :htn :ordered-subtasks in p16.hddl
htn_ordered_subtask_BW_rand_35 = Multigoal("goal-BW-rand-35", on= {"b29":"b14", "b26":"b29", "b8":"b26", "b32":"b8", "b13":"b32", 
                                                    "b2":"b13", "b1":"b2", "b24":"b1", "b30":"b24", "b18":"b21", 
                                                    "b10":"b18", "b20":"b10", "b34":"b20", "b23":"b9", "b17":"b23", 
                                                    "b27":"b17", "b12":"b27", "b35":"b12", "b15":"b35", "b16":"b33", 
                                                    "b28":"b16", "b4":"b5", "b3":"b4", "b31":"b3", "b19":"b31", 
                                                    "b7":"b19", "b11":"b7", "b25":"b11", "b22":"b25"})


# Set goal state from p16.hddl
goal_BW_rand_35 = {"b1":"b2", "b2":"b13", "b3":"b4", "b4":"b5", "b7":"b19", "b8":"b26", "b10":"b18", 
"b11":"b7", "b12":"b27", "b13":"b32", "b15":"b35", "b16":"b33", "b17":"b23", 
"b18":"b21", "b19":"b31", "b20":"b10", "b22":"b25", "b23":"b9", "b24":"b1", 
"b25":"b11", "b26":"b29", "b27":"b17", "b28":"b16", "b29":"b14", "b30":"b24", 
"b31":"b3", "b32":"b8", "b34":"b20"}

# ===== BW_rand_37 -------------------------------------------------- p17.hddl
state_BW_rand_37 = State("BW-rand-37_initial_state")

# Define all blocks
state_BW_rand_37.blocks = {"b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8", "b9", "b10",
                "b11", "b12", "b13", "b14", "b15", "b16", "b17", "b18", "b19", "b20",
                "b21", "b22", "b23", "b24", "b25", "b26", "b27", "b28", "b29", "b30",
                "b31", "b32", "b33", "b34", "b35", "b36", "b37"}

# Set initial state from p17.hddl
state_BW_rand_37.on = {"b1":"b25", "b2":"b27", "b3":"b32", "b4":"b26", "b5":"b21", "b6":"b4",
                       "b7":"b12", "b8":"b30", "b9":"b17", "b10":"b3", "b11":"b14", "b12":"b1",
                       "b13":"b6", "b14":"b13", "b15":"b2", "b16":"b34", "b17":"b24", "b18":"b9",
                       "b19":"b33", "b20":"b15", "b22":"b19", "b23":"b20", "b24":"b10", "b25":"b16",
                       "b26":"b23", "b27":"b22", "b28":"b7", "b31":"b5", "b33":"b18", "b35":"b36", "b37":"b29"}
state_BW_rand_37.ontable = {"b21", "b29", "b30", "b32", "b34", "b36"}
state_BW_rand_37.clear = {"b8", "b11", "b28", "b31", "b35", "b37"}
state_BW_rand_37.handempty = True
state_BW_rand_37.holding = None

# Set goal state from the :htn :ordered-subtasks in p17.hddl
htn_ordered_subtask_BW_rand_37 = Multigoal("goal-BW-rand-37", on= {"b1":"b30", "b21":"b1", "b26":"b21", "b37":"b32",
                                                    "b27":"b37", "b5":"b27", "b8":"b5", "b11":"b8",
                                                    "b17":"b11", "b36":"b17", "b22":"b36", "b2":"b22",
                                                    "b18":"b7", "b16":"b18", "b10":"b16", "b28":"b10",
                                                    "b13":"b28", "b6":"b13", "b34":"b6", "b29":"b34",
                                                    "b20":"b29", "b14":"b20", "b12":"b14", "b9":"b12",
                                                    "b23":"b9", "b15":"b23", "b35":"b15", "b19":"b35",
                                                    "b4":"b19", "b3":"b4", "b25":"b3", "b33":"b25",
                                                    "b24":"b31"})

# Set goal state from p17.hddl
goal_BW_rand_37 = {"b1":"b30", "b2":"b22", "b3":"b4", "b4":"b19", "b5":"b27", "b6":"b13", 
"b8":"b5", "b9":"b12", "b10":"b16", "b11":"b8", "b12":"b14", "b13":"b28", 
"b14":"b20", "b15":"b23", "b16":"b18", "b17":"b11", "b18":"b7", "b19":"b35", 
"b20":"b29", "b21":"b1", "b22":"b36", "b23":"b9", "b24":"b31", "b25":"b3", 
"b26":"b21", "b27":"b37", "b28":"b10", "b29":"b34", "b33":"b25", "b34":"b6", 
"b35":"b15", "b36":"b17"}

# ===== BW_rand_39 -------------------------------------------------- p18.hddl
state_BW_rand_39 = State("BW-rand-39_initial_state")

# Define all blocks
state_BW_rand_39.blocks = {"b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8", "b9", "b10",
                "b11", "b12", "b13", "b14", "b15", "b16", "b17", "b18", "b19", "b20",
                "b21", "b22", "b23", "b24", "b25", "b26", "b27", "b28", "b29", "b30",
                "b31", "b32", "b33", "b34", "b35", "b36", "b37", "b38", "b39"}

# Set initial state from p18.hddl
state_BW_rand_39.on = {"b1":"b39", "b2":"b11", "b3":"b32", "b4":"b6", "b7":"b19", "b8":"b25", "b9":"b34",
                       "b10":"b3", "b11":"b30", "b12":"b8", "b13":"b38", "b14":"b4", "b16":"b24", "b17":"b22",
                       "b18":"b23", "b19":"b2", "b20":"b26", "b21":"b1", "b23":"b7", "b24":"b29", "b25":"b31",
                       "b26":"b35", "b27":"b5", "b28":"b17", "b29":"b14", "b30":"b15", "b31":"b36", "b32":"b13",
                       "b33":"b12", "b34":"b33", "b35":"b18", "b38":"b27"}
state_BW_rand_39.ontable = {"b5", "b6", "b15", "b22", "b36", "b37", "b39"}
state_BW_rand_39.clear = {"b9", "b10", "b16", "b20", "b21", "b28", "b37"}
state_BW_rand_39.handempty = True
state_BW_rand_39.holding = None

# Set goal state from the :htn :ordered-subtasks in p18.hddl
htn_ordered_subtask_BW_rand_39 = Multigoal("goal-BW-rand-39", on= {"b15":"b36", "b21":"b15", "b27":"b21", "b3":"b27",
                                                    "b22":"b3", "b13":"b22", "b37":"b13", "b6":"b37", 
                                                    "b9":"b6", "b11":"b9", "b25":"b11", "b17":"b25",
                                                    "b31":"b17", "b14":"b31", "b10":"b14", "b18":"b10", 
                                                    "b1":"b18", "b32":"b1", "b33":"b32", "b4":"b33",
                                                    "b12":"b4", "b26":"b8", "b19":"b26", "b30":"b19", 
                                                    "b24":"b30", "b5":"b24", "b28":"b5", "b16":"b29",
                                                    "b39":"b35", "b20":"b39", "b2":"b20", "b7":"b2", 
                                                    "b34":"b7", "b23":"b34"})

# Set goal state from p18.hddl
goal_BW_rand_39 = {"b1":"b18", "b2":"b20", "b3":"b27", "b4":"b33", "b5":"b24", "b6":"b37", 
"b7":"b2", "b9":"b6", "b10":"b14", "b11":"b9", "b12":"b4", "b13":"b22", 
"b14":"b31", "b15":"b36", "b16":"b29", "b17":"b25", "b18":"b10", "b19":"b26", 
"b20":"b39", "b21":"b15", "b22":"b3", "b23":"b34", "b24":"b30", "b25":"b11", 
"b26":"b8", "b27":"b21", "b28":"b5", "b30":"b19", "b31":"b17", "b32":"b1", 
"b33":"b32", "b34":"b7", "b37":"b13"}

# ===== BW_rand_41 -------------------------------------------------- p19.hddl
state_BW_rand_41 = State("BW-rand-41_initial_state")

#define all blocks
state_BW_rand_41.blocks = {"b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8", "b9", "b10",
                           "b11", "b12", "b13", "b14", "b15", "b16", "b17", "b18", "b19", "b20",
                           "b21", "b22", "b23", "b24", "b25", "b26", "b27", "b28", "b29", "b30",
                           "b31", "b32", "b33", "b34", "b35", "b36", "b37", "b38", "b39", "b40",
                           "b41"}

# Set initial state from p19.hddl
state_BW_rand_41.on = {"b1":"b4", "b2":"b36", "b3":"b2", "b4":"b10", "b5":"b25", "b6":"b40", "b7":"b31", "b8":"b37", 
                       "b9":"b18", "b10":"b23", "b11":"b24", "b12":"b32", "b13":"b39", "b14":"b16", "b15":"b14",
                       "b19":"b38", "b23":"b3", "b24":"b29", "b25":"b1", "b26":"b12", "b27":"b20", "b28":"b19",
                       "b29":"b13", "b32":"b34", "b33":"b15", "b34":"b11", "b35":"b7", "b36":"b30", "b37":"b33",
                       "b38":"b21", "b39":"b41", "b40":"b17", "b41":"b22"}

state_BW_rand_41.ontable = {"b16", "b17", "b18", "b20", "b21", "b22", "b30", "b31"}
state_BW_rand_41.clear = {"b5", "b6", "b8", "b9", "b26", "b27", "b28", "b35"}
state_BW_rand_41.handempty = True
state_BW_rand_41.holding = None

# Set goal state from the :htn :ordered-subtasks in p19.hddl
htn_ordered_subtask_BW_rand_41 = Multigoal("goal-BW-rand-41", on= {"b36":"b21", "b35":"b36", "b2":"b35", "b29":"b2", "b3":"b29", 
                                                    "b33":"b3", "b38":"b33", "b14":"b38", "b31":"b14", "b1":"b31", 
                                                    "b18":"b1", "b34":"b18", "b23":"b24", "b26":"b23", "b28":"b26", 
                                                    "b30":"b28", "b39":"b30", "b5":"b39", "b4":"b5", "b15":"b4",
                                                    "b6":"b10", "b7":"b6", "b11":"b7", "b19":"b11", "b20":"b19",
                                                    "b36":"b21", "b25":"b34", "b27":"b25", "b41":"b27", "b17":"b41",
                                                    "b32":"b17", "b16":"b32", "b40":"b16", "b12":"b40", "b22":"b12",
                                                    "b13":"b9", "b37":"b8"})

# Set goal state from p19.hddl
goal_BW_rand_41 = {"b1":"b31", "b2":"b35", "b3":"b29", "b4":"b5", "b5":"b39", "b6":"b10", "b7":"b6", 
"b11":"b7", "b12":"b40", "b13":"b9", "b14":"b38", "b15":"b4", "b16":"b32", 
"b17":"b41", "b18":"b1", "b19":"b11", "b20":"b19", "b22":"b12", "b23":"b24", 
"b25":"b34", "b26":"b23", "b27":"b25", "b28":"b26", "b29":"b2", "b30":"b28", 
"b31":"b14", "b32":"b17", "b33":"b3", "b34":"b18", "b35":"b36", "b36":"b21", 
"b37":"b8", "b38":"b33", "b39":"b30", "b40":"b16"}

# ===== BW_rand_43 -------------------------------------------------- p20.hddl
state_BW_rand_43 = State("BW-rand-43_initial_state")

#define all blocks
state_BW_rand_43.blocks = {"b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8", "b9", "b10",
                           "b11", "b12", "b13", "b14", "b15", "b16", "b17", "b18", "b19", "b20",
                           "b21", "b22", "b23", "b24", "b25", "b26", "b27", "b28", "b29", "b30",
                           "b31", "b32", "b33", "b34", "b35", "b36", "b37", "b38", "b39", "b40",
                           "b41", "b43"}

# Set initial state from p20.hddl
state_BW_rand_43.on = {"b1":"b2", "b2":"b5", "b3":"b22", "b5":"b8", "b6":"b35", "b7":"b28", "b8":"b9", "b9":"b23", 
                       "b10":"b16", "b12":"b32", "b13":"b38", "b14":"b21", "b15":"b25", "b16":"b1", "b17":"b26",
                       "b18":"b6", "b19":"b12", "b20":"b42", "b21":"b10", "b22":"b20", "b24":"b17", "b26":"b13",
                       "b27":"b33", "b28":"b30", "b29":"b34", "b31":"b41", "b32":"b37", "b33":"b40", "b34":"b24",
                       "b35":"b4", "b36":"b14", "b37":"b15", "b39":"b18", "b41":"b43"}

state_BW_rand_43.ontable = {"b4", "b11", "b23", "b25", "b30", "b38", "b40", "b42", "b43"}
state_BW_rand_43.clear = {"b3", "b7", "b11", "b19", "b27", "b29", "b31", "b36", "b39"}
state_BW_rand_43.handempty = True
state_BW_rand_43.holding = None

# Set goal state from the :htn :ordered-subtasks in p20.hddl
htn_ordered_subtask_BW_rand_43 = Multigoal("goal-BW-rand-43", on= {"b40":"b38", "b18":"b40", "b1":"b18", "b23":"b6", "b16":"b23",
                                                    "b41":"b16", "b29":"b41", "b15":"b29", "b34":"b26", "b4":"b34",
                                                    "b31":"b4", "b2":"b31", "b33":"b2", "b13":"b33", "b21":"b14",
                                                    "b22":"b27", "b7":"b22", "b12":"b7", "b32":"b12", "b25":"b32",
                                                    "b35":"b20", "b3":"b35", "b8":"b3", "b30":"b8", "b11":"b30",
                                                    "b24":"b11", "b37":"b24", "b36":"b37"})

# Set goal state from p20.hddl
goal_BW_rand_43 = {"b1":"b18", "b2":"b31", "b3":"b35", "b4":"b34", "b5":"b15", "b7":"b22", 
"b8":"b3", "b9":"b39", "b10":"b17", "b11":"b30", "b12":"b7", "b13":"b33", 
"b15":"b29", "b16":"b23", "b17":"b42", "b18":"b40", "b19":"b5", "b21":"b14", 
"b22":"b27", "b23":"b6", "b24":"b11", "b25":"b32", "b28":"b9", "b29":"b41", 
"b30":"b8", "b31":"b4", "b32":"b12", "b33":"b2", "b34":"b26", "b35":"b20", 
"b36":"b37", "b37":"b24", "b39":"b43", "b40":"b38", "b41":"b16"}

# ============================================================================
# END OF FILE
# ============================================================================