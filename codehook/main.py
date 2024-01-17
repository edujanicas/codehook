import os.path
from pathlib import Path
from typing import List, Optional

import boto3
import typer
from dotenv import load_dotenv
from rich import print
from typing_extensions import Annotated

from .core import CodehookCore
from .model import CloudName, Events, SourceName

CODEHOOK_WELCOME_MESSAGE = """
</> Welcome to codehook! </>

Codehook relies on having your AWS account running on the background. So, before using Codehook, you need to set up authentication credentials for your AWS account using either the [blue link=https://console.aws.amazon.com/iam/home]IAM Console[/blue link] or the AWS CLI. 

For instructions about how to create a user using the IAM Console, see [blue link=https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html#id_users_create_console]Creating IAM users[/blue link]. 
Once the user has been created, see [blue link=https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html#Using_CreateAccessKey]Managing access keys[/blue link] to learn how to create and retrieve the keys used to authenticate the user.

If you have the [blue link=http://aws.amazon.com/cli/]AWS CLI[/blue link] installed, then you can use the [bold]aws configure[/bold] command to configure your credentials file:
"""

CODEHOOK_CONFIGURED_MESSAGE = """
</> Welcome to codehook! </>

Your AWS account is already configured. 
Run [bold]codehook reconfigure[/bold] for instructions on setting up a new AWS account.
"""

load_dotenv()
app = typer.Typer()
codehook_core = CodehookCore(CloudName.aws)


@app.callback()
def callback():
    """
    Webhook logic and infrastructure automated
    """


@app.command()
def configure():
    """
    We try to to use your AWS account configuration automatically.
    If you have the AWS CLI installed, then you can use the aws configure command to configure your credentials file.

    Boto3 will look in several locations when searching for credentials.
    The mechanism in which Boto3 looks for credentials is to search through a list of possible locations and stop as soon as it finds credentials.
    The order in which Boto3 searches for credentials is:
        1. Passing credentials as parameters in the boto.client() method
        2. Passing credentials as parameters when creating a Session object
        3. Environment variables
        4. Shared credential file (~/.aws/credentials)
        5. AWS config file (~/.aws/config)
        6. Assume Role provider
        7. Boto2 config file (/etc/boto.cfg and ~/.boto)
        8. Instance metadata service on an Amazon EC2 instance that has an IAM role configured.
    """
    print(CODEHOOK_CONFIGURED_MESSAGE) if boto3.resource("s3") else print(
        CODEHOOK_WELCOME_MESSAGE
    )


@app.command()
def reconfigure():
    """
    Reonfigure your local environment to connect to your AWS account
    """
    print(CODEHOOK_WELCOME_MESSAGE)


@app.command()
def create(
    command: Annotated[str, typer.Option()],
    name: Annotated[str, typer.Option()],
    source: Annotated[
        SourceName, typer.Option(case_sensitive=False)
    ] = SourceName.stripe,
    enabled_events: Annotated[
        Optional[List[Events]], typer.Option(case_sensitive=False)
    ] = list(Events.all),
):
    """
    This is the main command for codehook if you plan on using natural language to generate a function.
    Create takes a string, creates a Python function, and deploys it as a webhook handler,
    taking care of all the boilerplate and infrastructure for you. Depending on the source, the function can be using
    different skeletons.

    Deploys the handler in FILE as a webhook handler for SOURCE, optionally with a custom --name.
    If no custom name is given, the handler will inherit the file name
    """

    print("[bold red]Not implemented yet[/bold red]")
    print("Please use the deploy command instead")

    # TODO: Add a way to create a function from a string
    file = codehook_core.create(command, name, source, enabled_events)
    # codehook_core.deploy(file, name, source, enabled_events)


@app.command()
def deploy(
    file: Annotated[
        Path,
        typer.Option(
            exists=True,
            file_okay=True,
            dir_okay=False,
            writable=False,
            readable=True,
            resolve_path=True,
        ),
    ],
    name: Annotated[str, typer.Option()] = None,
    source: Annotated[
        SourceName, typer.Option(case_sensitive=False)
    ] = SourceName.stripe,
    enabled_events: Annotated[
        Optional[List[Events]], typer.Option(case_sensitive=False)
    ] = list(Events.all),
):
    """
    This is the main command for codehook. Deploy takes a function and deploys it as a webhook handler,
    taking care of all the boilerplate and infrastructure for you. Depending on the source, the function can be using
    different skeletons.

    Deploys the handler in FILE as a webhook handler for SOURCE, optionally with a custom --name.
    If no custom name is given, the handler will inherit the file name
    """
    if not name:
        name = os.path.splitext(os.path.basename(file))[0]

    codehook_core.deploy(file, name, source, enabled_events)


@app.command()
def list():
    """
    List all the endpoints currently deployed by Codehook
    """
    codehook_core.list()


@app.command()
def delete(
    lambda_function_name: Annotated[
        str, typer.Option(help="Name of the Lambda function to delete")
    ] = None,
    api_id: Annotated[str, typer.Option(help="Name of the Rest API to delete")] = None,
    webhook_id: Annotated[
        str, typer.Option(help="Name of the Webhook Endpoint to delete")
    ] = None,
    delete_all: Annotated[bool, typer.Option("--all")] = False,
):
    """
    Delete the REST API, AWS Lambda function, and security role
    """
    codehook_core.delete(lambda_function_name, api_id, webhook_id, delete_all)


if __name__ == "__main__":
    app()
