import streamlit as st
import os
import base64
from pages.utils import gpt_utils as gpt
from pages.utils.web_helpers import generate_response, display_response

# Initialize 'extracted' in session state if not already present
if 'extracted' not in st.session_state:
    st.session_state.extracted = None
if 'extracted_edit_prompt' not in st.session_state:
    st.session_state.extracted_edit_prompt = None
if 'image_url' not in st.session_state:
    st.session_state.image_url = None
if 'gen_images' not in st.session_state:
    st.session_state.gen_images = []


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


def display_history():
    for i, image in enumerate(st.session_state.gen_images, start=1):
        expander1 = st.sidebar.expander(f"Image #{i}: {image[1][:40]}...")
        expander1.image(image[0])
        expander1.write(image[1])
        st.sidebar.divider()
        # Tab history
        with tab2:
            st.image(image[0])
            expander2 = st.expander(f"{image[1][:60]}...")
            expander2.write(image[1])


# def handle_response(response):
#     st.write(response)
#     try:
#         json_data = json.loads(response)
#         st.write(f"json_Data: {json_data}")
#         text = json_data.get('extracted', 'No text found')
#         text_title = json_data.get('title', 'No title found')
#         return text, text_title
#     except json.JSONDecodeError:
#         raise

# Begin web app widgets
st.title("Imagine Eyes")

tab1, tab2 = st.tabs(["Capture", "History"])

tab1.header("Capture Text", divider='rainbow')
tab2.header("Imagined History", divider='rainbow')

text_prompt = """
Extract the text words from the following image.
Do not add quotes around the extracted text, or add any of your own comments.
"""

api_key = os.environ["OPENAI_API_KEY"]
chat_engine = gpt.ChatEngine(api_key=api_key)

#
if st.session_state.extracted:
    display_history()

with tab1:
    # start_cam = st.button('Open Camera', key='start_cam')
    camera = st.empty()

    captured_image = camera.camera_input('Take a picture', disabled=False, key='capture')
    extract = st.empty()

    if captured_image:
        # Display prompt box for additional context

        if extract.button('Read', key='extract'):
            prompt = encode_image_prompt(captured_image)

            try:
                extracted = generate_response(
                    chat_engine,
                    prompt=prompt,
                    text_prompt=text_prompt,
                    role_context='image_to_text'
                )

                st.session_state.extracted = extracted

                # REMOVED DISPLAY RESPONSE

                # Remove extract button after receiving response
                extract.empty()
            except Exception as e:
                st.error(e)

with tab1:
    if st.session_state.extracted and captured_image:
        extracted_edit_box = st.empty()

        prompt_context = st.text_input(
            label="Image Context",
            help="Enter additional information as context for the scanned text.",
            value=""
        )
        #
        prompt_restrictions = st.text_input(
            label="Image Restrictions",
            help="Enter anything you **do not** want included in the image.",
            value=""
        )

        extracted_edit = extracted_edit_box.text_area(
            label="Extracted text",
            help="",
            value=st.session_state.extracted
        )

        st.session_state.extracted_edit_display = extracted_edit

        # Update the extracted text to include additional context from text box
        if prompt_context:
            extracted_edit = f"Image context: {prompt_context} \n\n {extracted_edit} \n\n"

        if prompt_restrictions:
            extracted_edit = f"Image Restrictions: {prompt_restrictions} \n\n {extracted_edit} \n\n"

        st.session_state.extracted_edit_prompt = extracted_edit

        # # Append additional notes for image prompt
        # extracted = f"Restrictions: do not add text or words to the image. \n\n{extracted}"
        print(st.session_state.extracted_edit_prompt)

with tab1:
    if st.session_state.extracted_edit_prompt and captured_image:
        submit = st.empty()
        if submit.button('Imagine', type='primary'):
            image_url = generate_response(
                chat_engine,
                prompt=st.session_state.extracted_edit_prompt,
                role_context='text_to_image',
            )

            st.session_state.image_url = image_url

            st.subheader("I imagine this...")
            display_response(st.session_state.extracted_edit_display, download=False)

            st.subheader("...to look like this")
            st.image(image_url)

            st.session_state.gen_images.append((image_url, st.session_state.extracted_edit_display))
            # clear widgets
            submit.empty()
