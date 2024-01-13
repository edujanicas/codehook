import configparser
import logging

import stripe

logger = logging.getLogger(__name__)

config = configparser.ConfigParser()
config.read("config.cfg")

STRIPE_API_KEY = config["default"]["stripe_api_key"]

stripe.api_key = STRIPE_API_KEY


class Stripe:
    def __init__(self):
        self.tags = {"codehook": "true"}

    def create(self, enabled_events, api_url):
        """
        Create a webhook endpoint in Stripe. A webhook endpoint must have a url and a list of enabled_events.

        :param enabled_events: The list of events to enable for this endpoint.
        You may specify ['*'] to enable all events, except those that require explicit selection.
        :param api_url: The URL of the webhook endpoint.
        :return: The webhook endpoint id.
        """
        endpoint = stripe.WebhookEndpoint.create(
            enabled_events=enabled_events, url=api_url, metadata=self.tags
        )
        logger.info("Created endpoint %s.", endpoint.id)
        return endpoint.id

    def delete_endpoint(self, webhook_id):
        """
        Deletes a Stripe Webhook Endpoint.

        :param webhook_id: The id of the endpoint to delete.
        """
        try:
            stripe.WebhookEndpoint.delete(webhook_id)
        except Exception:
            logger.exception("Couldn't delete endpoint %s.", webhook_id)
            raise

    def list_endpoints(self):
        """
        Returns a list of your webhook endpoints for the current account.

        :return: A list of your webhook endpoints.
        """
        try:
            endpoints = []
            for endpoint in stripe.WebhookEndpoint.list().auto_paging_iter():
                if endpoint["metadata"] == self.tags:
                    endpoints.append(endpoint)
            return endpoints
        except Exception:
            logger.exception("Couldn't retrieve webhook Endpoints.")
            raise
