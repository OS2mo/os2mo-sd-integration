# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0

from fastramqpi.config import Settings as FastRAMQPISettings
from pydantic import BaseSettings


class Settings(BaseSettings):
    class Config:
        frozen = True
        env_nested_delimiter = "__"

    fastramqpi: FastRAMQPISettings


def get_settings(*args, **kwargs) -> Settings:
    return Settings(*args, **kwargs)
