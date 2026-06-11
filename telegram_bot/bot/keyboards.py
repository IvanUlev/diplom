from aiogram.types import InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_custom_callback_btns(
    *,
    btns: dict[str, str],
    layout: list[int]
):
    keyboard = InlineKeyboardBuilder()

    button_queue = []

    for text, data in btns.items():

        if isinstance(data, tuple):

            if data[0] == 'webapp':
                button_queue.append(
                    InlineKeyboardButton(
                        text=text,
                        web_app=WebAppInfo(url=data[1])
                    )
                )

            elif data[0] == 'url':
                button_queue.append(
                    InlineKeyboardButton(
                        text=text,
                        url=data[1]
                    )
                )

        else:
            button_queue.append(
                InlineKeyboardButton(
                    text=text,
                    callback_data=str(data)
                )
            )

    index = 0

    for row_size in layout:
        if index >= len(button_queue):
            break

        row_buttons = button_queue[index:index + row_size]
        keyboard.row(*row_buttons)

        index += row_size

    return keyboard.as_markup()