# lines.py
import pygame
from ..settings import COLOR_BEAT, COLOR_MEASURE, COLOR_SUBDIVISION, SCREEN_HEIGHT

class Line:
    """辅助线类，每个小节一条粗实线，每一拍（4分音符）一条虚线，每个16分音符一个点"""
    def __init__(self, origin_x, line_type):
        self.x = origin_x
        self.line_type = line_type

    def update(self, speed, dt):
        self.x -= speed * dt

    def draw(self, surface):
        if self.line_type == 'measure':
            pygame.draw.line(surface, COLOR_MEASURE, (self.x, 0), (self.x, SCREEN_HEIGHT), 3)
        elif self.line_type == 'quarter':
            # 虚线
            for y in range(0, SCREEN_HEIGHT, 10):
                pygame.draw.line(surface, COLOR_BEAT, (self.x, y), (self.x, y+5), 2)
        elif self.line_type == 'sixteenth':
            pygame.draw.circle(surface, COLOR_SUBDIVISION, (int(self.x), SCREEN_HEIGHT//2), 3)


class LineManager:
    def __init__(self, speed) -> None:
        self.speed = speed
        self.lines: list[Line] = []
        
    def update(self, dt):
        for line in self.lines:
            line.update(self.speed, dt)
            
    def add_line(self, origin_x, line_type):
        self.lines.append(Line(origin_x, line_type))
        
        self.lines = [l for l in self.lines if l.x > -10]
        
    def draw_lines(self, screen):
        for line in self.lines:
            line.draw(screen)