"""
Stripe Payment Integration Routes

Handles payment processing, payment intents, and webhook events for Stripe.
"""

import logging
import os
from typing import Any, Dict

import stripe
from backend.auth import get_current_user
from backend.db import get_typed_db
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Initialize Stripe with secret key from environment
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
if not stripe.api_key:
    logger.warning(
        "STRIPE_SECRET_KEY not set. Stripe payments will not work. "
        "Set this in your .env file for payment processing."
    )

# Webhook secret for validating webhook signatures
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

router = APIRouter(prefix="/api/payments", tags=["payments"])
db = get_typed_db()


# ============================================================================
# Pydantic Models
# ============================================================================


class CreatePaymentIntentRequest(BaseModel):
    """Request model for creating a payment intent."""

    amount: int = Field(..., description="Amount in cents (e.g., 1000 = $10.00)", gt=0)
    currency: str = Field(default="usd", description="Currency code (ISO 4217)")
    description: str | None = Field(None, description="Payment description")
    metadata: Dict[str, Any] | None = Field(None, description="Additional metadata")
    require_cvc_recollection: bool = Field(
        default=False,
        description="Require CVC re-entry for saved cards (enhanced security)",
    )


class PaymentIntentResponse(BaseModel):
    """Response model for payment intent creation."""

    client_secret: str = Field(..., description="Client secret for frontend Stripe.js")
    payment_intent_id: str = Field(..., description="Payment intent ID")


class SubscriptionRequest(BaseModel):
    """Request model for creating a subscription."""

    price_id: str = Field(..., description="Stripe price ID")
    payment_method_id: str = Field(..., description="Payment method ID from frontend")


# ============================================================================
# Payment Intent Endpoints
# ============================================================================


@router.post("/create-payment-intent", response_model=PaymentIntentResponse)
async def create_payment_intent(
    request: CreatePaymentIntentRequest,
    current_user: str = Depends(get_current_user),
) -> PaymentIntentResponse:
    """
    Create a payment intent for one-time payments.

    This endpoint creates a payment intent on Stripe and returns the client
    secret for completing the payment on the frontend.

    Args:
        request: Payment intent creation request
        current_user: Authenticated user (from dependency)

    Returns:
        PaymentIntentResponse with client_secret and payment_intent_id

    Raises:
        HTTPException: If Stripe API call fails
    """
    if not stripe.api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment processing is not configured. Please contact support.",
        )

    try:
        # Build payment method options
        payment_method_options = {}

        # Enable CVC recollection for saved cards if requested
        if request.require_cvc_recollection:
            payment_method_options["card"] = {
                "require_cvc_recollection": True,
            }

        # Create payment intent with Stripe
        payment_intent = stripe.PaymentIntent.create(
            amount=request.amount,
            currency=request.currency,
            description=request.description,
            metadata={
                "user_id": current_user.get("id"),
                "user_email": current_user.get("email"),
                **(request.metadata or {}),
            },
            # Enable automatic payment methods (cards, digital wallets, Link, etc.)
            automatic_payment_methods={"enabled": True},
            # Include payment method options if any
            **(
                {"payment_method_options": payment_method_options}
                if payment_method_options
                else {}
            ),
        )

        logger.info(
            f"Created payment intent {payment_intent.id} for user {current_user.get('id')}"
        )

        return PaymentIntentResponse(
            client_secret=payment_intent.client_secret,
            payment_intent_id=payment_intent.id,
        )

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating payment intent: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create payment intent: {str(e)}",
        )


@router.get("/payment-intent/{payment_intent_id}")
async def get_payment_intent(
    payment_intent_id: str,
    current_user: str = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Retrieve a payment intent by ID.

    Args:
        payment_intent_id: Stripe payment intent ID
        current_user: Authenticated user

    Returns:
        Payment intent details

    Raises:
        HTTPException: If payment intent not found or access denied
    """
    if not stripe.api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment processing is not configured.",
        )

    try:
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

        # Verify the payment intent belongs to the current user
        if payment_intent.metadata.get("user_id") != current_user.get("id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this payment intent.",
            )

        return {
            "id": payment_intent.id,
            "amount": payment_intent.amount,
            "currency": payment_intent.currency,
            "status": payment_intent.status,
            "description": payment_intent.description,
            "metadata": payment_intent.metadata,
        }

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error retrieving payment intent: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment intent not found: {str(e)}",
        )


# ============================================================================
# Subscription Endpoints
# ============================================================================


@router.post("/create-subscription")
async def create_subscription(
    request: SubscriptionRequest,
    current_user: str = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Create a subscription for recurring payments.

    Args:
        request: Subscription creation request
        current_user: Authenticated user

    Returns:
        Subscription details including client_secret if requires confirmation

    Raises:
        HTTPException: If subscription creation fails
    """
    if not stripe.api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment processing is not configured.",
        )

    try:
        # Get or create Stripe customer
        user_email = current_user.get("email")
        customers = stripe.Customer.list(email=user_email, limit=1)

        if customers.data:
            customer = customers.data[0]
        else:
            customer = stripe.Customer.create(
                email=user_email,
                metadata={"user_id": current_user.get("id")},
            )

        # Attach payment method to customer
        stripe.PaymentMethod.attach(
            request.payment_method_id,
            customer=customer.id,
        )

        # Set as default payment method
        stripe.Customer.modify(
            customer.id,
            invoice_settings={"default_payment_method": request.payment_method_id},
        )

        # Create subscription
        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[{"price": request.price_id}],
            payment_behavior="default_incomplete",
            payment_settings={"save_default_payment_method": "on_subscription"},
            expand=["latest_invoice.payment_intent"],
        )

        logger.info(
            f"Created subscription {subscription.id} for user {current_user.get('id')}"
        )

        return {
            "subscription_id": subscription.id,
            "client_secret": subscription.latest_invoice.payment_intent.client_secret,
            "status": subscription.status,
        }

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create subscription: {str(e)}",
        )


# ============================================================================
# Webhook Endpoint
# ============================================================================


@router.post("/webhook")
async def stripe_webhook(request: Request) -> Response:
    """
    Handle Stripe webhook events.

    This endpoint receives events from Stripe (payment succeeded, failed, etc.)
    and updates the database accordingly.

    IMPORTANT: Configure this URL in Stripe Dashboard:
    https://dashboard.stripe.com/webhooks

    Args:
        request: Raw FastAPI request (needed for signature verification)

    Returns:
        200 OK response if event processed successfully

    Raises:
        HTTPException: If signature verification fails
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not STRIPE_WEBHOOK_SECRET:
        logger.warning(
            "STRIPE_WEBHOOK_SECRET not set. Webhook signature verification disabled. "
            "This is insecure! Set STRIPE_WEBHOOK_SECRET in production."
        )
        # In development, allow webhooks without signature verification
        # NEVER do this in production!
        event = stripe.Event.construct_from(
            stripe.util.convert_to_stripe_object(payload), stripe.api_key
        )
    else:
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            # Invalid payload
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError:
            # Invalid signature
            raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle the event
    event_type = event["type"]
    event_data = event["data"]["object"]

    logger.info(f"Received Stripe webhook: {event_type}")

    try:
        if event_type == "payment_intent.succeeded":
            await handle_payment_succeeded(event_data)
        elif event_type == "payment_intent.payment_failed":
            await handle_payment_failed(event_data)
        elif event_type == "customer.subscription.created":
            await handle_subscription_created(event_data)
        elif event_type == "customer.subscription.updated":
            await handle_subscription_updated(event_data)
        elif event_type == "customer.subscription.deleted":
            await handle_subscription_deleted(event_data)
        elif event_type == "invoice.payment_succeeded":
            await handle_invoice_paid(event_data)
        elif event_type == "invoice.payment_failed":
            await handle_invoice_failed(event_data)
        else:
            logger.info(f"Unhandled event type: {event_type}")

    except Exception as e:
        logger.error(f"Error handling webhook event {event_type}: {e}")
        # Still return 200 to prevent Stripe from retrying
        # Log the error for manual investigation

    return Response(status_code=200)


# ============================================================================
# Webhook Event Handlers
# ============================================================================


async def handle_payment_succeeded(payment_intent: Dict[str, Any]) -> None:
    """Handle successful payment intent."""
    user_id = payment_intent.get("metadata", {}).get("user_id")
    amount = payment_intent.get("amount")

    logger.info(
        f"Payment succeeded: {payment_intent['id']} for user {user_id}, amount {amount}"
    )

    # Update user's payment history in database
    await db.payments.insert_one(
        {
            "user_id": user_id,
            "payment_intent_id": payment_intent["id"],
            "amount": amount,
            "currency": payment_intent.get("currency"),
            "status": "succeeded",
            "created_at": payment_intent.get("created"),
        }
    )


async def handle_payment_failed(payment_intent: Dict[str, Any]) -> None:
    """Handle failed payment intent."""
    user_id = payment_intent.get("metadata", {}).get("user_id")

    logger.warning(f"Payment failed: {payment_intent['id']} for user {user_id}")

    # Log failed payment
    await db.payments.insert_one(
        {
            "user_id": user_id,
            "payment_intent_id": payment_intent["id"],
            "amount": payment_intent.get("amount"),
            "currency": payment_intent.get("currency"),
            "status": "failed",
            "error": payment_intent.get("last_payment_error"),
            "created_at": payment_intent.get("created"),
        }
    )


async def handle_subscription_created(subscription: Dict[str, Any]) -> None:
    """Handle subscription creation."""
    customer_id = subscription.get("customer")
    subscription_id = subscription["id"]

    logger.info(f"Subscription created: {subscription_id} for customer {customer_id}")

    # Get user from customer ID
    customer = stripe.Customer.retrieve(customer_id)
    user_id = customer.metadata.get("user_id")

    # Save subscription to database
    await db.subscriptions.insert_one(
        {
            "user_id": user_id,
            "subscription_id": subscription_id,
            "customer_id": customer_id,
            "status": subscription.get("status"),
            "current_period_end": subscription.get("current_period_end"),
            "created_at": subscription.get("created"),
        }
    )


async def handle_subscription_updated(subscription: Dict[str, Any]) -> None:
    """Handle subscription update."""
    subscription_id = subscription["id"]

    logger.info(f"Subscription updated: {subscription_id}")

    # Update subscription in database
    await db.subscriptions.update_one(
        {"subscription_id": subscription_id},
        {
            "$set": {
                "status": subscription.get("status"),
                "current_period_end": subscription.get("current_period_end"),
            }
        },
    )


async def handle_subscription_deleted(subscription: Dict[str, Any]) -> None:
    """Handle subscription cancellation."""
    subscription_id = subscription["id"]

    logger.info(f"Subscription deleted: {subscription_id}")

    # Mark subscription as canceled
    await db.subscriptions.update_one(
        {"subscription_id": subscription_id}, {"$set": {"status": "canceled"}}
    )


async def handle_invoice_paid(invoice: Dict[str, Any]) -> None:
    """Handle successful invoice payment."""
    subscription_id = invoice.get("subscription")

    logger.info(f"Invoice paid for subscription: {subscription_id}")

    # Update subscription payment status
    await db.subscriptions.update_one(
        {"subscription_id": subscription_id}, {"$set": {"last_payment_status": "paid"}}
    )


async def handle_invoice_failed(invoice: Dict[str, Any]) -> None:
    """Handle failed invoice payment."""
    subscription_id = invoice.get("subscription")

    logger.warning(f"Invoice payment failed for subscription: {subscription_id}")

    # Update subscription payment status
    await db.subscriptions.update_one(
        {"subscription_id": subscription_id},
        {"$set": {"last_payment_status": "failed"}},
    )


# ============================================================================
# Configuration Endpoints
# ============================================================================


@router.get("/config")
async def get_stripe_config() -> Dict[str, str]:
    """
    Get public Stripe configuration for frontend.

    Returns:
        Dictionary with publishable key and other public config

    Note:
        Publishable key is safe to expose - it's public by design
    """
    publishable_key = os.getenv("STRIPE_PUBLISHABLE_KEY", "")

    if not publishable_key:
        logger.warning("STRIPE_PUBLISHABLE_KEY not set in environment variables")

    return {
        "publishable_key": publishable_key,
        "currency": "usd",
        "country": "US",
    }
