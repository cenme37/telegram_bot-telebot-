import os
from random import choice

from dotenv import load_dotenv
from pydub import AudioSegment
import speech_recognition
import telebot
from PIL import Image, ImageFilter


load_dotenv()

token = os.getenv('TOKEN')

bot = telebot.TeleBot(token)


RANDOM_TASKS = [
    'Написать Гвидо письмо',
    'Выучить Python',
    'Записаться на курс Python',
    'Посмотреть 7 сезон Рик и Морти'
]

todos = dict()

HELP = '''
Список доступных команд:
* print  - напечать все задачи на заданную дату
* todo - добавить задачу
* random - добавить на сегодня случайную задачу
* help - Напечатать help
'''


def oga2wav(filename):
    """Конвертация формата файлов."""
    new_filename = filename.replace('.oga', '.wav')
    audio = AudioSegment.from_file(filename)
    audio.export(new_filename, format='wav')
    return new_filename


def recognize_speech(oga_filename):
    """Перевод голоса в текст и удаление использованных файлов."""
    wav_filename = oga2wav(oga_filename)
    recognizer = speech_recognition.Recognizer()
    with speech_recognition.WavFile(wav_filename) as source:
        wav_audio = recognizer.record(source)
    text = recognizer.recognize_google(wav_audio, language='ru')
    if os.path.exists(oga_filename):
        os.remove(oga_filename)
    if os.path.exists(wav_filename):
        os.remove(wav_filename)
    return text


def download_file(bot, file_id):
    """Скачивание файла, который прислал пользователь."""
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    filename = file_id + file_info.file_path
    filename = filename.replace('/', '_')
    with open(filename, 'wb') as f:
        f.write(downloaded_file)
    return filename


def add_todo(date, task):
    """Действия бота."""
    date = date.lower()
    if todos.get(date) is not None:
        todos[date].append(task)
    else:
        todos[date] = [task]


def send_sticer(message):
    """Направление стикера."""
    sticker = open('love.webp', 'rb')
    bot.send_sticker(message.chat.id, sticker)
    sticker.close()


def transform_image(filename):
    """Обработка изображения."""
    source_image = Image.open(filename)
    enhanced_image = source_image.filter(ImageFilter.EMBOSS)
    enhanced_image = enhanced_image.convert('RGB')
    width = enhanced_image.size[0]
    height = enhanced_image.size[1]
    enhanced_image = enhanced_image.resize((width // 2, height // 2))
    enhanced_image.save(filename)
    return filename


@bot.message_handler(commands=['help'])
def help(message):
    """Команда help."""
    bot.send_message(message.chat.id, HELP)
    send_sticer(message)


@bot.message_handler(commands=['random'])
def random(message):
    """Команда добавления случайной задачи."""
    task = choice(RANDOM_TASKS)
    add_todo('сегодня', task)
    bot.send_message(message.chat.id, f'Задача {task} добавлена на сегодня')
    send_sticer(message)


@bot.message_handler(commands=['add'])
def add(message):
    """Команда добавления задачи на определенную дату."""
    _, date, tail = message.text.split(maxsplit=2)
    task = ' '.join([tail])
    add_todo(date, task)
    bot.send_message(message.chat.id, f'Задача {task} добавлена '
                     f'на дату {date}')
    send_sticer(message)


@bot.message_handler(commands=['show'])
def print_(message):
    """Команда печати всех задач на определенную дату."""
    date = message.text.split()[1].lower()
    if date in todos:
        tasks = ''
        for task in todos[date]:
            tasks += f'[ ] {task}\n'
    else:
        tasks = 'Такой даты нет'
    bot.send_message(message.chat.id, tasks)
    send_sticer(message)


@bot.message_handler(content_types=['voice'])
def transcript(message):
    """Команда, отправляющая текст в ответ на голосовое."""
    filename = download_file(bot, message.voice.file_id)
    text = recognize_speech(filename)
    bot.send_message(message.chat.id, text)


@bot.message_handler(content_types=['photo'])
def resend_photo(message):
    """Отправка обработанного изображения."""
    file_id = message.photo[-1].file_id
    filename = download_file(bot, file_id)
    transform_image(filename)
    image = open(filename, 'rb')
    bot.send_photo(message.chat.id, image)
    image.close()
    if os.path.exists(filename):
        os.remove(filename)


bot.polling(none_stop=True)
