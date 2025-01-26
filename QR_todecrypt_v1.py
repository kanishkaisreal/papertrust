import os
import zlib
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import cv2

# Function to derive a key from a password
def derive_key(password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(password.encode())

# Decrypt the encrypted file
def decrypt_file(encrypted_file, password, output_file):
    with open(encrypted_file, "rb") as f:
        data = f.read()

    salt = data[:16]  # Extract salt
    iv = data[16:32]  # Extract initialization vector
    ciphertext = data[32:]  # Extract the actual encrypted content

    key = derive_key(password, salt)

    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    # Save the decrypted data to the output file
    with open(output_file, "wb") as f:
        f.write(plaintext)

    print(f"Decrypted file saved at {output_file}")

# Read QR code to get the file path
def read_qr_code(qr_file):
    img = cv2.imread(qr_file)
    detector = cv2.QRCodeDetector()
    data, _, _ = detector.detectAndDecode(img)

    if data:
        print(f"QR code data: {data}")
        return data
    else:
        raise ValueError("Failed to read QR code or no data found!")

# Main function
if __name__ == "__main__":
    qr_code_file = "/Users/kanishka/Library/Mobile Documents/com~apple~CloudDocs/" \
        "paperTrust/OCR/results/surya/pdf_to_ocr/encrypted_data_qr.png"

    password = "kt"  # Same password used for encryption
    output_file = "/Users/kanishka/Library/Mobile Documents/com~apple~CloudDocs/" \
        "paperTrust/OCR/results/surya/pdf_to_ocr/decrypted_image.png"

    # Step 1: Read the encrypted file path from the QR code
    encrypted_file = read_qr_code(qr_code_file)

    # Step 2: Decrypt the file to restore the original
    decrypt_file(encrypted_file, password, output_file)

    print("Decryption completed.")
