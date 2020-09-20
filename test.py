import logging, time, flask, telebot, constants, mysql.connector from 
telebot import types cnx = 
mysql.connector.connect(host=constants.db_host,
                              user=constants.db_user,
                              password=constants.db_passwd,
                              database=constants.db_base) print(cnx) 
cursor = cnx.cursor(buffered=True) cnx.autocommit = True
# Webhook settings
WEBHOOK_HOST = constants.webhook_host WEBHOOK_PORT = 88 # 443, 80, 88 or 
8443 (port need to be 'open') WEBHOOK_LISTEN = '0.0.0.0' # In some VPS 
you may need to put here the IP addr WEBHOOK_SSL_CERT = 
'./webhook_cert.pem' # Path to the ssl certificate WEBHOOK_SSL_PRIV = 
'./webhook_pkey.pem' # Path to the ssl private key WEBHOOK_URL_BASE = 
"https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT) WEBHOOK_URL_PATH = "/%s/" 
% constants.token logger = telebot.logger 
telebot.logger.setLevel(logging.INFO)
# Init bot
bot = telebot.TeleBot(constants.token) app = flask.Flask(__name__)
# Keyboards
admin_chat_id = constants.admins main_menu = 
types.ReplyKeyboardMarkup(True) main_menu.row("📢Подати петицію") 
main_menu.row("🤝Підтримати петицію") main_menu.row("🚀Про проект") 
uni_markup = types.ReplyKeyboardMarkup(True) uni_markup.row("ЛНТУ") 
uni_markup.row("СНУ") change_uni = types.ReplyKeyboardMarkup(True) 
change_uni.row("Так") change_uni.row("Ні") LNTU_markup = 
types.ReplyKeyboardMarkup(True) LNTU_markup.row("Факультет комп'ютерних 
наук та інформаційних технологій") LNTU_markup.row("Технологічний 
факультет(ТФ)") LNTU_markup.row("Факультет архітектури, будівництва та 
дизайну ") LNTU_markup.row("Факультет фінансів, обліку, лінгвістики та 
права ") LNTU_markup.row("Машинобудівний факультет (МБФ)") 
LNTU_markup.row("Факультет екології, туризму та електроінженерії") 
LNTU_markup.row("Повідомити про проблему") SNU_markup = 
types.ReplyKeyboardMarkup(True) SNU_markup.row("Факультет фізичної 
культури, спорту та здоров'я") SNU_markup.row("Факультет педагогічної 
освіти та соціальної роботи") SNU_markup.row("Факультет економіки та 
управління") SNU_markup.row("Факультет іноземної філології") 
SNU_markup.row("Факультет філології та журналістики") 
SNU_markup.row("Факультет історії, політології та національної безпеки") 
SNU_markup.row("Факультет хімії, екології та фармації") 
SNU_markup.row("Юридичний факультет") SNU_markup.row("Факультет 
міжнародних відносин") SNU_markup.row("Факультет інформаційних 
технологій і математики") SNU_markup.row("Навчально-науковий інститут 
неперервної освіти") SNU_markup.row("Коледж технологій, бізнесу та права 
Східноєвропейського національного університету імені Лесі Українки") 
SNU_markup.row("Факультет культури і мистецтв") 
SNU_markup.row("Факультет психології та соціології") 
SNU_markup.row("Медико-біологічний факультет") 
SNU_markup.row("Географічний факультет") SNU_markup.row("Підготовче 
відділення") SNU_markup.row("Навчально-науковий фізико-технологічний 
інститут") SNU_markup.row("Повідомити про проблему") remove_keyboard = 
types.ReplyKeyboardRemove() about_inline = 
types.InlineKeyboardMarkup(True) url_buttom = 
types.InlineKeyboardButton(text='Швидкий перехід:', 
url='http://www.studitor.com') about_inline.add(url_buttom)
# Empty webserver index, return nothing, just http 200
@app.route('/', methods=['GET', 'HEAD']) def index():
    return '' def listToString(s):
    str1 = ""
    for ele in s:
        str1 = str1 + " " + ele
    return str1 def listToString2(s):
    str1 = ""
    for ele in s:
        str1 = str(str1) + " " + str(ele)
    return str1
# Process webhook calls
@app.route(WEBHOOK_URL_PATH, methods=['POST']) def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403) @bot.message_handler(commands=['apply']) def 
apply(message):
    if message.chat.id == admin_chat_id:
        id = message.text.split(' ')[1]
        print(id)
        bot.send_message(message.chat.id, 'Окей. Включаю видимість.')
        cursor.execute("UPDATE petitions SET visible=1 WHERE 
petition_id=" + str(id))
        cursor.execute("SELECT * FROM petitions WHERE petition_id=" + 
str(id))
        data = cursor.fetchone()
        cursor.execute("UPDATE petitions SET signatures='" + 
str(data[1]) + "' WHERE petition_id=" + str(id))
        bot.send_message(data[1], 'Ваша петиція <i>\n\n"' + str(data[4]) 
+ '"</i>\n\nбула опублікована.',
                         parse_mode='HTML') 
@bot.message_handler(commands=['broadcast']) def 
broadcast_handler(message):
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
                time.sleep(0.5)
                bot.send_message(id[0], msg)
                new_count += 1
            except:
                pass
        bot.send_message(admin_chat_id, 'Відправлено ' + str(count) + ' 
користувачам.\nОтримали ' + str(new_count)) 
@bot.message_handler(commands=['start']) def start_handler(message):
    if message.chat.type == 'private':
        try:
            print(message.from_user.id)
            cursor.execute("SELECT step FROM users WHERE id=" + 
str(message.from_user.id))
            data = cursor.fetchone()
            print(data)
            if data is None:
                cursor.execute("INSERT INTO users(id,step) VALUES('" + 
str(message.from_user.id) + "', 'main_menu')")
                bot.send_message(message.from_user.id, """
                Привіт, """ + str(message.from_user.first_name) + """☺ 
🎓Studitor ❕Це платформа, яка поєднує студентів, які бачать проблеми 
університетів та адміністрацію, яка може їх вирішити
                """, reply_markup=main_menu)
            else:
                bot.send_message(message.from_user.id, """Привіт, """ 
+str(message.from_user.first_name)+"""☺️ 🎓Studitor ❕Це платформа, яка 
поєднує студентів, які бачать проблеми університетів та адміністрацію, 
яка може їх вирішити""", reply_markup=main_menu)
                cursor.execute("UPDATE users SET step='main_menu' WHERE 
id="+str(message.from_user.id))
        except:
            pass @bot.message_handler(content_types=['text']) def 
text_handler(message):
    if message.chat.type == 'private':
        cursor.execute("SELECT step FROM users WHERE id=" + 
str(message.from_user.id))
        data = cursor.fetchone()
        print(data)
        if data[0] == "main_menu":
            if message.text == "🚀Про проект":
                bot.send_message(message.from_user.id, 'Посилання на <a 
href="studitor.com">сайт</a>',
                                 reply_markup=about_inline, 
parse_mode='HTML')
            if message.text == "🤝Підтримати петицію":
                bot.send_message(message.from_user.id, 'Окей. Які 
петиції хочете переглян')
            if message.text == "📢Подати петицію":
                bot.send_message(message.from_user.id,
                                 "Чудово. Зачекайте секунду...",
                                 reply_markup=remove_keyboard)
                cursor.execute("SELECT uni FROM users WHERE id=" + 
str(message.from_user.id))
                uni = cursor.fetchone()
                print(uni)
                if uni[0] is None:
                    bot.send_message(message.from_user.id,
                                     '🧑‍🎓Окей, виберіть будь ласка 
університет',
                                     reply_markup=uni_markup)
                    cursor.execute("UPDATE users SET step='uni_select' 
WHERE id=" + str(message.from_user.id))
                else:
                    cursor.execute("SELECT * FROM users WHERE id=" + 
str(message.from_user.id))
                    data = cursor.fetchone()
                    if data[5] is None:
                        markup = None
                        if data[4] == "ЛНТУ":
                            markup = LNTU_markup
                        if data[4] == "СНУ":
                            markup = SNU_markup
                        bot.send_message(message.from_user.id,
                                         'Схоже ви не вибрали факультет. 
Чи не хочете ви його обрати?',
                                         reply_markup=markup)
                        cursor.execute("UPDATE users SET 
step='spec_select' WHERE id=" + str(message.from_user.id))
                    else:
                        cursor.execute("UPDATE users SET 
step='uni_reselect' WHERE id=" + str(message.from_user.id))
                        bot.send_message(message.from_user.id,
                                         'Хочете змінити університет і 
факультет?',
                                         reply_markup=change_uni)
        if data[0] == 'uni_reselect':
            if message.text == 'Так':
                cursor.execute("UPDATE users SET step='uni_select' WHERE 
id=" + str(message.from_user.id))
                bot.send_message(message.from_user.id,
                                 '🧑‍🎓Окей, виберіть будь ласка 
університет',
                                 reply_markup=uni_markup)
            if message.text == 'Ні':
                cursor.execute("UPDATE users SET step='petition_text' 
WHERE id=" + str(message.from_user.id))
                cursor.execute(
                    "INSERT INTO petitions(author, views) VALUES('" + 
str(message.from_user.id) + "','1')")
                cursor.execute(
                    "SELECT MAX(petition_id) FROM petitions WHERE 
author='" + str(message.from_user.id) + "'")
                petition_id = cursor.fetchone()[0]
                cursor.execute(
                    "UPDATE users SET current='" + str(petition_id) + "' 
WHERE id=" + str(message.from_user.id))
                bot.send_message(message.from_user.id,
                                 '⬇️Нижче ви можете повідомити про 
проблему та почати зміни уже зараз',
                                 reply_markup=remove_keyboard)
        if data[0] == "uni_select":
            if message.text == 'ЛНТУ':
                bot.send_message(message.from_user.id, "Окей. З якого ви 
факультету?", reply_markup=LNTU_markup)
                cursor.execute("UPDATE users SET uni='ЛНТУ' WHERE id=" + 
str(message.from_user.id))
                cursor.execute("UPDATE users SET step='spec_select' 
WHERE id=" + str(message.from_user.id))
            if message.text == 'СНУ':
                bot.send_message(message.from_user.id, "Окей. З якого ви 
факультету?", reply_markup=SNU_markup)
                cursor.execute("UPDATE users SET uni='СНУ' WHERE id=" + 
str(message.from_user.id))
                cursor.execute("UPDATE users SET step='spec_select' 
WHERE id=" + str(message.from_user.id))
        if data[0] == 'spec_select':
            if message.text == 'Повідомити про проблему':
                cursor.execute("UPDATE users SET step='petition_text' 
WHERE id=" + str(message.from_user.id))
                bot.send_message(message.from_user.id,
                                 '⬇️Нижче ви можете повідомити про 
проблему та почати зміни уже зараз',
                                 reply_markup=remove_keyboard)
                cursor.execute("INSERT INTO petitions(author, views) 
VALUES('" + str(message.from_user.id) + "','1')")
                cursor.execute(
                    "SELECT MAX(petition_id) FROM petitions WHERE 
author='" + str(message.from_user.id) + "'")
                petition_id = cursor.fetchone()[0]
                cursor.execute(
                    "UPDATE users SET current='" + str(petition_id) + "' 
WHERE id=" + str(message.from_user.id))
            else:
                cursor.execute(
                    'UPDATE users SET spec="' + str(message.text) + '" 
WHERE id=' + str(message.from_user.id))
                bot.send_message(message.from_user.id,
                                 '⬇️Нижче ви можете повідомити про 
проблему та почати зміни уже зараз',
                                 reply_markup=remove_keyboard)
                cursor.execute("INSERT INTO petitions(author, views) 
VALUES('" + str(message.from_user.id) + "','1')")
                cursor.execute(
                    "SELECT MAX(petition_id) FROM petitions WHERE 
author='" + str(message.from_user.id) + "'")
                petition_id = cursor.fetchone()[0]
                cursor.execute(
                    "UPDATE users SET current='" + str(petition_id) + "' 
WHERE id=" + str(message.from_user.id))
                cursor.execute("UPDATE users SET step='petition_text' 
WHERE id=" + str(message.from_user.id))
        """if data[0] == 'petition_header':
            cursor.execute("SELECT current FROM users WHERE 
id="+str(message.from_user.id))
            petition_id = cursor.fetchone()[0]
            cursor.execute("UPDATE petitions SET 
heading='"+str(message.text)+"' WHERE petition_id="+str(petition_id))
            bot.send_message(message.from_user.id, "⬇️Нижче ви можете 
повідомити про проблему та почати зміни уже зараз")
            cursor.execute("UPDATE users SET step='petition_text' WHERE 
id=" + str(message.from_user.id))"""
        if data[0] == 'petition_text':
            cursor.execute("SELECT current FROM users WHERE id=" + 
str(message.from_user.id))
            petition_id = cursor.fetchone()[0]
            cursor.execute("""UPDATE petitions SET text=\"""" + 
str(message.text) + """\" WHERE petition_id=""" + str(petition_id))
            cursor.execute("SELECT author FROM users WHERE id=" + 
str(message.from_user.id))
            author = cursor.fetchone()[0]
            print(author)
            if author is None:
                new_author = petition_id
                cursor.execute("UPDATE users SET author='" + 
str(new_author) + "' WHERE id=" + str(message.chat.id))
            else:
                new_author = str(author) + ' ' + str(petition_id)
                cursor.execute("UPDATE users SET author='" + 
str(new_author) + "' WHERE id=" + str(message.chat.id))
            bot.send_message(message.from_user.id,
                             '💡Дякуємо за те, що повідомили про 
проблему. Ваша петиція обробляється. Найближчим часом вона буде доступна 
для голосування.')
            bot.send_message(message.from_user.id, """
                            Привіт, """ + 
str(message.from_user.first_name) + """☺\n🎓Studitor\n❕Це платформа, 
яка поєднує студентів, які бачать проблеми університетів та 
адміністрацію, яка може їх вирішити
                            """, reply_markup=main_menu)
            cursor.execute("UPDATE users SET step='main_menu' WHERE id=" 
+ str(message.from_user.id))
            cursor.execute("SELECT current FROM users WHERE id=" + 
str(message.from_user.id))
            petition_id = cursor.fetchone()[0]
            cursor.execute("SELECT * FROM petitions WHERE petition_id=" 
+ str(petition_id))
            petition_info = cursor.fetchone()
            cursor.execute("UPDATE users SET current='0' WHERE id=" + 
str(message.from_user.id))
            bot.send_message(admin_chat_id, '<b>Нова петиція!</b>''\n' + 
str(
                petition_info[4]) + '\n\nВключити видимість: 
<code>/apply ' + str(petition_info[0]) + '</code>',
                             parse_mode='HTML')
# Remove webhook, it fails sometimes the set if there is a previous 
# webhook
bot.remove_webhook() time.sleep(0.1)
# Set webhook
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                certificate=open(WEBHOOK_SSL_CERT, 'r'))
# Start flask server
app.run(host=WEBHOOK_LISTEN,
        port=WEBHOOK_PORT,
        ssl_context=(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV),
        debug=True)
