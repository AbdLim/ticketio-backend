# Complete Hedera Implementation Guide

## Overview

The Hedera service has been fully implemented using the official Hedera SDK for Python. This provides real blockchain functionality for NFT ticketing operations.

## Installation

### 1. Install Hedera SDK

```bash
pip install hedera-sdk-py==2.24.0 aiohttp==3.9.1
```

### 2. Environment Configuration

Add these variables to your `.env` file:

```env
# Hedera Configuration
HEDERA_NETWORK=testnet                    # or "mainnet" for production
HEDERA_OPERATOR_ID=0.0.YOUR_ACCOUNT_ID    # Your Hedera account ID
HEDERA_OPERATOR_KEY=YOUR_PRIVATE_KEY      # Your account private key
HEDERA_MIRROR_NODE_URL=https://testnet.mirrornode.hedera.com
```

### 3. Getting Hedera Credentials

#### For Testnet (Development):

1. Go to [Hedera Portal](https://portal.hedera.com/)
2. Create a testnet account
3. Get your Account ID and Private Key
4. Fund your account with test HBAR

#### For Mainnet (Production):

1. Create a Hedera mainnet account
2. Fund with real HBAR for transaction fees
3. Use mainnet mirror node: `https://mainnet.mirrornode.hedera.com`

## Features Implemented

### 1. NFT Collection Creation

```python
# Creates a new NFT collection on Hedera
token_id = await hedera_service.create_nft_collection(
    name="Summer Festival Tickets",
    symbol="SUMMER2024",
    supply=1000,  # Maximum 1000 tickets
    metadata_uri="https://api.yoursite.com/metadata/"
)
# Returns: "0.0.123456"
```

### 2. NFT Minting

```python
# Mint individual tickets as NFTs
serial_number = await hedera_service.mint_nft(
    token_id="0.0.123456",
    metadata="Event: Summer Festival, Date: 2024-07-15, Seat: A1"
)
# Returns: "1" (serial number)
```

### 3. NFT Transfer

```python
# Transfer ticket to buyer's wallet
success = await hedera_service.transfer_nft(
    token_id="0.0.123456",
    serial_number="1",
    receiver_id="0.0.789012"  # Buyer's Hedera account
)
# Returns: True if successful
```

### 4. Ownership Verification

```python
# Verify ticket ownership for entry
is_owner = await hedera_service.verify_nft_ownership(
    token_id="0.0.123456",
    serial_number="1",
    wallet_address="0.0.789012"
)
# Returns: True if wallet owns the NFT
```

### 5. NFT Information Retrieval

```python
# Get detailed NFT information
nft_info = await hedera_service.get_nft_info(
    token_id="0.0.123456",
    serial_number="1"
)
# Returns: {
#     "token_id": "0.0.123456",
#     "serial_number": "1",
#     "owner": "0.0.789012",
#     "metadata": "Event: Summer Festival...",
#     "created_at": "2024-01-15T10:30:00Z"
# }
```

### 6. Account NFT Listing

```python
# Get all NFTs owned by an account
nfts = await hedera_service.get_account_nfts("0.0.789012")
# Returns: List of NFT objects
```

### 7. Token Information

```python
# Get token collection details
token_info = await hedera_service.get_token_info("0.0.123456")
# Returns: {
#     "token_id": "0.0.123456",
#     "name": "Summer Festival Tickets",
#     "symbol": "SUMMER2024",
#     "treasury_account": "0.0.123",
#     "max_supply": 1000,
#     "total_supply": 150
# }
```

## Integration with Ticketing System

### Event Creation Flow

1. **Organizer creates event** → `POST /organizer/events`
2. **System creates NFT collection** → `hedera_service.create_nft_collection()`
3. **Token ID stored** in event record
4. **Collection ready** for ticket sales

### Ticket Purchase Flow

1. **User purchases ticket** → `POST /tickets/purchase`
2. **System mints NFT** → `hedera_service.mint_nft()`
3. **NFT transferred to buyer** → `hedera_service.transfer_nft()`
4. **QR code generated** with token ID and serial number
5. **Ticket record saved** in database

### Ticket Verification Flow

1. **Staff scans QR code** → `POST /tickets/verify`
2. **System verifies ownership** → `hedera_service.verify_nft_ownership()`
3. **Ticket marked as used** if valid
4. **Entry granted/denied** based on verification

## Error Handling

The service includes comprehensive error handling:

```python
try:
    token_id = await hedera_service.create_nft_collection(...)
except Exception as e:
    # Handle creation failure
    logger.error(f"NFT collection creation failed: {e}")
```

Common error scenarios:

-   **Insufficient HBAR balance** for transaction fees
-   **Invalid account IDs** or private keys
-   **Network connectivity issues**
-   **Token association failures**

## Transaction Costs

Typical Hedera transaction costs (testnet/mainnet):

-   **Token Creation**: ~$1-2 USD
-   **NFT Minting**: ~$0.05 USD per NFT
-   **NFT Transfer**: ~$0.001 USD
-   **Token Association**: ~$0.05 USD

## Security Considerations

### 1. Private Key Management

-   **Never expose** private keys in code
-   **Use environment variables** for credentials
-   **Consider key rotation** for production

### 2. Account Security

-   **Multi-signature accounts** for high-value operations
-   **Separate treasury accounts** for different events
-   **Regular security audits**

### 3. Network Security

-   **Use HTTPS** for all API calls
-   **Validate all inputs** before blockchain operations
-   **Rate limiting** to prevent abuse

## Testing

### Unit Tests Example

```python
import pytest
from app.utils.hedera import hedera_service

@pytest.mark.asyncio
async def test_create_nft_collection():
    token_id = await hedera_service.create_nft_collection(
        name="Test Event",
        symbol="TEST",
        supply=100,
        metadata_uri="https://test.com/metadata"
    )
    assert token_id.startswith("0.0.")

@pytest.mark.asyncio
async def test_mint_and_transfer():
    # Create collection
    token_id = await hedera_service.create_nft_collection(...)

    # Mint NFT
    serial = await hedera_service.mint_nft(token_id, "test metadata")
    assert serial.isdigit()

    # Transfer NFT
    success = await hedera_service.transfer_nft(
        token_id, serial, "0.0.testaccount"
    )
    assert success is True
```

## Production Deployment

### 1. Environment Setup

```bash
# Production environment variables
HEDERA_NETWORK=mainnet
HEDERA_OPERATOR_ID=0.0.YOUR_MAINNET_ACCOUNT
HEDERA_OPERATOR_KEY=YOUR_MAINNET_PRIVATE_KEY
HEDERA_MIRROR_NODE_URL=https://mainnet.mirrornode.hedera.com
```

### 2. Monitoring

-   **Transaction success rates**
-   **HBAR balance monitoring**
-   **API response times**
-   **Error rate tracking**

### 3. Backup Strategy

-   **Private key backup** (secure storage)
-   **Account recovery procedures**
-   **Transaction history backup**

## Migration from Mock Implementation

The new implementation is **drop-in compatible** with the existing codebase:

1. **Same method signatures** - no code changes needed
2. **Same return types** - existing logic works unchanged
3. **Enhanced functionality** - real blockchain operations
4. **Better error handling** - more robust error reporting

## Performance Considerations

-   **Async operations** - all blockchain calls are non-blocking
-   **Connection pooling** - client reuse for efficiency
-   **Caching** - Mirror Node queries for read operations
-   **Batch operations** - multiple mints in single transaction (future enhancement)

## Future Enhancements

1. **Batch minting** for large events
2. **Custom metadata schemas** for different event types
3. **Royalty configuration** for secondary sales
4. **Multi-signature treasury** accounts
5. **Automated HBAR balance** monitoring and alerts

The Hedera implementation is now production-ready and provides real blockchain functionality for your NFT ticketing system!
