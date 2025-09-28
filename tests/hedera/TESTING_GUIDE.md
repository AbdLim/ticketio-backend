# Hedera Testing Guide

## Quick Start

### 1. Run Basic Test First

```bash
python tests/hedera/test_basic_connection.py
```

This verifies your Hedera SDK installation and basic connectivity.

### 2. Check Your Credentials

```bash
python tests/hedera/test_credentials.py
```

This verifies your `.env` file has the correct format.

### 3. Verify Account-Key Match (Most Important!)

```bash
python tests/hedera/test_account_key_match.py
```

This is the #1 cause of `INVALID_SIGNATURE` errors.

### 4. Run All Tests

```bash
python tests/hedera/run_all_tests.py
```

This runs all tests in the recommended order with interactive prompts.

## Environment Setup

Your `.env` file should have:

```env
HEDERA_NETWORK=testnet
HEDERA_OPERATOR_ID=0.0.YOUR_ACCOUNT_ID
HEDERA_OPERATOR_KEY=YOUR_DER_ENCODED_PRIVATE_KEY
HEDERA_MIRROR_NODE_URL=https://testnet.mirrornode.hedera.com
```

## Key Points

1. **Use DER ENCODED PRIVATE KEY** from Hedera Portal (the longer one)
2. **Account ID and Private Key must belong together** (most common issue)
3. **Need at least 1 HBAR** in your testnet account for transactions
4. **Mock implementation always works** for development

## Troubleshooting

-   **INVALID_SIGNATURE** → Run `test_account_key_match.py`
-   **Missing variables** → Run `test_credentials.py`
-   **Low balance** → Run `test_account_balance.py`
-   **SDK issues** → Run `test_basic_connection.py`

## Development Workflow

1. **Start with mock** → `test_mock_implementation.py`
2. **Fix credentials** → Run diagnostic tests
3. **Switch to real Hedera** → `test_full_implementation.py`
4. **Integrate with app** → Use corrected implementation
