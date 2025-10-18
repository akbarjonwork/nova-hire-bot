# states.py
from aiogram.fsm.state import State, StatesGroup

class CandidateForm(StatesGroup):
    full_name = State()
    occupation = State()
    phone_number = State()
    reason_apply = State()
    reason_leave = State()
    self_intro = State()
    confirmation = State()
