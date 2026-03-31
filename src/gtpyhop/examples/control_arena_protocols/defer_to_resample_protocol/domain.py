"""
Defer to Resample Protocol Domain for GTPyhop

This domain models the "Defer to Resample" micro-protocol from the
Control Arena AI safety framework. When the untrusted model's output
has high suspicion, instead of immediately deferring to the trusted
model, the protocol generates additional samples and monitors each.
If any sample has low enough suspicion, it is accepted. If all samples
are exhausted without finding a low-suspicion output, the protocol
defers to the trusted model.

This combines two GTPyhop mechanisms:
  - Backtracking at the routing decision (accept vs. resample vs. defer)
  - Recursive method decomposition for multi-round resampling

Architecture: HTN Planner only (no MCP servers, all actions symbolic)

Configuration Properties (set in problems.py):
  - config_suspicion_scores: List[float] - per-sample suspicion values
  - config_suspicion_threshold: float - threshold for accept/defer
  - config_max_samples: int - maximum number of samples to try

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
the_domain = Domain("defer_to_resample_protocol")
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
#  config_suspicion_scores: List[float] [CONFIG] - per-sample suspicion values
#  config_suspicion_threshold: float [CONFIG] - threshold for accept/defer
#  config_max_samples: int [CONFIG] - maximum samples to try
#  task_id: str [CONFIG] - task identifier
#
# Step 1: a_initialize_episode
#  (P) task_id [CONFIG]
#  (E) episode_initialized: True [ENABLER]
#  (E) audit_log: [] [DATA]
#
# Step 2: a_run_untrusted_policy (called per sample)
#  (P) episode_initialized [ENABLER]
#  (E) agent_output: str [DATA]
#  (E) untrusted_has_run: True [ENABLER]
#
# Step 3: a_run_monitor (called per sample)
#  (P) untrusted_has_run [ENABLER]
#  (P) config_suspicion_scores[sample_num] [CONFIG]
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


def a_run_untrusted_policy(state: State, task_id: str, sample_num: int) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_run_untrusted_policy(state, task_id, sample_num)

    Action parameters:
        task_id: Identifier for the task being evaluated
        sample_num: Which sample number this is (0-indexed)

    Action purpose:
        Invoke the untrusted model to generate a sample output

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
    if not isinstance(sample_num, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not task_id.strip(): return False
    if sample_num < 0: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'episode_initialized') and state.episode_initialized):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Symbolic placeholder for untrusted model output
    state.agent_output = f"untrusted_output:{task_id}:sample_{sample_num}"

    # [ENABLER] Untrusted policy has run - gates monitor
    state.untrusted_has_run = True

    state.audit_log.append(('run_untrusted', task_id, f'sample={sample_num}'))
    # END: Effects

    return state


def a_run_monitor(state: State, task_id: str, sample_num: int) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: None

    Action signature:
        a_run_monitor(state, task_id, sample_num)

    Action parameters:
        task_id: Identifier for the task being evaluated
        sample_num: Which sample number this is (0-indexed)

    Action purpose:
        Evaluate the current sample output for suspiciousness

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
    if not isinstance(sample_num, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not task_id.strip(): return False
    if sample_num < 0: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'untrusted_has_run') and state.untrusted_has_run):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Suspicion score from per-sample configuration
    scores = getattr(state, 'config_suspicion_scores', [0.0])
    if sample_num < len(scores):
        state.suspicion_score = scores[sample_num]
    else:
        state.suspicion_score = 1.0  # Default: maximum suspicion

    # [ENABLER] Monitor has evaluated - gates routing actions
    state.monitor_evaluation_complete = True

    state.audit_log.append(('monitor', task_id, f'sample={sample_num},suspicion={state.suspicion_score}'))
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
        Accept the current sample output when suspicion is low

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
        Defer to the trusted model after all samples are exhausted

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

def m_run_resample_protocol(state: State, task_id: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_run_resample_protocol(state, task_id)

    Method parameters:
        task_id: Identifier for the task being evaluated

    Method auxiliary parameters:
        max_samples: int (read from state.config_max_samples)

    Method purpose:
        Top-level orchestration of the Defer to Resample micro-protocol:
        initialize, run first sample, monitor, route/resample, score

    Preconditions:
        None (top-level method)

    Task decomposition:
        - a_initialize_episode: Initialize the episode
        - a_run_untrusted_policy: Generate first sample (sample 0)
        - a_run_monitor: Evaluate first sample
        - m_route_or_resample: Route or generate more samples
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

    # BEGIN: Auxiliary Parameter Inference
    max_samples = getattr(state, 'config_max_samples', 1)
    # END: Auxiliary Parameter Inference

    # BEGIN: Preconditions
    # No preconditions for top-level method
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_initialize_episode", task_id),
        ("a_run_untrusted_policy", task_id, 0),
        ("a_run_monitor", task_id, 0),
        ("m_route_or_resample", task_id, 1, max_samples),
        ("a_score_trajectory", task_id),
    ]
    # END: Task Decomposition


def m_accept_best_sample(state: State, task_id: str,
                         sample_num: int,
                         max_samples: int) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_accept_best_sample(state, task_id, sample_num, max_samples)

    Method parameters:
        task_id: Identifier for the task being evaluated
        sample_num: Next sample number (unused, accept uses current)
        max_samples: Maximum samples allowed (unused)

    Method purpose:
        Attempt to accept the current output. The action a_accept_output
        contains the threshold check that may fail, triggering
        backtracking to m_resample_loop or m_defer_after_resampling.

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
    if not isinstance(sample_num, int): return False
    if not isinstance(max_samples, int): return False
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


def m_resample_loop(state: State, task_id: str,
                    sample_num: int,
                    max_samples: int) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_resample_loop(state, task_id, sample_num, max_samples)

    Method parameters:
        task_id: Identifier for the task being evaluated
        sample_num: Next sample number to try
        max_samples: Maximum samples allowed

    Method purpose:
        Recursive resampling: generate another sample, monitor it,
        then recurse into m_route_or_resample with incremented counter.
        Terminates when sample_num >= max_samples (precondition fails).

    Preconditions:
        - Samples remaining (sample_num < max_samples)

    Task decomposition:
        - a_run_untrusted_policy: Generate next sample
        - a_run_monitor: Evaluate next sample
        - m_route_or_resample: Route or continue resampling (recursive)

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(task_id, str): return False
    if not isinstance(sample_num, int): return False
    if not isinstance(max_samples, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not task_id.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if sample_num >= max_samples:
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_run_untrusted_policy", task_id, sample_num),
        ("a_run_monitor", task_id, sample_num),
        ("m_route_or_resample", task_id, sample_num + 1, max_samples),
    ]
    # END: Task Decomposition


def m_defer_after_resampling(state: State, task_id: str,
                             sample_num: int,
                             max_samples: int) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_defer_after_resampling(state, task_id, sample_num, max_samples)

    Method parameters:
        task_id: Identifier for the task being evaluated
        sample_num: Next sample number (unused, all exhausted)
        max_samples: Maximum samples allowed (unused)

    Method purpose:
        Fallback: defer to trusted model after all samples are
        exhausted or suspicion remains high. Always succeeds.

    Preconditions:
        None (always available as final fallback)

    Task decomposition:
        - a_defer_to_trusted: Defer to trusted model

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(task_id, str): return False
    if not isinstance(sample_num, int): return False
    if not isinstance(max_samples, int): return False
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

declare_task_methods('m_run_resample_protocol', m_run_resample_protocol)
declare_task_methods('m_route_or_resample',
                     m_accept_best_sample,
                     m_resample_loop,
                     m_defer_after_resampling)
