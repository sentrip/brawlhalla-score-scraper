from abc import ABC, abstractmethod
from collections import namedtuple

from numpy import array, int as np_int
from nptyping import Array


__all__ = [
    'Color', 'Size', 'Vec2',
    'Runnable', 'Legends',
    'Colors', 'Events', 'Numbers',
    'Positions', 'Screen', 'Sizes',
]


Color = namedtuple("Color", ["red", "green", "blue"])
Color.to_int = lambda s: ((s.red << 16) | (s.blue << 8) | s.green)
Color.from_int = lambda i: Color((i >> 16) & 255, (i >> 8) & 255, i & 255)

Size = namedtuple("Size", ["width", "height"])

Vec2 = Array[np_int]


class Runnable(ABC):
    @abstractmethod
    def run(self):
        pass


class Legends:

    all = {
        'BODVAR', 'GNASH', 'SCARLET', 'LUCIEN', 'BARRAZA',
        'ULGRIM', 'WUSHANG', 'MIRAGE', 'ARTEMIS', 'KAYA',
        'ZARIEL', 'THOR', 'CASSIDY', 'QUEENNAI', 'THATCH',
        'TEROS', 'EMBER', 'DIANA', 'VAL', 'NIX',
        'CASPIAN', 'ISAIAH', 'RAYMAN', 'PETRA', 'ORION',
        'HATTORI', 'ADA', 'BRYNN', 'AZOTH', 'JHALA',
        'RAGNIR', 'MORDEX', 'SIDRA', 'JIRO', 'DUSK',
        'VECTOR', 'LORDVRAXX', 'SIRROLAND', 'SENTINEL', 'ASURI',
        'KOJI', 'KOR', 'CROSS', 'YUMIKO', 'XULL',
        'LINFEI', 'FAIT'
    }

    @staticmethod
    def exists(name: str) -> bool:
        return name in Legends.all


class Colors:
    Black: Color = Color(0, 0, 0)
    White: Color = Color(255, 255, 255)

    # Background color of position label after match (1st, 2nd, ...)
    RankLabel: Color = Color(20, 20, 60)

    # Background color of winning legend label after match (PETRA WINS!)
    WinLabel: Color = Color(0, 0, 51)

    # Top border color of winning legend label after match (PETRA WINS!)
    WinLabelBorder: Color = Color(0, 0, 51)


class Numbers:
    Port: int = 5000

    # Factor for ImageEnhance.Sharpness when processing name label
    NameLabelSharpnessEnhanceFactor: float = 5.0

    # Threshold for name label color (all colors below this are blacked out)
    NameLabelWhiteThreshold: int = 230

    # Threshold for account label color (all colors below this are blacked out)
    AccountLabelWhiteThreshold: int = 120


def arr(*args):
    return array(args, dtype=np_int)


class Screen:
    Width: int = 2560  # pyautogui.size().width
    Height: int = 1080  # pyautogui.size().height

    @staticmethod
    def center() -> Vec2:
        return arr(Screen.Width / 2, Screen.Height / 2)

    @staticmethod
    def border() -> Vec2:
        center = Screen.center()
        return arr(center[0] - 1920 / 2, center[1] - 1080 / 2)


class Positions:
    # Offset of account label comparing to the score box
    AccountLabelOffset: Vec2 = arr(70, 35)

    # Offset of name label comparing to the score box
    NameLabelOffset: Vec2 = arr(70, 5)

    # Offset of the right most score boxes comparing to the left most box
    NonWinningPlayerOffset: Vec2 = arr(390, 90)

    # Offset of a consistent pixel in the rank label comparing to the score box
    RankLabelOffset: Vec2 = arr(137, -33)

    # Offset from top left of score box to top left of area with only numbers
    ScoreAreaOffset: Vec2 = arr(140, 78)

    # Offsets of the left most score box for 2, 3 and 4 player screens
    @staticmethod
    def score_box_first_offset_4_player() -> Vec2:
        return Screen.border() + arr(240, 620)

    @staticmethod
    def score_box_first_offset_3_player() -> Vec2:
        return Screen.border() + arr(433, 620)

    @staticmethod
    def score_box_first_offset_2_player() -> Vec2:
        return Screen.border() + arr(628, 620)

    # Offset of a consistent pixel in the win label border
    @staticmethod
    def win_label_border_offset() -> Vec2:
        return Screen.border() + arr(1920 / 2, 36)

    # Offset of a line of consistent pixels in the win label border
    @staticmethod
    def win_label_border_offsets() -> [Vec2]:
        # + BRWL_win_label_offset * arr(i, 0)
        #  for i in range(-40, 60, 20)]
        return [Positions.win_label_border_offset()]

    # Offset of a consistent pixel in the win label
    @staticmethod
    def win_label_offset() -> Vec2:
        return Screen.border() + arr(1920 / 2, 40)

    # Offsets of a line of consistent pixels in the win label
    @staticmethod
    def win_label_offsets() -> [Vec2]:
        # + BRWL_win_label_offset * arr(i, 0)
        # for i in range(-40, 60, 20)]
        return [Positions.win_label_offset()]


class Sizes:
    # Size of the score box
    ScoreBox: Size = Size(270, 230)

    # Size of label containing account name in the score box
    AccountLabel: Size = Size(200, 35)

    # Size of label containing legend name in the score box
    NameLabel: Size = Size(200, 35)

    # Size of area containing only numbers in the score box
    ScoreArea: Size = Size(
        ScoreBox.width - Positions.ScoreAreaOffset[0],
        ScoreBox.height - Positions.ScoreAreaOffset[1]
    )


class Events:

    class Command:
        Pause: str = 'pause'
        AddPlayer: str = 'add_player'
        RemovePlayer: str = 'remove_player'
        AddAccount: str = 'add_account'
        RemoveAccount: str = 'remove_account'

    class Player:
        NewScores: str = 'player_new_scores'
        UpdatedAccounts: str = 'player_updated_accounts'
        UpdatedPlayers: str = 'player_updated_players'
        UpdatedPlayerAccounts: str = 'player_updated_player_accounts'
        UpdatedLivePlayers: str = 'player_updated_live_players'

    class Server:
        DeletePlayer: str = 'server_delete_player'
        SetAccount: str = 'server_set_account'
        SetPlayer: str = 'server_set_player'
