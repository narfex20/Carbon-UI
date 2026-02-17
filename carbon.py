# Carbon UI v0.1
import os
import sys
import subprocess
import yt_dlp
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import *
from PySide6.QtCore import *


class DownloadThread(QThread):
    output_signal = Signal(str)
    error_signal = Signal(str)

    def __init__(self, command):
        super().__init__()
        self.command = command

    def run(self):
        process = subprocess.Popen(
            self.command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            shell=True
        )
        
        for line in process.stdout:
            self.output_signal.emit(line.strip())
            
        process.wait()

class YTDLPGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(450, 350)
        self.resize(self.minimumSize())


        self.main_layout = QVBoxLayout(self)

        # ---- FORM LAYOUT (Link + File name) ----
        form_layout = QFormLayout()

        self.link_input = QLineEdit()
        self.link_input.setPlaceholderText("Paste video link here")

        self.path_input = QLineEdit("Downloads")

        # Set Current folder as default path
        if getattr(sys, 'frozen', False):
            program_folder = os.path.dirname(sys.executable)
        else:
            program_folder = os.path.dirname(os.path.abspath(__file__))
        
        self.path_input.setText(program_folder)

        self.filename_input = QLineEdit()

        form_layout.addRow("Link :", self.link_input)
        form_layout.addRow("File name :", self.filename_input)

        self.main_layout.addLayout(form_layout)

        # ---- FORMAT SELECTOR ----
        self.format_combo = QComboBox()
        self.format_combo.addItems(["Auto", "mp4", "mp3"])

        self.format_combo.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.format_combo.setFixedWidth(52)  # you can tweak this number

        form_layout.addRow("Format :", self.format_combo)

        # ---- COMMAND PREVIEW ----
        self.main_layout.addWidget(QLabel("yt-dlp Command :"))
        self.command_preview = QTextEdit()
        self.main_layout.addWidget(self.command_preview)

        # ---- OUTPUT + ERROR TABS ----
        self.tabs = QTabWidget()

        self.output_console = QTextEdit()
        self.output_console.setReadOnly(True)

        self.error_console = QTextEdit()
        self.error_console.setReadOnly(True)

        self.tabs.addTab(self.output_console, "Output")
        self.tabs.addTab(self.error_console, "Errors")

        self.main_layout.addWidget(self.tabs)

        # ---- DOWNLOAD BUTTON ----
        self.download_button = QPushButton("Download")
        self.main_layout.addWidget(self.download_button)
        self.download_button.setFixedWidth(70)

        # ---- DEFAULT FORMAT ----
        self.selected_format = "Auto"

        # ---- SIGNAL CONNECTIONS ----
        self.link_input.textChanged.connect(self.update_command)
        self.filename_input.textChanged.connect(self.update_command)
        self.format_combo.currentTextChanged.connect(self.change_format)
        self.download_button.clicked.connect(self.start_download)

        self.update_command()

    def change_format(self, text):
        self.selected_format = text
        self.update_command()

    def update_command(self):
        link = " " + self.link_input.text()
        filename = self.filename_input.text()
        formatt = ""

        # if the filename input isn't black: use the -o command with the name in the input box, if not: keep it blank
        if self.filename_input.text() != "":
            filename = f" -o {self.filename_input.text()}"
        else:
            filename = ""

        # if auto format is selected: don't insert format command
        if self.selected_format == "Auto":
            formatt = ""
        # if mp4 format is selected: insert mp4 command
        elif self.selected_format == "mp4":
            # downloads the best video and audio available and merges then into the selected format
            formatt = """ -f "bestvideo+bestaudio" --merge-output-format """ + self.selected_format
        # if mp4 format is selected: insert mp3 command
        elif self.selected_format == "mp3":
            # -x extracts the audio of the video in its original format and --audio-format converts it to another audio format
            formatt = " -x --audio-format " + self.selected_format

        # anatomy of the yt-dlp input command
        command = f"yt-dlp{link}{filename}{formatt}"

        self.command_preview.setPlainText(command)

    def start_download(self):
        command = self.command_preview.toPlainText()

        self.output_console.clear()
        self.error_console.clear()

        self.thread = DownloadThread(command)
        self.thread.output_signal.connect(self.output_console.append)
        self.thread.error_signal.connect(self.error_console.append)
        self.thread.start()

if __name__ == "__main__":
    app = QApplication([])
    app.setWindowIcon(QIcon("icon.ico"))
    window = YTDLPGUI()
    window.setWindowTitle("Carbon UI")
    window.show()
    sys.exit(app.exec())