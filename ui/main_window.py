from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QFileDialog, QFrame, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap
from core.tag_editor import TagEditor
from core.image_utils import image_to_bytes, bytes_to_qpixmap, resize_cover

# ---- Темы ----
THEMES = {
    "dark": {
        "background": "#1e1e1e",
        "text": "white",
        "input_bg": "#2b2b2b",
        "button_bg": "#4CAF50",
        "button_hover": "#45a049",
        "frame_bg": "#2b2b2b",
    },
    "light": {
        "background": "#f0f0f0",
        "text": "black",
        "input_bg": "white",
        "button_bg": "#2196F3",
        "button_hover": "#1976D2",
        "frame_bg": "#e0e0e0",
    }
}

class TagLoaderThread(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    def __init__(self, file_path): super().__init__(); self.file_path = file_path
    def run(self):
        try: self.finished.emit(TagEditor.load_tags(self.file_path))
        except Exception as e: self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎵 BeatTagger")
        self.setMinimumSize(800, 550)
        self.file_path = None
        self.cover_data = None
        self.loader_thread = None
        self.current_theme = "dark"

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout()
        central_widget.setLayout(self.main_layout)

        # Заголовок и переключатель темы
        header_layout = QHBoxLayout()
        title = QLabel("🎵 BeatTagger")
        title.setStyleSheet("font-size:22px;font-weight:bold;")
        header_layout.addWidget(title)
        self.btn_theme = QPushButton("Светлая тема")
        self.btn_theme.clicked.connect(self.toggle_theme)
        header_layout.addWidget(self.btn_theme)
        self.main_layout.addLayout(header_layout)

        # Кнопки выбора
        button_row = QHBoxLayout()
        self.btn_mp3 = QPushButton("Выбрать MP3"); self.btn_mp3.clicked.connect(self.choose_mp3)
        self.btn_folder = QPushButton("Выбрать папку"); self.btn_folder.clicked.connect(self.choose_folder)
        button_row.addWidget(self.btn_mp3); button_row.addWidget(self.btn_folder)
        self.main_layout.addLayout(button_row)

        # Поля для тегов
        fields_layout = QHBoxLayout()
        left_fields = QVBoxLayout()
        self.title_edit = QLineEdit(); self.artist_edit = QLineEdit()
        self.album_edit = QLineEdit(); self.genre_edit = QLineEdit()
        self.bpm_edit = QLineEdit(); self.mood_edit = QLineEdit()
        for placeholder, widget in [("Название", self.title_edit),("Артист", self.artist_edit),("Альбом", self.album_edit),("Жанр", self.genre_edit),("BPM", self.bpm_edit),("Настроение", self.mood_edit)]:
            widget.setPlaceholderText(placeholder); left_fields.addWidget(widget)
        self.comment_edit = QTextEdit(); self.comment_edit.setPlaceholderText("Комментарий...")
        left_fields.addWidget(self.comment_edit)
        fields_layout.addLayout(left_fields)

        # Обложка
        cover_layout = QVBoxLayout()
        self.cover_label = QLabel("Нет обложки"); self.cover_label.setAlignment(Qt.AlignCenter)
        self.cover_label.setFrameShape(QFrame.StyledPanel); cover_layout.addWidget(self.cover_label)
        self.btn_cover = QPushButton("Выбрать обложку"); self.btn_cover.clicked.connect(self.choose_cover)
        self.btn_clear_cover = QPushButton("Очистить обложку"); self.btn_clear_cover.clicked.connect(self.clear_cover)
        cover_layout.addWidget(self.btn_cover); cover_layout.addWidget(self.btn_clear_cover)
        fields_layout.addLayout(cover_layout)
        self.main_layout.addLayout(fields_layout)

        # Сохранение
        self.btn_save = QPushButton("💾 Сохранить теги"); self.btn_save.clicked.connect(self.save_tags)
        self.main_layout.addWidget(self.btn_save)

        # Подвал с кликабельными ссылками
        self.footer = QLabel()
        self.footer.setText(
            'Программа: <b>BeatTagger</b> 🎵 | '
            'Автор: <a href="https://t.me/RitinaADM">t.me/RitinaADM</a> | '
            'GitHub: <a href="https://github.com/RitinaADM/BeatTagger">github.com/RitinaADM/BeatTagger</a>'
        )
        self.footer.setAlignment(Qt.AlignCenter)
        self.footer.setStyleSheet("color: gray; font-size: 12px; margin-top: 10px;")
        self.footer.setOpenExternalLinks(True)
        self.main_layout.addWidget(self.footer)

        self.apply_theme()

    # ---- Тема ----
    def apply_theme(self):
        t = THEMES[self.current_theme]
        self.setStyleSheet(f"background-color:{t['background']}; color:{t['text']};")
        for widget in [self.title_edit,self.artist_edit,self.album_edit,self.genre_edit,self.bpm_edit,self.mood_edit,self.comment_edit]:
            widget.setStyleSheet(f"background-color:{t['input_bg']}; color:{t['text']}; border:1px solid #555; border-radius:4px;")
        for btn in [self.btn_mp3,self.btn_folder,self.btn_cover,self.btn_clear_cover,self.btn_save,self.btn_theme]:
            btn.setStyleSheet(f"background-color:{t['button_bg']}; color:white; border-radius:6px; padding:5px;")
        self.cover_label.setStyleSheet(f"background-color:{t['frame_bg']}; color:{t['text']}; border:1px solid #555;")

    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme=="dark" else "dark"
        self.btn_theme.setText("Тёмная тема" if self.current_theme=="light" else "Светлая тема")
        self.apply_theme()

    # ---- Диалоги ----
    def show_message(self, title, text, kind="info"):
        t = THEMES[self.current_theme]
        msg = QMessageBox(self)
        msg.setWindowTitle(title); msg.setText(text)
        icons = {"info": QMessageBox.Information, "warning": QMessageBox.Warning, "error": QMessageBox.Critical}
        msg.setIcon(icons.get(kind,"info"))
        msg.setStyleSheet(f"""
            QMessageBox {{background-color: {t['frame_bg']}; color:{t['text']};}}
            QPushButton {{background-color:{t['button_bg']}; color:white; border-radius:6px; padding:5px;}}
            QPushButton:hover {{background-color:{t['button_hover']}}};
        """)
        msg.exec_()

    # ---- MP3 ----
    def choose_mp3(self):
        path,_ = QFileDialog.getOpenFileName(self,"Выбор MP3 файла","","MP3 Files (*.mp3)")
        if path:
            self.file_path = path
            self.cover_label.setText("Загрузка...")
            self.loader_thread = TagLoaderThread(path)
            self.loader_thread.finished.connect(self.on_tags_loaded)
            self.loader_thread.error.connect(lambda e: self.show_message("Ошибка", e, "error"))
            self.loader_thread.start()

    def on_tags_loaded(self,tags):
        self.title_edit.setText(tags.get("title",""))
        self.artist_edit.setText(tags.get("artist",""))
        self.album_edit.setText(tags.get("album",""))
        self.genre_edit.setText(tags.get("genre",""))
        self.bpm_edit.setText(tags.get("bpm",""))
        self.mood_edit.setText(tags.get("mood",""))
        self.comment_edit.setText(tags.get("comment",""))
        if tags.get("cover"):
            try:
                self.cover_data = resize_cover(tags["cover"])
                self.cover_label.setPixmap(bytes_to_qpixmap(self.cover_data))
            except Exception as e:
                self.show_message("Ошибка при ресайзе обложки", str(e), "warning")
                self.cover_label.setText("Нет обложки")
        else: self.cover_label.setText("Нет обложки")

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self,"Выбор папки с MP3")
        if folder: self.show_message("Выбор папки", f"Выбрана папка: {folder}", "info")

    def choose_cover(self):
        path,_ = QFileDialog.getOpenFileName(self,"Выбор изображения","","Images (*.png *.jpg *.jpeg)")
        if path:
            try:
                self.cover_data = resize_cover(image_to_bytes(path))
                self.cover_label.setPixmap(bytes_to_qpixmap(self.cover_data))
            except Exception as e:
                self.show_message("Ошибка при загрузке обложки", str(e), "error")

    def clear_cover(self):
        self.cover_label.setText("Нет обложки"); self.cover_data = None

    def save_tags(self):
        if not self.file_path: self.show_message("Ошибка","Сначала выберите MP3 файл","warning"); return
        tags = {
            "title": self.title_edit.text(), "artist": self.artist_edit.text(),
            "album": self.album_edit.text(), "genre": self.genre_edit.text(),
            "bpm": self.bpm_edit.text(), "mood": self.mood_edit.text(),
            "comment": self.comment_edit.toPlainText(), "cover": self.cover_data
        }
        try: TagEditor.save_tags(self.file_path,tags); self.show_message("Успех","Теги сохранены!","info")
        except Exception as e: self.show_message("Ошибка",f"Не удалось сохранить теги: {e}","error")
