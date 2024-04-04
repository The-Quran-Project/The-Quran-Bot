from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup

from ..database import db
from .. import Quran


arabicStyles = {
    "1": "Uthmani",
    "2": "Simple",
}

reciterNames = {"1": "Mishary Rashid Al-Afasy", "2": "Abu Bakr Al-Shatri"}


settingsStateText = """
<u><b>Settings</b></u>

<b>Languages:</b>
- <b>Primary</b>    : {primary}
- <b>Secondary</b>  : {secondary}
- <b>Other</b>      : {other}

<b>Arabic Style</b> : {font}
<b>Show Tafsir</b>  : {showTafsir}
<b>Reciter</b>      : {reciter}
"""


async def handleSettingsButtonPress(u: Update, c):
    """Handles the settings buttons press"""
    message = u.effective_message
    userID = u.effective_user.id
    chatID = u.effective_chat.id
    isGroup = chatID != userID

    homeState = [
        [
            InlineKeyboardButton("Languages", callback_data="settings languages"),
            InlineKeyboardButton("Arabic Style", callback_data="settings font"),
        ],
        [
            InlineKeyboardButton("Tafsir", callback_data="settings showTafsir"),
            InlineKeyboardButton("Reciter", callback_data="settings reciter"),
        ],
    ]

    if isGroup:
        return await handleGroupSettingsButtonPress(u, c)

    user = db.getUser(userID)

    query = u.callback_query
    query_data = query.data

    query_data = query_data.split()[1:]
    method = query_data[0]

    if method == "languages":
        reply = "<b>Select your preferred languages by selecting any of the below:</b>"
        buttons = [
            [
                InlineKeyboardButton("Primary", callback_data="settings primary"),
                InlineKeyboardButton("Secondary", callback_data="settings secondary"),
            ],
            [InlineKeyboardButton("Other", callback_data="settings other")],
            [
                InlineKeyboardButton("Back", callback_data="settings home")
            ],  # Return to the home state
        ]

    elif method in ("primary", "secondary", "other"):
        languages = Quran.getLanguages()
        reply = f"""
<b>Select your preferred {method.capitalize()} language:</b>
If you don't want to set any language, select <b>None</b>.

Current Setting: <b>{Quran.getTitleLanguageFromAbbr(user['settings'][method])}</b>
"""
        buttons = [[]]

        for abbr, lang in languages:
            if len(buttons[-1]) == 2:
                buttons.append([])
            buttons[-1].append(
                InlineKeyboardButton(
                    lang, callback_data=f"settings set {method} {abbr}"
                )
            )

        if len(buttons[-1]) == 1:
            buttons[-1].append(
                InlineKeyboardButton(
                    "None", callback_data=f"settings set {method} None"
                )
            )
        else:
            buttons.append(
                [
                    InlineKeyboardButton(
                        "None", callback_data=f"settings set {method} None"
                    )
                ]
            )

        buttons.append(
            [InlineKeyboardButton("Back", callback_data="settings languages")]
        )

    elif method == "set":
        setting = query_data[1]
        title = Quran.getTitleLanguageFromAbbr(query_data[2])

        otherLanguages = (i for i in ("primary", "secondary", "other") if i != setting)

        if title == None and all(user["settings"][i] == "None" for i in otherLanguages):
            reply = "You can't set all of the languages to None. At least one language should be set."
            await query.answer(reply, show_alert=True)
            buttons = homeState
        else:
            user["settings"][setting] = query_data[2]
            db.updateUser(userID, user["settings"])
            reply = f"Your preferred <b>{setting}</b> language has been set to <b>{title}</b>"
            buttons = homeState

    elif method == "font":
        if len(query_data) == 1:
            reply = f"""
<b>Select your preferred Arabic font style:</b>

Uthmani : بِسْمِ ٱللَّهِ ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ
Simple  : بسم الله الرحمن الرحيم

Current Setting: <b>{arabicStyles[str(user['settings']['font'])]}</b>
"""
            buttons = [
                [
                    InlineKeyboardButton("Uthmani", callback_data="settings font 1"),
                    InlineKeyboardButton("Simple", callback_data="settings font 2"),
                ],
                [InlineKeyboardButton("Back", callback_data="settings home")],
            ]
        else:
            user["settings"]["font"] = int(query_data[1])
            db.updateUser(userID, user["settings"])
            reply = f"Your preferred Arabic font style has been set to <b>{arabicStyles[str(user['settings']['font'])]}</b>"
            buttons = homeState

    elif method == "showTafsir":
        if len(query_data) == 1:
            reply = f"""
<b>Select whether you want to see Tafsir in the ayah:</b>

Current Setting: <b>{["No", "Yes"][user['settings']['showTafsir']]}</b>
"""
            buttons = [
                [
                    InlineKeyboardButton("Yes", callback_data="settings showTafsir 1"),
                    InlineKeyboardButton("No", callback_data="settings showTafsir 0"),
                ],
                [InlineKeyboardButton("Back", callback_data="settings home")],
            ]
        else:
            user["settings"]["showTafsir"] = int(query_data[1])
            db.updateUser(userID, user["settings"])
            reply = f"Show Tafsir has been set to <b>{['No', 'Yes'][user['settings']['showTafsir']]}</b>"
            buttons = homeState

    elif method == "reciter":
        if len(query_data) == 1:
            reply = f"""
<b>Select your preferred reciter:</b>

Current Setting: <b>{reciterNames[str(user['settings']['reciter'])]}</b>
"""
            buttons = [
                [
                    InlineKeyboardButton(
                        "Mishary Rashid Al-Afasy", callback_data="settings reciter 1"
                    ),
                    InlineKeyboardButton(
                        "Abu Bakr Al-Shatri", callback_data="settings reciter 2"
                    ),
                ],
                [InlineKeyboardButton("Back", callback_data="settings home")],
            ]
        else:
            user["settings"]["reciter"] = int(query_data[1])
            db.updateUser(userID, user["settings"])
            reply = f"Your preferred reciter has been set to <b>{reciterNames[str(user['settings']['reciter'])]}</b>"
            buttons = homeState

    elif method == "home":
        reply = settingsStateText.format(
            primary=Quran.getTitleLanguageFromAbbr(user["settings"]["primary"]),
            secondary=Quran.getTitleLanguageFromAbbr(user["settings"]["secondary"]),
            other=Quran.getTitleLanguageFromAbbr(user["settings"]["other"]),
            font=arabicStyles[str(user["settings"]["font"])],
            showTafsir=["No", "Yes"][user["settings"]["showTafsir"]],
            reciter=reciterNames[str(user["settings"]["reciter"])],
        )
        buttons = homeState

    if not reply:
        return await query.answer("Maybe it was an old message?", show_alert=True)

    await message.edit_text(reply, reply_markup=InlineKeyboardMarkup(buttons))


async def handleGroupSettingsButtonPress(u: Update, c):
    """Handles the settings buttons press in a group"""
    message = u.effective_message
    userID = u.effective_user.id
    chatID = u.effective_chat.id
    homeStateGroup = [
        [
            InlineKeyboardButton(
                "Handle Messages", callback_data=f"settings handleMessages {userID}"
            ),
            InlineKeyboardButton(
                "Allow Audio", callback_data=f"settings allowAudio {userID}"
            ),
        ],
        [
            InlineKeyboardButton(
                "Preview Link", callback_data=f"settings previewLink {userID}"
            ),
            InlineKeyboardButton(
                "Restricted Languages",
                callback_data=f"settings restrictedLangs {userID}",
            ),
        ],
        [
            InlineKeyboardButton("Close", callback_data=f"close {userID}"),
        ],
    ]

    chat = db.getChat(chatID)
    settings = chat["settings"]
    query = u.callback_query
    query_data = query.data

    query_data = query_data.split()[1:-1]
    method = query_data[0]

    if method == "handleMessages":
        if len(query_data) == 1:
            reply = f"""
<b>Select whether you want to handle messages in this group:</b>

Current Setting: <b>{["No", "Yes"][settings['handleMessages']]}</b>

<b>Yes</b>: Members can send `x:y` to get the ayah
<b>No</b>: Members needs to send send `/get x:y` to get the ayah
"""
            buttons = [
                [
                    InlineKeyboardButton(
                        "Yes", callback_data=f"settings handleMessages 1 {userID}"
                    ),
                    InlineKeyboardButton(
                        "No", callback_data=f"settings handleMessages 0 {userID}"
                    ),
                ],
                [InlineKeyboardButton("Back", callback_data=f"settings home {userID}")],
            ]
        else:
            settings["handleMessages"] = int(query_data[1])
            db.updateChat(chatID, settings)
            reply = f"Handling messages has been set to <b>{['No', 'Yes'][settings['handleMessages']]}</b>"
            buttons = homeStateGroup

    elif method == "allowAudio":
        if len(query_data) == 1:
            reply = f"""
<b>Select whether you want to allow sending audio recitations in this group:</b>

Current Setting: <b>{["No", "Yes"][settings['allowAudio']]}</b>

<b>Yes</b>: Bot will send audio files if asked for
<b>No</b>: Bot will not send audio files if asked for
"""
            buttons = [
                [
                    InlineKeyboardButton(
                        "Yes", callback_data=f"settings allowAudio 1 {userID}"
                    ),
                    InlineKeyboardButton(
                        "No", callback_data=f"settings allowAudio 0 {userID}"
                    ),
                ],
                [InlineKeyboardButton("Back", callback_data=f"settings home {userID}")],
            ]
        else:
            settings["allowAudio"] = int(query_data[1])
            db.updateChat(chatID, settings)
            reply = f"Allowing audio has been set to <b>{['No', 'Yes'][settings['allowAudio']]}</b>"
            buttons = homeStateGroup

    elif method == "previewLink":
        if len(query_data) == 1:
            reply = f"""
<b>Select whether you want to show preview of the Tafsir link in this group:</b>

Current Setting: <b>{["No", "Yes"][settings['previewLink']]}</b>

<b>Yes</b>: Bot will show the preview of the Tafsir link
<b>No</b>: Bot will not show the preview of the Tafsir link

The preview will be like <a href="https://telegra.ph/Tafsir-of-1-1-06-03-4">this</a>
"""
            buttons = [
                [
                    InlineKeyboardButton(
                        "Yes", callback_data=f"settings previewLink 1 {userID}"
                    ),
                    InlineKeyboardButton(
                        "No", callback_data=f"settings previewLink 0 {userID}"
                    ),
                ],
                [InlineKeyboardButton("Back", callback_data=f"settings home {userID}")],
            ]
        else:
            settings["previewLink"] = int(query_data[1])
            db.updateChat(chatID, settings)
            reply = f"Preview link has been set to <b>{['No', 'Yes'][settings['previewLink']]}</b>"
            buttons = homeStateGroup

    elif method == "restrictedLangs":
        allLangs = Quran.getLanguages()
        restrictedLangs = settings["restrictedLangs"]
        reply = (
            "<b>Click on a language to toggle it between restricted & allowed.</b>"
            "\n✅ means the language is allowed.\n❌ means the language is restricted."
            "\n\nRestricted languages are not shown in groups even if the user has the language selected."
        )
        buttons = [[]]
        for langCode, lang in allLangs:
            isRstd = langCode in restrictedLangs
            text = f"{'❌' if isRstd else '✅'} {lang}"

            # unrestrict if already restricted, else restrict
            callback_text = (
                f"settings {'un' if isRstd else ''}restrict {langCode} {userID}"
            )

            button = InlineKeyboardButton(text, callback_data=callback_text)
            if len(buttons[-1]) < 2:
                buttons[-1].append(button)
            else:
                buttons.append([button])

        buttons.append(
            [InlineKeyboardButton("Back", callback_data=f"settings home {userID}")]
        )

    elif method == "restrict":
        langCode = query_data[1]
        allLangs = dict(Quran.getLanguages())
        settings = db.getChat(chatID)["settings"]
        if langCode in settings["restrictedLangs"]:
            return await query.answer(f"{allLangs[langCode]} is already restricted.")

        await query.answer(f"You restricted {allLangs[langCode]}")

        settings["restrictedLangs"].append(langCode)

        db.updateChat(chatID, settings)

        # -- Previous State --
        restrictedLangs = settings["restrictedLangs"]
        reply = (
            "<b>Click on a language to toggle it between restricted & allowed.</b>"
            "\n✅ means the language is allowed.\n❌ means the language is restricted."
            "\n\nRestricted languages are not shown in groups even if the user has the language selected."
        )
        buttons = [[]]
        for langCode, lang in allLangs.items():
            isRstd = langCode in restrictedLangs
            text = f"{'❌' if isRstd else '✅'} {lang}"

            # unrestrict if already restricted, else restrict
            callback_text = (
                f"settings {'un' if isRstd else ''}restrict {langCode} {userID}"
            )

            button = InlineKeyboardButton(text, callback_data=callback_text)
            if len(buttons[-1]) < 2:
                buttons[-1].append(button)
            else:
                buttons.append([button])

        buttons.append(
            [InlineKeyboardButton("Back", callback_data=f"settings home {userID}")]
        )

    elif method == "unrestrict":
        langCode = query_data[1]
        allLangs = dict(Quran.getLanguages())
        settings = db.getChat(chatID)["settings"]
        if langCode not in settings["restrictedLangs"]:
            return await query.answer(f"{allLangs[langCode]} is not restricted.")

        await query.answer(f"You unrestricted {allLangs[langCode]}")

        settings["restrictedLangs"].remove(langCode)

        db.updateChat(chatID, settings)

        # -- Previous State --
        restrictedLangs = settings["restrictedLangs"]
        reply = (
            "<b>Click on a language to toggle it between restricted & allowed.</b>"
            "\n✅ means the language is allowed.\n❌ means the language is restricted."
            "\n\nRestricted languages are not shown in groups even if the user has the language selected."
        )
        buttons = [[]]
        for langCode, lang in allLangs.items():
            isRstd = langCode in restrictedLangs
            text = f"{'❌' if isRstd else '✅'} {lang}"

            # unrestrict if already restricted, else restrict
            callback_text = (
                f"settings {'un' if isRstd else ''}restrict {langCode} {userID}"
            )

            button = InlineKeyboardButton(text, callback_data=callback_text)
            if len(buttons[-1]) < 2:
                buttons[-1].append(button)
            else:
                buttons.append([button])

        buttons.append(
            [InlineKeyboardButton("Back", callback_data=f"settings home {userID}")]
        )

    elif method == "home":
        handleMessages = settings["handleMessages"]
        allowAudio = settings["allowAudio"]
        previewLink = settings["previewLink"]
        restrictedLangs = settings["restrictedLangs"]
        allLangs = dict(Quran.getLanguages())

        # <a href="https://t.me/quraniumbot?startgroup=bot">Add me to your group</a>

        reply = f"""
<u><b>Group Settings</b></u>
Change the settings of the group from here.


<b>Handle Messages</b>  : {["No", "Yes"][handleMessages]}
<b>Allow Audio</b>      : {["No", "Yes"][allowAudio]}
<b>Preview Link</b>     : {["No", "Yes"][previewLink]}
<b>Restricted Languages: </b> {', '.join(allLangs[i] for i in restrictedLangs)}
"""

        buttons = homeStateGroup

    if not reply:
        return await query.answer("Maybe it was an old message?", show_alert=True)

    await message.edit_text(reply, reply_markup=InlineKeyboardMarkup(buttons))
