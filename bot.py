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
    pdf_to_images, merge_images_to_pdf, merge_pdfs,
    compress_pdf, reorder_pdf
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
        [InlineKeyboardButton("Split PDF", callback_data='split_pdf'),
         InlineKeyboardButton("Merge PDFs", callback_data='merge_pdf')],
        [InlineKeyboardButton("Reorder PDF", callback_data='reorder_pdf'),
         InlineKeyboardButton("Compress PDF", callback_data='compress_pdf')],
        [InlineKeyboardButton("Image → PDF", callback_data='image_to_pdf'),
         InlineKeyboardButton("PDF → Images", callback_data='pdf_to_images')],
        [InlineKeyboardButton("Cancel", callback_data='cancel')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Welcome! Choose an action. Then upload your file(s).",
        reply_markup=reply_markup
    )
    return SELECTING_ACTION

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    action = query.data

    if action == 'cancel':
        user_data.pop(user_id, None)
        await query.edit_message_text("Operation cancelled. Send /start to choose a new action.")
        return ConversationHandler.END

    user_data[user_id] = {'action': action, 'files': [], 'images': []}
    await query.edit_message_text(f"Selected: {action.replace('_', ' ').title()}\n\nNow upload your file(s). Use /done when ready if uploading multiple files.")
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

        # For multiple files (merge, reorder), store in user_data
        if action in ['merge_pdf', 'reorder_pdf']:
            user_data[user_id]['files'].append(file_path)
            await update.message.reply_text("File received. Upload more or send /done.")
            return WAITING_FILE

        # For single-file actions:
        await update.message.reply_text("Processing...")
        try:
            if action == 'pdf_to_word':
                output = convert_pdf_to_word(file_path)
            elif action == 'word_to_pdf':
                output = convert_word_to_pdf(file_path)
            elif action == 'compress_pdf':
                output = compress_pdf(file_path)
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
            elif action == 'split_pdf':
                user_data[user_id]['file_path'] = file_path
                await update.message.reply_text("Send page ranges to split (e.g., 1,3-5):")
                return WAITING_PAGE_RANGE
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

    try:
        if action == 'merge_pdf':
            pdf_paths = user_data[user_id]['files']
            if len(pdf_paths) < 2:
                await update.message.reply_text("Please upload at least two PDFs to merge.")
                return WAITING_FILE
            output = merge_pdfs(pdf_paths)
            await context.bot.send_document(chat_id=update.effective_chat.id, document=open(output, 'rb'))

        elif action == 'reorder_pdf':
            pdf_paths = user_data[user_id]['files']
            if len(pdf_paths) != 1:
                await update.message.reply_text("Please upload exactly one PDF to reorder.")
                return WAITING_FILE
            user_data[user_id]['file_path'] = pdf_paths[0]
            await update.message.reply_text("Send new page order (e.g., 3,1,2):")
            return WAITING_PAGE_RANGE

        elif action == 'image_to_pdf':
            images = user_data[user_id]['images']
            if not images:
                await update.message.reply_text("No images uploaded yet.")
                return ConversationHandler.END
            output = merge_images_to_pdf(images)
            await context.bot.send_document(chat_id=update.effective_chat.id, document=open(output, 'rb'))

    except Exception as e:
        logger.error(f"Error in handle_done for {action}: {e}")
        await update.message.reply_text(f"Error: {e}")

    return ConversationHandler.END

def parse_order(order_str):
    return [int(x.strip()) for x in order_str.split(',') if x.strip().isdigit()]

def parse_page_range_text(text: str) -> list[list[int]]:
    groups = []
    for part in text.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-")
            groups.append(list(range(int(start), int(end) + 1)))
        else:
            groups.append([int(part)])
    return groups

async def handle_page_range(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    action = user_data[user_id].get('action')
    file_path = user_data[user_id].get('file_path')

    try:
        if action == 'reorder_pdf':
            new_order = parse_order(update.message.text)
            output = reorder_pdf(file_path, new_order)
            await context.bot.send_document(chat_id=update.effective_chat.id, document=open(output, 'rb'))

        elif action == 'split_pdf':
            page_groups = parse_page_range_text(update.message.text)
            split_paths = split_pdf(file_path, page_groups)

            for split_file in split_paths:
                await context.bot.send_document(chat_id=update.effective_chat.id, document=open(split_file, 'rb'))

    except Exception as e:
        logger.error(f"Error in handle_page_range for {action}: {e}")
        await update.message.reply_text(f"Error: {e}")
        return WAITING_PAGE_RANGE

    return ConversationHandler.END

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send /start to begin and choose an action.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECTING_ACTION: [CallbackQueryHandler(button_handler)],
            WAITING_FILE: [
                MessageHandler(filters.Document.ALL | filters.PHOTO, handle_file),
                CommandHandler("done", handle_done)
            ],
            WAITING_PAGE_RANGE: [MessageHandler(filters.TEXT & (~filters.COMMAND), handle_page_range)],
        },
        fallbacks=[CommandHandler("help", help_command)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("help", help_command))
    app.run_polling()

if __name__ == '__main__':
    main()
