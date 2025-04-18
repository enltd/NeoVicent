import logging
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext
from sentiment_analysis import analyze_market_sentiment
from dotenv import load_dotenv
import os

# === Configura tu token aquí ===
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# === Logging para debug ===
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


# === Comando: /start ===
def start(update: Update, context: CallbackContext):
    update.message.reply_text("👋 ¡Hola! Soy NeoVincent.\nUsa /analisis_sentimental para analizar el mercado cripto.")


# === Comando: /analisis_sentimental ===
def analisis_sentimental(update: Update, context: CallbackContext):
    update.message.reply_text("🔍 Realizando análisis de sentimiento...")

    resultado = analyze_market_sentiment(news_limit=15)

    # Enviar índice Fear & Greed
    fg = resultado["fear_greed"]
    fg_msg = f"📊 *Fear & Greed Index*: {fg['valor']} ({fg['sentimiento']})"
    context.bot.send_message(chat_id=update.effective_chat.id, text=fg_msg, parse_mode='Markdown')

    # Enviar tendencia general
    tendencia = resultado["tendencia_general"]
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"📈 Tendencia del mercado: *{tendencia.upper()}*", parse_mode='Markdown')

    # Guardar y enviar gráficos
    from matplotlib import pyplot as plt
    from sentiment_analysis import plot_sentiment_distribution, plot_compound_scores

    plot_sentiment_distribution(resultado["news"])
    plt.savefig("sentimiento.png")
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=open("sentimiento.png", "rb"))
    os.remove("sentimiento.png")

    plot_compound_scores(resultado["news"])
    plt.savefig("compound.png")
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=open("compound.png", "rb"))
    os.remove("compound.png")

    # Enviar resumen de titulares
    resumen = resultado["news"][["sentimiento", "texto"]].head(5)
    resumen_msg = "\n\n".join([f"*{r.sentimiento.upper()}*: {r.texto}" for r in resumen.itertuples()])
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"🗞 *Noticias recientes:*\n\n{resumen_msg}", parse_mode='Markdown')


# === Main ===
def main():
    updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("analisis_sentimental", analisis_sentimental))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
