# -*- coding: utf8 -*-
"""Helper types for pacman game development"""


class Point(object):
    """!
    @brief хранение данных с x и y
    """

    def __init__(self, x: int, y: int):
        """!
        :type x: int
        :type y: int
        """
        self.x = x  # pylint: disable=invalid-name
        self.y = y  # pylint: disable=invalid-name

    def __eq__(self, other):
        return (self.x == other.x) and (self.x == other.x)


class Size(object):
    """!
    @brief хранение данных с шириной и выстой
    """

    def __init__(self, width, height):
        """!
        :type width: int
        :type height: int
        """
        self.width = width
        self.height = height

    def __eq__(self, other):
        return (self.width == other.width) and (self.height == other.height)
