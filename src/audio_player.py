import pygame
import time

class AudioPlayer:
    def __init__(self, filepath, offset=0.0, volume=1.0):
        self.filepath = filepath
        self.offset = offset
        self.volume = volume
        self.start_play_time = None
        self.pause_start_time = None
        self.total_paused_time = 0.0
        self.scheduled_start_time = None
        self.is_paused = False

        pygame.mixer.init()
        pygame.mixer.music.set_volume(self.volume)

    def play(self):
        """计划播放，不阻塞"""
        self.scheduled_start_time = time.time() + max(0, self.offset)
        self.start_play_time = None
        self.total_paused_time = 0.0
        self.is_paused = False

    def update(self):
        """每帧调用，检查是否该播放了"""
        if self.scheduled_start_time and time.time() >= self.scheduled_start_time:
            pygame.mixer.music.load(self.filepath)
            pygame.mixer.music.play()
            self.start_play_time = time.time() - max(0, -self.offset)
            self.scheduled_start_time = None

    def pause(self):
        """暂停播放"""
        if not self.is_paused and pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.pause_start_time = time.time()
            self.is_paused = True

    def resume(self):
        """继续播放"""
        if self.is_paused:
            pygame.mixer.music.unpause()
            if self.pause_start_time:
                self.total_paused_time += time.time() - self.pause_start_time
            self.pause_start_time = None
            self.is_paused = False

    def stop(self):
        """停止播放"""
        pygame.mixer.music.stop()
        self.start_play_time = None
        self.pause_start_time = None
        self.total_paused_time = 0.0
        self.is_paused = False
        self.scheduled_start_time = None

    def is_playing(self):
        """是否正在播放（不包括暂停状态）"""
        return pygame.mixer.music.get_busy() and not self.is_paused

    def get_song_time(self):
        """
        获取音乐当前播放时间（秒）
        如果暂停，则时间不增长
        """
        if self.start_play_time is None:
            return 0.0

        if self.is_paused and self.pause_start_time:
            return self.pause_start_time - self.start_play_time - self.total_paused_time

        return time.time() - self.start_play_time - self.total_paused_time
