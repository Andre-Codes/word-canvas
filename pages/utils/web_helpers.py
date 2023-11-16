import streamlit as st
import json


ai_avatar = "/mount/src/code-tutor/web_app/pages/images/ct_logo_head.png"  # /mount/src/code-tutor/web_app/


def generate_response(app, prompt, role_context=None, **kwargs):
    # Add check for image_prompt and text_prompt in addition
    if prompt is None:
        raise ValueError("No prompt provided.")
    spinner_text = kwargs.get('spinner_text', 'thinking')
    param_configs = {
        'image_to_text': {'prompt': prompt, 'response_type': 'vision', 'raw_output': False},
        'text_to_image': {'prompt': prompt, 'response_type': 'image', 'raw_output': False}
    }
    with st.spinner(f'...{spinner_text} :thought_balloon:'):
        try:
            # Use the dictionary to get the appropriate parameters
            params = param_configs.get(role_context, {'prompt': prompt})
            # Update params with any additional kwargs provided
            params.update(kwargs)
            # Call the get_response method with the unpacked parameters
            response = app.get_response(**params)
            return response
        except Exception as e:
            raise e


def handle_file_output(responses):
    all_response_content = [f"{responses} \n\n"]
    file_data = ''.join(all_response_content)
    return file_data


def create_download(response, role_name):
    st.download_button(
        label=":green[Download] :floppy_disk:",
        data=response,
        file_name=f'{role_name}.md',
        mime='text/markdown'
    )


def display_response(response, streaming=False, download=True, role_name=None):
    markdown_placeholder = st.empty()
    collected_responses = []

    if streaming:
        for chunk in response:
            if chunk.choices[0].finish_reason != 'stop':
                content_chunk = chunk.choices[0].delta.content
                if content_chunk:
                    collected_responses.append(content_chunk)
                    response_content = ''.join(collected_responses)
                    markdown_placeholder.chat_message('ai', avatar=ai_avatar).markdown(f"{response_content}🖋️\n\n")
            else:
                markdown_placeholder.chat_message('ai', avatar=ai_avatar).markdown(response_content)
    else:
        response_content = response
        markdown_placeholder.markdown(response_content)
        file_data = response_content

    file_data = handle_file_output(response_content)  # not working with extra lesson

    if download:
        create_download(file_data, role_name)

    return response_content
