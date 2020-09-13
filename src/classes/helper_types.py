"""!
@file Вспомогательные классы
@brief Точка (универсальная для скорости и позиции) и Размер
"""


class Point(object):
    """!
    @brief хранение данных с x и y
    """

    def __init__(self, x: int, y: int):
        """!
        @brief Создание объекта для хранения данных формата (x; y)
        @param x позиция по горизонтали (int)
        @param y позиция по вертикали (int)
        """
        self.x = x  # pylint: disable=invalid-name
        self.y = y  # pylint: disable=invalid-name

    def __eq__(self, other):
        """!
        @brief Сравнение 2 объектов через ==
        """
        return (self.x == other.x) and (self.x == other.x)


class Size(object):
    """!
    @brief хранение данных с width и height
    """

    def __init__(self, width: int, height: int):
        """!
        @brief Создание объекта для хранения размера
        @param width ширина (int)
        @param height высота (int)
        """
        self.width = width
        self.height = height

    def __eq__(self, other):
        """!
        @brief Сравнение 2 объектов через ==
        """
        return (self.width == other.width) and (self.height == other.height)
