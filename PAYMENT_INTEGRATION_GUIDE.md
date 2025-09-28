# Payment Integration Guide

## 💳 Complete Ticket Purchase Flow with Payments

### **Traditional Payment Flow (Credit Card)**

#### 1. Get Event Price

```bash
GET /v1/events/event-uuid
Response:
{
  "id": "event-uuid",
  "name": "Summer Festival",
  "price": 99.99,
  "currency": "USD"
}
```

#### 2. Purchase Ticket with Payment

```bash
POST /v1/tickets/purchase
Authorization: Bearer <user_jwt_token>
{
  "event_id": "event-uuid",
  "buyer_wallet": "0.0.123456",
  "payment_method": "card",
  "payment_token": "pm_1234567890"  # From Stripe/payment provider
}

Response:
{
  "ticket_id": "ticket-uuid",
  "token_id": "0.0.6918940",
  "serial_number": "1",
  "qr_data": "data:image/png;base64,iVBORw0KGgo...",
  "payment_id": "pi_1234567890",
  "amount_paid": 99.99,
  "currency": "USD"
}
```

### **Cryptocurrency Payment Flow**

#### 1. Get Crypto Price

```bash
GET /v1/payments/crypto-price?event_id=event-uuid&currency=HBAR
Response:
{
  "usd_price": 99.99,
  "crypto_currency": "HBAR",
  "crypto_amount": 2000.0,
  "exchange_rate": 0.05,
  "expires_at": "2024-01-15T10:35:00Z",
  "payment_address": "0.0.organizer_account"
}
```

#### 2. User Sends Crypto Payment

```bash
# User sends 2000 HBAR to organizer's account
# Gets transaction hash: "0.0.123456@1234567890.123456789"
```

#### 3. Submit Payment Proof

```bash
POST /v1/tickets/purchase-crypto
Authorization: Bearer <user_jwt_token>
{
  "event_id": "event-uuid",
  "buyer_wallet": "0.0.123456",
  "transaction_hash": "0.0.123456@1234567890.123456789",
  "crypto_currency": "HBAR",
  "crypto_amount": 2000.0
}

Response:
{
  "ticket_id": "ticket-uuid",
  "token_id": "0.0.6918940",
  "serial_number": "1",
  "qr_data": "data:image/png;base64,iVBORw0KGgo...",
  "payment_verified": true,
  "transaction_hash": "0.0.123456@1234567890.123456789"
}
```

## 🔒 Payment Security & Error Handling

### **Payment Validation Steps**

1. **Amount Verification**

    ```python
    if payment_amount < event.price:
        raise HTTPException(400, "Insufficient payment amount")
    ```

2. **Payment Processing**

    ```python
    payment_result = await payment_service.process_payment(...)
    if not payment_result["success"]:
        raise HTTPException(402, "Payment failed")
    ```

3. **NFT Creation (After Payment)**
    ```python
    try:
        nft_result = await hedera_service.mint_nft(...)
    except Exception:
        await payment_service.refund_payment(payment_id)
        raise HTTPException(500, "NFT creation failed, payment refunded")
    ```

### **Error Scenarios & Handling**

| Scenario                     | Action                   | User Experience             |
| ---------------------------- | ------------------------ | --------------------------- |
| Payment fails                | Return error immediately | "Payment declined"          |
| Payment succeeds, NFT fails  | Auto-refund payment      | "Technical issue, refunded" |
| NFT succeeds, transfer fails | Auto-refund payment      | "Transfer failed, refunded" |
| All succeeds                 | Return ticket            | "Ticket purchased!"         |

## 💡 Implementation Options

### **Option 1: Traditional Payments (Recommended for MVP)**

-   ✅ **Stripe/PayPal integration**
-   ✅ **Credit cards, bank transfers**
-   ✅ **Familiar user experience**
-   ✅ **Automatic refunds**

### **Option 2: Cryptocurrency Payments**

-   ✅ **HBAR, ETH, USDC payments**
-   ✅ **Blockchain-native experience**
-   ✅ **Lower transaction fees**
-   ⚠️ **More complex UX**

### **Option 3: Hybrid Approach**

-   ✅ **Support both payment types**
-   ✅ **User chooses preferred method**
-   ✅ **Maximum accessibility**

## 🚀 Frontend Integration

### **Payment Form Example**

```javascript
// Traditional payment
const purchaseTicket = async (eventId, paymentMethod) => {
    const response = await fetch("/v1/tickets/purchase", {
        method: "POST",
        headers: {
            Authorization: `Bearer ${userToken}`,
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            event_id: eventId,
            buyer_wallet: userWallet,
            payment_method: "card",
            payment_token: paymentMethod.id,
        }),
    });

    if (response.ok) {
        const ticket = await response.json();
        // Show ticket with QR code
        displayTicket(ticket);
    } else {
        // Handle payment error
        showPaymentError();
    }
};
```

### **Crypto Payment Example**

```javascript
// Cryptocurrency payment
const purchaseWithCrypto = async (eventId, cryptoCurrency) => {
    // 1. Get crypto price
    const priceResponse = await fetch(
        `/v1/payments/crypto-price?event_id=${eventId}&currency=${cryptoCurrency}`,
    );
    const priceData = await priceResponse.json();

    // 2. Show payment instructions to user
    showCryptoPaymentInstructions(priceData);

    // 3. User sends payment and provides transaction hash
    const txHash = await getUserTransactionHash();

    // 4. Submit payment proof
    const purchaseResponse = await fetch("/v1/tickets/purchase-crypto", {
        method: "POST",
        headers: {
            Authorization: `Bearer ${userToken}`,
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            event_id: eventId,
            buyer_wallet: userWallet,
            transaction_hash: txHash,
            crypto_currency: cryptoCurrency,
            crypto_amount: priceData.crypto_amount,
        }),
    });

    const ticket = await purchaseResponse.json();
    displayTicket(ticket);
};
```

## 📊 Payment Analytics

Track important metrics:

-   **Payment success rate**
-   **Average payment processing time**
-   **Refund frequency**
-   **Popular payment methods**
-   **Revenue per event**

This ensures users have sufficient funds before NFT creation and provides a smooth, secure payment experience! 💳✨
