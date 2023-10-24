from aiogram import F, Router, types, flags
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, FSInputFile, BufferedInputFile, CallbackQuery
from aiogram.fsm.context import FSMContext

import datetime
import utils, kb, text, charts, db_runner, db
from states import Gen

router = Router()
jettons_limit = {} # TODO thread safe

@router.message(Command("start"))
async def start_handler(msg: Message, state: FSMContext):
    await state.set_state(Gen.initial)
    await msg.answer(text.greet.format(name=msg.from_user.full_name), reply_markup=kb.menu)

@router.message(F.text == "Меню")
@router.message(F.text == "Выйти в меню")
@router.message(F.text == "◀️ Выйти в меню")
async def menu(msg: Message, state: FSMContext):
    await state.set_state(Gen.initial)
    await msg.answer(text.menu, reply_markup=kb.menu)

@router.callback_query(F.data == "jetons_list")
async def input_jetons_list(clbck: CallbackQuery, state: FSMContext):
    await state.set_state(Gen.jettons_list)
    if clbck.from_user.id not in jettons_limit:
        jettons_limit[clbck.from_user.id] = 100
    pages_count = utils.calc_pages_count(jettons_limit[clbck.from_user.id], utils.jettons_count)
    pages = kb.pages_builder(1, pages_count)
    await clbck.message.edit_text(text.jetons_list_text, reply_markup=pages.as_markup())
    await clbck.message.answer(text.qwe_exit, reply_markup=kb.exit_kb)

@router.callback_query(F.data == "projects_list")
async def input_project_list(clbck: CallbackQuery, state: FSMContext):
    await state.set_state(Gen.projects_list)
    builder = kb.project_menu_builder()
    await clbck.message.edit_text("Проекты", reply_markup=builder.as_markup())
    await clbck.message.answer(text.qwe_exit, reply_markup=kb.exit_kb)

@router.callback_query(F.data == "add_tokens")
async def input_add_tokens(clbck: CallbackQuery, state: FSMContext):
    await state.set_state(Gen.add_jetons)
    await clbck.message.edit_text(text.add_jetons_text)
    await clbck.message.answer(text.qwe_exit, reply_markup=kb.exit_kb)

@router.callback_query(F.data == "charts_prices")
async def chart_menu(clbck: CallbackQuery, state: FSMContext):
    await state.set_state(Gen.choose_markets)
    await clbck.message.answer(text.choose_market_text, reply_markup=kb.markets)

@router.callback_query(F.data == "DeDust_chart")
async def dedust_prices(clbck: CallbackQuery, state: FSMContext):
    await state.set_state(Gen.dedust_chart)
    infos = await db_runner.get_dedust_info()
    dedust_text = ''
    for info in infos:
        dedust_text += "{}\n{}\n\n".format(info['name'], info['address'])
    await clbck.message.edit_text(dedust_text)
    await clbck.message.answer(text.chart_help)
    await clbck.message.answer(text.qwe_exit, reply_markup=kb.exit_kb)

@router.callback_query(F.data == "Ston_chart")
async def ston_prices(clbck: CallbackQuery, state: FSMContext):
    await state.set_state(Gen.ston_chart)
    infos = await db_runner.get_ston_info()
    ston_text = ''
    for info in infos:
        ston_text += "{}\n{}\n\n".format(info['name'], info['address'])
    await clbck.message.edit_text(ston_text)
    await clbck.message.answer(text.chart_help)
    await clbck.message.answer(text.qwe_exit, reply_markup=kb.exit_kb)

@router.callback_query(F.data == "help")
async def input_help(clbck: CallbackQuery, state: FSMContext):
    await state.set_state(Gen.help)
    await clbck.message.edit_text(text.help_text)
    await clbck.message.answer(text.qwe_exit, reply_markup=kb.exit_kb)

@router.callback_query(F.data.startswith("projbutton_"))
@flags.chat_action("upload_photo")
async def projbutton_pressed(clbck: types.CallbackQuery):
    number = int(clbck.data.split("_")[1])
    proj_data = utils.project_data[number]
    projtext = ""
    for i in (0,1,2,3):
        if proj_data[i]:
            projtext = projtext + proj_data[i] + '\n'
    photo = FSInputFile(proj_data[4])
    await clbck.message.answer_photo(photo, caption=projtext)
    await clbck.message.answer(text.qwe_exit, reply_markup=kb.exit_kb)

@router.message(Command("chart"))
async def cmd_limit(msg: Message, command: CommandObject, state: FSMContext):
    if command.args:
        if ((await state.get_state()) == Gen.ston_chart):
            address = command.args
            dt = datetime.datetime.now() - datetime.timedelta(days=1)
            data = await db_runner.get_ston_prices_by_address(dt, address)
            Y = data['price']
            X = data['time']
            info = {"title": data['name']}
            img = charts.chart_buffer(X, Y, info)
            photo = BufferedInputFile(img.getvalue(), filename="chart.png")
            result = await msg.answer_photo(
                photo=photo,
                caption=text.img_info
            )
            await msg.answer(text.qwe_exit, reply_markup=kb.exit_kb)
        elif ((await state.get_state()) == Gen.dedust_chart):
            address = command.args
            dt = datetime.datetime.now() - datetime.timedelta(days=1)
            data = await db_runner.get_dedust_prices_by_address(dt, address)
            Y = data['price']
            X = data['time']
            info = {"title": data['name']}
            img = charts.chart_buffer(X, Y, info)
            photo = BufferedInputFile(img.getvalue(), filename="chart.png")
            result = await msg.answer_photo(
                photo=photo,
                caption=text.img_info
            )
            await msg.answer(text.qwe_exit, reply_markup=kb.exit_kb)

@router.callback_query(F.data.startswith("page_"))
async def pagebutton_pressed(clbck: types.CallbackQuery):
    number = int(clbck.data.split("_")[1])
    if clbck.from_user.id not in jettons_limit:
        jettons_limit[clbck.from_user.id] = 100
    cur_jetton_limit = jettons_limit[clbck.from_user.id]
    offset = utils.calc_offset(cur_jetton_limit, number)
    msg_text = utils.get_jettons(cur_jetton_limit, offset)
    await clbck.message.edit_text(msg_text)

    pages_count = utils.calc_pages_count(cur_jetton_limit, utils.jettons_count)
    pages = kb.pages_builder(number, pages_count)
    await clbck.message.answer(text.jetons_list_text, reply_markup=pages.as_markup())
    await clbck.message.answer(text.qwe_exit, reply_markup=kb.exit_kb)

@router.message(Command("limit"))
async def cmd_limit(msg: Message, command: CommandObject, state: FSMContext):
    if command.args and command.args.isdigit():
        cur_jettons_limit = int(command.args)
        jettons_limit[msg.from_user.id] = cur_jettons_limit
        if (await state.get_state() == Gen.jettons_list):
            pages_count = utils.calc_pages_count(cur_jettons_limit, utils.jettons_count)
            pages = kb.pages_builder(1, pages_count)
            await msg.answer(text.jetons_list_text, reply_markup=pages.as_markup())
            await msg.answer(text.qwe_exit, reply_markup=kb.exit_kb)

@router.message(Command("page"))
async def cmd_limit(msg: Message, command: CommandObject, state: FSMContext):
    if command.args and command.args.isdigit():
        offset = int(command.args)
        if msg.from_user.id not in jettons_limit:
            jettons_limit[msg.from_user.id] = 100
        cur_jettons_limit = jettons_limit[msg.from_user.id]
        if (await state.get_state() == Gen.jettons_list):
            pages_count = utils.calc_pages_count(cur_jettons_limit, utils.jettons_count)
            pages = kb.pages_builder(offset, pages_count)
            await msg.answer(text.jetons_list_text, reply_markup=pages.as_markup())
            await msg.answer(text.qwe_exit, reply_markup=kb.exit_kb)
