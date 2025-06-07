# Changes and Modifications

**Latests are on top**

## 19) 8th June, 2025
- Add `uzbek` translation
- Add 3 more reciters. Now it supports all reciters from [Quran API](https://quranapi.pages.dev/getting-started/available-reciters)
  - Mishary Rashid Al Afasy
  - Abu Bakr Al Shatri
  - Nasser Al Qatami
  - Yasser Al Dosari
  - Hani Ar Rifai


## 18) 5th June, 2025
- Reimplement the local cached mongodb database with much simpler logic.
- Fix bug where `x:y` to get the verse was not restricting the restricted languages.
- Possible fix for `/schedule` verses. For some reason, they sometimes miss.


## 17) 30th November, 2024
- Add Active users field
- Forward messages to the active users only and give proper report
- `/login` command to login as an admin
- Keep log of daily request count in `db.analytics`


## 16) 29th November, 2024

- Better Search for the Surahs

## 15) 20th October, 2024

- Bot can now send the audio of a Full Surah.
  - Example: `/audio 1` will send the audio of Surah no. 1, Al-Fatihah.
- Dev Feature:
  - Developer can pass arguments from terminal.
    - Try out `python main.py --help` to see the available options.
- Other minor bug fixes and improvements.

## 14) 19th October, 2024

- Bug fix: If the user has 3 selected translations and asks for a verse that is long enough to exceed `4092` character limit, bot sent an error message.
  - Now, the bot will send the verse in with the first 2 translations only. And mention the user that the verse is too long to send with all the translations.

> Did some minor changes throughout this period. But, I forgot to keep the logs. Sorry for that.

## 14) 22nd April, 2024

- `/schedule` command bug fixed. Now, the bot will send the scheduled verse at the exact time.
- `/schedule` command will now send the verse in the group where the command was sent.
- `/delete` admin command added to delete a message sent by the bot.
- `/showJson` admin command added. It'll show the JSON data of the group.
- Refactor decorators to make the code more readable and maintainable.

## 13) 19th April, 2024

- `/schedule` command added. Now, you can schedule a verse to be sent at a specific time of every day.

## 12) 5th April, 2024

- Integrate custom local database logic to make database operations faster and more efficient.
- Add **Russian** translation of the Quran. Now, the bot supports 9 languages.
- Other minor bug fixes and improvements.

## 11) 16rd February, 2024

- Added 7 new translations of the Quran. Now, the bot supports 8 languages.
- Get your specific translation by `/<lang> x:y` command. Example: `/ben 1:2` (lang will be auto completed)
- `/settings` command for group admins to change the bot's settings in the group.
- Alert the user if bot doesn't have permission to send audio files in the group.
- `/start` command will only send the salam sticker in private chats, not in groups.
- `/info` command will only send the text in groups. In private chats, it'll send the text and the user's profile photo.
- Verses are given in quoted formatting.
- Refactored the code to make it more readable and maintainable.

## 10) 27th January, 2024

- Bug Fix: `/settings` command was not working properly. Now, it's fixed.

## 9) 25th January, 2024

- Fix: Bot replies wrong messages when someone joins a group [1]
- Fix: Bot replies with ayah if user types x:y or just x in group [1]
- Only who sent /get x:y can interact with the message buttons
- `x:y` will only work in private chat. In group, you have to use `/get x:y`

## 8) 13th January, 2024

- Added `/get`, `/get<lang>`, `/audio`, `/tafsir` commands
- Deprecate `/surah x:y` command. Now, you can use `/get x:y` instead.
- New reciter added: `Abu Bakr Al-Shatri` [May Allah bless him]
- Mention credits in `/about` command

## 5) 30th December, 2023

- Integrated MongoDB to store user's data. Now, the bot will remember the user's preference. To change `/settings`
- Refactored and restructured the code to make it more readable and maintainable.

## 4) 11th August, 2023

- added `keep_alive` file to prevent bot from going to sleep in cloud providers
- Refactored code to make it more readable

## 3) 4th July, 2023

- `/random` or `/rand` command added. As guessed, it'll give you a random verse from the Quran.
- Example: `/rand` or `/random` [Both are the same]
- Fixed a bug that was rejecting to search for surah if the text contained space.

## 2) 2nd July, 2023

- `/surah` command added. So, you can get any verse by doing `/surah <surah name>:<verse number>`
- Example: `/surah 1:2`

- Changed Folder Structure. Added `ChangeLogs` and `TODO` files. Now the project is more organized.

## 1) 1st July, 2023

- User can just send any surah name and the bot will send at most 3 options to choose from.
- The options will be the most relevant surahs that matches the user's given name.
- Example: `Fatiha` will give `1 Al-Fatihah`, `20 Taha` and `48 Al-Fath` as options. But `Fatihah` will only give `1 Al-Fatihah` as option. The capitalization from the user doesn't matter.

## Previous Logs have not been kept. Sorry for the inconvenience.
