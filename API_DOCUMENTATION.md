# NFT Ticketing System API Documentation

This document provides comprehensive documentation for all API endpoints in the NFT ticketing system.

## Base URL

```
http://localhost:8000/v1
```

## Authentication

Most endpoints require JWT authentication using Bearer tokens. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

---

## Authentication Endpoints

### 1. Register User

**Endpoint:** `POST /auth/register`

**Description:** Register a new user with their wallet address.

**Authorization:** None required

**Request Headers:**

```
Content-Type: application/json
```

**Request Body:**

```json
{
    "wallet_address": "0x1234567890abcdef1234567890abcdef12345678",
    "name": "John Doe",
    "email": "john@example.com",
    "role": "ATTENDEE"
}
```

**Response (201 Created):**

```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "wallet_address": "0x1234567890abcdef1234567890abcdef12345678",
    "name": "John Doe",
    "email": "john@example.com",
    "role": "ATTENDEE",
    "created_at": "2024-01-15T10:30:00Z",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Background Process:**

1. Validate request data using Pydantic schema
2. Check if wallet address already exists in database
3. Generate UUID for new user
4. Create user record in database with role defaulting to ATTENDEE
5. Generate JWT token with wallet address as subject
6. Return user data with access token

**Error Responses:**

-   `400 Bad Request`: User with wallet address already exists
-   `422 Unprocessable Entity`: Invalid request data

---

### 2. Login User

**Endpoint:** `POST /auth/login`

**Description:** Login with existing wallet address.

**Authorization:** None required

**Request Headers:**

```
Content-Type: application/json
```

**Request Body:**

```json
{
    "wallet_address": "0x1234567890abcdef1234567890abcdef12345678"
}
```

**Response (200 OK):**

```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "wallet_address": "0x1234567890abcdef1234567890abcdef12345678",
    "name": "John Doe",
    "email": "john@example.com",
    "role": "ATTENDEE",
    "created_at": "2024-01-15T10:30:00Z",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Background Process:**

1. Look up user by wallet address in database
2. Verify user exists
3. Generate new JWT token with wallet address as subject
4. Return user data with fresh access token

**Error Responses:**

-   `401 Unauthorized`: Invalid wallet address (user not found)

---

## Event Endpoints

### 3. List All Events (Public)

**Endpoint:** `GET /events`

**Description:** Get list of all active events available for ticket purchase.

**Authorization:** None required

**Request Headers:** None required

**Response (200 OK):**

```json
[
    {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "name": "Summer Music Festival",
        "description": "Annual outdoor music festival",
        "location": "Central Park, NYC",
        "date": "2024-07-15T18:00:00Z",
        "price": 99.99,
        "organizer_id": "550e8400-e29b-41d4-a716-446655440002",
        "token_id": "0.0.12345",
        "created_at": "2024-01-15T10:30:00Z"
    }
]
```

**Background Process:**

1. Initialize EventService dependency
2. Query database for all active events
3. Return list of events with full details

---

### 4. Get Event Details (Public)

**Endpoint:** `GET /events/{event_id}`

**Description:** Get detailed information about a specific event.

**Authorization:** None required

**Request Headers:** None required

**Path Parameters:**

-   `event_id`: UUID of the event

**Response (200 OK):**

```json
{
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "name": "Summer Music Festival",
    "description": "Annual outdoor music festival",
    "location": "Central Park, NYC",
    "date": "2024-07-15T18:00:00Z",
    "price": 99.99,
    "organizer_id": "550e8400-e29b-41d4-a716-446655440002",
    "token_id": "0.0.12345",
    "created_at": "2024-01-15T10:30:00Z"
}
```

**Background Process:**

1. Initialize EventService dependency
2. Query database for event by ID
3. Return event details if found

**Error Responses:**

-   `404 Not Found`: Event not found

---

### 5. Create Event (Organizer Only)

**Endpoint:** `POST /organizer/events`

**Description:** Create a new event and mint NFT collection for tickets.

**Authorization:** Required (Organizer role)

**Request Headers:**

```
Content-Type: application/json
Authorization: Bearer <organizer_jwt_token>
```

**Request Body:**

```json
{
    "name": "Summer Music Festival",
    "description": "Annual outdoor music festival",
    "location": "Central Park, NYC",
    "date": "2024-07-15T18:00:00Z",
    "price": 99.99,
    "ticket_supply": 1000
}
```

**Response (200 OK):**

```json
{
    "event_id": "550e8400-e29b-41d4-a716-446655440001",
    "token_id": "0.0.12345"
}
```

**Background Process:**

1. Verify JWT token and extract user
2. Verify user has ORGANIZER role
3. Generate UUID for new event
4. Create NFT collection on Hedera network:
    - Set collection name and symbol
    - Set total supply based on ticket_supply
    - Set metadata URI pointing to event details
5. Save event to database with generated token_id
6. Return event_id and token_id for reference

**Error Responses:**

-   `401 Unauthorized`: Invalid or missing token
-   `403 Forbidden`: User is not an organizer
-   `500 Internal Server Error`: Failed to create NFT collection

---

### 6. List Organizer Events

**Endpoint:** `GET /organizer/events`

**Description:** Get all events created by the current organizer.

**Authorization:** Required (Organizer role)

**Request Headers:**

```
Authorization: Bearer <organizer_jwt_token>
```

**Response (200 OK):**

```json
[
    {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "name": "Summer Music Festival",
        "description": "Annual outdoor music festival",
        "location": "Central Park, NYC",
        "date": "2024-07-15T18:00:00Z",
        "price": 99.99,
        "organizer_id": "550e8400-e29b-41d4-a716-446655440002",
        "token_id": "0.0.12345",
        "created_at": "2024-01-15T10:30:00Z"
    }
]
```

**Background Process:**

1. Verify JWT token and extract user
2. Verify user has ORGANIZER role
3. Query database for all events where organizer_id matches current user
4. Return list of organizer's events

**Error Responses:**

-   `401 Unauthorized`: Invalid or missing token
-   `403 Forbidden`: User is not an organizer

---

## Ticket Endpoints

### 7. Purchase Ticket

**Endpoint:** `POST /tickets/purchase`

**Description:** Purchase a ticket for an event, minting an NFT and transferring it to buyer.

**Authorization:** Required (Any authenticated user)

**Request Headers:**

```
Content-Type: application/json
Authorization: Bearer <user_jwt_token>
```

**Request Body:**

```json
{
    "event_id": "550e8400-e29b-41d4-a716-446655440001",
    "buyer_wallet": "0x1234567890abcdef1234567890abcdef12345678"
}
```

**Response (200 OK):**

```json
{
    "ticket_id": "550e8400-e29b-41d4-a716-446655440003",
    "token_id": "0.0.12345",
    "serial_number": "1",
    "qr_data": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
}
```

**Background Process:**

1. Verify JWT token and extract user
2. Validate event exists and has available tickets
3. Mint new NFT on Hedera network:
    - Use event's token_id
    - Include event metadata (name, date)
    - Get unique serial number
4. Transfer NFT from treasury to buyer's wallet
5. Create ticket record in database with serial number
6. Generate QR code containing:
    - Token ID
    - Serial number
    - Owner wallet address
7. Return ticket details with QR code

**Error Responses:**

-   `401 Unauthorized`: Invalid or missing token
-   `404 Not Found`: Event not found
-   `400 Bad Request`: Event tickets not available
-   `500 Internal Server Error`: Failed to mint or transfer NFT

---

### 8. List User Tickets

**Endpoint:** `GET /tickets/users/{user_id}/tickets`

**Description:** Get all tickets owned by a specific user.

**Authorization:** Required (User can only view their own tickets)

**Request Headers:**

```
Authorization: Bearer <user_jwt_token>
```

**Path Parameters:**

-   `user_id`: UUID of the user

**Response (200 OK):**

```json
[
    {
        "id": "550e8400-e29b-41d4-a716-446655440003",
        "event_id": "550e8400-e29b-41d4-a716-446655440001",
        "owner_wallet": "0x1234567890abcdef1234567890abcdef12345678",
        "serial_number": "1",
        "status": "ACTIVE",
        "created_at": "2024-01-15T11:00:00Z"
    }
]
```

**Background Process:**

1. Verify JWT token and extract user
2. Verify user is requesting their own tickets (user_id matches token)
3. Query database for all tickets owned by user's wallet address
4. Return list of user's tickets

**Error Responses:**

-   `401 Unauthorized`: Invalid or missing token
-   `403 Forbidden`: User trying to view other user's tickets

---

### 9. Verify Ticket (Staff Only)

**Endpoint:** `POST /tickets/verify`

**Description:** Verify ticket validity and mark as used for event entry.

**Authorization:** Required (Staff role)

**Request Headers:**

```
Content-Type: application/json
Authorization: Bearer <staff_jwt_token>
```

**Request Body:**

```json
{
    "token_id": "0.0.12345",
    "serial_number": "1",
    "wallet_address": "0x1234567890abcdef1234567890abcdef12345678"
}
```

**Response (200 OK):**

```json
{
    "status": "valid",
    "ticket_id": "550e8400-e29b-41d4-a716-446655440003",
    "event_id": "550e8400-e29b-41d4-a716-446655440001",
    "owner_wallet": "0x1234567890abcdef1234567890abcdef12345678"
}
```

**Background Process:**

1. Verify JWT token and extract user
2. Verify user has STAFF role
3. Verify NFT ownership on Hedera network:
    - Check if wallet address owns the NFT with given token_id and serial_number
4. Query database for ticket record
5. Check ticket status (must be ACTIVE)
6. Mark ticket as USED in database
7. Return verification result

**Error Responses:**

-   `401 Unauthorized`: Invalid or missing token
-   `403 Forbidden`: User is not staff
-   Response with `"status": "invalid"` for invalid tickets

---

## User Roles and Permissions

### ATTENDEE

-   Can register and login
-   Can purchase tickets
-   Can view their own tickets

### ORGANIZER

-   All ATTENDEE permissions
-   Can create events
-   Can view their created events

### STAFF

-   All ATTENDEE permissions
-   Can verify tickets at events

---

## Error Handling

All endpoints return appropriate HTTP status codes:

-   `200 OK`: Successful request
-   `201 Created`: Resource created successfully
-   `400 Bad Request`: Invalid request data
-   `401 Unauthorized`: Authentication required or invalid
-   `403 Forbidden`: Insufficient permissions
-   `404 Not Found`: Resource not found
-   `422 Unprocessable Entity`: Validation errors
-   `500 Internal Server Error`: Server-side errors

Error responses include a detail message:

```json
{
    "detail": "Error description"
}
```

---

## JWT Token Structure

Tokens contain:

-   `sub`: Wallet address (subject)
-   `exp`: Expiration timestamp
-   Additional claims as needed

Token expiration is configurable via `ACCESS_TOKEN_EXPIRE_MINUTES` setting.

---

## Blockchain Integration

The system integrates with Hedera Hashgraph for NFT operations:

-   **NFT Collections**: Created for each event
-   **NFT Minting**: Each ticket is a unique NFT
-   **Ownership Verification**: Tickets verified on-chain
-   **Transfer**: NFTs transferred to buyer wallets

All blockchain operations are handled through the Hedera service layer.
