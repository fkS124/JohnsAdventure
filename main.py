from data.scripts.world import Game

def Engine(game=Game()):
    game.update()


if __name__ == '__main__':
    Engine()
