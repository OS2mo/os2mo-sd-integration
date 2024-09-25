# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import date
from datetime import datetime

from sdclient.client import SDClient
from sdclient.responses import EmploymentWithLists
from zoneinfo import ZoneInfo

TIMEZONE = ZoneInfo("Europe/Copenhagen")


class SD:
    def __init__(self, username: str, password: str, institution_identifier: str):
        self.institution_identifier = institution_identifier
        self.client = SDClient(username, password)

    def build_timeline(
        self,
        start_date: date,
        cpr: str,
        emp_id: str,
    ) -> EmploymentWithLists:
        """
        Build the entire employment timeline for a given person and employment.

        Args:
            sd_client: The SDClient.
            inst_id: The SD InstitutionIdentifier.
            start_date: The date back to which we should at least include SD employment
                data. The start_date must be less than or equal to today.
            cpr: CPR-number of the person.
            emp_id: The SD EmploymentIdentifier for the persons employment.

        Returns:
            Entire employment timeline.
        """

        now = datetime.now(tz=TIMEZONE).date()
        assert start_date <= now, "start_date must be less than or equal to today"
