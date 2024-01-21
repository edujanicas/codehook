import json
import logging
import os

import handler
import stripe

stripe.api_key = os.getenv("API_KEY")
endpoint_secret = os.getenv("ENDPOINT_SECRET")

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, _):
    """
    Handles POST requests that are passed through an Amazon API Gateway REST API,
        with a JSON payload consisting of an event object.
    Quickly returns a successful status code (2xx) prior to any complex logic
        that could cause a timeout.
    For example, you it returns a 200 response before updating a customer’s
        invoice as paid in an accounting system.

    :param event: The event dict sent by Amazon API Gateway that contains all of the
                  request data.
    :param context: The context in which the function is called.
    :return: A response that is sent to Amazon API Gateway, to be wrapped into
             an HTTP response. The 'statusCode' field is the HTTP status code
             and the 'body' field is the body of the response.
    """
    logger.info("Request: %s", event)
    response_code = 200

    headers = event.get("headers")
    body = event.get("body")

    event = None

    if body:
        payload = body
    else:
        payload = "{}"

    try:
        event = json.loads(payload)
    except json.decoder.JSONDecodeError as e:
        print("Invalid webhook request: " + str(e))
        response_code = 400
        return {
            "statusCode": response_code,
            "headers": {"Content-Type": "*/*"},
            "body": json.dumps(
                {
                    "status_code": response_code,
                    "body": str(e),
                }
            ),
        }
    if endpoint_secret:
        # Only verify the event if there is an endpoint secret defined
        # Otherwise use the basic event deserialized with json
        sig_header = headers.get("stripe-signature")
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)  # type: ignore
        except stripe.error.SignatureVerificationError as e:  # type: ignore
            print("⚠️  Webhook signature verification failed." + str(e))
            response_code = 400
            return {
                "statusCode": response_code,
                "headers": {"Content-Type": "*/*"},
                "body": json.dumps(
                    {
                        "status_code": response_code,
                        "body": str(e),
                    }
                ),
            }
        pass

    # Inject code here
    (response_code, response_body) = handler.handler_logic(event)

    response = {
        "statusCode": response_code,
        "headers": {"Content-Type": "*/*"},
        "body": json.dumps(
            {
                "status_code": response_code,
                "body": response_body,
            }
        ),
    }

    logger.info("Response: %s", response)
    return response
