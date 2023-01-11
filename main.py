import auth
import requests
from twilio.rest import Client


# ------------ API Variables ------------ #
STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla Inc"

# ------------ API Variables ------------ #
STOCK_ENDPOINT = "https://www.alphavantage.co/query"
STOCK_API_KEY = auth.ALPHAVANTAGE_API_KEY
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
NEWS_API_KEY = auth.NEWS_API_KEY
twilio_sid = auth.twilio_sid
twilio_auth_token = auth.twilio_auth_token
FROM_PH = auth.FROM_PH
TO_PH = auth.TO_PH

stock_params = {
    'function': 'TIME_SERIES_DAILY_ADJUSTED',
    'symbol': STOCK_NAME,
    'apikey': STOCK_API_KEY
}

news_parameters = {
    'q': COMPANY_NAME,
    'apiKey': NEWS_API_KEY,
}


# ------------ Check Daily Stock Price Change ------------ #
av_response = requests.get(STOCK_ENDPOINT, stock_params)
av_response.raise_for_status()
stock_data = av_response.json()["Time Series (Daily)"]
stock_prices = list(stock_data.values())
curr_close_price = float(stock_prices[0]['4. close'])
prev_close_price = float(stock_prices[1]['4. close'])

pct_change = round((curr_close_price - prev_close_price) / prev_close_price * 100, 2)
print(pct_change)

# ------------ Get Company News if change of +/- 5% ------------ #

if abs(pct_change) >= 5:
    news_response = requests.get(NEWS_ENDPOINT, news_parameters)
    news_response.raise_for_status()
    news_data = news_response.json()

    top_news = [news for news in news_data['articles'][:3]]
    for news in top_news:
        print(news)
        headline = news['title']
        brief = news['description']
        url = news['url']

# ------------ Send first 3 news articles by SMS via Twilio ------------ #
        client = Client(twilio_sid, twilio_auth_token)
        message = client.messages.create(
            body=f"{STOCK_NAME}: {pct_change} \nHeadline: {headline} \nBrief: {brief} \nLink: {url}",
            from_=FROM_PH,
            to=TO_PH
        )
        print(message.sid)
        print(message.status)
