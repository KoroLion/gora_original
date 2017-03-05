"""!
@file Игровая панель
@brief Панель с игровым полем
"""
import pygame
from classes.helper_types import Point
from classes.basic_object import BasicObject

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
            for player in self.players:
                self.players[player].render(screen)

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

    def moving(self, entity):
        pass

    def update(self):
        """Game update function"""
        # entities' collisions with walls
        # pacman's collision with ghosts and the end of game
        pass
