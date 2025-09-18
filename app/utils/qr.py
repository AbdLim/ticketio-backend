import json
import base64
import qrcode
from io import BytesIO
from typing import Dict


class QRService:
    @staticmethod
    def generate_ticket_qr(
        token_id: str, serial_number: str, owner_wallet: str
    ) -> str:
        """
        Generate a QR code for a ticket.

        Args:
            token_id: The Hedera token ID
            serial_number: The NFT serial number
            owner_wallet: The wallet address of the ticket owner

        Returns:
            str: Base64 encoded QR code image
        """
        # Create ticket data
        ticket_data = {
            "token_id": token_id,
            "serial_number": serial_number,
            "owner_wallet": owner_wallet,
            "v": "1",  # Version number for future compatibility
        }

        # Convert to JSON string
        json_data = json.dumps(ticket_data)

        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(json_data)
        qr.make(fit=True)

        # Create image
        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()

    @staticmethod
    def decode_ticket_qr(qr_data: str) -> Dict[str, str]:
        """
        Decode a ticket QR code.

        Args:
            qr_data: Base64 encoded QR code data

        Returns:
            Dict[str, str]: Decoded ticket data containing token_id,
                           serial_number, and owner_wallet
        """
        try:
            # Decode base64
            decoded_bytes = base64.b64decode(qr_data)

            # Parse JSON
            ticket_data = json.loads(decoded_bytes.decode())

            # Validate required fields
            required_fields = ["token_id", "serial_number", "owner_wallet"]
            if not all(field in ticket_data for field in required_fields):
                raise ValueError("Invalid ticket QR code: missing required fields")

            return ticket_data
        except Exception as e:
            raise ValueError(f"Failed to decode QR code: {str(e)}")


# Create a singleton instance
qr_service = QRService()
