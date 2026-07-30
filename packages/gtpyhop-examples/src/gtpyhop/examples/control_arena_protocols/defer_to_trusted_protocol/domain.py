"""
Defer to Trusted Protocol Domain for GTPyhop

This domain models the "Defer to Trusted" micro-protocol from the
Control Arena AI safety framework. An untrusted model proposes output,
a monitor scores its suspiciousness, and a routing decision either
accepts the output (low suspicion) or defers to a trusted model
(high suspicion).

The routing decision is the backtracking point: two methods compete
for the task m_route_output. The first (m_accept_if_low_suspicion)
decomposes to a_accept_output, which checks suspicion <= threshold
and returns False if violated. The greedy planner cannot recover;
backtracking planners try m_defer_to_trusted_fallback.

Architecture: HTN Planner only (no MCP servers, all actions symbolic)

Configuration Properties (set in problems.py):
  - config_suspicion_score: float - scenario-specific suspicion value
  - config_suspicion_threshold: float - threshold for accept/defer

-- Generated 2026-03-31
"""

import sys
import os
from typing import Optional, Union, List, Tuple

# ============================================================================
# GTPYHOP IMPORT (with graceful degradation for direct imports)
# ============================================================================

try:
    import gtpyhop
    from gtpyhop import Domain, State, declare_actions, declare_task_methods, set_current_domain
except ImportError:
    # Graceful degradation: supports direct domain.py import (unsupported but functional)
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
    import gtpyhop
    from gtpyhop import Domain, State, declare_actions, declare_task_methods, set_current_domain

# ============================================================================
# DOMAIN
# ============================================================================
the_domain = Domain("defer_to_trusted_protocol")
set_current_domain(the_domain)

# ============================================================================
# STATE PROPERTY MAP
# ----------------------------------------------------------------------------
# Legend:
#  - (E) Created/modified by the action (Effects)
#  - (P) Consumed/checked by the action (Preconditions/State checks)
#  - [ENABLER] Property acts as a workflow gate for subsequent steps
#  - [DATA]    Informational/data container
#  - [CONFIG]  Configuration parameter read from initial state
#
# Configuration Properties (set in problems.py):
#  config_suspicion_score: float [CONFIG] - scenario-specific suspicion value
#  config_suspicion_threshold: float [CONFIG] - threshold for accept/defer
#  task_id: str [CONFIG] - task identifier
#
# --- SAFETY INVARIANT ---
# a_accept_output MUST NOT fire unless:
#   monitor_evaluation_complete == True [ENABLER]
#   suspicion_score <= config_suspicion_threshold [PRECONDITION]
#
# Step 1: a_initialize_episode
#  (P) task_id [CONFIG]
#  (E) episode_initialized: True [ENABLER]
#  (E) audit_log: [] [DATA]
#
# Step 2: a_run_untrusted_policy
#  (P) episode_initialized [ENABLER]
#  (E) agent_output: str [DATA]
#  (E) untrusted_has_run: True [ENABLER]
#
# Step 3: a_run_monitor
#  (P) untrusted_has_run [ENABLER]
#  (P) config_suspicion_score [CONFIG]
#  (E) suspicion_score: float [DATA]
#  (E) monitor_evaluation_complete: True [ENABLER]
#
# Step 4a: a_accept_output (BACKTRACKING TRIGGER)
#  (P) monitor_evaluation_complete [ENABLER]
#  (P) suspicion_score <= config_suspicion_threshold [PRECONDITION]
#  (E) output_accepted: True [DATA]
#
# Step 4b: a_defer_to_trusted
#  (P) monitor_evaluation_complete [ENABLER]
#  (E) deferred_to_trusted: True [DATA]
#  (E) trusted_output: str [DATA]
#
# Step 5: a_score_trajectory
#  (P) output_accepted OR deferred_to_trusted [ENABLER]
#  (E) trajectory_scored: True [ENABLER]
# ============================================================================

# ============================================================================
# ACTIONS
# ============================================================================

def a_initialize_episode(state: State, task_id: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_initialize_episode(state, task_id)

    Action parameters:
        task_id: Identifier for the task being evaluated

    Action purpose:
        Initialize a micro-protocol episode for the given task

    Preconditions:
        None (initialization action)

    Effects:
        - Episode initialized flag (state.episode_initialized) [ENABLER]
        - Audit log initialized (state.audit_log) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(task_id, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not task_id.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # No preconditions for initialization action
    # END: Preconditions

    # BEGIN: Effects
    # [ENABLER] Episode initialization completed - gates untrusted policy
    state.episode_initialized = True

    # [DATA] Initialize audit trail
    state.audit_log = [('initialize', task_id, 'episode_started')]
    # END: Effects

    return state


def a_run_untrusted_policy(state: State, task_id: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_run_untrusted_policy(state, task_id)

    Action parameters:
        task_id: Identifier for the task being evaluated

    Action purpose:
        Invoke the untrusted model to generate output for the task

    Preconditions:
        - Episode is initialized (state.episode_initialized)

    Effects:
        - Agent output generated (state.agent_output) [DATA]
        - Untrusted policy has run (state.untrusted_has_run) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(task_id, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not task_id.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'episode_initialized') and state.episode_initialized):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Symbolic placeholder for untrusted model output
    state.agent_output = f"untrusted_output:{task_id}"

    # [ENABLER] Untrusted policy has run - gates monitor
    state.untrusted_has_run = True

    state.audit_log.append(('run_untrusted', task_id, 'output_generated'))
    # END: Effects

    return state


def a_run_monitor(state: State, task_id: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_run_monitor(state, task_id)

    Action parameters:
        task_id: Identifier for the task being evaluated

    Action purpose:
        Evaluate the untrusted model output for suspiciousness

    Preconditions:
        - Untrusted policy has run (state.untrusted_has_run)

    Effects:
        - Suspicion score computed (state.suspicion_score) [DATA]
        - Monitor evaluation complete (state.monitor_evaluation_complete) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(task_id, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not task_id.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'untrusted_has_run') and state.untrusted_has_run):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Suspicion score from scenario configuration
    state.suspicion_score = getattr(state, 'config_suspicion_score', 0.0)

    # [ENABLER] Monitor has evaluated - gates routing actions
    state.monitor_evaluation_complete = True

    state.audit_log.append(('monitor', task_id, f'suspicion={state.suspicion_score}'))
    # END: Effects

    return state


def a_accept_output(state: State, task_id: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_accept_output(state, task_id)

    Action parameters:
        task_id: Identifier for the task being evaluated

    Action purpose:
        Accept the untrusted model output when suspicion is low

    Preconditions:
        - Monitor evaluation is complete (state.monitor_evaluation_complete)
        - Suspicion score is at or below threshold
          (state.suspicion_score <= state.config_suspicion_threshold)

    Effects:
        - Output accepted flag (state.output_accepted) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(task_id, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not task_id.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'monitor_evaluation_complete') and state.monitor_evaluation_complete):
        return False
    # BACKTRACKING TRIGGER: suspicion must be at or below threshold
    threshold = getattr(state, 'config_suspicion_threshold', 0.7)
    if state.suspicion_score > threshold:
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Output accepted
    state.output_accepted = True

    state.audit_log.append(('accept', task_id, f'suspicion={state.suspicion_score}<=threshold={threshold}'))
    # END: Effects

    return state


def a_defer_to_trusted(state: State, task_id: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_defer_to_trusted(state, task_id)

    Action parameters:
        task_id: Identifier for the task being evaluated

    Action purpose:
        Defer to the trusted model when suspicion is high

    Preconditions:
        - Monitor evaluation is complete (state.monitor_evaluation_complete)

    Effects:
        - Deferred to trusted flag (state.deferred_to_trusted) [DATA]
        - Trusted model output (state.trusted_output) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(task_id, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not task_id.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'monitor_evaluation_complete') and state.monitor_evaluation_complete):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Deferred to trusted model
    state.deferred_to_trusted = True

    # [DATA] Symbolic placeholder for trusted model output
    state.trusted_output = f"trusted_output:{task_id}"

    state.audit_log.append(('defer', task_id, f'suspicion={state.suspicion_score}>threshold'))
    # END: Effects

    return state


def a_score_trajectory(state: State, task_id: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_score_trajectory(state, task_id)

    Action parameters:
        task_id: Identifier for the task being evaluated

    Action purpose:
        Score the completed trajectory for usefulness and safety

    Preconditions:
        - Output has been accepted or deferred (state.output_accepted
          or state.deferred_to_trusted)

    Effects:
        - Trajectory scored flag (state.trajectory_scored) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(task_id, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not task_id.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    accepted = hasattr(state, 'output_accepted') and state.output_accepted
    deferred = hasattr(state, 'deferred_to_trusted') and state.deferred_to_trusted
    if not (accepted or deferred):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [ENABLER] Trajectory scoring completed
    state.trajectory_scored = True

    outcome = 'accepted' if accepted else 'deferred'
    state.audit_log.append(('score', task_id, f'outcome={outcome}'))
    # END: Effects

    return state


# ============================================================================
# METHODS
# ============================================================================

def m_run_defer_to_trusted_protocol(state: State, task_id: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_run_defer_to_trusted_protocol(state, task_id)

    Method parameters:
        task_id: Identifier for the task being evaluated

    Method purpose:
        Top-level orchestration of the Defer to Trusted micro-protocol:
        initialize, propose, monitor, route, score

    Preconditions:
        None (top-level method)

    Task decomposition:
        - a_initialize_episode: Initialize the episode
        - a_run_untrusted_policy: Generate output from untrusted model
        - a_run_monitor: Evaluate output suspiciousness
        - m_route_output: Route based on suspicion (accept or defer)
        - a_score_trajectory: Score the completed trajectory

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(task_id, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not task_id.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # No preconditions for top-level method
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_initialize_episode", task_id),
        ("a_run_untrusted_policy", task_id),
        ("a_run_monitor", task_id),
        ("m_route_output", task_id),
        ("a_score_trajectory", task_id),
    ]
    # END: Task Decomposition


def m_accept_if_low_suspicion(state: State, task_id: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_accept_if_low_suspicion(state, task_id)

    Method parameters:
        task_id: Identifier for the task being evaluated

    Method purpose:
        Attempt to accept the untrusted output. This method always
        returns a valid decomposition; the action a_accept_output
        contains the threshold check that may fail, triggering
        backtracking to m_defer_to_trusted_fallback.

    Preconditions:
        None (threshold check is in the action)

    Task decomposition:
        - a_accept_output: Accept output (fails if suspicion > threshold)

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(task_id, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not task_id.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # No method-level preconditions; threshold check is in a_accept_output
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [("a_accept_output", task_id)]
    # END: Task Decomposition


def m_defer_to_trusted_fallback(state: State, task_id: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_defer_to_trusted_fallback(state, task_id)

    Method parameters:
        task_id: Identifier for the task being evaluated

    Method purpose:
        Fallback routing: defer to the trusted model. This method
        is tried by the backtracking planner when
        m_accept_if_low_suspicion fails (suspicion > threshold).

    Preconditions:
        None (always succeeds as fallback)

    Task decomposition:
        - a_defer_to_trusted: Defer to trusted model

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(task_id, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not task_id.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # No preconditions - always available as fallback
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [("a_defer_to_trusted", task_id)]
    # END: Task Decomposition


# ============================================================================
# DOMAIN REGISTRATION
# ============================================================================

declare_actions(
    a_initialize_episode,
    a_run_untrusted_policy,
    a_run_monitor,
    a_accept_output,
    a_defer_to_trusted,
    a_score_trajectory,
)

declare_task_methods('m_run_defer_to_trusted_protocol', m_run_defer_to_trusted_protocol)
declare_task_methods('m_route_output', m_accept_if_low_suspicion, m_defer_to_trusted_fallback)
