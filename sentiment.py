from textblob import TextBlob
import requests

def get_sentiment(stock):
    url = f"https://newsapi.org/v2/everything?q={stock}&apiKey=YOUR_KEY"
    
    response = requests.get(url).json()
    
    sentiments = []
    
    for article in response["articles"][:10]:
        text = article["title"]
        score = TextBlob(text).sentiment.polarity
        sentiments.append(score)
    
    return sum(sentiments)/len(sentiments)