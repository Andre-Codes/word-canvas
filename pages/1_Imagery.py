import streamlit as st
import zipfile
import os
from fpdf import FPDF
import base64
import requests
import io
import tempfile
from pages.utils import gpt_utils as gpt
from pages.utils.web_helpers import generate_response, display_response


st.set_page_config(page_title="Word Canvas")
# Initialize 'extracted' in session state if not already present
if 'extracted_text' not in st.session_state:
    st.session_state.extracted_text = None
if 'extract_button' not in st.session_state:
    st.session_state.extract_button = None
if 'image_url' not in st.session_state:
    st.session_state.image_url = None
if 'gen_images' not in st.session_state:
    st.session_state.gen_images = []
if 'art_style_filter' not in st.session_state:
    st.session_state.art_style_filter = None

art_formats = [
    "logo", "movie poster", "album cover", "book cover", "magazine cover", "flyer", "brochure", "infographic",
    "business card", "banner", "billboard", "postcard", "invitation", "greeting card", "calendar design",
    "product packaging", "label design", "menu design", "webpage design", "app interface", "icon design",
    "comic strip", "graphic novel illustration", "storybook illustration", "concept art piece", "character sketch",
    "environment artwork", "storyboard art", "portrait illustration", "landscape painting", "still life artwork",
    "abstract art piece", "mural design", "street art creation", "digital artwork", "vector illustration",
    "pixel art creation", "typographic artwork", "motion graphic design", "3D artwork", "3D render",
    "augmented reality scene", "virtual reality environment", "interactive art piece", "user interface mockup",
    "user experience design", "data visualization graphic", "architectural illustration", "fashion illustration",
    "textile design", "jewelry design sketch", "automotive artwork", "game concept art", "level design illustration",
    "emote artwork", "tattoo design", "ceramic art design", "sculpture model", "installation art concept",
    "performance art visualization", "collage artwork", "photo manipulation art", "photo collage design",
    "conceptual photo art", "landscape photo art", "portrait photo art", "wildlife photo art",
    "sports photo art", "astro photo art", "underwater photo art", "street photo art",
    "documentary photo art", "fine art photography", "experimental photo art", "time-lapse photo art",
    "panoramic photo art", "high-speed photo art", "macro photo art", "medical illustration",
    "scientific illustration", "technical drawing", "blueprint design", "map artwork",
    "historical art reconstruction", "anatomical illustration", "botanical illustration", "infographic design",
    "educational illustration", "event ticket design", "postage stamp design", "currency artwork",
    "coin design", "trading card design", "board game artwork", "puzzle artwork", "diploma/certificate design",
    "campaign poster design", "political cartoon", "memorial plaque artwork", "signage design",
    "wallpaper design", "fabric pattern design", "apparel graphic design", "shoe artwork",
    "custom vehicle artwork", "luggage artwork", "furniture design", "interior decor artwork",
    "lighting artwork", "stage design concept", "exhibit design concept", "storefront artwork"
]

art_styles = [
    "realistic", "cartoon", "watercolor", "oil painting", "sketch", "surreal", "impressionist", "cubist",
    "abstract expressionist", "baroque", "rococo", "gothic", "digital art", "pop art", "folk art",
    "art nouveau", "art deco", "graffiti", "minimalist art", "conceptual art", "pointillism", "fauvism",
    "expressionism", "neoclassicism", "primitivism", "dadaism", "futurism", "constructivism", "surrealism",
    "byzantine", "romanesque", "renaissance", "mannerism", "romanticism", "realism", "pre-raphaelite",
    "arts and crafts movement", "symbolism", "art brut", "naïve art", "socialist realism", "art informel",
    "tachisme", "op art", "kinetic art", "psychedelic art", "street art", "video art", "installation art",
    "land art", "performance art", "hyperrealism", "photorealism", "vorticism", "ashcan school",
    "post-impressionism", "color field painting", "lyrical abstraction", "hard-edge painting", "minimalism",
    "fluxus", "arte povera", "post-minimalism", "neo-expressionism", "transavanguardia", "bad painting",
    "neo-geo", "bio art", "new media art", "interactive art", "relational aesthetics", "virtual art",
    "internet art", "post-digital art", "vaporwave", "macro realism", "micro impressionism", "environmental art",
    "urban realism", "space art", "fantasy", "sci-fi art", "narrative art", "conceptual photography",
    "manga", "anime", "graphic novel style", "collage", "paper cutting", "textile art", "sand art",
    "ice sculpture", "body art", "temporary art", "light painting", "3D projection art", "holographic art",
    "low-poly", "steampunk", 'disney animation', 'pixar animation', 'minecraft'
]

artist_names = [
    'leonardo da vinci', 'michelangelo', 'raphael', 'vincent van gogh', 'pablo picasso',
    'claude monet', 'rembrandt van rijn', 'johannes vermeer', 'salvador dalí', 'frida kahlo',
    'jackson pollock', 'georgia o\'keeffe', 'andy warhol', 'gustav klimt', 'edvard munch',
    'caravaggio', 'hieronymus bosch', 'jan van eyck', 'sandro botticelli', 'titian',
    'henri de toulouse-lautrec', 'gustave doré', 'john martin', 'edward hopper',
    'frederic remington', 'charles marion russell', 'Rembrandt', 'thomas kinkade',
    'arshile gorky', 'tim burton'
]


# @st.cache_data
def get_image_history_zip(image_list):
    # Create a bytes buffer for the zip file
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for i, image in enumerate(image_list, start=1):
            # Check if image[0] is a list of URLs or a single URL
            if isinstance(image[0], list):
                # Handle the case where there are multiple URLs in image[0]
                for j, url in enumerate(image[0], start=1):
                    download_and_add_to_zip(zipf, url, i, j, image)
            else:
                # Handle the case where image[0] is a single URL
                download_and_add_to_zip(zipf, image[0], i, None, image)

    # Go to the beginning of the BytesIO buffer
    zip_buffer.seek(0)
    return zip_buffer


def download_and_add_to_zip(zipf, url, image_number, subimage_number, image):
    # Adjust image path based on whether it's a single image or part of a list
    image_index = f"{image_number}_{subimage_number}" if subimage_number else str(image_number)
    image_path = f'image_{image_index}.png'

    # Download and save the image
    response = requests.get(url)
    if response.status_code == 200:
        zipf.writestr(image_path, response.content)

    # Save the associated information only for the first image or if it's a single image
    if subimage_number in [1, None]:
        info_path = f'image_{image_number}_info.txt'
        info_content = f"Description: {image[1]}\n" \
                       f"Art Style: {image[2]}\n" \
                       f"Image Format: {image[3]}\n" \
                       f"Enhanced Description: {image[4] or 'N/A'}"
        zipf.writestr(info_path, info_content)


@st.cache_data
def create_pdf(image_data):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for image_info in image_data:
        image_urls, description, art_style, art_format, rev_prompt = image_info

        # Check if the first element is a list of URLs or a single URL
        if isinstance(image_urls, list):
            # Iterate through each URL in the list
            for url in image_urls:
                add_image_to_pdf(pdf, url)
        else:
            # Handle a single URL
            add_image_to_pdf(pdf, image_urls)

        # Add the text information
        pdf.multi_cell(0, 10, f"Description: {description}")
        pdf.ln(1)
        pdf.multi_cell(0, 10, f"Art Style: {art_style}")
        pdf.ln(1)
        pdf.multi_cell(0, 10, f"Art Format: {art_format}")
        pdf.ln(10)

    # Generate the PDF and return as BytesIO
    pdf_output = pdf.output(dest='S')
    pdf_bytes_io = io.BytesIO(pdf_output.encode('latin-1'))
    pdf_bytes_io.seek(0)
    return pdf_bytes_io


def add_image_to_pdf(pdf, image_url):
    # Fetch the image and save to a temporary file
    response = requests.get(image_url)
    if response.status_code == 200:
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_image_file:
            temp_image_file.write(response.content)
            temp_image_file_path = temp_image_file.name

        # Add the image to the PDF using the file path
        pdf.image(temp_image_file_path, x=10, w=100)  # Adjust dimensions as needed
        os.unlink(temp_image_file_path)  # Delete the temporary file

        pdf.ln(20)  # Move below the image


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


def display_image_and_expander(column, image):
    with column:
        st.image(image[0])
        expander = st.expander(f"""
:orange[{image[2].title()}]\n
:blue[{image[1][:45]}]. . .
        """)
        expander.markdown(f"""
### Description
**{image[1].strip()}**

#### Enhanced Description
{image[4] or 'N/A'}
##### Art Style:
{image[2] or 'Default'} \n
##### Image Format:
{image[3] or 'Default'}
""")


def download_history():
    zip_button_col, pdf_button_col, col3 = st.columns([3,3,2])
    st.toast("Saving history...", icon="⌛")
    # Create zip and pdf files as byte objects
    zip_buffer = get_image_history_zip(st.session_state.gen_images)
    pdf_buffer = create_pdf(st.session_state.gen_images)
    with zip_button_col:
        download = st.empty()
        download.download_button(
            label='📂 **Zip**',
            data=zip_buffer,
            file_name="image_history.zip",
            mime="application/zip"
        )
    with pdf_button_col:
        # Download button for the PDF
        download = st.empty()
        download.download_button(
            label="🗒️ **PDF**",
            data=pdf_buffer,
            file_name="image_history.pdf",
            mime="application/pdf"
        )
    st.toast("Image history is ready for download!", icon="✅")


def manage_history():
    # Display history in Sidebar
    for i, image in enumerate(st.session_state.gen_images, start=1):
        expander1 = st.sidebar.expander(f"{i}. {image[1][:40]}...")
        expander1.image(image[0])
        expander1.markdown(image[1])

    # Display history in Tabs
    with tab2:
        art_style_list = [image[2] for image in st.session_state.gen_images]
        style_filter, *cols, filter_count_col = st.columns([2,1,1])
        with style_filter:
            art_style_filter = st.multiselect(
                ':orange[Style]',
                options=set(art_style_list),
                placeholder='Filter by style...'
            )

        # Create columns for save button and nested download button columns
        save_col1, save_col2, save_col3 = st.columns([2,2,3])
        with save_col1:
            if st.button("💾:blue[Save History]"):
                download_history()

        st.divider()

        # Initialize columns
        img_col1, img_col2 = st.columns(2)

        # Counter for filtered images
        filtered_image_count = 0

        for image in st.session_state.gen_images:
            if image[2] in art_style_filter or not art_style_filter:
                # Select column based on filtered_image_count
                column = img_col1 if filtered_image_count % 2 == 0 else img_col2
                display_image_and_expander(column, image)

                # Increment counter for filtered images
                filtered_image_count += 1
        with filter_count_col:
            st.markdown(f"**{filtered_image_count}** image(s)")


def start_fresh():
    st.session_state.extracted_text = None


# Begin web app widgets
st.title(":rainbow[Text to Art]")

tab1, tab2 = st.tabs(["Capture", "History"])

tab1.header("Capture Imagery", divider='rainbow')
tab2.header("Imagery History", divider='rainbow')

text_prompt = """
Extract the text words from the following image.
Do not add quotes around the extracted text, or add any of your own comments.
If there is no text to extract, describe the image with detailed imagery.
"""

api_key = os.environ["OPENAI_API_KEY"] or st.secrets["OPENAI_API_KEY"]
chat_engine = gpt.ChatEngine(api_key=api_key)


if st.session_state.gen_images:
    manage_history()

with tab1:
    # start_cam = st.button('Open Camera', key='start_cam')
    capture_method = st.radio("Method",
                              options=['Camera', 'File', 'Type'],
                              horizontal=True,
                              label_visibility='hidden',
                              on_change=start_fresh,
                              captions=['Extract text or describe the scene',
                                        'Upload and extract text',
                                        'Write your own description']
                              )
    if capture_method == 'Camera':
        captured_text = st.camera_input('Snap', on_change=start_fresh)
    if capture_method == 'File':
        captured_text = st.file_uploader("Upload")
        if captured_text:
            st.image(captured_text)
    if capture_method == 'Type':
        captured_text = "custom"
        # Store the text in session state and skip prompt settings section
        st.session_state.extracted_text = captured_text

    # Display the extract text/read button and execute the vision api call
    # only if an image has been capture with camera_input and extracted_text
    # has been cleared from previous image generation
    if captured_text and not st.session_state.extracted_text:
        extract_button = False
        # Initialize columns
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            extract = st.empty()
        # Display prompt box for additional context
        if capture_method in ('Camera', 'File'):
            if extract.button('👁️:green[Read]', key='extract_button', use_container_width=True):
                extract_button = True
                prompt = encode_image_prompt(captured_text)
                try:
                    with col2:
                        extracted_text = generate_response(
                            chat_engine,
                            prompt=prompt,
                            text_prompt=text_prompt,
                            role_context='image_to_text',
                            spinner_text='Reading'
                        )

                    st.session_state.extracted_text = extracted_text
                except Exception as e:
                    st.error(e)
        else:
            st.session_state.extracted_text = captured_text
            # Remove extract button if a response was received and extracted text
            # is found stored in session state
            extract.empty()

with tab1:
    # Initialize emtpy variables
    extracted_edit_prompt = None
    if captured_text and st.session_state.extracted_text:
        st.divider()
        extracted_edit_box = st.empty()
        # Fill the text box with extracted text, or leave blank if 'Type'
        # method selected for custom prompt
        extracted_edit = extracted_edit_box.text_area(
            label="Image Description",
            help="",
            value="" if st.session_state.extracted_text == 'custom' else st.session_state.extracted_text
        )

        prompt_context = st.text_input(
            label="Context",
            help="Enter additional information as context for the desired image.",
            value=""
        )
        if prompt_context == 'CAF':
            col1, col2 = st.columns(2)
            with col1:
                image_count = st.number_input('n images', min_value=1, max_value=10)
            image_q = 'hd' if st.checkbox('HD Output') else 'standard'
            revised_prompt = True if st.checkbox('Enhance Prompt') else False
        else:
            image_count = 1
            image_q = 'standard'
            revised_prompt = False

        # Initialize columns
        col1, col2 = st.columns(2)

        with col1:
            art_style = st.multiselect('Art Styles',
                                       options=sorted(art_styles + artist_names),
                                       placeholder='Choose a style (optional)',
                                       format_func=lambda x: f"{x.title()} (artist)" if x in artist_names else x.title(),
                                       help="Leave empty for the default style")

        with col2:
            art_format = st.multiselect('Art Formats',
                                        options=sorted(art_formats),
                                        placeholder='Choose a format (optional)',
                                        format_func=lambda x: x.title(),
                                        help="Leave empty for a basic format")

        # Save the user edited prompt to separate state before storing system additions
        st.session_state.extracted_edit_display = extracted_edit
        # Save formatted prompt used for API call
        extracted_edit_prompt = f"Prompt: {extracted_edit}"

        # Update the extracted text to include additional context from text box
        if prompt_context and prompt_context != 'CAF':
            extracted_edit_prompt = f"{extracted_edit_prompt} \n\n Image context: {prompt_context}"
        # Check if art_style and art_format are empty and set to 'Default' if they are
        art_style_str = ', '.join(art_style) if art_style else 'Default'
        art_format_str = ', '.join(art_format) if art_format else 'Default'
        if art_style:
            extracted_edit_prompt += f" \n\n Art style: {art_style_str}"
        if art_format:
            extracted_edit_prompt += f" \n\n Image format: {art_format_str}"

        # Save final formatted prompt to session state for use in API call
        # st.session_state.extracted_edit_prompt = extracted_edit_prompt

        # # Append additional notes for image prompt
        # extracted = f"Restrictions: do not add text or words to the image. \n\n{extracted}"

with tab1:
    if extracted_edit_prompt and captured_text:
        st.divider()
        # Initialize widgets and layout
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            submit = st.empty()
        if submit.button('💭Imagine', type='primary', use_container_width=True):
            with col2:
                image_response = generate_response(
                    chat_engine,
                    prompt=extracted_edit_prompt,
                    role_context='text_to_image',
                    spinner_text='Imagining',
                    image_count=image_count,
                    image_q=image_q,
                    revised_prompt=revised_prompt  # returns a tuple of images, revised prompts
                )
                # print(f'edited prompt: {extracted_edit_prompt}')
                # print(f'full response: {image_response}')
                # print(f'image urls: {image_response[0]}')
                # print(f'revised prompts: {image_response[1]}')
            submit.empty()

            st.session_state.image_response = image_response[0]

            st.subheader("I imagine this...")

            display_response(
                st.session_state.extracted_edit_display,
                download=False,
                simulate_stream=False
            )

            st.subheader("...to look like this")
            st.image(image_response[0])

            # If revised prompt enabled store result in revised_prompt
            # otherwise append False (N/A)
            if revised_prompt:
                revised_prompt = image_response[1][0]

            st.session_state.gen_images.insert(
                0, (image_response[0], st.session_state.extracted_edit_display, art_style_str, art_format_str, revised_prompt)
            )
