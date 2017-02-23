# -*- coding: utf8 -*-
"""Basic class for all GameObject"""
from pygame import sprite

from .basic_object import BasicObject
from src.helper_types import Point, Size


class GameObject(BasicObject, sprite.Sprite):
    """Class which is basic for all game objects in the level."""

    def __init__(self, position, animation, angle=0):
        """
        Initialize GameObject
        :param position: pacman.helper_types.Position
        :param size: pacman.helper_types.Size
        :param texture: pacman.resources.Animation
        """
        super(GameObject, self).__init__(position, Size(20, 20), True)
        sprite.Sprite.__init__(self)

        self.speed = Point(0, 0)
        self.angle = angle

        self.texture = animation
        self.texture.size = self.size
        self.image = animation.frame

        # for backward compatibility
        self.animation = self.texture

        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.position.x, self.position.y

    def update(self):
        """
        Update GameObject data
        """
        self.texture.size = self.size
        self.texture.angle = self.angle

        self.image = self.texture.frame
        self.rect = self.image.get_rect()

        self.rect.x, self.rect.y = self.position.x, self.position.y  # if position were changed from code
        self.rect = self.rect.move([self.speed.x, self.speed.y])
        self.position.x, self.position.y = self.rect.x, self.rect.y  # to accept moving

    def render(self, screen):
        """
        Render GameObject
        :param screen: pygame.display
        """
        self.update()
        # render if visible
        if self.visible:
            screen.blit(self.image, self.rect)
