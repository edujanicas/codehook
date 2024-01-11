import typer
import boto3

import os.path
from pathlib import Path
from typing_extensions import Annotated
from typing import Optional
from rich import print
from dotenv import load_dotenv
from .Deployer import Deployer
from .APIGateway import APIGateway
from .Lambda import Lambda
from .helpers import Source, Events

load_dotenv()
app = typer.Typer()

CODEHOOK_WELCOME_MESSAGE = """
</> Welcome to codehook! </>
Codehook relies on having your AWS account running on the background. So, before using Codehook, you need to set up authentication credentials for your AWS account using either the [blue link=https://console.aws.amazon.com/iam/home]IAM Console[/blue link] or the AWS CLI. 

For instructions about how to create a user using the IAM Console, see [blue link=https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html#id_users_create_console]Creating IAM users[/blue link]. 
Once the user has been created, see [blue link=https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html#Using_CreateAccessKey]Managing access keys[/blue link] to learn how to create and retrieve the keys used to authenticate the user.

If you have the [blue link=http://aws.amazon.com/cli/]AWS CLI[/blue link] installed, then you can use the [bold]aws configure[/bold] command to configure your credentials file:
"""


def init_aws() -> tuple[APIGateway, Lambda]:
    iam_resource = boto3.resource("iam")
    lambda_client = boto3.client("lambda")
    apigateway_client = boto3.client("apigateway")
    api_wrapper = APIGateway(apigateway_client)
    lambda_wrapper = Lambda(lambda_client, iam_resource)

    return api_wrapper, lambda_wrapper


@app.callback()
def callback():
    """
    Webhook logic and infrastructure automated
    """


@app.command()
def configure():
    """
    Configure your local environment to connect to your AWS account
    """
    if boto3.resource('s3'):
        print(
            """
</> Welcome to codehook! </>

Your AWS account is already configured. Run [bold]codehook reconfigure[/bold] for instructions on setting up a new AWS account.
            """
        )
    else:
        print(CODEHOOK_WELCOME_MESSAGE)


@app.command()
def reconfigure():
    """
    Reonfigure your local environment to connect to your AWS account
    """
    print(CODEHOOK_WELCOME_MESSAGE)


@app.command()
def deploy(file: Annotated[Path, typer.Option(
    exists=True,
    file_okay=True,
    dir_okay=False,
    writable=False,
    readable=True,
    resolve_path=True,
)],
    name: str = None,
    source: Annotated[
        Source, typer.Option(case_sensitive=False)
] = Source.stripe,
    enabled_events: Annotated[
        Events, typer.Option(case_sensitive=False)
] = Events.all
):
    """
    This is the main command for codehook. Deploy takes a function and deploys it as a webhook handler, 
    taking care of all the boilerplate and infrastructure for you. Depending on the source, the function can be using 
    different skeletons.

    Deploys the handler in FILE as a webhook handler for SOURCE, optionally with a custom --name. 
    If no custom name is given, the handler will inherit the file name
    """

    api_wrapper, lambda_wrapper = init_aws()

    if not name:
        name = os.path.splitext(os.path.basename(file))[0]

    print(
        f"Creating a [blue]{source.value}[/blue] endpoint that listens to [blue]{enabled_events.value}[/blue] events...")
    print(f"Deploying [blue]{file}[/blue] as [blue]{name}[/blue] :rocket:")

    rest_deployer = Deployer(file, name, api_wrapper, lambda_wrapper)
    lambda_function_name, api_id = rest_deployer.deploy()

    print("[bold green]Deployment complete[/bold green] :rocket:")
    print(f"Function name: [blue]{lambda_function_name}[/blue]")
    print(f"API ID: [blue]{api_id}[/blue]")


@app.command()
def list():
    """
    List all the endpoints currently deployed by Codehook
    """
    api_wrapper, lambda_wrapper = init_aws()

    print(f"Listing all codehook endpoints...")
    endpoints = api_wrapper.get_rest_apis()

    if endpoints:
        print(endpoints)
    else:
        print(f"[bold red]No codehook endpoints[/bold red]")

    print(f"Listing all lambda functions...")
    lambdas = lambda_wrapper.list_functions()
    if lambdas:
        print(lambdas)
    else:
        print(f"[bold red]No lambda functions[/bold red]")


@app.command()
def delete(
    lambda_function_name: Annotated[str, typer.Option(
        help="Name of the Lambda function to delete")] = None,
    api_id: Annotated[str, typer.Option(
        help="Name of the Rest API to delete")] = None,
    delete_all: Annotated[bool, typer.Option("--all")] = False
):
    """
    Delete the REST API, AWS Lambda function, and security role
    """
    api_wrapper, lambda_wrapper = init_aws()

    if delete_all:
        print("[bold red]Deleting all functions and endpoints[/bold red]")
        print(f"Listing all codehook endpoints...")
        endpoints = api_wrapper.get_rest_apis()

        if endpoints:
            for endpoint in endpoints:
                api_id = endpoint['id']
                api_wrapper.delete_rest_api(api_id)
                print(
                    f"[bold red]Deleting [/bold red][blue]{api_id}[/blue]"
                )
        else:
            print(f"[bold red]No codehook endpoints[/bold red]")

        print(f"Listing all lambda functions...")
        lambdas = lambda_wrapper.list_functions()
        if lambdas:
            for function in lambdas:
                lambda_function_name = function['FunctionName']
                lambda_wrapper.delete_function(lambda_function_name)
                print(
                    f"[bold red]Deleting [/bold red][blue]{lambda_function_name}[/blue][bold red]"
                )
        else:
            print(f"[bold red]No lambda functions[/bold red]")
    else:
        print(
            f"[bold red]Deleting [/bold red][blue]{lambda_function_name}[/blue][bold red] and [/bold red][blue]{api_id}[/blue]"
        )

        lambda_wrapper.delete_function(lambda_function_name)
        api_wrapper.delete_rest_api(api_id)

    print(f"[bold red]Deletion complete[/bold red]")


if __name__ == "__main__":
    app()
