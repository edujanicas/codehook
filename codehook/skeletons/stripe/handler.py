def handler_logic(body):
    """
    Handles the logic around a Stripe webhook event
    :param body: The event in JSON format. Example available on example_payload.json
    :return: A tuple containing the HTTP status code and the body of the response.
    The response body is used for logging purposes only, as webhooks are asynchronous.
        (response_code, response_body)
    """
    # if event.type == 'payment_intent.succeeded':
    #     payment_intent = event.data.object # contains a stripe.PaymentIntent
    #     print('PaymentIntent was successful!')
    # elif event.type == 'payment_method.attached':
    #     payment_method = event.data.object # contains a stripe.PaymentMethod
    #     print('PaymentMethod was attached to a Customer!')
    # # ... handle other event types
    # else:
    #     print('Unhandled event type {}'.format(event.type))
    return (500, "Handler logic skeleton")
