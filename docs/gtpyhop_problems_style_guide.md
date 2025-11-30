# GTPyhop 1.6.0+ Problems Style Guide

## How to Write Problem Files (Initial States and Goal Tasks) for GTPyhop 1.6.0+ (LibCST-Compatible Format)

**Version**: 1.0.0
**Target Audience**: Domain developers writing GTPyhop 1.6.0+ problem files
**Purpose**: Enable automated extraction of state properties and problem metadata using Meta's LibCST tool for database ingestion

---

## Table of Contents

1. [Introduction and Purpose](#1-introduction-and-purpose)
2. [File Structure Overview](#2-file-structure-overview)
3. [Problem Definition Structure](#3-problem-definition-structure)
4. [Naming Conventions](#4-naming-conventions)
5. [Documentation Requirements](#5-documentation-requirements)
6. [Comment Marker Conventions for LibCST](#6-comment-marker-conventions-for-libcst)
7. [State Property Organization](#7-state-property-organization)
8. [Complete Working Examples](#8-complete-working-examples)
9. [Common Patterns](#9-common-patterns)
10. [Anti-patterns](#10-anti-patterns)
11. [Validation Checklist](#11-validation-checklist)
12. [BNF Grammar Specification](#12-bnf-grammar-specification)

---

## 1. Introduction and Purpose

This style guide defines **mandatory conventions** for writing GTPyhop 1.6.0+ problem files (`problems.py`). Following these conventions enables:

1. **Automated parsing** using Meta's LibCST tool
2. **Database ingestion** of problem definitions and state configurations
3. **Consistency** across domain implementations
4. **Validation** of problem file correctness before runtime

### Scope

This guide covers:
- **Problem Files**: Files defining initial states and goal tasks for planning
- **Scenario Definitions**: Individual problem instances with specific configurations
- **State Initialization**: Setting initial state properties

### Reference Files

This guide is derived from analysis of:
- `tnf_cancer_modelling/problems.py` (1 scenario)
- `cross_server/problems.py` (2 scenarios)
- `bio_opentrons/problems.py` (6 scenarios)
- `omega_hdq_dna_bacteria_flex_96_channel/problems.py` (3 scenarios)

---

## 2. File Structure Overview

### 2.1 Required File Sections

A compliant `problems.py` file MUST contain these sections in order:

| Section | Purpose | Required |
|---------|---------|----------|
| **Module Docstring** | File description with generation date | ✅ Yes |
| **Imports** | GTPyhop and standard library imports | ✅ Yes |
| **Helper Functions** | Factory functions for state creation (if needed) | ⚠️ Optional |
| **Problem Section** | Contains Domain and Initial State markers | ✅ Yes |
| **Problems Dictionary** | Mapping of scenario IDs to (state, tasks, description) | ✅ Yes |
| **get_problems() Function** | Returns problems dictionary for benchmarking | ✅ Yes |

### 2.2 File Organization Template

```python
"""
Problem definitions for the [Domain Name] example.
-- Generated YYYY-MM-DD

This file defines initial states for [workflow description].
The workflow demonstrates coordination between [N] MCP servers:
  - Server 1 (name): Description
  - Server 2 (name): Description
  ...
"""

import sys
import os

# Secure GTPyhop import strategy
try:
    import gtpyhop
    from gtpyhop import State
except ImportError:
    # Fallback to local development
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
        import gtpyhop
        from gtpyhop import State
    except ImportError as e:
        print(f"Error: Could not import gtpyhop: {e}")
        print("Please install gtpyhop using: pip install gtpyhop")
        sys.exit(1)


# ============================================================================
# HELPER FUNCTION (optional)
# ============================================================================

def create_base_state(name: str) -> State:
    """Create a base state with common properties."""
    state = State(name)
    # ... initialize common properties ...
    return state


# ============================================================================
# PROBLEM
# ============================================================================

# BEGIN: Domain: domain_name

# BEGIN: Initial State: state_name_1
# ===== [SCENARIO 1] Description -> N actions ================================
initial_state_scenario_1 = create_base_state('state_name_1')
initial_state_scenario_1.property = value
# END: Initial State

# BEGIN: Initial State: state_name_2
# ===== [SCENARIO 2] Description -> N actions ================================
initial_state_scenario_2 = create_base_state('state_name_2')
initial_state_scenario_2.property = different_value
# END: Initial State

# END: Domain


# ============================================================================
# PROBLEM DEFINITIONS FOR BENCHMARKING
# ============================================================================

# Each problem is a tuple of (initial_state, task_list, description)
problems = {
    'scenario_1_name': (
        initial_state_scenario_1,
        [('m_top_level_method', arg1, arg2)],
        'Description -> N actions'
    ),
    'scenario_2_name': (
        initial_state_scenario_2,
        [('m_top_level_method',)],
        'Description -> N actions'
    )
}


def get_problems():
    """
    Return all problem definitions for benchmarking.

    Returns:
        Dictionary mapping problem IDs to (state, tasks, description) tuples.
    """
    return problems
```

---

## 3. Problem Definition Structure

### 3.1 Scenario Definition Components

Each scenario requires these components:

| Component | Description | Example |
|-----------|-------------|---------|
| **BEGIN Marker** | LibCST extraction marker | `# BEGIN: Initial State: state_name` |
| **Scenario Header** | Visual separator with scenario number | `# ===== [SCENARIO N] Description ===` |
| **State Creation** | State object instantiation | `initial_state_scenario_N = State('name')` |
| **Property Assignment** | State property initialization | `state.property = value` |
| **END Marker** | Closes the Initial State block | `# END: Initial State` |

### 3.2 Problem Dictionary Entry

Each entry in the `problems` dictionary is a 3-tuple:

```python
'scenario_key': (
    initial_state_object,           # State object
    [('task_name', arg1, arg2)],    # Goal task list
    'Human-readable description'     # Description with expected plan length
)
```

---

## 4. Naming Conventions

### 4.1 Scenario Variable Names

**Pattern**: `initial_state_scenario_N_descriptor`

| Component | Convention | Example |
|-----------|------------|---------|
| Prefix | `initial_state_` | `initial_state_` |
| Scenario Number | `scenario_N` | `scenario_1`, `scenario_2` |
| Descriptor | `_descriptor` (optional) | `_standard`, `_dry_run`, `_4samples` |

**Examples**:
- `initial_state_scenario_1`
- `initial_state_scenario_1_standard`
- `initial_state_scenario_2_dry_run`
- `initial_state_scenario_3_16samples`

### 4.2 State Name Strings

**Pattern**: `domain_variant` or `descriptive_name`

**Examples**:
- `'hdq_standard'`
- `'hdq_dry_run'`
- `'pcr_4samples_25cycles'`
- `'cross_server_pick_and_place'`

### 4.3 Problem Dictionary Keys

**Pattern**: `scenario_N_descriptor`

**Examples**:
- `'scenario_1_standard'`
- `'scenario_2_dry_run'`
- `'scenario_1_4samples'`

---

## 5. Documentation Requirements

### 5.1 Module Docstring Requirements

| Element | Required | Description |
|---------|----------|-------------|
| **Title** | ✅ Yes | "Problem definitions for the [Domain] example." |
| **Generation Date** | ✅ Yes | "-- Generated YYYY-MM-DD" |
| **Description** | ✅ Yes | Brief workflow description |
| **Server List** | ⚠️ If applicable | MCP servers involved |
| **Scenario List** | ✅ Yes | All scenarios with expected plan lengths |

### 5.2 Scenario Documentation

Each scenario MUST include:

1. **BEGIN/END Markers** for LibCST extraction
2. **[SCENARIO N] prefix** in the header comment
3. **Expected plan length** in the description

---

## 6. Comment Marker Conventions for LibCST

### 6.1 Domain Markers

```python
# BEGIN: Domain: domain_name
# ... all scenarios ...
# END: Domain
```

### 6.2 Initial State Markers

```python
# BEGIN: Initial State: state_name
# ===== [SCENARIO N] Description -> N actions ================================
initial_state_scenario_N = State('state_name')
initial_state_scenario_N.property = value
# END: Initial State
```

### 6.3 Marker Syntax Rules

| Rule | Description |
|------|-------------|
| **Exact format** | `# BEGIN: ` and `# END: ` with space after colon |
| **Domain name** | Must match directory name exactly |
| **State name** | Must match State constructor argument |
| **No nesting** | Initial State blocks cannot be nested |

---

## 7. State Property Organization

### 7.1 Property Categories

Organize state properties by category using comment blocks:

```python
state = State('name')

# ========================================
# Category 1: Description
# ========================================
state.property_1a = value
state.property_1b = value

# ========================================
# Category 2: Description
# ========================================
state.property_2a = value
```

### 7.2 Common Property Categories

| Category | Examples |
|----------|----------|
| **Server/Hardware State** | `server_ready`, `gripper_state`, `module_available` |
| **Object Locations** | `object_location`, `labware_position` |
| **Volumes/Quantities** | `sample_vol`, `num_cycles`, `num_washes` |
| **Configuration Flags** | `dry_run`, `tip_mixing`, `protocol_type` |
| **Tracking State** | `well_contents`, `tips_used`, `current_step` |

---

## 8. Complete Working Examples

### 8.1 Simple Problem File (1 scenario)

```python
"""
Problem definitions for the TNF Cancer Modeling example.
-- Generated 2025-11-26

This file defines initial states for the multiscale TNF cancer modeling workflow.
"""

import sys
import os

try:
    import gtpyhop
    from gtpyhop import State
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
    import gtpyhop
    from gtpyhop import State

# ============================================================================
# PROBLEM
# ============================================================================

# BEGIN: Domain: tnf_cancer_modelling

# BEGIN: Initial State: multiscale_cancer_initial
# ===== [SCENARIO 1] Multiscale TNF Cancer Modeling --------------------------
initial_state_scenario_1 = State('multiscale_cancer_initial')
initial_state_scenario_1.tnf_gene_list = ["TNF", "TNFR1", "NFKB1"]
initial_state_scenario_1.omnipath_available = True
# END: Initial State

# END: Domain


problems = {
    'scenario_1_multiscale': (
        initial_state_scenario_1,
        [('m_run_multiscale_workflow',)],
        'Multiscale TNF cancer modeling workflow'
    )
}


def get_problems():
    """Return all problem definitions for benchmarking."""
    return problems
```

---

## 9. Common Patterns

### 9.1 Factory Function Pattern

Use when scenarios share common base properties:

```python
def create_base_state(name: str) -> State:
    state = State(name)
    # Common initialization
    return state

initial_state_scenario_1 = create_base_state('variant_1')
initial_state_scenario_1.variant_property = 'value_1'

initial_state_scenario_2 = create_base_state('variant_2')
initial_state_scenario_2.variant_property = 'value_2'
```

### 9.2 Configuration Override Pattern

Start with defaults, override specific properties:

```python
# Scenario 1: All defaults
initial_state_scenario_1 = create_base_state('standard')

# Scenario 2: Override specific settings
initial_state_scenario_2 = create_base_state('custom')
initial_state_scenario_2.dry_run = True
initial_state_scenario_2.num_washes = 1
```

---

## 10. Anti-patterns

### 10.1 Missing LibCST Markers

```python
# ❌ INCORRECT - No BEGIN/END markers
initial_state_scenario_1 = State('test')
initial_state_scenario_1.value = 1

# ✅ CORRECT - Proper markers
# BEGIN: Initial State: test
initial_state_scenario_1 = State('test')
initial_state_scenario_1.value = 1
# END: Initial State
```

### 10.2 Inconsistent Naming

```python
# ❌ INCORRECT - Inconsistent patterns
state1 = State('first')
second_state = State('second')

# ✅ CORRECT - Consistent pattern
initial_state_scenario_1 = State('first')
initial_state_scenario_2 = State('second')
```

### 10.3 Incorrect problems Dictionary Format

```python
# ❌ INCORRECT - Missing description
problems = {
    'scenario_1': (initial_state_scenario_1, [('task',)])
}

# ✅ CORRECT - (state, tasks, description)
problems = {
    'scenario_1': (initial_state_scenario_1, [('task',)], 'Description')
}
```

---

## 11. Validation Checklist

### 11.1 File Structure
- [ ] Module docstring with generation date present
- [ ] GTPyhop import with fallback strategy
- [ ] `problems` dictionary defined
- [ ] `get_problems()` function defined

### 11.2 Domain Markers
- [ ] `# BEGIN: Domain: domain_name` present
- [ ] `# END: Domain` present (after all scenarios)
- [ ] Domain name matches directory name

### 11.3 Each Scenario
- [ ] `# BEGIN: Initial State: state_name` present
- [ ] `# ===== [SCENARIO N]` header with description
- [ ] State variable follows naming pattern
- [ ] `# END: Initial State` present
- [ ] Entry in `problems` dictionary with 3-tuple format

---

## 12. BNF Grammar Specification

### 12.1 Problem File Grammar (EBNF)

```ebnf
problem_file        = docstring imports [helper_functions] problem_section
                      problems_dict get_problems_func ;

docstring           = '"""' file_description gen_date workflow_desc '"""' ;
gen_date            = "-- Generated" DATE NEWLINE ;

domain_block        = domain_begin {initial_state_block} domain_end ;
domain_begin        = "# BEGIN: Domain:" domain_name NEWLINE ;
domain_end          = "# END: Domain" NEWLINE ;

initial_state_block = state_begin scenario_header state_creation
                      {property_assignment} state_end ;
state_begin         = "# BEGIN: Initial State:" state_name NEWLINE ;
state_end           = "# END: Initial State" NEWLINE ;
scenario_header     = "# ===== [SCENARIO" INTEGER "]" description "=" {N} NEWLINE ;

problems_dict       = "problems" "=" "{" {problem_entry ","} "}" ;
problem_entry       = STRING ":" "(" state_var "," task_list "," STRING ")" ;
task_list           = "[" {task_tuple ","} "]" ;
task_tuple          = "(" STRING {"," expression} ")" ;
```

### 12.2 Marker Grammar

```ebnf
domain_marker       = "# BEGIN: Domain:" SPACE domain_name
                    | "# END: Domain" ;

state_marker        = "# BEGIN: Initial State:" SPACE state_name
                    | "# END: Initial State" ;

scenario_marker     = "# ===== [SCENARIO" SPACE INTEGER "]"
                      SPACE description SPACE "=" {N} ;
```

---

*Document Version: 1.0.0*
*Generated: 2025-11-30*
*Based on analysis of: tnf_cancer_modelling/problems.py, cross_server/problems.py, bio_opentrons/problems.py, omega_hdq_dna_bacteria_flex_96_channel/problems.py*
