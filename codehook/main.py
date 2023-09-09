import typer
import boto3

import os.path
from rich import print
from dotenv import load_dotenv
from .RestDeployer import RestDeployer
from .RestBasics import RestWrapper

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
    rest_deployer.deploy()
    print("[bold green]Deployment complete[/bold green] :rocket:")

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
