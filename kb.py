from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder
import utils

menu = [
    [InlineKeyboardButton(text="📝 Список жетонов", callback_data="jetons_list"),
    InlineKeyboardButton(text="📜 Список проектов", callback_data="projects_list")],
    [InlineKeyboardButton(text="💳 Добавление жетонов", callback_data="add_tokens"),
    InlineKeyboardButton(text="📊 Графики цен", callback_data="charts_prices")],
    [InlineKeyboardButton(text="🔎 Помощь", callback_data="help")]
]
menu = InlineKeyboardMarkup(inline_keyboard=menu)
exit_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="◀️ Выйти в меню")]], resize_keyboard=True)
iexit_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Выйти в меню", callback_data="menu")]])

markets = [
    [InlineKeyboardButton(text="LAVE", callback_data="LAVE_chart")],
    [InlineKeyboardButton(text="FNZ", callback_data="FNZ_chart")],
    [InlineKeyboardButton(text="stTON", callback_data="stTON_chart")]
]
markets = InlineKeyboardMarkup(inline_keyboard=markets)

def pages_builder(page, pages_count):
    prev_page = str(page - 1)
    cur_page = str(page)
    next_page = str(page+1)
    if page <= 3:
        prev_page = "2"
        cur_page = "3"
        next_page = "4"
    elif page >= (pages_count - 2):
        prev_page = str(pages_count-3)
        cur_page = str(pages_count-2)
        next_page = str(pages_count-1)
    builder = InlineKeyboardBuilder()
    builder.button(text="<< 1", callback_data="page_1")
    builder.button(text="<" + prev_page, callback_data="page_{}".format(prev_page))
    builder.button(text=cur_page, callback_data="page_{}".format(cur_page))
    builder.button(text=next_page + ">", callback_data="page_{}".format(next_page))
    builder.button(text=str(pages_count) + ">>", callback_data="page_{}".format(str(pages_count)))
    builder.adjust(5)
    return builder

def project_menu_builder():
    menu_builder = InlineKeyboardBuilder()
    for i in range(len(utils.project_data)):
        menu_builder.button(text=utils.project_data[i][0], callback_data=f"projbutton_{i}")
    menu_builder.adjust(3)
    return menu_builder
