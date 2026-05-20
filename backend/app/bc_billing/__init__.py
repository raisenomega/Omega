"""bc_billing · bounded context de billing/Stripe (DDD V3).

Domain: capa pura · plan pricing + billing events
Application: use cases (create_checkout, process_webhook)
Infrastructure: único entry a stripe SDK (stripe_adapter)
"""
