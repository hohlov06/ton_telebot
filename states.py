from aiogram.fsm.state import StatesGroup, State

class Gen(StatesGroup):
    add_jetons = State()
    choose_markets = State()
    jettons_list = State()
    help = State()
    projects_list = State()
    initial = State()
