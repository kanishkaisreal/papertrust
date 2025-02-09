from PIL import Image
from surya.recognition import RecognitionPredictor
from surya.detection import DetectionPredictor

def extract_text_from_image(image_path):
    """Extract text from an image using Surya-OCR."""
    image = Image.open(image_path)

    # Initialize Surya-OCR predictors
    recognition_predictor = RecognitionPredictor()
    detection_predictor = DetectionPredictor()

    # Perform OCR
    predictions = recognition_predictor([image], [None], detection_predictor)

    # Extract text from predictions
    extracted_text = " ".join([line['text'] for page in predictions for line in page["text_lines"]])
    return extracted_text.strip()

# Example usage
image_path = r'F:\papertrust\papertrust\results\surya\pdf_to_ocr\pdf_to_ocr_0_text.png'  # Replace with your actual image file
text = extract_text_from_image(image_path)
print("Extracted Text:", text)
