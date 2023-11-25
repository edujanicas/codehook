import typer
import boto3

import os.path
from rich import print
from dotenv import load_dotenv
from .RestDeployer import RestDeployer
from .RestBasics import RestWrapper
from .LambdaBasics import LambdaWrapper

load_dotenv()
app = typer.Typer()

CODEHOOK_WELCOME_MESSAGE = """
</> Welcome to codehook! </>
Codehook relies on having your AWS account running on the background. So, before using Codehook, you need to set up authentication credentials for your AWS account using either the [blue link=https://console.aws.amazon.com/iam/home]IAM Console[/blue link] or the AWS CLI. 

For instructions about how to create a user using the IAM Console, see [blue link=https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html#id_users_create_console]Creating IAM users[/blue link]. 
Once the user has been created, see [blue link=https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html#Using_CreateAccessKey]Managing access keys[/blue link] to learn how to create and retrieve the keys used to authenticate the user.

If you have the [blue link=http://aws.amazon.com/cli/]AWS CLI[/blue link] installed, then you can use the [bold]aws configure[/bold] command to configure your credentials file:
"""


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
    if os.environ["AWS_ACCESS_KEY_ID"]:
        print(
            """
</> Welcome to codehook! </>

Your AWS account is already configured. Run [bold]codehook reconfigure[/bold] for instructions on setting up a new AWS account.
    [green]Access Key ID:[/green] {access_key_id}
    [green]Default Region:[/green] {default_region}
            """.format(
                access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
                default_region=os.environ["AWS_DEFAULT_REGION"],
            )
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
def deploy(file: str, name: str = ""):
    """
    Deploy the function in FILE, optionally with a custom --name
    """

    if not name:
        name = os.path.splitext(os.path.basename(file))[0]

    print(f"Deploying [blue]{file}[/blue] as [blue]{name}[/blue] :rocket:")

    rest_deployer = RestDeployer(file, name)
    lambda_function_name, api_id = rest_deployer.deploy()

    print("[bold green]Deployment complete[/bold green] :rocket:")
    print(f"Function name: [blue]{lambda_function_name}[/blue]")
    print(f"API ID: [blue]{api_id}[/blue]")


@app.command()
def list():
    """
    List all the endpoints currently deployed by Codehook
    """
    iam_resource = boto3.resource("iam")
    lambda_client = boto3.client("lambda")
    apigateway_client = boto3.client("apigateway")
    rest_wrapper = RestWrapper(apigateway_client)
    lambda_wrapper = LambdaWrapper(lambda_client, iam_resource)

    print(f"Listing all codehook endpoints...")
    endpoints = rest_wrapper.get_rest_apis()

    if endpoints:
        print(endpoints)
    else:
        print("[bold red]No codehook endpoints[/bold red]")

    print(f"Listing all lambda functions...")
    lambdas = lambda_wrapper.list_functions()
    if lambdas:
        print(lambdas)
    else:
        print("[bold red]No lambda functions[/bold red]")


@app.command()
def delete(lambda_function_name: str, api_id: str):
    """
    Delete the REST API, AWS Lambda function, and security role
    """

    iam_resource = boto3.resource("iam")
    lambda_client = boto3.client("lambda")
    apigateway_client = boto3.client("apigateway")

    print(
        f"[bold red]Deleting [/bold red][blue]{lambda_function_name}[/blue][bold red] and [/bold red][blue]{api_id}[/blue]"
    )

    lambda_wrapper = LambdaWrapper(lambda_client, iam_resource)
    rest_wrapper = RestWrapper(apigateway_client)

    lambda_wrapper.delete_function(lambda_function_name)
    rest_wrapper.delete_rest_api(api_id)

    print("[bold red]Deletion complete[/bold red]")


if __name__ == "__main__":
    app()
