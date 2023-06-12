import streamlit as st
import pandas as pd
import joblib
from preprocessText import preprocess
from apiSearch import get_metadata,get_trending_videos
import base64
import requests
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
# Load the model
def read_model(region):
    if(region == "United States"):
        model = joblib.load(r'C:\Users\LEGION\Desktop\MMU\Data Science Fundamental\Project\Prediction of Video\85pct(2).pkl')
    return model

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
            .stDownloadButton > button{{
                background-color: #e7e7e7;
                color:black;
                font-weight: bold; 
                width: 150px;
                height: 35px;
                float: right;
            }}
            .stButton > button:hover {{
                background-color: white;
                color:#d72324;
            }}
            .my-container {{
                border: 2px solid #d72324;
                padding: 10px;
            }}
           
           
        </style>
        """,
        unsafe_allow_html=True
    )
    st.markdown("<body><img style = 'max-width: 20%;max-height: 20%;text-align: center;' src=\"https://media.tenor.com/U7OFq772kIEAAAAj/sweet-dreams.gif\"></body>",unsafe_allow_html=True)
    st.markdown("<h1>YouTube Trend Prediction</h1>", unsafe_allow_html=True)
    #https://www.freepnglogos.com/uploads/youtube-play-red-logo-png-transparent-background-6.png
    # st.write("Enter the video details below:")

    @st.cache_data 
    def convert_df(df):
        return df.to_csv(index=False).encode('utf-8')
  
    # Sidebar menu options
    menu_options = ["Predict", "Trending", "Visualize"]
    selected_option = st.sidebar.selectbox("Menu", menu_options)

    # Input fields
    if selected_option == "Predict":
        region = st.sidebar.selectbox("Select Region", ['United States'])
        model = read_model(region)
        with st.container():
            col1, col2, col3 = st.columns(3)
            getTitle, getDuration, getCategory = "", 0.00, 1
            getThumbnailUrl = ""
            with col1:
                url = st.text_input("URL", placeholder="Enter a video URL")
                if url:
                    metadata = get_metadata(url)
                    if not metadata.empty:
                        getTitle = metadata['title'].iloc[0]
                        getDuration = metadata['duration'].iloc[0]
                        category_id = metadata['category_id'].iloc[0]
                        getThumbnailUrl = metadata['thumbnail_link'].iloc[0]
                        getCategory = int(category_id)
                        getDescription = metadata['description'].iloc[0]

                        if getThumbnailUrl is not None:
                            picture = get_picture_from_url(getThumbnailUrl)
                            if picture:
                                st.image(picture, caption='Thumbnail captured', width=320, channels="BGR")
            with col2:
                title = st.text_input("Title", placeholder="Enter a video title", value=getTitle)
                duration = st.number_input("Duration (in seconds)", min_value=0.0, value=getDuration)
                category = st.selectbox(
                    "Category", list(categories.keys()), index=list(categories.values()).index(getCategory)
                )


            with col3:
                picture = st.file_uploader("Upload Picture", type=["jpg", "jpeg", "png"])
                if picture is not None:
                    st.picture(picture, caption='Thumbnail Uploaded', width=400, channels="BGR")

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
                    prediction = predict_trend(model,title, duration, categoryId)
                    if prediction[0] == 1:
                        st.success("This video is predicted to be a trend!")
                        st.markdown("![Alt Text](https://media.tenor.com/Cyi2zT7wcmcAAAAj/pentol-gif-eak.gif)")
                    else:
                        st.info("This video is predicted not to be a trend.")
                        st.markdown("![Alt Text](https://media.tenor.com/VYKtkKnHaUcAAAAj/quby-cute.gif)")

    elif selected_option == "Trending":
        tab1, tab2 = st.tabs(["Trending Board", "Video Info"])
        country_code = st.sidebar.selectbox("Select Country Code", ['US', 'CA', 'GB', 'DE', 'FR', 'RU', 'BR', 'IN', 'MY', 'SG', 'JP', 'KR'])
        with st.container():
            with tab1:
                st.write("Top 10 Trending Videos")
                df = get_trending_videos(country_code)
                st.dataframe(df)
                
                csv = convert_df(df)
                st.download_button(
                    "Download",
                    csv,
                    "top10Trending.csv",
                    "text/csv",
                    key='download-csv'
                )
                
            with tab2:
                if df is not None:
                    # Display video titles
                    selected_video_title = st.selectbox("Select a Video", df['title'])
                    selected_video = df[df['title'] == selected_video_title].iloc[0]
                else:
                    st.error('Failed to retrieve trending videos.')
                col4, col5 = st.columns(2)
                with col4:
                    if selected_video is not None:
                        image = get_picture_from_url(selected_video['thumbnail_link'])
                        if image:
                            st.image(image, caption='Thumbnail captured', width=400, channels="BGR")
                with col5:
                    st.write("Title:", selected_video['title'])
                    category_name = next(
                        (key for key, value in categories.items() if value == selected_video['category_id']), 'Unknown Category'
                    )
                    st.write("Category:", category_name)
                    st.write("Duration:", selected_video['duration'])
           

    elif selected_option == "Visualize":
        with st.container():
            tab3, tab4, tab5, tab6 = st.tabs(["Best Category", "Best Duration","Best Title","Best Title Length"])
            with tab3:
                col6, col7 = st.columns(2)
                with col6:
                    show_top_category()

                with col7:
                    show_best_category()
            
            with tab4:
                col8, col9 = st.columns(2)
                with col8:
                    show_top_duration()

                with col9:
                    show_best_duration()
            
            with tab5:
                col10, col11 = st.columns(2)
                with col10:
                    show_top_title()
                with col11:
                    show_best_title()

            with tab6:
                col12, col13 = st.columns(2)
                with col12:
                    show_top_titleLength()
                with col13:
                    show_best_titleLength()
         
def get_picture_from_url(url):
    try:
        response = requests.get(url)
        image_data = response.content
        return image_data
    except:
        return None

def get_top_category():
    topCategory = pd.read_csv(r'C:\Users\LEGION\Desktop\MMU\Data Science Fundamental\Project\Prediction of Video\topCategory.csv')
    # Sort the DataFrame in ascending order based on predicted_prob column
    topCategory_sorted = topCategory.sort_values('predicted_prob')

    # Add a 'rank' column representing the ascending order of predicted_prob
    topCategory_sorted['rank'] = range(1, len(topCategory_sorted) + 1)
    # Map category_id to category name using the categories dictionary
    topCategory_sorted['category_name'] = topCategory_sorted['category_id'].map(lambda x: next((key for key, value in categories.items() if value == x), 'Unknown Category'))
    return topCategory_sorted

def show_top_category():
    topCategory_sorted = get_top_category()

    # Set a color palette for the plot
    color_palette = sns.color_palette('Set2', len(topCategory_sorted['category_id'].unique()))

    # Create a bar plot based on rank and predicted_prob columns with different colors for each category_name
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=topCategory_sorted, x='rank', y='predicted_prob', hue='category_name', palette=color_palette)
    plt.xlabel('Rank')
    plt.ylabel('Predicted Probability')
    plt.title('Top Categories')

    # Display the legend and the plot in Streamlit
    st.pyplot(fig)

def show_best_category():
    topCategory_sorted = get_top_category()
    top_3_categories = topCategory_sorted.sort_values('predicted_prob', ascending=True).head(3)
    top_3_categories = top_3_categories['category_name'].head(3)
    st.header("Top 3 Categories")
    # Display the top 3 category IDs with colorful formatting in Streamlit
    for category_id in top_3_categories:
        color = '#339933' if category_id == top_3_categories.iloc[0] else '#ffcc33' if category_id == top_3_categories.iloc[1] else '#ff9900'
        st.write(f"<span style='color:{color};font-weight:bold;'>{category_id}</span>", unsafe_allow_html=True)

def get_top_duration():
    topDurationsorted = pd.read_csv(r'C:\Users\LEGION\Desktop\MMU\Data Science Fundamental\Project\Prediction of Video\topDuration.csv')
    topDurationsorted = topDurationsorted.sort_values('predicted_prob', ascending=False)
    return topDurationsorted

def show_top_duration():
    topDuration_sorted = get_top_duration()
    # Set the style of the plot
    sns.set(style='whitegrid')
    # Plot the graph using Seaborn
    plt.figure(figsize=(10, 6))
    sns.barplot(x='duration_range', y='predicted_prob',data=topDuration_sorted)
    plt.xlabel('Duration')
    plt.ylabel('Predicted Probability')
    plt.title('Top Durations')
    plt.xticks(rotation=45)
    plt.show()
    st.pyplot(plt)


def show_best_duration():
    topDurationRange = get_top_duration()
    top_3_durationRange = topDurationRange.sort_values('predicted_prob', ascending=False).head(3)
    top_3_range = top_3_durationRange['duration_range'].head(3)
    st.header("Top 3 Duration Range")
    for range in top_3_range:
        color = '#339933' if range == top_3_range.iloc[0] else '#ffcc33' if range == top_3_range.iloc[1] else '#ff9900'
        st.write(f"<span style='color:{color};font-weight:bold;'>{range}</span>", unsafe_allow_html=True)

def get_top_title():
    topTitle = pd.read_csv(r'C:\Users\LEGION\Desktop\MMU\Data Science Fundamental\Project\Prediction of Video\topTitle.csv')
    # Sort the DataFrame in ascending order based on predicted_prob column
    topTitle_sorted = topTitle.sort_values('Importance Score', ascending=False)
    return topTitle_sorted

def show_top_title():
    topTitle_sorted = get_top_title()
    sns.set(style="whitegrid")
    plt.figure(figsize=(8, 6))
    sns.barplot(x='Importance Score', y='Feature', data=topTitle_sorted, palette="rocket")
    plt.xlabel('Importance Score', fontsize=12)
    plt.ylabel('Feature', fontsize=12)
    plt.title('Top Title Features', fontsize=14)
    plt.tight_layout()
    st.pyplot(plt)

def show_best_title():
    topTitle_sorted = get_top_title()
    top_3_keyword = topTitle_sorted.sort_values('Importance Score', ascending=False).head(3)
    top_3_keyword = topTitle_sorted['Feature'].head(3)
    st.header("Top 3 Keyword")
    for feature in top_3_keyword:
        color = '#339933' if feature == top_3_keyword.iloc[0] else '#ffcc33' if feature == top_3_keyword.iloc[1] else '#ff9900'
        st.write(f"<span style='color:{color};font-weight:bold;'>{feature}</span>", unsafe_allow_html=True)


def round_interval(interval_str):
    start, end = map(float, interval_str.strip('()[]').split(','))
    return f"({int(start)}, {int(end)})"

def get_top_titleLength():
    topTitleLength = pd.read_csv(r'C:\Users\LEGION\Desktop\MMU\Data Science Fundamental\Project\Prediction of Video\topTitleLength.csv')
    title_length_ranges = topTitleLength['titleLength']
    predicted_probs = topTitleLength['predicted_prob']
    rounded_ranges = [round_interval(range_val) for range_val in title_length_ranges]
    data = {
        'rounded_ranges': rounded_ranges,
        'predicted_probs': predicted_probs
    }

    topTitleLength = pd.DataFrame(data)

    # Sort the DataFrame by predicted_probs in descending order
    sorted_titleLength = topTitleLength.sort_values(by='predicted_probs', ascending=False)
    return sorted_titleLength

def show_top_titleLength():
    topTitleLength = get_top_titleLength()
    
    # Set the style of the plot
    sns.set(style='whitegrid')
    # Plot the graph using Seaborn
    plt.figure(figsize=(10, 6))
    sns.barplot(x='rounded_ranges', y='predicted_probs',data=topTitleLength)
    plt.xlabel('Title Length Range')
    plt.ylabel('Predicted Probability')
    plt.title('Top 5 Ranges for Title Length vs. Predicted Probability')
    plt.xticks(rotation=45)
    plt.show()
    st.pyplot(plt)

def show_best_titleLength():
    topTitleLength = get_top_titleLength()
    top_3_titleLength = topTitleLength.sort_values('predicted_probs', ascending=False).head(3)
    top_3_range = top_3_titleLength['rounded_ranges'].head(3)
    st.header("Top 3 Title Length Range")
    for range in top_3_range:
        color = '#339933' if range == top_3_range.iloc[0] else '#ffcc33' if range == top_3_range.iloc[1] else '#ff9900'
        st.write(f"<span style='color:{color};font-weight:bold;'>{range}</span>", unsafe_allow_html=True)

# Function to make predictions
def predict_trend(model,title, duration, category_id):
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
