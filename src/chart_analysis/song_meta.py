import time

class SongMeta:
    def __init__(self, chart_path, chart_offset):
        """
        bar_info: 列表 [(bpm, beats_per_bar, beat_note_value), ...]
                  每个元素表示一个小节的 BPM 和拍号
        """
        self.start_time = time.time()
        self.bar_info = []
        self.parse_chart_file(chart_path)
        self.chart_offset = chart_offset
        
    def get_events(self):
        """
        根据每小节的BPM和拍号生成事件
        """
        events = []
        current_time = 0.0

        for bpm, beats_per_bar, beat_note_value in self.bar_info:
            beat_interval = 60 / bpm  # 以四分音符为基准的秒数
            beat_length_seconds = beat_interval  # 这里不假设4分音符为1拍，也就是说尽管是8分音符为一拍，也照样是这个BPM（而没有BPM翻倍）

            # 小节开始
            events.append((current_time, 'measure'))

            for beat_index in range(beats_per_bar):
                quarter_time = current_time + beat_index * beat_length_seconds
                events.append((quarter_time, 'quarter'))

                # 每拍拆分为4个16分音符
                sixteenth_interval = beat_length_seconds / 4
                for i in range(1, 16 // beat_note_value):
                    # 这里不需要默认4分音符为一拍
                    events.append((quarter_time + i * sixteenth_interval, 'sixteenth'))

            current_time += beats_per_bar * beat_length_seconds

        # 后处理，为events加上对应的偏移量
        events = [(event[0] + self.chart_offset, event[1]) for event in events]
        return events

    
    def parse_chart_file(self, path):
        bar_info = []
        current_bpm = None
        current_measure = (4, 4)  # 默认 4/4
        in_chart = False

        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()

                if not line or line.startswith("//"):  # 跳过空行和注释
                    continue

                if line.upper() == "#START":
                    in_chart = True
                    continue
                if line.upper() == "#END":
                    break

                if not in_chart:
                    continue

                # 解析 BPM 变化
                if line.upper().startswith("#BPMCHANGE"):
                    parts = line.split()
                    if len(parts) == 2:
                        current_bpm = float(parts[1])
                    continue

                # 解析 拍号变化
                if line.upper().startswith("#MEASURE"):
                    parts = line.split()
                    if len(parts) == 2:
                        num, den = parts[1].split("/")
                        current_measure = (int(num), int(den))
                    continue

                # 如果是小节数据行
                if line and (line[0].isdigit() or line[0] in " ,"):
                    if current_bpm is None:
                        raise ValueError("BPM 未定义，请在谱面开始处设置 #BPMCHANGE")

                    beats_per_bar, beat_note_value = current_measure
                    bar_info.append((current_bpm, beats_per_bar, beat_note_value))

        self.bar_info = bar_info