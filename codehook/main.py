import typer
import logging

from rich import print
from rich.prompt import Prompt
from dotenv import load_dotenv
from .lambda_deployer import LambdaDeployer

logger = logging.getLogger(__name__)
load_dotenv()
app = typer.Typer()


@app.callback()
def callback():
    """
    Callback function
    """


@app.command()
def deploy(basic_file, lambda_name):
    """
    Deploys a simple lambda function.

    :param basic_file: The name of the file that contains the basic Lambda handler.
    :param lambda_name: The name to give resources created for the scenario, such as the
                        IAM role and the Lambda function.
    """

    deployer = LambdaDeployer(basic_file, lambda_name)
    deployer.deploy()

    print("Function deployed (and deleted)")

    
