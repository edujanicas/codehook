import typer
import logging

from rich import print
from dotenv import load_dotenv
from .RestDeployer import RestDeployer


logger = logging.getLogger(__name__)
load_dotenv()
app = typer.Typer()


@app.callback()
def callback():
    """
    Callback function
    """

@app.command()
def deploy(basic_file, lambda_name, api_name):
   rest_deployer = RestDeployer(basic_file, lambda_name, api_name)
   rest_deployer.deploy()
