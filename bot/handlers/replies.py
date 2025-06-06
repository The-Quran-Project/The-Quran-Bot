start = """
Assalamu Alaikum <b>{firstName}!</b>

See, /use to know how to use this bot.

This bot is <a href="{repoURL}">open-source</a>. Your contribution can make it more helpful for the Ummah.

For any feedback, discuss in here: @AlQuranDiscussion.
Get the latest updates of the bot: @AlQuranUpdates
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
/showJSON - Get the JSON of the current update

<u>Usage of Bot:</u>
/settings - Change your settings
/surah - The list of all the Surahs
/get x:y - Get the ayah x from Surah y
/lang x:y - Get the ayah <code>x</code> from Surah <code>y</code> in the language &lt;lang&gt;
/schedule 11:30 - Get a random ayah at 11:30 everyday
<i>See the Telegraph for more in depth usage of schedule</i>

/langs, /languages, /translations - Get the list of all the available translations
/rand, /random - Get a random ayah
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
- The Translations and Tafsirs were taken from <a href="https://quran.com">quran.com</a>
- The tafsir used here is from <a href="https://quran.com/1:1/tafsirs/en-tafisr-ibn-kathir">Ibn Kathir</a>
- The recitations were taken from <a href="https://everyayah.com">everyayah.com</a>
- The bot is hosted on <a href="http://koyeb.com/">Koyeb</a>
- The bot is written in Python3 using the <a href="https://t.me/pythontelegrambotgroup">python-telegram-bot</a> library
- The bot is maintained by @Roboter403 and @Nusab19
"""


adminCommands = """
Commands:
/forward <code>chatID</code> [ Reply to a message ]
/getUser <code>chatID</code> [ Reply to a message ]
/delete [ Reply to a message ]
/eval <code>Python Code</code>
"""
