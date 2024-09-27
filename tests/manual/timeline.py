# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime

import click

from sdlon.sd.timeline import SD


@click.group()
@click.option("--username", required=True, help="SD username")
@click.option("--password", required=True, help="SD password")
@click.option(
    "--inst-id",
    required=True,
    help="SD institution identifier",
)
@click.pass_context
def cli(
    ctx,
    username: str,
    password: str,
    inst_id: str,
) -> None:
    ctx.ensure_object(dict)
    ctx.obj["username"] = username
    ctx.obj["password"] = password
    ctx.obj["inst_id"] = inst_id


@cli.command()
@click.option("--start-date", type=click.DateTime(), required=True)
@click.option("--cpr", required=True, help="Person CPR number")
@click.option("--emp-id", required=True, help="SDs EmploymentIdentifier")
@click.pass_context
def timeline(ctx, start_date: datetime, cpr: str, emp_id: str) -> None:
    """
    Print the timeline for an SD employment.

    Args:
        start_date: The date back to which we should at least include SD employment
            data. The start_date must be less than or equal to today.
        cpr: CPR-number of the person.
        emp_id: The SD EmploymentIdentifier for the persons employment.
    """
    sd = SD(
        username=ctx.obj["username"],
        password=ctx.obj["password"],
        institution_identifier=ctx.obj["inst_id"],
    )

    emp_timeline = sd.build_timeline(start_date.date(), cpr, emp_id)
    print(emp_timeline)


if __name__ == "__main__":
    cli(obj={})
