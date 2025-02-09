import qrcode
from PIL import Image
import cv2
from pyzbar.pyzbar import decode

def extract_qr_code(qr_file):
    image = cv2.imread(qr_file)
    decoded_objects = decode(image)
    
    if decoded_objects:
        return decoded_objects[0].data.decode("utf-8")
    else:
        return "No QR code found"

# Extract information from QR code
if __name__ == "__main__":
    output_image2_path = r'F:\papertrust\papertrust\results\surya\pdf_to_ocr\pdf_to_ocr_0_text_qr_rev.png'
    qr_data = extract_qr_code(output_image2_path)
    print("Extracted QR Code Data:", qr_data)
