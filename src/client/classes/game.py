# -*- coding: utf8 -*-
"""Game module"""
import pygame
from src.helper_types import Point
from .game_object import GameObject

D_TOP = 0
D_BOTTOM = 1
D_LEFT = 2
D_RIGHT = 3


class Game(object):
    def __init__(self, resources):
        self.res = resources
        self.position = Point(0, 0)
        self.visible = True
        self.score = 0
        self.over = False
        self.objects = []

        # creating level and adding walls to form and to pygame walls group
        # self.pacman = Pacman(Position(480, 660), self.res.animations.pacman)
        # self.pacman.visible = False
        # self.add_object(self.pacman)
        self.players = {}
        self.player1 = GameObject(Point(0, 0), self.res.textures.wall_type_default)
        self.player1.visible = False
        self.add_object(self.player1)
        self.player2 = GameObject(Point(0, 0), self.res.textures.player2)
        self.player2.visible = False
        self.add_object(self.player2)
        self.player3 = GameObject(Point(0, 0), self.res.textures.wall_type_default)
        self.player3.visible = False
        self.add_object(self.player3)
        self.player4 = GameObject(Point(0, 0), self.res.textures.wall_type_default)
        self.player4.visible = False
        self.add_object(self.player4)

    def new_game(self):
        pass

        self.over = False

    def add_object(self, form_object):
        """
        Add object to game
        :param form_object: BasicObject
        """
        self.objects.append(form_object)

    def render(self, screen):
        """Render all managed game objects on map"""
        self.update()
        # render if visible
        if self.visible:
            for obj in self.objects:
                obj.render(screen)

    @staticmethod
    def sprite_group_collide(sprite, group):
        """
        Check collision between sprite and group
        :param sprite: pygame.sprite.Sprite
        :param group: pygame.sprite.Group
        :return same as pygame.sprite.groupcollide()
        """
        temp = pygame.sprite.Group(sprite)
        return pygame.sprite.groupcollide(temp, group, False, False)

    def get_object(self, obj_position, direction):
        """
        (возвращает объект на соседнем (direction) блоке от position)
        :param position: helper_types.Position
        :param direction: int
        :return GameObject
        """
        #position = Position(obj_position.x, obj_position.y)

        #for obj in self.objects:
        #    if direction == 0:
        #        if (obj.position.x == position.x) and (obj.position.y == position.y - constants.BLOCK_HEIGHT):
        #            return obj
        #    elif direction == 1:
        #        if (obj.position.x == position.x) and (obj.position.y == position.y + constants.BLOCK_HEIGHT):
        #            return obj
        #    elif direction == 2:
        #        if (obj.position.x == position.x - constants.BLOCK_WIDTH) and (obj.position.y == position.y):
        #            return obj
        #    else:
        #        if (obj.position.x == position.x + constants.BLOCK_WIDTH) and (obj.position.y == position.y):
        #            return obj

    def moving(self, entity):
        pass

    def eating_seeds(self):
        pass

    def ghosts_ai(self):
        pass

    def update(self):
        """Game update function"""
        # entities' collisions with walls
        # pacman's collision with ghosts and the end of game

        pass
