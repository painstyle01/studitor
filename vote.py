import logging, time, flask, telebot, constants, mysql.connector, random
from telebot import types

cnx = mysql.connector.connect(host=constants.db_host,
                              user=constants.db_user,
                              password=constants.db_passwd,
                              database=constants.db_base)
print(cnx)
cursor = cnx.cursor(buffered=True)
cnx.autocommit = True
# Webhook settings
WEBHOOK_HOST = constants.webhook_host
WEBHOOK_PORT = 88  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP addr

WEBHOOK_SSL_CERT = './webhook_cert.pem'  # Path to the ssl certificate
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'  # Path to the ssl private key

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % constants.token

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

# Init bot

bot = telebot.TeleBot(constants.token)

app = flask.Flask(__name__)

# Keyboards
admin_chat_id = constants.admins

main_menu = types.ReplyKeyboardMarkup(True)
main_menu.row("📢Повідомити про проблему")
main_menu.row("🤝Вирішити проблему")
main_menu.row("🚀Про проект")
main_menu.row("🎲Giveaway код")

uni_markup = types.ReplyKeyboardMarkup(True)
uni_markup.row("ЛНТУ")
uni_markup.row("СНУ")

change_uni = types.ReplyKeyboardMarkup(True)
change_uni.row("Так")
change_uni.row("Ні")

LNTU_markup = types.ReplyKeyboardMarkup(True)
LNTU_markup.row("Факультет комп'ютерних наук та інформаційних технологій")
LNTU_markup.row("Технологічний факультет(ТФ)")
LNTU_markup.row("Факультет архітектури, будівництва та дизайну ")
LNTU_markup.row("Факультет фінансів, обліку, лінгвістики та права ")
LNTU_markup.row("Машинобудівний факультет (МБФ)")
LNTU_markup.row("Факультет екології, туризму та електроінженерії")
LNTU_markup.row("Повідомити про проблему")

SNU_markup = types.ReplyKeyboardMarkup(True)
SNU_markup.row("Факультет фізичної культури, спорту та здоров'я")
SNU_markup.row("Факультет педагогічної освіти та соціальної роботи")
SNU_markup.row("Факультет економіки та управління")
SNU_markup.row("Факультет іноземної філології")
SNU_markup.row("Факультет філології та журналістики")
SNU_markup.row("Факультет історії, політології та національної безпеки")
SNU_markup.row("Факультет хімії, екології та фармації")
SNU_markup.row("Юридичний факультет")
SNU_markup.row("Факультет міжнародних відносин")
SNU_markup.row("Факультет інформаційних технологій і математики")
SNU_markup.row("Навчально-науковий інститут неперервної освіти")
SNU_markup.row("Коледж технологій, бізнесу та права Східноєвропейського національного університету імені Лесі Українки")
SNU_markup.row("Факультет культури і мистецтв")
SNU_markup.row("Факультет психології та соціології")
SNU_markup.row("Медико-біологічний факультет")
SNU_markup.row("Географічний факультет")
SNU_markup.row("Підготовче відділення")
SNU_markup.row("Навчально-науковий фізико-технологічний інститут")
SNU_markup.row("Повідомити про проблему")

vote = types.ReplyKeyboardMarkup(True)
vote.row("👍")
vote.row("👎")

select = types.ReplyKeyboardMarkup(True)
select.row("5 випадкових")
select.row("5 популярних")

remove_keyboard = types.ReplyKeyboardRemove()

about_inline = types.InlineKeyboardMarkup(True)
url_buttom = types.InlineKeyboardButton(text='Швидкий перехід:', url='http://www.studitor.com')
about_inline.add(url_buttom)


# Empty webserver index, return nothing, just http 200
@app.route('/', methods=['GET', 'HEAD'])
def index():
    return ''


def listToString(s):
    str1 = ""
    for ele in s:
        str1 = str1 + " " + ele
    return str1


def listToString2(s):
    str1 = ""
    for ele in s:
        str1 = str(str1) + " " + str(ele)
    return str1


def extract_unique_code(text):
    # Extracts the unique_code from the sent /start command.
    return text.split()[1] if len(text.split()) > 1 else None


# Process webhook calls
@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    print(call.message.chat.id)
    print(call.data)
    if call.message:
        data = call.data
        data = data.split(" ")
        id = data[0]
        vote = data[1]
        cursor.execute("SELECT voted FROM petition_void WHERE id="+str(id))
        voted = cursor.fetchone()
        print(voted)
        print(call.message.message_id)
        if voted[0] is None:
            cursor.execute("UPDATE petition_void SET voted='"+str(call.message.chat.id)+" 1' WHERE id="+str(id))
            if vote == "yes":
                cursor.execute("SELECT yes FROM petition_void WHERE id="+str(id))
                count = cursor.fetchone()[0]
                cursor.execute("UPDATE petition_void SET yes="+str(int(count) + 1)+" WHERE id="+str(id))
                print(call.message.message_id)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Ви проголосували за.")
            if vote == "no":
                cursor.execute("SELECT no FROM petition_void WHERE id="+str(id))
                count = cursor.fetchone()[0]
                cursor.execute("UPDATE petition_void SET no="+str(int(count) + 1)+" WHERE id="+str(id))
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Ви проголосували проти.")
            bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text="Ви успішно проголосували.")

        else:
            list = voted[0].split(" ")
            if str(call.message.chat.id) in list:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Ви вже голосували.")
                bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text="Ви вже голосували")
            else:
                new_voted = voted[0] + " " + str(call.message.chat.id)
                cursor.execute("UPDATE petition_void SET voted='"+str(new_voted)+"' WHERE id="+str(id))
                if vote == "yes":
                    cursor.execute("SELECT yes FROM petition_void WHERE id=" + str(id))
                    count = cursor.fetchone()[0]
                    cursor.execute("UPDATE petition_void SET yes=" + str(int(count) + 1) + " WHERE id=" + str(id))
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Ви проголосували за.")
                if vote == "no":
                    cursor.execute("SELECT yes FROM petition_void WHERE id=" + str(id))
                    count = cursor.fetchone()[0]
                    cursor.execute("UPDATE petition_void SET yes=" + str(int(count) + 1) + " WHERE id=" + str(id))
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Ви проголосували проти.")
                bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text="Ви успішно проголосували.")


@bot.message_handler(commands=['codes'])
def codes(message):
    cursor.execute("SELECT codes FROM users WHERE id={}".format(str(message.from_user.id)))
    codes = cursor.fetchone()
    if codes[0] is None:
        bot.send_message(message.from_user.id, "У вас немає жодного коду.")
    else:
        codes_list = codes[0].split(" ")
        print(codes_list)
        text = "Ваші giveaway коди:"
        for code in codes_list:
            text = text + "\n" + code
        bot.send_message(message.from_user.id, text)



@bot.message_handler(commands=['call'])
def call(message):
    if message.chat.id == admin_chat_id:
        id = message.text.split(' ')[1]
        cursor.execute("UPDATE users SET caller='" + str(message.from_user.id) + "' WHERE id=" + str(id))
        cursor.execute("UPDATE users SET caller='" + str(id) + "' WHERE id=" + str(message.from_user.id))
        cursor.execute("UPDATE users SET step='calling' WHERE id=" + str(id))
        cursor.execute("UPDATE users SET step='calling' WHERE id=" + str(message.from_user.id))
        bot.send_message(message.from_user.id, "Перевірка підключення")
        try:
            bot.send_message(id, "До вас підключився адміністратор.")
            bot.send_message(message.from_user.id, "Підключено. Для кінця розмови напишіть /end в чаті адміністраторів.")
        except Exception as e:
            bot.send_message(message.from_user.id, "Підключення не вдалось. Помилка:\n" + str(e))
            cursor.execute("UPDATE users SET caller='0' WHERE id=" + str(id))
            cursor.execute("UPDATE users SET caller='0' WHERE id=" + str(message.from_user.id))
            cursor.execute("UPDATE users SET step='main_menu' WHERE id=" + str(id))
            cursor.execute("UPDATE users SET step='main_menu' WHERE id=" + str(message.from_user.id))

@bot.message_handler(commands=["end"])
def end_call(message):
    if message.chat.id == admin_chat_id:
       cursor.execute("SELECT caller FROM users WHERE id={}".format(message.from_user.id))
       data = cursor.fetchone()
       cursor.execute("UPDATE users SET step='main_menu' WHERE id={}".format(data[0]))
       bot.send_message(data[0], "Адміністратор відключився", reply_markup=main_menu)
       cursor.execute("UPDATE users SET step='main_menu' WHERE id={}".format(message.from_user.id))
       bot.send_message(admin_chat_id, 'Success')

@bot.message_handler(commands=['apply'])
def apply(message):
    if message.chat.id == admin_chat_id:
        id = message.text.split(' ')[1]
        print(id)
        bot.send_message(message.chat.id, 'Окей. Включаю видимість.')
        cursor.execute("UPDATE petitions SET visible=1 WHERE petition_id=" + str(id))
        cursor.execute("SELECT * FROM petitions WHERE petition_id=" + str(id))
        data = cursor.fetchone()
        cursor.execute("UPDATE petitions SET signatures='" + str(data[1]) + "' WHERE petition_id=" + str(id))
        bot.send_message(data[1], 'Ваша петиція <i>\n\n"' + str(data[4]) + '"</i>\n\nбула опублікована.',
                         parse_mode='HTML')


@bot.message_handler(commands=['view'])
def view(message):
    if message.chat.type == "private":
        id = message.text.split(' ')[1]
        print(id)
        cursor.execute("SELECT * FROM petition_void WHERE id=" + str(id))
        data = cursor.fetchone()
        cursor.execute("UPDATE users SET vote_id='" + str(id) + "' WHERE id=" + str(message.from_user.id))
        cursor.execute("UPDATE users SET step='voting' WHERE id=" + str(message.from_user.id))
        bot.send_message(message.from_user.id,
                         "Проблема #" + str(id) + "\n" + str(data[1]) + "\n👍" + str(data[2]) + "|👎" + str(data[3]),
                         reply_markup=vote)


@bot.message_handler(commands=['broadcast'])
def broadcast_handler(message):
    if message.chat.id == admin_chat_id:
        broadcast_message = message.text.split(" ")
        broadcast_message.pop(0)
        msg = listToString(broadcast_message)
        cursor.execute("SELECT id FROM users")
        ids = cursor.fetchall()
        print(ids)
        count = len(ids)
        new_count = 0
        for id in ids:
            try:
                time.sleep(0.3)
                bot.send_message(id[0], msg, reply_markup=main_menu)
                cursor.execute("UPDATE users SET step='main_menu' WHERE id="+str(id[0]))
                new_count += 1
            except:
                pass
        bot.send_message(admin_chat_id, 'Відправлено ' + str(count) + ' користувачам.\nОтримали ' + str(new_count))


@bot.message_handler(commands=['start'])
def start_handler(message):
    if message.chat.type == 'private':
        try:
            unique_code = extract_unique_code(message.text)
            print(message.from_user.id)
            cursor.execute("SELECT step FROM users WHERE id=" + str(message.from_user.id))
            data = cursor.fetchone()
            print(data)
            if data is None:
                cursor.execute("INSERT INTO users(id,step) VALUES('" + str(message.from_user.id) + "', 'main_menu')")
                bot.send_message(message.from_user.id, """
                Привіт, """ + str(message.from_user.first_name) + """☺
🎓Studitor
❕Це платформа, яка поєднує студентів, які бачать проблеми університетів та адміністрацію, яка може їх вирішити
                """, reply_markup=main_menu)
                if unique_code:
                    print(unique_code)
                    cursor.execute("UPDATE users SET start_provider='" + str(unique_code) + "' WHERE id=" + str(
                        message.from_user.id))
            else:
                if data[0] == "calling":
                    pass
                else:
                    bot.send_message(message.from_user.id, """Привіт, """ + str(message.from_user.first_name) + """
🎓Studitor
❕Це платформа, яка поєднує студентів, які бачать проблеми університетів та адміністрацію, яка може їх вирішити""",
                                     reply_markup=main_menu)
                    cursor.execute("UPDATE users SET step='main_menu' WHERE id=" + str(message.from_user.id))
        except:
            cnx.reconnect(10, 1)




@bot.message_handler(content_types=['text'])
def text_handler(message):
    try:
        cnx.reconnect(1, 0)
        print(message.text)
        if message.chat.type == 'private':
            cursor.execute("SELECT step FROM users WHERE id=" + str(message.from_user.id))
            data = cursor.fetchone()
            print(data)
            if data[0] == "uni_vote_select":
                bot.send_message(message.from_user.id, "Супер. Тепер я знаю проблеми якого універа вам показувати.", reply_markup=main_menu)
                cursor.execute("UPDATE users SET uni='{}' WHERE id={}".format(message.text, message.from_user.id))
                cursor.execute("UPDATE users SET step='main_menu' WHERE id={}".format(message.from_user.id))
            if data[0] == 'calling':
                cursor.execute("SELECT caller FROM users WHERE id={}".format(message.from_user.id))
                uid = cursor.fetchone()
                print(uid)
                bot.send_message(uid[0], message.text)
                print(message.text)
            if data[0] == 'select':
                if message.text == "5 випадкових":
                    cursor.execute("SELECT uni FROM users WHERE id=" + str(message.from_user.id))
                    uni = cursor.fetchone()[0]
                    print(uni)
                    if uni is None:
                        cursor.execute("UPDATE users SET step='uni_vote_select' WHERE id=" + str(message.from_user.id))
                        bot.send_message(message.from_user.id, "Будь ласка, оберіть ваш університет щоб продовжити.",
                                         reply_markup=uni_markup)
                    else:
                        print("else")
                        cursor.execute("SELECT uni FROM users WHERE id=" + str(message.from_user.id))
                        uni = cursor.fetchone()[0]
                        cursor.execute("SELECT MAX(view) FROM petition_void")
                        maximal = cursor.fetchone()[0]
                        print(maximal)
                        cursor.execute(
                            "SELECT petition_add.id FROM petition_add INNER JOIN petition_void ON "
                            "petition_add.id=petition_void.id WHERE petition_add.university='" + str(
                                uni) + "' AND view < " + str(maximal) + " ORDER BY RAND() LIMIT 5")
                        c = cursor.fetchall()
                        print(c)
                        if c == []:
                            print("true")
                            cursor.execute(
                                "SELECT petition_add.id FROM petition_add INNER JOIN petition_void ON "
                                "petition_add.id=petition_void.id WHERE petition_add.university='" + str(
                                    uni) + "' ORDER BY RAND() LIMIT 5")
                            c = cursor.fetchall()
                            print(c)
                            for d in c:
                                time.sleep(1)
                                print(d[0])
                                cursor.execute(
                                    "SELECT petition_add.title, petition_void.yes, petition_void.no FROM petition_add "
                                    "INNER JOIN petition_void ON petition_add.id=petition_void.id WHERE "
                                    "petition_void.id=" + str(d[0]) + " ORDER BY RAND() LIMIT 5")
                                info = cursor.fetchone()
                                print(info)
                                keyboard = types.InlineKeyboardMarkup()
                                yes_button = types.InlineKeyboardButton(text="👍", callback_data=str(d[0]) + " yes")
                                no_button = types.InlineKeyboardButton(text="👎", callback_data=str(d[0]) + " no")
                                keyboard.add(yes_button)
                                keyboard.add(no_button)
                                bot.send_message(message.from_user.id,
                                                 "Проблема #" + str(d[0]) + ":\n" + str(
                                                     info[0]) + "\n\n👍" + str(
                                                     info[1]) + "|👎" + str(
                                                     info[2]), parse_mode="HTML", reply_markup=keyboard)
                                cursor.execute("SELECT view FROM petition_void WHERE id=" + str(d[0]))
                                views = cursor.fetchone()[0]
                                cursor.execute(
                                    "UPDATE petition_void SET view='" + str(views + 1) + "' WHERE id=" + str(d[0]))
                            bot.send_message(message.from_user.id,
                                             "Щоб проголосувати за проблему введіть команду під проблемою.",
                                             reply_markup=main_menu)
                            cursor.execute("UPDATE users SET step='main_menu' WHERE id=" + str(message.from_user.id))
                        else:
                            for id in c:
                                time.sleep(1)
                                print(id[0])
                                cursor.execute(
                                    "SELECT petition_add.title, petition_void.yes, petition_void.no FROM petition_add "
                                    "INNER JOIN petition_void ON petition_add.id=petition_void.id WHERE "
                                    "petition_void.id=" + str(
                                        id[0]))
                                data = cursor.fetchone()
                                print(data)
                                keyboard = types.InlineKeyboardMarkup()
                                yes_button = types.InlineKeyboardButton(text="👍", callback_data=str(id[0]) + " yes")
                                no_button = types.InlineKeyboardButton(text="👎", callback_data=str(id[0]) + " no")
                                keyboard.add(yes_button, no_button)
                                bot.send_message(message.from_user.id,
                                                 "Проблема #" + str(id[0]) + ":\n" + str(data[0]) + "\n\n👍" + str(
                                                     data[1]) + "|👎" + str(
                                                     data[2]),parse_mode="HTML",reply_markup=keyboard)
                                cursor.execute("SELECT view FROM petition_void WHERE id=" + str(id[0]))
                                views = cursor.fetchone()[0]
                                cursor.execute(
                                    "UPDATE petition_void SET view='" + str(views + 1) + "' WHERE id=" + str(id[0]))
                            cursor.execute("UPDATE users SET step='main_menu' WHERE id=" + str(message.from_user.id))
                            bot.send_message(message.chat.id, "Перегляньте ці проблеми. Вони потребують вашої уваги.",
                                             reply_markup=main_menu)
                if message.text == "5 популярних":
                    cursor.execute("SELECT uni FROM users WHERE id=" + str(message.from_user.id))
                    uni = cursor.fetchone()[0]
                    print(uni)
                    if uni is None:
                        cursor.execute("UPDATE users SET step='uni_vote_select' WHERE id=" + str(message.from_user.id))
                        bot.send_message(message.from_user.id, "Будь ласка, оберіть ваш університет щоб продовжити.",
                                         reply_markup=uni_markup)
                    else:
                        print("else")
                        cursor.execute("SELECT uni FROM users WHERE id=" + str(message.from_user.id))
                        uni = cursor.fetchone()[0]
                        cursor.execute("SELECT MAX(view) FROM petition_void")
                        maximal = cursor.fetchone()[0]
                        print(maximal)
                        cursor.execute(
                            "SELECT petition_add.id FROM petition_add INNER JOIN petition_void ON "
                            "petition_add.id=petition_void.id WHERE petition_add.university='" + str(
                                uni) + "' ORDER BY view DESC LIMIT 5")
                        c = cursor.fetchall()
                        print(c)
                        if c == []:
                            print("true")
                            cursor.execute(
                                "SELECT petition_add.id FROM petition_add INNER JOIN petition_void ON "
                                "petition_add.id=petition_void.id WHERE petition_add.university='" + str(
                                    uni) + "' ORDER BY view DESC LIMIT 5")
                            c = cursor.fetchall()
                            print(c)
                            for d in c:
                                time.sleep(1)
                                print(d[0])
                                cursor.execute(
                                    "SELECT petition_add.title, petition_void.yes, petition_void.no FROM petition_add "
                                    "INNER JOIN petition_void ON petition_add.id=petition_void.id WHERE "
                                    "petition_void.id=" + str(d[0]) + " ORDER BY view DESC LIMIT 5")
                                info = cursor.fetchone()
                                print(info)
                                keyboard = types.InlineKeyboardMarkup()
                                yes_button = types.InlineKeyboardButton(text="👍", callback_data=str(d[0]) + " yes")
                                no_button = types.InlineKeyboardButton(text="👎", callback_data=str(d[0]) + " no")
                                keyboard.add(yes_button, no_button)
                                bot.send_message(message.from_user.id,
                                                 "Проблема #" + str(d[0]) + ":\n" + str(data[0]) + "\n\n👍" + str(
                                                     data[1]) + "|👎" + str(
                                                     data[2]),parse_mode="HTML",reply_markup=keyboard)
                                cursor.execute("SELECT view FROM petition_void WHERE id=" + str(d[0]))
                                views = cursor.fetchone()[0]
                                cursor.execute(
                                    "UPDATE petition_void SET view='" + str(views + 1) + "' WHERE id=" + str(d[0]))
                            bot.send_message(message.from_user.id,
                                             "Щоб проголосувати за проблему введіть команду під проблемою.",
                                             reply_markup=main_menu)
                            cursor.execute("UPDATE users SET step='main_menu' WHERE id=" + str(message.from_user.id))
                        else:
                            for id in c:
                                time.sleep(1)
                                print(id[0])
                                cursor.execute(
                                    "SELECT petition_add.title, petition_void.yes, petition_void.no FROM petition_add "
                                    "INNER JOIN petition_void ON petition_add.id=petition_void.id WHERE "
                                    "petition_void.id=" + str(
                                        id[0]))
                                data = cursor.fetchone()
                                print(data)
                                keyboard = types.InlineKeyboardMarkup()
                                yes_button = types.InlineKeyboardButton(text="👍", callback_data=str(id[0]) + " yes")
                                no_button = types.InlineKeyboardButton(text="👎", callback_data=str(id[0]) + " no")
                                keyboard.add(yes_button, no_button)
                                bot.send_message(message.from_user.id,
                                                 "Проблема #" + str(id[0]) + ":\n" + str(data[0]) + "\n\n👍" + str(
                                                     data[1]) + "|👎" + str(
                                                     data[2]),parse_mode="HTML",reply_markup=keyboard)
                                cursor.execute("SELECT view FROM petition_void WHERE id=" + str(id[0]))
                                views = cursor.fetchone()[0]
                                cursor.execute(
                                    "UPDATE petition_void SET view='" + str(views + 1) + "' WHERE id=" + str(id[0]))
                            cursor.execute("UPDATE users SET step='main_menu' WHERE id=" + str(message.from_user.id))
                            bot.send_message(message.chat.id, "Перегляньте ці проблеми. Вони потребують вашої уваги.",reply_markup=main_menu)
            if data[0] == "main_menu":
                if message.text == "🎲Giveaway код":
                    cursor.execute("SELECT codes FROM users WHERE id={}".format(str(message.from_user.id)))
                    codes = cursor.fetchone()
                    if codes[0] is None:
                        bot.send_message(message.from_user.id, "У вас немає жодного коду.")
                    else:
                        codes_list = codes[0].split(" ")
                        print(codes_list)
                        text = "Ваш giveaway код:"
                        for code in codes_list:
                            text = text + " " + code
                        bot.send_message(message.from_user.id, text)
                if message.text == "🚀Про проект":
                    bot.send_message(message.from_user.id, 'Посилання на <a href="studitor.com">сайт</a>',
                                     reply_markup=about_inline, parse_mode='HTML')
                if message.text == "🤝Вирішити проблему":
                    bot.send_message(message.from_user.id, 'Які проблеми будем переглядати?', reply_markup=select)
                    cursor.execute("UPDATE users SET step='select' WHERE id=" + str(message.from_user.id))
                if message.text == "📢Повідомити про проблему":
                    bot.send_message(message.from_user.id,
                                     "Чудово. Зачекайте секунду...",
                                     reply_markup=remove_keyboard)
                    cursor.execute("SELECT uni FROM users WHERE id=" + str(message.from_user.id))
                    uni = cursor.fetchone()
                    print(uni)
                    if uni[0] is None:
                        bot.send_message(message.from_user.id,
                                         '🧑‍🎓Окей, виберіть будь ласка університет',
                                         reply_markup=uni_markup)
                        cursor.execute("UPDATE users SET step='uni_select' WHERE id=" + str(message.from_user.id))
                    else:
                        cursor.execute("SELECT * FROM users WHERE id=" + str(message.from_user.id))
                        data = cursor.fetchone()
                        if data[5] is None:
                            markup = None
                            if data[4] == "ЛНТУ":
                                markup = LNTU_markup
                            if data[4] == "СНУ":
                                markup = SNU_markup
                            bot.send_message(message.from_user.id,
                                             'Схоже ви не вибрали факультет. Чи не хочете ви його обрати?',
                                             reply_markup=markup)
                            cursor.execute("UPDATE users SET step='spec_select' WHERE id=" + str(message.from_user.id))
                        else:
                            cursor.execute("UPDATE users SET step='uni_reselect' WHERE id=" + str(message.from_user.id))
                            bot.send_message(message.from_user.id,
                                             'Хочете змінити університет і факультет?',
                                             reply_markup=change_uni)
            if data[0] == 'uni_reselect':
                if message.text == 'Так':
                    cursor.execute("UPDATE users SET step='uni_select' WHERE id=" + str(message.from_user.id))
                    bot.send_message(message.from_user.id,
                                     '🧑‍🎓Окей, виберіть будь ласка університет',
                                     reply_markup=uni_markup)
                if message.text == 'Ні':
                    cursor.execute("UPDATE users SET step='petition_text' WHERE id=" + str(message.from_user.id))
                    cursor.execute(
                        "INSERT INTO petitions(author, views) VALUES('" + str(message.from_user.id) + "','1')")
                    cursor.execute(
                        "SELECT MAX(petition_id) FROM petitions WHERE author='" + str(message.from_user.id) + "'")
                    petition_id = cursor.fetchone()[0]
                    cursor.execute(
                        "UPDATE users SET current='" + str(petition_id) + "' WHERE id=" + str(message.from_user.id))
                    bot.send_message(message.from_user.id,
                                     '⬇️Нижче ви можете повідомити про проблему та почати зміни уже зараз',
                                     reply_markup=remove_keyboard)
            if data[0] == "uni_select":
                if message.text == 'ЛНТУ':
                    bot.send_message(message.from_user.id, "Окей. З якого ви факультету?", reply_markup=LNTU_markup)
                    cursor.execute("UPDATE users SET uni='ЛНТУ' WHERE id=" + str(message.from_user.id))
                    cursor.execute("UPDATE users SET step='spec_select' WHERE id=" + str(message.from_user.id))
                if message.text == 'СНУ':
                    bot.send_message(message.from_user.id, "Окей. З якого ви факультету?", reply_markup=SNU_markup)
                    cursor.execute("UPDATE users SET uni='СНУ' WHERE id=" + str(message.from_user.id))
                    cursor.execute("UPDATE users SET step='spec_select' WHERE id=" + str(message.from_user.id))
            if data[0] == 'spec_select':
                if message.text == 'Повідомити про проблему':
                    cursor.execute("UPDATE users SET step='petition_text' WHERE id=" + str(message.from_user.id))
                    bot.send_message(message.from_user.id,
                                     '⬇️Нижче ви можете повідомити про проблему та почати зміни уже зараз',
                                     reply_markup=remove_keyboard)
                    cursor.execute(
                        "INSERT INTO petitions(author, views) VALUES('" + str(message.from_user.id) + "','1')")
                    cursor.execute(
                        "SELECT MAX(petition_id) FROM petitions WHERE author='" + str(message.from_user.id) + "'")
                    petition_id = cursor.fetchone()[0]
                    cursor.execute(
                        "UPDATE users SET current='" + str(petition_id) + "' WHERE id=" + str(message.from_user.id))
                else:
                    cursor.execute(
                        'UPDATE users SET spec="' + str(message.text) + '" WHERE id=' + str(message.from_user.id))
                    bot.send_message(message.from_user.id,
                                     '⬇️Нижче ви можете повідомити про проблему та почати зміни уже зараз',
                                     reply_markup=remove_keyboard)
                    cursor.execute(
                        "INSERT INTO petitions(author, views) VALUES('" + str(message.from_user.id) + "','1')")
                    cursor.execute(
                        "SELECT MAX(petition_id) FROM petitions WHERE author='" + str(message.from_user.id) + "'")
                    petition_id = cursor.fetchone()[0]
                    cursor.execute(
                        "UPDATE users SET current='" + str(petition_id) + "' WHERE id=" + str(message.from_user.id))
                    cursor.execute("UPDATE users SET step='petition_text' WHERE id=" + str(message.from_user.id))
            """if data[0] == 'petition_header':
                cursor.execute("SELECT current FROM users WHERE id="+str(message.from_user.id))
                petition_id = cursor.fetchone()[0]
                cursor.execute("UPDATE petitions SET heading='"+str(message.text)+"' WHERE petition_id="+str(petition_id))
                bot.send_message(message.from_user.id, "⬇️Нижче ви можете повідомити про проблему та почати зміни уже зараз")
                cursor.execute("UPDATE users SET step='petition_text' WHERE id=" + str(message.from_user.id))"""
            if data[0] == 'petition_text':
                cursor.execute("SELECT current FROM users WHERE id=" + str(message.from_user.id))
                petition_id = cursor.fetchone()[0]
                cursor.execute(
                    "UPDATE petitions SET text='" + str(message.text) + "' WHERE petition_id=" + str(petition_id))
                cursor.execute("SELECT author FROM users WHERE id=" + str(message.from_user.id))
                author = cursor.fetchone()[0]
                print(author)
                if author is None:
                    new_author = petition_id
                    cursor.execute("UPDATE users SET author='" + str(new_author) + "' WHERE id=" + str(message.chat.id))
                else:
                    new_author = str(author) + ' ' + str(petition_id)
                    cursor.execute("UPDATE users SET author='" + str(new_author) + "' WHERE id=" + str(message.chat.id))
                bot.send_message(message.from_user.id,
                                 '💡Дякуємо за те, що повідомили про проблему. Ваша петиція обробляється. Найближчим часом вона буде доступна для голосування.')
                bot.send_message(message.from_user.id, """
                                Привіт, """ + str(message.from_user.first_name) + """☺\n🎓Studitor\n❕Це платформа, яка поєднує студентів, які бачать проблеми університетів та адміністрацію, яка може їх вирішити
                                """, reply_markup=main_menu)
                cursor.execute("UPDATE users SET step='main_menu' WHERE id=" + str(message.from_user.id))
                cursor.execute("SELECT current FROM users WHERE id=" + str(message.from_user.id))
                petition_id = cursor.fetchone()[0]
                cursor.execute("SELECT * FROM petitions WHERE petition_id=" + str(petition_id))
                petition_info = cursor.fetchone()
                cursor.execute("UPDATE users SET current='0' WHERE id=" + str(message.from_user.id))
                bot.send_message(admin_chat_id, '<b>Нова петиція!</b>''\n' + str(
                    petition_info[4]) + '\n\nВключити видимість: <code>/apply ' + str(petition_info[0]) + '</code>\n'
                                                                                                          'Звязатись:<code>/call ' + str(
                    message.from_user.id) + '</code>',
                                 parse_mode='HTML')
    except:
        cnx.reconnect(10, 1)


# Remove webhook, it fails sometimes the set if there is a previous webhook
bot.remove_webhook()

time.sleep(1)

# Set webhook
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                certificate=open(WEBHOOK_SSL_CERT, 'r'))

# Start flask server
app.run(host=WEBHOOK_LISTEN,
        port=WEBHOOK_PORT,
        ssl_context=(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV),
        debug=True)

