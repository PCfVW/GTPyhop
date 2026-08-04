# ============================================================================
# Candidate Planning Poetry HTN Domain
# Neuro-Symbolic Poetry Generation with Multi-Candidate Rhyme Selection
# ============================================================================
#
# MOTIVATION:
# Anthropic's "Planning in Poems" (March 2025) discovered that Claude 3.5
# Haiku maintains multiple candidate end-of-line words simultaneously before
# committing to one. This domain makes that multi-candidate mechanism EXPLICIT
# by replacing the single a_select_rhyme_target from structured_poetry with a
# 3-action pipeline: generate candidates -> rank candidates -> commit target.
#
# KEY DIFFERENCE FROM STRUCTURED_POETRY:
# Structured poetry uses 1 action for rhyme selection:
#   a_select_rhyme_target (select one word)
#
# This domain uses 3 actions for rhyme selection:
#   a_generate_rhyme_candidates (produce N candidate end-words)
#   a_rank_candidates           (score by rhyme quality + semantic fit)
#   a_commit_target             (select the top-ranked candidate)
#
# ARCHITECTURE:
#   HTN Planner (GTPyhop)     ->  structural plan (form, rhyme, meter)
#   LLM Server (MCP)          ->  fluent text generation within constraints
#   Phonetics Server (MCP)    ->  candidate generation, ranking, verification
#
# SUPPORTED FORMS:
#   - Rhyming couplet (AA)
#   - Limerick (AABBA, anapestic meter)
#   - Haiku (5-7-5 syllables, no rhyme)
#   - Shakespearean sonnet (ABAB CDCD EFEF GG, iambic pentameter)
#
# PLAN LENGTH BY FORM:
#   Couplet:  2 + (5 x 2) = 12 actions
#   Limerick: 2 + (5 x 5) = 27 actions
#   Haiku:    2 + (2 x 3) = 8 actions  (no candidate selection needed)
#   Sonnet:   2 + (5 x 14) = 72 actions
#
# ============================================================================

# ============================================================================
# FILE ORGANIZATION
# ----------------------------------------------------------------------------
# This file is organized into the following sections:
#   - Imports (with secure path handling)
#   - Domain (1)
#   - Constants
#   - State Property Map (Candidate Planning Poetry Workflow)
#   - Actions (8)
#   - Methods (8)
# ============================================================================

# ============================================================================
# IMPORTS
# ============================================================================

import sys
import os
from typing import Optional, Union, List, Tuple, Dict

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
the_domain = Domain("candidate_planning_poetry")
set_current_domain(the_domain)

# ============================================================================
# CONSTANTS -- Poetic Form Specifications
# ============================================================================

FORM_SPECS = {
    "couplet": {
        "num_lines": 2,
        "rhyme_scheme": ["A", "A"],
        "meter": "iambic_tetrameter",
        "syllables_per_line": [8, 8],
    },
    "limerick": {
        "num_lines": 5,
        "rhyme_scheme": ["A", "A", "B", "B", "A"],
        "meter": "anapestic",
        "syllables_per_line": [8, 8, 5, 5, 8],
    },
    "haiku": {
        "num_lines": 3,
        "rhyme_scheme": [None, None, None],
        "meter": "syllabic",
        "syllables_per_line": [5, 7, 5],
    },
    "sonnet": {
        "num_lines": 14,
        "rhyme_scheme": [
            "A", "B", "A", "B",   # quatrain 1
            "C", "D", "C", "D",   # quatrain 2
            "E", "F", "E", "F",   # quatrain 3
            "G", "G",             # couplet
        ],
        "meter": "iambic_pentameter",
        "syllables_per_line": [10] * 14,
    },
}

# Number of candidate end-words to generate per line
NUM_CANDIDATES = 5

# ============================================================================
# STATE PROPERTY MAP (Candidate Planning Poetry Workflow)
# ----------------------------------------------------------------------------
# Legend:
#  - (E) Created/modified by the action (Effects)
#  - (P) Consumed/checked by the action (Preconditions/State checks)
#  - [ENABLER] Property acts as a workflow gate for subsequent steps
#  - [DATA]    Informational/data container
#
# Server 1: phonetics-server (Candidate Generation, Ranking & Verification)
# Server 2: llm-server (Text Generation via LLM)
#
# --- INITIALIZATION ---
# a_initialize_poem
#  (P) poem_form: str [DATA] - poetic form name
#  (P) topic: str [DATA] - poem topic/theme
#  (E) form_spec: Dict [DATA] - full form specification
#  (E) rhyme_registry: Dict[str, str] [DATA] - maps rhyme labels to target words
#  (E) lines: List[str] [DATA] - generated lines (initially empty)
#  (E) line_targets: List[Optional[str]] [DATA] - planned end-words per line
#  (E) candidates: Dict[int, List[str]] [DATA] - candidate end-words per line
#  (E) ranked_candidates: Dict[int, List[str]] [DATA] - ranked candidates per line
#  (E) num_candidates: int [DATA] - number of candidates to generate
#  (E) poem_initialized: True [ENABLER]
#
# --- PHONETICS SERVER ACTIONS (Server 1) ---
# a_generate_rhyme_candidates
#  (P) poem_initialized == True [ENABLER]
#  (P) rhyme_registry: Dict [DATA]
#  (E) candidates[line_idx]: List[str] [DATA] - N candidate end-words
#  (E) candidates_generated[line_idx]: True [ENABLER]
#
# a_rank_candidates
#  (P) candidates_generated[line_idx] == True [ENABLER]
#  (E) ranked_candidates[line_idx]: List[str] [DATA] - candidates sorted by score
#  (E) candidates_ranked[line_idx]: True [ENABLER]
#
# a_verify_line
#  (P) line_generated[line_idx] == True [ENABLER]
#  (E) line_verified[line_idx]: True [ENABLER]
#  (E) verification_errors[line_idx]: List[str] [DATA]
#
# --- LOCAL ACTIONS ---
# a_commit_target
#  (P) candidates_ranked[line_idx] == True [ENABLER]
#  (E) line_targets[line_idx]: str [DATA] - committed end-word
#  (E) rhyme_registry[label]: str [DATA] - registered rhyme word
#  (E) rhyme_target_selected[line_idx]: True [ENABLER]
#
# --- LLM SERVER ACTIONS (Server 2) ---
# a_generate_line
#  (P) poem_initialized == True [ENABLER]
#  (P) rhyme_target_selected[line_idx] == True [ENABLER]
#  (E) lines[line_idx]: str [DATA] - generated line text
#  (E) line_generated[line_idx]: True [ENABLER]
#
# a_generate_line_no_rhyme
#  (P) poem_initialized == True [ENABLER]
#  (E) lines[line_idx]: str [DATA]
#  (E) line_generated[line_idx]: True [ENABLER]
#
# --- ASSEMBLY ---
# a_assemble_poem
#  (P) all line_verified[i] == True [ENABLER]
#  (E) final_poem: str [DATA] - assembled poem text
#  (E) poem_complete: True [ENABLER]
# ============================================================================


# ============================================================================
# ACTIONS (8)
# ============================================================================

def a_initialize_poem(state: State, poem_form: str, topic: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: local:initialize_poem

    Action signature:
        a_initialize_poem(state, poem_form, topic)

    Action parameters:
        poem_form: Poetic form ('couplet', 'limerick', 'haiku', 'sonnet')
        topic: Theme or subject of the poem (e.g., 'autumn', 'the sea')

    Action purpose:
        Initialize the poem state with form specification, empty line buffers,
        rhyme registry, and candidate buffers

    Preconditions:
        - poem_form must be a recognized form

    Effects:
        - Form specification loaded (state.form_spec) [DATA]
        - Rhyme registry initialized (state.rhyme_registry) [DATA]
        - Line buffers initialized (state.lines, state.line_targets) [DATA]
        - Candidate buffers initialized (state.candidates, state.ranked_candidates) [DATA]
        - Candidate count set (state.num_candidates) [DATA]
        - Poem initialized flag set (state.poem_initialized) [ENABLER]
        - Tracking dictionaries (state.candidates_generated) [DATA]
        - Tracking dictionaries (state.candidates_ranked) [DATA]
        - Form specification (state.poem_form) [DATA]
        - Form specification (state.topic) [DATA]
        - Line generated (state.line_generated) [ENABLER]
        - Line verified (state.line_verified) [ENABLER]
        - Meter (state.meter) [DATA]
        - Num lines (state.num_lines) [ENABLER]
        - Rhyme scheme (state.rhyme_scheme) [DATA]
        - Rhyme target selected (state.rhyme_target_selected) [ENABLER]
        - Syllables per line (state.syllables_per_line) [DATA]
        - Verification errors (state.verification_errors) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(poem_form, str): return False
    if not isinstance(topic, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if not poem_form.strip(): return False
    if not topic.strip(): return False
    if poem_form not in FORM_SPECS: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # No state preconditions -- this is the initialization action
    # END: Preconditions

    # BEGIN: Effects
    spec = FORM_SPECS[poem_form]

    # [DATA] Form specification
    state.poem_form = poem_form
    state.topic = topic
    state.form_spec = spec
    state.num_lines = spec["num_lines"]
    state.rhyme_scheme = spec["rhyme_scheme"]
    state.meter = spec["meter"]
    state.syllables_per_line = spec["syllables_per_line"]

    # [DATA] Rhyme registry: maps rhyme labels (A, B, C...) to target words
    state.rhyme_registry = {}

    # [DATA] Line buffers
    state.lines = [""] * spec["num_lines"]
    state.line_targets = [None] * spec["num_lines"]

    # [DATA] Candidate buffers (new in this domain)
    state.candidates = {}
    state.ranked_candidates = {}
    state.num_candidates = NUM_CANDIDATES

    # [DATA] Tracking dictionaries
    state.candidates_generated = {}
    state.candidates_ranked = {}
    state.rhyme_target_selected = {}
    state.line_generated = {}
    state.line_verified = {}
    state.verification_errors = {}

    # [ENABLER] Gates all subsequent actions
    state.poem_initialized = True
    # END: Effects

    return state


def a_generate_rhyme_candidates(state: State, line_idx: int, rhyme_label: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: phonetics_server:generate_rhyme_candidates

    Action signature:
        a_generate_rhyme_candidates(state, line_idx, rhyme_label)

    Action parameters:
        line_idx: Zero-based index of the line to generate candidates for
        rhyme_label: Rhyme group label (e.g., 'A', 'B', 'C')

    Action purpose:
        Generate N candidate end-words for a line. If the rhyme label already
        has a registered word, candidates must rhyme with it. If this is the
        first line with this label, candidates are topic-appropriate words.
        This models the paper's finding that the LLM activates multiple
        candidate words simultaneously at the newline token.

    Preconditions:
        - Poem must be initialized (state.poem_initialized)
        - line_idx must be within range

    Effects:
        - Candidate list stored (state.candidates[line_idx]) [DATA]
        - Candidates generated flag set (state.candidates_generated[line_idx]) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(line_idx, int): return False
    if not isinstance(rhyme_label, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if line_idx < 0: return False
    if not rhyme_label.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'poem_initialized') and state.poem_initialized):
        return False
    if line_idx >= state.num_lines:
        return False
    # END: Preconditions

    # BEGIN: Effects
    n = state.num_candidates

    # [DATA] Generate candidate end-words (populated by phonetics server at runtime)
    if rhyme_label in state.rhyme_registry:
        # Subsequent line: candidates must rhyme with the registered word
        existing_word = state.rhyme_registry[rhyme_label]
        state.candidates[line_idx] = [
            f"${{rhyme_candidate:{existing_word}:{i}}}" for i in range(n)
        ]
    else:
        # First line with this label: candidates are topic-appropriate words
        state.candidates[line_idx] = [
            f"${{topic_candidate:{state.topic}:{rhyme_label}:{i}}}" for i in range(n)
        ]

    # [ENABLER] Gates a_rank_candidates for this line
    state.candidates_generated[line_idx] = True
    # END: Effects

    return state


def a_rank_candidates(state: State, line_idx: int) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: phonetics_server:rank_candidates

    Action signature:
        a_rank_candidates(state, line_idx)

    Action parameters:
        line_idx: Zero-based index of the line whose candidates to rank

    Action purpose:
        Score and rank the candidate end-words by rhyme quality and semantic
        fit with the poem's topic and preceding lines. The phonetics server
        evaluates rhyme precision while the ranking also considers how
        naturally each candidate word fits the poem's thematic context.

    Preconditions:
        - Candidates must be generated for this line (state.candidates_generated[line_idx])

    Effects:
        - Ranked candidate list stored (state.ranked_candidates[line_idx]) [DATA]
        - Candidates ranked flag set (state.candidates_ranked[line_idx]) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(line_idx, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if line_idx < 0: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'candidates_generated') and
            state.candidates_generated.get(line_idx)):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Ranked candidates (sorted by phonetics server at runtime)
    # At planning time, we store the candidates in placeholder-ranked order
    state.ranked_candidates[line_idx] = [
        f"${{ranked:{c}}}" for c in state.candidates[line_idx]
    ]

    # [ENABLER] Gates a_commit_target for this line
    state.candidates_ranked[line_idx] = True
    # END: Effects

    return state


def a_commit_target(state: State, line_idx: int, rhyme_label: str) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: local:commit_target

    Action signature:
        a_commit_target(state, line_idx, rhyme_label)

    Action parameters:
        line_idx: Zero-based index of the line to commit a target for
        rhyme_label: Rhyme group label (e.g., 'A', 'B', 'C')

    Action purpose:
        Commit the top-ranked candidate as the line's rhyme target word.
        If this is the first line with this rhyme label, register the
        committed word in the rhyme registry for subsequent lines.

    Preconditions:
        - Candidates must be ranked for this line (state.candidates_ranked[line_idx])
        - Ranked candidate list must not be empty

    Effects:
        - Target word stored (state.line_targets[line_idx]) [DATA]
        - Rhyme registry updated (state.rhyme_registry[label]) [DATA]
        - Rhyme target selected flag (state.rhyme_target_selected[line_idx]) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(line_idx, int): return False
    if not isinstance(rhyme_label, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if line_idx < 0: return False
    if not rhyme_label.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'candidates_ranked') and
            state.candidates_ranked.get(line_idx)):
        return False
    if not (hasattr(state, 'ranked_candidates') and
            line_idx in state.ranked_candidates and
            len(state.ranked_candidates[line_idx]) > 0):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Commit the top-ranked candidate as the target
    committed_word = state.ranked_candidates[line_idx][0]
    state.line_targets[line_idx] = committed_word

    # [DATA] Register in rhyme registry if first use of this label
    if rhyme_label not in state.rhyme_registry:
        state.rhyme_registry[rhyme_label] = f"${{registered:{rhyme_label}:{committed_word}}}"

    # [ENABLER] Gates a_generate_line for this line
    state.rhyme_target_selected[line_idx] = True
    # END: Effects

    return state


def a_generate_line(state: State, line_idx: int, target_syllables: int) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: llm_server:generate_line

    Action signature:
        a_generate_line(state, line_idx, target_syllables)

    Action parameters:
        line_idx: Zero-based index of the line to generate
        target_syllables: Target syllable count for the line

    Action purpose:
        Generate a line of poetry using an LLM, constrained by the committed
        rhyme target word and syllable count. The LLM receives the poem
        context (topic, preceding lines, target end-word) and produces
        text that naturally ends with the target word.

    Preconditions:
        - Poem must be initialized (state.poem_initialized)
        - Rhyme target must be selected for this line (state.rhyme_target_selected[line_idx])

    Effects:
        - Generated line text stored (state.lines[line_idx]) [DATA]
        - Line generated flag set (state.line_generated[line_idx]) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(line_idx, int): return False
    if not isinstance(target_syllables, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if line_idx < 0: return False
    if target_syllables <= 0: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'poem_initialized') and state.poem_initialized):
        return False
    if not (hasattr(state, 'rhyme_target_selected') and
            state.rhyme_target_selected.get(line_idx)):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Line text (populated by LLM server at runtime)
    # The LLM receives: topic, preceding lines, target word, syllable count, meter
    state.lines[line_idx] = (
        f"${{llm_generate:topic={state.topic},"
        f"target={state.line_targets[line_idx]},"
        f"syllables={target_syllables},"
        f"meter={state.meter},"
        f"context={state.lines[:line_idx]}}}"
    )

    # [ENABLER] Gates a_verify_line for this line
    state.line_generated[line_idx] = True
    # END: Effects

    return state


def a_generate_line_no_rhyme(state: State, line_idx: int, target_syllables: int) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: llm_server:generate_line_free

    Action signature:
        a_generate_line_no_rhyme(state, line_idx, target_syllables)

    Action parameters:
        line_idx: Zero-based index of the line to generate
        target_syllables: Target syllable count for the line

    Action purpose:
        Generate a line of poetry without a rhyme constraint (e.g., haiku lines).
        Only syllable count and thematic coherence are enforced.

    Preconditions:
        - Poem must be initialized (state.poem_initialized)

    Effects:
        - Generated line text stored (state.lines[line_idx]) [DATA]
        - Line generated flag set (state.line_generated[line_idx]) [ENABLER]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(line_idx, int): return False
    if not isinstance(target_syllables, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if line_idx < 0: return False
    if target_syllables <= 0: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'poem_initialized') and state.poem_initialized):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Line text (populated by LLM server at runtime)
    state.lines[line_idx] = (
        f"${{llm_generate_free:topic={state.topic},"
        f"syllables={target_syllables},"
        f"context={state.lines[:line_idx]}}}"
    )

    # [ENABLER] Gates a_verify_line for this line
    state.line_generated[line_idx] = True
    # END: Effects

    return state


def a_verify_line(state: State, line_idx: int) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: phonetics_server:verify_line

    Action signature:
        a_verify_line(state, line_idx)

    Action parameters:
        line_idx: Zero-based index of the line to verify

    Action purpose:
        Verify that a generated line satisfies its constraints: syllable count,
        meter pattern, and rhyme (if applicable). Uses the phonetics server
        for syllable counting and rhyme checking.

    Preconditions:
        - Line must be generated (state.line_generated[line_idx])

    Effects:
        - Line verified flag set (state.line_verified[line_idx]) [ENABLER]
        - Any verification errors recorded (state.verification_errors[line_idx]) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(line_idx, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if line_idx < 0: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'line_generated') and
            state.line_generated.get(line_idx)):
        return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Verification result (populated by phonetics server at runtime)
    # Checks: syllable count, meter, rhyme match (if rhymed line)
    state.verification_errors[line_idx] = []  # Empty = passed

    # [ENABLER] Gates assembly or next line generation
    state.line_verified[line_idx] = True
    # END: Effects

    return state


def a_assemble_poem(state: State) -> Union[State, bool]:
    """
    Class: Action

    MCP_Tool: local:assemble_poem

    Action signature:
        a_assemble_poem(state)

    Action parameters:
        None

    Action purpose:
        Assemble all verified lines into the final poem text

    Preconditions:
        - All lines must be verified

    Effects:
        - Final poem text assembled (state.final_poem) [DATA]
        - Poem complete flag set (state.poem_complete) [DATA]

    Returns:
        Updated state if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional parameters to validate
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not hasattr(state, 'line_verified'):
        return False
    for i in range(state.num_lines):
        if not state.line_verified.get(i):
            return False
    # END: Preconditions

    # BEGIN: Effects
    # [DATA] Final assembled poem
    state.final_poem = "\n".join(state.lines)

    # [DATA] Workflow complete
    state.poem_complete = True
    # END: Effects

    return state


# ============================================================================
# METHODS (8)
# ============================================================================

# ============================================================================
# TOP-LEVEL ENTRY POINT
# ============================================================================

def m_write_poem(state: State, poem_form: str, topic: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_write_poem(state, poem_form, topic)

    Method parameters:
        poem_form: Poetic form ('couplet', 'limerick', 'haiku', 'sonnet')
        topic: Theme or subject of the poem

    Method purpose:
        Top-level entry point. Initializes the poem, dispatches to the
        appropriate form-specific method, then assembles the result.

    Preconditions:
        - poem_form must be a recognized form

    Task decomposition:
        - a_initialize_poem: Set up form spec, buffers, rhyme registry, candidate buffers
        - m_compose_<form>: Form-specific composition method
        - a_assemble_poem: Join verified lines into final text

    Returns:
        Task decomposition if successful, False otherwise

    Hierarchical Decomposition:
        m_write_poem
        +-- a_initialize_poem
        +-- m_compose_couplet | m_compose_limerick | m_compose_haiku | m_compose_sonnet
        +-- a_assemble_poem
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(poem_form, str): return False
    if not isinstance(topic, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if poem_form not in FORM_SPECS: return False
    if not topic.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    # No state preconditions -- this is the entry point
    # END: Preconditions

    # BEGIN: Task Decomposition
    form_method = f"m_compose_{poem_form}"
    return [
        ("a_initialize_poem", poem_form, topic),
        (form_method,),
        ("a_assemble_poem",),
    ]
    # END: Task Decomposition


# ============================================================================
# FORM-SPECIFIC COMPOSITION METHODS
# ============================================================================

def m_compose_couplet(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_compose_couplet(state)

    Method parameters:
        None (uses state.form_spec)

    Method purpose:
        Compose a rhyming couplet (AA scheme, 2 lines).
        Line 1: generate candidates, rank, commit target A, generate, verify.
        Line 2: generate candidates rhyming with A, rank, commit, generate, verify.

    Preconditions:
        - Poem must be initialized (state.poem_initialized)

    Task decomposition:
        - m_write_rhymed_line x 2

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional parameters to validate
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'poem_initialized') and state.poem_initialized):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("m_write_rhymed_line", 0, "A", 8),
        ("m_write_rhymed_line", 1, "A", 8),
    ]
    # END: Task Decomposition


def m_compose_limerick(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_compose_limerick(state)

    Method parameters:
        None (uses state.form_spec)

    Method purpose:
        Compose a limerick (AABBA scheme, 5 lines).
        Lines 1,2,5: 8 syllables, rhyme group A.
        Lines 3,4: 5 syllables, rhyme group B.

    Preconditions:
        - Poem must be initialized (state.poem_initialized)

    Task decomposition:
        - m_write_rhymed_line x 5 with appropriate labels and syllable counts

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional parameters to validate
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'poem_initialized') and state.poem_initialized):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    # AABBA: lines 0,1,4 rhyme A (8 syl); lines 2,3 rhyme B (5 syl)
    return [
        ("m_write_rhymed_line", 0, "A", 8),
        ("m_write_rhymed_line", 1, "A", 8),
        ("m_write_rhymed_line", 2, "B", 5),
        ("m_write_rhymed_line", 3, "B", 5),
        ("m_write_rhymed_line", 4, "A", 8),
    ]
    # END: Task Decomposition


def m_compose_haiku(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_compose_haiku(state)

    Method parameters:
        None (uses state.form_spec)

    Method purpose:
        Compose a haiku (5-7-5 syllables, no rhyme).
        Each line is generated freely with only syllable constraints.

    Preconditions:
        - Poem must be initialized (state.poem_initialized)

    Task decomposition:
        - m_write_free_line x 3 with syllable counts [5, 7, 5]

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional parameters to validate
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'poem_initialized') and state.poem_initialized):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("m_write_free_line", 0, 5),
        ("m_write_free_line", 1, 7),
        ("m_write_free_line", 2, 5),
    ]
    # END: Task Decomposition


def m_compose_sonnet(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_compose_sonnet(state)

    Method parameters:
        None (uses state.form_spec)

    Method purpose:
        Compose a Shakespearean sonnet (ABAB CDCD EFEF GG, 14 lines,
        iambic pentameter = 10 syllables per line).
        Decomposes into 3 quatrains + 1 couplet.

    Preconditions:
        - Poem must be initialized (state.poem_initialized)

    Task decomposition:
        - m_write_quatrain x 3 (lines 0-3, 4-7, 8-11)
        - m_write_rhymed_line x 2 (closing couplet, lines 12-13)

    Returns:
        Task decomposition if successful, False otherwise

    Hierarchical Decomposition:
        m_compose_sonnet
        +-- m_write_quatrain(0, "A", "B")   [lines 0-3: ABAB]
        +-- m_write_quatrain(4, "C", "D")   [lines 4-7: CDCD]
        +-- m_write_quatrain(8, "E", "F")   [lines 8-11: EFEF]
        +-- m_write_rhymed_line(12, "G", 10) [closing couplet]
        +-- m_write_rhymed_line(13, "G", 10)
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    # No additional parameters to validate
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'poem_initialized') and state.poem_initialized):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("m_write_quatrain", 0, "A", "B"),
        ("m_write_quatrain", 4, "C", "D"),
        ("m_write_quatrain", 8, "E", "F"),
        ("m_write_rhymed_line", 12, "G", 10),
        ("m_write_rhymed_line", 13, "G", 10),
    ]
    # END: Task Decomposition


# ============================================================================
# STRUCTURAL SUB-METHODS
# ============================================================================

def m_write_quatrain(state: State, start_line: int, label_1: str, label_2: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_write_quatrain(state, start_line, label_1, label_2)

    Method parameters:
        start_line: Index of the first line in this quatrain
        label_1: Rhyme label for lines 1 and 3 (e.g., 'A')
        label_2: Rhyme label for lines 2 and 4 (e.g., 'B')

    Method purpose:
        Write a four-line quatrain with ABAB rhyme scheme (cross-rhyme).
        Each line is 10 syllables (iambic pentameter).

    Preconditions:
        - Poem must be initialized (state.poem_initialized)

    Task decomposition:
        - m_write_rhymed_line x 4 in ABAB pattern

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(start_line, int): return False
    if not isinstance(label_1, str): return False
    if not isinstance(label_2, str): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if start_line < 0: return False
    if not label_1.strip(): return False
    if not label_2.strip(): return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'poem_initialized') and state.poem_initialized):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    # ABAB pattern within the quatrain
    return [
        ("m_write_rhymed_line", start_line + 0, label_1, 10),
        ("m_write_rhymed_line", start_line + 1, label_2, 10),
        ("m_write_rhymed_line", start_line + 2, label_1, 10),
        ("m_write_rhymed_line", start_line + 3, label_2, 10),
    ]
    # END: Task Decomposition


# ============================================================================
# LINE-LEVEL METHODS (leaf-level decomposition)
# ============================================================================

def m_write_rhymed_line(state: State, line_idx: int, rhyme_label: str, target_syllables: int) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_write_rhymed_line(state, line_idx, rhyme_label, target_syllables)

    Method parameters:
        line_idx: Zero-based line index
        rhyme_label: Rhyme group label ('A', 'B', etc.)
        target_syllables: Target syllable count for the line

    Method purpose:
        Write a single rhymed line using the multi-candidate pipeline.
        This is the core 5-action cycle that models the LLM's simultaneous
        consideration of multiple candidate words before committing:
        generate candidates -> rank -> commit -> generate line -> verify.

    Preconditions:
        - Poem must be initialized (state.poem_initialized)

    Task decomposition:
        - a_generate_rhyme_candidates: Produce N candidate end-words
        - a_rank_candidates: Score candidates by rhyme quality + semantic fit
        - a_commit_target: Select top-ranked candidate as line target
        - a_generate_line: Backward planning (write toward committed target)
        - a_verify_line: Constraint checking (meter, rhyme, coherence)

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(line_idx, int): return False
    if not isinstance(rhyme_label, str): return False
    if not isinstance(target_syllables, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if line_idx < 0: return False
    if not rhyme_label.strip(): return False
    if target_syllables <= 0: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'poem_initialized') and state.poem_initialized):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_generate_rhyme_candidates", line_idx, rhyme_label),
        ("a_rank_candidates", line_idx),
        ("a_commit_target", line_idx, rhyme_label),
        ("a_generate_line", line_idx, target_syllables),
        ("a_verify_line", line_idx),
    ]
    # END: Task Decomposition


def m_write_free_line(state: State, line_idx: int, target_syllables: int) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m_write_free_line(state, line_idx, target_syllables)

    Method parameters:
        line_idx: Zero-based line index
        target_syllables: Target syllable count for the line

    Method purpose:
        Write a single unrhymed line (e.g., haiku): generate text -> verify.
        No candidate selection needed.

    Preconditions:
        - Poem must be initialized (state.poem_initialized)

    Task decomposition:
        - a_generate_line_no_rhyme: Free generation with syllable constraint
        - a_verify_line: Constraint checking (syllable count)

    Returns:
        Task decomposition if successful, False otherwise
    """
    # BEGIN: Type Checking
    if not isinstance(state, State): return False
    if not isinstance(line_idx, int): return False
    if not isinstance(target_syllables, int): return False
    # END: Type Checking

    # BEGIN: State-Type Checks
    if line_idx < 0: return False
    if target_syllables <= 0: return False
    # END: State-Type Checks

    # BEGIN: Preconditions
    if not (hasattr(state, 'poem_initialized') and state.poem_initialized):
        return False
    # END: Preconditions

    # BEGIN: Task Decomposition
    return [
        ("a_generate_line_no_rhyme", line_idx, target_syllables),
        ("a_verify_line", line_idx),
    ]
    # END: Task Decomposition


# ============================================================================
# DECLARE ACTIONS TO DOMAIN
# ============================================================================

declare_actions(
    a_initialize_poem,
    a_generate_rhyme_candidates,
    a_rank_candidates,
    a_commit_target,
    a_generate_line,
    a_generate_line_no_rhyme,
    a_verify_line,
    a_assemble_poem,
)

# ============================================================================
# DECLARE METHODS TO DOMAIN
# ============================================================================

# Top-level entry point
declare_task_methods('m_write_poem', m_write_poem)

# Form-specific composition methods
declare_task_methods('m_compose_couplet', m_compose_couplet)
declare_task_methods('m_compose_limerick', m_compose_limerick)
declare_task_methods('m_compose_haiku', m_compose_haiku)
declare_task_methods('m_compose_sonnet', m_compose_sonnet)

# Structural sub-methods
declare_task_methods('m_write_quatrain', m_write_quatrain)

# Line-level methods
declare_task_methods('m_write_rhymed_line', m_write_rhymed_line)
declare_task_methods('m_write_free_line', m_write_free_line)

# ============================================================================
# END OF FILE
# ============================================================================
