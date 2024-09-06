# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0

from fastapi import FastAPI
from fastramqpi.main import FastRAMQPI

from sdlon import api
from sdlon.config import get_settings
from sdlon.depends import GraphQLClient


def create_app(**kwargs) -> FastAPI:
    settings = get_settings(**kwargs)

    fastramqpi = FastRAMQPI(
        application_name="sdlon",
        settings=settings.fastramqpi,
        graphql_version=22,
        graphql_client_cls=GraphQLClient,
    )

    # FastAPI router
    app = fastramqpi.get_app()
    app.include_router(api.router)

    return app
