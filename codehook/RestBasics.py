"""
Purpose

Shows how to use the AWS SDK for Python (Boto3) to use Amazon API Gateway to
create a REST API backed by a Lambda function.

Instead of using the low-level Boto3 client APIs shown in this example, you can use
AWS Chalice to more easily create a REST API.

    For a working code example, see the `lambda/chalice_examples/lambda_rest` example
    in this GitHub repo.

    For more information about AWS Chalice, see https://github.com/aws/chalice.
"""
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class RestWrapper:
    def __init__(self, apigateway_client):
        self.apigateway_client = apigateway_client

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
            response = self.apigateway_client.create_rest_api(name=api_name)
            api_id = response["id"]
            logger.info("Create REST API %s with ID %s.", api_name, api_id)
        except ClientError:
            logger.exception("Couldn't create REST API %s.", api_name)
            raise

        try:
            response = self.apigateway_client.get_resources(restApiId=api_id)
            root_id = next(
                item["id"] for item in response["items"] if item["path"] == "/"
            )
            logger.info("Found root resource of the REST API with ID %s.", root_id)
        except ClientError:
            logger.exception(
                "Couldn't get the ID of the root resource of the REST API."
            )
            raise

        try:
            response = self.apigateway_client.create_resource(
                restApiId=api_id, parentId=root_id, pathPart=api_base_path
            )
            base_id = response["id"]
            logger.info("Created base path %s with ID %s.", api_base_path, base_id)
        except ClientError:
            logger.exception("Couldn't create a base path for %s.", api_base_path)
            raise

        try:
            self.apigateway_client.put_method(
                restApiId=api_id,
                resourceId=base_id,
                httpMethod="ANY",
                authorizationType="NONE",
            )
            logger.info(
                "Created a method that accepts all HTTP verbs for the base " "resource."
            )
        except ClientError:
            logger.exception("Couldn't create a method for the base resource.")
            raise

        lambda_uri = (
            f"arn:aws:apigateway:{self.apigateway_client.meta.region_name}:"
            f"lambda:path/2015-03-31/functions/{lambda_function_arn}/invocations"
        )
        try:
            # NOTE: You must specify 'POST' for integrationHttpMethod or this will not work.
            self.apigateway_client.put_integration(
                restApiId=api_id,
                resourceId=base_id,
                httpMethod="ANY",
                type="AWS_PROXY",
                integrationHttpMethod="POST",
                uri=lambda_uri,
            )
            logger.info(
                "Set function %s as integration destination for the base resource.",
                lambda_function_arn,
            )
        except ClientError:
            logger.exception(
                "Couldn't set function %s as integration destination.",
                lambda_function_arn,
            )
            raise

        try:
            self.apigateway_client.create_deployment(
                restApiId=api_id, stageName=api_stage
            )
            logger.info("Deployed REST API %s.", api_id)
        except ClientError:
            logger.exception("Couldn't deploy REST API %s.", api_id)
            raise

        source_arn = (
            f"arn:aws:execute-api:{self.apigateway_client.meta.region_name}:"
            f"{account_id}:{api_id}/*/*/{api_base_path}"
        )
        try:
            lambda_client.add_permission(
                FunctionName=lambda_function_arn,
                StatementId=f"demo-invoke",
                Action="lambda:InvokeFunction",
                Principal="apigateway.amazonaws.com",
                SourceArn=source_arn,
            )
            logger.info(
                "Granted permission to let Amazon API Gateway invoke function %s "
                "from %s.",
                lambda_function_arn,
                source_arn,
            )
        except ClientError:
            logger.exception(
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
        logger.info("Constructed REST API base URL: %s.", api_url)
        return api_url

    def delete_rest_api(self, api_id):
        """
        Deletes a REST API and all of its resources from Amazon API Gateway.

        :param apigateway_client: The Boto3 Amazon API Gateway client.
        :param api_id: The ID of the REST API.
        """
        try:
            self.apigateway_client.delete_rest_api(restApiId=api_id)
            logger.info("Deleted REST API %s.", api_id)
        except ClientError:
            logger.exception("Couldn't delete REST API %s.", api_id)
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
                rest_apis.extend(page['items'])
            return rest_apis
        
        except ClientError:
            logger.exception("Couldn't list REST APIs.")
            raise