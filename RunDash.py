import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout,
    QWidget, QListWidget, QHBoxLayout, QPushButton
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPalette, QColor, QFont

class TimecodeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RunDash")
        self.setGeometry(0, 0, 800, 400)

        # VLC settings
        self.vlc_url = "http://localhost:8080/requests/status.json"
        self.vlc_password = "vlc"  # Match your VLC Lua HTTP password
        self.auth = requests.auth.HTTPBasicAuth("", self.vlc_password)


        # Set black background
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("black"))
        self.setPalette(palette)

        # Central layout
        main_layout = QVBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Top custom status bar
        self.status_label = QLabel("STANDBY")
        self.status_label.setFixedHeight(45)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            color: white;
            font-weight: bold;
            font-size: 24px;
            padding: 6px;
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 #444, stop:1 #222
            );
        """)
        main_layout.addWidget(self.status_label)

        # Horizontal layout for timecode and cues
        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)

        # Timecode Display (from VLC)
        self.time_label = QLabel("00:00:00.00")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("""
            font-size: 90px;
            color: #00FF00;
            background-color: black;
""")
        self.time_label.setFont(QFont("Arial", 90))

        # Clock Display (below timecode)
        self.clock_label = QLabel("Loading clock...")
        self.clock_label.setAlignment(Qt.AlignCenter)
        self.clock_label.setStyleSheet("""
            font-size: 70px;
            color: #FFFFFF;
            background-color: black;
""")
        self.clock_label.setFont(QFont("Arial", 70))

        # Vertical layout for both
        time_layout = QVBoxLayout()
        time_layout.addWidget(self.time_label)
        time_layout.addWidget(self.clock_label)
        content_layout.addLayout(time_layout, 3)

        # Cue List
        self.cue_list = QListWidget()
        self.cues = ["Ready", "Sync", "Intro", "MAIN", "LIVE CUT", "LIVE", "LIVE OUTRO", "MUSIC OUTRO", "Outro", "Loop", "De-Sync", "ALL STOP"]
        self.current_cue_index = 0
        for cue in self.cues:
            self.cue_list.addItem(cue)

        self.cue_list.setStyleSheet("""
            QListWidget {
                background-color: #111;
                color: white;
                font-size: 18px;
            }
            QListWidget::item:selected {
                background-color: #0000ff;
            }
        """)
        self.update_cue_highlight()
        content_layout.addWidget(self.cue_list, 1)

        # Bottom Buttons
        button_layout = QHBoxLayout()
        main_layout.addLayout(button_layout)

        # Status buttons
        for status, color1, color2 in [
            ("STANDBY", "#616161", "#000000"),
            ("LIVE", "#00aa00", "#000000"),
            ("STOPPED", "#ff0000", "#000000"),
            ("PAUSED", "#d0ff00", "#000000")
        ]:
            btn = QPushButton(status)
            btn.clicked.connect(lambda checked, s=status, c1=color1, c2=color2: self.set_status(s, c1, c2))
            button_layout.addWidget(btn)

        # Cue control buttons
        prev_btn = QPushButton("Previous Cue")
        prev_btn.clicked.connect(self.prev_cue)
        button_layout.addWidget(prev_btn)

        next_btn = QPushButton("Next Cue")
        next_btn.clicked.connect(self.next_cue)
        button_layout.addWidget(next_btn)

        # Timer to update VLC timecode
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timecode)
        self.timer.start(500)


        # Clock update timer
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)

    def update_timecode(self):
        try:
            response = requests.get(self.vlc_url, auth=self.auth, timeout=0.5)
            if response.status_code == 200:
                data = response.json()
                vlc_time = float(data.get("time", 0))  # Changed to float just in case
                self.time_label.setText(self.seconds_to_timecode(vlc_time))
                self.vlc_connected = True
            else:
                self.vlc_connected = False
        except:
            self.vlc_connected = False



    def seconds_to_timecode(self, seconds):
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        ms = int((seconds - int(seconds)) * 1000)  # get milliseconds
        return f"{hrs:02}:{mins:02}:{secs:02}.{ms:03}"

    def update_clock(self):
        from datetime import datetime
        now = datetime.now().strftime("%I:%M:%S %p")
        self.clock_label.setText(now)


    def set_status(self, message, color1, color2):
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"""
            color: white;
            font-weight: bold;
            font-size: 24px;
            padding: 6px;
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 {color1}, stop:1 {color2}
            );
        """)

    def update_cue_highlight(self):
        self.cue_list.setCurrentRow(self.current_cue_index)

    def next_cue(self):
        if self.current_cue_index < len(self.cues) - 1:
            self.current_cue_index += 1
            self.update_cue_highlight()
            self.set_status(f"CUE: {self.cues[self.current_cue_index]}", "#0000ff", "#000000")

    def prev_cue(self):
        if self.current_cue_index > 0:
            self.current_cue_index -= 1
            self.update_cue_highlight()
            self.set_status(f"CUE: {self.cues[self.current_cue_index]}", "#0000ff", "#000000")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TimecodeApp()
    window.show()
    sys.exit(app.exec_())
