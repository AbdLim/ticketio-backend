# Ticketio Backend

A FastAPI-based backend for issuing and managing ticket NFTs using Hedera. The service uses
SQLModel for the database layer, Redis for lightweight caching, and Alembic for schema migrations.

## Contents

-   `app/` — main FastAPI application, routers, services, and utilities
-   `app/utils/hedera.py` — primary Hedera service implementation (production-ready)
-   `app/services/hedera_wallet.py` — wallet/account helper service
-   `hedera_implementations/` — alternate Hedera implementations (minimal / corrected)
-   `tests/hedera/` — Hedera integration and unit tests

## Prerequisites

-   Python 3.13+
-   PostgreSQL
-   Redis
-   Environment variables (see below)

## Quick Start

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

2. Copy and edit environment config:

```bash
cp example.env .env
# Edit .env to set DB, Redis and Hedera credentials
```

3. Run migrations and start the app:

```bash
createdb ticketio_db
uv run alembic upgrade head
uv run dev
```

4. Open the API docs at `http://localhost:8000/docs`

## Hedera integration — overview

This project integrates Hedera in multiple ways to support account management and NFTs (tickets):

-   Hedera client setup and operator credentials are centralized via environment settings.
-   NFT lifecycle operations are implemented (collection creation, minting, transfers).
-   Mirror Node API is used for NFT ownership verification and metadata queries.

Key environment variables (set these in `.env`):

-   `HEDERA_NETWORK` — `testnet` or `mainnet`
-   `HEDERA_OPERATOR_ID` — operator account id (e.g. `0.0.x`)
-   `HEDERA_OPERATOR_KEY` — operator private key
-   `HEDERA_MIRROR_NODE_URL` — mirror node base URL for queries

## Hedera implementations in this repository

There are three Hedera service implementations to support different needs and to make testing easier:

1. `app/utils/hedera.py` — HederaService (Full / production)

-   Purpose: Primary, production-ready implementation used by the application.
-   Features:
    -   Create NFT collections (TokenCreateTransaction)
    -   Mint NFTs with metadata (TokenMintTransaction)
    -   Transfer NFTs between accounts (TransferTransaction)
    -   Query NFT info and verify ownership via Mirror Node (HTTP /api/v1/tokens/...)
    -   Manage Hedera `Client` lifecycle and operator configuration
-   Notes: Uses the hedera SDK objects such as `Client`, `AccountId`, `PrivateKey`, `TokenId`, and `Hbar`.

2. `hedera_implementations/hedera_corrected.py` — CorrectedHederaService

-   Purpose: A corrected/cleaned implementation with explicit SDK-correct usage and helpful utilities.
-   Features: Same core features as `HederaService`, with clearer API usage and extra helper queries (e.g., `TokenNftInfoQuery`, `TokenInfoQuery`).
-   Usage: Useful for running the full Hedera test suite (`tests/hedera/test_full_implementation.py`) or as a drop-in replacement when debugging SDK changes.

3. `hedera_implementations/hedera_minimal.py` — MinimalHederaService

-   Purpose: Lightweight fallback implementation for environments where only minimal functionality is needed (or when debugging).
-   Features: Minimal NFT create/mint/transfer and Mirror Node ownership verification. Simpler client initialization.
-   Usage: Designed for local testing or when you need a small surface area for Hedera calls.

4. `app/services/hedera_wallet.py` — HederaWalletService

-   Purpose: High-level wallet/account helper for the app's auth flows and user wallet management.
-   Features:
    -   Create new Hedera account (keypair generation + AccountCreateTransaction) with an initial HBAR top-up
    -   Query account balance (AccountBalanceQuery)
    -   Query account info (AccountInfoQuery)
    -   Check sufficient balance before payment
    -   Exchange-rate lookup (cached) to convert HBAR to USD for UI/UX

## How the Hedera flows work (high level)

-   Account creation: `HederaWalletService.create_new_hedera_account()` generates an ED25519 key pair, uses the configured operator to create a Hedera account, and returns the account id + keys and initial balance.
-   NFT creation & minting: The app creates an NFT collection (TokenCreateTransaction) and mints NFTs with metadata (TokenMintTransaction). Mint receipts return serial numbers that are stored in the application database as ticket identifiers.
-   Transfers: When tickets are transferred (resale, transfer), the app uses `TransferTransaction` to move the NFT from one account to another.
-   Ownership verification: Mirror Node queries (e.g., `GET /api/v1/tokens/{token_id}/nfts/{serial}`) are used to confirm current owner addresses.

## Where to find code and tests

-   Production Hedera service: `app/utils/hedera.py`
-   Wallet/account helper: `app/services/hedera_wallet.py`
-   Corrected and minimal implementations: `hedera_implementations/` folder
-   Hedera tests: `tests/hedera/` (includes `test_full_implementation.py` and other unit tests)

## Example: create account (API)

One documented endpoint is the account creation flow (see `docs/HEDERA_WALLET_INTEGRATION.md`):

```
POST /v1/auth/create-account
{
    "name": "John Doe",
    "email": "john@example.com"
}

Response contains: `wallet_address` (the new Hedera account id), `private_key`/`public_key` (if created by server), initial balances and a JWT token used by the app.
```

## Running Hedera tests

Set Hedera credentials in your environment (or `.env`) and run the Hedera test suite:

```bash
# from repository root
python -m pytest tests/hedera -q
```

## Next steps & notes

-   If you plan to deploy to `mainnet`, rotate and secure `HEDERA_OPERATOR_KEY` carefully and consider hardware key management.
-   For production scale, run Mirror Node queries against a reliable mirror node endpoint or run your own mirror node for improved SLAs.
-   Consider using Redis or another persistent store for exchange-rate caching and operational metrics.

## Additional documentation

-   Hedera integration guides and developer notes: `docs/HEDERA_WALLET_INTEGRATION.md`, `docs/HEDERA_IMPLEMENTATION.md` (if present), and `docs/PAYMENT_INTEGRATION_GUIDE.md`.

---

If you'd like, I can also add a small example script showing how to call `HederaService.mint_nft()` from the project or add a README badge that shows current CI/test status.
