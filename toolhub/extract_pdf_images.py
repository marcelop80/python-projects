import os
import uuid
import zipfile
import fitz
from PIL import Image

def extract_images_from_pdf(file_storage, temp_dir):
    """
    Receives an uploaded PDF from Flask, extracts all images,
    and returns a path to a ZIP file containing all images.

    file_storage: the file object from request.files
    temp_dir: folder where we temporarily save files
    returns: path to the ZIP file
    """

    # Create the temp folder if it doesn't exist yet
    os.makedirs(temp_dir, exist_ok=True)

    # Generate a unique ID so files don't clash between users
    unique_id = str(uuid.uuid4())

    # Save the uploaded PDF to the temp folder
    pdf_path = os.path.join(temp_dir, f'{unique_id}.pdf')
    file_storage.save(pdf_path)

    # Create a subfolder to store the extracted images
    images_dir = os.path.join(temp_dir, unique_id)
    os.makedirs(images_dir, exist_ok=True)

    # Open the PDF with PyMuPDF
    pdf_file = fitz.open(pdf_path)

    # Track how many images we find total
    total_images = 0

    # Iterate through each page
    for page_index in range(len(pdf_file)):
        page = pdf_file.load_page(page_index)
        image_list = page.get_images(full=True)

        for image_index, img in enumerate(image_list, start=1):

            # Get the XREF and extract the image bytes
            xref = img[0]
            base_image = pdf_file.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]

            # Save each image into the images subfolder
            image_name = f"page{page_index + 1}_image{image_index}.{image_ext}"
            image_path = os.path.join(images_dir, image_name)
            with open(image_path, "wb") as image_file:
                image_file.write(image_bytes)

            total_images += 1

    # Close the PDF
    pdf_file.close()

    # Delete the original PDF since we don't need it anymore
    os.remove(pdf_path)

    # If no images were found, return None so Flask can show an error
    if total_images == 0:
        return None

    # Zip all the extracted images into a single file
    zip_path = os.path.join(temp_dir, f'{unique_id}_images.zip')
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for image_name in os.listdir(images_dir):
            zipf.write(os.path.join(images_dir, image_name), image_name)

    # Return the zip path so Flask can send it to the user
    return zip_path