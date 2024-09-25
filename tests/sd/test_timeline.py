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

from sdlon.sd.timeline import SD
from sdlon.sd.timeline import TIMEZONE

CPR = "0101011234"
EMP_ID = "12345"


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


@freeze_time("2024-01-01")
def test_build_timeline_start_date_ok() -> None:
    # Arrange
    sd = SD("username", "password", "II")

    # Act + Assert
    with pytest.raises(AssertionError):
        sd.build_timeline(date(2025, 1, 1), CPR, EMP_ID)
