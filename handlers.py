# handlers.py
from aiogram import Router, F
from aiogram.types import (
    Message, ReplyKeyboardMarkup, KeyboardButton,
    ReplyKeyboardRemove
)
from aiogram.fsm.context import FSMContext
from aiogram import Bot
import os
from texts_uz import TEXTS
from states import CandidateForm

router = Router()

# 🔹 Utility: ID generator
def get_next_candidate_id():
    counter_file = "candidate_counter.txt"
    if not os.path.exists(counter_file):
        with open(counter_file, "w") as f:
            f.write("0")
    with open(counter_file, "r+") as f:
        last_id = int(f.read().strip())
        new_id = last_id + 1
        f.seek(0)
        f.write(str(new_id))
        f.truncate()
    return f"C-{new_id:03d}"


# 🔹 Create main menu keyboard
def main_menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=TEXTS["start_button"])],
            [
                KeyboardButton(text=TEXTS["restart_button"]),
                KeyboardButton(text=TEXTS["stop_button"])
            ]
        ],
        resize_keyboard=True
    )


# 🔹 Start command
@router.message(F.text == "/start")
async def cmd_start(message: Message):
    await message.answer(TEXTS["welcome"], reply_markup=main_menu_keyboard())


# 🔹 Step 1: Full Name
@router.message(F.text == TEXTS["start_button"])
async def ask_full_name(message: Message, state: FSMContext):
    await message.answer(TEXTS["enter_full_name"], reply_markup=ReplyKeyboardRemove())
    await state.set_state(CandidateForm.full_name)


@router.message(CandidateForm.full_name)
async def get_full_name(message: Message, state: FSMContext):
    candidate_id = get_next_candidate_id()
    await state.update_data(full_name=message.text, candidate_id=candidate_id)
    await message.answer(TEXTS["enter_birth_date"])
    await state.set_state(CandidateForm.birth_date)


# 🔹 Step 2: Birth Date
@router.message(CandidateForm.birth_date)
async def get_birth_date(message: Message, state: FSMContext):
    await state.update_data(birth_date=message.text)
    await message.answer(TEXTS["enter_address"])
    await state.set_state(CandidateForm.address)


# 🔹 Step 3: Address
@router.message(CandidateForm.address)
async def get_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=TEXTS["option_1"])],
            [KeyboardButton(text=TEXTS["option_2"])],
            [KeyboardButton(text=TEXTS["option_3"])]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await message.answer(TEXTS["choose_job_type"], reply_markup=keyboard)
    await state.set_state(CandidateForm.job_type)


# 🔹 Step 4: Job Type
@router.message(CandidateForm.job_type)
async def get_job_type(message: Message, state: FSMContext):
    await state.update_data(job_type=message.text)
    await message.answer(TEXTS["extra_skills"], reply_markup=ReplyKeyboardRemove())
    await state.set_state(CandidateForm.extra_skills)


# 🔹 Step 5: Extra Skills
@router.message(CandidateForm.extra_skills)
async def get_extra_skills(message: Message, state: FSMContext):
    await state.update_data(extra_skills=message.text)
    await message.answer(TEXTS["last_workplace"])
    await state.set_state(CandidateForm.last_workplace)


# 🔹 Step 6: Last Workplace (Voice Only)
@router.message(CandidateForm.last_workplace)
async def get_last_workplace(message: Message, state: FSMContext):
    if not message.voice:
        await message.answer("❗ Iltimos, ushbu savolga faqat ovozli xabar yuboring.")
        return

    await state.update_data(
        last_workplace_voice_id=message.voice.file_id,
        last_workplace_text="🎤 Ovozli xabar qabul qilindi"
    )

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=TEXTS["share_contact_button"], request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer(TEXTS["ask_phone"], reply_markup=keyboard)
    await state.set_state(CandidateForm.phone_number)


# 🔹 Step 7: Phone Number
@router.message(CandidateForm.phone_number)
async def get_phone_number(message: Message, state: FSMContext):
    phone_number = (
        message.contact.phone_number if message.contact else message.text
    )
    await state.update_data(phone_number=phone_number)
    username = message.from_user.username or "N/A"
    await state.update_data(username=username)

    data = await state.get_data()
    summary = (
        f"{TEXTS['summary_title']}\n\n"
        f"🆔 ID: *{data['candidate_id']}*\n"
        f"👤 Ism: {data['full_name']}\n"
        f"📅 Tug'ilgan sana: {data['birth_date']}\n"
        f"🏠 Manzil: {data['address']}\n"
        f"💼 Ish turi: {data['job_type']}\n"
        f"🧩 Qo'shimcha Qobilyatlar: {data['extra_skills']}\n"
        f"📞 Telefon: {data['phone_number']}\n"
        f"🔗 Telegram: @{data['username']}\n\n"
        f"{TEXTS['confirm_question']}"
    )

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=TEXTS["yes_submit"]), KeyboardButton(text=TEXTS["no_edit"])]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer(summary, parse_mode="Markdown", reply_markup=keyboard)
    await state.set_state(CandidateForm.confirmation)


# 🔹 Step 8: Confirmation (Yes)
@router.message(CandidateForm.confirmation, F.text == TEXTS["yes_submit"])
async def confirm_submission(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    backlog_chat_id = os.getenv("BACKLOG_CHAT_ID")

    backlog_message = (
        f"📥 *Yangi nomzod arizasi*\n\n"
        f"🆔 *ID:* {data['candidate_id']}\n"
        f"👤 *Ism:* {data['full_name']}\n"
        f"📅 *Tug‘ilgan sana:* {data['birth_date']}\n"
        f"🏠 *Manzil:* {data['address']}\n"
        f"💼 *Ish turi:* {data['job_type']}\n"
        f"🧩 *Qo'shimcha Qobilyatlar:* {data['extra_skills']}\n"
        f"📞 *Telefon:* {data['phone_number']}\n"
        f"🔗 *Telegram:* @{data['username']}\n"
    )

    await bot.send_message(backlog_chat_id, backlog_message, parse_mode="Markdown")

    if "last_workplace_voice_id" in data:
        await bot.send_voice(backlog_chat_id, voice=data["last_workplace_voice_id"])

    await message.answer(
        f"✅ Rahmat! Sizning arizangiz (ID: *{data['candidate_id']}*) yuborildi.",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )
    await state.clear()


# 🔹 Step 9: Restart form (No)
@router.message(CandidateForm.confirmation, F.text == TEXTS["no_edit"])
async def restart_form(message: Message, state: FSMContext):
    await message.answer(TEXTS["restart_fullname"], reply_markup=ReplyKeyboardRemove())
    await state.clear()
    await state.set_state(CandidateForm.full_name)


# 🔹 Restart button action
@router.message(F.text == TEXTS["restart_button"])
async def handle_restart(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("♻️ Bot qayta ishga tushirildi.", reply_markup=main_menu_keyboard())


# Keep track of stopped users in memory
stopped_users = set()


# 🔹 Stop button action (fixed)
@router.message(F.text == TEXTS["stop_button"])
async def handle_stop(message: Message, state: FSMContext):
    await state.clear()
    stopped_users.add(message.from_user.id)
    await message.answer("🛑 Bot to'xtatildi. Rahmat!", reply_markup=ReplyKeyboardRemove())


# 🔹 Prevent stopped users from interacting
@router.message()
async def block_stopped_users(message: Message):
    if message.from_user.id in stopped_users:
        # Ignore all messages silently
        return

