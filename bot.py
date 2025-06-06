import os
import logging
import zipfile
import io
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, CallbackQueryHandler, ConversationHandler
)
from handlers.pdf_handlers import (
    convert_pdf_to_word, split_pdf, image_to_pdf,
    pdf_to_images, merge_images_to_pdf, merge_pdfs
)
from handlers.word_handlers import convert_word_to_pdf

# Load environment variables
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

DOWNLOADS_DIR = "downloads"
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SELECTING_ACTION, WAITING_FILE, WAITING_PAGE_RANGE = range(3)

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("PDF → Word", callback_data='pdf_to_word'),
         InlineKeyboardButton("Word → PDF", callback_data='word_to_pdf')],
        [InlineKeyboardButton("Split PDF", callback_data='split_pdf')],
        [InlineKeyboardButton("Image → PDF", callback_data='image_to_pdf'),
         InlineKeyboardButton("PDF → Images", callback_data='pdf_to_images')],
        [InlineKeyboardButton("Merge PDF", callback_data='merge_pdf')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Welcome! Choose an action. Then upload your file(s).\nYou can also send /cancel to cancel the operation.",
        reply_markup=reply_markup
    )
    return SELECTING_ACTION

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    action = query.data
    user_data[user_id] = {'action': action, 'images': [], 'pdfs': []}
    await query.edit_message_text(f"Selected: {action.replace('_', ' ').title()}\n\nNow upload your file(s). For merge, upload all and send /done when ready.")
    return WAITING_FILE

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    action = user_data.get(user_id, {}).get('action')

    if not action:
        await update.message.reply_text("Please use /start to select an action first.")
        return ConversationHandler.END

    if action == 'image_to_pdf' and update.message.photo:
        file_obj = update.message.photo[-1]
        file_path = os.path.join(DOWNLOADS_DIR, f"{file_obj.file_id}.jpg")
        new_file = await context.bot.get_file(file_obj.file_id)
        await new_file.download_to_drive(custom_path=file_path)
        user_data[user_id]['images'].append(file_path)
        await update.message.reply_text("Image received. Send more images or send /done when ready.")
        return WAITING_FILE

    if update.message.document:
        file_obj = update.message.document
        file_path = os.path.join(DOWNLOADS_DIR, file_obj.file_name)
        new_file = await context.bot.get_file(file_obj.file_id)
        await new_file.download_to_drive(custom_path=file_path)

        if action == 'split_pdf':
            user_data[user_id]['file_path'] = file_path
            await update.message.reply_text("Enter page numbers or ranges to split (e.g., 1,3-5):")
            return WAITING_PAGE_RANGE

        if action == 'merge_pdf':
            user_data[user_id]['pdfs'].append(file_path)
            await update.message.reply_text("PDF received. Send more PDFs or send /done when ready.")
            return WAITING_FILE

        await update.message.reply_text("Processing...")
        try:
            if action == 'pdf_to_word':
                output = convert_pdf_to_word(file_path)
            elif action == 'word_to_pdf':
                output = convert_word_to_pdf(file_path)
            elif action == 'image_to_pdf':
                output = image_to_pdf(file_path)
            elif action == 'pdf_to_images':
                images = pdf_to_images(file_path, all_pages=True)
                if len(images) > 1:
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, 'w') as z:
                        for img in images:
                            z.write(img, arcname=os.path.basename(img))
                    zip_buffer.seek(0)
                    await context.bot.send_document(chat_id=update.effective_chat.id, document=zip_buffer, filename="pdf_images.zip")
                    return ConversationHandler.END
                else:
                    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(images[0], 'rb'))
                    return ConversationHandler.END
            else:
                await update.message.reply_text("Unsupported action.")
                return ConversationHandler.END

            await context.bot.send_document(chat_id=update.effective_chat.id, document=open(output, 'rb'))
        except Exception as e:
            logger.error(f"Error: {e}")
            await update.message.reply_text(f"Error occurred: {e}")

        return ConversationHandler.END

    await update.message.reply_text("Please upload a valid file or image.")
    return WAITING_FILE

async def handle_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    action = user_data.get(user_id, {}).get('action')

    if action == 'image_to_pdf':
        images = user_data[user_id]['images']
        if not images:
            await update.message.reply_text("No images received yet.")
            return ConversationHandler.END

        await update.message.reply_text("Merging images into a PDF...")
        try:
            output = merge_images_to_pdf(images)
            await context.bot.send_document(chat_id=update.effective_chat.id, document=open(output, 'rb'))
        except Exception as e:
            logger.error(f"Error merging images: {e}")
            await update.message.reply_text(f"Failed to merge images: {e}")

    elif action == 'merge_pdf':
        pdfs = user_data[user_id]['pdfs']
        if not pdfs:
            await update.message.reply_text("No PDFs received yet.")
            return ConversationHandler.END

        await update.message.reply_text("Merging PDFs...")
        try:
            output = merge_pdfs(pdfs)
            await context.bot.send_document(chat_id=update.effective_chat.id, document=open(output, 'rb'))
        except Exception as e:
            logger.error(f"Error merging PDFs: {e}")
            await update.message.reply_text(f"Failed to merge PDFs: {e}")

    return ConversationHandler.END

async def handle_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_data.pop(user_id, None)
    await update.message.reply_text("Operation cancelled. Send /start to begin again.")
    return ConversationHandler.END

async def handle_page_range(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    file_path = user_data[user_id].get('file_path')

    try:
        await update.message.reply_text("Splitting PDF...")
        output_paths = split_pdf(file_path, update.message.text)

        if len(output_paths) > 1:
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as z:
                for p in output_paths:
                    z.write(p, arcname=os.path.basename(p))
            zip_buffer.seek(0)
            await context.bot.send_document(chat_id=update.effective_chat.id, document=zip_buffer, filename="split_segments.zip")
        else:
            await context.bot.send_document(chat_id=update.effective_chat.id, document=open(output_paths[0], 'rb'))

    except Exception as e:
        logger.error(f"Error splitting PDF: {e}")
        await update.message.reply_text("Invalid page range. Please try again. Example: `1,3-7`", parse_mode="Markdown")
        return WAITING_PAGE_RANGE

    return ConversationHandler.END

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send /start to begin and choose an action.\nYou can send /cancel to cancel anytime.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECTING_ACTION: [CallbackQueryHandler(button_handler)],
            WAITING_FILE: [
                MessageHandler(filters.Document.ALL | filters.PHOTO, handle_file),
                CommandHandler("done", handle_done),
                CommandHandler("cancel", handle_cancel)
            ],
            WAITING_PAGE_RANGE: [MessageHandler(filters.TEXT & (~filters.COMMAND), handle_page_range)],
        },
        fallbacks=[CommandHandler("help", help_command), CommandHandler("cancel", handle_cancel)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("cancel", handle_cancel))
    app.run_polling()

if __name__ == '__main__':
    main()
