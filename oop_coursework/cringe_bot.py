import telebot
import requests
from bs4 import BeautifulSoup
import random

class AnekdotProvider:
    def get_anekdot(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            anekdot_divs = soup.find_all('div', class_='topicbox')

            if anekdot_divs:
                random_div = random.choice(anekdot_divs)
                anekdot_text = random_div.find('div', class_='text')
                if anekdot_text:
                    return anekdot_text.get_text(strip=True)
                else:
                    return "Приносим свои извинения, анекдот удалён с сайта по требованию законодательства Российской Федерации. Попробуйте следующий" 
            else:
                return "Анекдоты закончились"

        except requests.exceptions.RequestException as e:
            return f"Ошибка HTTP-запроса: {e}"
        except Exception as e:
            return f"Произошла ошибка: {e}"


class CommandHandler:
    def __init__(self, bot):
        self.bot = bot
        self.bot.message_handler(commands=['start'])(self.send_welcome)
        self.bot.message_handler(commands=['info'])(self.send_info)
        self.bot.message_handler(commands=['prt'])(self.send_prt)

    def send_welcome(self, message):
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        category_list = list(categories.keys())
        if category_list:  
            markup.add(telebot.types.KeyboardButton(category_list[0]))
            for i in range(1, len(category_list), 2):
                row = []
                for j in range(2):
                    if i + j < len(category_list):
                        row.append(telebot.types.KeyboardButton(category_list[i + j]))
                markup.add(*row)
        self.bot.reply_to(message, "Добро пожаловать в бот несмешных анекдотов, взятых с сайта anekdot.ru. Для удобства использования были исключены анекдоты с ненормативной лексикой и провокационными темами. Для начала работы выберите категорию:", reply_markup=markup)

    def send_info(self, message):
        try:
            with open('info.txt', 'r', encoding='utf-8') as file:
                content = file.read()
                self.bot.reply_to(message, content)
        except FileNotFoundError:
            self.bot.reply_to(message, "Файл info.txt не найден.")
        except Exception as e:
            self.bot.reply_to(message, f"Ошибка чтения файла: {e}")


    def send_prt(self, message):
        try:
            with open('prt1.txt', 'r', encoding='utf-8') as file1, \
                    open('prt2.txt', 'r', encoding='utf-8') as file2:
                content1 = file1.read()
                content2 = file2.read()
                self.bot.reply_to(message, content1)
                self.bot.reply_to(message, content2)
        except FileNotFoundError:
            self.bot.reply_to(message, "Один или оба файла prt1.txt и prt2.txt не найдены.")
        except Exception as e:
            self.bot.reply_to(message, f"Ошибка чтения файлов: {e}")


class MediaHandler:
    def __init__(self, bot):
        self.bot = bot
        self.bot.message_handler(content_types=['photo'])(self.handle_photo)
        self.bot.message_handler(content_types=['video', 'video_note'])(self.handle_video)
        self.bot.message_handler(content_types=['audio', 'voice'])(self.handle_audio)


    def handle_photo(self, message):
        self.send_media(message, 'ans.jpg', 'photo')

    def handle_video(self, message):
        self.send_media(message, 'ans.mov', 'video')

    def handle_audio(self, message):
        self.send_media(message, 'ans.ogg', 'audio')

    def send_media(self, message, filename, media_type):
        try:
            with open(filename, 'rb') as media:
                if media_type == 'photo':
                    self.bot.send_photo(message.chat.id, media)
                elif media_type == 'video':
                    self.bot.send_video(message.chat.id, media)
                elif media_type == 'audio':
                    self.bot.send_audio(message.chat.id, media)
        except FileNotFoundError:
            self.bot.reply_to(message, f"Файл '{filename}' не найден.")
        except Exception as e:
            self.bot.reply_to(message, f"Ошибка отправки медиа: {e}")


class TelegramBot:
    def __init__(self, token, categories, bad_words, anekdot_provider):
        self.bot = telebot.TeleBot(token)
        self.categories = categories
        self.bad_words = bad_words
        self.anekdot_provider = anekdot_provider
        self.command_handler = CommandHandler(self.bot)
        self.media_handler = MediaHandler(self.bot)
        self.bot.message_handler(func=lambda message: True)(self.handle_message)

    def handle_message(self, message):
        username = message.from_user.username if message.from_user.username else "Не указано"
        print(f"User: {message.from_user.first_name} ({message.from_user.id}), Username: @{username}")

        if message.text in self.categories:
            anekdot = self.anekdot_provider.get_anekdot(self.categories[message.text])
            self.bot.reply_to(message, anekdot)
        else:
            bad_word = random.choice(self.bad_words)
            self.bot.reply_to(message, f"Это {bad_word} анекдот. Вы не смыслите в юморе. Лучше выберите анекдот из предложенных категорий.")

    def run(self):
        self.bot.polling(none_stop=True)


token = [x for x in open('token.txt')][0]

categories = {
    'Случайный анекдот 🔄': 'https://www.anekdot.ru/random/anekdot/',
    'Анекдоты про мужа и жену 👩‍❤️‍👨': 'https://www.anekdot.ru/tags/муж%20и%20жена',
    'Анекдоты про коронавирус 🦠': 'https://www.anekdot.ru/tags/коронавирус',
    'Анекдоты про интернет 🌐': 'https://www.anekdot.ru/tags/интернет',
    'Анекдоты про программистов 👨‍💻': 'https://www.anekdot.ru/tags/программист',
    'Анекдоты про Вовочку 👦': 'https://www.anekdot.ru/tags/вовочка',
    'Анекдоты про тёщу 🐍': 'https://www.anekdot.ru/tags/тёща'
}

bad_words = ["плохой", "скучный", "бездарный", "отвратительный", "позорный", "посредственный", "слабый", "жалкий", "низкосортный", "никудышный"]

anekdot_provider = AnekdotProvider()
bot = TelegramBot(token, categories, bad_words, anekdot_provider)
bot.run()