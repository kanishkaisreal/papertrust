import os
import zlib
import base64
import cv2
from extract_qr_v1 import extract_qr_code 
from capture_validation_doc import recover_image_from_scan
from autheticity_check_ssim import compare_images
from QR_todecrypt_v2 import decrypt_file
from ocr_recogniton_v1 import extract_info

# Main function
if __name__ == "__main__":
    #qr_code_file = "/Users/kanishka/Library/Mobile Documents/com~apple~CloudDocs/" \
    #    "paperTrust/OCR/results/surya/pdf_to_ocr/encrypted_data_qr.png"
    
    scanned_image_path = r'F:\papertrust\papertrust\ocr_data\pdf_to_ocr_0_text_out_scan_5.png'
    recoverd_image_path = r'F:\papertrust\papertrust\ocr_data\pdf_to_ocr_0_text_rev.png'
    sury_recovered_image_path = r'F:\papertrust\papertrust\results\surya\pdf_to_ocr_0_text_rev\pdf_to_ocr_0_text_rev_0_text.png'
    recovered_qrcode_path = r'F:\papertrust\papertrust\results\surya\pdf_to_ocr\pdf_to_ocr_0_text_qr_rev.png'
    decripted_orginial_file_path = r'F:\papertrust\papertrust\results\surya\pdf_to_ocr\pdf_to_ocr_0_text_decrypt.png'
    
    recover_image_from_scan(input_image_path=scanned_image_path, output_image1_path=recoverd_image_path, output_image2_path=recovered_qrcode_path)

    #extract information from the recovered image
    # Run surya ocr on the recovered image
    print('Trying to run Surya OCR')
    command = [
        "surya_ocr", 
        recoverd_image_path, 
        "--images"
    ]
    extract_info(command)



    

    password = "kt"  # Same password used for encryption
    #output_file = "/Users/kanishka/Library/Mobile Documents/com~apple~CloudDocs/" \
    #    "paperTrust/OCR/results/surya/pdf_to_ocr/decrypted_image.png"

    # Step 1: Read the encrypted file path from the QR code
    #encrypted_file = read_qr_code(qr_code_file)
    encrypted_file = extract_qr_code(recovered_qrcode_path)

    # Step 2: Decrypt the file to restore the original
    decrypt_file(encrypted_file, password, decripted_orginial_file_path)

    print("Decryption completed.")

    # Step 3: Compare decripted file with recovered file
    #TODO

    print(f'Original image:{decripted_orginial_file_path}')
    print(f'Recovered image:{sury_recovered_image_path}')


    similarity_score = compare_images(decripted_orginial_file_path, sury_recovered_image_path)

    print(f"Similarity: {similarity_score:}%")


