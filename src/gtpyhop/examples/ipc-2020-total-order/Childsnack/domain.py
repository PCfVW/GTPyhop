# ============================================================================
# IPC 2020 Total Order - Childsnack Domain
# ============================================================================

# ============================================================================
# FILE ORGANIZATION
# ----------------------------------------------------------------------------
# This file is organized into the following sections:
#   - Imports (with secure path handling)
#   - Domain (1)
#   - Actions (7)
#   - Helpers - State Parameter Inference (6)
#   - Methods (2)
#   - Goal Methods
# ============================================================================

# ============================================================================
# IMPORTS
# ============================================================================

# -------------------- Smart GTPyhop import strategy with secure path handling
import sys
import os
from typing import Optional, Union, List, Tuple

def safe_add_to_path(relative_path: str) -> Optional[str]:
    """
    Safely add a relative path to sys.path with validation to prevent path traversal attacks.

    Args:
        relative_path: Relative path to add to sys.path

    Returns:
        The absolute path that was added, or None if validation failed

    Raises:
        ValueError: If path traversal is detected
    """
    base_path = os.path.dirname(os.path.abspath(__file__))
    target_path = os.path.normpath(os.path.join(base_path, relative_path))

    # Validate the path is within expected boundaries to prevent path traversal
    if not target_path.startswith(os.path.dirname(base_path)):
        raise ValueError(f"Path traversal detected: {target_path}")

    if os.path.exists(target_path) and target_path not in sys.path:
        sys.path.insert(0, target_path)
        return target_path
    return None

# ----- Secure GTPyhop import strategy - tries PyPI first, falls back to local
try:
    import gtpyhop
    from gtpyhop import Domain, State, set_current_domain, declare_actions, declare_task_methods, declare_unigoal_methods, declare_multigoal_methods
except ImportError:
    # Fallback to local development with secure path handling
    try:
        safe_add_to_path(os.path.join('..', '..', '..', '..'))
        import gtpyhop
        from gtpyhop import Domain, State, set_current_domain, declare_actions, declare_task_methods, declare_unigoal_methods, declare_multigoal_methods
    except (ImportError, ValueError) as e:
        print(f"Error: Could not import gtpyhop: {e}")
        print("Please install gtpyhop using: pip install gtpyhop")
        sys.exit(1)

# ============================================================================
# DOMAIN
# ============================================================================
the_domain = Domain('Childsnack')
set_current_domain(the_domain)

# ============================================================================
# ACTIONS (7)
# ----------------------------------------------------------------------------
#   - make_sandwich_no_gluten
#   - make_sandwich
#   - put_on_tray
#   - serve_sandwich_no_gluten
#   - serve_sandwich
#   - move_tray
#   - nop
# ============================================================================

# (:action make_sandwich_no_gluten
#   :parameters (?s - sandwich ?b - bread-portion ?c - content-portion)
#   :precondition (and (at_kitchen_bread ?b) (at_kitchen_content ?c) (no_gluten_bread ?b) (no_gluten_content ?c) (notexist ?s))
#   :effect (and (not (at_kitchen_bread ?b)) (not (at_kitchen_content ?c)) (at_kitchen_sandwich ?s) (no_gluten_sandwich ?s) (not (notexist ?s))))
def make_sandwich_no_gluten(state: State, s: str, b: str, c: str) -> Union[State, bool]:
    """
    Class: Action

    Action signature:
        make_sandwich_no_gluten(state, s, b, c)

    Action parameters:
        s: sandwich
        b: bread-portion
        c: content-portion

    Action auxiliary parameters:
        None (inferred from None)

    Action purpose:
        Make gluten-free sandwich s from bread-portion b and content-portion c

    Returns:
        Updated state if successful, False otherwise
    """
    # Check types
    # Python type checking: parameter state must be a State
    if not (isinstance(state, State)):
        return False
    # Python type checking: parameter s must be a string
    # Python type checking: parameter b must be a string
    # Python type checking: parameter c must be a string
    if not (isinstance(s, str) and isinstance(b, str) and isinstance(c, str)):
        return False
    # State type checking: parameter s must be a sandwich
    # State type checking: parameter b must be a bread-portion
    # State type checking: parameter c must be a content-portion
    if not (s in state.sandwiches and b in state.bread_portions and c in state.content_portions): 
        return False
    
    # No inferred auxiliary parameters

    # (and (at_kitchen_bread ?b) (at_kitchen_content ?c) (no_gluten_bread ?b) (no_gluten_content ?c) (notexist ?s))
    # -----> Check preconditions
    if not ((b in state.at_kitchen_bread) and 
            (c in state.at_kitchen_content) and 
            (b in state.no_gluten_bread) and 
            (c in state.no_gluten_content) and 
            (s in state.notexist)):
        return False

    # (and (not (at_kitchen_bread ?b)) (not (at_kitchen_content ?c)) (at_kitchen_sandwich ?s) (no_gluten_sandwich ?s) (not (notexist ?s))))
    # <----- Apply effects
    state.at_kitchen_bread.discard(b)       # HDDL: (not (at_kitchen_bread ?b))
    state.at_kitchen_content.discard(c)     # HDDL: (not (at_kitchen_content ?c))
    state.at_kitchen_sandwich.add(s)        # HDDL: (at_kitchen_sandwich ?s)
    state.no_gluten_sandwich.add(s)         # HDDL: (no_gluten_sandwich ?s)
    state.notexist.discard(s)               # HDDL: (not (notexist ?s))

    return state

# (:action make_sandwich
#   :parameters (?s - sandwich ?b - bread-portion ?c - content-portion)
#   :precondition (and (at_kitchen_bread ?b) (at_kitchen_content ?c) (notexist ?s))
#   :effect (and (not (at_kitchen_bread ?b)) (not (at_kitchen_content ?c)) (at_kitchen_sandwich ?s) (not (notexist ?s))))
def make_sandwich(state: State, s: str, b: str, c: str)  -> Union[List[Tuple], bool]:
    """
    Class: Action

    Action signature:
        make_sandwich(state, s, b, c)

    Action parameters:
        s: sandwich
        b: bread-portion
        c: content-portion

    Action auxiliary parameters:
        None (inferred from None)

    Action purpose:
        Make sandwich s from bread-portion b and content-portion c

    Returns:
        Updated state if successful, False otherwise
    """
    # Check types
    # Python type checking: parameter state must be a State
    if not (isinstance(state, State)):
        return False
    # Python type checking: parameter s must be a string
    # Python type checking: parameter b must be a string
    # Python type checking: parameter c must be a string
    if not (isinstance(s, str) and isinstance(b, str) and isinstance(c, str)):
        return False
    # State type checking: parameter s must be a sandwich
    # State type checking: parameter b must be a bread-portion
    # State type checking: parameter c must be a content-portion
    if not ((s in state.sandwiches) and (b in state.bread_portions) and (c in state.content_portions)): 
        return False
    
    # No inferred auxiliary parameters

    # (and (at_kitchen_bread ?b) (at_kitchen_content ?c) (notexist ?s))
    # -----> Check preconditions
    if not ((b in state.at_kitchen_bread) and 
            (c in state.at_kitchen_content) and 
            (s in state.notexist)):
        return False

    # (and (not (at_kitchen_bread ?b)) (not (at_kitchen_content ?c)) (at_kitchen_sandwich ?s) (not (notexist ?s))))
    # <----- Apply effects
    state.at_kitchen_bread.discard(b)       # HDDL: (not (at_kitchen_bread ?b))
    state.at_kitchen_content.discard(c)     # HDDL: (not (at_kitchen_content ?c))
    state.at_kitchen_sandwich.add(s)        # HDDL: (at_kitchen_sandwich ?s)
    state.notexist.discard(s)               # HDDL: (not (notexist ?s))

    return state

# (:action put_on_tray
#   :parameters (?s - sandwich ?t - tray)
#   :precondition (and (at_kitchen_sandwich ?s) (at ?t kitchen))
#   :effect (and (not (at_kitchen_sandwich ?s)) (ontray ?s ?t)))
def put_on_tray(state: State, s: str, t: str) -> Union[List[Tuple], bool]:
    """
    Class: Action

    Action signature:
        put_on_tray(state, s, t)

    Action parameters:
        s: sandwich
        t: tray

    Action auxiliary parameters:
        None (inferred from None)

    Action purpose:
        Place sandwich s onto tray t

    Returns:
        Updated state if successful, False otherwise
    """
    # Check types
    # Python type checking: parameter state must be a State
    if not (isinstance(state, State)):
        return False
    # Python type checking: parameter s must be a string
    # Python type checking: parameter t must be a string
    if not (isinstance(s, str) and isinstance(t, str)):
        return False
    # State type checking: parameter s must be a sandwich
    # State type checking: parameter t must be a tray
    if not (s in state.sandwiches and t in state.trays): 
        return False
    
    # No inferred auxiliary parameters

    # (and (at_kitchen_sandwich ?s) (at ?t kitchen))
    # -----> Check preconditions
    if not ((s in state.at_kitchen_sandwich) and 
            (t in state.at and state.at[t] == "kitchen")):
        return False

    # (and (not (at_kitchen_sandwich ?s)) (ontray ?s ?t)))
    # <----- Apply effects
    state.at_kitchen_sandwich.discard(s)    # HDDL: (not (at_kitchen_sandwich ?s))
    state.ontray[s] = t                     # HDDL: (ontray ?s ?t)

    return state

# (:action serve_sandwich_no_gluten
#   :parameters (?s - sandwich ?c - child ?t - tray ?p - place)
#   :precondition (and (allergic_gluten ?c) (ontray ?s ?t) (waiting ?c ?p) (no_gluten_sandwich ?s) (at ?t ?p))
#   :effect (and (not (ontray ?s ?t)) (served ?c)))
def serve_sandwich_no_gluten(state: State, s: str, c: str, t: str, p: str) -> Union[List[Tuple], bool]:
    """
    Class: Action

    Action signature:
        serve_sandwich_no_gluten(state, s, c, t, p)

    Action parameters:
        s: sandwich
        c: child
        t: tray
        p: place

    Action auxiliary parameters:
        None (inferred from None)

    Action purpose:
        Serve no gluten sandwich s to child c at place p from tray t

    Returns:
        Updated state if successful, False otherwise
    """
    # Check types
    # Python type checking: parameter state must be a State
    if not (isinstance(state, State)):
        return False
    # Python type checking: parameter s must be a string
    # Python type checking: parameter c must be a string
    # Python type checking: parameter t must be a string
    # Python type checking: parameter p must be a string
    if not (isinstance(s, str) and isinstance(c, str) and isinstance(t, str) and isinstance(p, str)):
        return False
    # State type checking: parameter s must be a sandwich
    # State type checking: parameter c must be a child
    # State type checking: parameter t must be a tray
    # State type checking: parameter p must be a place
    if not ((s in state.sandwiches) and (c in state.children) and (t in state.trays) and (p in state.places)): 
        return False
    
    # No inferred auxiliary parameters

    # (and (allergic_gluten ?c) (ontray ?s ?t) (waiting ?c ?p) (no_gluten_sandwich ?s) (at ?t ?p))
    # -----> Check preconditions
    if not ((c in state.allergic_gluten) and 
            (s in state.ontray and state.ontray[s] == t) and 
            (c in state.waiting and state.waiting[c] == p) and 
            (s in state.no_gluten_sandwich) and 
            (t in state.at and state.at[t] == p)):
        return False

    # (and (not (ontray ?s ?t)) (served ?c)))
    # <----- Apply effects
    state.ontray.pop(s, None)       # HDDL: (not (ontray ?s ?t))
    state.served[c] = p             # HDDL: (served ?c)

    return state

# (:action serve_sandwich
#   :parameters (?s - sandwich ?c - child ?t - tray ?p - place)
#   :precondition (and (not_allergic_gluten ?c) (waiting ?c ?p) (ontray ?s ?t) (at ?t ?p))
#   :effect (and (not (ontray ?s ?t)) (served ?c)))
def serve_sandwich(state: State, s: str, c: str, t: str, p: str) -> Union[List[Tuple], bool]:
    """
    Class: Action

    Action signature:
        serve_sandwich(state, s, c, t, p)

    Action parameters:
        s: sandwich
        c: child
        t: tray
        p: place

    Action auxiliary parameters:
        None (inferred from None)

    Action purpose:
        Serve sandwich s to child c at place p from tray t

    Returns:
        Updated state if successful, False otherwise
    """
    # Check types
    # Python type checking: parameter state must be a State
    if not (isinstance(state, State)):
        return False
    # Python type checking: parameter s must be a string
    # Python type checking: parameter c must be a string
    # Python type checking: parameter t must be a string
    # Python type checking: parameter p must be a string
    if not (isinstance(s, str) and isinstance(c, str) and isinstance(t, str) and isinstance(p, str)):
        return False
    # State type checking: parameter s must be a sandwich
    # State type checking: parameter c must be a child
    # State type checking: parameter t must be a tray
    # State type checking: parameter p must be a place
    if not ((s in state.sandwiches) and (c in state.children) and (t in state.trays) and (p in state.places)): 
        return False
    
    # No inferred auxiliary parameters

    # (and (not_allergic_gluten ?c) (waiting ?c ?p) (ontray ?s ?t) (at ?t ?p))
    # -----> Check preconditions
    if not ((c in state.not_allergic_gluten) and 
            (c in state.waiting and state.waiting[c] == p) and 
            (s in state.ontray and state.ontray[s] == t) and 
            (t in state.at and state.at[t] == p)):
        return False

    # (and (not (ontray ?s ?t)) (served ?c)))
    # <----- Apply effects()
    state.ontray.pop(s, None)       # HDDL: (not (ontray ?s ?t))
    state.served[c] = p             # HDDL: (served ?c)

    return state

# (:action move_tray
#   :parameters (?t - tray ?p1 - place ?p2 - place)
#   :precondition (and (at ?t ?p1))
#   :effect (and (not (at ?t ?p1)) (at ?t ?p2)))
def move_tray(state: State, t: str, p1: str, p2: str) -> Union[List[Tuple], bool]:
    """
    Class: Action

    Action signature:
        move_tray(state, t, p1, p2)

    Action parameters:
        t: tray
        p1: place
        p2: place

    Action auxiliary parameters:
        None (inferred from None)

    Action purpose:
        Move tray t from place p1 to place p2

    Returns:
        Updated state if successful, False otherwise
    """
    # Check types
    # Python type checking: parameter state must be a State
    if not (isinstance(state, State)):
        return False
    # Python type checking: parameter t must be a string
    # Python type checking: parameter p1 must be a string
    # Python type checking: parameter p2 must be a string
    if not (isinstance(t, str) and isinstance(p1, str) and isinstance(p2, str)):
        return False
    # State type checking: parameter t must be a tray
    # State type checking: parameter p1 must be a place (or the kitchen)
    # State type checking: parameter p2 must be a place (or the kitchen)
    if not ((t in state.trays) and 
            ((p1 == "kitchen") or (p1 in state.places)) and 
            ((p2 == "kitchen") or (p2 in state.places))): 
        return False
    
    # No inferred auxiliary parameters

    # (and (at ?t ?p1))
    # -----> Check preconditions
    if not ((t in state.at) and (state.at[t] == p1)):
        return False

    # (and (not (at ?t ?p1)) (at ?t ?p2)))
    # <----- Apply effects
    # state.at.discard(t)           # HDDL: (not (at ?t ?p1))
    # state.at[t] = p2              # HDDL: (at ?t ?p2)
    state.at[t] = p2                # Optimization: Combine the two lines above into one

    return state

# (:action nop
#   :parameters ()
#   :precondition ()
#   :effect ())
# )
def nop(state: State) -> Union[List[Tuple], bool]:
    """
    Class: Action

    Action signature:
        nop(state)

    Action parameters:
        None

    Action auxiliary parameters:
        None (inferred from None)

    Action purpose:
        Do nothing

    Returns:
        Same state if successful, False otherwise
    """
    # Check types
    # Python type checking: state must be a State
    if not (isinstance(state, State)):
        return False
    
    # No inferred auxiliary parameters

    # ()
    # -----> Check preconditions

    # ()
    # <----- Apply effects

    return state

# Declare actions to the domain
declare_actions(make_sandwich_no_gluten)
declare_actions(make_sandwich)
declare_actions(put_on_tray)
declare_actions(serve_sandwich_no_gluten)
declare_actions(serve_sandwich)
declare_actions(move_tray)
declare_actions(nop)

# ============================================================================
# HELPERS - STATE PARAMETER INFERENCE (6)
# ----------------------------------------------------------------------------
#   - infer_available_tray
#   - infer_no_gluten_bread
#   - infer_no_gluten_content
#   - infer_with_gluten_bread
#   - infer_with_gluten_content
#   - infer_non_existent_sandwich
# ============================================================================
def infer_available_tray(state: State) -> Optional[str]:
    """
    Class: Helper-State-Parameter-Inference

    Helper signature:
        infer_available_tray(state)

    Helper parameters:
        state: current state

    Helper auxiliary parameters:
        None (inferred from None)

    Helper purpose:
        Find an available tray in the current state

    Helper returns:
        An available tray if found, None otherwise
    """
    # Check types
    # Python type checking: state must be a State
    if not (isinstance(state, State)):
        return None

    # No inferred auxiliary parameters

    # Find an available tray in the kitchen
    for tray in state.trays:
        if tray in state.at and state.at[tray] == "kitchen":
            return tray

    return None

def infer_no_gluten_bread(state: State) -> Optional[str]:
    """
    Class: Helper-State-Parameter-Inference

    Helper signature:
        infer_no_gluten_bread(state)

    Helper parameters:
        state: current state

    Helper auxiliary parameters:
        None (inferred from None)

    Helper purpose:
        Find a no-gluten bread-portion in the current state

    Helper returns:
        A no-gluten bread-portion if found, None otherwise
    """
    # Check types
    # Python type checking: state must be a State
    if not (isinstance(state, State)):
        return None

    # No inferred auxiliary parameters

    # Find a gluten free bread-portion in the kitchen
    for bread in state.bread_portions:
        if ((bread in state.at_kitchen_bread) and (bread in state.no_gluten_bread)):
            return bread
    return None

def infer_no_gluten_content(state: State) -> Optional[str]:
    """
    Class: Helper-State-Parameter-Inference

    Helper signature:
        infer_no_gluten_content(state)

    Helper parameters:
        state: current state

    Helper auxiliary parameters:
        None (inferred from None)

    Helper purpose:
        Find a no-gluten content-portion in the current state

    Helper returns:
        A no-gluten content-portion if found, None otherwise
    """
    # Check types
    # Python type checking: state must be a State
    if not (isinstance(state, State)):
        return None

    # No inferred auxiliary parameters

    # Find a gluten free content-portion in the kitchen
    for content in state.content_portions:
        if ((content in state.at_kitchen_content) and (content in state.no_gluten_content)):
            return content
    return None

def infer_with_gluten_bread(state: State) -> Optional[str]:
    """
    Class: Helper-State-Parameter-Inference

    Helper signature:
        infer_with_gluten_bread(state)

    Helper parameters:
        state: current state

    Helper auxiliary parameters:
        None (inferred from None)

    Helper purpose:
        Find a gluten bread-portion in the current state

    Helper returns:
        A gluten bread-portion if found, None otherwise
    """
    # Check types
    # Python type checking: state must be a State
    if not (isinstance(state, State)):
        return None

    # No inferred auxiliary parameters

    # Find a gluten bread-portion in the kitchen
    for bread in state.bread_portions:
        if ((bread in state.at_kitchen_bread) and (bread not in state.no_gluten_bread)):
            return bread
    return None

def infer_with_gluten_content(state: State) -> Optional[str]:
    """
    Class: Helper-State-Parameter-Inference

    Helper signature:
        infer_with_gluten_content(state)

    Helper parameters:
        state: current state

    Helper auxiliary parameters:
        None (inferred from None)

    Helper purpose:
        Find a gluten content-portion in the current state

    Helper returns:
        A gluten content-portion if found, None otherwise
    """
    # Check types
    # Python type checking: state must be a State
    if not (isinstance(state, State)):
        return None

    # No inferred auxiliary parameters

    # Find a gluten content-portion in the kitchen
    for content in state.content_portions:
        if ((content in state.at_kitchen_content) and (content not in state.no_gluten_content)):
            return content
    return None

def infer_non_existent_sandwich(state: State) -> Optional[str]:
    """
    Class: Helper-State-Parameter-Inference

    Helper signature:
        infer_non_existent_sandwich(state)

    Helper parameters:
        state: current state

    Helper auxiliary parameters:
        None (inferred from None)

    Helper purpose:
        Find a non-existent sandwich in the current state

    Helper returns:
        A non-existent sandwich if found, None otherwise
    """
    # Check types
    # Python type checking: state must be a State
    if not (isinstance(state, State)):
        return None

    # No inferred auxiliary parameters

    # Find a non-existent sandwich in the kitchen
    for sandwich in state.sandwiches:
        if (sandwich in state.notexist):
            return sandwich
    return None

# ============================================================================
# METHODS (2)
# ----------------------------------------------------------------------------
#   - m0_serve
#   - m1_serve
# ============================================================================

# (:method m0_serve
#   :parameters ( ?c - child ?s - sandwich ?b - bread-portion ?cont - content-portion ?t - tray ?p2 - place )
#   :task (serve ?c)
#   :precondition (and (allergic_gluten ?c) (notexist ?s) (waiting ?c ?p2) (no_gluten_bread ?b) (no_gluten_content ?cont))
#   :ordered-subtasks(and (t1 (make_sandwich_no_gluten ?s ?b ?cont)) (t2 (put_on_tray ?s ?t)) (t3 (move_tray ?t kitchen ?p2)) (t4 (serve_sandwich_no_gluten ?s ?c ?t ?p2)) (t5 (move_tray ?t ?p2 kitchen))) ) 
def m0_serve(state: State, c: str, p2: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m0_serve(state, c, p2)

    Method parameters:
        c: child
        p2: place

    Method auxiliary parameters:
        s: sandwich             (inferred from state)
        b: bread-portion        (inferred from state)
        cont: content-portion   (inferred from state)
        t: tray                 (inferred from state)

    Method purpose:
        Serve child c a no-gluten sandwich s made from no-gluten bread-portion b and no-gluten content-portion cont at place p2 using tray t

    Method returns:
        List of subtasks if successful, False otherwise
    """
    # Check types
    # Python type checking: state must be a State
    if not (isinstance(state, State)):
        return False
    # Python type checking: parameter c must be a string
    # Python type checking: parameter p2 must be a string
    if not (isinstance(c, str) and isinstance(p2, str)):
        return False
    # State type checking: parameter c must be a child
    # State type checking: parameter p2 must be a place
    if not ((c in state.children) and (p2 in state.places)): 
        return False

    # Inferred auxiliary parameters
    s = infer_non_existent_sandwich(state)
    b = infer_no_gluten_bread(state)
    cont = infer_no_gluten_content(state)
    t = infer_available_tray(state)

    # (and (allergic_gluten ?c) (notexist ?s) (waiting ?c ?p2) (no_gluten_bread ?b) (no_gluten_content ?cont))
    # -----> Check preconditions
    if not ((c in state.allergic_gluten) and 
            (s in state.notexist) and 
            (c in state.waiting and state.waiting[c] == p2) and 
            (b in state.no_gluten_bread) and 
            (cont in state.no_gluten_content)):
        return False

    # Return ordered subtask decomposition
    return [("make_sandwich_no_gluten", s, b, cont),
            ("put_on_tray", s, t),
            ("move_tray", t, "kitchen", p2),
            ("serve_sandwich_no_gluten", s, c, t, p2),
            ("move_tray", t, p2, "kitchen")]

# (:method m1_serve
#   :parameters ( ?c - child ?s - sandwich ?b - bread-portion ?cont - content-portion ?t - tray ?p2 - place )
#   :task (serve ?c)
#   :precondition (and (not_allergic_gluten ?c) (notexist ?s) (waiting ?c ?p2) (not(no_gluten_bread ?b)) (not(no_gluten_content ?cont)))
#   :ordered-subtasks(and (t1 (make_sandwich ?s ?b ?cont)) (t2 (put_on_tray ?s ?t)) (t3 (move_tray ?t kitchen ?p2)) (t4 (serve_sandwich ?s ?c ?t ?p2)) (t5 (move_tray ?t ?p2 kitchen))) ) 
def m1_serve(state: State, c: str, p2: str) -> Union[List[Tuple], bool]:
    """
    Class: Method

    Method signature:
        m1_serve(state, c, s, b, cont, t, p2)
    
    Method parameters:
        c: child
        p2: place

    Method auxiliary parameters:
        s: sandwich             (inferred from state)
        b: bread-portion        (inferred from state)   
        cont: content-portion   (inferred from state)
        t: tray                 (inferred from state)

    Method purpose:
        Serve child c a sandwich s made from bread-portion b and content-portion cont at place p2 using tray t

    Method returns:
        List of subtasks if successful, False otherwise
    """
    # Check types
    # Python type checking: state must be a State
    if not (isinstance(state, State)):
        return False
    # Python type checking: parameter c must be a string
    # Python type checking: parameter p2 must be a string
    if not (isinstance(c, str) and isinstance(p2, str)):
        return False
    # State type checking: parameter c must be a child
    # State type checking: parameter p2 must be a place
    if not ((c in state.children) and (p2 in state.places)): 
        return False

    # Inferred auxiliary parameters
    s = infer_non_existent_sandwich(state)
    b = infer_with_gluten_bread(state)
    cont = infer_with_gluten_content(state)
    t = infer_available_tray(state)

    # (and (not_allergic_gluten ?c) (notexist ?s) (waiting ?c ?p2) (not(no_gluten_bread ?b)) (not(no_gluten_content ?cont)))
    # -----> Check preconditions
    if not ((c in state.not_allergic_gluten) and 
            (s in state.notexist) and 
            (c in state.waiting and state.waiting[c] == p2) and 
            (b not in state.no_gluten_bread) and 
            (cont not in state.no_gluten_content)):
        return False
    
    # Return ordered subtask decomposition
    return [("make_sandwich", s, b, cont),
            ("put_on_tray", s, t),
            ("move_tray", t, "kitchen", p2),
            ("serve_sandwich", s, c, t, p2),
            ("move_tray", t, p2, "kitchen")]

# Declare methods to the domain
declare_task_methods("served", m0_serve, m1_serve)

# ============================================================================
# GOAL METHODS
# ============================================================================
declare_unigoal_methods("served", m0_serve, m1_serve)
declare_multigoal_methods(gtpyhop.m_split_multigoal)

# ============================================================================
# END OF FILE
# ============================================================================