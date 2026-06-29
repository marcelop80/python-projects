import os
import uuid
from gtts import gTTS

def convert_text_to_audiobook(file_storage, temp_dir):
    """
    Receives an uploaded .txt file from Flask, converts it to an MP3 audiobook.

    file_storage: the file object from request.files
    temp_dir: folder where we temporarily save files
    returns: path to the MP3 file
    """

    # Create the temp folder if it doesn't exist yet
    os.makedirs(temp_dir, exist_ok=True)

    # Generate a unique ID so files don't clash between users
    unique_id = str(uuid.uuid4())

    # Save the uploaded .txt file to the temp folder
    txt_path = os.path.join(temp_dir, f'{unique_id}.txt')
    file_storage.save(txt_path)

    # Read the text content from the saved file
    with open(txt_path, "r", encoding="utf-8") as f:
        text = f.read()

    # If the file is empty, return None so Flask can show an error
    if not text.strip():
        os.remove(txt_path)
        return None

    # Convert the text to audio using gTTS
    audio = gTTS(text, lang="en")

    # Save the MP3 to the temp folder
    mp3_path = os.path.join(temp_dir, f'{unique_id}.mp3')
    audio.save(mp3_path)

    # Delete the original text file since we don't need it anymore
    os.remove(txt_path)

    # Return the MP3 path so Flask can send it to the user
    return mp3_path