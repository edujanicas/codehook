import configparser
import shutil
import tempfile
import time

import boto3
from rich import print
from rich.progress import Progress

config = configparser.ConfigParser()
config.read("config.cfg")

IAM_ROLE_NAME = config["default"]["iam_role_name"]
STRIPE_LAYER = config["default"]["stripe_layer"]
STRIPE_API_KEY = config["default"]["stripe_api_key"]

class Deployer:
    def __init__(
        self, file, name, rest_wrapper, lambda_wrapper, stripe_wrapper, enabled_events
    ):
        self.file = file
        self.lambda_name = name
        self.api_name = name
        self.rest_wrapper = rest_wrapper
        self.lambda_wrapper = lambda_wrapper
        self.stripe_wrapper = stripe_wrapper
        self.enabled_events = enabled_events

    def deploy(self):
        """
        Deploy an AWS Lambda function and create a REST API
        """
        with (
            Progress(transient=True) as progress,
            tempfile.TemporaryDirectory() as tmpdirname,
        ):
            task = progress.add_task("[blue]Creating codehook files...", total=300)
            print("Created temporary directory", tmpdirname)
            progress.update(task, advance=100)

            shutil.copytree("codehook/skeletons/stripe", tmpdirname, dirs_exist_ok=True)
            print("Copied skeleton files to temporary directory", tmpdirname)
            progress.update(task, advance=100)

            shutil.copy(self.file, tmpdirname + "/handler.py")
            print("Copied custom handler to temporary directory", tmpdirname)
            progress.update(task, advance=100)

            task = progress.add_task("[blue]Deploying codehook endpoint...", total=1000)
            print("Launching the AWS Deployer :rocket:")

            lambda_path = tmpdirname
            lambda_filename = "lambda_handler_rest"
            lambda_handler_name = lambda_filename + ".lambda_handler"
            lambda_role_name = IAM_ROLE_NAME
            lambda_function_name = self.lambda_name
            api_name = self.api_name
            layers = [STRIPE_LAYER]
            environment = {"Variables": {"API_KEY": STRIPE_API_KEY}}
            progress.update(task, advance=100)

            print("Checking for IAM role for Lambda...")
            iam_role, should_wait = self.lambda_wrapper.create_iam_role_for_lambda(
                lambda_role_name
            )
            if should_wait:
                print("Giving AWS time to create resources...")
                time.sleep(5)
            progress.update(task, advance=200)

            print(
                f"Creating AWS Lambda function {lambda_function_name} from "
                f"{lambda_handler_name}..."
            )
            # destination file without the full path
            deployment_package = self.lambda_wrapper.create_deployment_package(
                lambda_path
            )
            progress.update(task, advance=100)
            lambda_function_arn = self.lambda_wrapper.create_function(
                lambda_function_name,
                lambda_handler_name,
                iam_role,
                deployment_package,
                layers,
                environment,
            )
            progress.update(task, advance=200)

            print(f"Creating Amazon API Gateway REST API {api_name}...")
            account_id = boto3.client("sts").get_caller_identity()["Account"]
            api_base_path = "codehook"
            api_stage = "prod"
            api_id = self.rest_wrapper.create_rest_api(
                api_name,
                api_base_path,
                api_stage,
                account_id,
                self.lambda_wrapper.lambda_client,
                lambda_function_arn,
            )
            progress.update(task, advance=300)

            api_url = self.rest_wrapper.construct_api_url(
                api_id, api_stage, api_base_path
            )
            progress.update(task, advance=100)
            print(f"REST API created, URL is :\n\t{api_url}")

            task = progress.add_task(
                "[blue]Setting up endpoint in Stripe...", total=100
            )

            print("Configuring the webhook endpoint in Stripe")
            webhook_id = self.stripe_wrapper.create(self.enabled_events, api_url)
            progress.update(task, advance=100)
            print(f"Webhook endpoint {webhook_id} created")

            return (lambda_function_name, api_id, api_url, webhook_id)
