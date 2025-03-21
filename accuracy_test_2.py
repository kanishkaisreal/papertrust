import os
import zlib
import base64
import cv2
from extract_qr_v1 import extract_qr_code 
from capture_validation_doc import recover_image_from_scan
from autheticity_check_ssim import compare_images
from QR_todecrypt_v2 import decrypt_file
from ocr_recogniton_v1 import extract_info
import shutil
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Main function
if __name__ == "__main__":
    #qr_code_file = "/Users/kanishka/Library/Mobile Documents/com~apple~CloudDocs/" \
    #    "paperTrust/OCR/results/surya/pdf_to_ocr/encrypted_data_qr.png"
    
    
    recoverd_image_path = r'F:\papertrust\papertrust\ocr_data\pdf_to_ocr_0_text_rev.png'
    sury_recovered_image_path = r'F:\papertrust\papertrust\results\surya\pdf_to_ocr_0_text_rev\pdf_to_ocr_0_text_rev_0_text.png'
    recovered_qrcode_path = r'F:\papertrust\papertrust\results\surya\pdf_to_ocr\pdf_to_ocr_0_text_qr_rev.png'
    decripted_orginial_file_path = r'F:\papertrust\papertrust\results\surya\pdf_to_ocr\pdf_to_ocr_0_text_decrypt.png'
    run_path = r'F:\papertrust\papertrust\ocr_data\accuracy\run_'
    
    

    #extract information from the recovered image
    # Run surya ocr on the recovered image
    # for count in range(1,11):
    #     scanned_image_path = f'F:\papertrust\papertrust\ocr_data\pdf_to_ocr_0_text_out_scan_{count}.png'
    #     print(f'Scanning image: {scanned_image_path}')
    #     recover_image_from_scan(input_image_path=scanned_image_path, output_image1_path=recoverd_image_path, output_image2_path=recovered_qrcode_path)

    #     command = [
    #         "surya_ocr", 
    #         recoverd_image_path, 
    #         "--images"
    #     ]
    #     extract_info(command)
    

    #     # Copy file to a new file with a different name
    #     shutil.copy(sury_recovered_image_path, f'{run_path}{count}.png')
    #     os.remove(sury_recovered_image_path)

    # Initialize a matrix for similarity scores
    scores = np.zeros((10, 10))
    for i in range(1,11):
        for j in range(1,11):

            similarity_score = compare_images(f'{run_path}{i}.png', f'{run_path}{j}.png')
            print(f"Similarity: {similarity_score:}%")
            scores[i-1, j-1] = similarity_score
plt.figure(figsize=(10, 8))
sns.heatmap(scores, annot=True, cmap='YlGnBu', fmt='.2f', xticklabels=range(1, 11), yticklabels=range(1, 11))
plt.title('Image Similarity Score (%)')
plt.xlabel('Run j')
plt.ylabel('Run i')
plt.show()

