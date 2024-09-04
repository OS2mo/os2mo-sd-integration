# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0

from fastapi import APIRouter

from sdlon.depends import GraphQLClient

router = APIRouter()


@router.get("/trigger")
async def trigger(mo: GraphQLClient) -> dict[str, str]:
    # Make a sandbox query for now just to verify that it's working
    org = await mo.get_organization()
    return {"org_uuid": str(org.uuid)}
