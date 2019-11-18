import sys

import pyautogui
import pytesseract
from numpy import array, int as np_int
from PIL import Image, ImageEnhance

from .constants import *
from .models import Score


__all__ = [
    'get_scores_from_screen',
    'is_on_scores_screen',
    'is_on_character_select_screen',
]


def get_scores_from_screen() -> [(str, str, Score)]:
    scores = []

    for i, offset in enumerate(get_score_box_offsets()):
        score_image = pyautogui.screenshot(region=offset.score_region.tuple)
        name_image = pyautogui.screenshot(region=offset.name_region.tuple)
        account_image = pyautogui.screenshot(region=offset.account_region.tuple)
        account = get_name_from_image(account_image)
        scores.append((
            get_name_from_image(name_image),
            ScoreBoxOffsets.AccountAlias.get(account, account),
            Score(i + 1, get_score_data_from_image(score_image))
        ))

    return scores


def is_on_scores_screen() -> bool:
    return color_at_points(Colors.WinLabel, Positions.win_label_offsets()) \
           and color_at_points(Colors.WinLabelBorder, Positions.win_label_border_offsets())


def is_on_character_select_screen() -> bool:
    # TODO: is_on_character_select_screen
    return not is_on_scores_screen()


# region Detail


class Region:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    @property
    def corners(self):
        return self.x, self.y, self.x + self.width, self.y + self.height

    @property
    def tuple(self):
        return self.x, self.y, self.width, self.height


class ScoreBoxOffsets:

    # TODO: Replace AccountAlias with improved account name recognition
    AccountAlias: {str: str} = {
        'PlayerI': 'Player1',
    }

    def __init__(self, position: Vec2, player_index: int = 0):

        multiplier = array([player_index, 0 if not player_index else 1], dtype=np_int)

        self.position = position + Positions.NonWinningPlayerOffset * multiplier

        self.rank_offset = self.position + Positions.RankLabelOffset

        self.account_region = Region(
            *(self.position + Positions.AccountLabelOffset), *Sizes.AccountLabel)

        self.name_region = Region(
            *(self.position + Positions.NameLabelOffset), *Sizes.NameLabel)

        self.score_region = Region(
            *(self.position + Positions.ScoreAreaOffset), *Sizes.ScoreArea)

    @staticmethod
    def all():
        return {
            'couch_4': [ScoreBoxOffsets(Positions.score_box_first_offset_4_player(), i) for i in range(4)],
            'couch_3': [ScoreBoxOffsets(Positions.score_box_first_offset_3_player(), i) for i in range(3)],
            'couch_2': [ScoreBoxOffsets(Positions.score_box_first_offset_2_player(), i) for i in range(2)]
        }


def color_at_point(color: Color, point: Vec2) -> bool:
    return color == pyautogui.pixel(int(point[0]), int(point[1]))


def color_at_points(color: Color, points: [Vec2]) -> bool:
    return all(color_at_point(color, p) for p in points)


def colors_at_points(points_and_colors: [(Vec2, Color)]) -> bool:
    return all(color_at_point(c, p) for p, c in points_and_colors)


def get_score_box_offsets() -> [ScoreBoxOffsets]:
    # TODO: Add support for teams
    # TODO: Add support for ranked
    # TODO: Add support for ranked teams
    for _, offsets in ScoreBoxOffsets.all().items():
        if color_at_points(Colors.RankLabel, map(lambda x: x.rank_offset, offsets)):
            return offsets
    return []


def get_name_from_image(image: Image.Image) -> str:
    prefix = '-' if sys.platform in {'win32', 'cygwin'} else ''
    enhancer = ImageEnhance.Sharpness(image)
    enhanced = enhancer.enhance(Numbers.NameLabelSharpnessEnhanceFactor)
    threshold = enhanced.point(lambda p: p > Numbers.NameLabelWhiteThreshold and 255)
    text = pytesseract.image_to_string(threshold, lang='eng', config=prefix + '-psm 7')
    return text.replace(' ', '')


def get_score_data_from_image(image: Image.Image) -> (int, int, int, int, int, int):
    prefix = '-' if sys.platform in {'win32', 'cygwin'} else ''
    text = pytesseract.image_to_string(image, lang='numbers', config=prefix + '-psm 6')
    return tuple(map(lambda v: int(v), filter(lambda v: v != '', text.split('\n'))))


# endregion
