import cv2
import importlib
from surya import image_to_text
from Levenshtein import distance as levenshtein_distance

def extract_text_from_image(image_path):
    """Extract text from an image using Surya-OCR."""
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(f"Error: Unable to load image from {image_path}. Check the file path.")

    # Convert image to grayscale for better OCR accuracy
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Perform OCR using Surya-OCR
    extracted_text = image_to_text(gray)
    
    return extracted_text.strip()

def compare_text_levenshtein(original_text, extracted_text):
    """Compute similarity percentage using Levenshtein Distance."""
    dist = levenshtein_distance(original_text, extracted_text)
    max_len = max(len(original_text), len(extracted_text))
    
    if max_len == 0:
        return 100.0 if original_text == extracted_text else 0.0

    similarity = (1 - dist / max_len) * 100  # Convert to percentage
    return similarity

if __name__ == "__main__":
# Example usage
    recoverd_image_path = r'F:\papertrust\papertrust\results\surya\pdf_to_ocr\pdf_to_ocr_0_text_rev.png'
    decripted_orginial_file_path = r'F:\papertrust\papertrust\results\surya\pdf_to_ocr\pdf_to_ocr_0_text_decrypt.png'

    print(f'Original image: {decripted_orginial_file_path}')
    print(f'Recovered image: {recoverd_image_path}')

    decripted_orginial_text = extract_text_from_image(decripted_orginial_file_path)
    recovered_from_scan_text = extract_text_from_image(recoverd_image_path)
    similarity_score = compare_text_levenshtein(decripted_orginial_text, recovered_from_scan_text)

    print(f"Levenshtein Similarity: {similarity_score:.2f}%")