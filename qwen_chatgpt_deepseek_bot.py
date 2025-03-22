import logging
import aiohttp
import asyncio
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# 📌 Load environment variables from .env file
load_dotenv()

# 🔑 API Keys (⚠️ Keep them secret!)
TELEGRAM_BOT_TOKEN = "7909627028:AAFBua1Sa2MRGHKL88G3EEZ_JOVYaqDsFGU"
OPENROUTER_API_KEY = "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"

# 🌐 OpenRouter API Config
BASE_URL = "https://openrouter.ai/api/v1"
MODEL = "qwen/qwq-32b:free"

# 📝 Logging Setup
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# 🤖 AI Chat Function
async def chat_with_ai(user_message: str) -> str:
    """OpenRouter AI se chat response lene ka function."""
    try:
        system_prompt = "You are a helpful AI assistant. Answer concisely."

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://t.me/ok_deepseek_bot",
            "X-Title": "qwen_chatgpt_deepseek_bot"
        }

        data = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{BASE_URL}/chat/completions", json=data, headers=headers) as response:
                response_json = await response.json()
                return response_json.get("choices", [{}])[0].get("message", {}).get("content", "😴 I'm resting. Try again!").strip()
    
    except Exception as e:
        logger.error(f"AI Chat Error: {str(e)}")
        return f"❌ Error: {str(e)}"

# 📜 Command Handlers
async def start(update: Update, context: CallbackContext) -> None:
    """User ke liye welcome message."""
    welcome_text = (
        "🎉 **Welcome!**\n\n"
        "🤖 *I'm your AI Assistant!* I can help you with:\n"
        "🔹 Casual chat (Friendly Talk 🤝)\n"
        "🔹 Coding & Debugging (Python, JavaScript, etc. 💻)\n"
        "🔹 AI & Prompt Engineering (Text-to-Image, AI Tips 🤖🎨)\n"
        "🔹 Knowledge & Facts (History, Science, Tech 📚)\n"
        "🔹 Creative Writing (Stories, Poems, Ideas ✍️)\n\n"
        "🚀 *Just send a message and let's start!*"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown", disable_web_page_preview=True)

async def handle_message(update: Update, context: CallbackContext) -> None:
    """User ke messages handle karega."""
    user_message = update.message.text
    typing_msg = await update.message.reply_text("⌛ Thinking...")

    ai_response = await chat_with_ai(user_message)

    await context.bot.delete_message(chat_id=update.message.chat_id, message_id=typing_msg.message_id)
    await update.message.reply_text(ai_response, parse_mode="Markdown")

# 🚀 Main Function to Run Bot
def main() -> None:
    """Bot ko run karne ka main function."""
    if not TELEGRAM_BOT_TOKEN or not OPENROUTER_API_KEY:
        logger.error("⚠️ API keys are missing! Check your .env file or add keys manually.")
        return

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # ✅ Command Handlers
    app.add_handler(CommandHandler("start", start))
    
    # ✅ Message Handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🚀 Bot is Online! Type /start to test.")
    app.run_polling()

if __name__ == "__main__":
    main()
