# handlers.py
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from states import CandidateForm
from aiogram import Bot
import os
from texts_uz import TEXTS  # ✅ imported Uzbek text file

router = Router()


# Utility: Get next incremental candidate ID
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


# /start handler
@router.message(F.text == "/start")
async def cmd_start(message: Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=TEXTS["start_button"])]],
        resize_keyboard=True
    )
    await message.answer(TEXTS["welcome"], reply_markup=keyboard)


# Step 1
@router.message(F.text == TEXTS["start_button"])
async def start_application(message: Message, state: FSMContext):
    await message.answer(TEXTS["enter_full_name"], reply_markup=ReplyKeyboardRemove())
    await state.set_state(CandidateForm.full_name)


# Step 2
@router.message(CandidateForm.full_name)
async def get_full_name(message: Message, state: FSMContext):
    candidate_id = get_next_candidate_id()
    await state.update_data(full_name=message.text, candidate_id=candidate_id)
    await message.answer(TEXTS["ask_occupation"])
    await state.set_state(CandidateForm.occupation)


# Step 3
@router.message(CandidateForm.occupation)
async def get_occupation(message: Message, state: FSMContext):
    await state.update_data(occupation=message.text)

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=TEXTS["share_contact_button"], request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await message.answer(TEXTS["ask_phone"], reply_markup=keyboard)
    await state.set_state(CandidateForm.phone_number)


# Step 4
@router.message(CandidateForm.phone_number)
async def get_phone(message: Message, state: FSMContext):
    phone_number = message.contact.phone_number if message.contact else message.text
    await state.update_data(phone_number=phone_number)

    username = message.from_user.username or "N/A"
    await state.update_data(username=username)

    await message.answer(TEXTS["ask_reason_apply"], reply_markup=ReplyKeyboardRemove())
    await state.set_state(CandidateForm.reason_apply)


# Step 5
@router.message(CandidateForm.reason_apply)
async def get_reason_apply(message: Message, state: FSMContext):
    await state.update_data(reason_apply=message.text)
    await message.answer(TEXTS["ask_reason_leave"])
    await state.set_state(CandidateForm.reason_leave)


# Step 6
@router.message(CandidateForm.reason_leave)
async def get_reason_leave(message: Message, state: FSMContext):
    await state.update_data(reason_leave=message.text)
    await message.answer(TEXTS["ask_intro"])
    await state.set_state(CandidateForm.self_intro)


# Step 7
@router.message(CandidateForm.self_intro)
async def get_intro(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()

    if message.voice:
        data["self_intro"] = "🎤 Ovozli xabar qabul qilindi"
        data["voice_file_id"] = message.voice.file_id
    else:
        data["self_intro"] = message.text or "N/A"

    summary = (
        f"{TEXTS['summary_title']}\n\n"
        f"🆔 ID: *{data['candidate_id']}*\n"
        f"👤 Ism: {data['full_name']}\n"
        f"💼 Kasb: {data['occupation']}\n"
        f"📞 Telefon: {data['phone_number']}\n"
        f"🔗 Telegram: @{data['username']}\n"
        f"📝 Ariza sababi: {data['reason_apply']}\n"
        f"🚪 Tark etish sababi: {data['reason_leave']}\n"
        f"💬 Tanishtirish: {data['self_intro']}\n\n"
        f"{TEXTS['confirm_question']}"
    )

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=TEXTS["yes_submit"]), KeyboardButton(text=TEXTS["no_edit"])]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await message.answer(summary, reply_markup=keyboard, parse_mode="Markdown")
    await state.update_data(**data)
    await state.set_state(CandidateForm.confirmation)


# Step 8
@router.message(CandidateForm.confirmation, F.text == TEXTS["yes_submit"])
async def confirm_submission(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    backlog_chat_id = os.getenv("BACKLOG_CHAT_ID")

    backlog_message = (
        f"📥 *Yangi nomzod arizasi*\n\n"
        f"🆔 *ID:* {data['candidate_id']}\n"
        f"👤 *Ism:* {data['full_name']}\n"
        f"💼 *Kasb:* {data['occupation']}\n"
        f"📞 *Telefon:* {data['phone_number']}\n"
        f"🔗 *Telegram:* @{data['username']}\n"
        f"📝 *Ariza sababi:* {data['reason_apply']}\n"
        f"🚪 *Tark etish sababi:* {data['reason_leave']}\n"
    )

    await bot.send_message(chat_id=backlog_chat_id, text=backlog_message, parse_mode="Markdown")

    if "voice_file_id" in data:
        await bot.send_voice(chat_id=backlog_chat_id, voice=data["voice_file_id"])

    await message.answer(
        f"✅ Rahmat! Sizning arizangiz (ID: *{data['candidate_id']}*) muvaffaqiyatli yuborildi.",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=TEXTS["start_button"])]],
        resize_keyboard=True
    )
    await message.answer(TEXTS["restart_prompt"], reply_markup=keyboard)
    await state.clear()


@router.message(CandidateForm.confirmation, F.text == TEXTS["no_edit"])
async def restart_form(message: Message, state: FSMContext):
    await message.answer(TEXTS["restart_fullname"], reply_markup=ReplyKeyboardRemove())
    await state.clear()
    await state.set_state(CandidateForm.full_name)
