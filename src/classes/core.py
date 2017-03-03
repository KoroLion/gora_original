"""Main game core module"""
import pygame
from classes.constants import *
from classes.helper_types import Point, Size


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
        # настроечки...
        self.limit_framerate = False
        self.max_framerate = 60
        self.full_screen = False

        self.icon = pygame.image.load("images/robots/textures/robot_blue.png")

        if self.full_screen:
            self.full_screen = pygame.FULLSCREEN

        self.display = pygame.display
        self.surface = self.display.set_mode((size.width, size.height), self.full_screen)  # = old self.screen
        self.display.set_caption(caption)
        self.display.set_icon(self.icon)

        self.terminated = False
        self.pause = False
        self.color = color
        self.fps = fps
        self.clock = pygame.time.Clock()
        self.size = size

        self.game_cycles = 0
        self.objects = []

        self.background = None
        self.set_background()

        self.update()

    def add_object(self, form_object):
        """
        Add object to core
        :param form_object: BasicObject
        """
        self.objects.append(form_object)

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
            obj.render(self.surface)

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

    def set_background(self, color: str=None):
        if color:
            self.color = color

        self.background = pygame.Surface((self.size.width, self.size.height))
        self.background.fill(self.color)

    def get_camera_view(self, point, bg):
        """!
        @brief Возвращает вид камеры на точку
        @param point точка, за которой следит камера (Point)
        @param bg поверхность, на которой лежит точка (Surface)
        @return Surface
        """
        size = bg.get_size()
        cam = pygame.Surface(size)
        cam.blit(bg, (-point.x + int(size[0] / 2), -point.y + int(size[1] / 2)))
        return cam

    def update(self, camera_mode=False, point=None):
        """Game update function"""

        # очищаем экран (ставим поверх всего прямоуг.)
        self.surface.blit(self.background, (0, 0))
        # рендерим объекты
        self.render_objects()

        if camera_mode:
            camera_surface = self.get_camera_view(point, self.surface)
            self.surface.blit(camera_surface, (0, 0))

        self.game_cycles += 1

        # обновляем экран и ждём =)
        self.display.flip()

        if self.limit_framerate:
            self.clock.tick(self.max_framerate)

    def terminate(self):
        """Gracefully exit from game"""
        self.terminated = True
