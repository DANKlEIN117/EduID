import qrcode
import io
from PIL import Image
import os

def generate_qr_code(data, filename):
    """
    Generate QR code and save to file
    
    Args:
        data: Data to encode in QR code (usually student ID number)
        filename: Path to save the QR code image
    
    Returns:
        Path to saved QR code image
    """
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        img.save(filename)
        return filename
    except Exception as e:
        print(f"Error generating QR code: {e}")
        return None


def generate_qr_code_pil(data):
    """
    Generate QR code as PIL Image object (for in-memory use)
    
    Args:
        data: Data to encode in QR code
    
    Returns:
        PIL Image object
    """
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        return img
    except Exception as e:
        print(f"Error generating QR code: {e}")
        return None
