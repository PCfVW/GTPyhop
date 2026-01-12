"""
Scalable Recursive Decomposition - Memory Tracking Example

This example demonstrates memory scaling behavior when planning complexity
arises from recursive method decomposition depth rather than data size.

Based on Alford et al. (2015) "Tight Bounds for HTN Planning", Theorem 4.1:
    Plan-existence for totally-ordered mostly-acyclic propositional HTN
    problems is PSPACE-complete.

The binary recursive structure produces 2^k leaf tasks for depth k.
"""

from .domain import the_domain
from .problems import get_problems

__all__ = ['the_domain', 'get_problems']
