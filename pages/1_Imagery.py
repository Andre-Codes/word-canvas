import streamlit as st
import os
import base64
from pages.utils import gpt_utils as gpt
from pages.utils.web_helpers import generate_response, display_response

# Initialize 'extracted' in session state if not already present
if 'extracted_text' not in st.session_state:
    st.session_state.extracted_text = None
if 'extract_button' not in st.session_state:
    st.session_state.extract_button = None
if 'image_url' not in st.session_state:
    st.session_state.image_url = None
if 'gen_images' not in st.session_state:
    st.session_state.gen_images = []

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
    "ice sculpture", "body art", "temporary art", "light painting", "3D projection art", "holographic art"
]


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
        expander1 = st.sidebar.expander(f"{i}. {image[1][:40]}...")
        expander1.image(image[0])
        expander1.markdown(image[1])
        # Tab history
        with tab2:
            st.image(image[0])
            expander2 = st.expander(f"{image[1][:60]}...")
            expander2.markdown(f"""
### Description
:blue[{image[1]}]

##### Art Style:
{image[2] or 'Default'} \n
##### Image Format:
{image[3] or 'Default'}
""")


def start_fresh():
    st.session_state.extracted_text = None


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
if st.session_state.gen_images:
    display_history()

with tab1:
    # start_cam = st.button('Open Camera', key='start_cam')
    camera = st.empty()

    captured_image = camera.camera_input('Take a picture', disabled=False, on_change=start_fresh)

    # Display the extract text/read button and execute the vision api call
    # only if an image has been capture with camera_input and extracted_text
    # has been cleared from previous image generation
    if captured_image and not st.session_state.extracted_text:
        extract_button = False
        # Initialize columns
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            extract = st.empty()
        # Display prompt box for additional context
        if extract.button('👁️:green[Read]', key='extract_button', use_container_width=True):
            extract_button = True
            prompt = encode_image_prompt(captured_image)
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
            # Remove extract button if a response was received and extracted text
            # is found stored in session state
            extract.empty()

with tab1:
    # Initialize emtpy variables
    extracted_edit_prompt = None

    if captured_image and st.session_state.extracted_text:
        extracted_edit_box = st.empty()

        extracted_edit = extracted_edit_box.text_area(
            label="Extracted text",
            help="",
            value=st.session_state.extracted_text
        )

        prompt_context = st.text_input(
            label="Context",
            help="Enter additional information as context for the scanned text.",
            value=""
        )

        # Initialize columns
        col1, col2 = st.columns(2)

        with col1:
            art_style = st.multiselect('Art Styles', options=sorted(art_styles), format_func=lambda x: x.title())

        with col2:
            art_format = st.multiselect('Art formats', options=sorted(art_formats), format_func=lambda x: x.title())

        # Save the user edited prompt to separate state before storing system additions
        st.session_state.extracted_edit_display = extracted_edit
        # Save formatted prompt used for API call
        extracted_edit_prompt = f"Prompt: {extracted_edit}"

        # Update the extracted text to include additional context from text box
        if prompt_context:
            extracted_edit_prompt = f"{extracted_edit_prompt} \n\n Image context: {prompt_context}"
        if art_style:
            art_style = ', '.join(art_style)
            extracted_edit_prompt = f"{extracted_edit_prompt} \n\n Art style: {art_style}"
        if art_format:
            art_format = ', '.join(art_format)
            extracted_edit_prompt = f"{extracted_edit_prompt} \n\n Image format: {art_format}"

        # Save final formatted prompt to session state for use in API call
        # st.session_state.extracted_edit_prompt = extracted_edit_prompt

        # # Append additional notes for image prompt
        # extracted = f"Restrictions: do not add text or words to the image. \n\n{extracted}"
        print(extracted_edit_prompt)

with tab1:
    if extracted_edit_prompt and captured_image:
        # Initialize widgets and layout
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            submit = st.empty()
        if submit.button('💭Imagine', type='primary', use_container_width=True):
            with col2:
                image_url = generate_response(
                    chat_engine,
                    prompt=extracted_edit_prompt,
                    role_context='text_to_image',
                    spinner_text='Imagining'
                )

            submit.empty()

            st.session_state.image_url = image_url

            st.subheader("I imagine this...")

            display_response(st.session_state.extracted_edit_display, download=False)

            st.subheader("...to look like this")
            st.image(image_url)

            st.session_state.gen_images.append((image_url, st.session_state.extracted_edit_display, art_style, art_format))
            # Clean up session state not needed in future runs
