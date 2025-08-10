"""
Compatibility wrapper for QGIS plugin loading.
The original mainPlugin.py had indentation errors causing IndentationError on load.
Logic moved to poiskmore.py; this file re-exports PoiskMorePlugin for compatibility.
"""

from .poiskmore import PoiskMorePlugin

__all__ = ["PoiskMorePlugin"]