import os
import time

import boto3
import pytest

from codehook.aws import AWS, APIGateway, Lambda


@pytest.fixture(scope="module")
def my_aws():
    return AWS()


@pytest.fixture(scope="module")
def my_lambda():
    return Lambda(boto3.client("lambda"), boto3.resource("iam"))


@pytest.fixture(scope="module")
def my_api():
    return APIGateway(boto3.client("apigateway"))


@pytest.fixture(scope="module")
def my_account_id():
    return boto3.client("sts").get_caller_identity()["Account"]


class TestLambda:
    def test_list_functions(self, my_lambda):
        result = my_lambda.list_functions()
        assert result == []

    def test_get_iam_role(self, my_lambda):
        result = my_lambda.get_iam_role("CODEHOOK_LAMBDA_ROLE")
        assert result.name == "CODEHOOK_LAMBDA_ROLE"

    def test_no_iam_role(self, my_lambda):
        result = my_lambda.get_iam_role("NON_EXISTENT_ROLE")
        assert result is None

    def test_create_existing_iam_role(self, my_lambda):
        result, value = my_lambda.create_iam_role_for_lambda("CODEHOOK_LAMBDA_ROLE")
        assert value is False
        assert result.name == "CODEHOOK_LAMBDA_ROLE"

    def test_create_new_iam_role(self, my_lambda):
        result, value = my_lambda.create_iam_role_for_lambda("NEW_ROLE")
        assert value is True
        assert result.name == "NEW_ROLE"
        my_lambda.delete_iam_lambda_role("NEW_ROLE")

    def test_delete_new_iam_role(self, my_lambda):
        my_lambda.create_iam_role_for_lambda("NEW_ROLE")
        result = my_lambda.delete_iam_lambda_role("NEW_ROLE")
        assert result is True

    def test_create_deployment_package(self, my_lambda):
        result = my_lambda.create_deployment_package("./codehook/skeletons/stripe")
        assert result is not None

    def test_create_function(self, my_lambda):
        name = "test_function"
        role, _ = my_lambda.create_iam_role_for_lambda("CODEHOOK_LAMBDA_ROLE")
        package = my_lambda.create_deployment_package("./codehook/skeletons/stripe")
        layers = [os.getenv("STRIPE_LAYER")]
        env_vars = {"Variables": {"API_KEY": os.getenv("STRIPE_API_KEY")}}

        result = my_lambda.create_function(
            name,
            name,
            role,
            package,
            layers,
            env_vars,
        )
        assert "arn:aws:lambda" in result

        lambdas = my_lambda.list_functions()
        lambda_names = [lambda_function["FunctionName"] for lambda_function in lambdas]
        assert name in lambda_names

        my_lambda.delete_function(result)

    def test_delete_function(self, my_lambda):
        name = "test_function"
        role, _ = my_lambda.create_iam_role_for_lambda("CODEHOOK_LAMBDA_ROLE")
        package = my_lambda.create_deployment_package("./codehook/skeletons/stripe")
        layers = [os.getenv("STRIPE_LAYER")]
        env_vars = {"Variables": {"API_KEY": os.getenv("STRIPE_API_KEY")}}
        result = my_lambda.create_function(
            name,
            name,
            role,
            package,
            layers,
            env_vars,
        )

        my_lambda.delete_function(result)
        lambdas = my_lambda.list_functions()
        lambda_names = [lambda_function["FunctionName"] for lambda_function in lambdas]

        assert name not in lambda_names


class TestAPI:
    def test_list_apis(self, my_api):
        result = my_api.get_rest_apis()
        assert result == []

    def test_create_api(self, my_api, my_lambda, my_account_id):
        name = "test_function"
        role, _ = my_lambda.create_iam_role_for_lambda("CODEHOOK_LAMBDA_ROLE")
        package = my_lambda.create_deployment_package("./codehook/skeletons/stripe")
        layers = [os.getenv("STRIPE_LAYER")]
        env_vars = {"Variables": {"API_KEY": os.getenv("STRIPE_API_KEY")}}
        function_id = my_lambda.create_function(
            name,
            name,
            role,
            package,
            layers,
            env_vars,
        )

        result = my_api.create_rest_api(
            "test_api",
            "codehook",
            "prod",
            my_account_id,
            my_lambda.lambda_client,
            function_id,
        )
        assert result is not None
        endpoints = my_api.get_rest_apis()
        endpoint_ids = [endpoint["id"] for endpoint in endpoints]
        assert result in endpoint_ids

        my_api.delete_rest_api(result)
        time.sleep(30)  # AWS only supports 1 request every 30 seconds per account
        my_lambda.delete_function(function_id)

    def test_delete_api(self, my_api, my_lambda, my_account_id):
        name = "test_function"
        role, _ = my_lambda.create_iam_role_for_lambda("CODEHOOK_LAMBDA_ROLE")
        package = my_lambda.create_deployment_package("./codehook/skeletons/stripe")
        layers = [os.getenv("STRIPE_LAYER")]
        env_vars = {"Variables": {"API_KEY": os.getenv("STRIPE_API_KEY")}}
        function_id = my_lambda.create_function(
            name,
            name,
            role,
            package,
            layers,
            env_vars,
        )
        result = my_api.create_rest_api(
            "test_api",
            "codehook",
            "prod",
            my_account_id,
            my_lambda.lambda_client,
            function_id,
        )

        my_api.delete_rest_api(result)
        time.sleep(30)  # AWS only supports 1 request every 30 seconds per account
        my_lambda.delete_function(function_id)
        endpoints = my_api.get_rest_apis()
        endpoint_ids = [endpoint["id"] for endpoint in endpoints]
        assert result not in endpoint_ids

    def test_construct_api_url(self, my_api, my_lambda, my_account_id):
        name = "test_function"
        role, _ = my_lambda.create_iam_role_for_lambda("CODEHOOK_LAMBDA_ROLE")
        package = my_lambda.create_deployment_package("./codehook/skeletons/stripe")
        layers = [os.getenv("STRIPE_LAYER")]
        env_vars = {"Variables": {"API_KEY": os.getenv("STRIPE_API_KEY")}}
        function_id = my_lambda.create_function(
            name,
            name,
            role,
            package,
            layers,
            env_vars,
        )

        api_id = my_api.create_rest_api(
            "test_api",
            "codehook",
            "prod",
            my_account_id,
            my_lambda.lambda_client,
            function_id,
        )

        url = my_api.construct_api_url(api_id, "prod", "codehook")

        endpoints = my_api.get_rest_apis()
        endpoint_ids = [endpoint["id"] for endpoint in endpoints]
        assert api_id in endpoint_ids
        assert api_id in url
        assert "codehook" in url
        assert "prod" in url

        my_api.delete_rest_api(api_id)
        time.sleep(30)  # AWS only supports 1 request every 30 seconds per account
        my_lambda.delete_function(function_id)


class TestAWS:
    def test_create_function(self, my_aws):
        function_arn = my_aws.create_function(
            "test_function", "./codehook/skeletons/stripe"
        )
        result = my_aws.list_functions()
        assert "test_function" in result
        assert "arn:aws:lambda" in function_arn
        my_aws.delete_function(function_arn)

    def test_delete_function(self, my_aws):
        function_arn = my_aws.create_function(
            "test_function", "./codehook/skeletons/stripe"
        )
        my_aws.delete_function(function_arn)
        result = my_aws.list_functions()
        assert "test_function" not in result

    def test_create_api(self, my_aws):
        function_arn = my_aws.create_function(
            "test_function", "./codehook/skeletons/stripe"
        )
        api_id, api_url = my_aws.create_api("test_api", function_arn)
        result = my_aws.list_apis()
        assert api_id in api_url
        assert api_id in result
        my_aws.delete_api(api_id)
        my_aws.delete_function(function_arn)
        time.sleep(30)  # AWS only supports 1 request every 30 seconds per account

    def test_delete_api(self, my_aws):
        function_arn = my_aws.create_function(
            "test_function", "./codehook/skeletons/stripe"
        )
        api_id, _ = my_aws.create_api("test_api", function_arn)
        my_aws.delete_api(api_id)
        my_aws.delete_function(function_arn)

        result = my_aws.list_apis()
        assert api_id not in result

        time.sleep(30)  # AWS only supports 1 request every 30 seconds per account
