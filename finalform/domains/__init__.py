"""Domain-specific processors for finalform.

Each domain handles a specific category of measurement:
- questionnaire: Clinical questionnaires, scales, inventories, checklists
- lab: Laboratory panels and test results
- vital: Vital signs measurements
- wearable: Wearable device data streams
"""

from finalform.domains.lab import LabProcessor
from finalform.domains.questionnaire import QuestionnaireProcessor
from finalform.domains.vital import VitalProcessor
from finalform.domains.wearable import WearableProcessor

__all__ = [
    "LabProcessor",
    "QuestionnaireProcessor",
    "VitalProcessor",
    "WearableProcessor",
]
