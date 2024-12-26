import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext
from telegram.ext import filters  # Use filters now
from openai import OpenAI  # Import OpenAI from the updated SDK
from googleapiclient.discovery import build
import google.generativeai as genai  # Import Gemini AI
from dotenv import load_dotenv
# Set up API keys from environment variables
google_api_key = os.getenv("GOOGLE_API_KEY")  # Get Google API key
google_cx = os.getenv("GOOGLE_CX_ID")         # Get Google Custom Search Engine ID
telegram_token = "token_id"  # without extra quotes
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # Initialize OpenAI client with your API key

# Configure Google Gemini API key
genai.configure(api_key=os.getenv("GOOGLE_GEMINI_API_KEY"))  # Set your Gemini API key here

# Function to start the bot
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Welcome! Ask me anything, and I'll provide answers from ChatGPT, Gemini, and Google.")

# Function to handle the messages
async def handle_message(update: Update, context: CallbackContext) -> None:
    user_query = update.message.text
    chatgpt_response = await get_chatgpt_response(user_query)
    gemini_response = await get_gemini_response(user_query)
    google_response = get_google_search_results(user_query)

    response = f"**ChatGPT Response:**\n{chatgpt_response}\n\n"
    response += f"**Gemini Response:**\n{gemini_response}\n\n"
    response += f"**Google Search Results:**\n{google_response}"
    await update.message.reply_text(response)

# Function to get ChatGPT response
async def get_chatgpt_response(prompt):
    try:
        response = openai_client.chat.completions.create(  # Use OpenAI's new client method
            model="gpt-3.5-turbo",  # Switch to GPT-3.5 if you don't have access to GPT-4
            messages=[{"role": "user", "content": prompt}],
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error with ChatGPT: {e}"

# Function to get Google search results
def get_google_search_results(query):
    try:
        service = build("customsearch", "v1", developerKey=google_api_key)
        res = service.cse().list(q=query, cx=google_cx).execute()
        results = res.get("items", [])
        return "\n".join([f"{item['title']}: {item['link']}" for item in results[:3]])
    except Exception as e:
        return f"Error with Google Search: {e}"

# Function to get Gemini AI response
async def get_gemini_response(prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")  # Specify the correct Gemini model
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error with Gemini: {e}"

# Main function to run the bot
def main():
    # Set up the application with your bot token
    application = Application.builder().token(telegram_token).build()

    # Add handlers for start command and messages
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()
