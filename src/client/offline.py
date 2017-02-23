"""!
@file
@brief Оффлайн клиент, созданный для тестов.
"""
# -*- coding: utf-8 -*-
import pygame
import math

from classes.constants import FORM_WIDTH, FORM_HEIGHT, FPS
from classes.resources import Resources
from classes.core import Core
from classes.game import Game
from classes.game_object import GameObject

from src.helper_types import Size, Point

pygame.init()

res = Resources(sounds_volume=0.5)

main_form = Core("GORA pre-alpha 0.1", Size(FORM_WIDTH, FORM_HEIGHT), res.background, FPS * 1)
game = Game(res)
main_form.add_object(game)


def main():
    """!
    @brief Поток отображения offline клиента
    """
    player = GameObject(Point(0, 0), res.textures.wall_type_default)
    player.visible = True
    game.add_object(player)
    ## @brief Переменная, хранящая координаты мыши
    mouse_pos = (0, 0)  # type: list

    while not main_form.terminated:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                main_form.terminate()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    go_top(player)
                if event.key == pygame.K_s:
                    go_bottom(player)
                if event.key == pygame.K_d:
                    go_right(player)
                if event.key == pygame.K_a:
                    go_left(player)
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos

        player.texture.angle = get_angle(player.position, mouse_pos, player.size)

        res.update()
        game.update()
        main_form.update()


def get_angle(pl_pos: Point, pos: list, size: Size) -> float:
    """!
    @brief Возращает угол между мышью и объектом

    @param size: Size(helper_types)
    @param pl_pos: list(координаты игрока)
    @param pos: list(координаты мыши)
    @return: float(градус поворота)
    """
    x = pos[0] + size.width - pl_pos.x
    y = pl_pos.y - pos[1] + size.height
    if x != 0:
        angle = math.atan(y / x) * 180 / 3.14
        if x > 0:
            angle += 270
            return angle
        else:
            angle += 90
            return angle
    else:
        angle = 0
        return angle


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
