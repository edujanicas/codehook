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


@app.callback()
def callback():
    """
    Callback function
    """


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
    List the endpoints currently deployed
    """
    apigateway_client = boto3.client("apigateway")
    wrapper = RestWrapper(apigateway_client)

    print(f"Listing all codehook endpoints")
    endpoints = wrapper.get_rest_apis()

    if (endpoints):
        print(endpoints)
    else:
        print("[bold red]No codehook endpoints[/bold red]")

@app.command()
def delete(lambda_function_name: str, api_id: str):
    """
    Delete the REST API, AWS Lambda function, and security role
    """

    iam_resource = boto3.resource("iam")
    lambda_client = boto3.client("lambda")
    apigateway_client = boto3.client("apigateway")

    print(f"[bold red]Deleting [/bold red][blue]{lambda_function_name}[/blue][bold red] and [/bold red][blue]{api_id}[/blue]")
        
    lambda_wrapper = LambdaWrapper(lambda_client, iam_resource)
    rest_wrapper = RestWrapper(apigateway_client)
    
    lambda_wrapper.delete_function(lambda_function_name)
    rest_wrapper.delete_rest_api(api_id)

    print("[bold red]Deletion complete[/bold red]")