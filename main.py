# main.py
import pygame
import sys
import time
from src.settings import *
from src.chart_analysis import *
from src.elements import *
from src.audio_player import *


chart_path = r"E:\rhythm-chart-generator\rythm\011662_03.tja"
audio_path = r"E:\rhythm-chart-generator\rythm\1662.mp3"
chart_offset = 0.9  # @TODO: 后续需要加一个自动或手动的确认偏移量的按钮，否则很难对准
audio_offset = 0

# 初始化
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("音游节奏解析器")
clock = pygame.time.Clock()

# 判定圆
judgement = JudgementCircle()

# 小节线
line_manager = LineManager()

# 歌曲元信息（假设拍号每小节不同）
song = SongMeta(chart_path, chart_offset)
events = song.get_events()

# 音乐播放器
audio_player = AudioPlayer(audio_path, audio_offset)
audio_player.play()

# 音符管理器
note_manager = NoteManager(chart_path, chart_offset)

running = True
start_time = time.time()

while running:
    dt = clock.tick(FPS) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    now = time.time() - start_time
    while events and now >= events[0][0]:
        _, event_type = events.pop(0)
        line_manager.add_line(SCREEN_WIDTH, event_type)

    line_manager.update(dt)
    audio_player.update()
    note_manager.update(now, dt)

    screen.fill(COLOR_BG)
    judgement.draw(screen)
    line_manager.draw_lines(screen)
    note_manager.draw_notes(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()
