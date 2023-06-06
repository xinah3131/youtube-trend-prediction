import streamlit as st
import pandas as pd
import joblib
from preprocessText import preprocess
from apiSearch import get_metadata
import base64
import requests
# Load the model

model = joblib.load(r'C:\Users\LEGION\Desktop\MMU\Data Science Fundamental\Project\Prediction of Video\85pct.pkl')

# Define the categories
categories = {
    'Film & Animation': 1,
    'Autos & Vehicles': 2,
    'Music': 10,
    'Pets & Animals': 15,
    'Sports' : 17,
    'Short Movies' : 18,
    'Travel & Events' : 19,
    'Gaming' : 20,
    'Videoblogging' : 21,
    'People & Blogs' : 22,
    'Comedy' : 23,
    'Entertainment' : 24,
    'News & Politics' : 25,
    'Howto & Style' : 26,
    'Education' : 27,
    'Science & Technology' : 28,
    'Nonprofits & Activism' : 29
}


# Create the Streamlit web application
def main():
    st.set_page_config(layout="wide")
    st.markdown(
        f"""
      
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
            @import url('https://fonts.googleapis.com/css2?family=YouTube+Sans&display=swap');
            html, body, [class*="css"]  {{
			    font-family: 'Roboto', sans-serif;
             
			}}
            [data-testid="stAppViewContainer"] > .main {{
                background-color : white;
            
           
            }}
            p{{
                font-family: 'Roboto', sans-serif;
                text-weight: bold;
                font-size: 25px;
            }}
            body{{
                display: flex;
                justify-content: center;
                align-items: center;
                text-align: center;
            }}
            h1{{
                text-align: center;
                color: #d72324;
            }}
            img{{
                max-width: 100%;
                max-height: 100%;
            }}
            .stButton > button {{
                background-color: #d72324;
                color:white;
                font-weight: bold; 
                width: 500px;
                height: 50px;
            }}
            .my-container {{
                border: 2px solid #d72324;
                padding: 10px;
            }}
            .stButton > button:hover {{
                background-color: white;
                color:#d72324;
            }}
           
        </style>
        """,
        unsafe_allow_html=True
    )
    st.markdown("<body><img style = 'max-width: 20%;max-height: 20%;text-align: center;' src=\"https://media.tenor.com/U7OFq772kIEAAAAj/sweet-dreams.gif\"></body>",unsafe_allow_html=True)
    st.markdown("<h1>YouTube Trend Prediction</h1>", unsafe_allow_html=True)
    #https://www.freepnglogos.com/uploads/youtube-play-red-logo-png-transparent-background-6.png
    # st.write("Enter the video details below:")

    # Define a boolean flag variable to track prediction status
    prediction_done = False
    tab1, tab2 = st.tabs(["Predict", "Test"])
    # Input fields
    with tab1:
        with st.container():
            col1, col2, col3 = st.columns(3)
            getTitle, getDuration, getCategory = "", 0.00, 1
            getThumbnailUrl = ""
            with col1:
                url = st.text_input("URL",placeholder="Enter a video url")
                if url:
                    metadata = get_metadata(url)
                    if not metadata.empty:
                        getTitle = metadata['title'].iloc[0]
                        getDuration = metadata['duration'].iloc[0]
                        category_id = metadata['category_id'].iloc[0]
                        getThumbnailUrl = metadata['thumbnail_link'].iloc[0]
                        getCategory = int(category_id)

                        if getThumbnailUrl is not None:
                            picture = get_picture_from_url(getThumbnailUrl)
                            if picture:
                                st.image(picture, caption='Thumbnail captured',width = 400, channels="BGR")
            with col2:
                title = st.text_input("Title", placeholder="Enter a video title",value=getTitle)
                duration = st.number_input("Duration (in minutes)", min_value=0.0, value=getDuration)
                category = st.selectbox("Category", list(categories.keys()), index=list(categories.values()).index(getCategory))
            
            with col3:
                picture = st.file_uploader("Upload Picture", type=["jpg", "jpeg", "png"])
                if picture is not None:
                    st.picture(picture,caption='Thumbnail Uploaded',width = 400, channels="BGR")
    # Convert category to category ID
        categoryId = categories[category]

    
        if st.button("Predict"):
            # Perform prediction
            if title is None or title.strip() == "" and duration == 0:
                st.warning("Please enter a title and duration.")
         
            else:
                if title is None or title.strip() == "":
                    st.warning("Please enter a title")

                if duration == 0:
                    st.warning("Please enter a duration.")
        
                else:
                    prediction = predict_trend(title, duration, categoryId)
                    prediction_done = True  # Set the prediction flag to True
                    if prediction[0] == 1:
                        st.success("This video is predicted to be a trend!")
                        st.markdown("![Alt Text](https://media.tenor.com/Cyi2zT7wcmcAAAAj/pentol-gif-eak.gif)")
                    else:
                        st.info("This video is predicted not to be a trend.")
                        st.markdown("![Alt Text](https://media.tenor.com/VYKtkKnHaUcAAAAj/quby-cute.gif)")
            
        if prediction_done:
            with tab2:
                st.write("Tab 2 content goes here...")

def get_picture_from_url(url):
    try:
        response = requests.get(url)
        image_data = response.content
        return image_data
    except:
        return None

# Function to make predictions
def predict_trend(title, duration, category_id):
    duration = str(duration)
    category_id = int(category_id)
    clean_new_title = preprocess(title)
    # Join the preprocessed words back into a string
    clean_new_title_str = ' '.join(clean_new_title)
    # Prepare the input data
    data = {
        'cleanTitle': [clean_new_title_str],
        'titleLength' : [len(title)],
        'categoryId': [category_id],
        'duration': [duration]
    }
    data = pd.DataFrame(data)
    data['categoryId'] = data['categoryId'].astype('category')
    data['duration'] = data['duration'].astype('float64')
    # Make the prediction
    print(model.predict_proba(data))
    prediction = model.predict(data)
    return prediction

if __name__ == "__main__":
    main()
