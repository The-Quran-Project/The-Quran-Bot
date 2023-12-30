from telegram import InlineKeyboardButton
from ...quran import QuranClass


def splitListIntoChunks(listToSplit: list, chunkSize: int = 3):
    """
    Splits a list into chunks of the given size.

    Args:
        listToSplit (list): The list to split.
        chunkSize (int, optional): The size of each chunk. Defaults to 3.

    Returns:
        list: A 2D list of the given list split into chunks.

    Examples:
        >>> splitListIntoChunks([1, 2, 3, 4, 5, 6], 2)
        [[1, 2], [3, 4], [5, 6]]

        >>> splitListIntoChunks([1, 2, 3, 4, 5, 6], 3)
        [[1, 2, 3], [4, 5, 6]]

        >>> splitListIntoChunks([1, 2, 3, 4, 5, 6], 4)
        [[1, 2, 3, 4], [5, 6]]

    Note:
        Here, this function is used to split a list of buttons into chunks of 3 buttons per row.
    """

    x = []
    while listToSplit:
        x.append(listToSplit[:chunkSize])
        listToSplit = listToSplit[chunkSize:]

    return x


def generateSurahButtons(Quran: QuranClass):
    """
    Generates page-wise buttons for all the surahs in the Quran.
    Each page contains 33 buttons (11 rows of 3 buttons each).

    Args:
        Quran (QuranClass): An instance of the QuranClass.

    Returns:
        list: A 2D list of `InlineKeyboardButtons` for all the surahs in the Quran.

    Examples:
        >>> getSurahButtons(Quran)
        [
            [
                [InlineKeyboardButton("1 Al-Fatihah", callback_data="surahName 1"),
                InlineKeyboardButton("2 Al-Baqarah", callback_data="surahName 2"),
                InlineKeyboardButton("3 Al-Imran", callback_data="surahName 3")],
                [InlineKeyboardButton("Previous", callback_data="prev 1"),
                InlineKeyboardButton("Next", callback_data="next 1")]
            ],
            [
                [InlineKeyboardButton("4 An-Nisa", callback_data="surahName 4"),
                InlineKeyboardButton("5 Al-Ma'idah", callback_data="surahName 5"),
                InlineKeyboardButton("6 Al-An'am", callback_data="surahName 6")],
                [InlineKeyboardButton("Previous", callback_data="prev 2"),
                InlineKeyboardButton("Next", callback_data="next 2")]
            ],
            ...
        ]
    """
    inlineButtons = [[]]
    allSurahNames = Quran.SURAHS

    # A Matrix of 11 x 3 per page
    # | 1  | 2  | 3  |
    # | 4  | 5  | 6  |
    # | 7  | 8  | 9  |
    # | 10 | 11 | 12 |
    # | 13 | 14 | 15 |
    # | 16 | 17 | 18 |
    # | 19 | 20 | 21 |
    # | 22 | 23 | 24 |
    # | 25 | 26 | 27 |
    # | 28 | 29 | 30 |
    # | 31 | 32 | 33 |
    # | Prev | Next |
    totalButtonsPerRow = 3  # 3 buttons per row, means 3 columns per row
    totalButtonsPerPage = 33  # 33 buttons per page, means 11 rows per page

    for surahNumber, surahName in enumerate(allSurahNames, start=1):
        button = InlineKeyboardButton(
            f"{surahNumber} {surahName}", callback_data=f"surahName {surahNumber}"
        )
        buttonsCount = len(inlineButtons[-1])
        pageCount = len(inlineButtons)

        if buttonsCount < totalButtonsPerPage:
            inlineButtons[-1].append(button)
        else:
            navigationButtons = [
                InlineKeyboardButton("Previous", callback_data=f"prev {pageCount-1}"),
                InlineKeyboardButton("Next", callback_data=f"next {pageCount-1}"),
            ]
            inlineButtons[-1] = splitListIntoChunks(inlineButtons[-1])
            inlineButtons[-1].append(navigationButtons)

            inlineButtons.append([button])

    if inlineButtons[-1]:
        navigationButtons = [
            InlineKeyboardButton("Previous", callback_data=f"prev {pageCount-1}"),
            InlineKeyboardButton("Next", callback_data=f"next {pageCount-1}"),
        ]
        inlineButtons[-1] = splitListIntoChunks(inlineButtons[-1])
        inlineButtons[-1].append(navigationButtons)
    
    return inlineButtons
