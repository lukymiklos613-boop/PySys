import sys
import os
import subprocess
import shutil
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, 
                             QLineEdit, QFileDialog, QVBoxLayout, QHBoxLayout, QMessageBox)
os.system(sys.executable + " -m pip install PyQt5")
class PySysInstaller(QWidget):
    def __init__(self):
        super().__init__()
        self.installer_dir = os.path.dirname(os.path.abspath(__file__))
        self.archive_7z = os.path.join(self.installer_dir, "PySys.7z")
        
        # --- UNIVERSAL 7-ZIP DETECTION (WIN + LINUX) ---
        self.cmd_7z = None
        self.detect_7z()
        
        self.initUI()
        
    def detect_7z(self):
        """Attempts to locate 7z on any operating system."""
        # 1. Check if 7z is available in the global system PATH (Linux or well-configured Windows)
        for cmd in ["7z", "7zz"]:
            if shutil.which(cmd):
                self.cmd_7z = cmd
                return

        # 2. If on Windows and global command is missing, check typical installation paths
        if sys.platform.startswith("win"):
            possible_paths = [
                r"C:\Program Files\7-Zip\7z.exe",
                r"C:\Program Files\7-Zip\7-Zip\7z.exe",
                os.path.join(self.installer_dir, "7z.exe") # Checks local script directory as well
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    self.cmd_7z = path
                    return

    def initUI(self):
        self.setWindowTitle('PySys - Setup and Repair')
        self.setFixedSize(550, 170)
        
        main_layout = QVBoxLayout()
        
        self.source_info = QLabel(self)
        if os.path.exists(self.archive_7z):
            self.source_info.setText("Archive status: PySys.7z (Found)")
            self.source_info.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.source_info.setText("PySys 1.0 Setup")
            self.source_info.setStyleSheet("color: black; font-weight: bold;")
            
        main_layout.addWidget(self.source_info)
        main_layout.addSpacing(5)
        
        main_layout.addWidget(QLabel('Select folder for setup / repair:', self))
        target_layout = QHBoxLayout()
        self.path_input = QLineEdit(self)
        
        # Universal cross-platform default folder path
        self.path_input.setText(os.path.abspath(os.path.join(".", "PySys")))
        
        target_layout.addWidget(self.path_input)
        
        self.browse_btn = QPushButton('Browse...', self)
        self.browse_btn.clicked.connect(self.select_target_dir)
        target_layout.addWidget(self.browse_btn)
        main_layout.addLayout(target_layout)
        
        main_layout.addSpacing(15)
        
        buttons_layout = QHBoxLayout()
        
        self.install_btn = QPushButton('Install, Repair or Update', self)
        self.install_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; font-size: 13px;")
        self.install_btn.setFixedHeight(40)
        self.install_btn.clicked.connect(self.run_installation)
        buttons_layout.addWidget(self.install_btn)
        
        
        
        main_layout.addLayout(buttons_layout)
        self.setLayout(main_layout)
        
    def show_missing_7z_error(self):
        """Displays an OS-specific error message if 7-Zip is missing."""
        if sys.platform.startswith("win"):
            msg = ("7-Zip program was not found on your system!\n\n"
                   "Please install it using CMD:\nwinget install 7zip.7zip\n"
                   "Or download it manually from https://www.7-zip.org/")
        else:
            msg = ("7-Zip program (7z/7zz) is missing from your system!\n\n"
                   "Please install it using your package manager, e.g.:\n"
                   "Ubuntu/Debian: sudo apt install 7zip\n"
                   "Arch Linux: sudo pacman -S p7zip")
        QMessageBox.critical(self, "System Error", msg)

    def validate_archive(self):
        if not os.path.exists(self.archive_7z):
            QMessageBox.critical(self, "Error", f"Missing source archive!\n\nPlease place the original 'PySys.7z' file in this folder:\n{self.installer_dir}")
            return False
        if not self.cmd_7z:
            self.show_missing_7z_error()
            return False
        return True

    def select_target_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Target Directory", self.path_input.text())
        if directory:
            self.path_input.setText(os.path.abspath(directory))

    def run_installation(self):
        if not self.validate_archive():
            return
            
        target_dir = self.path_input.text().strip()
        if not target_dir:
            QMessageBox.warning(self, "Error", "Please select a valid target folder.")
            return
            
        try:
            os.makedirs(target_dir, exist_ok=True)
            command = [self.cmd_7z, "x", self.archive_7z, f"-o{target_dir}", "-y"]
            subprocess.run(command, capture_output=True, text=True, check=True)
            QMessageBox.information(self, "Success", f"Full installation completed successfully to:\n{target_dir}")
            
        except subprocess.CalledProcessError as e:
            error_details = e.stderr if e.stderr else e.stdout
            QMessageBox.critical(self, "Archive Error", f"Failed to extract the archive.\n\nDetails:\n{error_details}")

    def run_repair(self):
        if not self.validate_archive():
            return
            
        target_dir = self.path_input.text().strip()
        if not os.path.exists(target_dir):
            QMessageBox.warning(self, "Error", "Target directory does not exist. Please install the program first.")
            return
            
        try:
            list_command = [self.cmd_7z, "l", "-slt", self.archive_7z]
            result = subprocess.run(list_command, capture_output=True, text=True, check=True)
            
            target_filenames = {"PySys.py"}
            files_to_extract = []
            
            for line in result.stdout.splitlines():
                if line.startswith("Path = "):
                    internal_path = line[7:].strip()
                    normalized_path = internal_path.replace('\\', '/')
                    basename = os.path.basename(normalized_path).lower()
                    if basename in target_filenames:
                        files_to_extract.append(internal_path)
            
            if not files_to_extract:
                QMessageBox.warning(
                    self, 
                    "Repair Error", 
                    "Could not find PySys.py' inside the archive."
                )
                return
                
            repair_command = [self.cmd_7z, "e", self.archive_7z, f"-o{target_dir}", "-y"] + files_to_extract
            subprocess.run(repair_command, capture_output=True, text=True, check=True)
            
            # Safe for Python 3.9 (No backslashes inside the f-string)
            fixed_list_str = "\n".join(["- " + os.path.basename(f.replace('\\', '/')) for f in files_to_extract])
            
            QMessageBox.information(
                self, 
                "Repair Completed", 
                f"Core files were successfully restored from the archive!\n\n"
                f"The following files have been overwritten:\n{fixed_list_str}"
            )
            
        except subprocess.CalledProcessError as e:
            error_details = e.stderr if e.stderr else e.stdout
            QMessageBox.critical(self, "Repair Error", f"Failed to extract files for repair.\n\nDetails:\n{error_details}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PySysInstaller()
    ex.show()
    sys.exit(app.exec_())
