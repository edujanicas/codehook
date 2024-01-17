from enum import Enum

class Events(str, Enum):
    all = "*",
    account_application_authorized = "account.application.authorized"
    account_application_deauthorized = "account.application.deauthorized"
    account_external_account_created = "account.external_account.created"
    account_external_account_deleted = "account.external_account.deleted"
    account_external_account_updated = "account.external_account.updated"
    account_updated = "account.updated"
    application_fee_created = "application_fee.created"
    application_fee_refund_updated = "application_fee.refund.updated"
    application_fee_refunded = "application_fee.refunded"
    balance_available = "balance.available"
    billing_portal_configuration_created = "billing_portal.configuration.created"
    billing_portal_configuration_updated = "billing_portal.configuration.updated"
    billing_portal_session_created = "billing_portal.session.created"
    capability_updated = "capability.updated"
    cash_balance_funds_available = "cash_balance.funds_available"
    charge_captured = "charge.captured"
    charge_dispute_closed = "charge.dispute.closed"
    charge_dispute_created = "charge.dispute.created"
    charge_dispute_funds_reinstated = "charge.dispute.funds_reinstated"
    charge_dispute_funds_withdrawn = "charge.dispute.funds_withdrawn"
    charge_dispute_updated = "charge.dispute.updated"
    charge_expired = "charge.expired"
    charge_failed = "charge.failed"
    charge_pending = "charge.pending"
    charge_refund_updated = "charge.refund.updated"
    charge_refunded = "charge.refunded"
    charge_succeeded = "charge.succeeded"
    charge_updated = "charge.updated"
    checkout_session_async_payment_failed = "checkout.session.async_payment_failed"
    checkout_session_async_payment_succeeded = "checkout.session.async_payment_succeeded"
    checkout_session_completed = "checkout.session.completed"
    checkout_session_expired = "checkout.session.expired"
    climate_order_canceled = "climate.order.canceled"
    climate_order_created = "climate.order.created"
    climate_order_delayed = "climate.order.delayed"
    climate_order_delivered = "climate.order.delivered"
    climate_order_product_substituted = "climate.order.product_substituted"
    climate_product_created = "climate.product.created"
    climate_product_pricing_updated = "climate.product.pricing_updated"
    coupon_created = "coupon.created"
    coupon_deleted = "coupon.deleted"
    coupon_updated = "coupon.updated"
    credit_note_created = "credit_note.created"
    credit_note_updated = "credit_note.updated"
    credit_note_voided = "credit_note.voided"
    customer_cash_balance_transaction_created = "customer_cash_balance_transaction.created"
    customer_created = "customer.created"
    customer_deleted = "customer.deleted"
    customer_discount_created = "customer.discount.created"
    customer_discount_deleted = "customer.discount.deleted"
    customer_discount_updated = "customer.discount.updated"
    customer_source_created = "customer.source.created"
    customer_source_deleted = "customer.source.deleted"
    customer_source_expiring = "customer.source.expiring"
    customer_source_updated = "customer.source.updated"
    customer_subscription_created = "customer.subscription.created"
    customer_subscription_deleted = "customer.subscription.deleted"
    customer_subscription_paused = "customer.subscription.paused"
    customer_subscription_pending_update_applied = "customer.subscription.pending_update_applied"
    customer_subscription_pending_update_expired = "customer.subscription.pending_update_expired"
    customer_subscription_resumed = "customer.subscription.resumed"
    customer_subscription_trial_will_end = "customer.subscription.trial_will_end"
    customer_subscription_updated = "customer.subscription.updated"
    customer_tax_id_created = "customer.tax_id.created"
    customer_tax_id_deleted = "customer.tax_id.deleted"
    customer_tax_id_updated = "customer.tax_id.updated"
    customer_updated = "customer.updated"
    file_created = "file.created"
    financial_connections_account_created = "financial_connections.account.created"
    financial_connections_account_deactivated = "financial_connections.account.deactivated"
    financial_connections_account_disconnected = "financial_connections.account.disconnected"
    financial_connections_account_reactivated = "financial_connections.account.reactivated"
    financial_connections_account_refreshed_balance = "financial_connections.account.refreshed_balance"
    financial_connections_account_refreshed_transactions = "financial_connections.account.refreshed_transactions"
    identity_verification_session_canceled = "identity.verification_session.canceled"
    identity_verification_session_created = "identity.verification_session.created"
    identity_verification_session_processing = "identity.verification_session.processing"
    identity_verification_session_redacted = "identity.verification_session.redacted"
    identity_verification_session_requires_input = "identity.verification_session.requires_input"
    identity_verification_session_verified = "identity.verification_session.verified"
    invoice_created = "invoice.created"
    invoice_deleted = "invoice.deleted"
    invoice_finalization_failed = "invoice.finalization_failed"
    invoice_finalized = "invoice.finalized"
    invoice_marked_uncollectible = "invoice.marked_uncollectible"
    invoice_paid = "invoice.paid"
    invoice_payment_action_required = "invoice.payment_action_required"
    invoice_payment_failed = "invoice.payment_failed"
    invoice_payment_succeeded = "invoice.payment_succeeded"
    invoice_sent = "invoice.sent"
    invoice_upcoming = "invoice.upcoming"
    invoice_updated = "invoice.updated"
    invoice_voided = "invoice.voided"
    invoiceitem_created = "invoiceitem.created"
    invoiceitem_deleted = "invoiceitem.deleted"
    issuing_authorization_created = "issuing_authorization.created"
    issuing_authorization_request = "issuing_authorization.request"
    issuing_authorization_updated = "issuing_authorization.updated"
    issuing_card_created = "issuing_card.created"
    issuing_card_updated = "issuing_card.updated"
    issuing_cardholder_created = "issuing_cardholder.created"
    issuing_cardholder_updated = "issuing_cardholder.updated"
    issuing_dispute_closed = "issuing_dispute.closed"
    issuing_dispute_created = "issuing_dispute.created"
    issuing_dispute_funds_reinstated = "issuing_dispute.funds_reinstated"
    issuing_dispute_submitted = "issuing_dispute.submitted"
    issuing_dispute_updated = "issuing_dispute.updated"
    issuing_token_created = "issuing_token.created"
    issuing_token_updated = "issuing_token.updated"
    issuing_transaction_created = "issuing_transaction.created"
    issuing_transaction_updated = "issuing_transaction.updated"
    mandate_updated = "mandate.updated"
    order_canceled = "order.canceled"
    order_completed = "order.completed"
    order_inventory_reservation_expired = "order.inventory_reservation_expired"
    order_payment_completed = "order.payment_completed"
    order_processing = "order.processing"
    order_reopened = "order.reopened"
    order_submitted = "order.submitted"
    payment_intent_amount_capturable_updated = "payment_intent.amount_capturable_updated"
    payment_intent_canceled = "payment_intent.canceled"
    payment_intent_created = "payment_intent.created"
    payment_intent_partially_funded = "payment_intent.partially_funded"
    payment_intent_payment_failed = "payment_intent.payment_failed"
    payment_intent_processing = "payment_intent.processing"
    payment_intent_requires_action = "payment_intent.requires_action"
    payment_intent_succeeded = "payment_intent.succeeded"
    payment_link_created = "payment_link.created"
    payment_link_updated = "payment_link.updated"
    payment_method_attached = "payment_method.attached"
    payment_method_automatically_updated = "payment_method.automatically_updated"
    payment_method_detached = "payment_method.detached"
    payment_method_updated = "payment_method.updated"
    payout_canceled = "payout.canceled"
    payout_created = "payout.created"
    payout_failed = "payout.failed"
    payout_paid = "payout.paid"
    payout_reconciliation_completed = "payout.reconciliation_completed"
    payout_updated = "payout.updated"
    person_created = "person.created"
    person_deleted = "person.deleted"
    person_updated = "person.updated"
    plan_created = "plan.created"
    plan_deleted = "plan.deleted"
    plan_updated = "plan.updated"
    price_created = "price.created"
    price_deleted = "price.deleted"
    price_updated = "price.updated"
    product_created = "product.created"
    product_deleted = "product.deleted"
    product_updated = "product.updated"
    promotion_code_created = "promotion_code.created"
    promotion_code_updated = "promotion_code.updated"
    quote_accepted = "quote.accepted"
    quote_canceled = "quote.canceled"
    quote_created = "quote.created"
    quote_finalized = "quote.finalized"
    radar_early_fraud_warning_created = "radar.early_fraud_warning.created"
    radar_early_fraud_warning_updated = "radar.early_fraud_warning.updated"
    refund_created = "refund.created"
    refund_updated = "refund.updated"
    reporting_report_run_failed = "reporting.report_run.failed"
    reporting_report_run_succeeded = "reporting.report_run.succeeded"
    reporting_report_type_updated = "reporting.report_type.updated"
    review_closed = "review.closed"
    review_opened = "review.opened"
    setup_intent_canceled = "setup_intent.canceled"
    setup_intent_created = "setup_intent.created"
    setup_intent_requires_action = "setup_intent.requires_action"
    setup_intent_setup_failed = "setup_intent.setup_failed"
    setup_intent_succeeded = "setup_intent.succeeded"
    sigma_scheduled_query_run_created = "sigma.scheduled_query_run.created"
    source_canceled = "source.canceled"
    source_chargeable = "source.chargeable"
    source_failed = "source.failed"
    source_mandate_notification = "source.mandate_notification"
    source_refund_attributes_required = "source.refund_attributes_required"
    source_transaction_created = "source.transaction.created"
    source_transaction_updated = "source.transaction.updated"
    subscription_schedule_aborted = "subscription_schedule.aborted"
    subscription_schedule_canceled = "subscription_schedule.canceled"
    subscription_schedule_completed = "subscription_schedule.completed"
    subscription_schedule_created = "subscription_schedule.created"
    subscription_schedule_expiring = "subscription_schedule.expiring"
    subscription_schedule_released = "subscription_schedule.released"
    subscription_schedule_updated = "subscription_schedule.updated"
    tax_rate_created = "tax_rate.created"
    tax_rate_updated = "tax_rate.updated"
    tax_settings_updated = "tax.settings.updated"
    terminal_hardware_order_canceled = "terminal_hardware_order.canceled"
    terminal_hardware_order_created = "terminal_hardware_order.created"
    terminal_hardware_order_delivered = "terminal_hardware_order.delivered"
    terminal_hardware_order_ready_to_ship = "terminal_hardware_order.ready_to_ship"
    terminal_hardware_order_shipped = "terminal_hardware_order.shipped"
    terminal_hardware_order_undeliverable = "terminal_hardware_order.undeliverable"
    terminal_reader_action_failed = "terminal.reader.action_failed"
    terminal_reader_action_succeeded = "terminal.reader.action_succeeded"
    test_helpers_test_clock_advancing = "test_helpers.test_clock.advancing"
    test_helpers_test_clock_created = "test_helpers.test_clock.created"
    test_helpers_test_clock_deleted = "test_helpers.test_clock.deleted"
    test_helpers_test_clock_internal_failure = "test_helpers.test_clock.internal_failure"
    test_helpers_test_clock_ready = "test_helpers.test_clock.ready"
    topup_canceled = "topup.canceled"
    topup_created = "topup.created"
    topup_failed = "topup.failed"
    topup_reversed = "topup.reversed"
    topup_succeeded = "topup.succeeded"
    transfer_created = "transfer.created"
    transfer_reversed = "transfer.reversed"
    transfer_updated = "transfer.updated"


class CloudName(str, Enum):
    aws = "aws"

class Cloud:
    """
    Represents a cloud service provider.

    Methods:
    - create_function: Creates a new function in the cloud.
    - update_function: Updates an existing function in the cloud.
    - delete_function: Deletes a function from the cloud.
    - list_functions: Lists all functions available in the cloud.
    - create_api: Creates a new API in the cloud.
    - delete_api: Deletes an API from the cloud.
    - list_apis: Lists all APIs available in the cloud.
    """
    def __init__(self):
        pass
    
    def create_function(self, name: str, path: str):
        pass

    def update_function(self, id: str, path: str):
        pass

    def delete_function(self, id: str):
        pass

    def list_functions(self):
        pass

    def create_api(self, name: str, function_id: str):
        pass

    def delete_api(self, id: str):
        pass

    def list_apis(self):
        pass


class SourceName(str, Enum):
    stripe = "stripe"

class Source():
    """
    Represents a source of webhook events.

    Methods:
    - create_webhook: Creates a new webhook endpoint in the source.
    - delete_webhook: Deletes a webhook endpoint from the source.
    - list_webhooks: Lists all webhook endpoints available in the source.
    """
    def __init__(self):
        pass
    
    def create_webhook(self, events: list[Events], url: str):
        pass

    def delete_webhook(self, id: str):
        pass

    def list_webhooks(self):
        pass



