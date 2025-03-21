from PIL import Image
def color_match(pixel, marker_color, tolerance=100):
    return all(abs(pixel[i] - marker_color[i]) <= tolerance for i in range(3))


def recover_image_from_scan(input_image_path, output_image1_path, output_image2_path, marker_color=(255, 0, 0), margin=10):
    """
    Splits an image into two parts using a corner marker in the margin.

    :param input_image_path: Path to the input image containing the marker.
    :param output_image1_path: Path to save the first box (main content).
    :param output_image2_path: Path to save the second box (QR code).
    :param marker_color: RGB color of the corner marker (default: red).
    :param margin: Margin height to identify the splitting region.
    """
    # Load the input image
    input_image = Image.open(input_image_path)
    pixels = input_image.load()
    print(input_image_path)

    # Detect the marker rectangle based on its color
    width, height = input_image.size
    marker_found = False

    for y in range(height):
        for x in range(margin-10, margin + 25):  # Only check the margin area
            if color_match(pixels[x, y], marker_color):
                marker_found = True
                marker_y = y
                marker_x = x
                break
        if marker_found:
            print(f'marker X={x}, Y={y}')
            break

    if not marker_found:
        raise ValueError("No corner marker found to determine the split.")

    # Define the main content and QR code areas
    first_box = (marker_x, marker_x, width-marker_x, marker_y)
    second_box = (marker_x, marker_y + marker_x, width-marker_x, height-marker_x)

    # Crop the images
    first_image = input_image.crop(first_box)
    second_image = input_image.crop(second_box)
    print(first_image.size)

    # Save the cropped images
    first_image.save(output_image1_path)
    second_image.save(output_image2_path)

    print(f"Main content saved to {output_image1_path}")
    print(f"QR code saved to {output_image2_path}")


if __name__ == "__main__":
    # Call the function to split the image
    input_image_path = r'F:\papertrust\papertrust\ocr_data\pdf_to_ocr_0_text_out_scan.png'
    #input_image_path = r'F:\papertrust\papertrust\results\surya\pdf_to_ocr\pdf_to_ocr_0_text_out.png'
    output_image1_path = r'F:\papertrust\papertrust\results\surya\pdf_to_ocr\pdf_to_ocr_0_text_rev.png'
    output_image2_path = r'F:\papertrust\papertrust\results\surya\pdf_to_ocr\pdf_to_ocr_0_text_qr_rev.png'

    recover_image_from_scan(
        input_image_path=input_image_path,
        output_image1_path=output_image1_path,
        output_image2_path=output_image2_path
    )