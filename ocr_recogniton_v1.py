from PIL import Image
from surya.recognition import RecognitionPredictor
from surya.detection import DetectionPredictor

import subprocess

def extract_info(command):
    # Define the command and arguments
    # Run the command
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print("Command output:", result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error:", e.stderr)

    print('done')
if __name__ == "__main__":
    print('You are in OCR main loop')
    command = [
        "surya_ocr", 
        "F:\papertrust\papertrust\ocr_data\pdf_to_ocr.png", 
        "--images"
    ]

    command2 = [
        "surya_ocr", 
        "F:\papertrust\papertrust\ocr_data\pdf_to_ocr_0_text_rev.png", 
        "--images"
    ]
    extract_info(command)
