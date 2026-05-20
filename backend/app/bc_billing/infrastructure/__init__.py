"""bc_billing.infrastructure · única capa que toca stripe SDK."""
from app.bc_billing.infrastructure.stripe_adapter import (
    StripeAdapter,
    get_stripe_adapter,
)

__all__ = ["StripeAdapter", "get_stripe_adapter"]
