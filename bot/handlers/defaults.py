defaultSettings = {
    "font": 1,  # 1 -> Uthmani, 2 -> Simple
    "showTafsir": True,
    "reciter": 1,  # 1 -> Mishary Rashid Al-Afasy, 2 -> Abu Bakr Al-Shatri ... etc.
    "primary": "ar",
    "secondary": "en",
    "other": None,
}
defaultGroupSettings = {
    "handleMessages": False,  # Sending `x:y` for ayah (will the bot read `messages` too or not.)
    "allowAudio": True,  # Allow sending audio recitations
    "previewLink": False,  # Show preview of the Tafsir link
    "restrictedLangs": [],
}
defaultChannelSettings = {}


# from: https://quranapi.pages.dev/api/reciters.json
reciterNames = {
    "1": "Mishary Rashid Al Afasy",
    "2": "Abu Bakr Al Shatri",
    "3": "Nasser Al Qatami",
    "4": "Yasser Al Dosari",
    "5": "Hani Ar Rifai",
}
