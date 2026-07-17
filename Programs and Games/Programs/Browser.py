import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import (QApplication, QMainWindow, QToolBar, 
                             QLineEdit, QPushButton, QStatusBar)
from PyQt5.QtWebEngineWidgets import QWebEngineView

class MyBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://www.google.com"))
        self.setCentralWidget(self.browser)
        self.setWindowTitle("PySys Web Browser")
        self.resize(1200, 800)

        navbar = QToolBar()
        self.addToolBar(navbar)

        back_btn = QPushButton("<")
        back_btn.clicked.connect(self.browser.back)
        navbar.addWidget(back_btn)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        navbar.addWidget(self.url_bar)

        self.browser.urlChanged.connect(self.update_url)

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith("http"):
            url = "http://" + url
        self.browser.setUrl(QUrl(url))

    def update_url(self, q):
        self.url_bar.setText(q.toString())

app = QApplication(sys.argv)
window = MyBrowser()
window.show()
sys.exit(app.exec_()) # Use exec_() with an underscore for PyQt5
