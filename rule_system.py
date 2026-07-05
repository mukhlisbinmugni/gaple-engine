from game_end_result import (
    GameEndResult,
    FinishType,
    SpecialResult,
)


class RuleSystem:
    """
    RuleSystem hanya mengevaluasi Game yang sudah selesai.
    Tidak menjalankan gameplay.
    """

    # =========================================================
    # MAIN EVALUATION
    # =========================================================
    @staticmethod
    def evaluate(game):
        finish_type = RuleSystem.detect_finish_type(game)

        if finish_type == FinishType.GUPLAH:
            player_points = RuleSystem.calculate_player_points(game)
            winner = RuleSystem.find_guplah_winner(
                player_points, game.last_move_player
            )
        else:
            winner = RuleSystem.detect_winner(game)

        special_result = RuleSystem.detect_special_result(
            game, finish_type, winner
        )

        penalty_changes = RuleSystem.calculate_penalty_changes(
            game,
            winner,
            finish_type,
            special_result
        )

        return GameEndResult(
            winner=winner,
            finish_type=finish_type,
            special_result=special_result,
            penalty_changes=penalty_changes
        )

    # =========================================================
    # WINNER DETECTION
    # =========================================================
    @staticmethod
    def detect_winner(game):
        for player in game.players:
            if player.is_empty():
                return player
        return None

    # =========================================================
    # FINISH TYPE
    # =========================================================
    @staticmethod
    def detect_finish_type(game):
        """
        DOM/PASAR hanya bisa terdeteksi jika ada pemain yang
        habis kartunya. PASAR adalah bentuk khusus dari DOM:
        domino terakhir yang dimainkan harus legal di KEDUA
        ujung meja pada saat SEBELUM domino itu dimainkan.

        PASAR TIDAK dideteksi dari jumlah PASS berturut-turut.
        (Lihat AI_CONTEXT.md: "Do not model PASAR as merely
        four consecutive PASS actions.")

        GUPLAH terjadi ketika tidak ada pemain yang habis
        kartunya, tetapi permainan sudah berhenti (game.game_over
        bernilai True) karena satu putaran penuh semua pemain
        PASS. game.game_over adalah fakta yang sudah dicatat oleh
        Game sendiri; RuleSystem hanya menafsirkannya sebagai
        GUPLAH.

        Jika belum ada pemain yang habis kartunya DAN game belum
        berhenti, game belum selesai dan hasilnya untuk sementara
        dikembalikan sebagai FinishType.NORMAL.
        """

        for player in game.players:
            if player.is_empty():
                if RuleSystem._is_pasar(game):
                    return FinishType.PASAR
                return FinishType.DOM

        if game.game_over:
            return FinishType.GUPLAH

        return FinishType.NORMAL

    # =========================================================
    # PASAR DETECTION (INTERNAL)
    # =========================================================
    @staticmethod
    def _is_pasar(game):
        """
        PASAR terjadi jika domino terakhir yang dimainkan
        legal dipasang di kedua ujung meja SEBELUM domino
        tersebut dimainkan.

        Membutuhkan dua fakta yang dicatat oleh Game/Table:
        - game.last_move: Move terakhir yang dimainkan.
        - table.previous_left_end / previous_right_end:
          ujung meja sebelum move terakhir diterapkan.

        Jika meja masih kosong sebelum move terakhir (artinya
        move terakhir adalah move pembuka), PASAR tidak
        didefinisikan untuk kondisi ini, sehingga dianggap
        bukan PASAR.

        PASAR hanya berlaku untuk move satu-placement (NORMAL).
        Move dengan lebih dari satu placement (mis. RATUS) bukan
        PASAR, terlepas dari kondisi meja sebelumnya.
        """

        move = game.last_move

        if move is None:
            return False

        if len(move.placements) != 1:
            return False

        table = game.table

        if table.previous_left_end is None or table.previous_right_end is None:
            return False

        domino = move.placements[0].domino

        return (
            domino.can_connect(table.previous_left_end)
            and domino.can_connect(table.previous_right_end)
        )

    # =========================================================
    # SPECIAL RESULT
    # =========================================================
    @staticmethod
    def detect_special_result(game, finish_type, winner):
        """
        Untuk finish_type selain GUPLAH, belum ada special result
        yang didefinisikan (RATUS/RIBU reserved untuk masa depan).

        Untuk GUPLAH, special result menandai hasil dari upaya
        pembuat guplah, terpisah dari finish_type itu sendiri:
        - SpecialResult.GUPLAH: pembuat guplah adalah winner.
        - SpecialResult.FAILED_GUPLAH: pembuat guplah BUKAN
          winner (pip-nya kalah dari pemain lain).
        """

        if finish_type != FinishType.GUPLAH:
            return SpecialResult.NONE

        if game.last_move_player == winner:
            return SpecialResult.GUPLAH

        return SpecialResult.FAILED_GUPLAH

    # =========================================================
    # PENALTY SYSTEM
    # =========================================================
    @staticmethod
    def calculate_penalty_changes(game, winner, finish_type, special_result):
        player_points = RuleSystem.calculate_player_points(game)

        if finish_type == FinishType.DOM:
            return RuleSystem.calculate_dom_score(player_points, winner)

        if finish_type == FinishType.PASAR:
            return RuleSystem.calculate_pasar_score(player_points, winner)

        if finish_type == FinishType.GUPLAH:
            return RuleSystem.calculate_guplah_score(
                player_points, winner, game.last_move_player
            )

        return {}

    # =========================================================
    # PLAYER POINTS
    # =========================================================
    @staticmethod
    def calculate_player_points(game):
        return {
            player: player.total_pips()
            for player in game.players
        }

    # =========================================================
    # DOMINO RANK (SUM-BASED, sesuai MASTER_CORE.md Step 4)
    # =========================================================
    @staticmethod
    def domino_rank(domino):
        """
        Urutan pembanding satu domino:
        1. Pip sum (kedua sisi dijumlahkan).
        2. Jika sum sama, nilai sisi yang lebih tinggi.
        3. Jika masih sama, nilai sisi yang lebih rendah.

        Karena setiap domino pada satu set double-six bersifat
        unik, urutan ini selalu deterministik ketika
        membandingkan dua domino milik dua pemain berbeda.
        """

        high = max(domino.left, domino.right)
        low = min(domino.left, domino.right)

        return (
            domino.left + domino.right,
            high,
            low,
        )

    # =========================================================
    # HIGHEST DOMINO (per pemain, sum-based)
    # =========================================================
    @staticmethod
    def highest_domino(player):
        return max(player.hand, key=RuleSystem.domino_rank)

    # =========================================================
    # BALAK HELPERS
    # =========================================================
    @staticmethod
    def _balak_dominoes(player):
        """
        Mengembalikan seluruh domino balak (kembar) yang
        dipegang seorang pemain.
        """
        return [d for d in player.hand if d.left == d.right]

    @staticmethod
    def _highest_balak_value(player):
        """
        Nilai pip dari balak tertinggi yang dipegang pemain.
        Hanya valid dipanggil untuk pemain yang dipastikan
        memegang setidaknya satu balak.
        """
        balak = RuleSystem._balak_dominoes(player)
        return max(d.left + d.right for d in balak)

    # =========================================================
    # DOM / PASAR PENALTY RECIPIENT
    # Mengikuti MASTER_CORE.md:
    # Step 1 -> Step 2 -> Step 3.0 -> Step 3a -> Step 3b -> Step 4
    #
    # Nama method ini tetap "find_dom_loser" untuk menjaga
    # kompatibilitas dengan test yang sudah ada. Fungsi ini juga
    # dipakai oleh calculate_pasar_score, karena tie-break untuk
    # menentukan penerima denda PASAR sudah dikonfirmasi identik
    # dengan DOM — hanya nilai penalti yang berbeda (4, bukan 3).
    # =========================================================
    @staticmethod
    def find_dom_loser(player_points, winner):

        candidates = [p for p in player_points if p != winner]

        if len(candidates) == 1:
            return candidates[0]

        # ---------------------------------
        # STEP 1: TOTAL PIP TERBESAR
        # ---------------------------------
        max_points = max(player_points[p] for p in candidates)
        candidates = [p for p in candidates if player_points[p] == max_points]

        if len(candidates) == 1:
            return candidates[0]

        # ---------------------------------
        # STEP 2: JUMLAH KARTU TERBANYAK
        # ---------------------------------
        max_cards = max(len(p.hand) for p in candidates)
        candidates = [p for p in candidates if len(p.hand) == max_cards]

        if len(candidates) == 1:
            return candidates[0]

        # ---------------------------------
        # STEP 3.0: KEPEMILIKAN BALAK
        # ---------------------------------
        balak_holders = [
            p for p in candidates if RuleSystem._balak_dominoes(p)
        ]

        if len(balak_holders) == 1:
            return balak_holders[0]

        if len(balak_holders) >= 2:
            candidates = balak_holders

            # ---------------------------------
            # STEP 3a: JUMLAH BALAK TERBANYAK
            # ---------------------------------
            max_balak_count = max(
                len(RuleSystem._balak_dominoes(p)) for p in candidates
            )
            candidates = [
                p for p in candidates
                if len(RuleSystem._balak_dominoes(p)) == max_balak_count
            ]

            if len(candidates) == 1:
                return candidates[0]

            # ---------------------------------
            # STEP 3b: NILAI BALAK TERTINGGI
            # ---------------------------------
            max_balak_value = max(
                RuleSystem._highest_balak_value(p) for p in candidates
            )
            candidates = [
                p for p in candidates
                if RuleSystem._highest_balak_value(p) == max_balak_value
            ]

            # Karena setiap nilai balak unik dalam satu set,
            # Step 3b seharusnya selalu menghasilkan tepat satu
            # kandidat. Jika tidak, ada bug di tempat lain
            # (mis. data domino rusak/duplikat) — engine harus
            # berhenti secara eksplisit, bukan diam-diam memilih
            # candidates[0].
            if len(candidates) == 1:
                return candidates[0]

            raise RuntimeError(
                "Unexpected tie after Step 3b: multiple players "
                "have identical highest balak value."
            )

        # Tidak ada kandidat yang memegang balak sama sekali.
        # Lanjut ke Step 4 dengan seluruh kandidat yang tersisa.

        # ---------------------------------
        # STEP 4: DOMINO TERTINGGI (SUM-BASED)
        # ---------------------------------
        def highest_rank(player):
            return RuleSystem.domino_rank(
                RuleSystem.highest_domino(player)
            )

        best_rank = max(highest_rank(p) for p in candidates)
        candidates = [p for p in candidates if highest_rank(p) == best_rank]

        # Karena setiap domino dalam satu set bersifat unik,
        # Step 4 seharusnya selalu menghasilkan tepat satu
        # kandidat. Jika tidak, ada bug di tempat lain (mis.
        # data domino rusak/duplikat) — engine harus berhenti
        # secara eksplisit, bukan diam-diam memilih candidates[0].
        if len(candidates) == 1:
            return candidates[0]

        raise RuntimeError(
            "Unexpected tie after Step 4: multiple players hold "
            "an identically-ranked highest domino."
        )

    # =========================================================
    # GUPLAH WINNER
    #
    # Berbeda dari DOM/PASAR, GUPLAH mencari WINNER (bukan
    # penerima denda) di antara SELURUH pemain (tidak ada pemain
    # yang dikecualikan seperti "winner" pada DOM), karena tidak
    # ada satu pun pemain yang menghabiskan kartunya.
    #
    # Urutannya mencerminkan MASTER_CORE.md, dengan dua
    # perbedaan penting dari DOM:
    #
    # 1. Setelah Step 1, ada pengecekan status "pembuat guplah":
    #    jika pembuat guplah termasuk salah satu kandidat yang
    #    tied di pip terkecil, dia menang langsung tanpa masuk
    #    ke step manapun berikutnya.
    # 2. Step 2, 3.0, 3a, 3b, dan 4 seluruhnya memakai arah
    #    KEBALIKAN dari DOM: mencari beban PALING RINGAN
    #    (jumlah kartu tersedikit, tidak punya balak, jumlah
    #    balak tersedikit, nilai balak terendah, domino
    #    tertinggi yang paling rendah), karena di sini kita
    #    mencari pemenang, bukan penerima hukuman.
    # =========================================================
    @staticmethod
    def find_guplah_winner(player_points, guplah_maker):

        candidates = list(player_points.keys())

        if len(candidates) == 1:
            return candidates[0]

        # ---------------------------------
        # STEP 1: TOTAL PIP TERKECIL
        # ---------------------------------
        min_points = min(player_points[p] for p in candidates)
        candidates = [p for p in candidates if player_points[p] == min_points]

        if len(candidates) == 1:
            return candidates[0]

        # ---------------------------------
        # OVERRIDE: STATUS PEMBUAT GUPLAH
        # Jika pembuat guplah termasuk salah satu kandidat yang
        # tied di pip terkecil, dia menang langsung.
        # ---------------------------------
        if guplah_maker in candidates:
            return guplah_maker

        # ---------------------------------
        # STEP 2: JUMLAH KARTU TERSEDIKIT
        # ---------------------------------
        min_cards = min(len(p.hand) for p in candidates)
        candidates = [p for p in candidates if len(p.hand) == min_cards]

        if len(candidates) == 1:
            return candidates[0]

        # ---------------------------------
        # STEP 3.0: KETIADAAN BALAK LEBIH DIUTAMAKAN
        # ---------------------------------
        clean_players = [
            p for p in candidates if not RuleSystem._balak_dominoes(p)
        ]

        if len(clean_players) == 1:
            return clean_players[0]

        if len(clean_players) >= 2:
            # Baik ketika sebagian kandidat "bersih" (tidak
            # pegang balak) dan sisanya pegang balak (pemegang
            # balak dieliminasi di sini), maupun ketika TIDAK
            # ADA satu pun kandidat yang pegang balak (clean_players
            # == candidates), kedua kasus ini sama-sama berujung
            # langsung ke Step 4 tanpa melalui Step 3a/3b.
            return RuleSystem._guplah_step4(clean_players)

        # Tidak ada satu pun kandidat yang "bersih": semua
        # kandidat memegang setidaknya satu balak.

        # ---------------------------------
        # STEP 3a: JUMLAH BALAK TERSEDIKIT
        # ---------------------------------
        min_balak_count = min(
            len(RuleSystem._balak_dominoes(p)) for p in candidates
        )
        candidates = [
            p for p in candidates
            if len(RuleSystem._balak_dominoes(p)) == min_balak_count
        ]

        if len(candidates) == 1:
            return candidates[0]

        # ---------------------------------
        # STEP 3b: NILAI BALAK TERTINGGI YANG PALING RENDAH
        # ---------------------------------
        min_balak_value = min(
            RuleSystem._highest_balak_value(p) for p in candidates
        )
        candidates = [
            p for p in candidates
            if RuleSystem._highest_balak_value(p) == min_balak_value
        ]

        if len(candidates) == 1:
            return candidates[0]

        raise RuntimeError(
            "Unexpected tie after GUPLAH Step 3b: multiple players "
            "have identical lowest highest-balak value."
        )

    # =========================================================
    # GUPLAH STEP 4 (INTERNAL)
    # Sama seperti Step 4 DOM (memakai highest_domino/domino_rank
    # milik masing-masing pemain), tetapi yang menang adalah
    # domino tertinggi yang NILAINYA PALING RENDAH di antara
    # para kandidat.
    # =========================================================
    @staticmethod
    def _guplah_step4(candidates):
        def highest_rank(player):
            return RuleSystem.domino_rank(
                RuleSystem.highest_domino(player)
            )

        best_rank = min(highest_rank(p) for p in candidates)
        winners = [p for p in candidates if highest_rank(p) == best_rank]

        if len(winners) == 1:
            return winners[0]

        raise RuntimeError(
            "Unexpected tie after GUPLAH Step 4: multiple players "
            "hold an identically-ranked highest domino."
        )

    # =========================================================
    # DOM SCORE
    # =========================================================
    @staticmethod
    def calculate_dom_score(player_points, winner):
        scores = {p: 0 for p in player_points}

        if winner is None:
            return scores

        loser = RuleSystem.find_dom_loser(player_points, winner)

        scores[winner] = -3
        scores[loser] = 3

        return scores

    # =========================================================
    # PASAR SCORE
    # PASAR adalah bentuk khusus DOM: winner dan tie-break
    # penerima denda memakai aturan DOM yang sama persis (lihat
    # find_dom_loser). Yang membedakan hanya besar penaltinya:
    # DOM = -3/+3, PASAR = -4/+4.
    # =========================================================
    @staticmethod
    def calculate_pasar_score(player_points, winner):
        scores = {p: 0 for p in player_points}

        if winner is None:
            return scores

        loser = RuleSystem.find_dom_loser(player_points, winner)

        scores[winner] = -4
        scores[loser] = 4

        return scores

    # =========================================================
    # GUPLAH SCORE
    #
    # Winner selalu -5.
    #
    # Ada dua mode distribusi penalti, tergantung apakah
    # pembuat guplah adalah winner atau bukan:
    #
    # - Jika pembuat guplah == winner: SEMUA pemain lain
    #   (bukan winner) mendapat +5 masing-masing.
    # - Jika pembuat guplah != winner: HANYA pembuat guplah
    #   yang mendapat +5. Pemain lain yang bukan winner dan
    #   bukan pembuat guplah tidak dihukum sama sekali (0).
    # =========================================================
    @staticmethod
    def calculate_guplah_score(player_points, winner, guplah_maker):
        scores = {p: 0 for p in player_points}

        if winner is None:
            return scores

        scores[winner] = -5

        if guplah_maker == winner:
            for p in player_points:
                if p != winner:
                    scores[p] = 5
        else:
            scores[guplah_maker] = 5

        return scores