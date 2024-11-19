import telebot
from io import BytesIO
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from PIL import Image
from flask import Flask, request

TOKEN = "7587484876:AAEhY-_4HZeAbtce441zDKkfLOmjZEVbyaE"
bot = telebot.TeleBot(TOKEN)

user_data = {}

app = Flask(__name__)

@bot.message_handler(commands=['start'])
def start(message):
    user_data[message.chat.id] = {'file_count': 0, 'images': [], 'next_image_number': 1}
    markup = InlineKeyboardMarkup()
    owner_button = InlineKeyboardButton("Owner", url="https://t.me/FF_OO_X")
    markup.add(owner_button)
    bot.send_message(message.chat.id, "Enter the number of images to convert to PDF:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text.isdigit() or message.text in ["١", "٢", "٣", "٤", "٥", "٦", "٧", "٨", "٩", "١٠"])
def set_image_count(message):
    count = int(message.text) if message.text.isdigit() else int(message.text.translate(str.maketrans("١٢٣٤٥٦٧٨٩٠", "1234567890")))
    user_data[message.chat.id]['file_count'] = count
    bot.send_message(message.chat.id, f"Please send Image 1")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.chat.id
    user_images = user_data.get(user_id, {})
    if not user_images:
        return
    if len(user_images['images']) < user_images['file_count']:
        file_info = bot.get_file(message.photo[-1].file_id)
        file = bot.download_file(file_info.file_path)
        image = Image.open(BytesIO(file))
        user_images['images'].append(image)
        if len(user_images['images']) < user_images['file_count']:
            user_images['next_image_number'] += 1
            bot.send_message(user_id, f"Please send Image {user_images['next_image_number']}")
        else:
            pdf_name = f"File({user_images['next_image_number']}).pdf"
            pdf_data = compile_images_to_pdf(user_images['images'])
            pdf_data.name = pdf_name
            bot.send_document(user_id, pdf_data)
            user_images['next_image_number'] += 1

def compile_images_to_pdf(images):
    pdf_data = BytesIO()
    images[0].save(pdf_data, format="PDF", save_all=True, append_images=images[1:])
    pdf_data.seek(0)
    return pdf_data

@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url='https://your-domain.com/webhook')
    app.run(host="0.0.0.0", port=4000)
