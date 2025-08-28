# -*- coding: utf-8 -*-
"""Dialogs package."""

from .incident_registration_dialog import IncidentRegistrationDialog
from .authorization_dialog import AuthorizationDialog
from .about_dialog import AboutDialog
from .calculators_dialog import CalculatorsDialog
from .iamsar_reference_dialog import IAMSARReferenceDialog

__all__ = [
    "IncidentRegistrationDialog",
    "AuthorizationDialog",
    "AboutDialog",
    "CalculatorsDialog",
    "IAMSARReferenceDialog",
]
