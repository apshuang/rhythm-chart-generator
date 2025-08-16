import pygame
import math
import copy

from ..settings import JUDGEMENT_Y, SCREEN_WIDTH, SPEED

NOTE_COLORS = {
    4: (255, 255, 255),   # 白色
    8: (0, 200, 255),     # 蓝色
    12: (255, 200, 0),    # 金色
    16: (0, 255, 0),      # 绿色
    24: (255, 0, 255),    # 紫色
    32: (255, 0, 0),      # 红色
}

NOTE_SHAPES = {
    4: "circle",
    8: "diamond",
    12: "triangle",
    16: "square",
    24: "pentagon",
    32: "hexagon",
}

class Note:
    def __init__(self, note_type, belong_measure, dotted = False):
        self.note_type = note_type
        self.belong_measure = belong_measure
        self.x = SCREEN_WIDTH
        self.y = JUDGEMENT_Y // 2  # 用判定圆的纵坐标
        self.color = NOTE_COLORS.get(note_type, (200, 200, 200))
        self.shape = NOTE_SHAPES.get(note_type, "circle")
        self.size = 20

    def update(self, dt):
        """按速度向左移动"""
        self.x -= SPEED * dt

    def draw(self, surface):
        """绘制不同形状的音符"""
        if self.shape == "circle":
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)
        elif self.shape == "diamond":
            points = [
                (self.x, self.y - self.size),
                (self.x + self.size, self.y),
                (self.x, self.y + self.size),
                (self.x - self.size, self.y)
            ]
            pygame.draw.polygon(surface, self.color, points)
        elif self.shape == "triangle":
            points = [
                (self.x, self.y - self.size),
                (self.x + self.size, self.y + self.size),
                (self.x - self.size, self.y + self.size)
            ]
            pygame.draw.polygon(surface, self.color, points)
        elif self.shape == "square":
            rect = pygame.Rect(self.x - self.size, self.y - self.size, self.size * 2, self.size * 2)
            pygame.draw.rect(surface, self.color, rect)
        elif self.shape == "pentagon":
            points = self._regular_polygon(5)
            pygame.draw.polygon(surface, self.color, points)
        elif self.shape == "hexagon":
            points = self._regular_polygon(6)
            pygame.draw.polygon(surface, self.color, points)

    def _regular_polygon(self, n):
        """生成正多边形顶点"""
        points = []
        for i in range(n):
            angle = math.pi * 2 * i / n - math.pi / 2
            px = self.x + math.cos(angle) * self.size
            py = self.y + math.sin(angle) * self.size
            points.append((px, py))
        return points



class NoteManager:
    def __init__(self, chart_path, chart_offset):
        """
        chart_path: 谱面路径
        chart_offset: 谱面偏移量
        """
        self.notes: list[Note] = []
        self.events: list[tuple[float, Note]] = []
        self.chart_offset = chart_offset
        self.parse_song(chart_path)
        
    def almost_equal(self, a: float, b: float, tol: float = 1e-6) -> bool:
        """
        判断两个浮点数是否近似相等
        :param a: 第一个数
        :param b: 第二个数
        :param tol: 容差（默认1e-6）
        """
        return abs(a - b) <= tol

    def parse_song(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        bpm = 120
        beats_per_bar = 4  # 每个小节有4拍
        beat_note_value = 4  # 四分音符为一拍
        current_time = 0.0  # 考虑到BPM和拍号都可能会变，所以用“时间”来记录note出现的时机，直接又准确
        last_note_time = 0.0  # 因为每个音符的时值是由它与后一个音符的距离来确定的，所以必须等到检索到后一个音符的时候，才能append这个音符
        current_measure = 0
        last_measure = 0
        
        prev_index = 0
        now_index = 0
        
        events: list[tuple[float, Note]] = []
        
        in_chart = False

        for line_number, line in enumerate(lines):
            line = line.strip()
            if line.startswith('#START'):
                in_chart = True
            
            if not in_chart:
                continue
            
            if line.startswith("#END"):
                # 将END视为最后一个音符，计算上一个音符的时值
                line = "1"
            if not line or line.startswith("#"):
                if line.startswith("#BPMCHANGE"):
                    # 处理BPM变化
                    bpm = float(line.split()[1])
                elif line.startswith("#MEASURE"):
                    # 处理拍号变化
                    ts = line.split()[1]
                    beats_per_bar, beat_note_value = map(int, ts.split('/'))
                continue
                
            # 每行小节数据
            chars = [c for c in line if c in "01"]
            if not chars:
                continue
            num_chars = len(chars)
            # 每拍时长
            beat_length = 60 / bpm
            measure_length = beat_length * beats_per_bar
            current_measure += 1
            
            in_line_index = 0
            for c in chars:
                if c == "1":
                    dotted = False
                    # 这个变量的意义是：这个音符占了多少个小节，对于一个4/4拍的小节，那么这个音符就占了一拍，也就是一个四分音符的时值
                    gap = max(now_index - prev_index, 1)  # 避免分母为0
                    gap_beat = gap * beats_per_bar / num_chars  # 这个变量的含义是这个音符占了多少拍
                    duration_ratio = beat_note_value / gap_beat  # 这个变量的含义是它是几分音符
                    
                    # 附点音符
                    for beat in NOTE_SHAPES.keys():
                        if duration_ratio * 1.5 == beat:
                            duration_ratio = beat
                            dotted = True
                    
                    # 对音符时值进行修正，如果比四分音符还长，应该确定为四分音符，如果比32分音符还短，就确定为32分音符
                    if duration_ratio <= 4:
                        duration_ratio = 4
                    elif duration_ratio >= 32:
                        duration_ratio = 32

                    if duration_ratio not in NOTE_COLORS.keys():
                        # 如果不是确定的那些时值，则报错并退出
                        # print(line_number)
                        # print(line)
                        events.pop(0)
                        self.events = events
                        self.print_all_notes()
                        raise Exception(f"Unknown beat: {duration_ratio}, current time: {current_time}, gap: {gap}")
                    
                    # 创建 Note
                    note = Note(note_type=duration_ratio, belong_measure=last_measure, dotted=dotted)
                    current_beat = in_line_index * beats_per_bar / num_chars  # 当前位置占了一个小节的多少拍
                    in_line_time = current_beat * beat_length
                    events.append((last_note_time, note))
                    print(note.note_type)
                    last_note_time = current_time + in_line_time
                    last_measure = current_measure
                    
                    prev_index = now_index
                now_index += 1
                in_line_index += 1

            # 小节时间累加
            current_time += measure_length
            
        # 后处理，为events加上对应的偏移量
        events = [(event[0] + self.chart_offset, event[1]) for event in events]
        events.pop(0)  # 去掉第一个没用的音符（因为每个音符的时值是与它后面的音符距离有关的，第一个音符相当于空音符，所以弹出）
        self.events = events

    def update(self, current_time, dt):
        while self.events and current_time >= self.events[0][0]:
            _, note = self.events.pop(0)
            self.notes.append(note)
        for note in self.notes:
            note.update(dt)
            
    def draw_notes(self, surface):
        for note in self.notes:
            note.draw(surface)

    def print_all_notes(self):
        events = copy.deepcopy(self.events)
        for current_measure in range(self.events[-1][1].belong_measure + 1):
            line = []
            while events and events[0][1].belong_measure == current_measure:
                _, note = events.pop(0)
                line.append(str(note.note_type))
            print(' '.join(line))
            