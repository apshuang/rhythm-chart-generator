import pygame
from ..settings import JUDGEMENT_X, JUDGEMENT_Y, JUDGEMENT_RADIUS, COLOR_JUDGEMENT


class JudgementCircle:
    def __init__(self, x=JUDGEMENT_X, y=JUDGEMENT_Y, radius=JUDGEMENT_RADIUS, color=COLOR_JUDGEMENT):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.radius, 3)

