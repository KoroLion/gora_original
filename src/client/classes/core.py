# -*- coding: utf8 -*-
"""Main game core module"""
import pygame
from .constants import *
from src.helper_types import Point


class Core(object):
    """Class that represents game core. Contains and serve game objects and manage game loop."""
    def __init__(self, caption, size, color, fps):
        """
        Initialize game core object
        :param caption: string
        :param size: pacman.helper_types.Size
        :param background: pygame.Color
        :param game_speed: int
        """

        self.terminated = False
        self.pause = False
        self.color = color
        self.caption = caption
        self.fps = fps
        self.clock = pygame.time.Clock()
        self.size = size

        self.game_cycles = 0
        self.objects = []

        self.screen = pygame.display.set_mode((size.width, size.height))
        self.background = pygame.Surface((size.width, size.height))

        self.update()

    def add_object(self, form_object):
        """
        Add object to core
        :param form_object: BasicObject
        """
        self.objects.append(form_object)

    @staticmethod
    def get_block_position(position):
        """
        Rounds the position
        :param position: helper_types.Position
        :return: helper_types.Position
        """
        position.x -= position.x % BLOCK_WIDTH
        position.y -= position.y % BLOCK_WIDTH
        return position

    def get_object(self, obj_position, direction):
        """
        (возвращает объект на соседнем (direction) блоке от position)
        :param position: helper_types.Position
        :param direction: int
        :return GameObject
        """
        position = Point(obj_position.x, obj_position.y)

        for obj in self.objects:
            if direction == 0:
                if (obj.position.x == position.x) and (obj.position.y == position.y - BLOCK_HEIGHT):
                    return obj
            elif direction == 1:
                if (obj.position.x == position.x) and (obj.position.y == position.y + BLOCK_HEIGHT):
                    return obj
            elif direction == 2:
                if (obj.position.x == position.x - BLOCK_WIDTH) and (obj.position.y == position.y):
                    return obj
            else:
                if (obj.position.x == position.x + BLOCK_WIDTH) and (obj.position.y == position.y):
                    return obj

    def render_objects(self):
        """Render all managed game objects on map"""
        for obj in self.objects:
            obj.render(self.screen)

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

    def update(self):
        """Game update function"""
        pygame.display.set_caption(self.caption)
        self.screen = pygame.display.set_mode((self.size.width, self.size.height))
        self.background.fill(self.color)
        self.screen.blit(self.background, (0, 0))
        self.render_objects()
        self.game_cycles += 1

        pygame.display.flip()
        self.clock.tick(self.fps)

    def terminate(self):
        """Gracefully exit from game"""
        self.terminated = True
