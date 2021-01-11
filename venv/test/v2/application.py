from flask import *
import requests
from datetime import *
from dateutil.relativedelta import *
import calendar
import time

application = Flask(__name__)

stock_name = ''
STOCK_API_KEY = "bb0e872d31ae808377684ad47c6bdcfbab21dbab"
NEWS_API_KEY = "37b59e454f0e4eca81034319d9b4710d"


@application.route('/', methods=['GET', 'POST'])
def index():
    global stock_name
    stock_name = request.form.get('Stockname')

    stock_api = STOCK_API_KEY
    news_api = NEWS_API_KEY

    outlook_url = 'https://api.tiingo.com/tiingo/daily/'
    summary_url = 'https://api.tiingo.com/iex/'
    news_url = 'https://newsapi.org/v2/everything?'

    outlook_result = {}
    summary_result = {'change': 0.0, 'changePercent': 0.0}
    top_five_news = []

    if request.method == 'POST':
        try:
            if stock_name == "":
                return render_template('index.html', outlook=outlook_result, summary=summary_result, news=top_five_news,
                                       error='No')

            outlook_return = requests.get(outlook_url + stock_name + '?token=' + stock_api)
            outlook_result = outlook_return.json()

            summary_return = requests.get(summary_url + stock_name + '?token=' + stock_api)
            summary_result = summary_return.json()[0]
            summary_result['timestamp'] = summary_result['timestamp'].split('T')[0]
            summary_result['change'] = round(summary_result['last'] - summary_result['prevClose'], 2)
            summary_result['changePercent'] = round(summary_result['change'] / summary_result['prevClose'] * 100, 2)

            news_return = requests.get(news_url + 'q=' + stock_name + '&apiKey=' + news_api)
            news_result = news_return.json()['articles']
            news_count = 0
            for article in news_result:
                if news_count >= 5:
                    break
                if article['title'] != '' and article['url'] != '' and article['urlToImage'] != '' and article[
                    'publishedAt'] != '':
                    total_date = article['publishedAt']
                    article['publishedAt'] = total_date.split('T')[0].replace('-', '/')
                    top_five_news.append(article)
                    news_count = news_count + 1
            return render_template('index.html', outlook=outlook_result, summary=summary_result, news=top_five_news,
                                   error='No')

        except:
            return render_template('index.html', outlook={}, summary={'change': 0.0, 'changePercent': 0.0}, news=[],
                                   error='Yes')

    return render_template('index.html', outlook=outlook_result, summary=summary_result, news=top_five_news, error='No')


@application.route('/stock', methods=['POST', 'GET'])
def stock_chart():
    global stock_name
    stock_api = STOCK_API_KEY

    chart_url = 'https://api.tiingo.com/iex/'

    charts_result = []

    if request.method == 'GET':
        TODAY = date.today()
        startDate = TODAY + relativedelta(months=-6)
        charts_return = requests.get(chart_url + stock_name + "/prices?startDate=" + str(
            startDate) + "&resampleFreq=12hour&columns=open,high,low,close,volume&token=" + stock_api)
        charts_json = charts_return.json()
        for chart_json in charts_json:
            chart_result = []
            time_day = chart_json['date'].split('T')[0]
            time_point = (chart_json['date'].split('T')[1]).split('.')[0]
            time_day_point = str(time_day) + ' ' + str(time_point)
            timeArray = time.strptime(time_day_point, "%Y-%m-%d %H:%M:%S")
            timestamp = int(time.mktime(timeArray) * 1000)
            chart_result.append(timestamp)
            chart_result.append(chart_json['open'])
            chart_result.append(chart_json['high'])
            chart_result.append(chart_json['low'])
            chart_result.append(chart_json['close'])
            chart_result.append(chart_json['volume'])
            charts_result.append(chart_result)
        chart_title = 'Stock Price ' + stock_name.upper() + ' ' + str(date.today())
        chart_stock = stock_name.upper()
    return {'charts_result': charts_result, 'chart_title': chart_title, 'chart_stock': chart_stock}


@application.route('/sample/outlook/<ticker>', methods=['GET'])
def sample(ticker):
    outlook_url = 'https://api.tiingo.com/tiingo/daily/'
    stock_api = STOCK_API_KEY
    outlook_return = requests.get(outlook_url + ticker + '?token=' + stock_api)
    outlook_result = outlook_return.json()
    return outlook_result


# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()
