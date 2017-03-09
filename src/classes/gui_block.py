import pygame


class GuiPanel(object):
    def __init__(self, size, app, gui, background_c: pygame.Color=None):
        self.visible = True
        self.surface = pygame.Surface(size, flags=pygame.SRCALPHA)
        self.gui = app
        self.gui.init(gui, self.surface)
        if background_c:
            self.background_c = background_c
        else:
            self.background_c = pygame.Color('#e8c94bBB')

    def render(self, parent_surface):
        if self.visible:
            self.surface.fill(self.background_c)
            self.gui.paint(self.surface)
            parent_surface.blit(self.surface, (0, 0))
