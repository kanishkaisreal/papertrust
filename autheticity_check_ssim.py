import cv2
from skimage.metrics import structural_similarity as ssim

def compare_images(img1_path, img2_path):
    # Read images in grayscale
    img1 = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)

    print(f'Original Image size:{img1.shape}')
    print(f'Rescanned Image size:{img2.shape}')

    # Ensure both images have the same size
    if img1.shape != img2.shape:
        print("Images dont have same dimension trying rescaling.")
        # Get dimensions of the first image
        height, width = img1.shape

        # Resize the second image to match the first image's dimensions
        img2= cv2.resize(img2, (width, height), interpolation=cv2.INTER_AREA)

    # Compute SSIM
    similarity, _ = ssim(img1, img2, full=True)
    return similarity

# Example usage
if __name__ == "__main__":
    recoverd_image_path = r'F:\papertrust\papertrust\results\surya\pdf_to_ocr\pdf_to_ocr_0_text_rev.png'
    decripted_orginial_file_path = r'F:\papertrust\papertrust\results\surya\pdf_to_ocr\pdf_to_ocr_0_text_decrypt.png'
    similarity_score = compare_images(decripted_orginial_file_path,recoverd_image_path)
    print(f"Image Similarity: {similarity_score:}")
