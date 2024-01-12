start = """
Assalamu Alaikum <b>{firstName}!</b>

This bot will give you verses from the Al-Quran.

It can give you the <b>Arabic</b> or <b>English</b> text and also the <b>Audio</b> of each ayah.

See, /use to know how to use this bot.

This bot is <a href="{repoURL}">open-source</a>. Your contribution can make it more helpful for the Ummah.

The Arabic, English and Tafsir's were taken from quran.com
"""

help = """
To know how to use the bot:
/use - A brief overview on how to use the bot


For any questions or discussions, reach out to @AlQuranDiscussion.
Stay updated with @AlQuranUpdates

Contact Maintainers: @Roboter403,  @Nusab19"""

howToUse = """
<u>Basic Commands:</u>
/start - Check if the bot is Alive
/help - Where to contact the dev and the community
/about - About the bot
/use - This message
/info - Details of the current chat
/ping - Check server's ping
/settings - Change your settings

<u>Usage of Bot:</u>
/surah - The list of all the Surahs
/get x:y - Get the ayah x from Surah y
/geten x:y - Get the English translation of ayah x from Surah y
/tafsir x:y - Get the Tafsir of ayah x from Surah y
/audio x:y - Get the audio of ayah x from Surah y

Send any message like:
<code>x : y</code>
<code>1:3</code>

<b>
Here, `x` means the surah no. and `y` means ayah no.</b>

For more in depth usage, check the <a href="{telegraphURL}">Telegraph</a> link."""


sendAyah = """
Surah : <b>{surahName} ({surahNo})</b>
Ayah  : <b>{ayahNo} out of {totalAyah}</b>
"""


about = """
Al Quran Bot is a bot that can give you verses from the Al-Quran. It is a non-profit project and is open-source.

<u><b>Credits:</b></u>
- The Arabic, English and Tafsir's were taken from [quran.com](https://quran.com)
- The recitations were taken from [everyayah.com](https://everyayah.com)
- The bot is hosted on [Render](https://render.com)
- The bot is written in Python3 using the [python-telegram-bot](https://t.me/pythontelegrambotgroup) library
- The bot is maintained by @Roboter403 and @Nusab19
"""
