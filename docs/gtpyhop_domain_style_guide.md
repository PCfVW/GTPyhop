# GTPyhop 1.7.0+ Domain Style Guide

## How to Write Domain Files (Actions and Methods) for GTPyhop 1.7.0+ (LibCST-Compatible Format)

**Version**: 1.1.0
**Target Audience**: Domain developers writing GTPyhop 1.7.0+ domains
**Purpose**: Enable automated extraction of preconditions, effects, and metadata using Meta's LibCST tool for database ingestion

---

## Table of Contents

1. [Introduction and Purpose](#1-introduction-and-purpose)
2. [Overview: Actions vs. Methods](#2-overview-actions-vs-methods)
3. [Formal Template: Primitive Actions](#3-formal-template-primitive-actions)
4. [Formal Template: Methods](#4-formal-template-methods)
5. [Type Hint Requirements](#5-type-hint-requirements)
6. [Docstring Format Specification](#6-docstring-format-specification)
7. [Comment Marker Conventions for LibCST](#7-comment-marker-conventions-for-libcst)
8. [Metadata Tags: DATA and ENABLER](#8-metadata-tags-data-and-enabler)
9. [Complete Working Examples](#9-complete-working-examples)
10. [Common Mistakes and How to Avoid Them](#10-common-mistakes-and-how-to-avoid-them)
11. [Validation Checklist](#11-validation-checklist)
12. [BNF Grammar Specification](#12-bnf-grammar-specification)

---

## 1. Introduction and Purpose

This style guide defines **mandatory conventions** for writing GTPyhop 1.7.0+ domain files containing primitive actions and methods. Following these conventions enables:

1. **Automated parsing** using Meta's LibCST tool
2. **Database ingestion** of domain knowledge (preconditions, effects, parameters)
3. **Consistency** across domain implementations
4. **Validation** of domain correctness before runtime

### Scope

This guide covers:
- **Primitive Actions**: Functions that directly modify state (prefix: `a_`)
- **Methods**: Functions that decompose tasks into subtasks (prefix: `m_`)

### Reference Domains

This guide is derived from analysis of:
- `tnf_cancer_modelling/domain.py` (12 actions, 14 methods)
- `cross_server/domain.py` (9 actions, 6 methods)

---

## 2. Overview: Actions vs. Methods

### 2.1 Primitive Actions

**Definition**: Functions that directly modify the planning state and represent executable operations.

| Property | Requirement |
|----------|-------------|
| **Prefix** | `a_` (e.g., `a_open_gripper`) |
| **First Parameter** | `state: State` |
| **Return Type** | `Union[State, bool]` |
| **Return Values** | Modified `state` on success, `False` on failure |
| **State Modification** | Directly modifies state attributes |

### 2.2 Methods

**Definition**: Functions that decompose high-level tasks into sequences of subtasks (actions or other methods).

| Property | Requirement |
|----------|-------------|
| **Prefix** | `m_` (e.g., `m_pick_object`) |
| **First Parameter** | `state: State` |
| **Return Type** | `Union[List[Tuple], bool]` |
| **Return Values** | List of task tuples on success, `False` on failure |
| **State Modification** | **Never** modifies state directly |

---

## 3. Formal Template: Primitive Actions

### 3.1 Complete Action Template

```python
def a_action_name(state: State, param1: Type1, param2: Type2 = default) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: server_name:tool_name

    Action signature:
        a_action_name(state, param1, param2)

    Action parameters:
        param1: Description of first parameter
        param2: Description of second parameter (default: default_value)

    Action purpose:
        One-line description of what this action accomplishes

    Preconditions:
        - First precondition description (state.property_name)
        - Second precondition description (state.other_property)

    Effects:
        - First effect description (state.new_property) [TAG]
        - Second effect description (state.modified_property) [TAG]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(param1, Type1): return False
    if not isinstance(param2, Type2): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # Validate parameter values against state or domain constraints
    if not param1.strip(): return False  # Example: non-empty string check
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Semantic preconditions that check state properties
    if not (hasattr(state, 'required_property') and state.required_property):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Description of data effect
    state.data_property = computed_value

    # [ENABLER] Description of enabler effect - gates subsequent action
    state.enabler_property = True

    # [DATA] Workflow tracking
    state.current_workflow_step = "step_name"
    # END: Effects

    return state
```

### 3.2 Action Structure Breakdown

| Section | Purpose | LibCST Extraction |
|---------|---------|-------------------|
| **Type Checking** | Validate Python types of all parameters | Extract parameter types |
| **State-Type Checks** | Validate parameter values against constraints | Extract value constraints |
| **Preconditions** | Check required state properties | Extract precondition list |
| **Effects** | Modify state properties | Extract effect list with tags |

---

## 4. Formal Template: Methods

### 4.1 Complete Method Template

```python
def m_method_name(state: State, param1: Type1) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_method_name(state, param1)

    Method parameters:
        param1: Description of parameter

    Method auxiliary parameters:
        aux_param: Type (inferred from state or computed)

    Method purpose:
        One-line description of decomposition goal

    Preconditions:
        - First precondition (state.required_property)
        - Second precondition (state.other_property)

    Task decomposition:
        - task_1: Description of first subtask
        - task_2: Description of second subtask

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State):
        return False
    if not isinstance(param1, Type1):
        return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not param1.strip():
        return False
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    aux_param = getattr(state, 'source_property', None)
    if aux_param is None:
        return False
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    if not (hasattr(state, 'required_property') and state.required_property):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_first_action", param1),
        ("m_nested_method", aux_param),
        ("a_final_action",)
    ]
    # END: Task Decomposition
```

### 4.2 Method Structure Breakdown

| Section | Purpose | LibCST Extraction |
|---------|---------|-------------------|
| **Type Checking** | Validate Python types | Extract parameter types |
| **State-Type Checks** | Validate parameter values | Extract value constraints |
| **Auxiliary Parameter Inference** | Compute parameters from state | Extract state dependencies |
| **Preconditions** | Check required state properties | Extract precondition list |
| **Task Decomposition** | Return subtask list | Extract decomposition structure |

---

## 5. Type Hint Requirements

### 5.1 Mandatory Type Annotations

**All parameters and return types MUST be annotated.**

```python
# ✅ CORRECT: All types annotated
def a_move_arm(state: State, position: str, speed: float = 1.0) -> Union[State, bool]:

# ❌ INCORRECT: Missing type annotations
def a_move_arm(state, position, speed=1.0):
```

### 5.2 Standard Type Imports

```python
from typing import Optional, Union, List, Tuple, Dict
```

### 5.3 Common Type Patterns

| Parameter Type | Annotation | Example |
|----------------|------------|---------|
| State object | `State` | `state: State` |
| String | `str` | `name: str` |
| Integer | `int` | `count: int` |
| Float | `float` | `temperature: float` |
| Boolean | `bool` | `enabled: bool` |
| String list | `List[str]` | `items: List[str]` |
| Dictionary | `Dict[str, Any]` | `config: Dict[str, Any]` |
| Optional | `Optional[str]` | `label: Optional[str] = None` |

### 5.4 Return Type Patterns

```python
# Actions return State or False
def a_action(state: State, ...) -> Union[State, bool]:

# Methods return task list or False
def m_method(state: State, ...) -> Union[List[Tuple], bool]:
```

---

## 6. Docstring Format Specification

### 6.1 Required Docstring Sections for Actions

| Section | Required | Description |
|---------|----------|-------------|
| `Class:` | ✅ Yes | Always `Action` |
| `MCP_Tool:` | ✅ Yes | MCP server:tool mapping |
| `Action signature:` | ✅ Yes | Function signature |
| `Action parameters:` | ✅ Yes | Parameter descriptions |
| `Action purpose:` | ✅ Yes | One-line purpose |
| `Preconditions:` | ✅ Yes | State requirements (or "None") |
| `Effects:` | ✅ Yes | State modifications with tags |
| `Returns:` | ✅ Yes | Return value description |

### 6.2 Required Docstring Sections for Methods

| Section | Required | Description |
|---------|----------|-------------|
| `Class:` | ✅ Yes | Always `Method` |
| `Method signature:` | ✅ Yes | Function signature |
| `Method parameters:` | ✅ Yes | Parameter descriptions |
| `Method auxiliary parameters:` | ⚠️ If applicable | State-inferred parameters |
| `Method purpose:` | ✅ Yes | One-line purpose |
| `Preconditions:` | ✅ Yes | State requirements (or "None") |
| `Task decomposition:` | ✅ Yes | Subtask descriptions |
| `Returns:` | ✅ Yes | Return value description |

### 6.3 Docstring Formatting Rules

1. **One blank line** between sections
2. **Bullet points** use `-` prefix with 8-space indent
3. **State references** use `(state.property_name)` format
4. **Effect tags** use `[DATA]` or `[ENABLER]` suffix
5. **No trailing whitespace**

---

## 7. Comment Marker Conventions for LibCST

### 7.1 Mandatory Code Block Markers

These comment markers enable LibCST to extract structured information:

| Marker | Purpose | Required |
|--------|---------|----------|
| `# BEGIN: Type Checking` | Start of type validation block | ✅ Yes |
| `# END: Type Checking` | End of type validation block | ✅ Yes |
| `# BEGIN: State-Type Checks` | Start of value validation block | ✅ Yes |
| `# END: State-Type Checks` | End of value validation block | ✅ Yes |
| `# BEGIN: Preconditions` | Start of precondition checks | ✅ Yes |
| `# END: Preconditions` | End of precondition checks | ✅ Yes |
| `# BEGIN: Effects` | Start of state modifications (actions only) | ✅ Actions |
| `# END: Effects` | End of state modifications | ✅ Actions |
| `# BEGIN: Auxiliary Parameter Inference` | Start of parameter inference (methods) | ⚠️ If needed |
| `# END: Auxiliary Parameter Inference` | End of parameter inference | ⚠️ If needed |
| `# BEGIN: Task Decomposition` | Start of task list (methods only) | ✅ Methods |
| `# END: Task Decomposition` | End of task list | ✅ Methods |

### 7.2 Inline Effect Tags

Within the `# BEGIN: Effects` block, each state modification must be tagged:

```python
# BEGIN: Effects
# [DATA] Description of informational property
state.data_property = value

# [ENABLER] Description of gate property - enables next_action
state.gate_property = True
# END: Effects
```

### 7.3 Empty Block Convention

If a block has no content, include a comment explaining why:

```python
# BEGIN: Preconditions
# No preconditions for initialization action
# END: Preconditions
```

---

## 8. Metadata Tags: DATA and ENABLER

### 8.1 Tag Definitions

| Tag | Meaning | Usage |
|-----|---------|-------|
| `[DATA]` | Informational property | Stores computed values, file paths, configurations |
| `[ENABLER]` | Workflow gate property | Controls whether subsequent actions can execute |

### 8.2 ENABLER Tag Guidelines

**ENABLER properties act as workflow gates.** They:
- Are typically boolean (`True`/`False`) or status strings (`"completed"`, `"passed"`)
- Are checked in preconditions of subsequent actions
- Represent completion of critical workflow steps

```python
# [ENABLER] Network creation completed - gates a_remove_bimodal_interactions
state.network_creation_status = "completed"
```

### 8.3 DATA Tag Guidelines

**DATA properties store information.** They:
- Store computed values, file paths, lists, dictionaries
- May be used as parameters to subsequent actions
- Do not gate workflow progression directly

```python
# [DATA] Raw interaction network file path
state.raw_network_file = f"tnf_network_{organism}.sif"

# [DATA] Network components for validation
state.network_components = ["TNF_sensing", "apoptosis", "proliferation"]
```

### 8.4 Tag Placement in State Property Map

Document all state properties at the file level:

```python
# ============================================================================
# STATE PROPERTY MAP
# ----------------------------------------------------------------------------
# Legend:
#  - (E) Created/modified by the action (Effects)
#  - (P) Consumed/checked by the action (Preconditions/State checks)
#  - [ENABLER] Property acts as a workflow gate for subsequent steps
#  - [DATA]    Informational/data container
#
# Step 1: a_create_network
#  (P) gene_list [ENABLER]
#  (E) network_file: str [DATA]
#  (E) network_created: True [ENABLER]
# ============================================================================
```

---

## 9. Complete Working Examples

### 9.1 Complete Action Example

```python
def a_grasp_object(state: State, object_id: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: robot_server:grasp

    Action signature:
        a_grasp_object(state, object_id)

    Action parameters:
        object_id: ID of the object to grasp (e.g., 'block_a')

    Action purpose:
        Grasp an object with the robot gripper

    Preconditions:
        - Gripper is open (state.gripper_state == "open")
        - Arm is at object location (state.arm_position == state.object_location[object_id])
        - Not currently holding anything (state.holding is None)
        - Server 2 is ready (state.server_2_ready)

    Effects:
        - Object is now being held (state.holding) [DATA]
        - Object added to grasped objects list (state.grasped_objects) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(object_id, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not object_id.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # Server 2 must be ready
    if not (hasattr(state, 'server_2_ready') and state.server_2_ready):
        return False
    # Gripper must be open
    if not (hasattr(state, 'gripper_state') and state.gripper_state == "open"):
        return False
    # Must not be holding anything
    if hasattr(state, 'holding') and state.holding is not None:
        return False
    # Object must exist
    if not (hasattr(state, 'object_location') and object_id in state.object_location):
        return False
    # Arm must be at object location
    if not (hasattr(state, 'arm_position') and
            state.arm_position == state.object_location[object_id]):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Now holding the object
    state.holding = object_id

    # [DATA] Add to grasped objects list
    if not hasattr(state, 'grasped_objects'):
        state.grasped_objects = []
    if object_id not in state.grasped_objects:
        state.grasped_objects.append(object_id)
    # END: Effects

    return state
```

### 9.2 Complete Method Example

```python
def m_pick_object(state: State, object_id: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_pick_object(state, object_id)

    Method parameters:
        object_id: ID of the object to pick up

    Method auxiliary parameters:
        object_location: str (inferred from state.object_location[object_id])

    Method purpose:
        Decompose pick task into: move to object → open gripper → grasp → close → verify

    Preconditions:
        - Object exists in object_location (state.object_location[object_id])
        - Not currently holding anything (state.holding is None)

    Task decomposition:
        - a_move_arm_to_position: Move arm to object location
        - a_open_gripper: Open gripper for grasping
        - a_grasp_object: Grasp the target object
        - a_close_gripper: Close gripper to secure object
        - a_verify_grasp: Verify successful grasp

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(object_id, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not object_id.strip(): return False
    # END: State-Type Checks

    # BEGIN: Auxiliary Parameter Inference
    if not (hasattr(state, 'object_location') and object_id in state.object_location):
        return False
    object_location = state.object_location[object_id]
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    # Must not be holding anything
    if hasattr(state, 'holding') and state.holding is not None:
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_move_arm_to_position", object_location),
        ("a_open_gripper",),
        ("a_grasp_object", object_id),
        ("a_close_gripper",),
        ("a_verify_grasp",)
    ]
    # END: Task Decomposition
```

---

## 10. Common Mistakes and How to Avoid Them

### 10.1 Missing Type Annotations

```python
# ❌ INCORRECT
def a_move(state, position):
    ...

# ✅ CORRECT
def a_move(state: State, position: str) -> Union[State, bool]:
    ...
```

### 10.2 Missing Block Markers

```python
# ❌ INCORRECT - No markers
if not isinstance(state, State): return False
if not state.ready: return False
state.done = True
return state

# ✅ CORRECT - All markers present
# BEGIN: Type Checking
if not isinstance(state, State): return False
# END: Type Checking

# BEGIN: State-Type Checks
# No state-type checks needed
# END: State-Type Checks

# BEGIN: Preconditions
if not state.ready: return False
# END: Preconditions

# BEGIN: Effects
state.done = True
# END: Effects

return state
```

### 10.3 Missing Effect Tags

```python
# ❌ INCORRECT - No tags
# BEGIN: Effects
state.file_path = "output.txt"
state.ready = True
# END: Effects

# ✅ CORRECT - All effects tagged
# BEGIN: Effects
# [DATA] Output file path
state.file_path = "output.txt"

# [ENABLER] Ready for next step
state.ready = True
# END: Effects
```

### 10.4 Method Modifying State

```python
# ❌ INCORRECT - Methods must not modify state
def m_setup(state: State) -> Union[List[Tuple], bool]:
    state.initialized = True  # WRONG!
    return [("a_configure",)]

# ✅ CORRECT - Return task that modifies state
def m_setup(state: State) -> Union[List[Tuple], bool]:
    return [
        ("a_initialize",),  # This action sets initialized = True
        ("a_configure",)
    ]
```

### 10.5 Wrong Return Type

```python
# ❌ INCORRECT - Action returning list
def a_move(state: State, pos: str) -> Union[State, bool]:
    return [("subtask",)]  # WRONG! Actions return state or False

# ❌ INCORRECT - Method returning state
def m_plan(state: State) -> Union[List[Tuple], bool]:
    state.planned = True
    return state  # WRONG! Methods return list or False
```

### 10.6 Incomplete Docstring

```python
# ❌ INCORRECT - Missing required sections
def a_action(state: State) -> Union[State, bool]:
    """Does something."""  # Missing all required sections!

# ✅ CORRECT - All sections present
def a_action(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: server:tool

    Action signature:
        a_action(state)

    Action parameters:
        None

    Action purpose:
        Perform the action

    Preconditions:
        None (no preconditions)

    Effects:
        - Action completed (state.action_done) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
```

### 10.7 Missing Prefix in Task Decomposition

**CRITICAL**: Task names in method decompositions MUST include the appropriate prefix (`a_` for actions, `m_` for methods). GTPyhop uses these prefixes to locate the corresponding function definitions.

```python
# ❌ INCORRECT - Missing prefixes in task decomposition
def m_drug_discovery(state: State, disease: str) -> Union[List[Tuple], bool]:
    # BEGIN: Task Decomposition
    return [
        ("search_disease", disease),      # WRONG! Should be "a_search_disease"
        ("get_targets", disease),         # WRONG! Should be "a_get_targets"
        ("validate_targets",),            # WRONG! Should be "m_validate_targets"
        ("analyze_pathways",),            # WRONG! Should be "m_analyze_pathways"
    ]
    # END: Task Decomposition

# ✅ CORRECT - All task names include proper prefixes
def m_drug_discovery(state: State, disease: str) -> Union[List[Tuple], bool]:
    # BEGIN: Task Decomposition
    return [
        ("a_search_disease", disease),    # Action prefix: a_
        ("a_get_targets", disease),       # Action prefix: a_
        ("m_validate_targets",),          # Method prefix: m_
        ("m_analyze_pathways",),          # Method prefix: m_
    ]
    # END: Task Decomposition
```

**Why this matters**: Without the correct prefix, GTPyhop cannot find the task function and planning will fail silently or with cryptic errors. The planner iterates through registered actions and methods looking for exact name matches.

---

## 11. Validation Checklist

Use this checklist before committing any action or method:

### 11.1 Action Checklist

- [ ] Function name starts with `a_`
- [ ] First parameter is `state: State`
- [ ] Return type is `Union[State, bool]`
- [ ] All parameters have type annotations
- [ ] Docstring contains all 8 required sections
- [ ] `# BEGIN/END: Type Checking` markers present
- [ ] `# BEGIN/END: State-Type Checks` markers present
- [ ] `# BEGIN/END: Preconditions` markers present
- [ ] `# BEGIN/END: Effects` markers present
- [ ] All effects have `[DATA]` or `[ENABLER]` tags
- [ ] Returns `state` on success, `False` on failure
- [ ] Never modifies state before precondition checks pass

### 11.2 Method Checklist

- [ ] Function name starts with `m_`
- [ ] First parameter is `state: State`
- [ ] Return type is `Union[List[Tuple], bool]`
- [ ] All parameters have type annotations
- [ ] Docstring contains all required sections
- [ ] `# BEGIN/END: Type Checking` markers present
- [ ] `# BEGIN/END: State-Type Checks` markers present
- [ ] `# BEGIN/END: Auxiliary Parameter Inference` markers (if needed)
- [ ] `# BEGIN/END: Preconditions` markers present
- [ ] `# BEGIN/END: Task Decomposition` markers present
- [ ] Returns list of tuples on success, `False` on failure
- [ ] **Never** modifies state directly
- [ ] Task tuples use correct format: `("task_name", arg1, arg2)`
- [ ] **All task names include proper prefix** (`a_` for actions, `m_` for methods)

---

## 12. BNF Grammar Specification

### 12.1 Action Grammar (EBNF)

```ebnf
action_definition   = "def" action_name "(" parameters ")" "->" return_type ":" NEWLINE
                      INDENT docstring body DEDENT ;

action_name         = "a_" identifier ;

parameters          = state_param ["," param_list] ;
state_param         = "state" ":" "State" ;
param_list          = param {"," param} ;
param               = identifier ":" type_annotation ["=" default_value] ;

return_type         = "Union" "[" "State" "," "bool" "]" ;

docstring           = '"""' NEWLINE
                      class_section
                      mcp_tool_section
                      signature_section
                      parameters_section
                      purpose_section
                      preconditions_section
                      effects_section
                      returns_section
                      '"""' ;

class_section       = "Class:" "Action" NEWLINE ;
mcp_tool_section    = "MCP_Tool:" server_name ":" tool_name NEWLINE ;
signature_section   = "Action signature:" NEWLINE action_signature NEWLINE ;
parameters_section  = "Action parameters:" NEWLINE {param_desc NEWLINE} ;
purpose_section     = "Action purpose:" NEWLINE purpose_text NEWLINE ;
preconditions_section = "Preconditions:" NEWLINE {precond_item NEWLINE} ;
effects_section     = "Effects:" NEWLINE {effect_item NEWLINE} ;
returns_section     = "Returns:" NEWLINE return_desc NEWLINE ;

precond_item        = "-" precond_desc "(" state_reference ")" ;
effect_item         = "-" effect_desc "(" state_reference ")" "[" tag "]" ;
tag                 = "DATA" | "ENABLER" ;

body                = type_checking_block
                      state_type_block
                      preconditions_block
                      effects_block
                      "return" ("state" | "False") ;

type_checking_block = BEGIN_TYPE_CHECK {type_check} END_TYPE_CHECK ;
state_type_block    = BEGIN_STATE_TYPE {state_check} END_STATE_TYPE ;
preconditions_block = BEGIN_PRECOND {precond_check} END_PRECOND ;
effects_block       = BEGIN_EFFECTS {tagged_effect} END_EFFECTS ;

BEGIN_TYPE_CHECK    = "# BEGIN: Type Checking" NEWLINE ;
END_TYPE_CHECK      = "# END: Type Checking" NEWLINE ;
BEGIN_STATE_TYPE    = "# BEGIN: State-Type Checks" NEWLINE ;
END_STATE_TYPE      = "# END: State-Type Checks" NEWLINE ;
BEGIN_PRECOND       = "# BEGIN: Preconditions" NEWLINE ;
END_PRECOND         = "# END: Preconditions" NEWLINE ;
BEGIN_EFFECTS       = "# BEGIN: Effects" NEWLINE ;
END_EFFECTS         = "# END: Effects" NEWLINE ;

tagged_effect       = "# [" tag "]" effect_comment NEWLINE
                      state_assignment NEWLINE ;
```

### 12.2 Method Grammar (EBNF)

```ebnf
method_definition   = "def" method_name "(" parameters ")" "->" return_type ":" NEWLINE
                      INDENT docstring body DEDENT ;

method_name         = "m_" identifier ;

return_type         = "Union" "[" "List" "[" "Tuple" "]" "," "bool" "]" ;

docstring           = '"""' NEWLINE
                      class_section
                      signature_section
                      parameters_section
                      [aux_params_section]
                      purpose_section
                      preconditions_section
                      decomposition_section
                      returns_section
                      '"""' ;

class_section       = "Class:" "Method" NEWLINE ;
aux_params_section  = "Method auxiliary parameters:" NEWLINE {aux_param NEWLINE} ;
decomposition_section = "Task decomposition:" NEWLINE {task_item NEWLINE} ;

body                = type_checking_block
                      state_type_block
                      [aux_inference_block]
                      preconditions_block
                      task_decomposition_block ;

aux_inference_block = BEGIN_AUX_INFER {aux_assignment} END_AUX_INFER ;
task_decomposition_block = BEGIN_DECOMP "return" task_list END_DECOMP ;

BEGIN_AUX_INFER     = "# BEGIN: Auxiliary Parameter Inference" NEWLINE ;
END_AUX_INFER       = "# END: Auxiliary Parameter Inference" NEWLINE ;
BEGIN_DECOMP        = "# BEGIN: Task Decomposition" NEWLINE ;
END_DECOMP          = "# END: Task Decomposition" NEWLINE ;

task_list           = "[" task_tuple {"," task_tuple} "]" ;
task_tuple          = "(" task_name ["," arg_list] ")" ;
task_name           = '"' task_prefix identifier '"' ;
task_prefix         = "a_" | "m_" ;  (* MANDATORY: task names MUST have a_ or m_ prefix *)
arg_list            = expression {"," expression} ;
```

### 12.3 Type Annotation Grammar

```ebnf
type_annotation     = simple_type | generic_type | union_type | optional_type ;

simple_type         = "State" | "str" | "int" | "float" | "bool" | "None" ;

generic_type        = "List" "[" type_annotation "]"
                    | "Dict" "[" type_annotation "," type_annotation "]"
                    | "Tuple" "[" type_list "]" ;

union_type          = "Union" "[" type_annotation "," type_annotation "]" ;

optional_type       = "Optional" "[" type_annotation "]" ;

type_list           = type_annotation {"," type_annotation} ;
```

---

## Appendix A: File Organization Template

```python
# ============================================================================
# MCP Orchestration - Domain Name
# ============================================================================

# ============================================================================
# FILE ORGANIZATION
# ----------------------------------------------------------------------------
# This file is organized into the following sections:
#   - Imports (with secure path handling)
#   - Domain (1)
#   - State Property Map
#   - Actions (N)
#   - Methods (M)
# ============================================================================

# ============================================================================
# IMPORTS
# ============================================================================
import sys
import os
from typing import Optional, Union, List, Tuple, Dict

# ... import gtpyhop ...

# ============================================================================
# DOMAIN
# ============================================================================
the_domain = Domain("domain_name")
set_current_domain(the_domain)

# ============================================================================
# STATE PROPERTY MAP
# ----------------------------------------------------------------------------
# ... document all state properties ...
# ============================================================================

# ============================================================================
# ACTIONS (N)
# ----------------------------------------------------------------------------
# ... action definitions ...
# ============================================================================

# ============================================================================
# DECLARE ACTIONS TO DOMAIN
# ============================================================================
declare_actions(a_action1, a_action2, ...)

# ============================================================================
# METHODS (M)
# ----------------------------------------------------------------------------
# ... method definitions ...
# ============================================================================

# ============================================================================
# DECLARE METHODS TO DOMAIN
# ============================================================================
declare_task_methods('m_method1', m_method1)
declare_task_methods('m_method2', m_method2)

# ============================================================================
# END OF FILE
# ============================================================================
```

---

## Appendix B: Quick Reference Card

### Action Template (Minimal)

```python
def a_name(state: State, param: str) -> Union[State, bool]:
    """
    Class: Action
    MCP_Tool: server:tool
    Action signature: a_name(state, param)
    Action parameters: param: description
    Action purpose: What it does
    Preconditions: - condition (state.prop)
    Effects: - effect (state.prop) [TAG]
    Returns: Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(param, str): return False
    # END: Type Checking
    # BEGIN: State-Type Checks
    # END: State-Type Checks
    # BEGIN: Preconditions
    # END: Preconditions
    # BEGIN: Effects
    # [ENABLER] Done
    state.done = True
    # END: Effects
    return state
```

### Method Template (Minimal)

```python
def m_name(state: State, param: str) -> Union[List[Tuple], bool]:
    """
    Class: Method
    Method signature: m_name(state, param)
    Method parameters: param: description
    Method purpose: What it decomposes
    Preconditions: - condition (state.prop)
    Task decomposition: - a_task: description
    Returns: Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(param, str): return False
    # END: Type Checking
    # BEGIN: State-Type Checks
    # END: State-Type Checks
    # BEGIN: Preconditions
    # END: Preconditions
    # BEGIN: Task Decomposition
    return [("a_task", param)]
    # END: Task Decomposition
```

---

*Document Version: 1.0.0*
*Generated: 2025-11-30*
*Based on analysis of: tnf_cancer_modelling/domain.py, cross_server/domain.py*

