# NFT Ticketing API Specification

Backend for a mobile application that handles NFT-based event ticketing on **Hedera**.

---

## 🛠 Tech Stack

-   **Framework:** FastAPI (Python)
-   **Web Server:** Uvicorn
-   **Database:** PostgreSQL (via SQLAlchemy + Alembic)
-   **Hedera Integration:** [Hiero SDK for Python](https://pypi.org/project/hiero-sdk-python/) (community-maintained)
-   **Auth:** JWT (via `python-jose` or `fastapi-jwt-auth`)
-   **Environment Management:** python-dotenv
-   **QR Code Generation:** `qrcode` or `segno` Python package

### Install Base Dependencies

```bash
pip install hiero-sdk-python python-jose[cryptography] qrcode
```

---

## 📦 Features

-   **User management**: Register/login with wallet address.
-   **Organizer events**: Create events, mint NFT tickets.
-   **Attendee**: Browse events, purchase tickets (NFT transfer).
-   **Ticket verification**: QR-based ownership check using Hedera Mirror Node.
-   **My tickets**: View all owned tickets.

---

## 🗂 Data Models

### User

| Field          | Type     | Notes                              |
| -------------- | -------- | ---------------------------------- |
| id (UUID)      | PK       |                                    |
| name           | string   | optional                           |
| email          | string   | optional                           |
| wallet_address | string   | Hedera public key                  |
| role           | enum     | `attendee` / `organizer` / `staff` |
| created_at     | datetime |                                    |

### Event

| Field        | Type     | Notes                         |
| ------------ | -------- | ----------------------------- |
| id (UUID)    | PK       |                               |
| organizer_id | FK->User |                               |
| name         | string   |                               |
| description  | text     |                               |
| location     | string   |                               |
| date         | datetime |                               |
| price        | decimal  | ticket price                  |
| token_id     | string   | Hedera Token ID after minting |
| created_at   | datetime |                               |

### Ticket

| Field         | Type      | Notes                    |
| ------------- | --------- | ------------------------ |
| id (UUID)     | PK        |                          |
| event_id      | FK->Event |                          |
| owner_wallet  | string    |                          |
| serial_number | string    | Hedera NFT serial number |
| status        | enum      | `active` / `used`        |
| created_at    | datetime  |                          |

---

## 🌐 Endpoints

### Auth

-   `POST /auth/register`

    -   **Request:** `{ "wallet_address": "...", "name": "...", "email": "...", "role": "attendee|organizer|staff" }`
    -   **Response:** `{"user_id": "...", "token": "jwt"}`

-   `POST /auth/login`
    -   **Request:** `{ "wallet_address": "..." }`
    -   **Response:** `{ "user_id": "...", "token": "jwt" }`

---

### Events (Public)

-   `GET /events`

    -   Lists all events.
    -   **Response:** `[{"id": "...", "name": "...", "date": "...", "location": "...", "price": ..., "token_id": "..."}]`

-   `GET /events/{id}`
    -   Returns single event details.

---

### Organizer

-   `POST /organizer/events`

    -   Creates event and mints NFT collection on Hedera.
    -   **Request:**
        ```json
        {
            "name": "Event name",
            "description": "Event description",
            "date": "2025-09-14T18:00:00Z",
            "location": "Abuja",
            "price": 10.5,
            "ticket_supply": 100
        }
        ```
    -   **Response:**
        ```json
        { "event_id": "...", "token_id": "0.0.xxxxx" }
        ```

-   `GET /organizer/events`
    -   Lists events created by the organizer.

---

### Ticket Purchase

-   `POST /tickets/purchase`

    -   Transfers an NFT ticket to buyer.
    -   **Request:** `{ "event_id": "...", "buyer_wallet": "..." }`
    -   **Backend action:**
        -   Use Hiero SDK to transfer NFT (token_id + next serial number) to `buyer_wallet`.
        -   Save ticket record in DB.
        -   Generate QR code string containing `{token_id,serial_number,owner_wallet}`.
    -   **Response:**
        ```json
        {
            "ticket_id": "...",
            "token_id": "0.0.xxxxx",
            "serial_number": "1234",
            "qr_data": "base64-encoded"
        }
        ```

-   `GET /users/{id}/tickets`
    -   Lists all tickets owned by the user.

---

### Verification (Event Staff)

-   `POST /tickets/verify`
    -   Validates ticket ownership.
    -   **Request:** `{ "token_id": "0.0.xxxxx", "serial_number": "1234", "wallet_address": "..." }`
    -   **Backend action:**
        -   Query Hedera Mirror Node API to confirm that `wallet_address` owns NFT `token_id` with `serial_number`.
    -   **Response:** `{ "status": "valid", "ticket_id": "...", "event_id": "...", "owner_wallet": "..." }`

---

## 📝 Notes for Implementation

-   Store only **public keys/wallet addresses** in DB; private keys and seed phrases stay on the client side.
-   Use JWT for authenticated endpoints (organizer creating events, ticket purchase).
-   Wrap Hedera calls (mint, transfer, verify) in separate service modules.

---

## 🚀 Next Steps for Codegen

1. Scaffold FastAPI project with these routes and Pydantic models.
2. Add SQLAlchemy models for `User`, `Event`, `Ticket`.
3. Integrate Hiero SDK in a service class `hedera_service.py` for NFT operations.
4. Add QR generation utility `qr_service.py`.
5. Configure Alembic migrations and .env file with database + Hedera credentials.
