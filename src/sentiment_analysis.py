import requests
import pandas as pd
import os
import matplotlib.pyplot as plt
from textblob import TextBlob
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

# === Configuración ===

CRYPTO_PANIC_TOKEN = os.getenv("CRYPTO_PANIC_TOKEN")



# === Obtener Fear & Greed Index ===
def get_fear_greed_index():
    print("📊 Obteniendo índice Fear & Greed...")
    try:
        response = requests.get("https://alternative.me/crypto/fear-and-greed-index/")
        soup = BeautifulSoup(response.text, 'html.parser')
        valor = soup.find("div", class_="fng-circle").text.strip()
        sentimiento = soup.find("div", class_="fng-value").find_next("div").text.strip()
        return {"valor": valor, "sentimiento": sentimiento}
    except Exception as e:
        print("❌ Error al obtener Fear & Greed Index:", e)
        return {"valor": "N/A", "sentimiento": "Desconocido"}


# === Obtener noticias desde CryptoPanic ===
def get_crypto_news(limit=15):
    print("📰 Analizando sentimiento de noticias CryptoPanic...")
    noticias = []
    try:
        url = f"https://cryptopanic.com/api/v1/posts/?auth_token={CRYPTO_PANIC_TOKEN}&kind=news"
        response = requests.get(url)
        data = response.json()

        for post in data.get("results", [])[:limit]:
            noticias.append(post.get("title", ""))
    except Exception as e:
        print("❌ Error al obtener noticias:", e)

    return noticias


# === Análisis de sentimiento con TextBlob ===
def analyze_news_sentiment(news_list):
    resultados = []
    for texto in news_list:
        blob = TextBlob(texto)
        sentimiento = blob.sentiment.polarity
        if sentimiento > 0.1:
            tipo = "positivo"
        elif sentimiento < -0.1:
            tipo = "negativo"
        else:
            tipo = "neutral"
        resultados.append({"texto": texto, "polaridad": sentimiento, "sentimiento": tipo})
    return pd.DataFrame(resultados)


# === Calcular tendencia general (robusto) ===
def get_general_trend(df):
    if df.empty or "sentimiento" not in df.columns:
        print("⚠️ No se encontraron noticias para analizar la tendencia.")
        return "desconocida"
    
    try:
        tendencia = df["sentimiento"].value_counts().idxmax()
        return tendencia
    except Exception as e:
        print(f"❌ Error al calcular la tendencia general: {e}")
        return "desconocida"


# === Visualizaciones ===
def plot_sentiment_distribution(df):
    if df.empty or "sentimiento" not in df.columns:
        print("📉 No hay datos para graficar la distribución de sentimientos.")
        return
    plt.figure(figsize=(6, 4))
    df["sentimiento"].value_counts().plot(kind="bar", color=["green", "red", "gray"])
    plt.title("Distribución de Sentimientos")
    plt.xlabel("Sentimiento")
    plt.ylabel("Cantidad")
    plt.tight_layout()
    plt.show()

def plot_compound_scores(df):
    if df.empty or "polaridad" not in df.columns:
        print("📉 No hay polaridades para graficar.")
        return
    plt.figure(figsize=(6, 4))
    plt.hist(df["polaridad"], bins=10, color="skyblue", edgecolor="black")
    plt.title("Histograma de Polaridades")
    plt.xlabel("Polaridad")
    plt.ylabel("Frecuencia")
    plt.tight_layout()
    plt.show()

# === Función principal de análisis ===
def analyze_market_sentiment(news_limit=15):
    fg_index = get_fear_greed_index()
    news_titles = get_crypto_news(news_limit)
    news_sentiment = analyze_news_sentiment(news_titles)
    tendencia = get_general_trend(news_sentiment)

    return {
        "fear_greed": fg_index,
        "news": news_sentiment,
        "tendencia_general": tendencia
    }


# === Si se ejecuta directamente ===
if __name__ == "__main__":
    resultado = analyze_market_sentiment(15)
    print("📊 Índice Fear & Greed:", resultado["fear_greed"])
    print("📈 Tendencia general:", resultado["tendencia_general"])
    
    plot_sentiment_distribution(resultado["news"])
    plot_compound_scores(resultado["news"])
