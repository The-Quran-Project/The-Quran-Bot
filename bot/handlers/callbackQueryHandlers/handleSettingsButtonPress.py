from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup

from ..database import db


ayahModes = {
    "1": "Arabic + English",
    "2": "Arabic Only",
    "3": "English Only",
}

arabicStyles = {
    "1": "Uthmani",
    "2": "Simple",
}

reciterNames = {"1": "Mishary Rashid Al-Afasy", "2": "Abu Bakr Al-Shatri"}


settingsStateText = """
<u><b>Settings</b></u>

<b>Ayah Mode</b>: {ayahMode}
<b>Arabic Style</b>: {arabicStyle}
<b>Show Tafsir</b>: {showTafsir}
<b>Reciter</b>: {reciter}
"""


settingsStateButtons = [
    [
        InlineKeyboardButton("Ayah Mode", callback_data="settings ayahMode"),
        InlineKeyboardButton("Arabic Style", callback_data="settings arabicStyle"),
    ],
    [
        InlineKeyboardButton("Show Tafsir", callback_data="settings showTafsir"),
        InlineKeyboardButton("Reciter", callback_data="settings reciter"),
    ],
]


async def handleSettingsButtonPress(u: Update, c):
    """Handles the settings button press"""
    message = u.effective_message
    userID = u.effective_user.id
    chatID = u.effective_chat.id
    isGroup = chatID != userID

    user = db.getUser(userID)

    query = u.callback_query
    query_data = query.data

    query_data = query_data.split()[1:]

    if query_data[0] == "home":
        reply = settingsStateText.format(
            ayahMode=ayahModes[str(user["settings"]["ayahMode"])],
            arabicStyle=arabicStyles[str(user["settings"]["arabicStyle"])],
            showTafsir=["No", "Yes"][user["settings"]["showTafsir"]],
            reciter=reciterNames[str(user["settings"]["reciter"])],
        )
        await message.edit_text(
            reply, reply_markup=InlineKeyboardMarkup(settingsStateButtons)
        )

    elif query_data[0] == "set":
        option, value = query_data[1:]
        newSettings = user["settings"]

        if option == "ayahMode":
            newSettings["ayahMode"] = int(value)
        elif option == "arabicStyle":
            newSettings["arabicStyle"] = int(value)
        elif option == "showTafsir":
            newSettings["showTafsir"] = bool(int(value))
        elif option == "reciter":
            newSettings["reciter"] = int(value)

        reply = settingsStateText.format(
            ayahMode=ayahModes[str(user["settings"]["ayahMode"])],
            arabicStyle=arabicStyles[str(user["settings"]["arabicStyle"])],
            showTafsir=["No", "Yes"][user["settings"]["showTafsir"]],
            reciter=reciterNames[str(user["settings"]["reciter"])],
        )
        await message.edit_text(
            reply, reply_markup=InlineKeyboardMarkup(settingsStateButtons)
        )

        await query.answer("Settings Updated")
        db.updateUser(userID, newSettings)

    elif query_data[0] == "ayahMode":
        ayahMode = user["settings"]["ayahMode"]
        reply = f"""
<u><b>Change Ayah Mode</b></u>

<b>Ayah Mode</b>: {ayahModes[str(ayahMode)]}

<b>-------------------------</b>

<b>Arabic + English</b>: Show Arabic and English Ayah
<b>Arabic Only</b>: Show only Arabic Ayah
<b>English Only</b>: Show only English Ayah
"""
        buttons = [
            [
                InlineKeyboardButton(
                    "Arabic + English", callback_data="settings set ayahMode 1"
                ),
                InlineKeyboardButton(
                    "Arabic Only", callback_data="settings set ayahMode 2"
                ),
            ],
            [
                InlineKeyboardButton(
                    "English Only", callback_data="settings set ayahMode 3"
                ),
            ],
            [
                InlineKeyboardButton("Go Back", callback_data="settings home"),
            ],
        ]
        await message.edit_text(reply, reply_markup=InlineKeyboardMarkup(buttons))

    elif query_data[0] == "arabicStyle":
        arabicStyle = user["settings"]["arabicStyle"]
        reply = f"""
<u><b>Change Arabic Style</b></u>

<b>Arabic Style</b>: {arabicStyles[str(arabicStyle)]}

<b>-------------------------</b>

<b>Uthmani</b>: With Harakat
<b>Simple</b>: Without Harakat
"""
        buttons = [
            [
                InlineKeyboardButton(
                    "Uthmani", callback_data="settings set arabicStyle 1"
                ),
                InlineKeyboardButton(
                    "Simple", callback_data="settings set arabicStyle 2"
                ),
            ],
            [
                InlineKeyboardButton("Go Back", callback_data="settings home"),
            ],
        ]
        await message.edit_text(reply, reply_markup=InlineKeyboardMarkup(buttons))

    elif query_data[0] == "showTafsir":
        showTafsir = user["settings"]["showTafsir"]
        reply = f"""
<u><b>Change Show Tafsir</b></u>

<b>Show Tafsir</b>: {["No", "Yes"][showTafsir]}

<b>-------------------------</b>

<b>Yes</b>: Show Tafsir with Ayah
<b>No</b>: Don't show Tafsir with Ayah
"""
        buttons = [
            [
                InlineKeyboardButton("No", callback_data="settings set showTafsir 0"),
                InlineKeyboardButton("Yes", callback_data="settings set showTafsir 1"),
            ],
            [
                InlineKeyboardButton("Go Back", callback_data="settings home"),
            ],
        ]
        await message.edit_text(reply, reply_markup=InlineKeyboardMarkup(buttons))

    elif query_data[0] == "reciter":
        reply = f"""
<u><b>Change Reciter</b></u>

<b>Reciter</b>: {reciterNames[str(user["settings"]["reciter"])]}

<b>-------------------------</b>

<b>1</b>: Mishary Rashid Al-Afasy

<b>2</b>: Abu Bakr Al-Shatri

"""
        buttons = [
            [
                InlineKeyboardButton(
                    "Mishary Rashid Al-Afasy", callback_data="settings set reciter 1"
                ),
                InlineKeyboardButton(
                    "Abu Bakr Al-Shatri", callback_data="settings set reciter 2"
                ),
            ],
            [
                InlineKeyboardButton("Go Back", callback_data="settings home"),
            ],
        ]
        await message.edit_text(reply, reply_markup=InlineKeyboardMarkup(buttons))
