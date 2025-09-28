# Hedera Tests

This directory contains comprehensive tests for the Hedera blockchain integration.

## Test Files

### Basic Tests

-   **`test_basic_connection.py`** - Tests basic Hedera SDK import and connection
-   **`test_credentials.py`** - Verifies credential format and parsing
-   **`test_account_balance.py`** - Checks HBAR balance and funding
-   **`test_account_key_match.py`** - Verifies account ID and private key match

### Implementation Tests

-   **`test_minimal_token.py`** - Minimal NFT token creation test
-   **`test_full_implementation.py`** - Full Hedera service test with all operations
-   **`test_mock_implementation.py`** - Tests the mock implementation for development

### Utilities

-   **`utils.py`** - Helper functions for testing and account creation

## Running Tests

### Prerequisites

1. Install dependencies: `pip install hedera-sdk-py aiohttp python-dotenv`
2. Set up your `.env` file with Hedera credentials
3. Ensure you have testnet HBAR in your account

### Run Individual Tests

```bash
# Basic connection test (start here)
python tests/hedera/test_basic_connection.py

# Check credentials
python tests/hedera/test_credentials.py

# Check balance
python tests/hedera/test_account_balance.py

# Verify account-key match (most important!)
python tests/hedera/test_account_key_match.py

# Test minimal token creation
python tests/hedera/test_minimal_token.py

# Test full implementation
python tests/hedera/test_full_implementation.py

# Test mock implementation (always works)
python tests/hedera/test_mock_implementation.py
```

### Run All Tests

```bash
python tests/hedera/run_all_tests.py
```

## Troubleshooting

### Common Issues

1. **INVALID_SIGNATURE Error**

    - Run `test_account_key_match.py` to verify account and key belong together
    - Make sure you're using the DER ENCODED PRIVATE KEY from Hedera Portal

2. **Missing Environment Variables**

    - Check your `.env` file has all required Hedera settings
    - Run `test_credentials.py` to verify format

3. **Insufficient Balance**

    - Run `test_account_balance.py` to check HBAR balance
    - Get free testnet HBAR from https://portal.hedera.com/

4. **Import Errors**
    - Make sure `hedera-sdk-py` is installed
    - Run `test_basic_connection.py` to verify SDK installation

### Environment Variables Required

```env
HEDERA_NETWORK=testnet
HEDERA_OPERATOR_ID=0.0.YOUR_ACCOUNT_ID
HEDERA_OPERATOR_KEY=YOUR_DER_ENCODED_PRIVATE_KEY
HEDERA_MIRROR_NODE_URL=https://testnet.mirrornode.hedera.com
```

### Getting Hedera Credentials

1. Go to [Hedera Portal](https://portal.hedera.com/)
2. Create a testnet account
3. Copy the **ACCOUNT ID** (format: 0.0.123456)
4. Copy the **DER ENCODED PRIVATE KEY** (long hex string)
5. Fund your account with free testnet HBAR

## Test Sequence

For new setups, run tests in this order:

1. `test_basic_connection.py` - Verify SDK works
2. `test_credentials.py` - Verify credential format
3. `test_account_balance.py` - Check funding
4. `test_account_key_match.py` - **Most important** - verify account-key match
5. `test_minimal_token.py` - Try simple token creation
6. `test_full_implementation.py` - Test complete functionality

If any test fails, fix the issue before proceeding to the next test.

## Development Workflow

-   Use `test_mock_implementation.py` for development when Hedera credentials have issues
-   Switch to real Hedera implementation once all tests pass
-   The mock and real implementations have identical APIs
