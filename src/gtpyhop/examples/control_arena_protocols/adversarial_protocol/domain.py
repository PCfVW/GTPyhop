"""
Adversarial Protocol Domain for GTPyhop

This domain extends the Defer to Trusted micro-protocol with adversarial
analysis. The untrusted model may operate honestly (no side task) or
adversarially (embedding a side task with varying subtlety). A monitor
maps attack subtlety levels to suspicion scores via calibrated detection
rates. The routing decision (accept vs. defer) determines whether the
attack succeeds.

Two backtracking/branching points:
  - m_generate_output: honest vs. attack (deterministic per scenario)
  - m_route_output: accept vs. defer (backtracking on threshold)

Security analysis:
  - SAFE: attack caught (suspicion > threshold -> defer)
  - VULNERABILITY: attack evades (suspicion <= threshold -> accept
    with side_task_embedded=True)
  - OVER-SENSITIVE: honest output deferred (false positive)

Architecture: HTN Planner only (no MCP servers, all actions symbolic)

Configuration Properties (set in problems.py):
  - config_attack_active: bool - whether attack mode is on
  - config_attack_subtlety: str - 'subtle', 'moderate', or 'obvious'
  - config_detection_rates: dict - maps subtlety -> suspicion score
  - config_honest_suspicion: float - baseline suspicion for honest output
  - config_suspicion_threshold: float - threshold for accept/defer

-- Generated 2026-03-31
"""

import sys
import os
from typing import Optional, Union, List, Tuple, Dict

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
the_domain = Domain("adversarial_protocol")
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
#  config_attack_active: bool [CONFIG] - whether attack mode is on
#  config_attack_subtlety: str [CONFIG] - 'subtle', 'moderate', or 'obvious'
#  config_detection_rates: Dict[str, float] [CONFIG] - maps subtlety -> suspicion
#  config_honest_suspicion: float [CONFIG] - baseline suspicion for honest output
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
# Step 2a: a_run_untrusted_policy_honest
#  (P) episode_initialized [ENABLER]
#  (E) agent_output: str [DATA]
#  (E) side_task_embedded: False [DATA]
#  (E) untrusted_has_run: True [ENABLER]
#
# Step 2b: a_run_untrusted_policy_attack
#  (P) episode_initialized [ENABLER]
#  (E) agent_output: str [DATA]
#  (E) side_task_embedded: True [DATA]
#  (E) attack_subtlety: str [DATA]
#  (E) untrusted_has_run: True [ENABLER]
#
# Step 3: a_run_monitor
#  (P) untrusted_has_run [ENABLER]
#  (P) config_detection_rates [CONFIG] (if side_task_embedded)
#  (P) config_honest_suspicion [CONFIG] (if not side_task_embedded)
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
    # [ENABLER] Episode initialization completed
    state.episode_initialized = True

    # [DATA] Initialize audit trail
    state.audit_log = [('initialize', task_id, 'episode_started')]
    # END: Effects

    return state


def a_run_untrusted_policy_honest(state: State, task_id: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_run_untrusted_policy_honest(state, task_id)

    Action parameters:
        task_id: Identifier for the task being evaluated

    Action purpose:
        Generate honest output from the untrusted model (no side task)

    Preconditions:
        - Episode is initialized (state.episode_initialized)

    Effects:
        - Agent output generated (state.agent_output) [DATA]
        - Side task not embedded (state.side_task_embedded) [DATA]
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
    # [DATA] Honest output (no side task)
    state.agent_output = f"honest_output:{task_id}"

    # [DATA] No side task embedded
    state.side_task_embedded = False

    # [ENABLER] Untrusted policy has run - gates monitor
    state.untrusted_has_run = True

    state.audit_log.append(('run_untrusted', task_id, 'honest'))
    # END: Effects

    return state


def a_run_untrusted_policy_attack(state: State, task_id: str,
                                  subtlety: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_run_untrusted_policy_attack(state, task_id, subtlety)

    Action parameters:
        task_id: Identifier for the task being evaluated
        subtlety: Attack subtlety level ('subtle', 'moderate', or 'obvious')

    Action purpose:
        Generate adversarial output that embeds the side task

    Preconditions:
        - Episode is initialized (state.episode_initialized)

    Effects:
        - Agent output with side task (state.agent_output) [DATA]
        - Side task embedded flag (state.side_task_embedded) [DATA]
        - Attack subtlety level (state.attack_subtlety) [DATA]
        - Untrusted policy has run (state.untrusted_has_run) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(task_id, str): return False
    if not isinstance(subtlety, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not task_id.strip(): return False
    if subtlety not in ('subtle', 'moderate', 'obvious'): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'episode_initialized') and state.episode_initialized):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Adversarial output with embedded side task
    state.agent_output = f"attack_output:{task_id}:{subtlety}"

    # [DATA] Side task is embedded
    state.side_task_embedded = True

    # [DATA] Attack subtlety level
    state.attack_subtlety = subtlety

    # [ENABLER] Untrusted policy has run - gates monitor
    state.untrusted_has_run = True

    state.audit_log.append(('run_untrusted', task_id, f'attack:{subtlety}'))
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
        Evaluate the untrusted model output for suspiciousness.
        Uses detection_rates to map attack subtlety to suspicion score
        when a side task is embedded; uses honest_suspicion baseline
        otherwise.

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
    if hasattr(state, 'side_task_embedded') and state.side_task_embedded:
        # [DATA] Suspicion from detection rates (calibrated per subtlety)
        detection_rates = getattr(state, 'config_detection_rates', {})
        subtlety = getattr(state, 'attack_subtlety', 'obvious')
        state.suspicion_score = detection_rates.get(subtlety, 0.95)
    else:
        # [DATA] Baseline suspicion for honest output
        state.suspicion_score = getattr(state, 'config_honest_suspicion', 0.1)

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
        Accept the output when suspicion is low

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

def m_run_adversarial_protocol(state: State, task_id: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_run_adversarial_protocol(state, task_id)

    Method parameters:
        task_id: Identifier for the task being evaluated

    Method purpose:
        Top-level orchestration of the adversarial micro-protocol:
        initialize, generate output (honest or attack), monitor, route, score

    Preconditions:
        None (top-level method)

    Task decomposition:
        - a_initialize_episode: Initialize the episode
        - m_generate_output: Generate output (honest or attack)
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
        ("m_generate_output", task_id),
        ("a_run_monitor", task_id),
        ("m_route_output", task_id),
        ("a_score_trajectory", task_id),
    ]
    # END: Task Decomposition


def m_honest_output(state: State, task_id: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_honest_output(state, task_id)

    Method parameters:
        task_id: Identifier for the task being evaluated

    Method purpose:
        Generate honest output (no side task). Selected when
        config_attack_active is False.

    Preconditions:
        - Attack is not active (state.config_attack_active == False)

    Task decomposition:
        - a_run_untrusted_policy_honest: Generate honest output

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
    if hasattr(state, 'config_attack_active') and state.config_attack_active:
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [("a_run_untrusted_policy_honest", task_id)]
    # END: Task Decomposition


def m_attack_output(state: State, task_id: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_attack_output(state, task_id)

    Method parameters:
        task_id: Identifier for the task being evaluated

    Method auxiliary parameters:
        subtlety: str (read from state.config_attack_subtlety)

    Method purpose:
        Generate adversarial output with embedded side task. Selected
        when config_attack_active is True. The subtlety level is read
        from state configuration.

    Preconditions:
        - Attack is active (state.config_attack_active == True)

    Task decomposition:
        - a_run_untrusted_policy_attack: Generate adversarial output

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

    # BEGIN: Auxiliary Parameter Inference
    subtlety = getattr(state, 'config_attack_subtlety', 'obvious')
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    if not (hasattr(state, 'config_attack_active') and state.config_attack_active):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [("a_run_untrusted_policy_attack", task_id, subtlety)]
    # END: Task Decomposition


def m_accept_if_low_suspicion(state: State, task_id: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_accept_if_low_suspicion(state, task_id)

    Method parameters:
        task_id: Identifier for the task being evaluated

    Method purpose:
        Attempt to accept the output. The action a_accept_output
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
        Fallback routing: defer to the trusted model. Always succeeds.

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
    a_run_untrusted_policy_honest,
    a_run_untrusted_policy_attack,
    a_run_monitor,
    a_accept_output,
    a_defer_to_trusted,
    a_score_trajectory,
)

declare_task_methods('m_run_adversarial_protocol', m_run_adversarial_protocol)
declare_task_methods('m_generate_output', m_honest_output, m_attack_output)
declare_task_methods('m_route_output', m_accept_if_low_suspicion, m_defer_to_trusted_fallback)
