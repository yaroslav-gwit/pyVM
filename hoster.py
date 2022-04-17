#!/usr/bin/env python3
import typer
import sys
import os
import subprocess

# Own libraries
from cli.vm import vm
from cli.host import host

""" Section below is responsible for the CLI input/output """
app = typer.Typer(context_settings=dict(max_content_width=800))
app.add_typer(vm.app, name="vm", help="List, Create, Remove or any other VM related operations")
app.add_typer(host.app, name="host", help="Show or modify the host related information")


@app.command()
def version(json: bool = typer.Option(False, help="JSON output")):
    """
    Show version and exit
    """

    print("Version: development-0.1-alpha")



""" If this file is executed from the command line, activate Typer """
if __name__ == "__main__":
    app()