import openai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

from config import BOT_TOKEN, OPENAI_API_KEY
from fonts import fancy_font

openai.api_key = OPENAI_API_KEY

memory = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Привет! Я твой ИИ-ассистент.\n\n"
        "Я умею:\n"
        "• Общаться\n"
        "• Шутить 😏\n"
        "• Делать красивые шрифты\n\n"
        "Напиши что-нибудь!"
    )

async def font_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("Напиши текст после команды /font")
        return
    
    styled = fancy_font(text)
    await update.message.reply_text(f"✨ {styled}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_text = update.message.text

    if user_id not in memory:
        memory[user_id] = []

    memory[user_id].append({"role": "user", "content": user_text})

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": 
             "Ты дружелюбный ИИ-ассистент. Шутишь, используешь эмодзи, отвечаешь интересно и живо."}
        ] + memory[user_id][-10:]
    )

    reply = response.choices[0].message.content

    memory[user_id].append({"role": "assistant", "content": reply})

    await update.message.reply_text(reply)

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("font", font_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()
