"""Application-wide constants.

TODO: Add CrimeNo format masks, case category codes (FIR/UDR/PAR/Zero FIR),
      and Catalyst table name prefixes.
"""

from __future__ import annotations

APP_NAME = "crime-intelligence-platform"
API_VERSION = "v1"

# CrimeNo structure (from Police_FIR_ER_Diagram.pdf):
# 1-digit Case Category + 4-digit District ID + 4-digit Police Station ID
# + 4-digit Year + 5-digit Running Serial
# TODO: Encode validation helpers once domain logic is implemented.
CRIME_NO_TOTAL_LENGTH = 18

CASE_CATEGORY_FIR = "1"
CASE_CATEGORY_UDR = "3"
CASE_CATEGORY_PAR = "4"
CASE_CATEGORY_ZERO_FIR = "8"
