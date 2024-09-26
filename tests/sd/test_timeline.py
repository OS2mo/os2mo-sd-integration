# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import date
from datetime import datetime
from datetime import timedelta
from unittest.mock import MagicMock

import pytest
from freezegun import freeze_time
from sdclient.client import SDClient
from sdclient.requests import GetEmploymentChangedRequest
from sdclient.requests import GetEmploymentRequest
from sdclient.responses import Employment
from sdclient.responses import EmploymentDepartment
from sdclient.responses import EmploymentStatus
from sdclient.responses import EmploymentWithLists
from sdclient.responses import Profession

from sdlon.sd.timeline import SD
from sdlon.sd.timeline import TIMEZONE

CPR = "0101011234"
EMP_ID = "12345"

CURRENT_EMPLOYMENT = Employment(
    EmploymentIdentifier="12345",
    EmploymentDate=date(1999, 1, 1),
    AnniversaryDate=date(1999, 1, 1),
    EmploymentStatus=EmploymentStatus(
        ActivationDate=date(2000, 1, 1),
        DeactivationDate=date(2000, 12, 31),
        EmploymentStatusCode=1,
    ),
    EmploymentDepartment=EmploymentDepartment(
        ActivationDate=date(2000, 1, 1),
        DeactivationDate=date(2000, 12, 31),
        DepartmentIdentifier="ABCD",
        DepartmentUUIDIdentifier="6220a7b8-db38-46d6-9a36-e1f432db2726",
    ),
    Profession=Profession(
        ActivationDate=date(2000, 1, 1),
        DeactivationDate=date(2000, 12, 31),
        JobPositionIdentifier=1000,
        EmploymentName="Ninja",
        AppointmentCode="1",
    ),
)

FUTURE_EMP_STATUSES = [
    EmploymentStatus(
        ActivationDate=date(2001, 1, 1),
        DeactivationDate=date(2001, 12, 31),
        EmploymentStatusCode=3,
    ),
    EmploymentStatus(
        ActivationDate=date(2002, 1, 1),
        DeactivationDate=date(9999, 12, 31),
        EmploymentStatusCode=1,
    ),
]

FUTURE_EMP_DEPARTMENTS = [
    EmploymentDepartment(
        ActivationDate=date(2001, 1, 1),
        DeactivationDate=date(2005, 12, 31),
        DepartmentIdentifier="BCDE",
        DepartmentUUIDIdentifier="123457b8-db38-46d6-9a36-e1f432db2726",
    ),
    EmploymentDepartment(
        ActivationDate=date(2006, 1, 1),
        DeactivationDate=date(9999, 12, 31),
        DepartmentIdentifier="ABCD",
        DepartmentUUIDIdentifier="6220a7b8-db38-46d6-9a36-e1f432db2726",
    ),
]

FUTURE_EMP_PROFESSIONS = [
    Profession(
        ActivationDate=date(2001, 1, 1),
        DeactivationDate=date(2003, 12, 31),
        JobPositionIdentifier=2000,
        EmploymentName="Shogun",
        AppointmentCode="0",
    ),
    Profession(
        ActivationDate=date(2004, 1, 1),
        DeactivationDate=date(9999, 12, 31),
        JobPositionIdentifier=3000,
        EmploymentName="Kejser",
        AppointmentCode="1",
    ),
]


def test__get_sd_employments() -> None:
    # Arrange
    sd = SD("username", "password", "II")
    fake_get_employment_response = MagicMock()
    sd.client = MagicMock(spec=SDClient)
    sd.client.get_employment.return_value = fake_get_employment_response

    now = datetime.now(tz=TIMEZONE).date()

    # Act
    emp = sd._get_sd_employments(now, CPR, EMP_ID)

    # Assert
    sd.client.get_employment.assert_called_once_with(
        GetEmploymentRequest(
            InstitutionIdentifier="II",
            EffectiveDate=now,
            PersonCivilRegistrationIdentifier=CPR,
            EmploymentIdentifier=EMP_ID,
            StatusActiveIndicator=True,
            StatusPassiveIndicator=True,
            EmploymentStatusIndicator=True,
            DepartmentIndicator=True,
            ProfessionIndicator=True,
            WorkingTimeIndicator=True,
            UUIDIndicator=True,
        )
    )
    assert emp == fake_get_employment_response


def test__get_sd_employments_changed() -> None:
    # Arrange
    sd = SD("username", "password", "II")
    fake_get_employment_changed_response = MagicMock()
    sd.client = MagicMock(spec=SDClient)
    sd.client.get_employment_changed.return_value = fake_get_employment_changed_response

    now = datetime.now(tz=TIMEZONE).date()
    tomorrow = now + timedelta(days=1)

    # Act
    emp = sd._get_sd_employments_changed(now, tomorrow, CPR, EMP_ID)

    # Assert
    sd.client.get_employment_changed.assert_called_once_with(
        GetEmploymentChangedRequest(
            InstitutionIdentifier="II",
            PersonCivilRegistrationIdentifier=CPR,
            EmploymentIdentifier=EMP_ID,
            ActivationDate=now,
            DeactivationDate=tomorrow,
            EmploymentStatusIndicator=True,
            DepartmentIndicator=True,
            ProfessionIndicator=True,
            WorkingTimeIndicator=True,
            UUIDIndicator=True,
        )
    )
    assert emp == fake_get_employment_changed_response


@pytest.mark.parametrize(
    "future_emp_status_list, future_emp_dep_list, future_emp_prof_list",
    [
        (FUTURE_EMP_STATUSES, FUTURE_EMP_DEPARTMENTS, FUTURE_EMP_PROFESSIONS),
        ([], [], []),
    ],
)
def test_get_current_and_future_emp_timeline(
    future_emp_status_list: list[EmploymentStatus],
    future_emp_dep_list: list[EmploymentDepartment],
    future_emp_prof_list: list[Profession],
) -> None:
    # Arrange
    employment_changed = EmploymentWithLists(
        EmploymentIdentifier="12345",
        EmploymentStatus=future_emp_status_list,
        EmploymentDepartment=future_emp_dep_list,
        Profession=future_emp_prof_list,
    )

    # Act
    emp_timeline = SD.get_current_and_future_emp_timeline(
        CURRENT_EMPLOYMENT, employment_changed
    )

    # Assert
    assert emp_timeline == EmploymentWithLists(
        EmploymentIdentifier="12345",
        EmploymentDate=date(1999, 1, 1),
        AnniversaryDate=date(1999, 1, 1),
        EmploymentStatus=[
            EmploymentStatus(
                ActivationDate=date(2000, 1, 1),
                DeactivationDate=date(2000, 12, 31),
                EmploymentStatusCode=1,
            ),
        ]
        + future_emp_status_list,
        EmploymentDepartment=[
            EmploymentDepartment(
                ActivationDate=date(2000, 1, 1),
                DeactivationDate=date(2000, 12, 31),
                DepartmentIdentifier="ABCD",
                DepartmentUUIDIdentifier="6220a7b8-db38-46d6-9a36-e1f432db2726",
            )
        ]
        + future_emp_dep_list,
        Profession=[
            Profession(
                ActivationDate=date(2000, 1, 1),
                DeactivationDate=date(2000, 12, 31),
                JobPositionIdentifier=1000,
                EmploymentName="Ninja",
                AppointmentCode="1",
            )
        ]
        + future_emp_prof_list,
    )


def test_get_current_and_future_emp_timeline_no_current_employment() -> None:
    # Arrange
    employment_changed = EmploymentWithLists(
        EmploymentIdentifier="12345",
        EmploymentStatus=FUTURE_EMP_STATUSES,
        EmploymentDepartment=FUTURE_EMP_DEPARTMENTS,
        Profession=FUTURE_EMP_PROFESSIONS,
    )

    # Act
    emp_timeline = SD.get_current_and_future_emp_timeline(None, employment_changed)

    # Assert
    assert emp_timeline == EmploymentWithLists(
        EmploymentIdentifier="12345",
        EmploymentStatus=FUTURE_EMP_STATUSES,
        EmploymentDepartment=FUTURE_EMP_DEPARTMENTS,
        Profession=FUTURE_EMP_PROFESSIONS,
    )


@freeze_time("2024-01-01")
def test_build_timeline_start_date_ok() -> None:
    # Arrange
    sd = SD("username", "password", "II")

    # Act + Assert
    with pytest.raises(AssertionError):
        sd.build_timeline(date(2025, 1, 1), CPR, EMP_ID)
