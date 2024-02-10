from aiogram import types, F, Router
from db import connect_to_db, close_db
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton


router = Router()


@router.message(F.text.lower() == "faq")
async def faq(message: types.Message):
    cursor, conn = await connect_to_db()
    cursor.execute(f"SELECT id, question, answer FROM public.faq_faq")
    records = cursor.fetchall()
    await close_db(cursor, conn)

    if len(records) == 0:
        await message.answer(text="Раздела FAQ пока не существует :(")
    else:
        buttons_list = []

        for item in records:
            question = item[1]
            answer_id = item[0]

            question_button = [types.InlineKeyboardButton(
                text=question,
                callback_data=f"Ответ {str(answer_id)}"
            )]
            buttons_list.append(question_button)
        kb = types.InlineKeyboardMarkup(inline_keyboard=buttons_list)
        await message.answer(text='Вот список частозадаваемых вопросов:', reply_markup=kb)


@router.callback_query(F.data.startswith("Ответ"))
async def get_faq_answer(callback: types.CallbackQuery):
    answer_id = callback.data.split()[1]
    cursor, conn = await connect_to_db()
    cursor.execute(f"SELECT question, answer FROM public.faq_faq WHERE id = {answer_id}")
    record = cursor.fetchall()
    await close_db(cursor, conn)
    question = record[0][0]
    answer = record[0][1]
    reply_message = f'Вот ответ на вопрос {question}: {answer}'
    await callback.message.answer(text=reply_message)
