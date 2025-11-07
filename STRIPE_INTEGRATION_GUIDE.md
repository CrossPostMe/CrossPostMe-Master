# 💳 Stripe Payment Integration Guide

Complete guide for integrating Stripe payments into CrossPostMe.

---

## 🎯 Overview

This guide covers:

- ✅ One-time payments (Payment Intents)
- ✅ Recurring subscriptions
- ✅ Webhook event handling
- ✅ Frontend React integration
- ✅ Security best practices
- ✅ Testing with Stripe test mode

---

## 📋 Prerequisites

### 1. Stripe Account

1. Go to https://stripe.com/
2. Sign up for a Stripe account
3. Complete account verification

### 2. Get API Keys

1. Login to https://dashboard.stripe.com/
2. Navigate to **Developers → API keys**
3. Copy keys:
   - **Publishable key** (starts with `pk_test_`)
   - **Secret key** (starts with `sk_test_`)

### 3. Set Up Webhook

1. Go to https://dashboard.stripe.com/webhooks
2. Click "+ Add endpoint"
3. Enter URL: `https://yourdomain.com/api/payments/webhook`
4. Select events to listen for:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. Copy **Signing secret** (starts with `whsec_`)

---

## 🔧 Backend Setup

### Step 1: Install Dependencies

```bash
cd app/backend
pip install -r requirements-stripe.txt
```

Or install manually:

```bash
pip install stripe==11.5.0
```

### Step 2: Configure Environment Variables

Add to `app/backend/.env`:

```bash
# ============================================
# STRIPE PAYMENT CONFIGURATION
# ============================================
# Test keys (for development)
STRIPE_SECRET_KEY=sk_test_51xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
STRIPE_PUBLISHABLE_KEY=pk_test_51xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# For production, use live keys:
# STRIPE_SECRET_KEY=sk_live_51xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# STRIPE_PUBLISHABLE_KEY=pk_live_51xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Step 3: Import Payment Routes

The routes are automatically imported in `server.py`. Verify:

```python
# In app/backend/server.py
from .routes import stripe_payments
app.include_router(stripe_payments.router)
```

### Step 4: Test Backend

```bash
# Start backend
cd app/backend
source .venv/bin/activate  # or .\.venv\Scripts\Activate.ps1 on Windows
uvicorn server:app --reload

# Test config endpoint
curl http://localhost:8000/api/payments/config
# Expected: {"publishable_key":"pk_test_...","currency":"usd","country":"US"}
```

---

## 🎨 Frontend Setup

### Step 1: Install Dependencies

```bash
cd app/frontend
npm install @stripe/stripe-js @stripe/react-stripe-js
```

Or with yarn:

```bash
yarn add @stripe/stripe-js @stripe/react-stripe-js
```

### Step 2: Import Payment Component

```jsx
import StripePayment from "./components/StripePayment";

function CheckoutPage() {
  const handleSuccess = (paymentIntent) => {
    console.log("Payment successful!", paymentIntent);
    // Redirect to success page or show confirmation
  };

  const handleError = (error) => {
    console.error("Payment failed:", error);
    // Show error message to user
  };

  return (
    <div className="checkout">
      <h1>Checkout</h1>
      <StripePayment
        amount={1000} // $10.00 (amount in cents)
        description="Premium Subscription"
        metadata={{ plan: "premium" }}
        onSuccess={handleSuccess}
        onError={handleError}
      />
    </div>
  );
}
```

---

## 💰 Payment Flows

### One-Time Payment

```jsx
<StripePayment
  amount={2500} // $25.00
  description="Ad Boost Package"
  metadata={{
    package: "boost",
    ad_id: "123456",
  }}
  onSuccess={(paymentIntent) => {
    console.log("Payment ID:", paymentIntent.id);
    // Update UI, unlock features, etc.
  }}
  onError={(error) => {
    alert(`Payment failed: ${error.message}`);
  }}
/>
```

### Subscription Payment

For subscriptions, use the backend API directly:

```javascript
const createSubscription = async (priceId, paymentMethodId) => {
  const token = localStorage.getItem("access_token");

  const response = await fetch(
    `${BACKEND_URL}/api/payments/create-subscription`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        price_id: priceId,
        payment_method_id: paymentMethodId,
      }),
    },
  );

  const data = await response.json();

  if (data.client_secret) {
    // Confirm payment with Stripe
    const { error } = await stripe.confirmCardPayment(data.client_secret);
    if (error) {
      console.error("Subscription payment failed:", error);
    } else {
      console.log("Subscription created!");
    }
  }
};
```

---

## 🎫 Creating Pricing Plans (Stripe Dashboard)

### Step 1: Create Products

1. Go to https://dashboard.stripe.com/products
2. Click "+ New"
3. Fill in:
   - **Name:** Premium Plan
   - **Description:** Full access to all features
   - **Pricing:** Recurring, Monthly
   - **Amount:** $9.99 USD
4. Save and copy **Price ID** (starts with `price_`)

### Step 2: Use Price ID in Code

```javascript
const PREMIUM_PLAN_PRICE_ID = "price_1234567890abcdef";

<button
  onClick={() => createSubscription(PREMIUM_PLAN_PRICE_ID, paymentMethodId)}
>
  Subscribe to Premium
</button>;
```

---

## 🔔 Webhook Events

The backend automatically handles these events:

| Event                           | Description                    | Action                            |
| ------------------------------- | ------------------------------ | --------------------------------- |
| `payment_intent.succeeded`      | Payment completed              | Save to database, unlock features |
| `payment_intent.payment_failed` | Payment failed                 | Log failure, notify user          |
| `customer.subscription.created` | Subscription started           | Create subscription record        |
| `customer.subscription.updated` | Subscription changed           | Update subscription status        |
| `customer.subscription.deleted` | Subscription cancelled         | Mark as cancelled                 |
| `invoice.payment_succeeded`     | Subscription payment succeeded | Update payment history            |
| `invoice.payment_failed`        | Subscription payment failed    | Notify user, retry payment        |

### Testing Webhooks Locally

Use Stripe CLI to forward webhooks to localhost:

```bash
# Install Stripe CLI: https://stripe.com/docs/stripe-cli
brew install stripe/stripe-cli/stripe  # macOS
# or download from https://github.com/stripe/stripe-cli/releases

# Login
stripe login

# Forward webhooks to local backend
stripe listen --forward-to localhost:8000/api/payments/webhook

# Copy webhook signing secret and add to .env:
# STRIPE_WEBHOOK_SECRET=whsec_...
```

Now when you make test payments, webhooks will be sent to your local server!

---

## 🧪 Testing

### Test Card Numbers

Stripe provides test card numbers for different scenarios:

| Scenario                   | Card Number         | CVC          | Expiry          |
| -------------------------- | ------------------- | ------------ | --------------- |
| ✅ Success                 | 4242 4242 4242 4242 | Any 3 digits | Any future date |
| ❌ Declined                | 4000 0000 0000 0002 | Any 3 digits | Any future date |
| 🔐 Requires authentication | 4000 0025 0000 3155 | Any 3 digits | Any future date |
| 💰 Insufficient funds      | 4000 0000 0000 9995 | Any 3 digits | Any future date |

### Testing Flow

```bash
# 1. Start backend
cd app/backend && uvicorn server:app --reload

# 2. Start frontend
cd app/frontend && npm start

# 3. Start webhook forwarding (in another terminal)
stripe listen --forward-to localhost:8000/api/payments/webhook

# 4. Test payment in browser
# Go to http://localhost:3000/checkout
# Use test card: 4242 4242 4242 4242
# Enter any CVC and future expiry date

# 5. Check webhook events
# Stripe CLI will show events being forwarded
```

### View Test Payments

1. Go to https://dashboard.stripe.com/test/payments
2. See all test payments and their status
3. Click on payment to view details

---

## 🔒 Security Best Practices

### ✅ DO

1. **Use environment variables for keys**

   ```bash
   # Never hardcode keys!
   STRIPE_SECRET_KEY=sk_test_...
   ```

2. **Verify webhook signatures**

   ```python
   # Always set STRIPE_WEBHOOK_SECRET in production
   event = stripe.Webhook.construct_event(
       payload, sig_header, STRIPE_WEBHOOK_SECRET
   )
   ```

3. **Use HTTPS in production**
   - Stripe requires HTTPS for live mode
   - Use SSL/TLS certificates

4. **Validate amounts on backend**

   ```python
   # Never trust amount from frontend
   # Always calculate on backend
   amount = calculate_order_total(cart_items)
   ```

5. **Handle idempotency**
   ```python
   # Use idempotency keys for retries
   stripe.PaymentIntent.create(
       amount=1000,
       currency='usd',
       idempotency_key='unique-key-123'
   )
   ```

### ❌ DON'T

1. **Never expose secret key in frontend**

   ```javascript
   // ❌ BAD - secret key in JavaScript!
   const stripe = Stripe("sk_test_...");

   // ✅ GOOD - only publishable key
   const stripe = Stripe("pk_test_...");
   ```

2. **Never skip webhook signature verification**

   ```python
   # ❌ BAD - no signature verification
   # Anyone can send fake webhooks!
   ```

3. **Never store full card details**
   - Use Stripe's tokenization
   - Let Stripe handle PCI compliance

4. **Never use test keys in production**
   - Test keys start with `sk_test_` / `pk_test_`
   - Live keys start with `sk_live_` / `pk_live_`

---

## 🚀 Production Deployment

### Step 1: Switch to Live Mode

1. Go to https://dashboard.stripe.com/
2. Toggle from "Test mode" to "Live mode" (top right)
3. Get live API keys from **Developers → API keys**

### Step 2: Update Environment Variables

```bash
# In production .env (Render, etc.)
STRIPE_SECRET_KEY=sk_live_51xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
STRIPE_PUBLISHABLE_KEY=pk_live_51xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Step 3: Configure Production Webhook

1. Go to https://dashboard.stripe.com/webhooks
2. Toggle to "Live mode"
3. Create new endpoint: `https://crosspostme.com/api/payments/webhook`
4. Copy live webhook secret
5. Update `STRIPE_WEBHOOK_SECRET` in production environment

### Step 4: Enable Payment Methods

1. Dashboard → Settings → Payment methods
2. Enable desired payment methods:
   - ✅ Cards (Visa, Mastercard, Amex)
   - ✅ Digital wallets (Apple Pay, Google Pay)
   - ✅ Bank accounts (ACH, SEPA)
   - ✅ Buy now, pay later (Klarna, Afterpay)

### Step 5: Verify Deployment

```bash
# Test production config endpoint
curl https://crosspostme.com/api/payments/config

# Should return live publishable key
{"publishable_key":"pk_live_..."}

# Test payment with real card (refund after testing!)
```

---

## 📊 Pricing Examples

### Common Pricing Models

**1. One-Time Payments**

```javascript
// Ad Boost Package
amount: 500,  // $5.00
description: "Boost your ad for 7 days"

// Premium Listing
amount: 1500,  // $15.00
description: "Featured listing for 30 days"
```

**2. Subscription Plans**

```javascript
// Basic Plan
price_id: "price_basic_monthly",
amount: 999,  // $9.99/month
description: "Basic features + 10 listings"

// Premium Plan
price_id: "price_premium_monthly",
amount: 2999,  // $29.99/month
description: "All features + unlimited listings"

// Annual Plan (discount)
price_id: "price_premium_annual",
amount: 29999,  // $299.99/year (save $60)
description: "Premium annual subscription"
```

**3. Usage-Based Pricing**

```javascript
// Pay per listing
amount: 299,  // $2.99 per listing
description: "Cross-post to 5 platforms"

// Bulk discount
listings: 10,
amount: 2490,  // $24.90 for 10 listings ($2.49 each)
description: "Bulk listing package"
```

---

## 🐛 Troubleshooting

### "API key not found" error

**Problem:** Stripe API key not configured

**Solution:**

```bash
# Check .env file has Stripe keys
grep STRIPE_ app/backend/.env

# Should see:
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...

# Restart backend after adding keys
```

### Webhook signature verification fails

**Problem:** Webhook secret mismatch or missing

**Solution:**

```bash
# Get webhook secret from Stripe CLI
stripe listen --print-secret

# Or from dashboard:
# https://dashboard.stripe.com/webhooks
# Click on endpoint → "Signing secret"

# Add to .env
STRIPE_WEBHOOK_SECRET=whsec_...
```

### Payment gets stuck on "Processing..."

**Problem:** Frontend not handling payment confirmation

**Solution:**

```javascript
// Ensure onSuccess callback is implemented
<StripePayment
  amount={1000}
  onSuccess={(paymentIntent) => {
    console.log("Success:", paymentIntent);
    // Redirect or show success message
  }}
  onError={(error) => {
    console.error("Error:", error);
    // Show error message
  }}
/>
```

### CORS errors on payment endpoint

**Problem:** Frontend and backend on different domains

**Solution:**

```bash
# In backend .env, add frontend domain to CORS
CORS_ORIGINS=http://localhost:3000,https://crosspostme.com
```

---

## 📚 Additional Resources

### Official Documentation

- **Stripe API Docs:** https://stripe.com/docs/api
- **Payment Intents Guide:** https://stripe.com/docs/payments/payment-intents
- **Subscriptions Guide:** https://stripe.com/docs/billing/subscriptions/overview
- **Webhooks Guide:** https://stripe.com/docs/webhooks
- **Testing Guide:** https://stripe.com/docs/testing

### Stripe Libraries

- **Python SDK:** https://github.com/stripe/stripe-python
- **React Components:** https://github.com/stripe/react-stripe-js
- **Stripe.js:** https://github.com/stripe/stripe-js

### CrossPostMe Documentation

- **Environment Variables:** [ENV_VARIABLES_REFERENCE.md](ENV_VARIABLES_REFERENCE.md)
- **Secrets Management:** [SECRETS_MANAGEMENT_GUIDE.md](SECRETS_MANAGEMENT_GUIDE.md)
- **Deployment Guide:** [DEPLOYMENT_QUICK_REFERENCE.md](DEPLOYMENT_QUICK_REFERENCE.md)

---

## ✅ Checklist

### Development Setup

- [ ] Stripe account created
- [ ] Test API keys obtained
- [ ] Backend dependencies installed (`pip install stripe`)
- [ ] Frontend dependencies installed (`npm install @stripe/stripe-js @stripe/react-stripe-js`)
- [ ] Environment variables configured in `.env`
- [ ] Webhook endpoint created in Stripe dashboard
- [ ] Stripe CLI installed for local webhook testing
- [ ] Test payment completed successfully

### Production Deployment

- [ ] Switched to live mode in Stripe dashboard
- [ ] Live API keys configured in production environment
- [ ] Production webhook endpoint created
- [ ] HTTPS enabled on production domain
- [ ] Payment methods enabled (cards, digital wallets, etc.)
- [ ] Real payment tested and refunded
- [ ] Webhook events verified in production
- [ ] Error monitoring set up (Sentry, etc.)
- [ ] CORS configured for production domains
- [ ] SSL certificate valid and not expired

---

**Last Updated:** 2025-10-27

**Questions?** Check Stripe documentation or create an issue on GitHub.
