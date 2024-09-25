# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import date
from datetime import datetime

from sdclient.client import SDClient
from sdclient.requests import GetEmploymentChangedRequest
from sdclient.requests import GetEmploymentRequest
from sdclient.responses import EmploymentWithLists
from sdclient.responses import GetEmploymentChangedResponse
from sdclient.responses import GetEmploymentResponse
from zoneinfo import ZoneInfo

TIMEZONE = ZoneInfo("Europe/Copenhagen")


class SD:
    def __init__(self, username: str, password: str, institution_identifier: str):
        self.institution_identifier = institution_identifier
        self.client = SDClient(username, password)

    def _get_sd_employments(
        self,
        effective_date: date,
        cpr: str,
        emp_id: str,
    ) -> GetEmploymentResponse:
        """
        Get SD employments from SD.

        Args:
            effective_date: the SD effective date
            cpr: CPR-number of the employee
            emp_id: SDs EmploymentIdentifier

        Returns:
            The SD employments
        """

        sd_employments = self.client.get_employment(
            GetEmploymentRequest(
                InstitutionIdentifier=self.institution_identifier,
                EffectiveDate=effective_date,
                PersonCivilRegistrationIdentifier=cpr,
                EmploymentIdentifier=emp_id,
                StatusActiveIndicator=True,
                StatusPassiveIndicator=True,
                EmploymentStatusIndicator=True,
                DepartmentIndicator=True,
                ProfessionIndicator=True,
                WorkingTimeIndicator=True,
                UUIDIndicator=True,
            )
        )
        return sd_employments

    def _get_sd_employments_changed(
        self,
        activation_date: date,
        deactivation_date: date,
        cpr: str,
        emp_id: str,
    ) -> GetEmploymentChangedResponse:
        """
        Get SD "employments changed" from SD via the GetEmploymentChanged
        endpoint.

        Args:
            activation_date: SDs ActivationDate
            deactivation_date: SDs DeactivationDate
            cpr: CPR-number of the employee
            emp_id: SDs EmploymentIdentifier

        Returns:
            The SD employments
        """

        sd_employments_changed = self.client.get_employment_changed(
            GetEmploymentChangedRequest(
                InstitutionIdentifier=self.institution_identifier,
                PersonCivilRegistrationIdentifier=cpr,
                EmploymentIdentifier=emp_id,
                ActivationDate=activation_date,
                DeactivationDate=deactivation_date,
                EmploymentStatusIndicator=True,
                DepartmentIndicator=True,
                ProfessionIndicator=True,
                WorkingTimeIndicator=True,
                UUIDIndicator=True,
            )
        )
        return sd_employments_changed

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
