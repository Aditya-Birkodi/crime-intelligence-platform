"""SQLAlchemy ORM models for FIR domain (B1+).

Table names use cip_ prefix to align with Catalyst Data Store plan.
"""

from __future__ import annotations

from app.models.case.accused import Accused
from app.models.case.act_section_association import ActSectionAssociation
from app.models.case.arrest_surrender import ArrestSurrender

# Case
from app.models.case.case_master import CaseMaster
from app.models.case.chargesheet_details import ChargesheetDetails
from app.models.case.complainant_details import ComplainantDetails
from app.models.case.inv_arrest_surrender_accused import InvArrestSurrenderAccused
from app.models.case.inv_occurance_time import InvOccuranceTime
from app.models.case.victim import Victim
from app.models.geography.court import Court
from app.models.geography.district import District

# Geography
from app.models.geography.state import State
from app.models.geography.unit import Unit
from app.models.geography.unit_type import UnitType

# Legal
from app.models.legal.act import Act
from app.models.legal.crime_head import CrimeHead
from app.models.legal.crime_head_act_section import CrimeHeadActSection
from app.models.legal.crime_sub_head import CrimeSubHead
from app.models.legal.section import Section

# Lookups
from app.models.lookups.case_category import CaseCategory
from app.models.lookups.case_status_master import CaseStatusMaster
from app.models.lookups.caste_master import CasteMaster
from app.models.lookups.gravity_offence import GravityOffence
from app.models.lookups.occupation_master import OccupationMaster
from app.models.lookups.religion_master import ReligionMaster

# Personnel
from app.models.personnel.designation import Designation
from app.models.personnel.employee import Employee
from app.models.personnel.rank import Rank

__all__ = [
    "CaseCategory",
    "CaseStatusMaster",
    "GravityOffence",
    "CasteMaster",
    "ReligionMaster",
    "OccupationMaster",
    "State",
    "District",
    "UnitType",
    "Unit",
    "Court",
    "Act",
    "Section",
    "CrimeHead",
    "CrimeSubHead",
    "CrimeHeadActSection",
    "Rank",
    "Designation",
    "Employee",
    "CaseMaster",
    "Accused",
    "Victim",
    "ComplainantDetails",
    "ActSectionAssociation",
    "InvOccuranceTime",
    "ArrestSurrender",
    "InvArrestSurrenderAccused",
    "ChargesheetDetails",
]
