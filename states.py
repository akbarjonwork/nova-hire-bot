# states.py
from aiogram.fsm.state import State, StatesGroup

class CandidateForm(StatesGroup):
    full_name = State()          # Step 1
    birth_date = State()         # Step 2
    address = State()            # Step 3
    job_type = State()           # Step 4
    extra_skills = State()       # Step 5
    last_workplace = State()     # Step 6
    phone_number = State()       # Step 7
    confirmation = State()       # Final confirmation
