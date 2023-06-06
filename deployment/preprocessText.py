import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
nltk.download('punkt')
nltk.download('corpus')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')
stop_words = set(stopwords.words('english'))  # set of English stop words
lemmatizer = WordNetLemmatizer()

def preprocess(text,target_language='en'):
  
    if not isinstance(text, str):
        try:
            text = str(text)
        except:
            raise TypeError('Input must be a string or a float')     
    # convert to lowercase
    text = text.lower()
    # Remove URLs
    text = re.sub(r'http\S+', '', text) 
    # Remove special characters and punctuation
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    # Removing repeated characters
    text = re.sub(r'(.)\1{2,}', r'\1', text)

    words = word_tokenize(text)
    words = [lemmatizer.lemmatize(w) for w in words]
    words = [w for w in words if not w in stop_words]
    return words