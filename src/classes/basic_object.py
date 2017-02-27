# -*- coding: utf8 -*-
"""Basic object module"""


class BasicObject(object):
    """
    Class that is basic for all objects on the form.
    Cannot be rendered!
    """

    def __init__(self, position, size, visible=True):
        """
        Initialize Basic_Object
        :param position: pacman.helper_types.Position
        :param size: pacman.helper_types.Size
        :param visible: boolean
        """
        self.position = position
        self.size = size
        self.visible = visible
