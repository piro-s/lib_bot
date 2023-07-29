import os
import json
import telebot
from telebot import types # For types
from hashlib import sha256 # For password


# global variables
token_filename = 'telegram_token'
users_filename = 'users_path.json'
lib_tree_filename = 'tree.json'
lib_players_filename = 'players'
lib_privacy_filename = 'privacy__'
size_limit_filename = 'telebot_size_limit'
lib_dir = "/lib" # Path to lib
folder_data = 0 # Because 1 it's a report

# token
try:
    with open(token_filename, 'r', encoding='utf-8') as file:
        telegram_token = file.read()
except FileNotFoundError:
    print("No file: '" + token_filename + "', check step 3 in readme.")
    quit()

# JSON folder data
try:
    with open(lib_tree_filename, 'r', encoding='utf-8') as file:
        jsonData = json.load(file)
        lib_folder_tree = jsonData[folder_data]
except FileNotFoundError:
    print("No file: '" + lib_tree_filename + "', check step 1 in readme.")
    quit()

# JSON users data
try:
    with open(users_filename, 'r', encoding='utf-8') as file:
        jsonData = json.load(file)
        users_path = jsonData
except FileNotFoundError:
    print("No file: '" + users_filename + "', check step 6 in readme.")
    quit()

# players data
try:
    with open(lib_players_filename, 'r', encoding='utf-8') as file:
        players = [players.rstrip() for players in file]
except FileNotFoundError:
    print("No file: '" + lib_players_filename + "', check step 5 in readme.")
    quit()

# Master password
try:
    with open('credential', 'r') as file:
        password_master = file.read()
except FileNotFoundError:
    print("No file: 'credential', check step 4 in readme.")
    quit()

# Large files; if file not create, create empty list
try:
    with open(size_limit_filename, 'r', encoding='utf-8') as file:
        size_limit_files = file.read()
except FileNotFoundError:
    size_limit_files = []


bot = telebot.TeleBot(telegram_token)


###--------------------------------------------------------------------------###


# functions
def authorization(message):
    chat_id = str(message.chat.id)

    if chat_id not in users_path:
        buttons = types.ReplyKeyboardMarkup(resize_keyboard=True)

        buttons.add(types.InlineKeyboardButton(text='Игрок'))
        buttons.add(types.InlineKeyboardButton(text='Мастер'))

        answer_group = bot.send_message(chat_id, text="Выберите свою группу:", reply_markup=buttons)
        bot.register_next_step_handler(answer_group, askName)
    else:
        bot.send_message(chat_id, "Вы уже зарегистрированы. "
            "Если хотите перерегистрироваться отправьте: /reg")

    # handle_text(message)

def askName(message):
    if message.text == 'Игрок':
        name = bot.send_message(message.chat.id, "Введите имя персонажа:", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(name, processName)
    elif message.text == 'Мастер':
        password = bot.send_message(message.chat.id, "Введите пароль:", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(password, processPassword)

def processName(message):
    if message.text in players:
        users_path[str(message.chat.id)] = {
            'name' : message.text,
            'group' : 'Players',
            'current_key' : '',
            'current_folder' : lib_folder_tree,
            'current_path' : '/',
            'path' : []
        }
        save_users_json()
        bot.send_message(message.chat.id, "Добро пожаловать, " + message.text)
        display_content(message)
    else:
        buttons = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons.add(types.InlineKeyboardButton(text='/start'))
        bot.send_message(message.chat.id, text="Вы не в нашей компании, повторите все снова.", reply_markup=buttons)


def processPassword(message):
    if password_master == sha256(message.text.encode()).hexdigest():
        users_path[str(message.chat.id)] = {
            'name' : 'Мастер',
            'group' : 'DM',
            'current_key' : '',
            'current_folder' : lib_folder_tree,
            'current_path' : '/',
            'path' : []
        }
        save_users_json()
        bot.send_message(message.chat.id, "Добро пожаловать Мастер!")
        display_content(message)
    else:
        buttons = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons.add(types.InlineKeyboardButton(text='/start'))
        bot.send_message(message.chat.id, text="Неправильный пароль, повторите все снова.", reply_markup=buttons)


def check_privacy(chat_id, item): # Return True if it's private
    path = lib_dir + users_path[chat_id]['current_path'] + lib_privacy_filename
    try:
        with open(path, 'r', encoding='utf-8') as file:
            privacy_files = file.read()

        if users_path[chat_id]['group'] == 'Players':
            if 'all_in_folder' in privacy_files:
                return True
            elif item in privacy_files:
                return True
            elif "json" in item:
                return True
            elif lib_privacy_filename in item:
                return True
            else:
                return False
        else:
            return False
    except FileNotFoundError:
        return False

def check_size_limit(chat_id, item): # Return True if size larger than telebot limit
    if item in size_limit_files:
        return True
    else:
        return False



def display_content(message, display=True):
    buttons = types.ReplyKeyboardMarkup(resize_keyboard=True)
    chat_id = str(message.chat.id)

    if users_path[chat_id]['current_folder']['type'] == 'directory':
        # if display:
        #     bot.send_message(chat_id, users_path[chat_id]['current_path'])
        for content in users_path[chat_id]['current_folder']['contents']:
            if not check_privacy(chat_id, content['name']):
                if content['type'] == 'directory':
                    button_text = str(content['name']) + '/'
                    buttons.add(types.InlineKeyboardButton(text=button_text))
            else:
                pass

        # Second loop to show all folders first and then all files
        for content in users_path[chat_id]['current_folder']['contents']:
            if not check_privacy(chat_id, content['name']):
                if content['type'] == 'file':
                    button_text = str(content['name'])
                    buttons.add(types.InlineKeyboardButton(text=button_text))
            else:
                pass
    else:
        pass

    if users_path[chat_id]['current_folder'] != lib_folder_tree:
        buttons.add(types.InlineKeyboardButton(text='Главная'))
        buttons.add(types.InlineKeyboardButton(text='Назад'))


    if display:
        message_text = "Текущая директория: " + users_path[chat_id]['current_path']
        bot.send_message(chat_id, text=message_text, reply_markup=buttons)

def save_users_json():
    with open(users_filename, 'w') as file:
        json.dump(users_path, file)


###--------------------------------------------------------------------------###


# bot handlers
@bot.message_handler(commands=['start'])
def start(message, res=False):
    authorization(message)


@bot.message_handler(commands=['id'])
def show_id(message, res=False):
    chat_id = str(message.chat.id)
    bot.send_message(chat_id, "ID вашего чата: " + chat_id)
    bot.send_message(chat_id, "Имя вашего персонажа: " + users_path[chat_id]['name'])
    bot.send_message(chat_id, "Ваша группа: " + users_path[chat_id]['group'])


@bot.message_handler(commands=['reg'])
def reg(message, res=False):
    chat_id = str(message.chat.id)
    if chat_id in users_path:
        bot.send_message(chat_id, "Удаляю текущего пользователя...")
        users_path.pop(chat_id, 'None')
    bot.send_message(chat_id, "Начата процедура регистрации:")
    authorization(message)


@bot.message_handler(commands=['home'])
def home(message, res=False):
    chat_id = str(message.chat.id)
    users_path[chat_id]['current_folder'] = lib_folder_tree
    users_path[chat_id]['current_path'] = '/'
    save_users_json()
    display_content(message)

###------------------------------------


@bot.message_handler(content_types=['text'])
def handle_text(message):
    chat_id = str(message.chat.id)

    if chat_id not in users_path.keys():
        authorization(message)
    else:
        display_content(message, display=False)

        users_path[chat_id]['current_key'] = message.text

        if users_path[chat_id]['current_key'] == 'Главная':
            users_path[chat_id]['current_folder'] = lib_folder_tree
            users_path[chat_id]['current_path'] = '/'
            save_users_json()
            display_content(message)
            # bot.send_message(chat_id, "Текущий путь: " + current_path)
        elif users_path[chat_id]['current_key'] == 'Назад':
            if users_path[chat_id]['current_folder'] == lib_folder_tree:
                bot.send_message(chat_id, "Вы уже на главной!")
            else:
                users_path[chat_id]['current_path'] = users_path[chat_id]['current_path'].replace(users_path[chat_id]['path'][-1], '')
                users_path[chat_id]['current_path'] = users_path[chat_id]['current_path'][:-1]
                users_path[chat_id]['path'] = users_path[chat_id]['path'][:-1] # Remove last element

                users_path[chat_id]['current_folder'] = lib_folder_tree
                for it in range(0, len(users_path[chat_id]['path'])):
                    for content in users_path[chat_id]['current_folder']['contents']:
                        if content['name'] == users_path[chat_id]['path'][it]:
                            users_path[chat_id]['current_folder'] = content
                            break
                # bot.send_message(chat_id, "Текущий путь: " + current_path)
                save_users_json()
                display_content(message)
        # processing directory
        else:
            founded_file = False
            founded_dir = False
            for content in users_path[chat_id]['current_folder']['contents']:
                if users_path[chat_id]['current_key'][-1] == '/':
                    current_key = users_path[chat_id]['current_key'][:-1]
                else:
                    current_key = users_path[chat_id]['current_key']

                if content['name'] == current_key:
                    if content['type'] == 'directory':
                        users_path[chat_id]['current_path'] = users_path[chat_id]['current_path'] + content['name'] + '/'
                        users_path[chat_id]['path'].append(content['name'])
                        users_path[chat_id]['current_folder'] = content
                        founded_dir = True
                        # bot.send_message(chat_id, "Текущий путь: " + users_path[chat_id]['current_path'])
                        break
                    elif content['type'] == 'file':
                        filename = lib_dir + users_path[chat_id]['current_path'] + current_key # For Linux
                        # filename = lib_dir + users_path[chat_id]['current_path'].replace('/', '\\') + current_key # For Windows
                        founded_file = True

                        # processing files
                        if check_size_limit(chat_id, filename):
                            bot.send_message(chat_id, "Файл [" + current_key + "] больше 50 МБ, "
                                "пожалуйста свяжитесь с Мастером Подземелья для того, чтобы его получить.")
                        else:
                            try:
                                file_size = os.path.getsize(filename) # file size in bytes
                                # print(file_size)
                                if file_size > 1024 * 1024 * 50: # if file larger than 50 MB
                                    bot.send_message(chat_id, "Файл [" + current_key + "] больше 50 МБ, "
                                        "пожалуйста свяжитесь с Мастером Подземелья для того, чтобы его получить.")
                                elif file_size > 1024 * 1024 * 10: # if file larger than 10 MB
                                    try:
                                        bot.send_message(chat_id, "Размер файла [" + current_key + "] больше 10 МБ, "
                                            "пожалуйста подождите одну минуту...")
                                        with open(filename, 'rb') as file:
                                            bot.send_document(chat_id, file, timeout=60)
                                    except:
                                        bot.send_message(chat_id, "Неудалось отправить файл [" + current_key + 
                                            "] попробуйте еще раз или свяжитесь с Мастером Подземелья.")
                                else:
                                    bot.send_message(chat_id, "Файл [" + current_key + "] отправляется...")
                                    try:
                                        with open(filename, 'rb') as file:
                                            bot.send_document(chat_id, file, timeout=60)
                                    except:
                                        bot.send_message(chat_id, "Неудалось отправить файл [" + current_key + 
                                            "] попробуйте еще раз или свяжитесь с Мастером Подземелья.")
                            except FileNotFoundError:
                                bot.send_message(chat_id, "Некорректный ввод, отправьте /home чтобы вернуться на главную.")

            if founded_dir:
                save_users_json()
                display_content(message)
            elif founded_file:
                pass
            else:
                bot.send_message(chat_id, "Некорректный ввод, отправьте /home чтобы вернуться на главную.")


###--------------------------------------------------------------------------###
