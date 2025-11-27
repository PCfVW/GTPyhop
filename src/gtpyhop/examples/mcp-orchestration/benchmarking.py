#!/usr/bin/env python3
"""
Benchmarking Script Wrapper for MCP Orchestration Examples

This is a thin wrapper that imports and delegates to the benchmarking infrastructure
from the ipc-2020-total-order directory.

Usage:
    python benchmarking.py <domain_package_name> [options]

Example:
    python benchmarking.py tnf_cancer_modelling --verbose --mode session
"""

import sys
import os

# Import the benchmarking infrastructure from ipc-2020-total-order
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ipc-2020-total-order'))
from benchmarking import *

if __name__ == "__main__":
    sys.exit(main())

