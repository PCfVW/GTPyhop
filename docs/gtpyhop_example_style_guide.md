# GTPyhop Example Style Guide

## How to Write Examples for GTPyhop

**Version**: 1.2.0
**Target Audience**: Developers creating new GTPyhop example domains

---

## 1. Folder Structure

Each example must follow this folder structure:

```
examples/
└── your-example-folder/           # Use kebab-case or snake_case
    ├── __init__.py                # Package initialization (REQUIRED)
    ├── domain.py                  # Domain definition (REQUIRED)
    ├── problems.py                # Problem definitions (REQUIRED)
    └── README.md                  # Documentation (REQUIRED)
```

For collections of related examples (e.g., benchmarks, orchestration):

```
examples/
└── example-collection/
    ├── __init__.py                # Optional for collection
    ├── benchmarking.py            # Shared benchmarking script
    ├── benchmarking_quickstart.md # Benchmarking documentation
    ├── README.md                  # Collection overview
    ├── example_one/
    │   ├── __init__.py
    │   ├── domain.py
    │   ├── problems.py
    │   └── README.md
    └── example_two/
        ├── __init__.py
        ├── domain.py
        ├── problems.py
        └── README.md
```

---

## 2. Required Files

### 2.1 `__init__.py` - Package Initialization

Every example package must export:
- `the_domain` - The domain object
- `get_problems()` - Function returning problem dictionary
- `GTPYHOP_SOURCE` - Import source indicator (`"pypi"` or `"local"`)

**Template:**

```python
"""
Your Example Domain for GTPyhop

Brief description of what this example demonstrates.
"""

import sys
import os
from typing import Dict, Tuple, List, Optional

# ============================================================================
# SMART GTPYHOP IMPORT STRATEGY
# ============================================================================

def safe_add_to_path(relative_path: str) -> Optional[str]:
    """Safely add a relative path to sys.path with validation."""
    base_path = os.path.dirname(os.path.abspath(__file__))
    target_path = os.path.normpath(os.path.join(base_path, relative_path))
    if not target_path.startswith(os.path.dirname(base_path)):
        raise ValueError(f"Path traversal detected: {target_path}")
    if os.path.exists(target_path) and target_path not in sys.path:
        sys.path.insert(0, target_path)
        return target_path
    return None

# Try PyPI installation first, fallback to local
try:
    import gtpyhop
    GTPYHOP_SOURCE = "pypi"
except ImportError:
    try:
        safe_add_to_path(os.path.join('..', '..', '..', '..'))
        import gtpyhop
        GTPYHOP_SOURCE = "local"
    except (ImportError, ValueError) as e:
        print(f"Error: Could not import gtpyhop: {e}")
        print("Please install gtpyhop using: pip install gtpyhop")
        sys.exit(1)

# ============================================================================
# IMPORT DOMAIN AND PROBLEMS
# ============================================================================

from . import domain
from . import problems

the_domain = domain.the_domain

# ============================================================================
# PROBLEM DISCOVERY FUNCTION
# ============================================================================

def get_problems() -> Dict[str, Tuple[gtpyhop.State, List[Tuple], str]]:
    """Return all problem definitions for benchmarking."""
    return problems.get_problems()

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = ['domain', 'problems', 'the_domain', 'get_problems', 'GTPYHOP_SOURCE']
```

### 2.2 `domain.py` - Domain Definition

See [gtpyhop_domain_style_guide.md](gtpyhop_domain_style_guide.md) for detailed conventions on writing actions and methods.

**Key points:**
- Use `# BEGIN:` / `# END:` markers to delimit code sections (Type Checking, Preconditions, Effects, etc.)
- Actions are prefixed with `a_`
- Methods are prefixed with `m_`
- Export `the_domain` at module level
- Use `declare_actions()` and `declare_task_methods()` to register

**Import Template (Graceful Degradation):**

The `domain.py` file should use a simplified import pattern that supports direct imports while relying on `__init__.py` for the authoritative import strategy:

```python
import sys
import os
from typing import Optional, Union, List, Tuple

# ============================================================================
# GTPYHOP IMPORT (with graceful degradation for direct imports)
# ============================================================================

try:
    import gtpyhop
    from gtpyhop import Domain, State, set_current_domain, declare_actions, declare_task_methods
except ImportError:
    # Graceful degradation: supports direct domain.py import (unsupported but functional)
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
    import gtpyhop
    from gtpyhop import Domain, State, set_current_domain, declare_actions, declare_task_methods

# ============================================================================
# DOMAIN
# ============================================================================
the_domain = Domain("your_domain_name")
set_current_domain(the_domain)
```

**Design Rationale:**
- The `__init__.py` contains the full import strategy with `safe_add_to_path()` and `GTPYHOP_SOURCE`
- `domain.py` uses graceful degradation: if imported via `__init__.py`, gtpyhop is already available; if imported directly (unsupported), a simple fallback is provided
- This avoids code duplication while maintaining functionality

### 2.3 `problems.py` - Problem Definitions

See [gtpyhop_problems_style_guide.md](gtpyhop_problems_style_guide.md) for detailed conventions on writing problem files.

**Key points:**
- Use unified scenario blocks with `# BEGIN: Scenario` / `# END: Scenario` markers
- Each problem is a tuple: `(state, tasks, description)`
- Export `get_problems()` function returning a dictionary

**Import Template (Graceful Degradation):**

```python
import sys
import os

# ============================================================================
# GTPYHOP IMPORT (with graceful degradation for direct imports)
# ============================================================================

try:
    import gtpyhop
    from gtpyhop import State
except ImportError:
    # Graceful degradation: supports direct problems.py import (unsupported but functional)
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
    import gtpyhop
    from gtpyhop import State
```

### 2.4 `README.md` - Documentation

Every example must include a README with:

1. **Overview** - What the example demonstrates
2. **Scenarios/Problems** - Table of available scenarios with expected results
3. **Domain Structure** - Actions and methods provided
4. **Usage Examples** - How to run the example
5. **File Structure** - Directory layout

**Template:**

```markdown
# Example Name

## Overview

Brief description of what this example demonstrates.

## Scenarios

| Scenario | Configuration | Actions | Status |
|----------|---------------|---------|--------|
| `scenario_1` | 4 items | 55 | Valid |
| `scenario_2` | 8 items | 79 | Valid |

## Domain Structure

### Actions
- `a_action_name` - Description

### Methods
- `m_method_name` - Description

## Usage

```python
from gtpyhop.examples.your_example import the_domain, get_problems

problems = get_problems()
state, tasks, desc = problems['scenario_1']
```

## File Structure

```
your_example/
├── __init__.py
├── domain.py
├── problems.py
└── README.md
```

---
*Generated YYYY-MM-DD*
```

---

## 3. Optional: Benchmarking Script

For example collections, include a shared `benchmarking.py`:

**Key requirements:**
- Import domains dynamically by name
- Support `--list-domains` or `--list-scenarios` option
- Use `PlannerSession` for thread-safe planning
- Print summary table with results

---

## 4. Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Example folder | kebab-case or snake_case | `bio_opentrons`, `ipc-2020-total-order` |
| Domain name | snake_case | `bio_opentrons_domain` |
| Action functions | `a_` prefix | `a_pick_up_tip` |
| Method functions | `m_` prefix | `m_transfer_samples` |
| State variables | `initial_state_scenario_N` | `initial_state_scenario_1` |
| Problem keys | `scenario_N` or descriptive | `scenario_1`, `scenario_1_dry_run` |

---

## 5. Checklist

Before submitting an example, verify:

- [ ] Folder contains `__init__.py`, `domain.py`, `problems.py`, `README.md`
- [ ] `__init__.py` exports `the_domain`, `get_problems()`, `GTPYHOP_SOURCE`
- [ ] `domain.py` follows [gtpyhop_domain_style_guide.md](gtpyhop_domain_style_guide.md)
- [ ] `problems.py` follows [gtpyhop_problems_style_guide.md](gtpyhop_problems_style_guide.md)
- [ ] `README.md` documents scenarios, domain structure, and usage
- [ ] Example runs successfully with `PlannerSession`
- [ ] All scenarios produce valid plans
- [ ] Doctests in `get_problems()` verify plan lengths and expected behavior (recommended)

---

## 6. Quick Start Template

To create a new example:

1. Create folder: `src/gtpyhop/examples/your_example/`
2. Copy files from an existing example (e.g., `bio_opentrons/`)
3. Replace domain logic in `domain.py`
4. Define scenarios in `problems.py`
5. Update `README.md`
6. Test: `python -c "from gtpyhop.examples.your_example import get_problems; print(get_problems())"`
7. Add doctests to `get_problems()` (see section 7)
8. Verify: `python -m doctest -v src/gtpyhop/examples/your_example/problems.py`

---

## 7. Doctests for Plan Verification

Add doctests to the `get_problems()` docstring in `problems.py` to verify that all scenarios produce correct plans. Doctests serve as both inline documentation and regression tests.

**What to test:**
- Plan success and plan length for each scenario
- Identity of key actions in the plan (e.g., which candidate was selected)
- Expected greedy planner failures for backtracking scenarios

**How to run:**

```bash
# Run doctests for a specific problems file
python -m doctest -v src/gtpyhop/examples/your_example/problems.py
```

**Conventions:**
- Suppress GTPyhop import messages with stdout redirection (they break doctest output matching)
- Use `verbose=0` in PlannerSession to prevent planner messages
- Pass `*probs['key'][:2]` to `find_plan` (slices off the description string)
- Add narrative text between test blocks explaining what each scenario verifies

See the [problems style guide](gtpyhop_problems_style_guide.md) (section 2.3) for the full pattern. All 7 poetry examples include doctests in `get_problems()` and can serve as reference implementations — from simple greedy plans (`structured_poetry`) to backtracking verification (`backtracking_poetry`, `replanning_poetry`) to feature injection checks (`feature_space_poetry`).

---

*Document Version: 1.2.0*
*Updated: 2026-02-18*
