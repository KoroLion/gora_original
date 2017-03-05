# -*- coding: utf8 -*-
"""Game resources module"""
from pygame import mixer, Color

from classes.texture import Texture


class Sounds(object):
    """"Class that stores and works with all sounds"""
    def __init__(self, volume):
        """
        Initialize sounds class
        :param volume: float
        """
        self.volume = volume

        # self.pacman_death = mixer.Sound("sounds/pacman_death.wav")

    def __getattr__(self, attr):
        return self.__dict__[attr]

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def update(self):
        """Update sounds (change volume if changed)"""
        for sound in self.__dict__:
            sound = self.__dict__[sound]
            if isinstance(sound, mixer.Sound):
                sound.set_volume(self.volume)


class Animations(object):
    """Class that stores and works with all animations"""

    def __init__(self):
        """Load all animations"""
        # self.numbers = Texture("images/wall/numbers", 2)

    def __getattr__(self, attr):
        return self.__dict__[attr]

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def update(self):
        """
        Change to the next frame all animations
        """
        for animation in self.__dict__:
            self.__dict__[animation].next_frame()


class Textures(object):
    """Class that stores textures"""

    def __init__(self):
        self.robot_blue = Texture("images/robots/textures/robot_blue.png")
        self.robot_green = Texture("images/robots/textures/robot_green.png")

        self.seed = Texture("images/seed.png")

        self.none_texture = Texture("images/no_texture.png")

        self.panel = Texture("images/background.png")
        self.button_play = Texture("images/start_button.png")
        self.button_play_hover = Texture("images/start_button_hover.png")

    def __getattr__(self, attr):
        return self.__dict__[attr]

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def update(self):
        """
        Change the size and the angle of textures
        """
        for texture in self.__dict__:
            self.__dict__[texture].update()


class Resources(object):
    """Class that stores all game resources: textures, animated textures, sounds, etc. ."""

    def __init__(self, sounds_volume):
        """
        Initialize Resource object
        Loads all game resources
        """

        # adding animations, textures and sounds
        self.sounds = Sounds(sounds_volume)
        self.animations = Animations()
        self.textures = Textures()

        self.score_label = Color("#FFFFFF")
        self.background = Color("#F2F2F2")

        self.aim = (  # sized 24x24
            "                        ",
            "           ooo          ",
            "           ooo          ",
            "           ooo          ",
            "           ooo          ",
            "           ooo          ",
            "           ooo          ",
            "           ooo          ",
            "           ooo          ",
            "                        ",
            "                        ",
            " oooooooo  ooo  oooooooo",
            " oooooooo  ooo  oooooooo",
            " oooooooo  ooo  oooooooo",
            "                        ",
            "                        ",
            "           ooo          ",
            "           ooo          ",
            "           ooo          ",
            "           ooo          ",
            "           ooo          ",
            "           ooo          ",
            "           ooo          ",
            "           ooo          ")

    def update(self):
        """Update animations and sounds"""
        self.animations.update()
        self.textures.update()
        self.sounds.update()
