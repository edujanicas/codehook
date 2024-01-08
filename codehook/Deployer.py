from rich import print

import boto3
from rich.progress import Progress
import time
import tempfile
import shutil

IAM_ROLE_NAME = "CODEHOOK_LAMBDA_ROLE"
STRIPE_LAYER = "arn:aws:lambda:us-east-1:764755761259:layer:stripe_layer:4"


class Deployer:
    def __init__(self, basic_file, name, rest_wrapper, lambda_wrapper):
        self.basic_file = basic_file
        self.lambda_name = name
        self.api_name = name
        self.rest_wrapper = rest_wrapper
        self.lambda_wrapper = lambda_wrapper

    def deploy(self):
        """
        Deploy an AWS Lambda function and create a REST API
        """
        with Progress(
            transient=True,
        ) as progress:
            task = progress.add_task("[blue]Creating codehook files...", total=200)
            with tempfile.TemporaryDirectory() as tmpdirname:
                print("Created temporary directory", tmpdirname)
                progress.update(task, advance=100)

                shutil.copytree("codehook/skeletons/stripe", tmpdirname, dirs_exist_ok=True)
                print("Copied skeleton files to temporary directory", tmpdirname)
                progress.update(task, advance=100)

                task = progress.add_task(
                    "[blue]Deploying codehook endpoint...", total=1000
                )
                print("Launching the AWS Deployer :rocket:")

                lambda_path = tmpdirname
                lambda_filename = "lambda_handler_rest"
                lambda_handler_name = lambda_filename + ".lambda_handler"
                lambda_role_name = IAM_ROLE_NAME
                lambda_function_name = self.lambda_name
                api_name = self.api_name
                layers = [STRIPE_LAYER]
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

                return (lambda_function_name, api_id)
