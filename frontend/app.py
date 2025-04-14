# frontend/app.py
import streamlit as st
import requests
from PIL import Image
import os
import base64

# Set page config with a stylish theme
st.set_page_config(
    page_title="StyleMatcher - Fashion Recommendation",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a fashionable look
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background: black;
    }
    
    /* Header styling */
    .header {
        background: rgba(0, 0, 0, 0.8);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(255, 255, 255, 0.1);
        margin-bottom: 2rem;
    }
    
    .header h1 {
        color: #FF0000 !important;
        text-align: center;
    }
    
    .header p {
        color: white !important;
    }
    
    /* Men's section styling */
    .mens-section {
        background: rgba(25, 118, 210, 0.1);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(255, 255, 255, 0.1);
        margin-bottom: 2rem;
    }
    
    .mens-section h3 {
        color: #2196f3 !important;
    }
    
    .mens-button {
        background: linear-gradient(45deg, #1976d2, #2196f3) !important;
    }
    
    .mens-button:hover {
        box-shadow: 0 5px 15px rgba(33, 150, 243, 0.4) !important;
    }
    
    .mens-uploader {
        border: 2px dashed #2196f3 !important;
    }
    
    .mens-input input {
        border: 2px solid #2196f3 !important;
        background: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
    }
    
    /* Women's section styling */
    .womens-section {
        background: rgba(194, 24, 91, 0.1);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(255, 255, 255, 0.1);
        margin-bottom: 2rem;
    }
    
    .womens-section h3 {
        color: #e91e63 !important;
    }
    
    .womens-button {
        background: linear-gradient(45deg, #c2185b, #e91e63) !important;
    }
    
    .womens-button:hover {
        box-shadow: 0 5px 15px rgba(233, 30, 99, 0.4) !important;
    }
    
    .womens-uploader {
        border: 2px dashed #e91e63 !important;
    }
    
    .womens-input input {
        border: 2px solid #e91e63 !important;
        background: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
    }
    
    /* Recommendation card styling */
    .recommendation-card {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem;
        box-shadow: 0 4px 6px rgba(255, 255, 255, 0.1);
        transition: transform 0.3s ease;
    }
    
    .recommendation-card:hover {
        transform: translateY(-5px);
    }
    
    .image-container {
        border-radius: 10px;
        overflow: hidden;
        margin-bottom: 1rem;
    }
    
    /* Button styling */
    .stButton>button {
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 25px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: scale(1.05);
    }
    
    /* File uploader styling */
    .stFileUploader>div {
        border-radius: 15px;
        padding: 2rem;
        background: rgba(255, 255, 255, 0.05);
    }
    
    /* Text input styling */
    .stTextInput>div>div>input {
        border-radius: 10px;
        color: white !important;
    }
    
    /* Spinner styling */
    .stSpinner>div {
        border-top-color: #FF0000;
    }
    
    /* Input image container */
    .input-image-container {
        background: rgba(255, 255, 255, 0.05);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
    }
    
    /* Text color */
    .stMarkdown, .stText, .stCaption {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

def get_first_sentence(text):
    """Extract the first sentence from text"""
    if not text:
        return "No caption available"
    # Split by period and take the first part
    first_sentence = text.split('.')[0].strip()
    # Add period if it's not empty
    return first_sentence + '.' if first_sentence else "No caption available"

def display_recommendations(response, gender):
    """Display recommendations in a clean layout"""
    if response.status_code == 200:
        results = response.json()
        if not results:
            st.warning("No recommendations found. Try a different query or image.")
            return
            
        st.markdown("### 🎯 Recommended Items")
        # Create a grid layout for top 3 recommendations
        cols = st.columns(3)
        for i, item in enumerate(results[:3]):  # Only show top 3
            with cols[i]:
                with st.container():
                    st.markdown(f"<div class='recommendation-card'>", unsafe_allow_html=True)
                    
                    # Image container
                    st.markdown("<div class='image-container'>", unsafe_allow_html=True)
                    try:
                        image_path = item.get('image', '')
                        if image_path and os.path.exists(image_path):
                            st.image(image_path, use_column_width=True)
                        else:
                            st.error("Image not found in database")
                    except Exception as e:
                        st.error(f"Error loading image: {str(e)}")
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Caption
                    caption = get_first_sentence(item.get('caption', ''))
                    st.markdown(f"**{caption}**")
                    st.caption(f"👤 {gender.capitalize()}")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.error(f"Error: {response.json().get('error', 'Unknown error')}")

# Main header
st.markdown("""
<div class='header'>
    <h1 style='text-align: center;'>👗 StyleMatcher</h1>
    <p style='text-align: center;'>Find your perfect fashion match with AI-powered recommendations</p>
</div>
""", unsafe_allow_html=True)

# Two-column layout for upload sections
col1, col2 = st.columns(2)

with col1:
    st.markdown("<div class='mens-section'>", unsafe_allow_html=True)
    st.markdown("### 👔 Men's Fashion")
    male_img = st.file_uploader("Upload your image", type=['jpg','png'], key='male')
    
    # Display uploaded image
    if male_img is not None:
        st.markdown("<div class='input-image-container'>", unsafe_allow_html=True)
        st.image(male_img, caption="Uploaded Image", width=200)
        st.markdown("</div>", unsafe_allow_html=True)
    
    male_text = st.text_input("Describe your style preference", key='male_text', 
                            placeholder="e.g., casual outfit with jeans and t-shirt")
    if st.button("Get Men's Recommendations", key='male_btn'):
        if male_img:
            with st.spinner("🔍 Finding similar men's fashion items..."):
                response = requests.post(
                    'http://localhost:5000/recommend',
                    files={'image': male_img},
                    data={'gender': 'male', 'query': male_text}
                )
            display_recommendations(response, 'male')
        else:
            st.warning("Please upload an image first")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='womens-section'>", unsafe_allow_html=True)
    st.markdown("### 👗 Women's Fashion")
    female_img = st.file_uploader("Upload your image", type=['jpg','png'], key='female')
    
    # Display uploaded image
    if female_img is not None:
        st.markdown("<div class='input-image-container'>", unsafe_allow_html=True)
        st.image(female_img, caption="Uploaded Image", width=200)
        st.markdown("</div>", unsafe_allow_html=True)
    
    female_text = st.text_input("Describe your style preference", key='female_text',
                              placeholder="e.g., summer dress with accessories")
    if st.button("Get Women's Recommendations", key='female_btn'):
        if female_img:
            with st.spinner("🔍 Finding similar women's fashion items..."):
                response = requests.post(
                    'http://localhost:5000/recommend',
                    files={'image': female_img},
                    data={'gender': 'female', 'query': female_text}
                )
            display_recommendations(response, 'female')
        else:
            st.warning("Please upload an image first")
    st.markdown("</div>", unsafe_allow_html=True)