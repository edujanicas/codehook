import stripe
from rich import print

from ..model import Source


class Stripe(Source):
    def __init__(self, api_key: str):
        super().__init__()
        self.tags = {"codehook": "true"}

        stripe.api_key = api_key

    def create_webhook(self, events: list[str], url: str):
        """
        Create a webhook endpoint in Stripe. A webhook endpoint must have a url and a list of enabled_events.

        :param events: The list of events to enable for this endpoint.
        You may specify ['*'] to enable all events, except those that require explicit selection.
        :param url: The URL of the webhook endpoint.
        :return: The webhook endpoint id.
        """
        print("Creating a webhook endpoint in Stripe")
        endpoint = stripe.WebhookEndpoint.create(
            enabled_events=events, url=url, metadata=self.tags
        )
        return endpoint.id

    def delete_webhook(self, id: str):
        """
        Deletes a Stripe Webhook Endpoint.

        :param id: The id of the endpoint to delete.
        """
        print(f"Deleting the Stripe webhook endpoint with id {id}")
        try:
            stripe.WebhookEndpoint.delete(id)
        except Exception:
            print(f"[bold red]Error: Couldn't delete endpoint {id}[/bold red]")
            raise

    def list_webhooks(self):
        """
        Returns a list of your webhook endpoints for the current account.

        :return: A list of your webhook endpoints.
        """
        try:
            print("Retrieving Stripe webhook endpoints")
            endpoints = []
            for endpoint in stripe.WebhookEndpoint.list().auto_paging_iter():
                if endpoint["metadata"] == self.tags:
                    endpoints.append(endpoint)

            webhook_ids = [webhook["id"] for webhook in endpoints]
            if webhook_ids:
                print(webhook_ids)
            else:
                print("[bold red]No webhook endpoints[/bold red]")
            return webhook_ids
        except Exception:
            print("[bold red]Error: Couldn't retreive Stripe endpoints[/bold red]")
            raise
