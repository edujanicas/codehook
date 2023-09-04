import typer
import boto3
import json
import logging

from rich import print
from rich.prompt import Prompt
from .LambdaBasics import LambdaWrapper
from .retries import wait

logger = logging.getLogger(__name__)

class LambdaDeployer:
    def __init__(self, basic_file, lambda_name):
        self.basic_file = basic_file
        self.lambda_name = lambda_name

    def deploy(self):
        """
        Deploy a lambda function from a .py file, run it, and delete it.
        """
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

        lambda_client = boto3.client("lambda")
        iam_resource = boto3.resource("iam")
        wrapper = LambdaWrapper(lambda_client, iam_resource)

        print("Checking for IAM role for Lambda...")
        iam_role, should_wait = wrapper.create_iam_role_for_lambda(self.lambda_name)
        if should_wait:
            logger.info("Giving AWS time to create resources...")
            wait(10)

        print(f"Looking for function {self.lambda_name}...")
        function = wrapper.get_function(self.lambda_name)
        if function is None:
            print("Zipping the Python script into a deployment package...")
            deployment_package = wrapper.create_deployment_package(
                self.basic_file, f"{self.lambda_name}.py"
            )
            print(f"...and creating the {self.lambda_name} Lambda function.")
            wrapper.create_function(
                self.lambda_name, f"{self.lambda_name}.lambda_handler", iam_role, deployment_package
            )
        else:
            print(f"Function {self.lambda_name} already exists.")
        print("-" * 88)

        print(f"Let's invoke {self.lambda_name}. This function increments a number.")
        action_params = {
            "action": "increment",
            "number": int(Prompt.ask("Give me a number to increment: ")),
        }
        print(f"Invoking {self.lambda_name}...")
        response = wrapper.invoke_function(self.lambda_name, action_params)
        print(
            f"Incrementing {action_params['number']} resulted in "
            f"{json.load(response['Payload'])}"
        )
        if typer.confirm("Do you want to list all of the functions in your account?"):
            wrapper.list_functions()
        print('-'*88)

        if typer.confirm("Ready to delete the function and role?"):
            for policy in iam_role.attached_policies.all():
                policy.detach_role(RoleName=iam_role.name)
            iam_role.delete()
            print(f"Deleted role {self.lambda_name}.")
            wrapper.delete_function(self.lambda_name)
            print(f"Deleted function {self.lambda_name}.")

        print("\nThanks for using codehook!")
        print("-" * 88)