'''
    Welcome to John's Adventure! Hope you like my new game!

    Please be patient with some pieces of the code, it will take some time to clean the code ;')

'''


import pygame as pg
import threading

from data.scripts.world import main, GameManager
from data.scripts.utils import resource_path


def load_game():
    global game_instance
    game_instance = main(debug=debug, first_state=first_state, no_rect=no_rect)


if __name__ == '__main__':

    game_instance: GameManager = None
    load_thread = threading.Thread(target=load_game).start()

    pg.init() # Initialize pygame
    screen = GameManager.DISPLAY
    while game_instance is None:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                raise SystemExit

        screen.fill((0, 0, 0))

        # TODO : MAKE IT LOOK BETTER

        pg.display.update()
    game_instance.update()
