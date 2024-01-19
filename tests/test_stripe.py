import os

import pytest

from codehook.sources.stripe import Stripe


@pytest.fixture(scope="module")
def my_stripe():
    stripe_api_key = os.getenv("STRIPE_API_KEY")
    return Stripe(stripe_api_key)


class TestStripe:
    def test_list_webhooks(self, my_stripe):
        result = my_stripe.list_webhooks()
        assert result == []

    def test_create_webhooks(self, my_stripe):
        
        events = ['*']
        url = "https://example.com/webhook"
        
        result = my_stripe.create_webhook(events, url)
        assert result.__contains__("we_")

        my_stripe.delete_webhook(result)

    def test_delete_webhooks(self, my_stripe):
        
        events = ['*']
        url = "https://example.com/webhook"
        
        result = my_stripe.create_webhook(events, url)
        my_stripe.delete_webhook(result)
        
        result = my_stripe.list_webhooks()
        assert result == []