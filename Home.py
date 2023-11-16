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

See what you read, enjoy what you imagine.
""")