# Hedera Wallet Integration Guide

## 🚀 **Complete Blockchain-Native Ticketing Flow**

### **User Journey: From Account Creation to Ticket Purchase**

## 📱 **Option 1: Create New Hedera Account**

### **Step 1: Create New Account**

```bash
POST /v1/auth/create-account
{
  "name": "John Doe",
  "email": "john@example.com"
}

Response:
{
  "id": "user-uuid",
  "wallet_address": "0.0.7891234",  # New Hedera account
  "name": "John Doe",
  "email": "john@example.com",
  "role": "ATTENDEE",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "hbar_balance": 10.0,             # Initial 10 HBAR
  "usd_balance": 0.50,              # ~$0.50 USD equivalent
  "last_balance_check": "2024-01-15T10:30:00Z"
}
```

**What Happens Behind the Scenes:**

1. ✅ **Generate new Hedera key pair**
2. ✅ **Create account on Hedera blockchain**
3. ✅ **Fund with 10 HBAR initial balance**
4. ✅ **Create user profile in database**
5. ✅ **Return account details + current balance**

## 🔐 **Option 2: Login with Existing Wallet**

### **Step 1: Login with Wallet Address**

```bash
POST /v1/auth/login
{
  "wallet_address": "0.0.123456"
}

Response:
{
  "id": "user-uuid",
  "wallet_address": "0.0.123456",
  "name": "Jane Smith",
  "email": "jane@example.com",
  "role": "ATTENDEE",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "hbar_balance": 1500.0,           # Current balance
  "usd_balance": 75.00,             # USD equivalent
  "last_balance_check": "2024-01-15T10:30:00Z"
}
```

**What Happens Behind the Scenes:**

1. ✅ **Verify wallet address exists in system**
2. ✅ **Query current HBAR balance from blockchain**
3. ✅ **Convert to USD equivalent**
4. ✅ **Return user profile + live balance**

## 🎫 **Ticket Purchase with HBAR**

### **Step 1: Browse Events**

```bash
GET /v1/events

Response:
[
  {
    "id": "event-uuid",
    "name": "Summer Music Festival",
    "price": 99.99,           # USD price
    "hbar_price": 2000.0,     # HBAR equivalent
    "date": "2024-07-15T18:00:00Z",
    "token_id": "0.0.6918940"
  }
]
```

### **Step 2: Check Balance Before Purchase**

```bash
GET /v1/auth/balance?wallet_address=0.0.123456

Response:
{
  "wallet_address": "0.0.123456",
  "hbar_balance": 1500.0,
  "usd_balance": 75.00,
  "sufficient_for_ticket": true,    # Has enough for 2000 HBAR ticket
  "last_updated": "2024-01-15T10:30:00Z"
}
```

### **Step 3: Purchase Ticket with HBAR**

```bash
POST /v1/tickets/purchase-hbar
Authorization: Bearer <user_jwt_token>
{
  "event_id": "event-uuid",
  "buyer_wallet": "0.0.123456",
  "payment_transaction_id": "0.0.123456@1234567890.123456789"
}

Response:
{
  "ticket_id": "ticket-uuid",
  "token_id": "0.0.6918940",
  "serial_number": "1",
  "qr_data": "data:image/png;base64,iVBORw0KGgo...",
  "payment_verified": true,
  "hbar_paid": 2000.0,
  "usd_equivalent": 100.00,
  "transaction_id": "0.0.123456@1234567890.123456789"
}
```

## 💰 **HBAR Payment Flow**

### **Backend Payment Processing:**

```python
# 1. Get event price in HBAR
event_price_usd = 99.99
hbar_rate = 0.05  # 1 HBAR = $0.05
required_hbar = event_price_usd / hbar_rate  # 2000 HBAR

# 2. Check user has sufficient balance
balance_check = await hedera_wallet_service.check_sufficient_balance(
    account_id="0.0.123456",
    required_hbar=required_hbar
)

if not balance_check["sufficient"]:
    raise HTTPException(402, "Insufficient HBAR balance")

# 3. Verify payment transaction
payment_verification = await crypto_payment_service.verify_hbar_payment(
    transaction_id="0.0.123456@1234567890.123456789",
    expected_amount=required_hbar,
    recipient_account="0.0.organizer_account",
    sender_account="0.0.123456"
)

if not payment_verification["success"]:
    raise HTTPException(400, "Payment verification failed")

# 4. Create NFT ticket (after verified payment)
serial_number = await hedera_service.mint_nft(
    token_id=event.token_id,
    metadata=f"Event: {event.name}, Paid: {required_hbar} HBAR"
)

# 5. Transfer NFT to buyer
await hedera_service.transfer_nft(
    token_id=event.token_id,
    serial_number=serial_number,
    receiver_id="0.0.123456"
)
```

## 🔄 **Real-Time Balance Updates**

### **Balance Refresh Endpoint:**

```bash
GET /v1/auth/balance?wallet_address=0.0.123456

# Always returns live balance from Hedera blockchain
{
  "wallet_address": "0.0.123456",
  "hbar_balance": 500.0,        # Updated after ticket purchase
  "usd_balance": 25.00,
  "last_updated": "2024-01-15T10:35:00Z"
}
```

## 🎯 **Frontend Integration Examples**

### **React Component for Balance Display:**

```javascript
const WalletBalance = ({ userToken, walletAddress }) => {
    const [balance, setBalance] = useState(null);

    useEffect(() => {
        const fetchBalance = async () => {
            const response = await fetch(
                `/v1/auth/balance?wallet_address=${walletAddress}`,
                {
                    headers: { Authorization: `Bearer ${userToken}` },
                },
            );
            const balanceData = await response.json();
            setBalance(balanceData);
        };

        fetchBalance();
        // Refresh balance every 30 seconds
        const interval = setInterval(fetchBalance, 30000);
        return () => clearInterval(interval);
    }, [walletAddress]);

    return (
        <div className="wallet-balance">
            <h3>Your Wallet</h3>
            <p>Address: {walletAddress}</p>
            <p>Balance: {balance?.hbar_balance} HBAR</p>
            <p>USD Value: ${balance?.usd_balance}</p>
        </div>
    );
};
```

### **Ticket Purchase with Balance Check:**

```javascript
const purchaseTicket = async (eventId, eventPrice) => {
    // 1. Check balance first
    const balanceResponse = await fetch(
        `/v1/auth/balance?wallet_address=${userWallet}`,
    );
    const balance = await balanceResponse.json();

    const requiredHbar = eventPrice / 0.05; // Convert USD to HBAR

    if (balance.hbar_balance < requiredHbar) {
        alert(
            `Insufficient balance. Need ${requiredHbar} HBAR, have ${balance.hbar_balance} HBAR`,
        );
        return;
    }

    // 2. Show payment instructions
    const paymentInstructions = {
        recipient: "0.0.organizer_account",
        amount: requiredHbar,
        memo: `Ticket for event ${eventId}`,
    };

    showHbarPaymentModal(paymentInstructions);

    // 3. After user sends payment, get transaction ID
    const transactionId = await getUserTransactionId();

    // 4. Purchase ticket
    const purchaseResponse = await fetch("/v1/tickets/purchase-hbar", {
        method: "POST",
        headers: {
            Authorization: `Bearer ${userToken}`,
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            event_id: eventId,
            buyer_wallet: userWallet,
            payment_transaction_id: transactionId,
        }),
    });

    const ticket = await purchaseResponse.json();
    displayTicket(ticket);
};
```

## 🔒 **Security Features**

### **Payment Verification:**

-   ✅ **Blockchain verification** - All payments verified on Hedera network
-   ✅ **Amount validation** - Exact HBAR amount required
-   ✅ **Recipient verification** - Payment must go to correct account
-   ✅ **Double-spend prevention** - Transaction IDs tracked

### **Balance Protection:**

-   ✅ **Real-time balance checks** - Always current blockchain data
-   ✅ **Insufficient funds prevention** - Check before purchase
-   ✅ **Automatic refunds** - If NFT creation fails after payment

## 🎉 **Benefits of This Approach**

### **For Users:**

-   🚀 **True ownership** - NFT tickets in their Hedera wallet
-   💰 **Transparent pricing** - See exact HBAR cost
-   🔄 **Real-time balance** - Always know current funds
-   🎫 **Transferable tickets** - Can sell/transfer NFTs

### **For Organizers:**

-   💎 **Instant payments** - HBAR transfers are fast
-   🔒 **No chargebacks** - Blockchain payments are final
-   📊 **Full transparency** - All transactions on public ledger
-   💸 **Lower fees** - Hedera has minimal transaction costs

This creates a fully blockchain-native ticketing experience where users manage their HBAR balance and purchase tickets directly with cryptocurrency! 🚀✨
