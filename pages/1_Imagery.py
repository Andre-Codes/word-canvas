import streamlit as st
import os
import base64
from pages.utils import gpt_utils as gpt
from pages.utils.web_helpers import generate_response, display_response


def encode_image_prompt(image_file):
    file_ext = image_file.type.split('/')[1]
    # MIME types to file ext. mapping
    mime_to_extension = {
        'jpeg': 'jpg',
        'png': 'png',
        'gif': 'gif',
        'bmp': 'bmp',
        'svg+xml': 'svg',
        'webp': 'webp'
    }
    # Get the MIME type from the type to ext. dict
    file_ext = mime_to_extension.get(file_ext, file_ext)
    # Getting the base64 string
    bytes_data = image_file.read()
    base64_image = base64.b64encode(bytes_data).decode('utf-8')

    return f"data:image/{file_ext};base64,{base64_image}"


def display_picture(image):
    st.divider()
    st.image(image)
    st.divider()


# def get_extracted_edit():
#     extracted_edit = st.text_area(label='Edit extracted text', value=st.session_state.extracted)
#     return extracted_edit

# The ChatEngine system_role var is being used as the 'user' prompt
# for the vision api call

text_prompt = """
Respond with the extracted text from this image. Only the extracted text.
Do not add quotes around the extracted text, or any of your own comments.
"""

api_key = os.environ["OPENAI_API_KEY"]
chat_engine = gpt.ChatEngine(api_key=api_key)

st.title("Snap a Photo")
st.subheader("See your text come to life...")
# start_cam = st.button('Open Camera', key='start_cam')
camera = st.empty()

captured_image = camera.camera_input('Take a picture', disabled=False, key='capture')
extract = st.empty()

# Initialize 'extracted' in session state if not already present
if 'extracted' not in st.session_state:
    st.session_state.extracted = None
if 'extracted_edit' not in st.session_state:
    st.session_state.extracted_edit = None

if captured_image and st.session_state['extracted'] is None:
    # Display prompt box for additional context
    prompt_addition = st.text_area(
        label="Additional context",
        help="Enter additional information as context for the written text.",
        value=""
    )

    if extract.button('Read', key='extract', type='primary'):
        prompt = encode_image_prompt(captured_image)
        # Additional text can be added to 'extracted' to provide extra context for vision API
        extracted = generate_response(
            chat_engine,
            prompt=prompt,
            text_prompt=text_prompt,
            role_context='image_to_text'
        )

        st.session_state.extracted = extracted

        st.subheader("I imagine this...")

        display_response(extracted, download=False)

        st.subheader("...to look like this")

        # Update the extracted text to include additional context from text box
        if prompt_addition:
            extracted = f"""
            Initial context: {prompt_addition} \n\n {extracted} \n\n
            """
        # Append additional notes for image prompt
        extracted = f"""
        {extracted} \n\n Do not add text or words to the image.
        """

        print(extracted)
        image_url = generate_response(
            chat_engine,
            prompt=extracted,
            role_context='text_to_image'
        )
        st.image(image_url)
        # Remove extract button after receiving response
        extract.empty()



