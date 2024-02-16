# Changes and Modifications

**Latests are on top**

## 11) 16rd February, 2024
- ...



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
