from rich import print
from dotenv import load_dotenv
from .RestBasics import RestWrapper
from .LambdaBasics import LambdaWrapper
from .retries import wait

import os.path
import calendar
import datetime
import json
import logging
import time
import boto3
import requests

logger = logging.getLogger(__name__)

class RestDeployer:
    def __init__(self, basic_file, name):
        self.basic_file = basic_file
        self.lambda_name = name
        self.api_name = name

    def deploy(self):
        """
        Shows how to deploy an AWS Lambda function, create a REST API, call the REST API
        in various ways, and remove all of the resources after the demo completes.
        """

        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
        print("-" * 88)
        print("Welcome to the AWS Lambda and Amazon API Gateway REST API creation demo.")
        print("-" * 88)

        lambda_filename = self.basic_file
        lambda_handler_name = os.path.splitext(os.path.basename(lambda_filename))[0]+ ".lambda_handler"
        lambda_role_name = self.lambda_name
        lambda_function_name = self.lambda_name
        api_name = self.api_name

        iam_resource = boto3.resource("iam")
        lambda_client = boto3.client("lambda")
        apigateway_client = boto3.client("apigateway")
        
        lambda_wrapper = LambdaWrapper(lambda_client, iam_resource)
        rest_wrapper = RestWrapper(apigateway_client)

        print("Checking for IAM role for Lambda...")
        iam_role, should_wait = lambda_wrapper.create_iam_role_for_lambda(lambda_role_name)
        if should_wait:
            logger.info("Giving AWS time to create resources...")
            wait(10)

        print(
            f"Creating AWS Lambda function {lambda_function_name} from "
            f"{lambda_handler_name}..."
        )
        # destination file without the full path
        deployment_package = lambda_wrapper.create_deployment_package(
            lambda_filename, os.path.basename(lambda_filename)
        )
        lambda_function_arn = lambda_wrapper.create_function(
            lambda_function_name, lambda_handler_name, iam_role, deployment_package
        )

        print(f"Creating Amazon API Gateway REST API {api_name}...")
        account_id = boto3.client("sts").get_caller_identity()["Account"]
        api_base_path = "demoapi"
        api_stage = "test"
        api_id = rest_wrapper.create_rest_api(
            api_name,
            api_base_path,
            api_stage,
            account_id,
            lambda_client,
            lambda_function_arn,
        )
        api_url = rest_wrapper.construct_api_url(
            api_id, api_stage, api_base_path
        )
        print(f"REST API created, URL is :\n\t{api_url}")
        print(f"Sleeping for a couple seconds to give AWS time to prepare...")
        time.sleep(2)

        print(f"Sending some requests to {api_url}...")
        https_response = requests.get(api_url)
        print(
            f"REST API returned status {https_response.status_code}\n"
            f"Message: {json.loads(https_response.text)['message']}"
        )

        https_response = requests.get(
            api_url,
            params={"name": "Martha"},
            headers={"day": calendar.day_name[datetime.date.today().weekday()]},
        )
        print(
            f"REST API returned status {https_response.status_code}\n"
            f"Message: {json.loads(https_response.text)['message']}"
        )

        https_response = requests.post(
            api_url,
            params={"name": "Martha"},
            headers={"day": calendar.day_name[datetime.date.today().weekday()]},
            json={"adjective": "fabulous"},
        )
        print(
            f"REST API returned status {https_response.status_code}\n"
            f"Message: {json.loads(https_response.text)['message']}"
        )

        https_response = requests.delete(api_url, params={"name": "Martha"})
        print(
            f"REST API returned status {https_response.status_code}\n"
            f"Message: {json.loads(https_response.text)['message']}"
        )
        return (lambda_function_name, api_id)