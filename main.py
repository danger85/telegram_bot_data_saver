import telebot
from telebot.apihelper import ApiTelegramException
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
import json
from bs4 import BeautifulSoup
import requests
from time import sleep

bot = telebot.TeleBot("...PLEASE FILL IN...")
get_date, id_to_delete, qty_out_text, table_in_use, mul_div = "", "", "", "birthdays", "div"
bot_id = 5148261882
user_id, page, total_pages, additional, qty_out, yn_id, cur_col, exchange_k = 0, 0, 0, 0, 10, 1, 0, 0
active_table_columns, got_data = [], []
is_date_in = False
messages_dict = {}


def markup_param(c_f):
    print(f"\tcame from {c_f} in markup_param")
    global table_in_use
    m_up_param = InlineKeyboardMarkup()
    ikb = InlineKeyboardButton
    m_up_param.add(ikb(text=f"Кол-во записей вывода (тек. знач = {qty_out})",
                       callback_data="{\"Kb\":\"param\",\"V\":\"qty_out\",\"CF\":\"parameters\"}"))
    m_up_param.add(ikb(text="Отобр. id(тек. знач = "+("Да" if yn_id == 1 else "Нет")+")",
                       callback_data="{\"Kb\":\"param\",\"V\":\"yn_id\",\"CF\":\"parameters\"}"))
    m_up_param.add(ikb(text="Создать новую таблицу",
                       callback_data="{\"Kb\":\"param\",\"V\":\"cr_t\",\"CF\":\"parameters\"}"))
    m_up_param.add(ikb(text=f"Выбрать таблицу для заполнения (тек. = {table_in_use})",
                       callback_data="{\"Kb\":\"param\",\"V\":\"ch_t\",\"CF\":\"parameters\"}"))
    m_up_param.add(ikb(text="Выйти из меню",
                       callback_data="{\"Kb\":\"param\",\"V\":\"leave\",\"CF\":\"parameters\"}"))
    return m_up_param


def markup_menu(came_from):
    print(f"\tCame from {came_from} to markup_menu, qty_out={qty_out}")
    # print("\t", messages_dict)
    m_up_menu = InlineKeyboardMarkup()
    ikb = InlineKeyboardButton
    m_up_menu.add(ikb(text="Отобразить все ", callback_data="{\"Kb\":\"menu\",\"V\":\"show\",\"CF\":\"" + came_from + "\"}"))
    m_up_menu.add(ikb(text="Добавить событ.", callback_data="{\"Kb\":\"menu\",\"V\":\"add\",\"CF\":\"" + came_from + "\"}"),
                  ikb(text="Удалить событ. ", callback_data="{\"Kb\":\"menu\",\"V\":\"delete\",\"CF\":\"" + came_from + "\"}"))
    return m_up_menu


def markup_navi(p: int, t_p: int, c_f: str):
    t_p = (0 if t_p < 0 else t_p)
    print(f"\tCame from {c_f} to markup_navi, with parameters: page = {p}, and  total_pages = {t_p}")
    m_up_navi = InlineKeyboardMarkup()
    ikb = InlineKeyboardButton
    if p == 0 and t_p == 0:
        m_up_navi.add(
            ikb("Стоп", callback_data="{\"Kb\":\"navi\",\"V\":\"stop\",\"CF\":\"" + str(p) + "\",\"TP\":\"" + str(t_p) + "\"}"))
    elif p == t_p and p != 1:
        m_up_navi.add(
            ikb("Предыд.", callback_data="{\"Kb\":\"navi\",\"V\":\"prev\",\"CF\":\"" + str(p) + "\",\"Tp\":\"" + str(t_p) + "\"}"),
            ikb("Стоп", callback_data="{\"Kb\":\"navi\",\"V\":\"stop\",\"CF\":\"" + str(p) + "\",\"TP\":\"" + str(t_p) + "\"}")
        )
    elif p == 0 and t_p != 0:
        m_up_navi.add(
            ikb("Стоп", callback_data="{\"Kb\":\"navi\",\"V\":\"stop\",\"CF\":\"" + str(p) + "\",\"TP\":\"" + str(t_p) + "\"}"),
            ikb("След.", callback_data="{\"Kb\":\"navi\",\"V\":\"next\",\"CF\":\"" + str(p) + "\",\"TP\":\"" + str(t_p) + "\"}"))
    else:
        m_up_navi.add(
            ikb("Предыд.", callback_data="{\"Kb\":\"navi\",\"V\":\"prev\",\"CF\":\"" + str(p) + "\",\"TP\":\"" + str(t_p) + "\"}"),
            ikb("Стоп", callback_data="{\"Kb\":\"navi\",\"V\":\"stop\",\"CF\":\"" + str(p) + "\",\"TP\":\"" + str(t_p) + "\"}"),
            ikb("След.", callback_data="{\"Kb\":\"navi\",\"V\":\"next\",\"CF\":\"" + str(p) + "\",\"TP\":\"" + str(t_p) + "\"}"))
    return m_up_navi


def markup_num(c_f: str, val: str):
    print(f"\tCame from {c_f} in markup_num, markup layout ")
    print(f"\tmessage is {val}, lh = {len(val)}")
    lh = len(val)
    m_up_num = InlineKeyboardMarkup(row_width=3)
    ikb = InlineKeyboardButton

    def _num_one_to_nine():
        m_up_num.add(ikb(text="7", callback_data="{\"Kb\":\"num\",\"V\":\"7\",\"CF\":\"" + c_f + "\"}"),
                     ikb(text="8", callback_data="{\"Kb\":\"num\",\"V\":\"8\",\"CF\":\"" + c_f + "\"}"),
                     ikb(text="9", callback_data="{\"Kb\":\"num\",\"V\":\"9\",\"CF\":\"" + c_f + "\"}")
                     )
        m_up_num.add(ikb(text="4", callback_data="{\"Kb\":\"num\",\"V\":\"4\",\"CF\":\"" + c_f + "\"}"),
                     ikb(text="5", callback_data="{\"Kb\":\"num\",\"V\":\"5\",\"CF\":\"" + c_f + "\"}"),
                     ikb(text="6", callback_data="{\"Kb\":\"num\",\"V\":\"6\",\"CF\":\"" + c_f + "\"}")
                     )
        m_up_num.add(ikb(text="1", callback_data="{\"Kb\":\"num\",\"V\":\"1\",\"CF\":\"" + c_f + "\"}"),
                     ikb(text="2", callback_data="{\"Kb\":\"num\",\"V\":\"2\",\"CF\":\"" + c_f + "\"}"),
                     ikb(text="3", callback_data="{\"Kb\":\"num\",\"V\":\"3\",\"CF\":\"" + c_f + "\"}")
                     )

    if c_f == "fill_table" and lh == 0 or val == "_":  # первая цифра дня
        m_up_num.add(ikb(text="1", callback_data="{\"Kb\":\"num\",\"V\":\"1\",\"CF\":\"" + c_f + "\"}"),
                     ikb(text="2", callback_data="{\"Kb\":\"num\",\"V\":\"2\",\"CF\":\"" + c_f + "\"}"),
                     ikb(text="3", callback_data="{\"Kb\":\"num\",\"V\":\"3\",\"CF\":\"" + c_f + "\"}")
                     )
        if val != 0:
            m_up_num.add(ikb(text="0", callback_data="{\"Kb\":\"num\",\"V\":\"0\",\"CF\":\"" + c_f + "\"}"))

    if c_f == "fill_table" and lh == 1:  # вторая цифра дня
        if val == "3":  # а первой является ...
            m_up_num.add(ikb(text="1", callback_data="{\"Kb\":\"num\",\"V\":\"1\",\"CF\":\"" + c_f + "\"}"))
            m_up_num.add(ikb(text="0", callback_data="{\"Kb\":\"num\",\"V\":\"0\",\"CF\":\"" + c_f + "\"}"))
        if val == "0":
            _num_one_to_nine()
        if val in str(list(range(1, 3))):
            _num_one_to_nine()
            m_up_num.add(ikb(text="0", callback_data="{\"Kb\":\"num\",\"V\":\"0\",\"CF\":\"" + c_f + "\"}"))

    if c_f == "fill_table" and lh == 3:  # первая цифра месяца
        m_up_num.add(ikb(text="1", callback_data="{\"Kb\":\"num\",\"V\":\"1\",\"CF\":\"" + c_f + "\"}"))
        m_up_num.add(ikb(text="0", callback_data="{\"Kb\":\"num\",\"V\":\"0\",\"CF\":\"" + c_f + "\"}"))

    if c_f == "fill_table" and lh == 4:  # вторая цифра месяца
        print(f"\t ({val[0:2]}, {type(val[0:2])}) , ({val[-1]},{type(val[-1])})")
        if val[0:2] == "31":
            if val[0:2] == "31" and val[-1] == "0":
                m_up_num.add(ikb(text="июля", callback_data="{\"Kb\":\"num\",\"V\":\"7\",\"CF\":\"" + c_f + "\"}"))
                m_up_num.add(ikb(text="января", callback_data="{\"Kb\":\"num\",\"V\":\"1\",\"CF\":\"" + c_f + "\"}"),
                             ikb(text="марта", callback_data="{\"Kb\":\"num\",\"V\":\"2\",\"CF\":\"" + c_f + "\"}"),
                             ikb(text="мая", callback_data="{\"Kb\":\"num\",\"V\":\"3\",\"CF\":\"" + c_f + "\"}"))
            if val[0:2] == "31" and val[-1] == "1":
                m_up_num.add(ikb(text="декабря", callback_data="{\"Kb\":\"num\",\"V\":\"2\",\"CF\":\"" + c_f + "\"}"))
                m_up_num.add(ikb(text="октября", callback_data="{\"Kb\":\"num\",\"V\":\"0\",\"CF\":\"" + c_f + "\"}"))
        else:
            if val[-1] == "0":
                _num_one_to_nine()
            if val[-1] == "1":
                m_up_num.add(ikb(text="1", callback_data="{\"Kb\":\"num\",\"V\":\"1\",\"CF\":\"" + c_f + "\"}"),
                             ikb(text="2", callback_data="{\"Kb\":\"num\",\"V\":\"2\",\"CF\":\"" + c_f + "\"}"))
                m_up_num.add(ikb(text="0", callback_data="{\"Kb\":\"num\",\"V\":\"0\",\"CF\":\"" + c_f + "\"}"))

    if c_f == "fill_table" and lh in list(range(6, 10)):
        _num_one_to_nine()
        m_up_num.add(ikb(text="0", callback_data="{\"Kb\":\"num\",\"V\":\"0\",\"CF\":\"" + c_f + "\"}"))

    if c_f == "fill_table" and lh <= 10:
        m_up_num.add(ikb(text="Очистить", callback_data="{\"Kb\":\"num\",\"V\":\"cls\",\"CF\":\"fill_table\"}"))
        if lh in list(range(7, 11)):
            m_up_num.add(ikb(text="↲ Ввод", callback_data="{\"Kb\":\"func_key\",\"V\":\"enter\",\"CF\":\"fill_table\"}"))

    if c_f == "delete":
        _num_one_to_nine()
        m_up_num.add(ikb(text="Удалить id", callback_data="{\"Kb\":\"func_key\",\"V\":\"enter\",\"CF\":\"delete\"}"),
                     ikb(text="0", callback_data="{\"Kb\":\"num\",\"V\":\"0\",\"CF\":\"delete\"}"),
                     ikb(text="Выйти", callback_data="{\"Kb\":\"func_key\",\"V\":\"exit\",\"CF\":\"delete\"}"))

    if c_f == "mod_p" or c_f == "calc":
        _num_one_to_nine()
        m_up_num.add(ikb(text="0", callback_data="{\"Kb\":\"num\",\"V\":\"0\",\"CF\":\"" + c_f + "\"}"),
                     ikb(text="Ввод.", callback_data="{\"Kb\":\"func_key\",\"V\":\"enter\",\"CF\":\"" + c_f + "\"}"))
    return m_up_num


def m_up_l_of_t(c_f: str, lh: int):
    print(f"\tCame from {c_f} in l_of_t, markup layout")
    conn = sqlite3.connect("book_db.db", check_same_thread=False, isolation_level=None)
    c = conn.cursor()
    dat = c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    tab_nam_l = sorted(list(zip(*dat))[0])
    markup_l_of_t = InlineKeyboardMarkup()
    ikb = InlineKeyboardButton
    for i in tab_nam_l:
        markup_l_of_t.add(ikb(text=i, callback_data="{\"Kb\":\"l_o_t\",\"V\":\""+i+"\",\"CF\":\""+c_f+"\"}"))
    return markup_l_of_t


def markup_currency(c_f: str, data: dict, row_name: list):
    print(f"\tCame from {c_f} in markup_currency, markup layout")
    print(data)
    markup_cur = InlineKeyboardMarkup(row_width=5)
    ikb = InlineKeyboardButton
    # row_name = ["Валюта", "операция", "до 200", "<10.000", ">10.000"]
    # data = {row_name[0]: ["$", "$", "€", "€"],
    #         row_name[1]: ["покупка", "продажа", "покупка", "продажа"],
    #         row_name[2]: [usd_curr_buy[0], usd_curr_sell[0], eur_curr_buy[0], eur_curr_sell[0]],
    #         row_name[3]: [usd_curr_buy[1], usd_curr_sell[1], eur_curr_buy[1], eur_curr_sell[1]],
    #         row_name[4]: [usd_curr_buy[2], usd_curr_sell[2], eur_curr_buy[2], eur_curr_sell[2]]
    #         }
    for x, i in enumerate(row_name):
        markup_cur.add(ikb(text=str(i), callback_data="{\"Kb\":\"cur\",\"V\":\"v\",\"CF\":\"cur\"}"),  # 0 колонка ['Валюта','операция',  'до 200', '<10.000', '>10.000']
                       ikb(text=str(data[i][0]),  # 1 колонка ['$','покупка', '63.80', ...]
                           callback_data="{\"Kb\":\"" + 'mul$' + "\",\"V\":\"" + str(data[i][0]) + "\",\"CF\":\"cur\"}"),
                       ikb(text=str(data[i][1]),  # 2 колонка ['$','продажа', '65.30',...]
                           callback_data="{\"Kb\":\"" + 'div$' + "\",\"V\":\"" + str(data[i][1]) + "\",\"CF\":\"cur\"}"),
                       ikb(text=str(data[i][2]),  # 3 колонка ['€','покупка', '64.50', ...]
                           callback_data="{\"Kb\":\"" + 'mul€' + "\",\"V\":\"" + str(data[i][2]) + "\",\"CF\":\"cur\"}"),
                       ikb(text=str(data[i][3]),  # 4  колонка ['€','продажа', '66.00',...]
                           callback_data="{\"Kb\":\"" + 'div€' + "\",\"V\":\"" + str(data[i][3]) + "\",\"CF\":\"cur\"}"))
    markup_cur.add(ikb(text="Выйти из меню", callback_data="{\"Kb\":\"param\",\"V\":\"leave\",\"CF\":\"parameters\"}"))
    return markup_cur


def markup_ok(c_f):
    print(f"\tcame from {c_f} in markup_ok")
    global table_in_use
    m_up_ok = InlineKeyboardMarkup()
    ikb = InlineKeyboardButton
    m_up_ok.add(ikb(text="Ок.", callback_data="{\"Kb\":\"param\",\"V\":\"leave\",\"CF\":\"parameters\"}"))
    return m_up_ok


@bot.message_handler(commands=["go", "start"])
def start(message):
    print("in start function. called by command. Message id = ", message.message_id)
    global messages_dict
    global user_id
    user_id = message.from_user.id
    print(f"\tmessage text is {message.text}, came from {message.from_user.id}")
    if message.from_user.id not in messages_dict:
        messages_dict[message.from_user.id] = []
    if message.message_id not in messages_dict[message.from_user.id]:
        messages_dict[message.from_user.id].append(message.message_id)
    print("\t", messages_dict)
    global get_date
    global id_to_delete
    global page
    global total_pages
    global additional
    global qty_out
    global qty_out_text
    get_date, id_to_delete, qty_out_text = "", "", ""
    page, total_pages, additional = 0, 0, 0
    # return f"CREATE TABLE IF NOT EXISTS {_scrub(tablename)} " \
    #        f"(id INTEGER PRIMARY KEY, {columns[0]} " + (",{} " * (len(columns) - 1)).format(*map(_scrub, columns[1:])) + ")"
    conn = sqlite3.connect("book_db.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS default_empty (id INTEGER PRIMARY KEY, one_column TEXT)")
    bot.send_message(message.chat.id, "Выберите действие", reply_markup=markup_menu("start"))


@bot.message_handler(commands=["c"])
def currency(message):
    print(f"in currency function, called by command /c")
    print(f"\tmessage text is {message.text}, came from {message.from_user.id}")
    global messages_dict
    global exchange_k
    global qty_out_text
    qty_out_text = ""
    exchange_k = 0

    try:
        bot.delete_message(message.chat.id, message.message_id)
    except ApiTelegramException:
        print(f"\twas NOT able to delete message {message.chat.id}")
    else:
        try:
            messages_dict[user_id].remove(message.message_id)
        except ValueError:
            pass
        else:
            print(f"\t Message {message.message_id} from {user_id} was deleted from messages_dict")

    if message.from_user.id not in messages_dict:
        messages_dict[message.from_user.id] = []
    if message.message_id not in messages_dict[message.from_user.id]:
        messages_dict[message.from_user.id].append(message.message_id)
    print(f"\t{messages_dict}")
    print("in currency function. called by command. Message id = ", message.message_id)
    r = requests.get("https://blagodatka.ru/")
    soup = BeautifulSoup(r.content, "lxml")
    curr_buy = []
    usd_curr_buy, eur_curr_buy = [], []
    for each in soup.findAll('td', class_="money_price buy_price"):
        if "eur-usd" not in str(each):
            if "usd" in str(each):
                usd_curr_buy.append(each.text)
            if "eur" in str(each):
                eur_curr_buy.append(each.text)
        curr_buy.append(each)
    #
    curr_sell = []
    usd_curr_sell, eur_curr_sell = [], []
    for each in soup.findAll('td', class_="money_price"):
        if each not in curr_buy:
            if "eur-usd" not in str(each):
                if "usd" in str(each):
                    usd_curr_sell.append(each.text)
                if "eur" in str(each):
                    eur_curr_sell.append(each.text)
            curr_sell.append(each)
    print(f"\t usd currency sale{usd_curr_sell} ,eur currency sale{eur_curr_sell},"
          f"usd currency buy {usd_curr_buy}, eur currency buy{eur_curr_buy} ")
    row_name = ["Валюта", "операция", "до 200", "<10.000", ">10.000"]
    data = {row_name[0]: ["$", "$", "€", "€"],
            row_name[1]: ["покупка", "продажа", "покупка", "продажа"],
            row_name[2]: [usd_curr_buy[0], usd_curr_sell[0], eur_curr_buy[0], eur_curr_sell[0]],
            row_name[3]: [usd_curr_buy[1], usd_curr_sell[1], eur_curr_buy[1], eur_curr_sell[1]],
            row_name[4]: [usd_curr_buy[2], usd_curr_sell[2], eur_curr_buy[2], eur_curr_sell[2]]
            }
    # ЦБР
    c = requests.get("http://www.cbr.ru")
    cbr_soup = BeautifulSoup(c.content, "lxml")
    x = cbr_soup.find_all('div', class_="main-indicator_rate")
    usd = x[0].findAll('div', class_="col-md-2 col-xs-9 _right mono-num")
    eur = x[1].findAll('div', class_="col-md-2 col-xs-9 _right mono-num")
    usd_rate = [i.string[:7] for i in usd]
    eur_rate = [i.string[:7] for i in eur]
    print(f"\t {usd_rate[1]}, {eur_rate[1]}")
    bot.edit_message_text(f"Данные с обменного пункта Благодатка, курс по ЦБ на сегодня $={usd_rate[1]} ₽, € = {eur_rate[1]} ₽ ",
                          message.chat.id, messages_dict[bot_id][-1],
                          reply_markup=markup_currency("currency", data, row_name))


@bot.message_handler(commands=["param", "p"])
def parameters(message):
    global messages_dict
    print("in parameters function, called by command 'p' or 'param'")
    print(f"\tmessage text is {message.text}, came from {message.from_user.id}")
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except ApiTelegramException:
        print(f"\twas NOT able to delete message {message.chat.id}")
    else:
        try:
            messages_dict[user_id].remove(message.message_id)
        except (ValueError, KeyError):
            pass
        else:
            print(f"\t Message {message.message_id} from {user_id} was deleted from messages_dict")
    if message.from_user.id not in messages_dict:
        messages_dict[message.from_user.id] = []
    if message.message_id not in messages_dict[message.from_user.id]:
        messages_dict[message.from_user.id].append(message.message_id)
    print(f"\t{messages_dict}")
    try:
        bot.edit_message_text("Выберите параметр для редактирования", message.chat.id, messages_dict[bot_id][-1],
                              reply_markup=markup_param("parameters"))
    except KeyError:
        pass


@bot.message_handler(content_types=["text"])
def start_over(message, *c_f):
    print(f"Came from {c_f} to start_over, message_id = {message.message_id}")
    # print(f"\tmessage text is {message.text}")
    global messages_dict
    if message.from_user.id not in messages_dict:
        messages_dict[message.from_user.id] = []
    if message.message_id not in messages_dict[message.from_user.id]:
        messages_dict[message.from_user.id].append(message.message_id)
    print(f"\t{messages_dict}")
    global get_date
    global id_to_delete
    global page
    global total_pages
    global additional
    global qty_out
    global user_id
    global got_data
    got_data = []
    get_date, id_to_delete = "", ""
    page, total_pages, additional, exchange_k = 0, 0, 0, 0
    try:  # если не получили по разным причинам user_id (не запустили робота)
        for x, i in enumerate(messages_dict[user_id]):
            try:
                bot.delete_message(message.chat.id, i)
            except ApiTelegramException:
                print(f"\twas NOT able to delete message with parameters: {message.chat.id} , {i}")
            else:
                print(f"\t Message {message.message_id} from {user_id} was deleted from messages_dict")
    except KeyError:
        pass
    bot.edit_message_text("Выберите действие", message.chat.id,  messages_dict[bot_id][-1],
                          reply_markup=markup_menu("start_over"))


@bot.callback_query_handler(func=lambda call: str(json.loads(call.data)["CF"]) == "cur")
def calc(call):
    # "{\"Kb\":\"cur\",\"V\":\"" + str(data[i][0]) + "\",\"CF\":\"cur\"}"
    print(f"Came from markup_currency to calc function, "
          f"called by {str(json.loads(call.data)['CF'])}, "
          f"value is {str(json.loads(call.data)['V'])},",
          f"action is {str(json.loads(call.data)['Kb'])}")
    global messages_dict
    global mul_div
    global exchange_k
    exchange_k = json.loads(call.data)['V']
    mul_div = json.loads(call.data)['Kb']
    if call.message.from_user.id not in messages_dict:
        messages_dict[call.message.from_user.id] = []
    if call.message.message_id not in messages_dict[call.message.from_user.id]:
        messages_dict[call.message.from_user.id].append(call.message.message_id)
    print(f"\t{messages_dict}")
    if mul_div[:-1] == "div":
        bot.edit_message_text(f"Введите сумму для внесения в кассу (₽), которую хотите обменять на {mul_div[-1]}",
                              call.message.chat.id, messages_dict[bot_id][-1], reply_markup=markup_num("calc", "0"))
    elif mul_div[:-1] == "mul":
        bot.edit_message_text(f"Введите сумму для внесения в кассу ({mul_div[-1]}), которую хотите обменять на ₽",
                              call.message.chat.id, messages_dict[bot_id][-1], reply_markup=markup_num("calc", "0"))


@bot.callback_query_handler(func=lambda call: str(json.loads(call.data)["V"]) in ["show", "prev", "stop", "next"])
def show_db(call):
    print("in show_db function, ClBkHr, called by parameter: ", str(json.loads(call.data)["V"]))
    # print(f"\tmessage text is {call.message.text}, came from {call.message.from_user.id}")
    global messages_dict
    if call.message.from_user.id not in messages_dict:
        messages_dict[call.message.from_user.id] = []
    if call.message.message_id not in messages_dict[call.message.from_user.id]:
        messages_dict[call.message.from_user.id].append(call.message.message_id)
    print(f"\t{messages_dict}")
    global page
    global additional
    global qty_out
    global yn_id
    global table_in_use
    global active_table_columns
    conn = sqlite3.connect("book_db.db", check_same_thread=False, isolation_level=None)
    c = conn.cursor()
    try:
        c.execute(f"SELECT * FROM {table_in_use}")
    except sqlite3.OperationalError:
        print(f"\t No such table {table_in_use}")
        table_in_use = "default_empty"
        c.execute(f"SELECT * FROM {table_in_use}")
    print(f"\t {c.description}")
    active_table_columns = list(list(zip(*c.description))[0])[1:]  # не берем id
    is_date = list(
        active_table_columns[x] for x in range(len(active_table_columns)) if active_table_columns[x] in ["dd", "mm", "yyyy"])
    if is_date != []:  # если не пустой лист, созданный из названий колонок с датой
        is_date_sql = " ||'.'|| ".join(is_date) + ","
    not_date = list(
        active_table_columns[x] for x in range(len(active_table_columns)) if active_table_columns[x] not in ["dd", "mm", "yyyy", "id"])
    if yn_id == 1 and is_date != []:
        c.execute(f"SELECT id, {is_date_sql} {', '.join(x for x in not_date)} FROM {table_in_use} ORDER BY yyyy, mm, dd DESC")
    elif yn_id == 1 and is_date == []:
        c.execute(f"SELECT id, {', '.join(x for x in not_date)} FROM {table_in_use} ORDER BY id DESC")
    elif yn_id == 0 and is_date != []:
        c.execute(f"SELECT {is_date_sql} {', '.join(x for x in not_date)} FROM {table_in_use} ORDER BY yyyy, mm, dd DESC")
    elif yn_id == 0 and is_date == []:
        c.execute(f"SELECT {', '.join(x for x in not_date)} FROM {table_in_use}")
    db_data = c.fetchall()  # данные формата [(1, '21.02.1985', 'my bd', 'bd'), (2, '08.03.1959', "pap's bd", 'bd')]
    if len(db_data) < 1:
        bot.edit_message_text("Пустая база данных.",
                              call.message.chat.id, call.message.message_id, reply_markup=markup_menu("show_db"))
        start_over(call.message, "show_db")

    # странные манипуляции для перевода списка с кортежами в сплошной текст с разделителями по строчке "\n"
    new_list = []
    new_l2 = []
    for tup in db_data:
        new_list.append(list(map(str, tup)))
    for each in new_list:
        new_l2.append(" / ".join(each))
    db_data = '\n'.join(new_l2)

    additional = (1 if db_data.count("\n") % qty_out > 0 else 0)
    if str(json.loads(call.data)["V"]) != "stop":
        if str(json.loads(call.data)["V"]) == "prev":
            page -= 1
        if str(json.loads(call.data)["V"]) == "next":
            page += 1
        try:
            bot.edit_message_text("\n".join(db_data.split("\n")[page * qty_out:qty_out + page * qty_out]),
                                  call.message.chat.id, call.message.message_id,
                                  reply_markup=markup_navi(page, db_data.count("\n") // qty_out + additional - 1, "show_db"))
        except ApiTelegramException:
            bot.edit_message_text("Повторный вызов",
                                  call.message.chat.id, call.message.message_id, reply_markup=markup_menu("show_db"))
    elif str(json.loads(call.data)["V"]) == "stop":
        start_over(call.message, "show_db, stop")


@bot.callback_query_handler(func=lambda call: str(json.loads(call.data)["V"]) == "delete")
def delete_menu(call):
    print(f"in delete_menu function, ClBkHr, called by : {str(json.loads(call.data)['V'])},message_id = {call.message.message_id}")
    print(f"\tmessage text is {call.message.text}, came from {call.message.from_user.id}")
    global messages_dict
    if call.message.from_user.id not in messages_dict:
        messages_dict[call.message.from_user.id] = []
    if call.message.message_id not in messages_dict[call.message.from_user.id]:
        messages_dict[call.message.from_user.id].append(call.message.message_id)
    print(f"\t{messages_dict}")
    bot.edit_message_text("Введите id", call.message.chat.id, call.message.message_id, reply_markup=markup_num("delete", "0"))


@bot.callback_query_handler(func=lambda call: str(json.loads(call.data)["V"]) == "add")
def add_to_db(call):
    print("in add_to_db function, ClBkHr, called by parameter: ", str(json.loads(call.data)["V"]))
    print(f"\tmessage text is {call.message.text}, came from {call.message.from_user.id}")
    fill_table(call.message, 0)


@bot.callback_query_handler(func=lambda call: all(i in list(json.loads(call.data).values()) for i in ["func_key", "enter", "fill_table"]))
def came_from_number_input(call):
    print(f"in came_from_number_input function, ClBkHr, came from num_markup")
    global got_data
    got_data[-3:] = call.message.text.split(".")
    print(f"\t {got_data}")
    save_db(call.message)


def fill_table(message, col: int):
    print(f"in fill_table function, column = {col} ")
    global table_in_use
    global messages_dict
    global got_data
    global active_table_columns
    global is_date_in
    if message.from_user.id not in messages_dict:
        messages_dict[message.from_user.id] = []
    if message.message_id not in messages_dict[message.from_user.id]:
        messages_dict[message.from_user.id].append(message.message_id)
    print(f"\t{messages_dict}")

    if col == 0:  # первый проход функции, получаем все данные о структуре таблицы
        conn = sqlite3.connect("book_db.db", check_same_thread=False, isolation_level=None)
        c = conn.cursor()
        c.execute(f"SELECT * FROM  {table_in_use}")
        active_table_columns = list(list(zip(*c.description))[0])[1:]  # получаем список столбцов, не берем id
        is_date_in = (True if {"dd", "mm", "yyyy"}.issubset(active_table_columns) else False)
        got_data.extend(["" for _ in range(len(active_table_columns))])  # формирую "форму" списка для внесения в таблицу
    print(f"\t column value is {col} and length of active table named {table_in_use} is {len(active_table_columns)} ")

    if col == len(active_table_columns):  # последний столбик для заполнения
        try:
            bot.delete_message(message.chat.id, messages_dict[user_id][-1])
        except ApiTelegramException:
            pass

        if is_date_in:  # и есть данные с датой
            got_data[col-4] = message.text  # Данные, полученные за прошлый проход функции, т.е. -4, т.к -1 - за 0 проход, -3 - за дату
            print(f"\t got data values is {got_data}")
            bot.edit_message_text('дд.мм.гггг', message.chat.id,  messages_dict[bot_id][-1],
                                  reply_markup=markup_num("fill_table", ""))
        if not is_date_in:  # последний столбик для заполнения и нет данных с датой
            got_data[col-1] = message.text
            save_db(message)

    elif active_table_columns[col] not in ["dd", "mm", "yyyy"]:  # если колонка не dd, mm, yyyy
        try:
            bot.delete_message(message.chat.id, messages_dict[user_id][-1])
        except ApiTelegramException:
            pass
        msg = bot.edit_message_text(f"Введите данные в поле {active_table_columns[col]}:", message.chat.id, messages_dict[bot_id][-1])
        if col != 0:  # если первый проход - данных введенных пользователем нет
            got_data[col - 1] = message.text
        bot.register_next_step_handler(msg, fill_table, col+1)
        print(f"\t{got_data}")
    else:
        fill_table(message, col+1)  # пропускаем столбики с dd , mm, yyyy


@bot.callback_query_handler(func=lambda call: json.loads(call.data)["Kb"] == "num")
def callback_num(call):
    print(f"in callback_num function, ClBkHr, called by: {json.loads(call.data)['Kb']}, message_id={call.message.message_id}")
    print(f"\tmessage text is {call.message.text}, came from user {call.message.from_user.id}")
    global messages_dict
    if call.message.from_user.id not in messages_dict:
        messages_dict[call.message.from_user.id] = []
    if call.message.message_id not in messages_dict[call.message.from_user.id]:
        messages_dict[call.message.from_user.id].append(call.message.message_id)
    print(f"\t{messages_dict}")
    digit = json.loads(call.data)["V"]
    if json.loads(call.data)["CF"] == "delete":  # если пришли из удаления
        global id_to_delete
        if len(id_to_delete) > 0:
            if id_to_delete[0] == "_":
                id_to_delete = ""
        id_to_delete = id_to_delete + digit
        bot.edit_message_text(id_to_delete, call.message.chat.id, call.message.message_id, reply_markup=markup_num("delete", "0"))
    if json.loads(call.data)["CF"] == "fill_table":
        global get_date
        if digit.isdigit() and len(get_date) <= 10:
            if get_date[:1] == "_":
                get_date = ""
            get_date = get_date + digit
        if len(get_date) == 2 or len(get_date) == 5:
            get_date = get_date + "."
        if digit == "cls":
            get_date = "_"
        bot.edit_message_text(get_date, call.message.chat.id, call.message.message_id, reply_markup=markup_num("fill_table", get_date))
    if str(json.loads(call.data)["CF"]) == "mod_p" or str(json.loads(call.data)["CF"]) == "calc":
        global qty_out_text
        qty_out_text = qty_out_text + str(digit)
        bot.edit_message_text(qty_out_text, call.message.chat.id, call.message.message_id,
                              reply_markup=markup_num(str(json.loads(call.data)["CF"]), qty_out_text))
    # if str(json.loads(call.data)["CF"]) == "calc":


@bot.callback_query_handler(func=lambda call: all(i in list(json.loads(call.data).values()) for i in ["func_key", "enter", "calc"]))
def exchange_calc(call):
    print(f"in exchange_calc function, ClBkHr, called by {list(json.loads(call.data).values())}")
    print(f"\tmessage text is {call.message.text}, came from {call.message.from_user.id}")
    global messages_dict
    global exchange_k
    global qty_out_text
    global mul_div
    if call.message.from_user.id not in messages_dict:
        messages_dict[call.message.from_user.id] = []
    if call.message.message_id not in messages_dict[call.message.from_user.id]:
        messages_dict[call.message.from_user.id].append(call.message.message_id)
    print(f"\t{messages_dict}")
    if mul_div[:-1] == "div":
        print(f"{qty_out_text}, {exchange_k}")
        bot.edit_message_text(f"При обмене {qty_out_text} ₽ , получите {float(qty_out_text) / float(exchange_k)} {mul_div[-1]}",
                              call.message.chat.id, call.message.message_id, reply_markup=markup_ok("exchange_calc"))
    else:
        bot.edit_message_text(f"При обмене {qty_out_text} {mul_div[-1]}, получите {float(qty_out_text) * float(exchange_k)} ₽",
                              call.message.chat.id, call.message.message_id, reply_markup=markup_ok("exchange_calc"))


@bot.callback_query_handler(func=lambda call: all(i in list(json.loads(call.data).values()) for i in ["func_key", "enter", "mod_p"]))
def change_qty_out(call):
    print(f"in change_qty_out function, ClBkHr, called by {list(json.loads(call.data).values())}")
    print(f"\tmessage text is {call.message.text}, came from {call.message.from_user.id}")
    global messages_dict
    if call.message.from_user.id not in messages_dict:
        messages_dict[call.message.from_user.id] = []
    if call.message.message_id not in messages_dict[call.message.from_user.id]:
        messages_dict[call.message.from_user.id].append(call.message.message_id)
    print(f"\t{messages_dict}")
    global qty_out
    qty_out = int(qty_out_text)
    start_over(call.message, "change_qty_out")


@bot.callback_query_handler(func=lambda call: all(i in list(json.loads(call.data).values()) for i in ["func_key", "enter", "delete"]))
def del_id(call):
    print("in del_id function, ClBkHr, called by parameter: ",
          list(json.loads(call.data).values()), " . message_id = ", call.message.message_id)
    print(f"\tmessage text is {call.message.text}, came from {call.message.from_user.id}")
    global messages_dict
    if call.message.from_user.id not in messages_dict:
        messages_dict[call.message.from_user.id] = []
    if call.message.message_id not in messages_dict[call.message.from_user.id]:
        messages_dict[call.message.from_user.id].append(call.message.message_id)
    print("\t", messages_dict)
    id_to_del = int(call.message.text)
    global table_in_use
    conn = sqlite3.connect("book_db.db", check_same_thread=False, isolation_level=None)
    c = conn.cursor()
    c.execute(f"SELECT id FROM {table_in_use} WHERE id={id_to_del}")
    if c.fetchone() is None:
        global id_to_delete
        id_to_delete = "_"
        bot.edit_message_text("Нет такой записи в БД", call.message.chat.id, call.message.message_id,
                              reply_markup=markup_menu("del_id"))
    else:
        c.execute(f"DELETE FROM {table_in_use} WHERE id={id_to_del}")
        conn.commit()
        bot.edit_message_text("Удалено", call.message.chat.id, call.message.message_id, reply_markup=markup_num("delete", "0"))
    bot.register_next_step_handler_by_chat_id(call.message.chat.id, start_over(call.message, "del_id"))


@bot.callback_query_handler(func=lambda call: str(json.loads(call.data)["Kb"]) == "param")
def mod_p(call):
    print(f"in mod_p function, ClBkHr, called by \"{json.loads(call.data)['Kb']}\"")
    print(f"\tmessage text is {call.message.text}, came from {call.message.from_user.id}")
    global messages_dict
    if call.message.from_user.id not in messages_dict:
        messages_dict[call.message.from_user.id] = []
    if call.message.message_id not in messages_dict[call.message.from_user.id]:
        messages_dict[call.message.from_user.id].append(call.message.message_id)
    print(f"\t{messages_dict}")
    if str(json.loads(call.data)["V"]) == "qty_out":
        bot.edit_message_text("Введите число",
                              call.message.chat.id, call.message.message_id, reply_markup=markup_num("mod_p", "0"))
    if str(json.loads(call.data)["V"]) == "yn_id":
        global yn_id
        yn_id = (1 if yn_id == 0 else 0)
        start_over(call.message, "mod_p")
    if str(json.loads(call.data)["V"]) == "leave":
        start_over(call.message, "mod_p")
    if str(json.loads(call.data)["V"]) == "cr_t":
        msg = bot.edit_message_text("Название таблицы", call.message.chat.id, call.message.message_id)
        bot.register_next_step_handler(msg, columns_name)
    if str(json.loads(call.data)["V"]) == "ch_t":
        bot.edit_message_text("Выберите таблицу", call.message.chat.id, call.message.message_id, reply_markup=m_up_l_of_t("mod_p", 0))


@bot.callback_query_handler(func=lambda call: str(json.loads(call.data)["Kb"]) == "l_o_t")
def table_select(call):
    print(f"in table_select, ClBkHr, called by \"{json.loads(call.data)['Kb']}\"")
    print(f"\tmessage text is {call.message.text}, came from {call.message.from_user.id}")
    global messages_dict
    if call.message.from_user.id not in messages_dict:
        messages_dict[call.message.from_user.id] = []
    if call.message.message_id not in messages_dict[call.message.from_user.id]:
        messages_dict[call.message.from_user.id].append(call.message.message_id)
    print(f"\t{messages_dict}")
    global table_in_use
    table_in_use = str(json.loads(call.data)["V"])
    start_over(call.message, "table_select")


def columns_name(message):
    print(f"in columns_name function")
    print(f"\tmessage text is {message.text}, came from {message.from_user.id}")
    global messages_dict
    if message.from_user.id not in messages_dict:
        messages_dict[message.from_user.id] = []
    if message.message_id not in messages_dict[message.from_user.id]:
        messages_dict[message.from_user.id].append(message.message_id)

    try:
        bot.delete_message(message.chat.id, message.message_id)
    except ApiTelegramException:
        print(f"\twas NOT able to delete message {message.chat.id}")
    else:
        try:
            messages_dict[user_id].remove(message.message_id)
        except ValueError:
            pass
        else:
            print(f"\t Message {message.message_id} from {user_id} was deleted from messages_dict")

    msg = bot.edit_message_text("Название столбцов", user_id, messages_dict[bot_id][-1])
    bot.register_next_step_handler(msg, create_new_table, message.text)


def create_new_table(message, table_name):
    def _scrub(t_name):
        return ''.join(sym for sym in t_name if sym.isalnum())

    def _create_query(tablename, columns):
        return f"CREATE TABLE IF NOT EXISTS {_scrub(tablename)} " \
               f"(id INTEGER PRIMARY KEY, {columns[0]} " + (",{} " * (len(columns) - 1)).format(*map(_scrub, columns[1:])) + ")"

    print(f"in create_new_table function, new table name is {table_name}")
    print(f"\tmessage text is {message.text}, came from {message.from_user.id}")
    global messages_dict
    global table_in_use
    if message.from_user.id not in messages_dict:
        messages_dict[message.from_user.id] = []
    if message.message_id not in messages_dict[message.from_user.id]:
        messages_dict[message.from_user.id].append(message.message_id)
    col_list = []
    [col_list.append(x) for x in message.text.split(",") if x not in col_list]
    print(f"\t {col_list}")
    for i in col_list:
        if "date" in i:
            col_list.extend(["dd", "mm", "yyyy"])
            col_list.remove(i)
        if i == "":
            col_list.remove(i)
    print(f"\t{_create_query(table_name, col_list)}")
    conn = sqlite3.connect("book_db.db", check_same_thread=False, isolation_level=None)
    c = conn.cursor()
    c.execute(_create_query(table_name, col_list))
    conn.commit()
    table_in_use = table_name
    start_over(message, "create_new_table")


def save_db(message):
    print("in save_db function, message_id = ", message.message_id)
    print(f"\tmessage text is {message.text}, came from {message.from_user.id}")
    global messages_dict
    global bot_id
    global user_id
    global got_data
    global active_table_columns
    if message.from_user.id not in messages_dict:
        messages_dict[message.from_user.id] = []
    if message.message_id not in messages_dict[message.from_user.id]:
        messages_dict[message.from_user.id].append(message.message_id)
    print(f"\t{messages_dict}")
    global table_in_use
    conn = sqlite3.connect("book_db.db", check_same_thread=False, isolation_level=None)
    c = conn.cursor()
    c.execute(f"SELECT * FROM  {table_in_use}")
    active_table_columns = list(list(zip(*c.description))[0])[1:]  # не берем id
    # print(f"\t{got_data}")
    # print(f"\t{active_table_columns}")
    print(f'INSERT INTO {table_in_use} ({", ".join(str(x) for x in active_table_columns)}) VALUES {*got_data,}')
    c.execute(f'INSERT INTO {table_in_use} ({", ".join(str(x) for x in active_table_columns)}) VALUES {*got_data,}')
    conn.commit()
    start_over(message, "save_db")


while True:
    try:
        bot.polling(none_stop=True)
    except Exception as _ex:
        print(_ex)
        sleep(15)
