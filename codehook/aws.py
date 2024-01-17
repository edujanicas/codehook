import io
import json
import os
import pathlib
import time
import zipfile
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from rich import print

from .model import Cloud


class Lambda:
    def __init__(self, lambda_client, iam_resource):
        self.tags = {"codehook": "true"}
        self.lambda_client = lambda_client
        self.iam_resource = iam_resource

    @staticmethod
    def create_deployment_package(source_path):
        """
        Creates a Lambda deployment package in .zip format in an in-memory buffer. This
        buffer can be passed directly to Lambda when creating the function.

        :param source_path: The path for the files that contains the Lambda handler
                            function.
        :return: The deployment package.
        """
        directory = pathlib.Path(source_path)

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as zipped:
            for source_file in directory.iterdir():
                zipped.write(source_file, arcname=source_file.name)
        buffer.seek(0)
        return buffer.read()

    def get_iam_role(self, iam_role_name):
        """
        Get an AWS Identity and Access Management (IAM) role.

        :param iam_role_name: The name of the role to retrieve.
        :return: The IAM role.
        """
        role = None
        try:
            temp_role = self.iam_resource.Role(iam_role_name)
            temp_role.load()
            role = temp_role
            print(f"Got IAM role {role.name}")
        except ClientError as err:
            if err.response["Error"]["Code"] == "NoSuchEntity":
                print(f"IAM role {iam_role_name} does not exist.")
            else:
                print(
                    "Couldn't get IAM role %s. Here's why: %s: %s",
                    iam_role_name,
                    err.response["Error"]["Code"],
                    err.response["Error"]["Message"],
                )
                raise
        return role

    def create_iam_role_for_lambda(self, iam_role_name):
        """
        Creates an IAM role that grants the Lambda function basic permissions. If a
        role with the specified name already exists, it is used instead.

        :param iam_role_name: The name of the role to create.
        :return: The role and a value that indicates whether the role is newly created.
        """
        role = self.get_iam_role(iam_role_name)
        if role is not None:
            return role, False

        lambda_assume_role_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "lambda.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                }
            ],
        }
        policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"

        try:
            role = self.iam_resource.create_role(
                RoleName=iam_role_name,
                AssumeRolePolicyDocument=json.dumps(lambda_assume_role_policy),
            )
            print(f"Created role {role.name}.")
            role.attach_policy(PolicyArn=policy_arn)
            print(f"Attached basic execution policy to role {role.name}")
        except ClientError as error:
            if error.response["Error"]["Code"] == "EntityAlreadyExists":
                role = self.iam_resource.Role(iam_role_name)
                print(f"The role {iam_role_name} already exists. Using it.")
            else:
                print(
                    "Couldn't create role %s or attach policy %s.",
                    iam_role_name,
                    policy_arn,
                )
                raise

        return role, True

    def create_function(
        self,
        function_name,
        handler_name,
        iam_role,
        deployment_package,
        layers,
        environment,
    ):
        """
        Deploys a Lambda function.

        :param function_name: The name of the Lambda function.
        :param handler_name: The fully qualified name of the handler function. This
                             must include the file name and the function name.
        :param iam_role: The IAM role to use for the function.
        :param deployment_package: The deployment package that contains the function
                                   code in .zip format.
        :return: The Amazon Resource Name (ARN) of the newly created function.
        """
        try:
            # Functions do not list its tags, so the description identifies it as a codehook function
            response = self.lambda_client.create_function(
                FunctionName=function_name,
                Description=str(self.tags),
                Runtime="python3.11",
                Role=iam_role.arn,
                Handler=handler_name,
                Code={"ZipFile": deployment_package},
                Publish=True,
                Tags=self.tags,
                Layers=layers,
                Environment=environment,
            )
            function_arn = response["FunctionArn"]
            waiter = self.lambda_client.get_waiter("function_active_v2")
            waiter.wait(FunctionName=function_name)
            print(
                f"Created function {function_name} with ARN: {response['FunctionArn']}."
            )
        except ClientError:
            print(f"Couldn't create function {function_name}.")
            raise
        else:
            return function_arn

    def delete_function(self, function_name):
        """
        Deletes a Lambda function.

        :param function_name: The name of the function to delete.
        """
        try:
            self.lambda_client.delete_function(FunctionName=function_name)
        except ClientError:
            print(f"Couldn't delete function {function_name}.")
            raise

    def update_function_code(self, function_name, deployment_package):
        """
        Updates the code for a Lambda function by submitting a .zip archive that contains
        the code for the function.

        :param function_name: The name of the function to update.
        :param deployment_package: The function code to update, packaged as bytes in
                                   .zip format.
        :return: Data about the update, including the status.
        """
        try:
            response = self.lambda_client.update_function_code(
                FunctionName=function_name, ZipFile=deployment_package
            )
        except ClientError as err:
            print(
                "Couldn't update function %s. Here's why: %s: %s",
                function_name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
        else:
            return response

    def update_function_configuration(self, function_name, env_vars):
        """
        Updates the environment variables for a Lambda function.

        :param function_name: The name of the function to update.
        :param env_vars: A dict of environment variables to update.
        :return: Data about the update, including the status.
        """
        try:
            response = self.lambda_client.update_function_configuration(
                FunctionName=function_name, Environment={"Variables": env_vars}
            )
        except ClientError as err:
            print.error(
                "Couldn't update function configuration %s. Here's why: %s: %s",
                function_name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
        else:
            return response

    def list_functions(self):
        """
        Lists the Lambda functions for the current account.

        :return: A list of all codehook functions on the account
        """
        try:
            functions = []
            paginator = self.lambda_client.get_paginator("list_functions")
            page_iterator = paginator.paginate()
            for page in page_iterator:
                for function in page["Functions"]:
                    # Functions do not list its tags, so the description identifies it as a codehook function
                    if function["Description"] == str(self.tags):
                        functions.append(function)
            return functions
        except ClientError:
            print("Couldn't list REST APIs.")
            raise


class APIGateway:
    def __init__(self, apigateway_client):
        self.tags = {"codehook": "true"}
        self.apigateway_client = apigateway_client
        self.tags = {"codehook": "true"}

    def create_rest_api(
        self,
        api_name,
        api_base_path,
        api_stage,
        account_id,
        lambda_client,
        lambda_function_arn,
    ):
        """
        Creates a REST API in Amazon API Gateway. The REST API is backed by the specified
        AWS Lambda function.

        The following is how the function puts the pieces together, in order:
        1. Creates a REST API in Amazon API Gateway.
        2. Creates a '/webhook' resource in the REST API.
        3. Creates a method that accepts all HTTP actions and passes them through to
        the specified AWS Lambda function.
        4. Deploys the REST API to Amazon API Gateway.
        5. Adds a resource policy to the AWS Lambda function that grants permission
        to let Amazon API Gateway call the AWS Lambda function.

        :param apigateway_client: The Boto3 Amazon API Gateway client object.
        :param api_name: The name of the REST API.
        :param api_base_path: The base path part of the REST API URL.
        :param api_stage: The deployment stage of the REST API.
        :param account_id: The ID of the owning AWS account.
        :param lambda_client: The Boto3 AWS Lambda client object.
        :param lambda_function_arn: The Amazon Resource Name (ARN) of the AWS Lambda
                                    function that is called by Amazon API Gateway to
                                    handle REST requests.
        :return: The ID of the REST API. This ID is required by most Amazon API Gateway
                methods.
        """
        try:
            response = self.apigateway_client.create_rest_api(
                name=api_name, tags=self.tags
            )
            api_id = response["id"]
            print(f"Create REST API {api_name} with ID {api_id}.")
        except ClientError:
            print(f"Couldn't create REST API {api_name}.")
            raise

        try:
            response = self.apigateway_client.get_resources(restApiId=api_id)
            root_id = next(
                item["id"] for item in response["items"] if item["path"] == "/"
            )
            print(f"Found root resource of the REST API with ID {root_id}.")
        except ClientError:
            print("Couldn't get the ID of the root resource of the REST API.")
            raise

        try:
            response = self.apigateway_client.create_resource(
                restApiId=api_id, parentId=root_id, pathPart=api_base_path
            )
            base_id = response["id"]
            print(f"Created base path {api_base_path} with ID {base_id}.")
        except ClientError:
            print(f"Couldn't create a base path for {api_base_path}.")
            raise

        try:
            self.apigateway_client.put_method(
                restApiId=api_id,
                resourceId=base_id,
                httpMethod="ANY",
                authorizationType="NONE",
            )
            print(
                "Created a method that accepts all HTTP verbs for the base " "resource."
            )
        except ClientError:
            print("Couldn't create a method for the base resource.")
            raise

        lambda_uri = (
            f"arn:aws:apigateway:{self.apigateway_client.meta.region_name}:"
            f"lambda:path/2015-03-31/functions/{lambda_function_arn}/invocations"
        )
        try:
            self.apigateway_client.put_integration(
                restApiId=api_id,
                resourceId=base_id,
                httpMethod="ANY",
                type="AWS_PROXY",
                integrationHttpMethod="POST",
                uri=lambda_uri,
            )
            print(
                "Set function %s as integration destination for the base resource.",
                lambda_function_arn,
            )
        except ClientError:
            print(
                "Couldn't set function %s as integration destination.",
                lambda_function_arn,
            )
            raise

        try:
            self.apigateway_client.create_deployment(
                restApiId=api_id, stageName=api_stage
            )
            print(f"Deployed REST API {api_id}.")
        except ClientError:
            print(f"Couldn't deploy REST API {api_id}.")
            raise

        source_arn = (
            f"arn:aws:execute-api:{self.apigateway_client.meta.region_name}:"
            f"{account_id}:{api_id}/*/*/{api_base_path}"
        )
        try:
            lambda_client.add_permission(
                FunctionName=lambda_function_arn,
                StatementId="demo-invoke",
                Action="lambda:InvokeFunction",
                Principal="apigateway.amazonaws.com",
                SourceArn=source_arn,
            )
            print(
                "Granted permission to let Amazon API Gateway invoke function %s "
                "from %s.",
                lambda_function_arn,
                source_arn,
            )
        except ClientError:
            print(
                "Couldn't add permission to let Amazon API Gateway invoke %s.",
                lambda_function_arn,
            )
            raise

        return api_id

    def construct_api_url(self, api_id, api_stage, api_base_path):
        """
        Constructs the URL of the REST API.

        :param api_id: The ID of the REST API.
        :param api_stage: The deployment stage of the REST API.
        :param api_base_path: The base path part of the REST API.
        :return: The full URL of the REST API.
        """
        region = self.apigateway_client.meta.region_name
        api_url = (
            f"https://{api_id}.execute-api.{region}.amazonaws.com/"
            f"{api_stage}/{api_base_path}"
        )
        print(f"Constructed REST API base URL: {api_url}.")
        return api_url

    def delete_rest_api(self, api_id):
        """
        Deletes a REST API and all of its resources from Amazon API Gateway.

        :param apigateway_client: The Boto3 Amazon API Gateway client.
        :param api_id: The ID of the REST API.
        """
        try:
            self.apigateway_client.delete_rest_api(restApiId=api_id)
            print(f"Deleted REST API {api_id}.")
        except ClientError:
            print(f"Couldn't delete REST API {api_id}.")
            raise

    def get_rest_apis(self):
        """
        Gets the ID of a REST API from its name by searching the list of REST APIs
        for the current account. Because names need not be unique, this returns only
        the first API with the specified name.

        :param api_name: The name of the API to look up.
        :return: A list with all rest apis
        """
        try:
            rest_apis = []
            paginator = self.apigateway_client.get_paginator("get_rest_apis")
            page_iterator = paginator.paginate()
            for page in page_iterator:
                rest_apis.extend(page["items"])
            return rest_apis

        except ClientError:
            print("Couldn't list REST APIs.")
            raise


class AWS(Cloud):
    def __init__(self):
        super().__init__()
        self.tags = {"codehook": "true"}

        load_dotenv()
        self.iam_role_name = os.getenv("IAM_ROLE_NAME")
        self.stripe_layer = os.getenv("STRIPE_LAYER")
        self.stripe_api_key = os.getenv("STRIPE_API_KEY")

        self.lambda_client = boto3.client("lambda")
        self.apigateway_client = boto3.client("apigateway")

        self.iam_resource = boto3.resource("iam")
        self.api_wrapper = APIGateway(self.apigateway_client)
        self.lambda_wrapper = Lambda(self.lambda_client, self.iam_resource)

    def create_function(self, name: str, path: str):
        # Step 2.1: Create IAM Role
        print("Checking for IAM role for Lambda")
        iam_role, should_wait = self.lambda_wrapper.create_iam_role_for_lambda(
            self.iam_role_name
        )
        if should_wait:
            print("Giving AWS time to create resources...")
            time.sleep(5)
        print(f"IAM role: {iam_role.name}")

        # Step 2.2: Create deployment package from the temporary directory
        print("Creating deployment package")
        deployment_package = self.lambda_wrapper.create_deployment_package(path)
        print("Deployment package ready to be deployed")

        # Step 2.3: Create lambda function from the deployment package
        # The lambda skeleton contains a file called lambda_handler_rest.py
        # which contains a function called lambda_handler. This is the
        # function that will be called when the lambda function is invoked.
        lambda_handler_name = "lambda_handler_rest.lambda_handler"
        env_vars = {"Variables": {"API_KEY": self.stripe_api_key}}
        print(f"Creating AWS Lambda function {name} from " f"{lambda_handler_name}")
        lambda_function_arn = self.lambda_wrapper.create_function(
            name,
            lambda_handler_name,
            iam_role,
            deployment_package,
            [self.stripe_layer],
            env_vars,
        )
        print(f"Lambda function created: {lambda_function_arn}")
        return lambda_function_arn

    def update_function(self, id: str, file: Path):
        pass

    def delete_function(self, id: str):
        self.lambda_wrapper.delete_function(id)

    def list_functions(self):
        lambdas = self.lambda_wrapper.list_functions()
        lambda_ids = [lambda_function["FunctionName"] for lambda_function in lambdas]
        if lambda_ids:
            print(lambda_ids)
        else:
            print("[bold red]No lambda functions[/bold red]")

        return lambda_ids

    def create_api(self, name: str, function_id: str):
        # Step 2.4: Create an API to front the lambda function
        print(f"Creating the {name} API for the lambda function")
        account_id = boto3.client("sts").get_caller_identity()["Account"]
        api_base_path = "codehook"
        api_stage = "prod"
        api_id = self.api_wrapper.create_rest_api(
            name,
            api_base_path,
            api_stage,
            account_id,
            self.lambda_wrapper.lambda_client,
            function_id,
        )
        print(f"API created with ID {api_id}")
        # Step 2.5: Assign the API a public URL
        print("Wrapping the API around a public URL")
        api_url = self.api_wrapper.construct_api_url(api_id, api_stage, api_base_path)
        print(f"REST API fully created, URL is :\n\t{api_url}")

        return api_id, api_url

    def delete_api(self, id: str):
        self.api_wrapper.delete_rest_api(id)

    def list_apis(self):
        endpoints = self.api_wrapper.get_rest_apis()
        endpoint_ids = [endpoint["id"] for endpoint in endpoints]
        if endpoint_ids:
            print(endpoint_ids)
        else:
            print("[bold red]No codehook endpoints[/bold red]")

        return endpoint_ids
