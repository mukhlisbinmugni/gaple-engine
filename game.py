from deck import Deck
from player import Player
from table import Table

from move import Move
from move_generator import MoveGenerator
from turn_result import TurnResult, TurnStatus


class Game:
    """
    Mengatur jalannya permainan Gaple.
    """

    def __init__(self):

        self.deck = Deck()

        self.players = [
            Player("P1"),
            Player("P2"),
            Player("P3"),
            Player("Mukhlis")
        ]

        self.table = Table()

        self.move_generator = MoveGenerator()

        self.current_player = 0

        # Status permainan
        self.game_over = False

        # Jumlah PASS berturut-turut
        self.pass_count = 0

        # Move terakhir yang benar-benar dimainkan (bukan PASS),
        # dan siapa yang memainkannya.
        # Fakta ini dibutuhkan oleh RuleSystem untuk mendeteksi
        # PASAR dan untuk mengidentifikasi pembuat guplah. Game
        # hanya mencatat fakta ini, tidak menafsirkannya.
        self.last_move = None
        self.last_move_player = None

    def start(self):
        """
        Mengocok kartu dan membagikannya.
        """

        self.deck.shuffle()

        hands = self.deck.deal()

        for player, hand in zip(self.players, hands):
            player.hand = hand

        self.current_player = 0
        self.game_over = False
        self.pass_count = 0
        self.last_move = None
        self.last_move_player = None

    def active_player(self):
        """
        Mengembalikan pemain yang sedang mendapat giliran.
        """
        return self.players[self.current_player]

    def next_turn(self):
        """
        Berpindah ke pemain berikutnya.
        """
        self.current_player = (
            self.current_player + 1
        ) % len(self.players)

    def is_over(self):
        """
        Mengembalikan True jika game telah selesai.
        """
        return self.game_over

    def choose_move(self, moves: list[Move]) -> Move:
        """
        Memilih satu move legal.

        Untuk sementara selalu memilih move pertama.
        Nantinya method ini akan diganti AI.
        """
        return moves[0]

    def play_turn(self) -> TurnResult:
        """
        Menjalankan satu giliran permainan.
        """

        if self.game_over:
            raise ValueError("Game sudah selesai.")

        player = self.active_player()

        moves = self.move_generator.generate(
            player.hand,
            self.table
        )

        # ==========================
        # PASS
        # ==========================

        if not moves:

            self.pass_count += 1

            if self.pass_count >= len(self.players):
                self.game_over = True

            result = TurnResult(
                player=player,
                move=None,
                status=TurnStatus.PASS
            )

            if not self.game_over:
                self.next_turn()

            return result

        # ==========================
        # PLAY
        # ==========================

        # Ada yang berhasil bermain,
        # maka PASS beruntun di-reset.
        self.pass_count = 0

        move = self.choose_move(moves)

        self.table.play(move)

        player.play(move.dominoes[0])

        # Catat move ini sebagai move terakhir yang dimainkan,
        # dan siapa yang memainkannya.
        self.last_move = move
        self.last_move_player = player

        if player.is_empty():
            self.game_over = True

        result = TurnResult(
            player=player,
            move=move,
            status=TurnStatus.PLAY
        )

        if not self.game_over:
            self.next_turn()

        return result