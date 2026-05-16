"""
Problem definitions for the Colt Express s4 character-priorities example.
-- Generated 2026-05-16

Four scenarios, one per character ability (Belle, Tuco, Django, Cheyenne).
Each invokes m_resolve_fire or m_resolve_punch directly with parameters
that force exactly one method in the priority ladder to fire:
  - scenario_1_belle_immunity_redirects_fire: target=belle, alt available
    -> Belle-immunity method fires, redirects to alt target (1 action)
  - scenario_2_tuco_fires_through_floor: shooter=tuco, target same car
    different level -> Tuco-through-floor method fires (1 action)
  - scenario_3_django_knockback_fire: shooter=django, standard roof-to-roof
    geometry -> Django-knockback method fires (1 action)
  - scenario_4_cheyenne_keeps_punched_purse: puncher=cheyenne, target has
    purse >= 250 -> Cheyenne-keep-purse method fires (1 action)

Pattern source: trunk_thumper s08_priority_methods (Game AI Pro Chapter
12.8). The Belle-immunity scenario structurally mirrors s08's
scenario_4_tired_blocks_whirlwind_combo: a higher-priority guard method
prevents a generic action from firing in a specific rule-defined case.

Note: the implementation plan originally specified 3 scenarios with a
combined "Tuco-or-Django" third scenario; we extended to 4 (one per
character) for clearer pedagogy. Plan length per scenario remains 1.
"""

import sys
import os
from typing import Dict, Tuple, List, Optional

try:
    import gtpyhop
    from gtpyhop import State
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))
    import gtpyhop
    from gtpyhop import State


# ============================================================================
# LOOT DISTRIBUTION (canonical; copy-pasted from s1)
# ============================================================================

COLT_EXPRESS_LOOT_DISTRIBUTION: Dict[str, List[int]] = {
    'purses':      [250]*5 + [300]*2 + [350]*1 + [400]*2 + [450]*1 + [500]*1,
    'jewels':      [500]*4,
    'strongboxes': [1000]*2,
}


# ============================================================================
# HELPER FUNCTIONS (canonical; copy-pasted from s1)
# ============================================================================

def h_sample_car_loot(seed: int,
                      num_jewels: int = 1,
                      num_purses: int = 4,
                      distribution: Optional[Dict[str, List[int]]] = None
                      ) -> List[str]:
    """
    Deterministically sample loot tokens for one car from the distribution.

    Returns a list of string tokens like
        ['jewel_500', 'purse_250', 'purse_300', 'purse_500', 'purse_250']

    Sampling is WITHOUT replacement from a copy of the distribution. The
    same seed yields the same output, so scenarios are reproducible.

    Args:
        seed: Integer seed for the deterministic PRNG.
        num_jewels: How many jewel tokens to include (default 1).
        num_purses: How many purse tokens to include (default 4).
        distribution: Optional override of COLT_EXPRESS_LOOT_DISTRIBUTION.

    Returns:
        List of loot-token strings, jewels first, then purses.
    """
    import random
    if distribution is None:
        distribution = COLT_EXPRESS_LOOT_DISTRIBUTION
    rng = random.Random(seed)
    jewels = list(distribution.get('jewels', []))
    purses = list(distribution.get('purses', []))
    rng.shuffle(jewels)
    rng.shuffle(purses)
    tokens  = [f'jewel_{v}' for v in jewels[:num_jewels]]
    tokens += [f'purse_{v}' for v in purses[:num_purses]]
    return tokens


def h_create_base_state(name: str) -> State:
    """
    Create a base state with the FULL canonical schema initialized.

    Sub-folders may add fields to this state after construction, but must
    not rename or reshape canonical fields. Unused fields are initialized
    to empty containers / None / 0 so cross-folder scenario copy-paste
    works without surprises.
    """
    state = State(name)

    # === Train geometry ===
    state.cars = []
    state.car_index = {}

    # === Bandits ===
    state.bandits = []
    state.bandit_car = {}
    state.bandit_level = {}
    state.bandit_purse = {}
    state.bandit_bullets_taken = {}
    state.bandit_character = {}

    # === Loot ===
    state.loot_at = {}

    # === Marshal ===
    state.marshal_car = None

    # === Programmed deck (Stealin') ===
    state.deck = []

    # === Round / event ===
    state.round_number = 1
    state.event_card = None

    # === Anti-idempotence counter ===
    state.actions_resolved = 0

    return state


def _h_setup_train(state: State, car_names: List[str]) -> None:
    """Convenience helper: populate state.cars and state.car_index."""
    state.cars = list(car_names)
    state.car_index = {name: i for i, name in enumerate(car_names)}


# ============================================================================
# SCENARIOS
# ============================================================================

problems: Dict[str, Tuple[State, List[Tuple], str]] = {}

# BEGIN: Domain: colt_express_s4

# BEGIN: Scenario: scenario_1_belle_immunity_redirects_fire
# Configuration
# Setup: Tuco on roof of caboose; Belle on roof of c1; Doc on roof of
# locomotive. All three on roof, all in different cars. Tuco tries to
# fire at Belle; Belle-immunity fires and redirects to Doc (the available
# alternative target).
# Expected plan: [('a_fire', 'tuco', 'doc')], length 1.

# State
initial_state_scenario_1 = h_create_base_state('scenario_1_belle_immunity_redirects_fire')
_h_setup_train(initial_state_scenario_1, ['locomotive', 'c1', 'caboose'])
initial_state_scenario_1.bandits = ['tuco', 'belle', 'doc']
initial_state_scenario_1.bandit_car = {'tuco': 'caboose', 'belle': 'c1', 'doc': 'locomotive'}
initial_state_scenario_1.bandit_level = {'tuco': 'roof', 'belle': 'roof', 'doc': 'roof'}
initial_state_scenario_1.bandit_purse = {'tuco': 0, 'belle': 0, 'doc': 0}
initial_state_scenario_1.bandit_bullets_taken = {'tuco': 0, 'belle': 0, 'doc': 0}
initial_state_scenario_1.bandit_character = {'tuco': 'tuco', 'belle': 'belle', 'doc': 'plain'}
initial_state_scenario_1.loot_at = {'locomotive': [], 'c1': [], 'caboose': []}

# Problem
problems['scenario_1_belle_immunity_redirects_fire'] = (
    initial_state_scenario_1,
    [('m_resolve_fire', 'tuco', 'belle')],
    'Belle immunity redirects Tuco\'s fire at Belle to the available '
    'alternative target (Doc) -> 1 action'
)
# END: Scenario

# BEGIN: Scenario: scenario_2_tuco_fires_through_floor
# Configuration
# Setup: Tuco on roof of c1; Doc on interior of c1 (same car, different
# level). Belle elsewhere (irrelevant). m_resolve_fire(tuco, doc):
# Belle-immunity falls through (target!=belle); Tuco-through-floor fires.
# Expected plan: [('a_fire_through_floor', 'tuco', 'doc')], length 1.

# State
initial_state_scenario_2 = h_create_base_state('scenario_2_tuco_fires_through_floor')
_h_setup_train(initial_state_scenario_2, ['locomotive', 'c1', 'caboose'])
initial_state_scenario_2.bandits = ['tuco', 'doc']
initial_state_scenario_2.bandit_car = {'tuco': 'c1', 'doc': 'c1'}
initial_state_scenario_2.bandit_level = {'tuco': 'roof', 'doc': 'interior'}
initial_state_scenario_2.bandit_purse = {'tuco': 0, 'doc': 0}
initial_state_scenario_2.bandit_bullets_taken = {'tuco': 0, 'doc': 0}
initial_state_scenario_2.bandit_character = {'tuco': 'tuco', 'doc': 'plain'}
initial_state_scenario_2.loot_at = {'locomotive': [], 'c1': [], 'caboose': []}

# Problem
problems['scenario_2_tuco_fires_through_floor'] = (
    initial_state_scenario_2,
    [('m_resolve_fire', 'tuco', 'doc')],
    'Tuco on roof of c1 fires through floor at Doc on interior of c1 -> '
    '1 action'
)
# END: Scenario

# BEGIN: Scenario: scenario_3_django_knockback_fire
# Configuration
# Setup: Django on roof of c1; Doc on roof of caboose. Standard
# roof-to-roof geometry. m_resolve_fire(django, doc): Belle-immunity
# falls through; Tuco-through-floor falls through (not Tuco); Django-
# knockback fires.
# Expected plan: [('a_fire_with_knockback', 'django', 'doc')], length 1.
# Side effect: Doc takes a bullet AND gets knocked one car backward; but
# Doc is at the caboose (train end), so per rulebook "Bandits can never
# leave the train" — Doc stays at caboose (no car movement). Bullet still
# applied.

# State
initial_state_scenario_3 = h_create_base_state('scenario_3_django_knockback_fire')
_h_setup_train(initial_state_scenario_3, ['locomotive', 'c1', 'caboose'])
initial_state_scenario_3.bandits = ['django', 'doc']
initial_state_scenario_3.bandit_car = {'django': 'c1', 'doc': 'caboose'}
initial_state_scenario_3.bandit_level = {'django': 'roof', 'doc': 'roof'}
initial_state_scenario_3.bandit_purse = {'django': 0, 'doc': 0}
initial_state_scenario_3.bandit_bullets_taken = {'django': 0, 'doc': 0}
initial_state_scenario_3.bandit_character = {'django': 'django', 'doc': 'plain'}
initial_state_scenario_3.loot_at = {'locomotive': [], 'c1': [], 'caboose': []}

# Problem
problems['scenario_3_django_knockback_fire'] = (
    initial_state_scenario_3,
    [('m_resolve_fire', 'django', 'doc')],
    'Django on roof of c1 fires with knockback at Doc on roof of caboose '
    '-> 1 action (Doc stays at caboose since knockback would push beyond '
    'train end)'
)
# END: Scenario

# BEGIN: Scenario: scenario_4_cheyenne_keeps_punched_purse
# Configuration
# Setup: Cheyenne and Doc both on interior of c1 (same car, same level).
# Doc has bandit_purse = 500 (>= 250, the punch transfer amount).
# m_resolve_punch(cheyenne, doc): Cheyenne-keep-purse method fires.
# Expected plan: [('a_punch_and_keep_purse', 'cheyenne', 'doc')], length 1.

# State
initial_state_scenario_4 = h_create_base_state('scenario_4_cheyenne_keeps_punched_purse')
_h_setup_train(initial_state_scenario_4, ['locomotive', 'c1', 'caboose'])
initial_state_scenario_4.bandits = ['cheyenne', 'doc']
initial_state_scenario_4.bandit_car = {'cheyenne': 'c1', 'doc': 'c1'}
initial_state_scenario_4.bandit_level = {'cheyenne': 'interior', 'doc': 'interior'}
initial_state_scenario_4.bandit_purse = {'cheyenne': 0, 'doc': 500}
initial_state_scenario_4.bandit_bullets_taken = {'cheyenne': 0, 'doc': 0}
initial_state_scenario_4.bandit_character = {'cheyenne': 'cheyenne', 'doc': 'plain'}
initial_state_scenario_4.loot_at = {'locomotive': [], 'c1': [], 'caboose': []}

# Problem
problems['scenario_4_cheyenne_keeps_punched_purse'] = (
    initial_state_scenario_4,
    [('m_resolve_punch', 'cheyenne', 'doc')],
    'Cheyenne punches Doc and keeps the $250 (instead of letting it fall '
    'on the floor) -> 1 action'
)
# END: Scenario

# END: Domain


def get_problems() -> Dict[str, Tuple[State, List[Tuple], str]]:
    """
    Return all problem definitions for benchmarking.

    Setup: suppress GTPyhop import messages.

    >>> import sys, io, copy; _o = sys.stdout; sys.stdout = io.StringIO()
    >>> import gtpyhop
    >>> from gtpyhop.examples.colt_express.s4_character_priorities import the_domain, problems
    >>> sys.stdout = _o
    >>> probs = problems.get_problems()
    >>> len(probs)
    4

    Scenario 1 - Belle immunity redirects fire to Doc (1 action).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
    ...         strategy='iterative_dfs_backtracking') as s:
    ...     r1 = s.find_plan(copy.deepcopy(probs['scenario_1_belle_immunity_redirects_fire'][0]),
    ...                      probs['scenario_1_belle_immunity_redirects_fire'][1])
    >>> sys.stdout = _o
    >>> r1.success, len(r1.plan)
    (True, 1)
    >>> r1.plan[0][0]
    'a_fire'
    >>> r1.plan[0][2]
    'doc'

    Scenario 2 - Tuco fires through floor (1 action).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
    ...         strategy='iterative_dfs_backtracking') as s:
    ...     r2 = s.find_plan(copy.deepcopy(probs['scenario_2_tuco_fires_through_floor'][0]),
    ...                      probs['scenario_2_tuco_fires_through_floor'][1])
    >>> sys.stdout = _o
    >>> r2.success, len(r2.plan)
    (True, 1)
    >>> r2.plan[0][0]
    'a_fire_through_floor'

    Scenario 3 - Django knockback fire (1 action).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
    ...         strategy='iterative_dfs_backtracking') as s:
    ...     r3 = s.find_plan(copy.deepcopy(probs['scenario_3_django_knockback_fire'][0]),
    ...                      probs['scenario_3_django_knockback_fire'][1])
    >>> sys.stdout = _o
    >>> r3.success, len(r3.plan)
    (True, 1)
    >>> r3.plan[0][0]
    'a_fire_with_knockback'

    Scenario 4 - Cheyenne keeps the punched purse (1 action).

    >>> _o = sys.stdout; sys.stdout = io.StringIO()
    >>> with gtpyhop.PlannerSession(domain=the_domain, verbose=0,
    ...         strategy='iterative_dfs_backtracking') as s:
    ...     r4 = s.find_plan(copy.deepcopy(probs['scenario_4_cheyenne_keeps_punched_purse'][0]),
    ...                      probs['scenario_4_cheyenne_keeps_punched_purse'][1])
    >>> sys.stdout = _o
    >>> r4.success, len(r4.plan)
    (True, 1)
    >>> r4.plan[0][0]
    'a_punch_and_keep_purse'

    Returns:
        Dictionary mapping problem IDs to (state, tasks, description) tuples.
    """
    return problems
