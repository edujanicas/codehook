import boto3
import pytest

from codehook.aws import AWS, APIGateway, Lambda


@pytest.fixture(scope="module")
def my_aws():
    return AWS()


@pytest.fixture(scope="module")
def my_lambda(my_aws):
    return Lambda(boto3.client("lambda"), boto3.resource("iam"))


@pytest.fixture(scope="module")
def my_api(my_aws):
    return APIGateway(boto3.client("apigateway"))


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


class TestAPI:
    def test_list_apis(self, my_api):
        result = my_api.get_rest_apis()
        assert result == []
