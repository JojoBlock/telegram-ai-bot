import logging
import aiohttp
import asyncio
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# 📝 Logging Setup
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# 🔑 API Keys (Loaded from environment variables in Render)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# 🌐 OpenRouter API Config
BASE_URL = "https://openrouter.ai/api/v1"
MODEL = "qwen/qwq-32b:free"

# 🤖 AI Chat Function
async def chat_with_ai(user_message: str) -> str:
    """Function to get AI response from OpenRouter."""
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

                # ✅ If response is empty, send a default message
                ai_response = response_json.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                
                if not ai_response:
                    return "⚠️ AI didn't respond. Please try again!"
                
                return ai_response

    except Exception as e:
        logger.error(f"AI Chat Error: {str(e)}")
        return f"❌ AI Error: {str(e)}"

# 📜 Command Handlers
async def start(update: Update, context: CallbackContext) -> None:
    """Sends a welcome message to the user."""
    welcome_text = "🎉 **Welcome!**\n\n🤖 *I'm your AI Assistant!* Just send a message and let's start!"
    await update.message.reply_text(welcome_text, parse_mode="Markdown", disable_web_page_preview=True)

async def handle_message(update: Update, context: CallbackContext) -> None:
    """Handles user messages."""
    user_message = update.message.text
    typing_msg = await update.message.reply_text("⌛ Thinking...")

    ai_response = await chat_with_ai(user_message)

    # ✅ If AI response is empty, send a default message
    if not ai_response.strip():
        ai_response = "😴 AI is resting! Try again later."

    await context.bot.delete_message(chat_id=update.message.chat_id, message_id=typing_msg.message_id)
    await asyncio.sleep(0.5)  # ✅ Added delay to prevent Telegram API overloading
    await update.message.reply_text(ai_response, parse_mode="Markdown")

# 🚀 Main Function to Run Bot
def main() -> None:
    """Main function to run the bot."""
    if not TELEGRAM_BOT_TOKEN or not OPENROUTER_API_KEY:
        logger.error("⚠️ API keys are missing! Check your environment variables in Render.")
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
