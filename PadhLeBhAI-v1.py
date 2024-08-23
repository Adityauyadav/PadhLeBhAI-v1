import streamlit as st
from openai import OpenAI
import cloudinary
import cloudinary.uploader
import cloudinary.api

# Retrieve the keys from Streamlit secrets
openai_api_key = st.secrets["openai"]["api_key"]
cloud_name = st.secrets["cloudinary"]["cloud_name"]
cloudinary_api_key = st.secrets["cloudinary"]["api_key"]
cloudinary_api_secret = st.secrets["cloudinary"]["api_secret"]

# Set up Cloudinary credentials
cloudinary.config(
    cloud_name=cloud_name,
    api_key=cloudinary_api_key,
    api_secret=cloudinary_api_secret
)

client = OpenAI(api_key=openai_api_key)
st.title("Padh Le Bh.AI")

# Allow the user to upload an image or provide a URL
image_option = st.radio("Select Image Input Method:", options=["URL", "Upload"])

image_url = ""
if image_option == "URL":
    image_url = st.text_input("Enter Image URL:")
else:
    uploaded_file = st.file_uploader("Upload an Image", type=["png", "jpg", "jpeg"])
    if uploaded_file is not None:
        # Upload to Cloudinary and convert to JPG
        upload_result = cloudinary.uploader.upload(uploaded_file, format="jpg")
        image_url = upload_result["secure_url"]
        st.success(f"Image uploaded to Cloudinary: {image_url}")

st.write("Please provide the following details:")
st.header("Schedule Preferences")

study_time = st.number_input("Daily Study Time (hours)", min_value=1, max_value=24, value=2)

start_date = st.date_input("Preferred Study Start Date")
end_date = st.date_input("Preferred Study End Date")

study_days = st.multiselect("Available Study Days", options=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])

st.header("Additional Preferences")

max_session_length = st.selectbox("Maximum Study Session Length", options=["30 minutes", "1 hour", "2 hours", "3 hours"], index=1)

break_interval = st.selectbox("Break Intervals", options=["5-minute break after 30 minutes of study", "10-minute break after 1 hour of study", "15-minute break after 2 hours of study"], index=0)

prompt = f"I want you to create me a study planner as my exams are upcoming in few days. My syllabus for the upcoming exam is [syllabus_file], and I want to start preparing from {start_date} to {end_date}. I want to dedicate {study_time} daily and my available study days are {study_days}. My maximum sitting hour will be of {max_session_length} and my break intervals will be of length {break_interval}. I want to cover each topic effectively so that I can pass my exam. Give me a schedule in tabular format based on the above requirements."

def generate_response(prompt, image_url):
    try:
        response = client.chat.completions.create(
            model='gpt-4o',
            messages=[
                {"role": "system", "content": "You are a helpful assistant that responds in Markdown. Help me with my math homework!"},
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]}
            ],
            temperature=0.0,
        )
        return response.choices[0].message.content
    
    except Exception as e:
        return f"Error: {e}"

if st.button("Submit"):
    if prompt and image_url:
        result = generate_response(prompt, image_url)
        st.write("Your Schedule to follow:")
        st.markdown(result)
        if image_url:
            st.image(image_url)
