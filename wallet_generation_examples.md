# Wallet Generation for NFT Ticketing Platform

## Option 1: Client-Side Wallet Generation (Recommended)

### JavaScript/TypeScript (Frontend)

```javascript
// Using ethers.js for Ethereum-compatible wallets
import { ethers } from "ethers";

// Generate a new wallet
function generateWallet() {
    const wallet = ethers.Wallet.createRandom();

    return {
        address: wallet.address,
        privateKey: wallet.privateKey,
        mnemonic: wallet.mnemonic.phrase,
    };
}

// Example usage
const newWallet = generateWallet();
console.log("Address:", newWallet.address);
console.log("Private Key:", newWallet.privateKey);
console.log("Mnemonic:", newWallet.mnemonic);
```

### For Hedera Specifically

```javascript
// Using @hashgraph/sdk for Hedera wallets
import { PrivateKey, AccountId } from "@hashgraph/sdk";

function generateHederaWallet() {
    const privateKey = PrivateKey.generateED25519();
    const publicKey = privateKey.publicKey;

    return {
        privateKey: privateKey.toString(),
        publicKey: publicKey.toString(),
        // Note: Account ID needs to be created on Hedera network
        // This requires a transaction with HBAR for account creation
    };
}
```

## Option 2: Server-Side Wallet Generation (Less Secure)

If you need server-side generation, here's how to implement it securely:

### Python Implementation

```python
# requirements.txt additions:
# cryptography==41.0.7
# mnemonic==0.20
# ecdsa==0.18.0

import secrets
import hashlib
from mnemonic import Mnemonic
from ecdsa import SigningKey, SECP256k1
from ecdsa.util import string_to_number
import binascii

class WalletGenerator:
    def __init__(self):
        self.mnemo = Mnemonic("english")

    def generate_wallet(self):
        """Generate a new wallet with mnemonic phrase"""
        # Generate entropy (128 bits = 12 words, 256 bits = 24 words)
        entropy = secrets.token_bytes(32)  # 256 bits for 24 words

        # Generate mnemonic
        mnemonic_phrase = self.mnemo.to_mnemonic(entropy)

        # Generate seed from mnemonic
        seed = self.mnemo.to_seed(mnemonic_phrase)

        # Generate private key from seed (simplified)
        private_key_bytes = hashlib.sha256(seed[:32]).digest()

        # Create signing key
        signing_key = SigningKey.from_string(private_key_bytes, curve=SECP256k1)

        # Get public key
        verifying_key = signing_key.verifying_key
        public_key_bytes = verifying_key.to_string("compressed")

        # Generate Ethereum-style address
        address = self._generate_eth_address(public_key_bytes)

        return {
            "address": address,
            "private_key": "0x" + binascii.hexlify(private_key_bytes).decode(),
            "public_key": "0x" + binascii.hexlify(public_key_bytes).decode(),
            "mnemonic": mnemonic_phrase
        }

    def _generate_eth_address(self, public_key_bytes):
        """Generate Ethereum-style address from public key"""
        # Remove the first byte (compression flag) for uncompressed key
        if len(public_key_bytes) == 33:  # compressed
            # For simplicity, using a hash-based approach
            address_bytes = hashlib.sha256(public_key_bytes).digest()[-20:]
        else:
            address_bytes = hashlib.sha256(public_key_bytes).digest()[-20:]

        return "0x" + binascii.hexlify(address_bytes).decode()

# Usage
generator = WalletGenerator()
wallet = generator.generate_wallet()
```

## Option 3: Integration with Existing Wallet Providers

### MetaMask Integration (Frontend)

```javascript
// Check if MetaMask is installed
if (typeof window.ethereum !== "undefined") {
    // Request account access
    async function connectWallet() {
        try {
            const accounts = await window.ethereum.request({
                method: "eth_requestAccounts",
            });
            return accounts[0]; // User's wallet address
        } catch (error) {
            console.error("User rejected connection");
        }
    }
}
```

### WalletConnect Integration

```javascript
import WalletConnect from "@walletconnect/client";
import QRCodeModal from "@walletconnect/qrcode-modal";

const connector = new WalletConnect({
    bridge: "https://bridge.walletconnect.org",
    qrcodeModal: QRCodeModal,
});

// Connect to wallet
if (!connector.connected) {
    connector.createSession();
}
```

## Recommended Implementation for Your Platform

Based on your current setup, here's what I recommend:

### 1. Update Registration Endpoint

```python
# Add to app/api/v1/auth.py

from typing import Optional
from app.utils.wallet import WalletGenerator

@router.post("/register-with-wallet", response_model=UserWithToken)
async def register_with_generated_wallet(
    user_create: UserCreateWithoutWallet,  # New schema without wallet_address
    db: Annotated[AsyncSession, Depends(get_session)],
):
    """
    Register a new user and generate a wallet for them.
    WARNING: This stores private keys server-side. Use only for demo purposes.
    """
    # Generate wallet
    wallet_gen = WalletGenerator()
    wallet_data = wallet_gen.generate_wallet()

    # Create user with generated wallet
    user_dict = user_create.model_dump()
    user_dict["id"] = str(uuid4())
    user_dict["wallet_address"] = wallet_data["address"]

    user_repo = UserRepository(db)
    user = await user_repo.create(user_dict)

    # Create access token
    token = create_access_token(user.wallet_address)

    return UserWithWalletToken(
        id=user.id,
        wallet_address=user.wallet_address,
        name=user.name,
        email=user.email,
        role=user.role,
        created_at=user.created_at,
        token=token,
        private_key=wallet_data["private_key"],  # Only return once!
        mnemonic=wallet_data["mnemonic"]  # Only return once!
    )
```

### 2. Create Wallet Utility

```python
# Create app/utils/wallet.py

import secrets
import hashlib
from mnemonic import Mnemonic
import binascii
from typing import Dict

class WalletGenerator:
    def __init__(self):
        self.mnemo = Mnemonic("english")

    def generate_wallet(self) -> Dict[str, str]:
        """Generate a new wallet with mnemonic phrase"""
        entropy = secrets.token_bytes(32)
        mnemonic_phrase = self.mnemo.to_mnemonic(entropy)
        seed = self.mnemo.to_seed(mnemonic_phrase)

        # Simple private key generation (use proper derivation in production)
        private_key_bytes = hashlib.sha256(seed[:32]).digest()

        # Generate address (simplified)
        address_bytes = hashlib.sha256(private_key_bytes).digest()[-20:]
        address = "0x" + binascii.hexlify(address_bytes).decode()

        return {
            "address": address,
            "private_key": "0x" + binascii.hexlify(private_key_bytes).decode(),
            "mnemonic": mnemonic_phrase
        }
```

### 3. Add Required Dependencies

```bash
pip install mnemonic cryptography ecdsa
```

## Security Considerations

1. **Never store private keys in your database** - Only return them once during registration
2. **Use HTTPS** - Always encrypt data in transit
3. **Client-side generation is safer** - Private keys never leave user's device
4. **Backup responsibility** - Users must save their mnemonic phrases
5. **Consider hardware wallets** - For high-value transactions

## Recommended Flow

1. **Frontend generates wallet** using ethers.js or similar
2. **User saves mnemonic phrase** securely
3. **Only wallet address** is sent to your backend
4. **Backend never sees private keys**

This approach gives users full control over their funds while keeping your platform secure.

Would you like me to implement any of these approaches in your codebase?
