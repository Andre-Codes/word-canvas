import streamlit as st


st.set_page_config(
    page_title='Word Canvas - Text to Art',
)
col1, col2, col3 = st.columns([2,4,2])

with col2:
    st.title(":rainbow[Word Canvas]")

st.markdown("""
Snap a photo of text from a book, magazine, comic, or anything with words!
Word Canvas will turn your imagery into beautiful artwork.

Image what you read, see what you imagine.
""")

col1, col2, col3 = st.columns([1, 3, 1])

with col2:
    st.markdown("""
👈Enter the imagery room from the sidebar.
    """)

st.warning("Refreshing the webpage will clear all image history", icon='ℹ️')

disclaimer = st.sidebar.container()
disclaimer.info("""
The content provided on this platform is generated using 
artificial intelligence (AI) techniques. AI-generated 
content is subject to potential errors, biases, and inaccuracies inherent 
to automated systems. Users are advised to exercise discretion and 
critically evaluate the content before relying on it for decision-making, 
coding, or any other purpose. Official OpenAI terms and policies can be
read here: https://openai.com/policies
""", icon="ℹ️")