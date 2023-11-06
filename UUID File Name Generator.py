import sys
import shutil
import uuid
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox, QWidget, QComboBox, QTextEdit, QCheckBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class UUIDFileGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.selected_file_paths = []
        self.show_full_paths = False
        self.uuid_types = ['UUID1', 'UUID3', 'UUID4', 'UUID5']
        self.init_ui()

    def generate_uuid(self, uuid_type):
        if uuid_type == 'UUID1':
            return str(uuid.uuid1())
        elif uuid_type == 'UUID3':
            return str(uuid.uuid3(uuid.NAMESPACE_DNS, 'python.org'))
        elif uuid_type == 'UUID4':
            return str(uuid.uuid4())
        elif uuid_type == 'UUID5':
            return str(uuid.uuid5(uuid.NAMESPACE_DNS, 'python.org'))
        else:
            return str(uuid.uuid4())

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            file_paths = [url.toLocalFile() for url in event.mimeData().urls()]
            self.selected_file_paths.extend(file_paths)
            self.show_selected_files()
            self.save_button.setEnabled(True)
            self.save_button.setStyleSheet("font: 14px; color: white; background-color: #4CAF50; padding: 12px 24px")
            event.accept()
        else:
            event.ignore()

    def select_files(self):
        try:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            self.selected_file_paths, _ = QFileDialog.getOpenFileNames(self, "Select Files", "", "", options=options)
            if self.selected_file_paths:
                self.show_selected_files()
                self.save_button.setEnabled(True)
                self.save_button.setStyleSheet("font: 14px; color: white; background-color: #4CAF50; padding: 12px 24px")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def show_selected_files(self):
        self.selected_file_label.setText("")
        if self.show_full_paths:
            for file_path in self.selected_file_paths:
                self.selected_file_label.append(file_path)
        else:
            for file_path in self.selected_file_paths:
                self.selected_file_label.append(file_path.split('/')[-1])

    def toggle_show_full_paths(self, state):
        self.show_full_paths = state
        self.show_selected_files()

    def save_with_uuid_name(self):
        try:
            if self.selected_file_paths:
                options = QFileDialog.Options()
                options |= QFileDialog.DontUseNativeDialog
                directory = QFileDialog.getExistingDirectory(self, "Select Directory to Save Files", options=options)
                if directory:
                    uuid_type = self.uuid_combo.currentText()

                    thread = threading.Thread(target=self.process_files, args=(directory, uuid_type))
                    thread.start()

                    QMessageBox.information(self, "Success", f"Files saved with {uuid_type}-assigned names in {directory}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def process_files(self, directory, uuid_type):
        for file_path in self.selected_file_paths:
            generated_uuid = self.generate_uuid(uuid_type)
            file_extension = file_path.split('.')[-1]
            file_name = f"{generated_uuid}.{file_extension}"
            new_file_path = f"{directory}/{file_name}"
            if new_file_path == file_path:
                new_file_path = f"{directory}/{generated_uuid}_1.{file_extension}"
            shutil.copy2(file_path, new_file_path)

    def clear_display(self):
        self.uuid_display.setText("")
        self.selected_file_label.setText("")
        self.save_button.setEnabled(False)
        self.save_button.setStyleSheet("font: 14px; color: white; background-color: #555555; padding: 12px 24px")

    def init_ui(self):
        self.setWindowTitle("UUID File Name Generator")
        self.setGeometry(100, 100, 600, 400)
        self.setStyleSheet("background-color: #FFFFFF")

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        title_label = QLabel("UUID File Name Generator", self)
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        layout.addWidget(title_label, alignment=Qt.AlignHCenter)

        description_label = QLabel("Drag and drop files or click to select files", self)
        description_label.setFont(QFont("Arial", 12))
        layout.addWidget(description_label, alignment=Qt.AlignHCenter)

        select_button = QPushButton("Select Files", self)
        select_button.clicked.connect(self.select_files)
        select_button.setStyleSheet("font: 14px; color: white; background-color: #2196F3; padding: 12px 24px")
        layout.addWidget(select_button, alignment=Qt.AlignHCenter)

        self.selected_files_label = QLabel("Selected Files:", self)
        self.selected_files_label.setFont(QFont("Arial", 12))
        layout.addWidget(self.selected_files_label, alignment=Qt.AlignLeft)

        self.selected_file_label = QTextEdit(self)
        self.selected_file_label.setReadOnly(True)
        self.selected_file_label.setStyleSheet("font: 12px")
        layout.addWidget(self.selected_file_label)

        self.uuid_combo = QComboBox(self)
        self.uuid_combo.addItems(self.uuid_types)
        self.uuid_combo.setMinimumWidth(200)
        layout.addWidget(self.uuid_combo, alignment=Qt.AlignHCenter)

        self.show_full_paths_checkbox = QCheckBox("Show Full Paths", self)
        self.show_full_paths_checkbox.stateChanged.connect(self.toggle_show_full_paths)
        layout.addWidget(self.show_full_paths_checkbox, alignment=Qt.AlignHCenter)

        self.save_button = QPushButton("Save Files", self)
        self.save_button.clicked.connect(self.save_with_uuid_name)
        self.save_button.setEnabled(False)
        self.save_button.setStyleSheet("font: 16px; color: white; background-color: #555555; padding: 14px 28px")
        layout.addWidget(self.save_button, alignment=Qt.AlignHCenter)

        clear_button = QPushButton("Clear", self)
        clear_button.clicked.connect(self.clear_display)
        clear_button.setStyleSheet("font: 12px; color: white; background-color: #f44336; padding: 8px 16px")
        layout.addWidget(clear_button, alignment=Qt.AlignHCenter)

        self.uuid_display = QLabel("", self)
        self.uuid_display.setAlignment(Qt.AlignCenter)
        self.uuid_display.setFont(QFont("Arial", 14))
        layout.addWidget(self.uuid_display, alignment=Qt.AlignHCenter)

        footer = QLabel(f"Developed by PatchGT | Version 2.3 | 2023-11-05", self)
        footer.setAlignment(Qt.AlignCenter)
        footer.setFont(QFont("Arial", 12, QFont.StyleItalic))
        layout.addWidget(footer)

        self.setAcceptDrops(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UUIDFileGenerator()
    window.show()
    sys.exit(app.exec_())
