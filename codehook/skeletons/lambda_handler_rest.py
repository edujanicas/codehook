import json
import logging

# import stripe
# This is a public sample test API key.
# Don’t submit any personally identifiable information in requests made with this key.
# Sign in to see your own test API key embedded in code samples.
# stripe.api_key = 'sk_test_26PHem9AhJZvU623DfE1x4sd'

# Replace this endpoint secret with your endpoint's unique secret
# If you are testing with the CLI, find the secret by running 'stripe listen'
# If you are using an endpoint defined with the API or dashboard, look in your webhook settings
# at https://dashboard.stripe.com/webhooks
endpoint_secret = "whsec_..."

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    Handles requests that are passed through an Amazon API Gateway REST API.
    GET, POST, PUT and DELETE requests all result in success codes that echo back input
    parameters in a message.

    :param event: The event dict sent by Amazon API Gateway that contains all of the
                  request data.
    :param context: The context in which the function is called.
    :return: A response that is sent to Amazon API Gateway, to be wrapped into
             an HTTP response. The 'statusCode' field is the HTTP status code
             and the 'body' field is the body of the response.
    """
    logger.info("Request: %s", event)
    response_code = 200

    http_method = event.get("httpMethod")
    query_string = event.get("queryStringParameters")
    headers = event.get("headers")
    body = event.get("body")

    event = None

    if body:
        payload = body
    else:
        payload = ""

    try:
        event = json.loads(payload)
    except json.decoder.JSONDecodeError as e:
        print("⚠️  Webhook error while parsing basic request." + str(e))
        response_code = 400
        return {
            "statusCode": response_code,
            "body": json.dumps(
                {
                    "input": event,
                    "method": http_method,
                    "query_string": query_string,
                    "headers": headers,
                    "body": body,
                }
            ),
        }
    if endpoint_secret:
        # Only verify the event if there is an endpoint secret defined
        # Otherwise use the basic event deserialized with json
        # sig_header = headers.get("stripe-signature")
        # try:
        #     event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        # except stripe.error.SignatureVerificationError as e:
        #     print("⚠️  Webhook signature verification failed." + str(e))
        #     return {
        #         "statusCode": response_code,
        #         "body": json.dumps(
        #             {
        #                 "input": event,
        #                 "method": http_method,
        #                 "query_string": query_string,
        #                 "headers": headers,
        #                 "body": body,
        #             }
        #         ),
        #     }
        pass
    
    # TODO
    # Handle the event
    # Handle the event
    # Handle the event

    response = {
        "statusCode": response_code,
        "body": json.dumps(
            {
                "input": event,
                "method": http_method,
                "query_string": query_string,
                "headers": headers,
                "body": body,
            }
        ),
    }

    logger.info("Response: %s", response)
    return response
