import os
import zlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import base64
import qrcode

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

# Encrypt the file
def encrypt_file(input_file, password, output_file):
    salt = os.urandom(16)  # Random salt
    key = derive_key(password, salt)
    iv = os.urandom(16)  # Initialization vector

    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    with open(input_file, "rb") as f:
        plaintext = f.read()

    ciphertext = encryptor.update(plaintext) + encryptor.finalize()

    # Save encrypted data to file
    with open(output_file, "wb") as f:
        f.write(salt + iv + ciphertext)

    print(f"Encrypted file saved at {output_file}")

# Generate a QR code with the file path
def generate_qr_code(data, qr_file):
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill="black", back_color="white")
    img.save(qr_file)
    print(f"QR code saved at {qr_file}")

# Main function
if __name__ == "__main__":
    #input_file = "F:/papertrust/papertrust/results/qr_code/surya/pdf_to_ocr/pdf_to_ocr_0_text.png" 
    input_file = r'F:\papertrust\papertrust\results\surya\pdf_to_ocr\pdf_to_ocr_0_text.png'
    
    print(f'your file path name is:{input_file}')

    encrypted_file = r'F:\papertrust\papertrust\results\surya\pdf_to_ocr\encrypted_data.enc'


    qr_code_file = r'F:\papertrust\papertrust\results\surya\pdf_to_ocr\encrypted_data_qr.png'

    password = "kt"  # Choose a strong password

    # Encrypt the file and save it
    encrypt_file(input_file, password, encrypted_file)

    # Generate a QR code with the file path
    generate_qr_code(encrypted_file, qr_code_file)

    print("done")
