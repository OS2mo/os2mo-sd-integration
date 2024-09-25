# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import date
from unittest.mock import MagicMock

import pytest
from freezegun import freeze_time

from sdlon.sd.timeline import build_timeline


@freeze_time("2024-01-01")
def test_build_timeline_start_date_ok() -> None:
    # Act + Assert
    with pytest.raises(AssertionError) as error:
        build_timeline(
            MagicMock(), "II", date(2025, 1, 1), "0101011234", "12345"
        )
