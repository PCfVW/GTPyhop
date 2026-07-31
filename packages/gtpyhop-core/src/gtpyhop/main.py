# SPDX-FileCopyrightText: 2021 University of Maryland
# SPDX-License-Identifier: BSD-3-Clause-Clear

################################################################################
#                                                                              #
#                              GTPyhop 2.0.0                                   #
#                                                                              #
#                    Goal-Task-Network Planning System                         #
#                                                                              #
################################################################################

"""
GTPyhop 2.0.0: A Goal-Task-Network planning system with session-based architecture

GTPyhop is an automated planning system that can plan for both tasks and goals.
Version 1.3.0 introduces session-based planning for better isolation, structured
logging for improved debugging, timeout management, and persistence capabilities.
Version 1.5.0 introduces MCP orchestration examples.
Version 1.7.0 introduces enhanced MCP orchestration, bug fixes, and documentation updates.
Version 1.8.0 introduces accurate memory tracking with background monitoring using psutil.
Version 1.9.2 introduces iterative DFS planning with full backtracking via explicit stack.

Original Author: Dana Nau <nau@umd.edu>, July 7, 2021
pip install project architecture: Eric Jacopin, 2025
Session Architecture: Eric Jacopin, 2025
Memory Tracking: Eric Jacopin, 2026
Iterative Backtracking: Eric Jacopin, 2026

Key Features:
- Hierarchical Task Network (HTN) planning
- Goal-oriented planning with multigoals
- Three planning strategies: recursive DFS, iterative greedy, iterative DFS with backtracking
- Session-based architecture for isolation and concurrency
- Structured logging with programmatic access
- Cross-platform timeout enforcement and resource management
- Session persistence and recovery mechanisms
- Memory tracking with accurate peak detection via background monitoring
- 100% backward compatibility with GTPyhop v1.2.1

Iterative DFS Backtracking (New in 1.9.0):
- Combines the iterative planner's explicit stack with the recursive planner's
  ability to backtrack across methods
- When a task has multiple applicable methods, all continuations are pushed onto
  the stack; if one path fails, the planner falls back to the next alternative
- Activated via set_recursive_planning("iterative_dfs_backtracking") or
  PlannerSession(strategy="iterative_dfs_backtracking")
- No Python recursion depth limit; safe because methods are read-only

Memory Tracking (New in 1.8.0):
- Uses psutil for real memory measurement (not time-based estimates)
- Background thread sampling (0.1s interval) captures true peak memory
- Disabled by default (memory_tracking=False) - no overhead unless enabled
- Graceful fallback when psutil is unavailable

    with PlannerSession(domain=my_domain, memory_tracking=True) as session:
        result = session.find_plan(state, tasks)
        print(f"Peak memory: {result.stats['peak_memory_mb']:.2f} MB")

This file contains the complete GTPyhop implementation organized into logical
sections for improved maintainability while preserving the single-file
architecture that makes GTPyhop easy to understand and deploy.

This package (gtpyhop-core) contains the planner only. Example domains showing
how to use GTPyhop live in the separate gtpyhop-examples package (installed
automatically by `pip install gtpyhop`, or directly via `pip install
gtpyhop-examples`); once installed, try importing any of the modules under
gtpyhop.examples.
"""

# For use in debugging:
# from IPython import embed
# from IPython.terminal.debugger import set_trace

################################################################################
#                                                                              #
#                               IMPORTS                                        #
#                                                                              #
################################################################################

# Standard library imports
import copy, re
import time
import threading
import uuid
import signal
import sys
import tracemalloc
import json
import pickle
import os
import atexit
import warnings

# Type hints and modern Python features
from typing import Optional, List, Dict, Any, Tuple, Union
from dataclasses import dataclass, field
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

# Import structured logging system (optional - graceful fallback if not available)
try:
    from .logging_system import get_logger, LogLevel, LegacyPrintReplacer, destroy_logger
    _STRUCTURED_LOGGING_AVAILABLE = True
except ImportError:
    _STRUCTURED_LOGGING_AVAILABLE = False
    get_logger = None
    LogLevel = None
    LegacyPrintReplacer = None
    destroy_logger = None

################################################################################
#                                                                              #
#                          LOGGING AND UTILITIES                              #
#                                                                              #
################################################################################

"""
This section contains logging infrastructure, utility functions, and helper
methods that support the core GTPyhop functionality.

Key Components:
- Verbose printing and logging configuration
- Structured logging integration with graceful fallback
- Utility functions for object representation and type checking
- Helper functions for string formatting and debugging
- Cross-references: Used throughout all other sections

Design Notes:
- Structured logging is optional - system gracefully degrades to print statements
- Global verbose level controls output across all planning operations
- Utility functions provide consistent object representation and debugging support
"""

################################################################################
# Global Configuration and Logging Infrastructure

# How much information to print while the program is running
verbose = 1

# Active PlanTrace instance during a find_plan(..., trace=True) call, or
# None otherwise. Set/restored by PlannerSession.isolated_execution(),
# mirroring how `verbose` and `current_domain` are already handled.
_trace_collector = None

# Whether the active trace should also snapshot the state each event was
# recorded against (find_plan(..., trace_state=True)). Kept as a separate
# global from _trace_collector because snapshotting deep-copies the state
# once per event, which is far more expensive than recording the event
# itself -- so plain trace=True must not pay for it. Set/restored alongside
# _trace_collector by PlannerSession.isolated_execution().
_trace_state = False

# Global structured logging support
_global_logger = None
_legacy_print_replacer = None

def _get_global_logger():
    """Get or create the global logger instance."""
    global _global_logger, _legacy_print_replacer
    if _STRUCTURED_LOGGING_AVAILABLE and _global_logger is None:
        _global_logger = get_logger("gtpyhop_global")
        _legacy_print_replacer = LegacyPrintReplacer(_global_logger, "gtpyhop")
    return _global_logger

def _log_if_available(level, component, message, **context):
    """Log a message if structured logging is available."""
    logger = _get_global_logger()
    if logger:
        if level == "debug":
            logger.debug(component, message, **context)
        elif level == "info":
            logger.info(component, message, **context)
        elif level == "warning":
            logger.warning(component, message, **context)
        elif level == "error":
            logger.error(component, message, **context)

def _verbose_print_and_log(message, verbose_level=1, component="gtpyhop", end='\n'):
    """Print message if verbose >= verbose_level and also log it."""
    if verbose >= verbose_level:
        print(message, end=end)

    # Also log the message
    if verbose_level <= 1:
        _log_if_available("info", component, message, verbose_level=verbose_level)
    elif verbose_level <= 2:
        _log_if_available("debug", component, message, verbose_level=verbose_level)
    else:
        _log_if_available("debug", component, message, verbose_level=verbose_level)


def set_verbose_level(level):
    """
    Set the verbosity (initial value is 1) level to determines how much debugging
    information GTPyhop will print:
    - level = 0: print nothing
    - level = 1: print the initial parameters and the answer
    - level = 2: also print a message on each recursive call
    - level = 3: also print some info about intermediate computations
   """
    global verbose
    if level < 0 or level > 3:
        raise ValueError("Verbose level must be between 0 and 3.")
    verbose = level
    print(f"Verbose level set to {verbose}.")


def get_verbose_level():
    """
    Returns the current verbosity level.
    """
    return verbose 

################################################################################
#                                                                              #
#                        DOMAIN AND STATE MANAGEMENT                          #
#                                                                              #
################################################################################

"""
This section contains the core data structures and management functions for
GTPyhop's planning domains, states, and goals.

Key Components:
- State class: Represents world states with state variables
- Multigoal class: Represents collections of goals to achieve
- Domain class: Contains actions, commands, and methods for a planning domain
- Domain management functions: Create, find, and manage planning domains
- State and goal utilities: Printing, copying, and manipulation functions

Cross-references:
- Used by Core Planning Algorithms for planning operations
- Used by Session-Based Architecture for domain-specific sessions
- Integrates with Logging and Utilities for debugging and representation

Design Notes:
- States use dynamic attribute assignment for flexible state variables
- Domains encapsulate all knowledge (actions, methods) for a planning problem
- Multigoals support complex goal structures with conjunctions and disjunctions
"""

################################################################################
# State Management

# Sequence number to use when making copies of states.
_next_state_number = 0

class State():
    """
    s = State(state_name, **kwargs) creates an object that contains the
    state-variable bindings for a state-of-the-world.
      - state_name is the name to use for the new state.
      - The keyword args are the names and initial values of state variables.
        A state-variable's initial value is usually {}, but it can also
        be a dictionary of arguments and their initial values.
    
    Example: here are three equivalent ways to specify a state named 'foo'
    in which boxes b and c are located in room2 and room3:
        First:
           s = State('foo')
           s.loc = {}   # create a dictionary for things like loc['b']
           s.loc['b'] = 'room2'
           s.loc['c'] = 'room3'
        Second:
           s = State('foo',loc={})
           s.loc['b'] = 'room2'
           s.loc['c'] = 'room3'
        Third:
           s = State('foo',loc={'b':'room2', 'c':'room3'})
    """
    
    def __init__(self, state_name, **kwargs):
        """
        state_name is the name to use for the state. The keyword
        args are the names and initial values of state variables.
        """
        self.__name__ = state_name
        vars(self).update(kwargs)
            
    def __str__(self):
        return f"<State {self.__name__}>"
        
    def __repr__(self):
        return _make_repr(self, 'State')

    def __eq__(self, other):
        if not isinstance(other, State):
            return False
        for v in vars(self):
            if v != '__name__':     # don't compare state names
                if v not in vars(other):
                    return False
                if vars(self)[v] != vars(other)[v]:
                    return False
        for v in vars(other):
            if v != '__name__':     # don't compare state names
                if v not in vars(self):
                    return False
        return True
    
    def __ne__(self, other):
        return not self.__eq__(other)

    def copy(self,new_name=None):
        """
        Make a copy of the state. For its name, use new_name if it is given.
        Otherwise use the old name, with a suffix '_copy#' where # is an integer.
        """
        global _next_state_number
        the_copy = copy.deepcopy(self)
        if new_name:
            the_copy.__name__ = new_name
        else:
            the_copy.__name__ = _name_for_copy(the_copy.__name__, _next_state_number)
            _next_state_number += 1
        return the_copy

    def display(self, heading=None):
        """
        Print the state's state-variables and their values.
         - heading (optional) is a heading to print beforehand.
        """
        _print_object(self, heading=heading)

    def state_vars(self):
        """Return a list of all state-variable names in the state"""
        return [v for v in vars(self) if v != '__name__']


# Sequence number to use when making copies of multigoals.
_next_multigoal_number = 0

class Multigoal():
    """
    g = Multigoal(goal_name, **kwargs) creates an object that represents
    a conjunctive goal, i.e., the goal of reaching a state that contains
    all of the state-variable bindings in g.
      - goal_name is the name to use for the new multigoal.
      - The keyword args are name and desired values of state variables.

    Example: here are three equivalent ways to specify a goal named 'goal1'
    in which boxes b and c are located in room2 and room3:
        First:
           g = Multigoal('goal1')
           g.loc = {}   # create a dictionary for things like loc['b']
           g.loc['b'] = 'room2'
           g.loc['c'] = 'room3'
        Second:
           g = Multigoal('goal1', loc={})
           g.loc['b'] = 'room2'
           g.loc['c'] = 'room3'
        Third:
           g = Multigoal('goal1',loc={'b':'room2', 'c':'room3'})
    """

    def __init__(self, multigoal_name, **kwargs):
        """
        multigoal_name is the name to use for the multigoal. The keyword
        args are the names and desired values of state variables.
        """
        self.__name__ = multigoal_name
        vars(self).update(kwargs)
            
    def __str__(self):
        return f"<Multigoal {self.__name__}>"
        
    def __repr__(self):
        return _make_repr(self, 'Multigoal')

    def copy(self,new_name=None):
        """
        Make a copy of the multigoal. For its name, use new_name if it is given.
        Otherwise use the old name, with a suffix '_copy#' where # is an integer.
        """
        global _next_multigoal_number
        the_copy = copy.deepcopy(self)
        if new_name:
            the_copy.__name__ = new_name
        else:
            the_copy.__name__ = _name_for_copy(the_copy.__name__, _next_multigoal_number)
            _next_multigoal_number += 1
        return the_copy

    def display(self, heading=None):
        """
        Print the multigoal's state-variables and their values.
         - heading (optional) is a heading to print beforehand.
        """
        _print_object(self, heading=heading)

    def state_vars(self):
        """Return a list of all state-variable names in the multigoal"""
        return [v for v in vars(self) if v != '__name__']


################################################################################
# Auxiliary functions for state and multigoal objects.


def _make_repr(object, class_name):
    """Return a string that can be used to reconstruct the object"""
    x = f"{class_name}('{object.__name__}', "
    x += ', '.join([f'{v}={vars(object)[v]}' for v in vars(object) if v != '__name__'])
    x += ')'
    return x
    

def _name_for_copy(old_name,next_integer):
    """
    Create a name to use for a copy of an object.
    - old_name is the name of the old object.
    - next_integer is the number to use at the end of the new name.
    """
    # if old_name ends in '_copy#' where # is an integer, then
    # just replace # with next_integer
    if re.findall('_copy_[0-9]*$',old_name):
        new_name = re.sub('_[0-9]*$', f'_{next_integer}', old_name)
    # otherwise use old_name with '_copy' and next_integer appended
    else:
        new_name = f'{old_name}_copy_{next_integer}'
    return new_name


def _print_object(object, heading=None):
    """
    Print the state-variables and values in 'object', which may be either a
    state or a multigoal. 'heading' is an optional heading to print beforehand.
    """
    if heading == None:
        heading = get_type(object)
    if object != False:
        title = f"{heading} {object.__name__}:"
        dashes = '-'*len(title)
        print(title)
        print(dashes)
        for (varname,val) in vars(object).items():
            if varname != '__name__':
                print(f"  - {varname} = {val}")
        print('')
    else: 
        print('{heading} = False','\n')


# print_state and print_multigoal are identical except for their names.
print_state = _print_object
print_multigoal = _print_object

def get_type(object):
    """Return object's type name"""
    return type(object).__name__


################################################################################
# Domain Class and Management

class Domain():
    """
    d = Domain(domain_name) creates an object to contain the actions, commands,
    and methods for a planning-and-acting domain. 'domain_name' is the name to
    use for the new domain.
    """

    def __init__(self,domain_name):
        """domain_name is the name to use for the domain."""

        global _domains, current_domain
        
        self.__name__ = domain_name

        _domains.append(self)
        current_domain = self
        
        # dictionary that maps each action name to the corresponding function
        self._action_dict = {}    
            
        # dictionary that maps each command name to the corresponding function
        self._command_dict = {}
        
        # dictionary that maps each task name to a list of relevant methods
        # _verify_g and _verify_mg are described later in this file.
        self._task_method_dict = \
            {'_verify_g': [_m_verify_g], '_verify_mg': [_m_verify_mg]}
        
        # dictionary that maps each unigoal name to a list of relevant methods
        self._unigoal_method_dict = {}
        
        # list of all methods for multigoals
        self._multigoal_method_list = []

    def __str__(self):
        return f"<Domain {self.__name__}>"
        
    def __repr__(self):
        return _make_repr(self, 'Domain')

    def copy(self,new_name=None):
        """
        Make a copy of the domain. For its name, use new_name if it is given.
        Otherwise use the old name, with a suffix '_copy#' where # is an integer.
        """
        global _next_domain_number
        the_copy = copy.deepcopy(self)
        if new_name:
            the_copy.__name__ = new_name
        else:
            the_copy.__name__ = _name_for_copy(the_copy.__name__, _next_domain_number)
            _next_domain_number += 1
        return the_copy

    def display(self):
        """Print the domain's actions, commands, and methods."""
        print_domain(self)
        

# Sequence number to use when making copies of domains.
_next_domain_number = 0

# A list of all domains that have been created
_domains = []

################################################################################
# Domain Management Functions

def print_domain_names():
    """
    Print the names of all domains that have been created.
    """
    if _domains:
        print('-- Domain names:', ', '.join([d.__name__ for d in _domains]))
    else:
        print('-- There are no domains --')


def find_domain_by_name(domain_name):
    """
    Search for a domain by its name in the _domains list.

    :param domain_name: The name of the domain to search for.
    :return: The domain instance if found, otherwise None.
    """
    for domain in _domains:
        if domain.__name__ == domain_name:
            return domain
    return None

def is_domain_created(domain_name):
    """
    Check if a domain with the given name has been created in the _domains list.

    :param domain_name: The name of the domain to check.
    :return: True if the domain is found, otherwise False.
    """
    for domain in _domains:
        if domain.__name__ == domain_name:
            return True
    return False

current_domain = None
"""
The Domain object that find_plan, run_lazy_lookahead, etc., will use.
"""

def set_current_domain(domain):
    """
    Set the current domain to the specified domain object.
    
    :param domain: The Domain object to set as the current domain.
    """
    global current_domain
    if not isinstance(domain, Domain):
        raise TypeError("The provided argument is not a Domain instance.")
    current_domain = domain

def get_current_domain():
    """
    Get the current domain object.
    
    :return: The current Domain object.
    """
    return current_domain

################################################################################
# Functions to print information about a domain


def print_domain(domain=None):
    """
    Print domain's actions, commands, and methods. The optional 'domain'
    argument defaults to the current domain
    """
    if domain == None:
        domain = current_domain
    print(f'\nDomain name: {domain.__name__}')
    print_actions(domain)
    print_commands(domain)
    print_methods(domain)

def print_actions(domain=None):
    """Print the names of all the actions"""
    if domain == None:
        domain = current_domain
    if domain._action_dict:
        print('-- Actions:', ', '.join(domain._action_dict))
    else:
        print('-- There are no actions --')

def print_operators():
    if verbose > 0:
        print("""
        >> print_operators exists to provide backward compatibility
        >> with Pyhop. In the future, please use print_actions instead.""")
    return print_actions()

def print_commands(domain=None):
    """Print the names of all the commands"""
    if domain == None:
        domain = current_domain
    if domain._command_dict:
        print('-- Commands:', ', '.join(domain._command_dict))
    else:
        print('-- There are no commands --')

def _print_task_methods(domain):
    """Print a table of the task_methods for each task"""
    if domain._task_method_dict:
        print('')
        print('Task name:         Relevant task methods:')
        print('---------------    ----------------------')
        for task in domain._task_method_dict:
            print(f'{task:<19}' + ', '.join(    \
                [f.__name__ for f in domain._task_method_dict[task]]))
        print('')
    else:
        print('-- There are no task methods --')

def _print_unigoal_methods(domain):
    """Print a table of the unigoal_methods for each state_variable_name"""
    if domain._unigoal_method_dict:
        print('State var name:    Relevant unigoal methods:')
        print('---------------    -------------------------')
        for var in domain._unigoal_method_dict:
            print(f'{var:<19}' + ', '.join( \
                [f.__name__ for f in domain._unigoal_method_dict[var]]))
        print('')
    else:
        print('-- There are no unigoal methods --')

def _print_multigoal_methods(domain):
    """Print the names of all the multigoal_methods"""
    if domain._multigoal_method_list:
        print('-- Multigoal methods:', ', '.join(  \
                [f.__name__ for f in domain._multigoal_method_list]))
    else:
        print('-- There are no multigoal methods --')
    
def print_methods(domain=None):
    """Print tables showing what all the methods are"""
    if domain == None:
        domain = current_domain
    _print_task_methods(domain)
    _print_unigoal_methods(domain)
    _print_multigoal_methods(domain)


################################################################################
# Functions to declare actions, commands, tasks, unigoals, multigoals


def declare_actions(*actions):
    """
    declare_actions adds each member of 'actions' to the current domain's list
    of actions. For example, this says that pickup and putdown are actions:
        declare_actions(pickup,putdown)
        
    declare_actions can be called multiple times to add more actions.
    
    You can see the current domain's list of actions by executing
        current_domain.display()
    """
    if current_domain == None:
        raise Exception(f"cannot declare actions until a domain has been created.")
    current_domain._action_dict.update({act.__name__:act for act in actions})
    return current_domain._action_dict



def declare_operators(*actions):
    if verbose > 0:
        print("""
        >> declare_operators exists to provide backward compatibility
        >> with Pyhop. In the future, please use declare_actions instead.""")
    return declare_actions(*actions)


def declare_commands(*commands):
    """
    declare_commands adds each member of 'commands' to the current domain's
    list of commands.  Each member of 'commands' should be a function whose
    name has the form c_foo, where foo is the name of an action. For example,
    this says that c_pickup and c_putdown are commands:
        declare_commands(c_pickup,c_putdown)
    
    declare_commands can be called several times to add more commands.

    You can see the current domain's list of commands by executing
        current_domain.display()

    """
    if current_domain == None:
        raise Exception(f"cannot declare commands until a domain has been created.")
    current_domain._command_dict.update({cmd.__name__:cmd for cmd in commands})
    return current_domain._command_dict


def declare_task_methods(task_name, *methods):
    """
    'task_name' should be a character string, and 'methods' should be a list
    of functions. declare_task_methods adds each member of 'methods' to the
    current domain's list of methods to use for tasks of the form
        (task_name, arg1, ..., argn).     

    Example:
        declare_task_methods('travel', travel_by_car, travel_by_foot)
    says that travel_by_car and travel_by_foot are methods and that GTPyhop
    should try using them for any task whose task name is 'travel', e.g.,
        ('travel', 'alice', 'store')
        ('travel', 'alice', 'umd', 'ucla')
        ('travel', 'alice', 'umd', 'ucla', 'slowly')
        ('travel', 'bob', 'home', 'park', 'looking', 'at', 'birds')

    This is like Pyhop's declare_methods function, except that it can be
    called several times to declare more methods for the same task.
    """
    if current_domain == None:
        raise Exception(f"cannot declare methods until a domain has been created.")
    if task_name in current_domain._task_method_dict:
        old_methods = current_domain._task_method_dict[task_name]
        # even though current_domain._task_method_dict[task_name] is a list,
        # we don't want to add any methods that are already in it
        new_methods = [m for m in methods if m not in old_methods]
        current_domain._task_method_dict[task_name].extend(new_methods)
    else:
        current_domain._task_method_dict.update({task_name:list(methods)})
    return current_domain._task_method_dict


def declare_methods(task, *methods):
    if verbose > 0:
        print("""
        >> declare_methods exists to provide backward compatibility with
        >> Pyhop. In the future, please use declare_task_methods instead.""")
    return declare_task_methods(task, *methods)


def declare_unigoal_methods(state_var_name, *methods):
    """
    'state_var_name' should be a character string, and 'methods' should be a
    list of functions. declare_unigoal_method adds each member of 'methods'
    to the current domain's list of relevant methods for goals of the form
        (state_var_name, arg, value)
    where 'arg' and 'value' are the state variable's argument and the desired
    value. For example,
        declare_unigoal_method('loc',travel_by_car)
    says that travel_by_car is relevant for goals such as these:
        ('loc', 'alice', 'ucla')
        ('loc', 'bob', 'home')

    The above kind of goal, i.e., a desired value for a single state
    variable, is called a "unigoal". To achieve a unigoal, GTPyhop will go
    through the unigoal's list of relevant methods one by one, trying each
    method until it finds one that is successful.

    To see each unigoal's list of relevant methods, use
        current_domain.display()    
    """
    if current_domain == None:
        raise Exception(f"cannot declare methods until a domain has been created.")
    if state_var_name not in current_domain._unigoal_method_dict:
        current_domain._unigoal_method_dict.update({state_var_name:list(methods)})
    else:
        old_methods = current_domain._unigoal_method_dict[state_var_name]
        new_methods = [m for m in methods if m not in old_methods]
        current_domain._unigoal_method_dict[state_var_name].extend(new_methods)
    return current_domain._unigoal_method_dict    


def declare_multigoal_methods(*methods):
    """
    declare_multigoal_methods adds each method in 'methods' to the current
    domain's list of multigoal methods. For example, this says that
    stack_all_blocks and unstack_all_blocks are multigoal methods:
        declare_multigoal_methods(stack_all_blocks, unstack_all_blocks)
    
    When GTPyhop tries to achieve a multigoal, it will go through the list
    of multigoal methods one by one, trying each method until it finds one
    that is successful. You can see the list by executing
        current_domain.display()

    declare_multigoal_methods can be called multiple times to add more
    multigoal methods to the list.
    
    For more information, see the docstring for the Multigoal class.
    """
    if current_domain == None:
        raise Exception(    \
                f"cannot declare methods until a domain has been created.")
    new_mg_methods = [m for m in methods if m not in \
                      current_domain._multigoal_method_list]
    current_domain._multigoal_method_list.extend(new_mg_methods)
    return current_domain._multigoal_method_list    

    
################################################################################
# A built-in multigoal method and its helper function.


def m_split_multigoal(state,multigoal):
    """
    m_split_multigoal is the only multigoal method that GTPyhop provides,
    and GTPyhop won't use it unless the user declares it explicitly using
        declare_multigoal_methods(m_split_multigoal)

    The method's purpose is to try to achieve a multigoal by achieving each
    of the multigoal's individual goals sequentially. Parameters:
        - 'state' is the current state
        - 'multigoal' is the multigoal to achieve 

    If multigoal is true in the current state, m_split_multigoal returns
    []. Otherwise, it returns a goal list
        [g_1, ..., g_n, multigoal],

    where g_1, ..., g_n are all of the goals in multigoal that aren't true
    in the current state. This tells the planner to achieve g_1, ..., g_n
    sequentially, then try to achieve multigoal again. Usually this means
    m_split_multigal will be used repeatedly, until it succeeds in producing
    a state in which all of the goals in multigoal are simultaneously true.

    The main problem with m_split_multigoal is that it isn't smart about
    choosing the order in which to achieve g_1, ..., g_n. Some orderings may
    work much better than others. Thus, rather than using the method as it's
    defined below, one might want to modify it to choose a good order, e.g.,
    by using domain-specific information or a heuristic function.
    """
    goal_dict = _goals_not_achieved(state,multigoal)
    goal_list = []
    for state_var_name in goal_dict:
        for arg in goal_dict[state_var_name]:
            val = goal_dict[state_var_name][arg]
            goal_list.append((state_var_name,arg,val))
    if goal_list:
        # achieve goals, then check whether they're all simultaneously true
        return goal_list + [multigoal]
    return goal_list


# helper function for m_split_multigoal above:

def _goals_not_achieved(state,multigoal):
    """
    _goals_not_achieved takes two arguments: a state s and a multigoal g.
    It returns a dictionary of the goals in g that aren't true in s.
    For example, suppose
        s.loc['c0'] = 'room0', g.loc['c0'] = 'room0',
        s.loc['c1'] = 'room1', g.loc['c1'] = 'room3',
        s.loc['c2'] = 'room2', g.loc['c2'] = 'room4'.
    Then _goals_not_achieved(s, g) will return
        {'loc': {'c1': 'room3', 'c2': 'room4'}}    
    """
    unachieved = {}
    for name in vars(multigoal):
        if name != '__name__':
            for arg in vars(multigoal).get(name):
                val = vars(multigoal).get(name).get(arg)
                if val != vars(state).get(name).get(arg):
                    # want arg_value_pairs.name[arg] = val
                    if not unachieved.get(name):
                        unachieved.update({name:{}})
                    unachieved.get(name).update({arg:val})
    return unachieved


################################################################################
# Functions to verify whether unigoal_methods achieve the goals they are
# supposed to achieve.


verify_goals = True
"""
If verify_goals is True, then whenever the planner uses a method m to refine
a unigoal or multigoal, it will insert a "verification" task into the
current partial plan. If verify_goals is False, the planner won't insert any
verification tasks into the plan.

The purpose of the verification task is to raise an exception if the
refinement produced by m doesn't achieve the goal or multigoal that it is
supposed to achieve. The verification task won't insert anything into the
final plan; it just will verify whether m did what it was supposed to do.
"""


def _m_verify_g(state, method, state_var, arg, desired_val, depth):
    """
    _m_verify_g is a method that GTPyhop uses to check whether a
    unigoal method has achieved the goal for which it was used.
    """
    if vars(state)[state_var][arg] != desired_val:
        raise Exception(f"depth {depth}: method {method} didn't achieve",
                f"goal {state_var}[{arg}] = {desired_val}")
    if verbose >= 3:
        print(f"depth {depth}: method {method} achieved",
                f"goal {state_var}[{arg}] = {desired_val}")
    return []       # i.e., don't create any subtasks or subgoals


def _m_verify_mg(state, method, multigoal, depth):
    """
    _m_verify_g is a method that GTPyhop uses to check whether a multigoal
    method has achieved the multigoal for which it was used.
    """
    goal_dict = _goals_not_achieved(state,multigoal)
    if goal_dict:
        raise Exception(f"depth {depth}: method {method} " + \
                        f"didn't achieve {multigoal}]")
    if verbose >= 3:
        print(f"depth {depth}: method {method} achieved {multigoal}")
    return []


################################################################################
# Function to validate a plan by executing its actions from the initial state
# and checking the goal is achieved when given

def validate_plan_from_goal(initial_state: State, plan, key_string: str = "", goal_dict: dict = []):
    """
    Validate a given plan by applying each action in sequence to the initial state.
    After executing the plan, check if the resulting state satisfies the goal state.
    Args:
        initial_state (State): The initial state before the plan is executed.
        plan (list): A list of actions to be executed in sequence.
        key_string: a string representing one attribute of the state to check.
        goal_dict (State): A dictionary representing one attribute of the final state and its desired values.
    Returns:
        bool: True if the plan leads to the goal_dict is a subset of the initial_state_dict, False otherwise.
    """
    state = initial_state.copy()
    if verbose >= 1:
        print(f'Validating plan: {plan}')
        if verbose == 2:
            print(state.__str__())
        else:   # verbose >= 3
            state.display('Initial state:')

    action_counter = 0
    for action in plan:
        if action[0] in current_domain._action_dict:
            action_func = current_domain._action_dict[action[0]]
            newstate = state.copy()
            state = action_func(newstate, *action[1:])
            action_counter += 1
            if state is False:
                if verbose >= 1:
                    print(f'Action {action} (#{action_counter}) failed. Plan is invalid.')
                return False
            if verbose == 2:
                print(f'New state after action {action[0]} (#{action_counter}): {state.__str__()}')
            elif verbose >= 3:
                print(f'New state after action {action} (#{action_counter}):')
                state.display()
        else:
            if verbose >= 1:
                print(f'Action {action} not found in domain. Plan is invalid.')
            return False

    # If no key_string or goal_dict is provided, just validate the plan execution
    if key_string == "" or goal_dict == []:
        if verbose >= 1:
            print(f'>>> {action_counter}-action Plan is valid.')
        return True

    # Check if the goal_dict is satisfied in the final state
    for arg, val in goal_dict.get(key_string, {}).items():
        if vars(state).get(key_string, {}).get(arg) != val:
            if verbose >= 1:
                print(f'Goal {key_string}[{arg}] = {val} not achieved. Plan is invalid.')
            return False
    if verbose >= 1:
        print(f'>>> {action_counter}-action Plan is valid and achieves the goal.')
    return True

################################################################################
#                                                                              #
#                         CORE PLANNING ALGORITHMS                            #
#                                                                              #
################################################################################

"""
This section contains the core HTN planning algorithms that form the heart
of GTPyhop's planning capabilities.

Key Components:
- Recursive Planning: seek_plan_recursive and supporting functions
- Iterative Planning: seek_plan_iterative and supporting functions
- Action Application: Functions to apply actions and continue planning
- Task Refinement: Functions to decompose tasks using methods
- Goal Achievement: Functions to achieve unigoals and multigoals
- Plan Finding: Main entry points (find_plan, pyhop) for planning

Cross-references:
- Uses Domain and State Management for accessing domains and states
- Used by Session-Based Architecture for session-specific planning
- Integrates with Logging and Utilities for debugging and verbose output

Design Notes:
- Supports three planning strategies: recursive DFS, iterative greedy, and
  iterative DFS with backtracking
- Recursive DFS uses Python's call stack for backtracking
- Iterative greedy uses explicit stack but commits to first applicable method
- Iterative DFS backtracking uses explicit stack and pushes all applicable
  method continuations, enabling backtracking without recursion depth limits
- All planning respects the global verbose level for output control
"""

################################################################################
# Recursive Planning Implementation


def _action_failure_status(returned_value):
    """
    Classify what an action returned when it did not return a State.

    False and None are both legitimate "this action's preconditions did not
    hold" signals:

      - False is what this project's own style guide teaches, and what the
        newer bundled example collections use.
      - None is what GTPyhop's original examples have always done -- the
        canonical `if <preconditions>: <effects>; return s` shape simply
        falls off the end of the function when the guard is false, with no
        explicit return at all. That is how blocks_htn, blocks_gtn,
        blocks_hgn, blocks_goal_splitting, simple_htn, simple_hgn,
        logistics_hgn and backtracking_htn are all written.

    Treating None as malformed would therefore label GTPyhop's own teaching
    examples as buggy, and would contradict the method-refinement paths,
    which have always accepted None as an ordinary "not applicable"
    (`subtasks != False and subtasks != None`).

    Anything else -- True, a string, an int, a list -- really does violate
    the contract, and remains "malformed_return". That is the case worth
    catching: an action that returns True instead of the state silently
    discards its own effects while looking successful.
    """
    if returned_value is False or returned_value is None:
        return "not_applicable"
    return "malformed_return"


def _record_trace_event(depth, item, status, returned_value=None, state=None):
    """
    Record one action-application or method-refinement attempt into the
    active PlanTrace, if find_plan(..., trace=True) is in effect for the
    current call (_trace_collector is None otherwise, in which case this is
    a no-op). Shared by the recursive, iterative, and iterative-backtracking
    action-application and refinement paths, so all three planning
    strategies produce traces through the same code path.

    state is the state the item was attempted against; it is snapshotted
    into the event only when find_plan(..., trace_state=True) asked for it
    (see TraceEvent.state). Callers pass the state they *called the action
    or method on*, never the state an action returned -- the diagnostic
    question is which preconditions held at the moment of the attempt.
    """
    if _trace_collector is None:
        return
    detail = None
    if status in ("malformed_return", "method_malformed_return"):
        detail = f"returned {type(returned_value).__name__}: {returned_value!r:.200}"
    snapshot = None
    if _trace_state and state is not None:
        # A plain copy.deepcopy, deliberately not State.copy(): the latter
        # renames the copy and bumps the global _next_state_number, which
        # would make merely *observing* a search change the auto-generated
        # names of states produced after it.
        try:
            snapshot = copy.deepcopy(state)
        except Exception:
            # An uncopyable object in a state variable must not take down
            # the search being diagnosed; the event is still worth having
            # without its snapshot.
            snapshot = None
    _trace_collector.record(depth=depth, item=item, status=status, detail=detail,
                            state=snapshot)


def _apply_action_and_continue_recursive(state, task1, todo_list, plan, depth):
    """
    _apply_action_and_continue is called only when task1's name matches an
    action name. It applies the action by retrieving the action's function
    definition and calling it on the arguments, then calls seek_plan
    recursively on todo_list.
    """
    if verbose >= 3:
        print(f'depth {depth} action {task1}: ', end='')
    action = current_domain._action_dict[task1[0]]
    
    # Create a copy of the state to avoid modifying the original
    state_copy = state.copy()
    # Apply the action to the copied state
    newstate = action(state_copy,*task1[1:])

    if isinstance(newstate, State):
        if (newstate != state): # == and != are overloaded for State; only attributes matter; state name doesn't
            # action changed the state: record it in the plan
            if verbose >= 3:
                print('applied')
                newstate.display()
            _record_trace_event(depth, task1, "applied", state=state)
            return seek_plan_recursive(newstate, todo_list, plan+[task1], depth+1)
        else:
            # action didn't change the state: don't record it in the plan
            if verbose >= 3:
                print('idempotent')
                newstate.display()
            _record_trace_event(depth, task1, "idempotent", state=state)
            return seek_plan_recursive(newstate, todo_list, plan, depth+1)

    if verbose >= 3:
        print('not applicable')
    _record_trace_event(depth, task1, _action_failure_status(newstate), newstate, state=state)
    return False


def _refine_task_and_continue_recursive(state, task1, todo_list, plan, depth):
    """
    If task1 is in the task-method dictionary, then iterate through the list
    of relevant methods to find one that's applicable, apply it to get
    additional todo_list items, and call seek_plan recursively on
            [the additional items] + todo_list.

    If the call to seek_plan_recursive fails, go on to the next method in the list.
    """
    relevant = current_domain._task_method_dict[task1[0]]
    if verbose >= 3:
        print(f'depth {depth} task {task1} methods {[m.__name__ for m in relevant]}')
    for method in relevant:
        if verbose >= 3:
            print(f'depth {depth} trying {method.__name__}: ', end='')
        subtasks = method(state, *task1[1:])
        # Can't just say "if subtasks:", because that's wrong if subtasks == []
        if subtasks != False and subtasks != None:
            if verbose >= 3:
                print('applicable')
                print(f'depth {depth} subtasks: {subtasks}')
            _record_trace_event(depth, task1,
                "method_applicable" if isinstance(subtasks, list) else "method_malformed_return",
                subtasks, state=state)
            result = seek_plan_recursive(state, subtasks+todo_list, plan, depth+1)
            if result != False and result != None:
                return result
        else:
            if verbose >= 3:
                print(f'not applicable')
            _record_trace_event(depth, task1, "method_not_applicable", state=state)
    if verbose >= 3:
        print(f'depth {depth} could not accomplish task {task1}')
    _record_trace_event(depth, task1, "task_exhausted", state=state)
    return False


def _refine_unigoal_and_continue_recursive(state, goal1, todo_list, plan, depth):
    """
    If goal1 is in the unigoal-method dictionary, then iterate through the
    list of relevant methods to find one that's applicable, apply it to get
    additional todo_list items, and call seek_plan recursively on
          [the additional items] + [verify_g] + todo_list,

    where [verify_g] verifies whether the method actually achieved goal1.
    If the call to seek_plan_recursive fails, go on to the next method in the list.
    """
    if verbose >= 3:
        print(f'depth {depth} goal {goal1}: ', end='')
    (state_var_name, arg, val) = goal1
    if vars(state).get(state_var_name).get(arg) == val:
        if verbose >= 3:
            print(f'already achieved')
        return seek_plan_recursive(state, todo_list, plan, depth+1)
    relevant = current_domain._unigoal_method_dict[state_var_name]
    if verbose >= 3:
        print(f'methods {[m.__name__ for m in relevant]}')
    for method in relevant:
        if verbose >= 3:
            print(f'depth {depth} trying method {method.__name__}: ', end='')
        subgoals = method(state,arg,val)
        # Can't just say "if subgoals:", because that's wrong if subgoals == []
        if subgoals != False and subgoals != None:
            if verbose >= 3:
                print('applicable')
                print(f'depth {depth} subgoals: {subgoals}')
            _record_trace_event(depth, goal1,
                "method_applicable" if isinstance(subgoals, list) else "method_malformed_return",
                subgoals, state=state)
            if verify_goals:
                verification = [('_verify_g', method.__name__, \
                                 state_var_name, arg, val, depth)]
            else:
                verification = []
            todo_list = subgoals + verification + todo_list
            result = seek_plan_recursive(state, todo_list, plan, depth+1)
            if result != False and result != None:
                return result
        else:
            if verbose >= 3:
                print(f'not applicable')
            _record_trace_event(depth, goal1, "method_not_applicable", state=state)
    if verbose >= 3:
        print(f'depth {depth} could not achieve goal {goal1}')
    _record_trace_event(depth, goal1, "goal_exhausted", state=state)
    return False


def _refine_multigoal_and_continue_recursive(state, goal1, todo_list, plan, depth):
    """
    If goal1 is a multigoal, then iterate through the list of multigoal
    methods to find one that's applicable, apply it to get additional
    todo_list items, and call seek_plan recursively on
          [the additional items] + [verify_mg] + todo_list,

    where [verify_mg] verifies whether the method actually achieved goal1.
    If the call to seek_plan_recursive fails, go on to the next method in the list.
    """
    if verbose >= 3:
        print(f'depth {depth} multigoal {goal1}: ', end='')
    relevant = current_domain._multigoal_method_list
    if verbose >= 3:
        print(f'methods {[m.__name__ for m in relevant]}')
    for method in relevant:
        if verbose >= 3:
            print(f'depth {depth} trying method {method.__name__}: ', end='')
        subgoals = method(state,goal1)
        # Can't just say "if subgoals:", because that's wrong if subgoals == []
        if subgoals != False and subgoals != None:
            if verbose >= 3:
                print('applicable')
                print(f'depth {depth} subgoals: {subgoals}')
            _record_trace_event(depth, goal1,
                "method_applicable" if isinstance(subgoals, list) else "method_malformed_return",
                subgoals, state=state)
            if verify_goals:
                verification = [('_verify_mg', method.__name__, goal1, depth)]
            else:
                verification = []
            todo_list = subgoals + verification + todo_list
            result = seek_plan_recursive(state, todo_list, plan, depth+1)
            if result != False and result != None:
                return result
        else:
            if verbose >= 3:
                print(f'not applicable')
            _record_trace_event(depth, goal1, "method_not_applicable", state=state)
    if verbose >= 3:
        print(f'depth {depth} could not achieve multigoal {goal1}')
    _record_trace_event(depth, goal1, "multigoal_exhausted", state=state)
    return False

def seek_plan_recursive(state, todo_list, plan, depth):
    """
    Recursive workhorse for find_plan. Arguments:
     - state is the current state
     - todo_list is the current list of goals, tasks, and actions
     - plan is the current partial plan
     - depth is the recursion depth, for use in debugging
    """
    if verbose >= 2: 
        todo_string = '[' + ', '.join([_item_to_string(x) for x in todo_list]) + ']'
        print(f'depth {depth} todo_list ' + todo_string)
    if todo_list == []:
        if verbose >= 3:
            print(f'depth {depth} no more tasks or goals, return plan')
        return plan
    item1 = todo_list[0]
    ttype = get_type(item1)
    if ttype in {'Multigoal'}:
        return _refine_multigoal_and_continue_recursive(state, item1, todo_list[1:], plan, depth)
    elif ttype in {'list','tuple'}:
        if item1[0] in current_domain._action_dict:
            return _apply_action_and_continue_recursive(state, item1, todo_list[1:], plan, depth)
        elif item1[0] in current_domain._task_method_dict:
            return _refine_task_and_continue_recursive(state, item1, todo_list[1:], plan, depth)
        elif item1[0] in current_domain._unigoal_method_dict:
            return _refine_unigoal_and_continue_recursive(state, item1, todo_list[1:], plan, depth)
    raise Exception(    \
        f"depth {depth}: {item1} isn't an action, task, unigoal, or multigoal\n")
    return False


###############################################################################
# Applying actions, commands, and methods iteratively to seek a plan

def _apply_action_and_continue_iterative(state, task1, todo_list, plan, depth):
    """
    Apply an action in iterative planning mode.
    Returns a tuple (new_state, new_todo_list, new_plan, new_depth) if successful,
    None if the action is not applicable.
    """
    if verbose >= 3:
        _verbose_print_and_log(f'depth {depth} action {task1}: ', 3, "apply_action", end='')

    _log_if_available("debug", "apply_action", "Attempting action",
                     action_name=task1[0], depth=depth, args=task1[1:])

    action = current_domain._action_dict[task1[0]]

    # Create a copy of the state to avoid modifying the original
    state_copy = state.copy()
    # Apply the action to the copied state
    newstate = action(state_copy, *task1[1:])

    if isinstance(newstate, State):
        if (newstate != state): # == and != are overloaded for State; only attributes matter; state name doesn't
            # action changed the state: record it in the plan
            if verbose >= 3:
                print('applied')
                newstate.display()
            _log_if_available("debug", "apply_action", "Action applied successfully",
                             action_name=task1[0], depth=depth)
            _record_trace_event(depth, task1, "applied", state=state)
            return (newstate, todo_list, plan + [task1], depth + 1)
        else:
            # action didn't change the state: don't record it in the plan
            if verbose >= 3:
                print('idempotent')
                newstate.display()
            _record_trace_event(depth, task1, "idempotent", state=state)
            return (newstate, todo_list, plan, depth + 1)

    if verbose >= 3:
        print('not applicable')
    _log_if_available("debug", "apply_action", "Action not applicable",
                     action_name=task1[0], depth=depth)
    _record_trace_event(depth, task1, _action_failure_status(newstate), newstate, state=state)
    return None

def _refine_task_and_continue_iterative(state, task1, todo_list, plan, depth):
    """
    Refine a task using task methods in iterative planning mode.
    Returns a tuple (state, new_todo_list, plan, new_depth) if successful,
    None if no applicable method is found.
    """
    relevant = current_domain._task_method_dict[task1[0]]
    if verbose >= 3:
        _verbose_print_and_log(f'depth {depth} task {task1} methods {[m.__name__ for m in relevant]}', 3, "refine_task")

    _log_if_available("debug", "refine_task", "Attempting task refinement",
                     task_name=task1[0], depth=depth, method_count=len(relevant))

    for method in relevant:
        if verbose >= 3:
            _verbose_print_and_log(f'depth {depth} trying {method.__name__}: ', 3, "refine_task", end='')

        _log_if_available("debug", "refine_task", "Trying method",
                         method_name=method.__name__, task_name=task1[0], depth=depth)

        subtasks = method(state, *task1[1:])
        if subtasks is not False and subtasks is not None:
            if verbose >= 3:
                print('applicable')
                _verbose_print_and_log(f'depth {depth} subtasks: {subtasks}', 3, "refine_task")
            # Record before the len() call below, which raises TypeError on
            # a malformed (non-list) subtasks value -- recording must happen
            # first so the malformed_return event survives that crash.
            _record_trace_event(depth, task1,
                "method_applicable" if isinstance(subtasks, list) else "method_malformed_return",
                subtasks, state=state)
            _log_if_available("debug", "refine_task", "Method applicable",
                             method_name=method.__name__, subtask_count=len(subtasks))
            result = (state, subtasks + todo_list, plan, depth + 1)
            return result  # Return new state to be added to the stack
        else:
            if verbose >= 3:
                print(f'not applicable')
            _log_if_available("debug", "refine_task", "Method not applicable",
                             method_name=method.__name__)
            _record_trace_event(depth, task1, "method_not_applicable", state=state)
    if verbose >= 3:
        _verbose_print_and_log(f'depth {depth} could not accomplish task {task1}', 3, "refine_task")
    _log_if_available("debug", "refine_task", "Task refinement failed",
                     task_name=task1[0], depth=depth)
    _record_trace_event(depth, task1, "task_exhausted", state=state)
    return None

def _refine_unigoal_and_continue_iterative(state, goal1, todo_list, plan, depth):
    """
    Refine a unigoal using unigoal methods in iterative planning mode.
    Returns a tuple (state, new_todo_list, plan, new_depth) if successful,
    None if no applicable method is found.
    """
    if verbose >= 3:
        print(f'depth {depth} goal {goal1}: ', end='')
    (state_var_name, arg, val) = goal1
    if vars(state).get(state_var_name).get(arg) == val:
        if verbose >= 3:
            print(f'already achieved')
        return (state, todo_list, plan, depth + 1)
    relevant = current_domain._unigoal_method_dict[state_var_name]
    if verbose >= 3:
        print(f'methods {[m.__name__ for m in relevant]}')
    for method in relevant:
        if verbose >= 3:
            print(f'depth {depth} trying method {method.__name__}: ', end='')
        subgoals = method(state, arg, val)
        if subgoals is not False and subgoals is not None:
            if verbose >= 3:
                print('applicable')
                print(f'depth {depth} subgoals: {subgoals}')
            _record_trace_event(depth, goal1,
                "method_applicable" if isinstance(subgoals, list) else "method_malformed_return",
                subgoals, state=state)
            if verify_goals:
                verification = [('_verify_g', method.__name__, state_var_name, arg, val, depth)]
            else:
                verification = []
            new_todo_list = subgoals + verification + todo_list
            return (state, new_todo_list, plan, depth + 1)
        else:
            if verbose >= 3:
                print(f'not applicable')
            _record_trace_event(depth, goal1, "method_not_applicable", state=state)
    if verbose >= 3:
        print(f'depth {depth} could not achieve goal {goal1}')
    _record_trace_event(depth, goal1, "goal_exhausted", state=state)
    return None

def _refine_multigoal_and_continue_iterative(state, goal1, todo_list, plan, depth):
    """
    Refine a multigoal using multigoal methods in iterative planning mode.
    Returns a tuple (state, new_todo_list, plan, new_depth) if successful,
    None if no applicable method is found.
    """
    if verbose >= 3:
        print(f'depth {depth} multigoal {goal1}: ', end='')
    relevant = current_domain._multigoal_method_list
    if verbose >= 3:
        print(f'methods {[m.__name__ for m in relevant]}')
    for method in relevant:
        if verbose >= 3:
            print(f'depth {depth} trying method {method.__name__}: ', end='')
        subgoals = method(state, goal1)
        if subgoals is not False and subgoals is not None:
            if verbose >= 3:
                print('applicable')
                print(f'depth {depth} subgoals: {subgoals}')
            _record_trace_event(depth, goal1,
                "method_applicable" if isinstance(subgoals, list) else "method_malformed_return",
                subgoals, state=state)
            if verify_goals:
                verification = [('_verify_mg', method.__name__, goal1, depth)]
            else:
                verification = []
            new_todo_list = subgoals + verification + todo_list
            return (state, new_todo_list, plan, depth + 1)
        else:
            if verbose >= 3:
                print(f'not applicable')
            _record_trace_event(depth, goal1, "method_not_applicable", state=state)
    if verbose >= 3:
        print(f'depth {depth} could not achieve multigoal {goal1}')
    _record_trace_event(depth, goal1, "multigoal_exhausted", state=state)
    return None

################################################################################
# Iterative Backtracking Refinement Helpers

def _refine_task_and_continue_iterative_bt(state, task1, todo_list, plan, depth):
    """
    Refine a task using task methods in iterative backtracking mode.
    Returns a list of continuations (one per applicable method), possibly empty.
    """
    relevant = current_domain._task_method_dict[task1[0]]
    if verbose >= 3:
        _verbose_print_and_log(f'depth {depth} task {task1} methods {[m.__name__ for m in relevant]}', 3, "refine_task_bt")

    _log_if_available("debug", "refine_task_bt", "Attempting task refinement (backtracking)",
                     task_name=task1[0], depth=depth, method_count=len(relevant))

    continuations = []
    for method in relevant:
        if verbose >= 3:
            _verbose_print_and_log(f'depth {depth} trying {method.__name__}: ', 3, "refine_task_bt", end='')

        _log_if_available("debug", "refine_task_bt", "Trying method",
                         method_name=method.__name__, task_name=task1[0], depth=depth)

        subtasks = method(state, *task1[1:])
        if subtasks is not False and subtasks is not None:
            if verbose >= 3:
                print('applicable')
                _verbose_print_and_log(f'depth {depth} subtasks: {subtasks}', 3, "refine_task_bt")
            # Record before the len() call below, which raises TypeError on
            # a malformed (non-list) subtasks value -- recording must happen
            # first so the malformed_return event survives that crash.
            _record_trace_event(depth, task1,
                "method_applicable" if isinstance(subtasks, list) else "method_malformed_return",
                subtasks, state=state)
            _log_if_available("debug", "refine_task_bt", "Method applicable",
                             method_name=method.__name__, subtask_count=len(subtasks))
            continuations.append((state, subtasks + todo_list, plan, depth + 1))
        else:
            if verbose >= 3:
                print(f'not applicable')
            _log_if_available("debug", "refine_task_bt", "Method not applicable",
                             method_name=method.__name__)
            _record_trace_event(depth, task1, "method_not_applicable", state=state)

    if not continuations:
        if verbose >= 3:
            _verbose_print_and_log(f'depth {depth} could not accomplish task {task1}', 3, "refine_task_bt")
        _log_if_available("debug", "refine_task_bt", "Task refinement failed",
                         task_name=task1[0], depth=depth)
        _record_trace_event(depth, task1, "task_exhausted", state=state)
    return continuations


def _refine_unigoal_and_continue_iterative_bt(state, goal1, todo_list, plan, depth):
    """
    Refine a unigoal using unigoal methods in iterative backtracking mode.
    Returns a list of continuations (one per applicable method), possibly empty.
    """
    if verbose >= 3:
        print(f'depth {depth} goal {goal1}: ', end='')
    (state_var_name, arg, val) = goal1
    if vars(state).get(state_var_name).get(arg) == val:
        if verbose >= 3:
            print(f'already achieved')
        return [(state, todo_list, plan, depth + 1)]
    relevant = current_domain._unigoal_method_dict[state_var_name]
    if verbose >= 3:
        print(f'methods {[m.__name__ for m in relevant]}')

    continuations = []
    for method in relevant:
        if verbose >= 3:
            print(f'depth {depth} trying method {method.__name__}: ', end='')
        subgoals = method(state, arg, val)
        if subgoals is not False and subgoals is not None:
            if verbose >= 3:
                print('applicable')
                print(f'depth {depth} subgoals: {subgoals}')
            _record_trace_event(depth, goal1,
                "method_applicable" if isinstance(subgoals, list) else "method_malformed_return",
                subgoals, state=state)
            if verify_goals:
                verification = [('_verify_g', method.__name__, state_var_name, arg, val, depth)]
            else:
                verification = []
            new_todo_list = subgoals + verification + todo_list
            continuations.append((state, new_todo_list, plan, depth + 1))
        else:
            if verbose >= 3:
                print(f'not applicable')
            _record_trace_event(depth, goal1, "method_not_applicable", state=state)

    if not continuations:
        if verbose >= 3:
            print(f'depth {depth} could not achieve goal {goal1}')
        _record_trace_event(depth, goal1, "goal_exhausted", state=state)
    return continuations


def _refine_multigoal_and_continue_iterative_bt(state, goal1, todo_list, plan, depth):
    """
    Refine a multigoal using multigoal methods in iterative backtracking mode.
    Returns a list of continuations (one per applicable method), possibly empty.
    """
    if verbose >= 3:
        print(f'depth {depth} multigoal {goal1}: ', end='')
    relevant = current_domain._multigoal_method_list
    if verbose >= 3:
        print(f'methods {[m.__name__ for m in relevant]}')

    continuations = []
    for method in relevant:
        if verbose >= 3:
            print(f'depth {depth} trying method {method.__name__}: ', end='')
        subgoals = method(state, goal1)
        if subgoals is not False and subgoals is not None:
            if verbose >= 3:
                print('applicable')
                print(f'depth {depth} subgoals: {subgoals}')
            _record_trace_event(depth, goal1,
                "method_applicable" if isinstance(subgoals, list) else "method_malformed_return",
                subgoals, state=state)
            if verify_goals:
                verification = [('_verify_mg', method.__name__, goal1, depth)]
            else:
                verification = []
            new_todo_list = subgoals + verification + todo_list
            continuations.append((state, new_todo_list, plan, depth + 1))
        else:
            if verbose >= 3:
                print(f'not applicable')
            _record_trace_event(depth, goal1, "method_not_applicable", state=state)

    if not continuations:
        if verbose >= 3:
            print(f'depth {depth} could not achieve multigoal {goal1}')
        _record_trace_event(depth, goal1, "multigoal_exhausted", state=state)
    return continuations

################################################################################
# Iterative Planning Implementation

def seek_plan_iterative(initial_state, initial_todo_list, initial_plan, initial_depth):
    """
    Iterative workhorse for find_plan. Arguments:
     - state is the current state
     - todo_list is the current list of goals, tasks, and actions
     - plan is the current partial plan
     - depth is the recursion depth, for use in debugging
    """
    stack = [(initial_state, initial_todo_list, initial_plan, initial_depth)]  # (state, todo_list, plan, depth)
    expansions = 0

    _log_if_available("debug", "seek_plan_iterative", "Starting iterative planning",
                     initial_depth=initial_depth,
                     initial_todo_count=len(initial_todo_list))

    while stack:
        state, todo_list, plan, depth = stack.pop()
        expansions += 1

        # Check for cooperative cancellation periodically (every 100 expansions for performance)
        if expansions % 100 == 0:
            try:
                # Try to get session_id from global logger if available
                if _global_logger and hasattr(_global_logger, 'session_id'):
                    ResourceManager.check_cancellation(_global_logger.session_id)
            except (AttributeError, PlanningTimeoutError):
                # If no session context or cancellation requested, handle appropriately
                pass

        if verbose >= 2:
            todo_string = '[' + ', '.join([_item_to_string(x) for x in todo_list]) + ']'
            _verbose_print_and_log(f'depth {depth} todo_list ' + todo_string, 2, "seek_plan_iterative")

        if not todo_list:
            if verbose >= 3:
                _verbose_print_and_log(f'depth {depth} no more tasks or goals, return plan', 3, "seek_plan_iterative")
            _log_if_available("debug", "seek_plan_iterative", "Planning completed successfully",
                             final_depth=depth, expansions=expansions, plan_length=len(plan))
            return plan

        item1 = todo_list[0]
        ttype = get_type(item1)

        if ttype in {'Multigoal'}:
            result = _refine_multigoal_and_continue_iterative(state, item1, todo_list[1:], plan, depth)
            if result is not None:
                stack.append(result)  # Add new state to the stack
        elif ttype in {'list', 'tuple'}:
            if item1[0] in current_domain._action_dict:
                result = _apply_action_and_continue_iterative(state, item1, todo_list[1:], plan, depth)
                if result is not None:
                    stack.append(result)  # Add new state to the stack
            elif item1[0] in current_domain._task_method_dict:
                result = _refine_task_and_continue_iterative(state, item1, todo_list[1:], plan, depth)
                if result is not None:
                    stack.append(result)  # Add new state to the stack
            elif item1[0] in current_domain._unigoal_method_dict:
                result = _refine_unigoal_and_continue_iterative(state, item1, todo_list[1:], plan, depth)
                if result is not None:
                    stack.append(result)  # Add new state to the stack

    return False

################################################################################
# Iterative Backtracking Planning Implementation

def seek_plan_iterative_backtracking(initial_state, initial_todo_list, initial_plan, initial_depth):
    """
    Iterative DFS workhorse for find_plan with full backtracking.
    When a task has multiple applicable methods, all continuations are pushed
    onto the stack (in reverse order for LIFO correctness). If one path fails,
    the stack falls through to the next alternative.

    Arguments:
     - initial_state is the current state
     - initial_todo_list is the current list of goals, tasks, and actions
     - initial_plan is the current partial plan
     - initial_depth is the recursion depth, for use in debugging
    """
    stack = [(initial_state, initial_todo_list, initial_plan, initial_depth)]
    expansions = 0

    _log_if_available("debug", "seek_plan_iterative_bt", "Starting iterative backtracking planning",
                     initial_depth=initial_depth,
                     initial_todo_count=len(initial_todo_list))

    while stack:
        state, todo_list, plan, depth = stack.pop()
        expansions += 1

        # Check for cooperative cancellation periodically (every 100 expansions for performance)
        if expansions % 100 == 0:
            try:
                if _global_logger and hasattr(_global_logger, 'session_id'):
                    ResourceManager.check_cancellation(_global_logger.session_id)
            except (AttributeError, PlanningTimeoutError):
                pass

        if verbose >= 2:
            todo_string = '[' + ', '.join([_item_to_string(x) for x in todo_list]) + ']'
            _verbose_print_and_log(f'depth {depth} todo_list ' + todo_string, 2, "seek_plan_iterative_bt")

        if not todo_list:
            if verbose >= 3:
                _verbose_print_and_log(f'depth {depth} no more tasks or goals, return plan', 3, "seek_plan_iterative_bt")
            _log_if_available("debug", "seek_plan_iterative_bt", "Planning completed successfully",
                             final_depth=depth, expansions=expansions, plan_length=len(plan))
            return plan

        item1 = todo_list[0]
        ttype = get_type(item1)

        if ttype in {'Multigoal'}:
            continuations = _refine_multigoal_and_continue_iterative_bt(state, item1, todo_list[1:], plan, depth)
            # Push in reverse so first method is tried first (LIFO)
            for c in reversed(continuations):
                stack.append(c)
        elif ttype in {'list', 'tuple'}:
            if item1[0] in current_domain._action_dict:
                # Actions have no alternatives -- reuse the standard iterative handler
                result = _apply_action_and_continue_iterative(state, item1, todo_list[1:], plan, depth)
                if result is not None:
                    stack.append(result)
                # If None: action failed, stack falls through to next alternative
            elif item1[0] in current_domain._task_method_dict:
                continuations = _refine_task_and_continue_iterative_bt(state, item1, todo_list[1:], plan, depth)
                for c in reversed(continuations):
                    stack.append(c)
            elif item1[0] in current_domain._unigoal_method_dict:
                continuations = _refine_unigoal_and_continue_iterative_bt(state, item1, todo_list[1:], plan, depth)
                for c in reversed(continuations):
                    stack.append(c)

    return False

############################################################
# The planning system

_current_seek_plan = None


def set_recursive_planning(strategy, verbose_output=False):
    """
    Set the planning strategy.

    Args:
        strategy: Planning strategy to use. Accepts:
            - True: recursive DFS (depth-first search with backtracking
              via Python call stack)
            - False: iterative greedy (irrevocable commitment to first
              applicable method; no backtracking)
            - "recursive_dfs": same as True
            - "iterative_greedy": same as False
            - "iterative_irrevocable_commitment": same as False
            - "iterative_dfs_backtracking": iterative depth-first search
              with full backtracking via explicit stack
        verbose_output: If True, print strategy change messages
    """
    global _current_seek_plan
    if isinstance(strategy, bool):
        if strategy:
            _current_seek_plan = seek_plan_recursive
            if verbose_output:
                print("Using recursive seek_plan.")
        else:
            _current_seek_plan = seek_plan_iterative
            if verbose_output:
                print("Using iterative seek_plan.")
    elif isinstance(strategy, str):
        if strategy == "recursive_dfs":
            _current_seek_plan = seek_plan_recursive
            if verbose_output:
                print("Using recursive DFS seek_plan.")
        elif strategy in ("iterative_greedy", "iterative_irrevocable_commitment"):
            _current_seek_plan = seek_plan_iterative
            if verbose_output:
                print("Using iterative greedy seek_plan.")
        elif strategy == "iterative_dfs_backtracking":
            _current_seek_plan = seek_plan_iterative_backtracking
            if verbose_output:
                print("Using iterative DFS seek_plan with backtracking.")
        else:
            raise ValueError(
                f"Unknown strategy '{strategy}'. Valid strategies: "
                f"'recursive_dfs', 'iterative_greedy', "
                f"'iterative_irrevocable_commitment', "
                f"'iterative_dfs_backtracking'")
    else:
        raise TypeError(
            f"strategy must be bool or str, got {type(strategy).__name__}")


def get_recursive_planning():
    """
    Returns True if the current strategy is recursive DFS, False otherwise.
    Note: returns False for both iterative greedy and iterative DFS backtracking.
    """
    if None == _current_seek_plan:
        raise Exception("No planning strategy has been set. Use set_recursive_planning(True|False|<strategy_name>) to set it.")
    return _current_seek_plan == seek_plan_recursive


def reset_planning_strategy():
    """
    Resets the planning strategy to None, so that the user must set it again
    using set_recursive_planning(True|False|<strategy_name>).
    """
    global _current_seek_plan
    _current_seek_plan = None


def seek_plan(state, todolist, plan, depth):
    return _current_seek_plan(state, todolist, plan, depth)

################################################################################
# Main Planning Entry Points

def find_plan(state, todo_list):
    """
    find_plan tries to find a plan that accomplishes the items in todo_list,
    starting from the given state, using whatever methods and actions you
    declared previously. If successful, it returns the plan. Otherwise it
    returns False. Arguments:
     - 'state' is a state;
     - 'todo_list' is a list of goals, tasks, and actions.
    """
    if None == _current_seek_plan:
        raise Exception("No planning strategy has been set. Use set_recursive_planning(True|False|<strategy_name>) to set it.")

    # Start timing for performance logging
    start_time = time.time()

    # Log planning start
    if _current_seek_plan == seek_plan_recursive:
        strategy = "recursive_dfs"
    elif _current_seek_plan == seek_plan_iterative_backtracking:
        strategy = "iterative_dfs_backtracking"
    else:
        strategy = "iterative_greedy"
    _log_if_available("info", "find_plan", "Planning started",
                     state_name=state.__name__,
                     todo_count=len(todo_list),
                     strategy=strategy)

    if verbose >= 1:
        todo_string = '[' + ', '.join([_item_to_string(x) for x in todo_list]) + ']'
        _verbose_print_and_log(f'FP> find_plan, verbose={verbose}:', 1, "find_plan")
        _verbose_print_and_log(f'    state = {state.__name__}\n    todo_list = {todo_string}', 1, "find_plan")

    result = _current_seek_plan(state, todo_list, [], 0)

    # Log planning completion
    duration_ms = int((time.time() - start_time) * 1000)
    success = result is not False and result is not None
    _log_if_available("info", "find_plan", "Planning completed",
                     success=success,
                     duration_ms=duration_ms,
                     plan_length=len(result) if success else 0)

    if verbose >= 1:
        _verbose_print_and_log(f'FP> result = {result}\n', 1, "find_plan")

    return result


def pyhop(state, todo_list):
    if verbose > 0:
        print("""
        >> The function 'pyhop' exists to provide backward compatibility
        >> with Pyhop. In the future, please use find_plan instead.""")
    return find_plan(state, todo_list)


def _item_to_string(item):
    """Return a string representation of a task or goal."""
    ttype = get_type(item)
    if ttype == 'list':
        return str([str(x) for x in item])
    elif ttype == 'tuple':
        return str(tuple([str(x) for x in item]))
    else:       # a multigoal
        return str(item)

################################################################################
# An actor


def run_lazy_lookahead(state, todo_list, max_tries=10):
    """
    An adaptation of the run_lazy_lookahead algorithm from Ghallab et al.
    (2016), Automated Planning and Acting. It works roughly like this:
        loop:
            plan = find_plan(state, todo_list)
            if plan = [] then return state    // the new current state
            for each action in plan:
                try to execute the corresponding command
                if the command fails, continue the outer loop
    Arguments:
      - 'state' is a state;
      - 'todo_list' is a list of tasks, goals, and multigoals;
      - max_tries is a bound on how many times to execute the outer loop.

    Note: whenever run_lazy_lookahead encounters an action for which there is
    no corresponding command definition, it uses the action definition instead.
    """
    start_time = time.time()

    _log_if_available("info", "run_lazy_lookahead", "Starting plan-and-act execution",
                     state_name=state.__name__,
                     todo_count=len(todo_list),
                     max_tries=max_tries)

    if verbose >= 1:
        _verbose_print_and_log(f"RLL> run_lazy_lookahead, verbose = {verbose}, max_tries = {max_tries}", 1, "run_lazy_lookahead")
        _verbose_print_and_log(f"RLL> initial state: {state.__name__}", 1, "run_lazy_lookahead")
        print('RLL> To do:', todo_list)

    for tries in range(1,max_tries+1):
        if verbose >= 1: 
            ordinals = {1:'st',2:'nd',3:'rd'}
            if ordinals.get(tries):
                print(f"RLL> {tries}{ordinals.get(tries)} call to find_plan:\n")
            else:
                print(f"RLL> {tries}th call to find_plan:\n")
        plan = find_plan(state, todo_list)
        if plan is False or plan is None:
            if verbose >= 1:
                print("RLL> find_plan has failed")
            raise Exception(
                    f"run_lazy_lookahead: find_plan has failed")
        if plan == []:
            if verbose >= 1: 
                print(f'RLL> Empty plan => success',
                      f'after {tries} calls to find_plan.')
            if verbose >= 2: state.display(heading='> final state')
            return state
        for action in plan:
            command_name = 'c_' + action[0]
            command_func = current_domain._command_dict.get(command_name)
            if command_func is None:
                if verbose >= 1: 
                    print(f'RLL> {command_name} not defined, using {action[0]} instead\n')
                command_func = current_domain._action_dict.get(action[0])
                
            if verbose >= 1:
                print('RLL> Command:', [command_name] + list(action[1:]))
            new_state = _apply_command_and_continue_rll(state, command_func, action[1:])
            if new_state is False:
                if verbose >= 1:
                    print(f'RLL> WARNING: command {command_name} failed; will call find_plan.')
                break
            else:
                if verbose >= 2: 
                    new_state.display()
                state = new_state
        # if state != False then we're here because the plan ended
        if verbose >= 1 and state:
            print(f'RLL> Plan ended; will call find_plan again.')
        
    if verbose >= 1: print('RLL> Too many tries, giving up.')
    if verbose >= 2: state.display(heading='RLL> final state')
    return state


def _apply_command_and_continue_rll(state, command, args):
    """
    _apply_command_and_continue applies 'command' by retrieving its
    function definition and calling it on the arguments.
    """
    if verbose >= 3:
        print(f"_apply_command_and_continue {command.__name__}, args = {args}")
    # Create a copy of the state to avoid modifying the original
    newstate = state.copy()
    # Apply the command to the copied state
    next_state = command(newstate,*args)
    if isinstance(next_state, State):
        # we ignore idempotent commands here
        if verbose >= 3:
            print('applied')
            next_state.display()
        return next_state
    else:
        if verbose >= 3:
            print('not applicable')
        return False


################################################################################
#                                                                              #
#                        SESSION-BASED ARCHITECTURE                           #
#                                                                              #
################################################################################

"""
This section implements GTPyhop's session-based architecture, providing
isolated planning contexts with comprehensive resource management and
structured result handling.

Key Components:
- Result Classes: PlanResult and ExecutionResult for structured operation results
- PlannerSession: Main session class providing isolated planning contexts
- Session Management: Functions to create, retrieve, and destroy sessions
- Isolated Execution: Context managers for thread-safe state isolation
- Session Planning: Session-specific planning methods with timeout support
- Session Execution: Plan-and-act execution with monitoring and control

Cross-references:
- Uses Core Planning Algorithms for actual planning operations
- Uses Domain and State Management for domain-specific sessions
- Integrates with Resource Management for timeout and monitoring
- Uses Logging and Utilities for structured logging and debugging

Design Notes:
- Sessions provide complete isolation from global GTPyhop state
- Thread-safe design supports concurrent session usage
- Structured results provide rich information for debugging and monitoring
- Backward compatibility maintained through global function preservation
"""

#: Terminal statuses: recorded once, when a search path has definitively
#: failed at that point. Candidates for PlanTrace.dead_end.
_TERMINAL_STATUSES = frozenset({
    "not_applicable", "malformed_return",
    "task_exhausted", "goal_exhausted", "multigoal_exhausted",
    # A malformed method return is structurally positioned like
    # "method_applicable" (the code proceeds to use it), but in practice
    # it is terminal: `subtasks + todo_list` on a non-list value raises
    # TypeError immediately, ending the search via exception rather than
    # ever reaching the "*_exhausted" line. Recording it as terminal means
    # dead_end reports the true proximate cause instead of missing it.
    "method_malformed_return",
})


@dataclass
class TraceEvent:
    """
    One attempt recorded during find_plan's search, in depth-first
    visitation order: applying an action, or trying a method to refine a
    task/unigoal/multigoal.

    status is one of:
      - "applied":          the action returned a State different from the
                             input state; recorded in the plan.
      - "idempotent":       the action returned a State equal to the input
                             state; not recorded in the plan, but the search
                             continued from it.
      - "not_applicable":   the action returned False or None -- a legitimate
                             precondition failure. False is what this
                             project's style guide teaches; None is what
                             GTPyhop's original examples have always done,
                             falling off the end of
                             `if <preconditions>: <effects>; return s` when
                             the guard is false. Both are ordinary failures,
                             matching the method-refinement paths, which have
                             likewise always accepted None. See
                             _action_failure_status. Terminal for this item.
      - "malformed_return": the action returned something that is neither a
                             State, False, nor None (e.g. True, a string, an
                             int). Before this status existed, GTPyhop treated
                             this identically to "not_applicable", making a
                             broken action indistinguishable from a legitimate
                             precondition failure -- the case that matters
                             being an action that returns True rather than the
                             state, silently discarding its own effects while
                             appearing to succeed. detail describes what was
                             actually returned. Terminal for this item.
      - "method_applicable":       a candidate method for this task/unigoal/
                                    multigoal returned a subtask/subgoal list.
                                    Not terminal -- for recursive search, a
                                    locally-applicable method can still lead
                                    to eventual failure deeper in the tree.
      - "method_not_applicable":   a candidate method returned False/None.
                                    Not terminal -- the loop moves on to the
                                    next candidate method, if any remain.
      - "method_malformed_return": a candidate method returned something
                                    that is neither a list, False, nor None
                                    (e.g. True) -- the method-level analogue
                                    of an action's malformed_return. Terminal:
                                    although structurally positioned like
                                    "method_applicable" in the code, the
                                    malformed value is used immediately
                                    afterward (subtasks + todo_list), which
                                    raises TypeError before the enclosing
                                    task/unigoal/multigoal's *_exhausted event
                                    would ever be reached. detail describes
                                    what was actually returned.
      - "task_exhausted":       every candidate method for this task was
                                 tried (recorded as method_applicable or
                                 method_not_applicable/malformed_return
                                 above) and none led to a successful plan.
                                 Terminal.
      - "goal_exhausted":       same, for a unigoal. Terminal.
      - "multigoal_exhausted":  same, for a multigoal. Terminal.

    item holds whatever todo_list entry this event concerns: an action tuple
    for "applied"/"idempotent"/"not_applicable"/"malformed_return"; a task,
    unigoal, or Multigoal for the method_*/*_exhausted statuses. This mirrors
    GTPyhop's own internal naming (`item1 = todo_list[0]`) for exactly this
    "todo-list entry of unknown-until-dispatched type" concept.

    state holds a deep copy of the state this item was attempted against --
    for an action, the state its preconditions were evaluated on (not the
    state the action returned); for a method_*/*_exhausted event, the state
    the method(s) were called on. It is None unless the search was run with
    find_plan(..., trace_state=True), and also None if the state could not
    be deep-copied (a domain may put an uncopyable object into a state
    variable; a diagnostic facility must not crash the planner it is
    diagnosing). Snapshots are what let a consumer move from "action a_foo
    was not applicable" to "action a_foo was not applicable *because*
    state.door_open was False": the static analysis gives the candidate
    preconditions, the snapshot says which of them actually did not hold.
    """
    depth: int
    item: Any
    status: str
    detail: Optional[str] = None
    state: Optional['State'] = None


class PlanTrace:
    """
    Structured, depth-first record of every action-application and
    method-refinement attempt made during one find_plan call. Opt-in via
    find_plan(..., trace=True); costs nothing when not requested (no events
    are recorded).

    This replaces two fragile patterns for consumers that need to know *why*
    a scenario failed to plan: parsing verbose=3 debug print output, and
    reaching into Domain's private _action_dict / _task_method_dict /
    _unigoal_method_dict / _multigoal_method_list. This class provides only
    mechanical facts (which action or method, at what depth, with what
    status, and -- with trace_state=True -- the state it was attempted
    against) -- it does not itself attribute failure to a specific
    precondition or state variable; that remains a source-level analysis for
    the caller, for which TraceEvent.state supplies the missing half of the
    evidence (see TraceEvent).
    """

    def __init__(self):
        self.events: List[TraceEvent] = []

    def record(self, depth: int, item: Any, status: str, detail: Optional[str] = None,
               state: Optional['State'] = None):
        self.events.append(TraceEvent(depth=depth, item=item, status=status, detail=detail,
                                      state=state))

    @property
    def dead_end(self) -> Optional[TraceEvent]:
        """
        The first terminal event (see _TERMINAL_STATUSES), in depth-first
        order -- the action or the exhausted task/unigoal/multigoal
        refinement that GTPyhop's search abandoned first on the path it
        actually explored. "method_applicable" and "method_not_applicable"
        are never terminal by themselves -- for a task/unigoal/multigoal to
        count as a dead end, either every candidate method must be
        exhausted ("*_exhausted"), or one of them must have returned a
        malformed value ("method_malformed_return", terminal because it
        crashes the search on use rather than yielding control back to the
        loop). For a
        non-backtracking strategy (iterative greedy) this is unambiguously
        the reason the search failed. For a backtracking strategy (recursive
        DFS, iterative DFS with backtracking), this is a heuristic, not a
        guarantee: later events may belong to alternative branches explored
        after this one was abandoned. Returns None if the search never hit a
        terminal event (i.e. it found a plan without ever exhausting an
        item's alternatives).
        """
        for event in self.events:
            if event.status in _TERMINAL_STATUSES:
                return event
        return None

    @property
    def applied_before_dead_end(self) -> int:
        """
        Count of "applied"/"idempotent" action events recorded strictly
        before dead_end (0 if there is no dead_end). Method-refinement
        events are not counted here -- this mirrors check_solvability.py's
        existing "expansion count" convention, which counts applied
        *actions*, not methods tried.
        """
        count = 0
        for event in self.events:
            if event.status in _TERMINAL_STATUSES:
                break
            if event.status in ("applied", "idempotent"):
                count += 1
        return count

    @property
    def malformed_returns(self) -> List[TraceEvent]:
        """All events where an action or method returned a value that
        violates its return contract (neither State/False for an action,
        nor list/False/None for a method)."""
        return [event for event in self.events
                if event.status in ("malformed_return", "method_malformed_return")]

    def __len__(self):
        return len(self.events)

    def __bool__(self):
        # A PlanTrace with zero events is still a meaningful, valid result
        # (e.g. an empty todo_list) -- never treat it as falsy.
        return True

    def __repr__(self):
        return f"PlanTrace({len(self.events)} events, dead_end={self.dead_end!r})"


@dataclass
class PlanResult:
    """Structured result from planning operations."""
    success: bool
    plan: Optional[List[Tuple]] = None
    error: Optional[str] = None
    logs: List[Dict[str, Any]] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)
    session_id: Optional[str] = None
    trace: Optional['PlanTrace'] = None

    def __post_init__(self):
        if self.plan is None:
            self.plan = []
        if not self.stats:
            self.stats = {"duration_ms": 0, "expansions": 0}

    def __bool__(self):
        # Dataclasses are truthy by default regardless of contents; without
        # this override, `if result:` is always True even when
        # result.success is False. Always check `.success`, not `bool(result)`.
        return self.success

@dataclass
class ExecutionResult:
    """Structured result from execution operations."""
    success: bool
    final_state: Optional['State'] = None
    executed_actions: List[Tuple] = field(default_factory=list)
    error: Optional[str] = None
    logs: List[Dict[str, Any]] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)
    session_id: Optional[str] = None
    tries_used: int = 0

    def __bool__(self):
        # Same rationale as PlanResult.__bool__ above.
        return self.success

class PlanningTimeoutError(Exception):
    """Raised when planning operations exceed time limits."""
    pass

class SessionPersistenceError(Exception):
    """Raised when session persistence operations fail."""
    pass

class SessionSerializer:
    """Handles session state serialization and deserialization."""

    @staticmethod
    def serialize_session(session: 'PlannerSession', format: str = 'json') -> bytes:
        """
        Serialize a session to bytes.

        Args:
            session: PlannerSession to serialize
            format: Serialization format ('json' or 'pickle')

        Returns:
            Serialized session data as bytes

        Raises:
            SessionPersistenceError: If serialization fails
        """
        try:
            with session._lock:
                # Create serializable session data
                session_data = {
                    'session_id': session.session_id,
                    'verbose': session.verbose,
                    'recursive': session.recursive,
                    'strategy': session._strategy,
                    'structured_logging': session.structured_logging,
                    'auto_cleanup': session.auto_cleanup,
                    'created_at': session._created_at,
                    'last_used': session._last_used,
                    'stats': session._stats.copy(),
                    'domain_name': session.domain.__name__ if session.domain else None,
                    'version': '2.0.0',
                    'timestamp': time.time()
                }

                if format == 'json':
                    return json.dumps(session_data, indent=2).encode('utf-8')
                elif format == 'pickle':
                    return pickle.dumps(session_data)
                else:
                    raise ValueError(f"Unsupported format: {format}")

        except Exception as e:
            raise SessionPersistenceError(f"Failed to serialize session {session.session_id}: {e}")

    @staticmethod
    def deserialize_session(data: bytes, format: str = 'json') -> Dict[str, Any]:
        """
        Deserialize session data from bytes.

        Args:
            data: Serialized session data
            format: Serialization format ('json' or 'pickle')

        Returns:
            Dictionary containing session data

        Raises:
            SessionPersistenceError: If deserialization fails
        """
        try:
            if format == 'json':
                session_data = json.loads(data.decode('utf-8'))
            elif format == 'pickle':
                session_data = pickle.loads(data)
            else:
                raise ValueError(f"Unsupported format: {format}")

            # Validate required fields
            required_fields = ['session_id', 'verbose', 'recursive', 'created_at', 'stats']
            for field in required_fields:
                if field not in session_data:
                    raise ValueError(f"Missing required field: {field}")

            return session_data

        except Exception as e:
            raise SessionPersistenceError(f"Failed to deserialize session data: {e}")

    @staticmethod
    def validate_session_data(session_data: Dict[str, Any]) -> bool:
        """
        Validate deserialized session data for completeness and consistency.

        Args:
            session_data: Deserialized session data

        Returns:
            True if data is valid, False otherwise
        """
        try:
            # Check version compatibility
            version = session_data.get('version', '1.0.0')
            if not version.startswith('1.'):
                return False

            # Check required fields and types
            checks = [
                ('session_id', str),
                ('verbose', int),
                ('recursive', bool),
                ('created_at', (int, float)),
                ('stats', dict)
            ]

            for field, expected_type in checks:
                if field not in session_data:
                    return False
                if not isinstance(session_data[field], expected_type):
                    return False

            # Validate stats structure
            stats = session_data['stats']
            required_stats = ['plans_generated', 'total_planning_time_ms', 'errors']
            for stat in required_stats:
                if stat not in stats or not isinstance(stats[stat], (int, float)):
                    return False

            return True

        except Exception:
            return False

################################################################################
#                                                                              #
#                      RESOURCE MANAGEMENT AND PERSISTENCE                    #
#                                                                              #
################################################################################

"""
This section implements resource management, timeout enforcement, and session
persistence capabilities for robust, production-ready planning operations.

Key Components:
- ResourceManager: Cross-platform timeout enforcement and memory monitoring
- ProcessCleanupManager: Graceful shutdown and resource cleanup
- Session Persistence: Save and restore session state to/from files
- Memory Tracking: Lightweight memory usage monitoring and reporting
- Timeout Handling: Cooperative cancellation and timeout enforcement
- Error Recovery: Robust error handling and graceful degradation

Cross-references:
- Used by Session-Based Architecture for session resource management
- Integrates with Core Planning Algorithms for timeout enforcement
- Uses Logging and Utilities for error reporting and debugging

Design Notes:
- Cross-platform timeout support (Windows threading, Unix signals)
- Cooperative cancellation prevents abrupt termination
- Lightweight memory tracking minimizes performance impact
- Persistence uses atomic file operations for reliability
- Graceful degradation ensures system continues operation on failures
"""

################################################################################
# Resource Management and Timeout Enforcement

class ResourceManager:
    """Cross-platform resource management for planning operations."""

    _cancellation_flags = {}  # session_id -> threading.Event
    _memory_tracker = None    # Lazy-initialized MemoryTracker instance
    _memory_monitor = None    # Lazy-initialized MemoryMonitor instance

    @staticmethod
    def _get_tracker():
        """Get or create memory tracker instance (lazy initialization)."""
        if ResourceManager._memory_tracker is None:
            try:
                from .memory_tracking import MemoryTracker, MEMORY_TRACKING_AVAILABLE
                if MEMORY_TRACKING_AVAILABLE:
                    ResourceManager._memory_tracker = MemoryTracker()
                else:
                    ResourceManager._memory_tracker = None
            except ImportError:
                ResourceManager._memory_tracker = None
        return ResourceManager._memory_tracker

    # Default sampling interval for memory monitoring
    _sampling_interval: float = 0.1

    @staticmethod
    def _get_monitor(sampling_interval: Optional[float] = None):
        """Get or create memory monitor instance (lazy initialization).

        Args:
            sampling_interval: Seconds between memory samples. If provided and different
                from current monitor's interval, recreates the monitor.
        """
        interval = sampling_interval if sampling_interval is not None else ResourceManager._sampling_interval

        # Check if we need to recreate with a different interval
        if ResourceManager._memory_monitor is not None:
            if hasattr(ResourceManager._memory_monitor, 'sampling_interval'):
                if ResourceManager._memory_monitor.sampling_interval != interval:
                    # Stop existing monitor and recreate with new interval
                    ResourceManager._memory_monitor = None

        if ResourceManager._memory_monitor is None:
            try:
                from .memory_tracking import MemoryMonitor, MEMORY_TRACKING_AVAILABLE
                if MEMORY_TRACKING_AVAILABLE and MemoryMonitor is not None:
                    ResourceManager._memory_monitor = MemoryMonitor(sampling_interval=interval)
                    ResourceManager._sampling_interval = interval
                else:
                    ResourceManager._memory_monitor = None
            except ImportError:
                ResourceManager._memory_monitor = None
        return ResourceManager._memory_monitor

    @staticmethod
    def reset():
        """Reset all cached state for fresh benchmarking.

        This method clears the singleton instances (_memory_monitor, _memory_tracker)
        and cancellation flags. Call this before each benchmark run to ensure
        measurements are not affected by previous runs.

        Also triggers garbage collection to release any accumulated memory.
        """
        import gc

        # Stop and clear memory monitor
        if ResourceManager._memory_monitor is not None:
            try:
                ResourceManager._memory_monitor.stop()
            except Exception:
                pass
            ResourceManager._memory_monitor = None

        # Clear memory tracker
        ResourceManager._memory_tracker = None

        # Clear cancellation flags
        ResourceManager._cancellation_flags.clear()

        # Reset sampling interval to default
        ResourceManager._sampling_interval = 0.1

        # Force garbage collection
        gc.collect()

    @staticmethod
    def with_timeout(timeout_ms: Optional[int] = None, session_id: Optional[str] = None):
        """Decorator to add timeout to planning operations."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                if timeout_ms is None or timeout_ms <= 0:
                    return func(*args, **kwargs)

                # Cross-platform timeout implementation
                if sys.platform == "win32" or not hasattr(signal, 'SIGALRM'):
                    # Use threading.Timer for Windows and systems without SIGALRM
                    return ResourceManager._timeout_with_thread(func, timeout_ms, session_id, *args, **kwargs)
                else:
                    # Use signal.SIGALRM for Unix-like systems
                    return ResourceManager._timeout_with_signal(func, timeout_ms, *args, **kwargs)
            return wrapper
        return decorator

    @staticmethod
    def _timeout_with_thread(func, timeout_ms, session_id, *args, **kwargs):
        """Thread-based timeout implementation for cross-platform support."""
        result = [None]
        exception = [None]

        def target():
            try:
                result[0] = func(*args, **kwargs)
            except Exception as e:
                exception[0] = e

        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout_ms / 1000.0)

        if thread.is_alive():
            # Set cancellation flag if session_id provided
            if session_id:
                ResourceManager.set_cancellation_flag(session_id)
            raise PlanningTimeoutError(f"Planning timed out after {timeout_ms}ms")

        if exception[0]:
            raise exception[0]

        return result[0]

    @staticmethod
    def _timeout_with_signal(func, timeout_ms, *args, **kwargs):
        """Signal-based timeout implementation for Unix-like systems."""
        def timeout_handler(signum, frame):
            raise PlanningTimeoutError(f"Planning timed out after {timeout_ms}ms")

        # Set up timeout
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(max(1, timeout_ms // 1000))  # Convert to seconds, minimum 1

        try:
            return func(*args, **kwargs)
        finally:
            signal.alarm(0)  # Cancel alarm
            signal.signal(signal.SIGALRM, old_handler)

    @staticmethod
    def set_cancellation_flag(session_id: str):
        """Set cancellation flag for cooperative cancellation."""
        if session_id not in ResourceManager._cancellation_flags:
            ResourceManager._cancellation_flags[session_id] = threading.Event()
        ResourceManager._cancellation_flags[session_id].set()

    @staticmethod
    def clear_cancellation_flag(session_id: str):
        """Clear cancellation flag."""
        if session_id in ResourceManager._cancellation_flags:
            ResourceManager._cancellation_flags[session_id].clear()

    @staticmethod
    def check_cancellation(session_id: str):
        """Check if operation should be cancelled."""
        if session_id in ResourceManager._cancellation_flags:
            if ResourceManager._cancellation_flags[session_id].is_set():
                raise PlanningTimeoutError("Planning cancelled due to timeout")

    @staticmethod
    def start_memory_tracking(session_id: str, sampling_interval: Optional[float] = None):
        """Start memory tracking for a session using psutil with background monitoring.

        Args:
            session_id: Unique session identifier
            sampling_interval: Seconds between memory samples (default: 0.1s).
                Lower values capture faster peaks but add overhead.
        """
        tracker = ResourceManager._get_tracker()
        monitor = ResourceManager._get_monitor(sampling_interval)

        if tracker is not None:
            tracker.start_session_tracking(session_id)

            # Also start background monitoring for accurate peak detection
            if monitor is not None:
                try:
                    import psutil
                    baseline = psutil.Process().memory_info().rss / 1024 / 1024
                    monitor.start_monitoring(session_id, baseline)
                except Exception:
                    pass  # Continue without monitoring if it fails
            return True
        return False

    @staticmethod
    def get_memory_usage(session_id: str) -> Dict[str, Any]:
        """Get actual memory usage for a session with accurate peak from background monitoring."""
        tracker = ResourceManager._get_tracker()
        monitor = ResourceManager._get_monitor()

        # Get current memory from tracker
        if tracker is not None:
            tracker_stats = tracker.get_session_memory(session_id)
        else:
            tracker_stats = {'memory_mb': 0.0, 'peak_memory_mb': 0.0}

        # Take an immediate sample to capture current memory state
        # This is critical for fast operations that complete before background sampling
        if monitor is not None:
            monitor.sample_now(session_id)

        # Get peak from monitor (more accurate due to background sampling)
        if monitor is not None and session_id in monitor.monitoring_sessions:
            with monitor._lock:
                session_data = monitor.monitoring_sessions.get(session_id)
                if session_data and session_data['samples']:
                    peak_from_monitor = max(session_data['samples']) - session_data['baseline_memory']
                    # Use the higher peak value (monitor is more accurate)
                    tracker_stats['peak_memory_mb'] = max(tracker_stats['peak_memory_mb'], peak_from_monitor)

        return tracker_stats

    @staticmethod
    def stop_memory_tracking(session_id: str) -> Dict[str, float]:
        """Stop memory tracking for a session and return final stats including accurate peak."""
        tracker = ResourceManager._get_tracker()
        monitor = ResourceManager._get_monitor()

        # Get final stats from monitor first (before stopping)
        monitor_stats = {'peak_memory_mb': 0.0, 'avg_memory_mb': 0.0}
        if monitor is not None:
            monitor_stats = monitor.stop_monitoring(session_id)

        # Stop tracker
        if tracker is not None:
            tracker.stop_session_tracking(session_id)

        # Clean up cancellation flags
        if session_id in ResourceManager._cancellation_flags:
            del ResourceManager._cancellation_flags[session_id]

        return monitor_stats

    @staticmethod
    def sample_memory(session_id: Optional[str] = None):
        """
        Take an immediate memory sample for one or all active sessions.

        This is useful for capturing memory at specific points during execution,
        particularly for fast operations that complete before the background
        monitoring thread can sample.

        Args:
            session_id: If provided, sample only this session.
                       If None, sample all active sessions.

        Note:
            This is a no-op if no monitor exists (i.e., no sessions have
            memory tracking enabled). It will NOT create a monitor, ensuring
            zero overhead when memory tracking is disabled.

        Example:
            >>> ResourceManager.sample_memory("my_session")  # Force a sample
            >>> # Or call from within domain actions for fine-grained tracking
        """
        # Only sample if a monitor already exists - don't create one
        # This ensures zero overhead when memory tracking is disabled
        if ResourceManager._memory_monitor is not None:
            ResourceManager._memory_monitor.sample_now(session_id)

################################################################################
# Session Management Classes

class PlannerSession:
    """Thread-safe, isolated planning session."""

    def __init__(self, session_id: Optional[str] = None, *,
                 domain: Optional['Domain'] = None,
                 verbose: int = 0,
                 recursive: bool = False,
                 strategy: Optional[str] = None,
                 structured_logging: bool = True,
                 auto_cleanup: bool = True,
                 memory_tracking: bool = False,
                 memory_sampling_interval: Optional[float] = None):
        """
        Initialize a new planning session.

        Args:
            session_id: Unique identifier for this session
            domain: Planning domain to use
            verbose: Verbosity level (0-3)
            recursive: Use recursive planning strategy (legacy; use strategy instead)
            strategy: Planning strategy name. When provided, takes precedence over
                recursive. Valid values: "recursive_dfs", "iterative_greedy",
                "iterative_irrevocable_commitment", "iterative_dfs_backtracking".
                Default None (falls back to recursive parameter).
            structured_logging: Enable structured logging
            auto_cleanup: Automatically clean up resources
            memory_tracking: Enable psutil-based memory tracking with background
                monitoring for accurate peak detection (default: False)
            memory_sampling_interval: Seconds between memory samples when tracking
                is enabled (default: 0.1s). Lower values capture faster peaks.
        """
        self.session_id = session_id or f"session_{uuid.uuid4().hex[:8]}"
        self.domain = domain
        self.verbose = verbose
        self.structured_logging = structured_logging
        self.auto_cleanup = auto_cleanup
        self.memory_tracking = memory_tracking
        self.memory_sampling_interval = memory_sampling_interval

        # Resolve effective strategy
        if strategy is not None:
            self._strategy = strategy
        elif recursive:
            self._strategy = "recursive_dfs"
        else:
            self._strategy = "iterative_greedy"

        # Session state
        self._created_at = time.time()
        self._last_used = time.time()
        self._lock = threading.RLock()  # Reentrant lock for nested calls
        self._last_trace = None  # PlanTrace from the most recent find_plan(..., trace=True) call
        self._stats = {
            "plans_generated": 0,
            "total_planning_time_ms": 0,
            "total_execution_time_ms": 0,
            "errors": 0,
            "memory_usage_mb": 0,
            "peak_memory_mb": 0,
            "timeouts": 0,
            "cancellations": 0
        }

        # Start memory tracking if enabled
        if self.memory_tracking:
            ResourceManager.start_memory_tracking(self.session_id, self.memory_sampling_interval)

        # Logging setup
        if structured_logging and _STRUCTURED_LOGGING_AVAILABLE:
            self.logger = get_logger(self.session_id)
            self.logger.info("session", f"Created session {self.session_id}",
                           domain=domain.__name__ if domain else None,
                           verbose=verbose, recursive=recursive)
        else:
            self.logger = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        if self.auto_cleanup:
            self.cleanup()

    @property
    def recursive(self):
        """Whether the session uses recursive DFS (derived from self._strategy)."""
        return self._strategy == "recursive_dfs"

    def _update_last_used(self):
        """Update last used timestamp."""
        self._last_used = time.time()

    def _log_operation(self, operation: str, **context):
        """Log session operation."""
        if self.logger:
            self.logger.info("session", f"Operation: {operation}", **context)

    @contextmanager
    def isolated_execution(self, trace: bool = False, trace_state: bool = False):
        """
        Context manager for isolated execution with state restoration.
        Saves and restores global GTPyhop state (domain, verbose, strategy,
        trace collector).

        Args:
            trace: If True, activate a PlanTrace for the duration of the
                yielded block; retrievable afterward via self._last_trace
                (find_plan(..., trace=True) reads this into result.trace).
                Default False costs nothing beyond the save/restore of a
                single global already performed for domain/verbose/strategy.
            trace_state: If True, additionally snapshot the state each
                recorded event was attempted against (TraceEvent.state).
                Implies trace, since a snapshot without an event to attach
                it to is meaningless. Costs one deep copy of the state per
                recorded event, so it is off by default even when tracing.
        """
        global _current_seek_plan, _trace_collector, _trace_state

        # A snapshot has nowhere to live unless events are being recorded.
        trace = trace or trace_state

        # Save current global state
        saved_domain = current_domain
        saved_verbose = verbose
        saved_strategy = _current_seek_plan
        saved_trace_collector = _trace_collector
        saved_trace_state = _trace_state

        try:
            # Set session-specific state
            if self.domain:
                set_current_domain(self.domain)
            set_verbose_level(self.verbose)
            set_recursive_planning(self._strategy)
            _trace_collector = PlanTrace() if trace else None
            _trace_state = trace_state

            self._log_operation("isolated_execution_start",
                              saved_domain=saved_domain.__name__ if saved_domain else None,
                              saved_verbose=saved_verbose)

            yield self

        finally:
            # Capture the populated trace (if any) before the global is
            # restored, so find_plan can read it back after this context
            # manager exits.
            self._last_trace = _trace_collector

            # Restore global state
            if saved_domain:
                set_current_domain(saved_domain)
            set_verbose_level(saved_verbose)
            _current_seek_plan = saved_strategy
            _trace_collector = saved_trace_collector
            _trace_state = saved_trace_state

            self._log_operation("isolated_execution_end")

    def find_plan(self, state: 'State', todo_list: List, *,
                  timeout_ms: Optional[int] = None,
                  max_expansions: Optional[int] = None,
                  trace: bool = False,
                  trace_state: bool = False) -> PlanResult:
        """
        Generate a plan for the given state and todo list.

        Args:
            state: Initial state
            todo_list: List of tasks/goals to achieve
            timeout_ms: Maximum planning time in milliseconds
            max_expansions: ACCEPTED BUT NOT ENFORCED -- passing a value
                emits a UserWarning and has no effect on the search. The
                parameter has been part of this signature since 1.3.0 but
                was never threaded into the seek_plan_* functions, so a
                caller asking for a bounded search has silently been given
                an exhaustive one. It is kept (rather than removed) because
                a deterministic search-effort cap is genuinely wanted as a
                companion to timeout_ms's wall-clock cap -- notably for
                bounding a possibly-adversarial machine-generated domain --
                but implementing it means adding an expansion counter to
                seek_plan_recursive (which has none; the two iterative
                strategies count main-loop iterations locally) and settling
                what one "expansion" means. Use timeout_ms meanwhile.
            trace: If True, populate result.trace with a PlanTrace recording
                every action-application attempt made during the search
                (depth, action, status). Default False; costs nothing when
                not requested. See PlanTrace for details.
            trace_state: If True, also record on each traced event a deep
                copy of the state that event was attempted against
                (TraceEvent.state), which is what lets a caller determine
                *which* precondition of a failing action did not hold rather
                than only that it failed. Implies trace. Default False:
                unlike trace, this one is not free even during a traced
                search -- it deep-copies the state once per recorded event.

        Returns:
            PlanResult with success status, plan, logs, and statistics
        """
        if max_expansions is not None:
            # Fail loudly rather than silently ignoring the cap: until this
            # is implemented, a caller passing it gets an exhaustive search
            # while believing the search was bounded. stacklevel=2 points
            # the warning at that caller, not at this line.
            warnings.warn(
                "find_plan(max_expansions=...) is accepted but NOT enforced: "
                "the search is not bounded by it. Use timeout_ms for a "
                "wall-clock bound. See the find_plan docstring for why the "
                "parameter is retained.",
                UserWarning,
                stacklevel=2,
            )

        with self._lock:
            self._update_last_used()
            start_time = time.time()

            result = PlanResult(success=False, session_id=self.session_id)
            # Reset so a stale trace from a previous call can't leak through
            # if this call is interrupted (e.g. by timeout_ms) before
            # isolated_execution's finally block runs.
            self._last_trace = None

            try:
                self._log_operation("find_plan",
                                  state_name=state.__name__,
                                  todo_count=len(todo_list),
                                  timeout_ms=timeout_ms,
                                  max_expansions=max_expansions)

                # Clear any previous cancellation flags
                ResourceManager.clear_cancellation_flag(self.session_id)

                # Use session-specific planning methods with timeout enforcement
                if timeout_ms and timeout_ms > 0:
                    # Apply timeout decorator to planning function
                    @ResourceManager.with_timeout(timeout_ms, self.session_id)
                    def timed_planning():
                        if self._strategy == "recursive_dfs":
                            return self._plan_recursive(state, todo_list, trace=trace, trace_state=trace_state)
                        elif self._strategy == "iterative_dfs_backtracking":
                            return self._plan_iterative_bt(state, todo_list, trace=trace, trace_state=trace_state)
                        else:
                            return self._plan_iterative(state, todo_list, trace=trace, trace_state=trace_state)
                    plan = timed_planning()
                else:
                    if self._strategy == "recursive_dfs":
                        plan = self._plan_recursive(state, todo_list, trace=trace, trace_state=trace_state)
                    elif self._strategy == "iterative_dfs_backtracking":
                        plan = self._plan_iterative_bt(state, todo_list, trace=trace, trace_state=trace_state)
                    else:
                        plan = self._plan_iterative(state, todo_list, trace=trace, trace_state=trace_state)

                # Process results
                duration_ms = int((time.time() - start_time) * 1000)

                if plan is not False and plan is not None:
                    result.success = True
                    result.plan = plan
                    self._stats["plans_generated"] += 1
                else:
                    result.error = "No plan found"
                    self._stats["errors"] += 1

                result.stats = {
                    "duration_ms": duration_ms,
                    "expansions": getattr(self, '_last_expansions', 0),
                    "strategy": self._strategy
                }

            except PlanningTimeoutError as e:
                result.error = f"Planning timeout: {e}"
                self._stats["errors"] += 1
                self._stats["timeouts"] += 1
                if "cancelled" in str(e).lower():
                    self._stats["cancellations"] += 1
                self._log_operation("find_plan_timeout", error=str(e))

            except Exception as e:
                result.error = f"Planning error: {e}"
                self._stats["errors"] += 1
                self._log_operation("find_plan_error", error=str(e))

            # Always populate result.trace, even if an exception propagated
            # out of the search (isolated_execution's finally block still
            # captures whatever was recorded up to the point of failure --
            # this is exactly the case where a partial trace showing "here's
            # the malformed step right before the crash" matters most).
            result.trace = self._last_trace

            # Always update timing stats
            duration_ms = int((time.time() - start_time) * 1000)
            self._stats["total_planning_time_ms"] += duration_ms

            # Update memory statistics if tracking is enabled
            if self.memory_tracking:
                memory_stats = ResourceManager.get_memory_usage(self.session_id)
                self._stats["memory_usage_mb"] = memory_stats["memory_mb"]
                self._stats["peak_memory_mb"] = max(self._stats["peak_memory_mb"], memory_stats["peak_memory_mb"])
            else:
                memory_stats = {"memory_mb": 0.0, "peak_memory_mb": 0.0}

            # Ensure result has complete stats
            if not result.stats:
                result.stats = {}

            result.stats.update({
                "duration_ms": duration_ms,
                "expansions": getattr(self, '_last_expansions', 0),
                "strategy": self._strategy,
                "memory_mb": memory_stats["memory_mb"],
                "peak_memory_mb": memory_stats["peak_memory_mb"]
            })

            # Collect logs
            if self.logger:
                result.logs = self.logger.get_logs()

            return result

    def _plan_recursive(self, state: 'State', todo_list: List, trace: bool = False,
                        trace_state: bool = False) -> Optional[List[Tuple]]:
        """Session-specific recursive planning implementation."""
        with self.isolated_execution(trace=trace, trace_state=trace_state):
            return seek_plan_recursive(state, todo_list, [], 0)

    def _plan_iterative(self, state: 'State', todo_list: List, trace: bool = False,
                        trace_state: bool = False) -> Optional[List[Tuple]]:
        """Session-specific iterative planning implementation."""
        with self.isolated_execution(trace=trace, trace_state=trace_state):
            return seek_plan_iterative(state, todo_list, [], 0)

    def _plan_iterative_bt(self, state: 'State', todo_list: List, trace: bool = False,
                           trace_state: bool = False) -> Optional[List[Tuple]]:
        """Session-specific iterative backtracking planning implementation."""
        with self.isolated_execution(trace=trace, trace_state=trace_state):
            return seek_plan_iterative_backtracking(state, todo_list, [], 0)

    def run_lazy_lookahead(self, state: 'State', todo_list: List, *,
                          max_tries: int = 10,
                          timeout_ms: Optional[int] = None) -> ExecutionResult:
        """
        Session-based plan-and-act execution.

        Args:
            state: Initial state
            todo_list: List of tasks/goals to achieve
            max_tries: Maximum number of planning attempts
            timeout_ms: Maximum execution time in milliseconds

        Returns:
            ExecutionResult with success status, final state, executed actions, logs, and statistics
        """
        with self._lock:
            self._update_last_used()
            start_time = time.time()

            result = ExecutionResult(success=False, session_id=self.session_id)
            result.final_state = state.copy()

            try:
                self._log_operation("run_lazy_lookahead",
                                  state_name=state.__name__,
                                  todo_count=len(todo_list),
                                  max_tries=max_tries,
                                  timeout_ms=timeout_ms)

                # Clear any previous cancellation flags
                ResourceManager.clear_cancellation_flag(self.session_id)

                # Execute plan-and-act loop with timeout if specified
                if timeout_ms and timeout_ms > 0:
                    @ResourceManager.with_timeout(timeout_ms, self.session_id)
                    def timed_execution():
                        return self._execute_lazy_lookahead_loop(result.final_state, todo_list, max_tries)
                    final_state, executed_actions, tries_used = timed_execution()
                else:
                    final_state, executed_actions, tries_used = self._execute_lazy_lookahead_loop(result.final_state, todo_list, max_tries)

                # Process results
                result.success = True
                result.final_state = final_state
                result.executed_actions = executed_actions
                result.tries_used = tries_used

            except PlanningTimeoutError as e:
                result.error = f"Execution timeout: {e}"
                self._stats["errors"] += 1
                self._stats["timeouts"] += 1
                if "cancelled" in str(e).lower():
                    self._stats["cancellations"] += 1
                self._log_operation("run_lazy_lookahead_timeout", error=str(e))

            except Exception as e:
                result.error = f"Execution error: {e}"
                self._stats["errors"] += 1
                self._log_operation("run_lazy_lookahead_error", error=str(e))

            # Always update timing stats
            duration_ms = int((time.time() - start_time) * 1000)
            self._stats["total_execution_time_ms"] += duration_ms

            # Update memory statistics if tracking is enabled
            if self.memory_tracking:
                memory_stats = ResourceManager.get_memory_usage(self.session_id)
                self._stats["memory_usage_mb"] = memory_stats["memory_mb"]
                self._stats["peak_memory_mb"] = max(self._stats["peak_memory_mb"], memory_stats["peak_memory_mb"])
            else:
                memory_stats = {"memory_mb": 0.0, "peak_memory_mb": 0.0}

            # Ensure result has complete stats
            if not result.stats:
                result.stats = {}

            result.stats.update({
                "duration_ms": duration_ms,
                "tries_used": result.tries_used,
                "executed_actions": len(result.executed_actions),
                "memory_mb": memory_stats["memory_mb"],
                "peak_memory_mb": memory_stats["peak_memory_mb"]
            })

            # Collect logs
            if self.logger:
                result.logs = self.logger.get_logs()

            return result

    def _execute_lazy_lookahead_loop(self, state: 'State', todo_list: List, max_tries: int) -> Tuple['State', List[Tuple], int]:
        """Execute the lazy lookahead loop with session isolation."""
        current_state = state.copy()
        executed_actions = []

        for try_num in range(max_tries):
            # Check for cancellation
            ResourceManager.check_cancellation(self.session_id)

            # Find a plan
            with self.isolated_execution():
                plan = find_plan(current_state, todo_list)

            if not plan or plan is False:
                # No plan found, we're done
                break

            if not todo_list:
                # No more goals, we're done
                break

            # Execute actions from the plan
            plan_executed = False
            for action in plan:
                # Check for cancellation
                ResourceManager.check_cancellation(self.session_id)

                # Try to execute the action as a command first, then as an action
                action_name = action[0]
                action_args = action[1:]

                # Execute with potential timeout for individual actions
                def execute_action():
                    with self.isolated_execution():
                        # Try command first
                        if current_domain and action_name in current_domain._command_dict:
                            command = current_domain._command_dict[action_name]
                            return command(current_state.copy(), *action_args)
                        elif current_domain and action_name in current_domain._action_dict:
                            # Fall back to action
                            action_func = current_domain._action_dict[action_name]
                            return action_func(current_state.copy(), *action_args)
                        else:
                            return False

                new_state = execute_action()

                if new_state and new_state is not False:
                    current_state = new_state
                    executed_actions.append(action)
                    plan_executed = True
                else:
                    # Action failed, break out of action loop to replan
                    break

            if not plan_executed:
                # No actions could be executed, we're stuck
                break

        return current_state, executed_actions, try_num + 1

    def save_to_file(self, filepath: str, format: str = 'json') -> bool:
        """
        Save session state to file.

        Args:
            filepath: Path to save the session file
            format: Serialization format ('json' or 'pickle')

        Returns:
            True if successful, False otherwise
        """
        try:
            start_time = time.time()

            # Serialize session data
            data = SessionSerializer.serialize_session(self, format)

            # Write to file atomically
            temp_filepath = filepath + '.tmp'
            with open(temp_filepath, 'wb') as f:
                f.write(data)

            # Atomic rename
            if os.path.exists(filepath):
                backup_filepath = filepath + '.backup'
                os.rename(filepath, backup_filepath)

            os.rename(temp_filepath, filepath)

            # Clean up backup if successful
            backup_filepath = filepath + '.backup'
            if os.path.exists(backup_filepath):
                os.remove(backup_filepath)

            # Update statistics
            duration_ms = int((time.time() - start_time) * 1000)
            if 'persistence_operations' not in self._stats:
                self._stats['persistence_operations'] = 0
            if 'persistence_time_ms' not in self._stats:
                self._stats['persistence_time_ms'] = 0

            self._stats['persistence_operations'] += 1
            self._stats['persistence_time_ms'] += duration_ms

            self._log_operation("save_session", filepath=filepath, format=format, duration_ms=duration_ms)
            return True

        except Exception as e:
            self._log_operation("save_session_error", filepath=filepath, error=str(e))
            return False

    @classmethod
    def load_from_file(cls, filepath: str, format: str = 'json') -> Optional['PlannerSession']:
        """
        Load session state from file.

        Args:
            filepath: Path to the session file
            format: Serialization format ('json' or 'pickle')

        Returns:
            Restored PlannerSession or None if failed
        """
        try:
            if not os.path.exists(filepath):
                return None

            # Read file data
            with open(filepath, 'rb') as f:
                data = f.read()

            # Deserialize session data
            session_data = SessionSerializer.deserialize_session(data, format)

            # Validate data
            if not SessionSerializer.validate_session_data(session_data):
                raise SessionPersistenceError("Invalid session data")

            # Reconstruct session
            session = cls._reconstruct_from_data(session_data)

            if session and session.logger:
                session._log_operation("load_session", filepath=filepath, format=format)

            return session

        except Exception as e:
            # Try to log error if possible, but don't fail if logging fails
            try:
                if _global_logger:
                    _global_logger.error("session", f"Failed to load session from {filepath}: {e}")
            except:
                pass
            return None

    @classmethod
    def _reconstruct_from_data(cls, session_data: Dict[str, Any]) -> Optional['PlannerSession']:
        """
        Reconstruct a PlannerSession from deserialized data.

        Args:
            session_data: Deserialized session data

        Returns:
            Reconstructed PlannerSession or None if failed
        """
        try:
            # Find domain by name if specified
            domain = None
            domain_name = session_data.get('domain_name')
            if domain_name:
                domain = find_domain_by_name(domain_name)
                if not domain:
                    # Domain not found, create session without domain
                    pass

            # Resolve strategy (backward compat: older data lacks 'strategy' field)
            strategy = session_data.get('strategy', None)

            # Create new session with restored configuration
            session = cls(
                session_id=session_data['session_id'],
                domain=domain,
                verbose=session_data['verbose'],
                recursive=session_data['recursive'],
                strategy=strategy,
                structured_logging=session_data.get('structured_logging', True),
                auto_cleanup=session_data.get('auto_cleanup', True)
            )

            # Restore timestamps and statistics
            session._created_at = session_data['created_at']
            session._last_used = session_data.get('last_used', session_data['created_at'])
            session._stats.update(session_data['stats'])

            return session

        except Exception as e:
            return None

    def get_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        with self._lock:
            return {
                **self._stats,
                "session_id": self.session_id,
                "created_at": self._created_at,
                "last_used": self._last_used,
                "age_seconds": time.time() - self._created_at,
                "idle_seconds": time.time() - self._last_used,
                "domain": self.domain.__name__ if self.domain else None
            }

    def cleanup(self):
        """Clean up session resources."""
        with self._lock:
            if self.logger:
                self._log_operation("cleanup", stats=self.get_stats())
                if _STRUCTURED_LOGGING_AVAILABLE and destroy_logger:
                    destroy_logger(self.session_id)
                self.logger = None

            # Stop resource tracking if it was enabled
            if self.memory_tracking:
                ResourceManager.stop_memory_tracking(self.session_id)

            # Clear references
            self.domain = None

# Global session registry
_sessions: Dict[str, PlannerSession] = {}
_sessions_lock = threading.Lock()
_default_session: Optional[PlannerSession] = None

################################################################################
# Process Cleanup and Persistence Management

# Process termination cleanup
_cleanup_handlers_registered = False
_persistence_directory: Optional[str] = None
_auto_save_enabled = True

class ProcessCleanupManager:
    """Manages graceful cleanup on process termination."""

    @staticmethod
    def register_cleanup_handlers():
        """Register signal handlers for graceful shutdown."""
        global _cleanup_handlers_registered

        if _cleanup_handlers_registered:
            return

        try:
            # Register atexit handler (works on all platforms)
            atexit.register(ProcessCleanupManager.cleanup_on_exit)

            # Register signal handlers (Unix-like systems)
            if hasattr(signal, 'SIGTERM'):
                signal.signal(signal.SIGTERM, ProcessCleanupManager.signal_handler)
            if hasattr(signal, 'SIGINT'):
                signal.signal(signal.SIGINT, ProcessCleanupManager.signal_handler)

            _cleanup_handlers_registered = True

        except Exception as e:
            # Cleanup registration failed, but don't fail the entire system
            if _global_logger:
                _global_logger.warning("cleanup", f"Failed to register cleanup handlers: {e}")

    @staticmethod
    def signal_handler(signum, frame):
        """Handle termination signals."""
        try:
            if _global_logger:
                _global_logger.info("cleanup", f"Received signal {signum}, initiating cleanup")

            ProcessCleanupManager.cleanup_on_exit()

            # Re-raise the signal for default handling
            if hasattr(signal, 'SIG_DFL'):
                signal.signal(signum, signal.SIG_DFL)
                os.kill(os.getpid(), signum)
            else:
                sys.exit(0)

        except Exception as e:
            # Emergency exit if cleanup fails
            sys.exit(1)

    @staticmethod
    def cleanup_on_exit():
        """Perform cleanup operations on process exit."""
        try:
            if _auto_save_enabled and _persistence_directory:
                ProcessCleanupManager.auto_save_sessions()

            ProcessCleanupManager.cleanup_all_sessions()

        except Exception as e:
            # Don't let cleanup errors prevent exit
            pass

    @staticmethod
    def auto_save_sessions():
        """Auto-save all active sessions."""
        try:
            if not _persistence_directory or not os.path.exists(_persistence_directory):
                return

            with _sessions_lock:
                sessions_to_save = list(_sessions.values())
                if _default_session:
                    sessions_to_save.append(_default_session)

            for session in sessions_to_save:
                try:
                    filepath = os.path.join(_persistence_directory, f"{session.session_id}.json")
                    session.save_to_file(filepath, format='json')
                except Exception:
                    # Continue with other sessions if one fails
                    continue

        except Exception:
            # Don't let auto-save errors prevent cleanup
            pass

    @staticmethod
    def cleanup_all_sessions():
        """Clean up all active sessions."""
        try:
            with _sessions_lock:
                sessions_to_cleanup = list(_sessions.values())
                if _default_session:
                    sessions_to_cleanup.append(_default_session)

            for session in sessions_to_cleanup:
                try:
                    session.cleanup()
                except Exception:
                    # Continue with other sessions if one fails
                    continue

        except Exception:
            # Don't let cleanup errors prevent exit
            pass

def set_persistence_directory(directory: str, auto_save: bool = True):
    """
    Set the directory for session persistence and enable auto-save.

    Args:
        directory: Directory path for saving sessions
        auto_save: Enable automatic saving on process termination
    """
    global _persistence_directory, _auto_save_enabled

    try:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        _persistence_directory = directory
        _auto_save_enabled = auto_save

        # Register cleanup handlers when persistence is enabled
        ProcessCleanupManager.register_cleanup_handlers()

        if _global_logger:
            _global_logger.info("persistence", f"Persistence directory set to {directory}, auto_save={auto_save}")

        return True

    except Exception as e:
        if _global_logger:
            _global_logger.error("persistence", f"Failed to set persistence directory: {e}")
        return False

def get_persistence_directory() -> Optional[str]:
    """Get the current persistence directory."""
    return _persistence_directory

################################################################################
# Global Session Management Functions

def create_session(session_id: Optional[str] = None, **kwargs) -> PlannerSession:
    """Create a new planning session."""
    with _sessions_lock:
        session = PlannerSession(session_id, **kwargs)
        _sessions[session.session_id] = session

        # Register cleanup handlers when first session is created
        ProcessCleanupManager.register_cleanup_handlers()

        return session

def restore_session(filepath: str, format: str = 'json') -> Optional[PlannerSession]:
    """
    Restore a session from a saved file with error recovery.

    Args:
        filepath: Path to the saved session file
        format: Serialization format ('json' or 'pickle')

    Returns:
        Restored PlannerSession or None if restoration failed
    """
    try:
        # Try to load the session
        session = PlannerSession.load_from_file(filepath, format)

        if session is None:
            # Try backup file if main file failed
            backup_filepath = filepath + '.backup'
            if os.path.exists(backup_filepath):
                session = PlannerSession.load_from_file(backup_filepath, format)
                if session and _global_logger:
                    _global_logger.warning("recovery", f"Restored session from backup: {backup_filepath}")

        if session is None:
            return None

        # Register the restored session
        with _sessions_lock:
            if session.session_id in _sessions:
                # Session ID conflict, generate new ID
                original_id = session.session_id
                session.session_id = f"{original_id}_restored_{uuid.uuid4().hex[:8]}"
                if _global_logger:
                    _global_logger.warning("recovery", f"Session ID conflict, renamed {original_id} to {session.session_id}")

            _sessions[session.session_id] = session

        if _global_logger:
            _global_logger.info("recovery", f"Successfully restored session {session.session_id}")

        return session

    except Exception as e:
        if _global_logger:
            _global_logger.error("recovery", f"Failed to restore session from {filepath}: {e}")
        return None

def restore_all_sessions(directory: str, format: str = 'json') -> List[PlannerSession]:
    """
    Restore all sessions from a directory with error recovery.

    Args:
        directory: Directory containing saved session files
        format: Serialization format ('json' or 'pickle')

    Returns:
        List of successfully restored sessions
    """
    restored_sessions = []

    try:
        if not os.path.exists(directory):
            return restored_sessions

        # Find all session files
        extension = '.json' if format == 'json' else '.pkl'
        session_files = [f for f in os.listdir(directory) if f.endswith(extension)]

        for filename in session_files:
            filepath = os.path.join(directory, filename)
            session = restore_session(filepath, format)
            if session:
                restored_sessions.append(session)

        if _global_logger:
            _global_logger.info("recovery", f"Restored {len(restored_sessions)} sessions from {directory}")

    except Exception as e:
        if _global_logger:
            _global_logger.error("recovery", f"Failed to restore sessions from {directory}: {e}")

    return restored_sessions

def get_session(session_id: Optional[str] = None) -> PlannerSession:
    """Get existing session or create default session."""
    global _default_session

    if session_id is None:
        if _default_session is None:
            _default_session = PlannerSession("default", domain=current_domain)
        return _default_session

    with _sessions_lock:
        if session_id not in _sessions:
            raise ValueError(f"Session '{session_id}' not found")
        return _sessions[session_id]

def destroy_session(session_id: str) -> bool:
    """Destroy a planning session."""
    global _default_session

    with _sessions_lock:
        if session_id == "default":
            if _default_session:
                _default_session.cleanup()
                _default_session = None
                return True
            return False

        session = _sessions.pop(session_id, None)
        if session:
            session.cleanup()
            return True
        return False

def list_sessions() -> List[str]:
    """List all active session IDs."""
    with _sessions_lock:
        active_sessions = list(_sessions.keys())
        if _default_session:
            active_sessions.append("default")
        return active_sessions

################################################################################
#                                                                              #
#                            END OF GTPYHOP 2.0.0                              #
#                                                                              #
################################################################################

# Note: Import-time initialization is now handled in __init__.py