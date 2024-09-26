# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import date
from datetime import datetime
from datetime import timedelta

from more_itertools import one
from sdclient.client import SDClient
from sdclient.requests import GetEmploymentChangedRequest
from sdclient.requests import GetEmploymentRequest
from sdclient.responses import Employment
from sdclient.responses import EmploymentDepartment
from sdclient.responses import EmploymentStatus
from sdclient.responses import EmploymentWithLists
from sdclient.responses import GetEmploymentChangedResponse
from sdclient.responses import GetEmploymentResponse
from structlog import get_logger
from zoneinfo import ZoneInfo

TIMEZONE = ZoneInfo("Europe/Copenhagen")


logger = get_logger()


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

    @staticmethod
    def get_current_and_future_emp_timeline(
        employment: Employment | None,
        employment_changed: EmploymentWithLists | None,
    ) -> EmploymentWithLists | None:
        if employment is None and employment_changed is None:
            return None

        def get_future_emp_attrs(
            attr: str,
        ) -> list[EmploymentStatus | EmploymentDepartment]:
            return (
                attr_
                if employment_changed is not None
                and (attr_ := getattr(employment_changed, attr)) is not None
                else []
            )

        # The EmploymentIdentifiers must match
        if employment is not None and employment_changed is not None:
            assert (
                employment.EmploymentIdentifier
                == employment_changed.EmploymentIdentifier
            )

        future_emp_statuses = get_future_emp_attrs("EmploymentStatus")
        future_emp_departments = get_future_emp_attrs("EmploymentDepartment")
        future_emp_professions = get_future_emp_attrs("Profession")

        if employment is not None:
            emp_timeline = EmploymentWithLists(
                EmploymentIdentifier=employment.EmploymentIdentifier,
                EmploymentDate=employment.EmploymentDate,
                AnniversaryDate=employment.AnniversaryDate,
                EmploymentStatus=[employment.EmploymentStatus] + future_emp_statuses,
                EmploymentDepartment=[employment.EmploymentDepartment]
                + future_emp_departments,
                Profession=[employment.Profession] + future_emp_professions,
            )
        else:
            assert employment_changed is not None
            emp_timeline = EmploymentWithLists(
                EmploymentIdentifier=employment_changed.EmploymentIdentifier,
                EmploymentDate=employment_changed.EmploymentDate,
                AnniversaryDate=employment_changed.AnniversaryDate,
                EmploymentStatus=future_emp_statuses,
                EmploymentDepartment=future_emp_departments,
                Profession=future_emp_professions,
            )

        return emp_timeline

    def build_timeline(
        self,
        start_date: date,
        cpr: str,
        emp_id: str,
    ) -> EmploymentWithLists | None:
        """
        Build the current and future employment timeline for a given person and
        employment.

        Args:
            sd_client: The SDClient.
            inst_id: The SD InstitutionIdentifier.
            start_date: The date back to which we should at least include SD employment
                data. The start_date must be less than or equal to today.
            cpr: CPR-number of the person.
            emp_id: The SD EmploymentIdentifier for the persons employment.

        Returns:
            Current and future employment timeline.
        """

        now = datetime.now(tz=TIMEZONE).date()
        assert start_date <= now, "start_date must be less than or equal to today"

        # Get timeline from today and onwards
        employment = self._get_sd_employments(now, cpr, emp_id)
        future_employments = self._get_sd_employments_changed(
            now + timedelta(days=1),  # Must be from tomorrow to avoid duplicates
            date.max,
            cpr,
            emp_id,
        )

        timeline = SD.get_current_and_future_emp_timeline(
            one(one(employment.Person).Employment),
            one(one(future_employments.Person).Employment),
        )

        return timeline
