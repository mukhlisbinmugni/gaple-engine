from game import Game


game = Game()

print("=== MEMULAI GAME ===")
game.start()

print()

print("=== KARTU MASING-MASING PEMAIN ===")

for player in game.players:
    print(player.name, ":", len(player.hand), "kartu")

print()

print("=== TEST GILIRAN ===")

for _ in range(6):
    print("Giliran:", game.active_player().name)
    game.next_turn()