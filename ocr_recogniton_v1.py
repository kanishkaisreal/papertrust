from PIL import Image
from surya.recognition import RecognitionPredictor
from surya.detection import DetectionPredictor

import subprocess

# Define the command and arguments
command = [
    "surya_ocr", 
    "/Users/kanishka/Library/Mobile Documents/com~apple~CloudDocs/paperTrust/OCR/ocr_data/pdf_to_ocr.png", 
    "--images"
]

# Run the command
try:
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    print("Command output:", result.stdout)
except subprocess.CalledProcessError as e:
    print("Error:", e.stderr)

print('done')