# -*- coding: utf8 -*-
"""Helper types for pacman game development"""


class Position(object):
    """Class for storing position data."""

    def __init__(self, x, y):
        """
        Initialize Position object
        :type x: int
        :type y: int
        """
        self.x = x  # pylint: disable=invalid-name
        self.y = y  # pylint: disable=invalid-name


class Size(object):
    """Class for storing size data."""

    def __init__(self, width, height):
        """
        Initialize Size object
        :type width: int
        :type height: int
        """
        self.width = width
        self.height = height

    def __eq__(self, other):
        return (self.width == other.width) and (self.height == other.height)


class Speed(object):
    """Class for storing speed data."""

    def __init__(self, x, y):
        """
        Initialize Speed object
        :type x: int
        :type y: int
        """
        self.x = x  # pylint: disable=invalid-name
        self.y = y  # pylint: disable=invalid-name

if __name__ == "__main__":
    pass
