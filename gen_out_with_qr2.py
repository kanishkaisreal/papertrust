from PIL import Image, ImageDraw

def add_qr_code_with_margin(input_image_path, qr_image_path, output_image_path, margin=10, margin_color="black", marker_color="red"):
    """
    Adds a QR code at the bottom of an image with a margin and a corner marker for easier separation.

    :param input_image_path: Path to the input image (e.g., PDF page or image).
    :param qr_image_path: Path to the QR code image.
    :param output_image_path: Path to save the final stitched image.
    :param margin: Height of the margin separating the QR code.
    :param margin_color: Color of the margin (default: "black").
    :param marker_color: Color of the marker for separation (default: "red").
    """
    # Load the input image and QR code
    main_image = Image.open(input_image_path)
    qr_image = Image.open(qr_image_path)

    # Resize the QR code to a width of 25% of the main image
    qr_width = main_image.width // 4
    qr_image = qr_image.resize((qr_width, qr_width))

    # Calculate the total height for the final image
    total_height = margin + main_image.height + qr_image.height + 3 * margin
    total_width = margin + main_image.width + margin
    # Create a blank canvas for the final image
    final_image = Image.new("RGB", (total_width, total_height), "white")

    # Paste the main image onto the canvas
    final_image.paste(main_image, (margin, margin))

    # Draw the margin rectangle
    draw = ImageDraw.Draw(final_image)
    margin_top = main_image.height
    draw.rectangle([margin, margin, (total_width - margin), (margin_top + margin)], outline=margin_color, width=4)
    draw.rectangle([margin,(margin_top + 2*margin), (total_width - margin), (total_height - margin)], outline=margin_color, width=4)

    # Add a small marker rectangle in the top-left corner of the qr code  margin
    marker_size = 10
    draw.rectangle(
   
        [margin, margin_top+margin, margin + marker_size, margin_top+ margin + marker_size],
        fill=marker_color
    )

    # Paste the QR code below the margin
    qr_x = (main_image.width - qr_image.width) // 2
    qr_y = margin_top + 2*margin
    final_image.paste(qr_image, (qr_x, qr_y))

    # Save the final image
    final_image.save(output_image_path)
    print(f"Image with QR code and marker saved to {output_image_path}.")


# Call to generate output file.
if __name__ == "__main__":
    ocr_file_path=r'F:\papertrust\papertrust\ocr_data\pdf_to_ocr.png'
    qr_file_path=r'F:\papertrust\papertrust\results\surya\pdf_to_ocr\encrypted_data_qr.png'
    out_file_path=r'F:\papertrust\papertrust\results\surya\pdf_to_ocr\pdf_to_ocr_0_text_out.png'
    add_qr_code_with_margin(
        input_image_path=ocr_file_path,
        qr_image_path=qr_file_path,
        output_image_path=out_file_path,
        margin=10,  # Adjust margin height as needed
        margin_color="black"  # Adjust margin color if needed
    )