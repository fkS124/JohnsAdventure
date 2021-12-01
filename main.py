'''
    Welcome to John's Adventure! Hope you like my new game!

    Please be patient with some pieces of the code, it will take some time to clean the code ;')

'''


import pygame as pg
import sys
import threading

from data.scripts.world import main, GameManager
from data.scripts.utils import resource_path


def load_game():
    global game_instance
    if sys.argv[-1] != "main.py" and sys.argv[-1] != "--debug":
        game_instance = main(debug=("--debug" in sys.argv), first_state=sys.argv[-1])
    else:
        game_instance = main(debug=("--debug" in sys.argv))


if __name__ == '__main__':

    game_instance: GameManager = None
    load_thread = threading.Thread(target=load_game).start()

    pg.init()
    screen = GameManager.DISPLAY
    font = pg.font.Font(resource_path("data/database/pixelfont.ttf"), 30)
    while game_instance is None:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                raise SystemExit

        screen.fill((0, 0, 0))
        screen.blit(font.render("Loading you sussy baka...", True, (0, 255, 0)), (0, 0))

        # TODO : MAKE IT LOOK BETTER

        pg.display.update()
    game_instance.update()
