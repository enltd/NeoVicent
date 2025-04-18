from src.data_fetcher import fetch_data
from src.sentiment_analysis import analyze_sentiment
from src.indicators import calculate_indicators
from src.visualization import plot_indicators

def main():
    data = fetch_data("BTC")  # o desde archivo/dataset
    sentiment_score = analyze_sentiment(data['news'])
    indicators = calculate_indicators(data['price'])
    plot_indicators(indicators, sentiment_score)

if __name__ == "__main__":
    main()
