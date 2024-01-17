import pytest

from codehook.aws import AWS, APIGateway, Lambda


@pytest.fixture(scope="module")
def my_aws():
    return AWS()


@pytest.fixture
def my_lambda(my_aws):
    return Lambda(my_aws.lambda_client, my_aws.iam_resource)


@pytest.fixture
def my_api(my_aws):
    return APIGateway(my_aws.apigateway_client)


def test_list_functions(my_lambda):
    result = my_lambda.list_functions()
    assert result == []


def test_list_apis(my_api):
    result = my_api.get_rest_apis()
    assert result == []
