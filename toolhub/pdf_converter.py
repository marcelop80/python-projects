import os
import uuid
from pdf2docx import Converter

def convert_pdf_to_word(file_storage, temp_dir):
    """
    Receives an uploaded file from Flask and converts it to .docx
    
    file_storage: the file object from request.files
    temp_dir: folder where we temporarily save files
    returns: path to the converted .docx file
    """
    
    # Create the temp folder if it doesn't exist yet
    os.makedirs(temp_dir, exist_ok=True)

    # Generate a unique ID so files don't overwrite each other
    unique_id = str(uuid.uuid4())

    # Build the full path for the uploaded PDF and the output docx
    pdf_path  = os.path.join(temp_dir, f'{unique_id}.pdf')
    docx_path = os.path.join(temp_dir, f'{unique_id}.docx')

    # Save the uploaded file to the temp folder
    file_storage.save(pdf_path)

    # Run the conversion (your original logic)
    cv = Converter(pdf_path)
    cv.convert(docx_path)
    cv.close()

    # Delete the original PDF since we don't need it anymore
    os.remove(pdf_path)

    # Return the path of the converted file so Flask can send it to the user
    return docx_path