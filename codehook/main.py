import os.path
from pathlib import Path

import boto3
import typer
from dotenv import load_dotenv
from rich import print
from typing_extensions import Annotated

from .aws_apigateway import APIGateway
from .aws_lambda import Lambda
from .deployer import Deployer
from .helpers import Events, Source
from .stripe import Stripe

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


def init() -> tuple[APIGateway, Lambda, Stripe]:
    iam_resource = boto3.resource("iam")
    lambda_client = boto3.client("lambda")
    apigateway_client = boto3.client("apigateway")
    api_wrapper = APIGateway(apigateway_client)
    lambda_wrapper = Lambda(lambda_client, iam_resource)
    stripe_wrapper = Stripe()

    return api_wrapper, lambda_wrapper, stripe_wrapper


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
    name: str = None,
    source: Annotated[Source, typer.Option(case_sensitive=False)] = Source.stripe,
    enabled_events: Annotated[list[Events], typer.Option(case_sensitive=False)] = list(
        Events.all
    ),
):
    """
    This is the main command for codehook. Deploy takes a function and deploys it as a webhook handler,
    taking care of all the boilerplate and infrastructure for you. Depending on the source, the function can be using
    different skeletons.

    Deploys the handler in FILE as a webhook handler for SOURCE, optionally with a custom --name.
    If no custom name is given, the handler will inherit the file name
    """

    api_wrapper, lambda_wrapper, stripe_wrapper = init()

    if not name:
        name = os.path.splitext(os.path.basename(file))[0]

    print(
        f"Creating a [blue]{source.value}[/blue] endpoint that listens to [blue]{enabled_events}[/blue] events..."
    )
    print(f"Deploying [blue]{file}[/blue] as [blue]{name}[/blue] :rocket:")

    events = [event.value for event in enabled_events]
    rest_deployer = Deployer(
        file, name, api_wrapper, lambda_wrapper, stripe_wrapper, events
    )
    lambda_function_name, api_id, webhook_url, webhook_id = rest_deployer.deploy()

    print("[bold green]Deployment complete[/bold green] :rocket:")
    print(f"Function name: [blue]{lambda_function_name}[/blue]")
    print(f"API ID: [blue]{api_id}[/blue]")
    print(f"Webhook URL: [blue]{webhook_url}[/blue]")
    print(f"Webhook ID: [blue]{webhook_id}[/blue]")


@app.command()
def list():
    """
    List all the endpoints currently deployed by Codehook
    """
    api_wrapper, lambda_wrapper, stripe_wrapper = init()

    print("Listing all codehook endpoints...")
    endpoints = api_wrapper.get_rest_apis()

    if endpoints:
        print(endpoints)
    else:
        print("[bold red]No codehook endpoints[/bold red]")

    print("Listing all lambda functions...")
    lambdas = lambda_wrapper.list_functions()
    if lambdas:
        print(lambdas)
    else:
        print("[bold red]No lambda functions[/bold red]")

    print("Listing all webhook endpoints...")
    webhooks = stripe_wrapper.list_endpoints()
    if webhooks:
        print(webhooks)
    else:
        print("[bold red]No webhook endpoints[/bold red]")


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
    api_wrapper, lambda_wrapper, stripe_wrapper = init()

    if delete_all:
        print("[bold red]Deleting all functions and endpoints[/bold red]")
        print("Listing all codehook endpoints...")
        endpoints = api_wrapper.get_rest_apis()

        if endpoints:
            for endpoint in endpoints:
                api_id = endpoint["id"]
                api_wrapper.delete_rest_api(api_id)
                print(f"[bold red]Deleting [/bold red][blue]{api_id}[/blue]")
        else:
            print("[bold red]No codehook endpoints[/bold red]")

        print("Listing all lambda functions...")
        lambdas = lambda_wrapper.list_functions()
        if lambdas:
            for function in lambdas:
                lambda_function_name = function["FunctionName"]
                lambda_wrapper.delete_function(lambda_function_name)
                print(
                    f"[bold red]Deleting [/bold red][blue]{lambda_function_name}[/blue][bold red]"
                )
        else:
            print("[bold red]No lambda functions[/bold red]")

        print("Listing all webhook endpoints...")
        webhooks = stripe_wrapper.list_endpoints()
        if webhooks:
            for webhook in webhooks:
                webhook_id = webhook["id"]
                stripe_wrapper.delete_endpoint(webhook_id)
                print(
                    f"[bold red]Deleting [/bold red][blue]{webhook_id}[/blue][bold red]"
                )
        else:
            print("[bold red]No webhook endpoints[/bold red]")
    else:
        print(
            f"[bold red]Deleting [/bold red][blue]{lambda_function_name}[/blue][bold red], [/bold red][blue]{api_id}[/blue] and [/bold red][blue]{webhook_id}[/blue]"
        )

        lambda_wrapper.delete_function(lambda_function_name)
        api_wrapper.delete_rest_api(api_id)
        stripe_wrapper.delete_endpoint(webhook_id)

    print("[bold red]Deletion complete[/bold red]")


if __name__ == "__main__":
    app()
