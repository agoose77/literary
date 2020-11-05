"""Notebook magic module

This module provides a namespace that can be imported into a Jupyter notebook
using `%run -m literary.notebook`.

It is implemented separately to `literary.notebook.__init__` in order to avoid mutating
an imported module (this module is regenerated for every execution)
"""
from . import *

update_namespace(globals())
