++
Project Title & Track

---

Ticketio — Backend (NFT Ticketing)  
Track: Hedera NFT & Wallet Integration

## Pitch deck and certification links

-   Pitch deck: (add your pitch deck URL here)
-   Certification / paperwork: (add certification link(s) here)

## Hedera Integration Summary

This repository uses Hedera primarily to issue and manage event tickets as NFTs and to manage user wallets/accounts. Below is a concise summary of which Hedera services and SDK features are used, why they were chosen, and how they are used in the codebase.

1. Hedera Token Service (HTS) — USED

-   What we use HTS for:

    -   Issuing NFT collections that represent ticket series (TokenCreateTransaction with NFT token type).
    -   Minting individual NFTs (tickets) with metadata (TokenMintTransaction). Mint receipts provide serial numbers used as ticket identifiers.
    -   Transferring NFTs between accounts when tickets are transferred or sold (TransferTransaction).
    -   Associating tokens with user accounts before they can receive/hold tokens (TokenAssociateTransaction).

-   Where in the repo:

    -   `app/utils/hedera.py` — primary production HederaService (create/mint/transfer, Token queries).
    -   `hedera_implementations/hedera_corrected.py` — corrected/full implementation used for tests and clarity.
    -   `hedera_implementations/hedera_minimal.py` — lightweight fallback implementation for local testing or minimal environments.

-   Why HTS:
    -   HTS is the native Hedera facility to create and manage fungible and non-fungible tokens. For ticketing, NFTs provide a canonical, transferable asset with on-chain ownership and serial numbers that map directly to tickets.
    -   HTS operations are supported by the Hedera SDKs used in the project (TokenCreateTransaction, TokenMintTransaction, TransferTransaction, TokenAssociateTransaction, TokenNftInfoQuery, TokenInfoQuery).

2. Mirror Node usage

-   The project uses Hedera Mirror Node REST APIs to query token NFT details and perform ownership verification (e.g., `GET /api/v1/tokens/{token_id}/nfts/{serial}`), which provides a reliable read-path for owner information and metadata.

3. Account / Wallet management (non-HTS operations)

-   `app/services/hedera_wallet.py` implements account-level operations:
    -   Creating new Hedera accounts with generated ED25519 key pairs and initial HBAR top-ups (AccountCreateTransaction).
    -   Querying balances (AccountBalanceQuery) and account info (AccountInfoQuery).
    -   Checking sufficient balance prior to performing transactions.

4. Environment & security

-   Required env vars used by Hedera code:

    -   `HEDERA_NETWORK` (testnet | mainnet)
    -   `HEDERA_OPERATOR_ID` (operator account id)
    -   `HEDERA_OPERATOR_KEY` (operator private key)
    -   `HEDERA_MIRROR_NODE_URL` (mirror node base URL)

-   Production notes:
    -   Keep operator keys secure and consider Hardware Security Module (HSM) or KMS for mainnet operator private keys.
    -   Mirror Node queries are used for reads; for high reliability consider a dedicated mirror node or vendor endpoint.

5. Tests and verification

-   Hedera tests live under `tests/hedera/` and include a `test_full_implementation.py` that exercises HTS operations (create/mint/transfer/verify) using the corrected implementation.

Appendix — Quick mapping of HTS SDK classes used

-   TokenCreateTransaction — create NFT collections
-   TokenMintTransaction — mint NFT metadata and get serials
-   TransferTransaction — transfer token ownership
-   TokenAssociateTransaction — allow an account to hold a token
-   TokenNftInfoQuery / TokenInfoQuery — get token/nft data via SDK
-   Mirror Node REST endpoints — ownership verification and NFT metadata reads
