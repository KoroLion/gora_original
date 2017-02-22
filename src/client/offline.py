"""!
@file
@brief Оффлайн клиент, созданный для тестов.
"""
# -*- coding: utf-8 -*-
import pygame
import math

from classes.constants import FORM_WIDTH, FORM_HEIGHT, FPS
from classes.helper_types import Size
from classes.resources import Resources
from classes.core import Core
from classes.game import Game

pygame.init()

res = Resources(sounds_volume=0.5)

main_form = Core("GORA pre-alpha 0.1", Size(FORM_WIDTH, FORM_HEIGHT), res.background, FPS * 1)
game = Game(res)
main_form.add_object(game)


def main():
    """!
    @brief Поток отображения offline клиента
    """
    game.player1.visible = True
    """!
    @brief Переменная, хранящая координаты мыши
    """
    mouse_pos = (0, 0)

    while not main_form.terminated:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                main_form.terminate()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    go_top(game.player1)
                if event.key == pygame.K_s:
                    go_bottom(game.player1)
                if event.key == pygame.K_d:
                    go_right(game.player1)
                if event.key == pygame.K_a:
                    go_left(game.player1)
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos

        look_at_mouse(game.player1, mouse_pos)

        res.update()
        game.update()
        main_form.update()


def look_at_mouse(player, pos):
    """!
    @brief Поворачивает обьект в сторону мыши
    @param player: game_object
    @param pos: list(координаты мыши)
    """
    x = pos[0] + 10 - player.position.x
    y = player.position.y - pos[1] + 10
    if x != 0:
        angle = math.atan(y/x)*180/3.14
        if x > 0:
            game.player1.texture.angle = angle + 270
        else:
            game.player1.texture.angle = angle + 90


def go_right(player):
    """!
    @brief Движение игрока вправо
    @param player: game_object
    """
    player.speed.x = 2
    player.speed.y = 0


def go_left(player):
    """!
    @brief Движение игрока влево
    @param player: game_object
    """
    player.speed.x = -2
    player.speed.y = 0


def go_bottom(player):
    """!
    @brief Движение игрока вниз
    @param player: game_object
    """
    player.speed.y = 2
    player.speed.x = 0


def go_top(player):
    """!
    @brief Движение игрока вверх
    @param player: game_object
    """
    player.speed.y = -2
    player.speed.x = 0

if __name__ == "__main__":
    main()
