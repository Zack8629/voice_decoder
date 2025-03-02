from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog, QTextEdit, QLabel, QSlider, QHBoxLayout, \
    QMenuBar, QMenu, QLineEdit, QProgressBar, QMessageBox, QCheckBox

from . import APP_VERSION, ICON_PATH
from .get_best_device import get_best_device
from .time_estimator import estimate_transcription_time
from .transcribe import transcribe


class TranscriptionThread(QThread):
    progress = pyqtSignal(int)
    result = pyqtSignal(str)

    def __init__(self, file_path, model_name, save_converted):
        super().__init__()
        self.file_path = file_path
        self.model_name = model_name
        self.save_converted = save_converted

    def run(self):
        try:
            text = transcribe(self.file_path, self.model_name, self.progress.emit, self.save_converted)
            self.result.emit(text)
        except Exception as e:
            print(f'Error run => {e}')


class WhisperApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle(f'Whisper Расшифровка {APP_VERSION}')
        self.setWindowIcon(QIcon(str(ICON_PATH)))
        self.setMinimumSize(600, 500)

        main_layout = QVBoxLayout()

        # Меню
        self.menu_bar = QMenuBar(self)
        file_menu = QMenu('Файл', self)
        about_menu = QMenu('Справка', self)

        self.check_hardware_action = QAction('Проверить железо', self)
        self.check_hardware_action.triggered.connect(self.check_hardware)
        file_menu.addAction(self.check_hardware_action)

        self.time_estimate_action = QAction('Примерное время обработки файла', self)
        self.time_estimate_action.triggered.connect(self.check_estimate)
        file_menu.addAction(self.time_estimate_action)

        exit_action = QAction('Выход', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        about_action = QAction('О программе', self)
        about_action.triggered.connect(self.show_about)
        about_menu.addAction(about_action)

        self.menu_bar.addMenu(file_menu)
        self.menu_bar.addMenu(about_menu)
        main_layout.addWidget(self.menu_bar)

        # Панель выбора файла
        file_layout = QHBoxLayout()
        self.btn_select = QPushButton('Выбрать файл')
        self.btn_select.clicked.connect(self.select_file)
        self.file_path_display = QLineEdit()
        self.file_path_display.setReadOnly(True)

        self.save_checkbox = QCheckBox('Сохранить конвертированный файл')
        self.save_checkbox.setChecked(False)
        self.save_checkbox.setStyleSheet("QCheckBox { text-align: right; }")

        file_layout.addWidget(self.btn_select)
        file_layout.addWidget(self.file_path_display)
        file_layout.addWidget(self.save_checkbox)
        main_layout.addLayout(file_layout)

        # Верхние метки (Быстро - Качественно)
        speed_layout = QHBoxLayout()
        self.fast_label = QLabel('Быстро')
        self.fast_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.quality_label = QLabel('Качественно')
        self.quality_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        speed_layout.addWidget(self.fast_label)
        speed_layout.addStretch()
        speed_layout.addWidget(self.quality_label)
        main_layout.addLayout(speed_layout)

        # Ползунок выбора модели
        self.slider_model = QSlider(Qt.Orientation.Horizontal)
        self.slider_model.setMinimum(0)
        self.slider_model.setMaximum(2)
        main_layout.addWidget(self.slider_model)

        # Подписи для ползунка
        slider_labels_layout = QHBoxLayout()
        self.label_small = QLabel('small')
        self.label_medium = QLabel('medium')
        self.label_large = QLabel('large-v3')

        slider_labels_layout.addWidget(self.label_small)
        slider_labels_layout.addStretch()
        slider_labels_layout.addWidget(self.label_medium)
        slider_labels_layout.addStretch()
        slider_labels_layout.addWidget(self.label_large)
        main_layout.addLayout(slider_labels_layout)

        # Кнопка расшифровки
        self.btn_transcribe = QPushButton('Расшифровать')
        self.btn_transcribe.clicked.connect(self.transcribe_file)
        main_layout.addWidget(self.btn_transcribe)

        # Поле вывода текста
        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        main_layout.addWidget(self.text_output)

        # Прогресс-бар с плавным обновлением
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat('Ожидание запуска')
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_bar.setStyleSheet('''
            QProgressBar {
                border: 2px solid gray;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
                background-color: #222;
            }
            QProgressBar::chunk {
                background: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(50, 205, 50, 255), 
                    stop:1 rgba(34, 139, 34, 255));
                border-radius: 5px;
            }
        ''')
        main_layout.addWidget(self.progress_bar)

        # Кнопка "Сохранить в Word" (неактивная)
        self.save_word_button = QPushButton('Сохранить в Word')
        self.save_word_button.setEnabled(False)
        main_layout.addWidget(self.save_word_button)

        self.setLayout(main_layout)
        self.file_path = ''
        self.model_names = ['small', 'medium', 'large-v3']

    def select_file(self):
        filters = 'Video Files (*.mp4 *.mkv *.avi *.mov *.wmv *.flv *.webm);;' \
                  'Audio Files (*.mp3 *.wav *.flac *.aac *.ogg *.m4a *.wma *.aiff *.aif)'

        file_path, _ = QFileDialog.getOpenFileName(self, 'Выбрать файл', '', filters)

        if file_path:
            self.file_path = file_path
            self.file_path_display.setText(file_path)

    def check_hardware(self):
        device = get_best_device()
        QMessageBox.information(self, 'Определение железа', f'Для работы программы будет использоваться {device}')

    def check_estimate(self):
        """Оценивает примерное время обработки файла."""
        if not self.file_path:
            QMessageBox.warning(self, 'Ошибка', 'Выберите файл перед расчетом времени!')
            return

        model_name = self.model_names[self.slider_model.value()]  # Выбранная модель
        msg_estimate = estimate_transcription_time(self.file_path, model_name)
        QMessageBox.information(self, 'Время обработки файла', msg_estimate)

    def transcribe_file(self):
        try:
            if not self.file_path:
                QMessageBox.warning(self, 'Ошибка', 'Выберите файл для расшифровки!')
                return

            self.progress_bar.setValue(0)
            self.text_output.setText('')

            self.btn_select.setEnabled(False)
            self.slider_model.setEnabled(False)
            self.save_checkbox.setEnabled(False)
            self.btn_transcribe.setEnabled(False)

            model_name = self.model_names[self.slider_model.value()]
            save_converted = self.save_checkbox.isChecked()  # Получаем состояние галки

            # Передаём save_converted в поток обработки
            self.transcription_thread = TranscriptionThread(self.file_path, model_name, save_converted)
            self.transcription_thread.progress.connect(self.update_progress)
            self.transcription_thread.result.connect(self.display_result)
            self.transcription_thread.start()
        except Exception as e:
            print(f'Error transcribe_file => {e}')

    def update_progress(self, target_value):
        """Плавное обновление прогресса."""
        if target_value == 0:
            if hasattr(self, 'progress_timer'):
                self.progress_timer.stop()  # Останавливаем таймер, если он работает
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat('Ошибка в работе программы!')
            self.progress_target = 0  # Сбрасываем целевое значение
        else:
            current_value = self.progress_bar.value()
            if current_value < target_value:
                self.progress_target = target_value
                self.progress_step = 1
                self.progress_timer = QTimer(self)
                self.progress_timer.timeout.connect(self.smooth_progress)
                self.progress_timer.start(22)

    def smooth_progress(self):
        """Плавное заполнение прогресс-бара."""
        try:
            current_value = self.progress_bar.value()

            if current_value < self.progress_target:
                self.progress_bar.setValue(current_value + self.progress_step)
            else:
                self.progress_timer.stop()

            # Обновление текста статуса в зависимости от прогресса
            if current_value == 0:
                self.progress_bar.setFormat('Ошибка в работе программы!')
            elif current_value < 30:
                self.progress_bar.setFormat(f'Конвертация файла... {current_value}%')
            elif current_value < 60:
                self.progress_bar.setFormat(f'Подготовка модели... {current_value}%')
            elif current_value < 100:
                self.progress_bar.setFormat(f'Обработка файла... {current_value}%')
            elif current_value >= 100:
                self.progress_bar.setFormat('Готово!')
                self.progress_timer.stop()
        except Exception as e:
            print(f'Error smooth_progress => {e}')
            self.update_progress(0)
            self.progress_bar.setFormat(f'Ошибка!')
            self.text_output.setText('Ошибка в smooth_progress')

    def display_result(self, text):
        """Выводит результат и завершает процесс."""
        self.text_output.setText(text)

        self.btn_select.setEnabled(True)
        self.slider_model.setEnabled(True)
        self.save_checkbox.setEnabled(True)
        self.btn_transcribe.setEnabled(True)

        print(f'display_result Done!')

    def show_about(self):
        text_information = (f'Whisper Расшифровка {APP_VERSION}\n'
                            f'Разработчик: Зарихин В. А.')
        QMessageBox.information(self, 'О программе', text_information)
