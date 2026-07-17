import sys
import random
from collections import deque
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QSlider, QLabel, QColorDialog, QFileDialog)
from PyQt5.QtGui import QPainter, QPen, QImage, QColor
from PyQt5.QtCore import Qt, QPoint, QRect

class DrawingCanvas(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_StaticContents)
        
        # Drawing configurations
        self.drawing = False
        self.brush_size = 5
        self.brush_color = QColor(Qt.black)
        self.current_tool = "brush"  # Options: brush, eraser, line, circle, rectangle, spray, bucket
        self.last_point = QPoint()

        # Canvas image tracking frames
        self.image = QImage(800, 600, QImage.Format_RGB32)
        self.image.fill(Qt.white)
        self.backup_image = QImage()
        
        # History stacks for Undo/Redo
        self.undo_stack = []
        self.redo_stack = []
        self.max_history_steps = 30

    def resizeEvent(self, event):
        if self.image.size() != self.size():
            new_image = QImage(self.size(), QImage.Format_RGB32)
            new_image.fill(Qt.white)
            
            painter = QPainter(new_image)
            painter.drawImage(QPoint(0, 0), self.image)
            self.image = new_image
        super().resizeEvent(event)

    def paintEvent(self, event):
        canvas_painter = QPainter(self)
        canvas_painter.drawImage(self.rect(), self.image, self.image.rect())

    def save_undo_state(self):
        """Saves a snapshot of the canvas to the undo stack."""
        if len(self.undo_stack) >= self.max_history_steps:
            self.undo_stack.pop(0)
        self.undo_stack.append(QImage(self.image))

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append(QImage(self.image))
            self.image = self.undo_stack.pop()
            self.update()

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append(QImage(self.image))
            self.image = self.redo_stack.pop()
            self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.save_undo_state()
            self.redo_stack.clear()
            
            if self.current_tool == "bucket":
                self.flood_fill(event.pos())
                self.update()
            else:
                self.drawing = True
                self.last_point = event.pos()
                self.backup_image = QImage(self.image)

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton) and self.drawing:
            current_point = event.pos()
            
            if self.current_tool in ["brush", "eraser"]:
                painter = QPainter(self.image)
                painter.setPen(self.create_pen())
                painter.drawLine(self.last_point, current_point)
                self.last_point = current_point
                
            elif self.current_tool == "spray":
                painter = QPainter(self.image)
                painter.setPen(self.create_pen())
                radius = self.brush_size * 3
                for _ in range(15):
                    dx = random.randint(-radius, radius)
                    dy = random.randint(-radius, radius)
                    if dx*dx + dy*dy <= radius*radius:
                        painter.drawPoint(current_point.x() + dx, current_point.y() + dy)
                        
            else:
                self.image = QImage(self.backup_image)
                painter = QPainter(self.image)
                painter.setPen(self.create_pen())
                
                if self.current_tool == "line":
                    painter.drawLine(self.last_point, current_point)
                elif self.current_tool == "circle":
                    painter.drawEllipse(QRect(self.last_point, current_point))
                elif self.current_tool == "rectangle":
                    painter.drawRect(QRect(self.last_point, current_point))
            
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = False

    def create_pen(self):
        pen = QPen()
        color = QColor(Qt.white) if self.current_tool == "eraser" else self.brush_color
        pen.setColor(color)
        pen.setWidth(self.brush_size)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        return pen

    def flood_fill(self, pos):
        width, height = self.image.width(), self.image.height()
        target_rgb = self.image.pixel(pos.x(), pos.y())
        fill_rgb = self.brush_color.rgb()

        if target_rgb == fill_rgb:
            return

        queue = deque([(pos.x(), pos.y())])
        self.image.setPixel(pos.x(), pos.y(), fill_rgb)

        while queue:
            cx, cy = queue.popleft()
            for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                if 0 <= nx < width and 0 <= ny < height:
                    if self.image.pixel(nx, ny) == target_rgb:
                        self.image.setPixel(nx, ny, fill_rgb)
                        queue.append((nx, ny))

    def clear_canvas(self):
        self.save_undo_state()
        self.redo_stack.clear()
        self.image.fill(Qt.white)
        self.update()


class PaintWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt5 Pro Paint Application")
        self.setGeometry(100, 100, 1050, 750)

        main_widget = QWidget()
        main_layout = QHBoxLayout()
        
        self.canvas = DrawingCanvas()

        toolbar_layout = QVBoxLayout()
        toolbar_layout.setAlignment(Qt.AlignTop)

        # --- DRAWING TOOLS ---
        toolbar_layout.addWidget(QLabel("<b>Brushes & FX:</b>"))
        
        self.btn_brush = QPushButton("🖌️ Brush")
        self.btn_brush.clicked.connect(lambda: self.set_tool("brush"))
        toolbar_layout.addWidget(self.btn_brush)

        self.btn_spray = QPushButton("💨 Spray Can")
        self.btn_spray.clicked.connect(lambda: self.set_tool("spray"))
        toolbar_layout.addWidget(self.btn_spray)

        self.btn_bucket = QPushButton("🪣 Bucket Fill")
        self.btn_bucket.clicked.connect(lambda: self.set_tool("bucket"))
        toolbar_layout.addWidget(self.btn_bucket)

        self.btn_eraser = QPushButton("🧽 Eraser")
        self.btn_eraser.clicked.connect(lambda: self.set_tool("eraser"))
        toolbar_layout.addWidget(self.btn_eraser)
        
        toolbar_layout.addSpacing(10)

        # --- SHAPE TOOLS ---
        toolbar_layout.addWidget(QLabel("<b>Shapes:</b>"))

        self.btn_line = QPushButton("📏 Line")
        self.btn_line.clicked.connect(lambda: self.set_tool("line"))
        toolbar_layout.addWidget(self.btn_line)

        self.btn_circle = QPushButton("⭕ Circle")
        self.btn_circle.clicked.connect(lambda: self.set_tool("circle"))
        toolbar_layout.addWidget(self.btn_circle)

        self.btn_rect = QPushButton("🟩 Rectangle")
        self.btn_rect.clicked.connect(lambda: self.set_tool("rectangle"))
        toolbar_layout.addWidget(self.btn_rect)
        
        toolbar_layout.addSpacing(10)

        # --- BRUSH SIZE ---
        self.size_label = QLabel(f"Size: {self.canvas.brush_size} px")
        toolbar_layout.addWidget(self.size_label)
        
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(50)
        self.slider.setValue(self.canvas.brush_size)
        self.slider.valueChanged.connect(self.change_size)
        toolbar_layout.addWidget(self.slider)

        toolbar_layout.addSpacing(10)

        # --- COLOR SELECTION ---
        toolbar_layout.addWidget(QLabel("<b>Colors:</b>"))
        
        colors = [
            ("Black", Qt.black), ("Red", Qt.red), 
            ("Green", Qt.green), ("Blue", Qt.blue)
        ]
        for name, color in colors:
            btn = QPushButton(name)
            btn.clicked.connect(lambda checked, c=color: self.change_color(c))
            toolbar_layout.addWidget(btn)

        self.btn_custom_color = QPushButton("Custom Color...")
        self.btn_custom_color.clicked.connect(self.pick_custom_color)
        toolbar_layout.addWidget(self.btn_custom_color)

        toolbar_layout.addSpacing(25)

        # --- EDIT ACTIONS ---
        toolbar_layout.addWidget(QLabel("<b>Actions:</b>"))
        
        history_layout = QHBoxLayout()
        self.btn_undo = QPushButton("↩️ Undo")
        self.btn_undo.clicked.connect(self.canvas.undo)
        self.btn_redo = QPushButton("↪️ Redo")
        self.btn_redo.clicked.connect(self.canvas.redo)
        history_layout.addWidget(self.btn_undo)
        history_layout.addWidget(self.btn_redo)
        toolbar_layout.addLayout(history_layout)

        # New File Loading Action
        self.btn_load = QPushButton("📂 Open Image")
        self.btn_load.setStyleSheet("background-color: #e6f2ff;")
        self.btn_load.clicked.connect(self.load_file)
        toolbar_layout.addWidget(self.btn_load)

        self.btn_save = QPushButton("💾 Save Image")
        self.btn_save.setStyleSheet("background-color: #ccffcc; font-weight: bold;")
        self.btn_save.clicked.connect(self.save_file)
        toolbar_layout.addWidget(self.btn_save)

        self.btn_clear = QPushButton("🗑️ Clear Canvas")
        self.btn_clear.setStyleSheet("background-color: #ffcccc;")
        self.btn_clear.clicked.connect(self.canvas.clear_canvas)
        toolbar_layout.addWidget(self.btn_clear)

        # Sidebar Assembly
        sidebar_widget = QWidget()
        sidebar_widget.setLayout(toolbar_layout)
        sidebar_widget.setFixedWidth(160)

        main_layout.addWidget(sidebar_widget)
        main_layout.addWidget(self.canvas)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    # Controller Actions
    def set_tool(self, tool_name):
        self.canvas.current_tool = tool_name

    def change_size(self, value):
        self.canvas.brush_size = value
        self.size_label.setText(f"Size: {value} px")

    def change_color(self, color):
        if self.canvas.current_tool == "eraser":
            self.canvas.current_tool = "brush"
        self.canvas.brush_color = QColor(color)

    def pick_custom_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.change_color(color)

    def load_file(self):
        """Opens an image from your computer and loads it onto the canvas."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*)"
        )
        if file_path:
            loaded_image = QImage(file_path)
            if not loaded_image.isNull():
                # Scale the image container to clean 32-bit RGB format matching the canvas configuration
                self.canvas.image = loaded_image.convertToFormat(QImage.Format_RGB32)
                # Clear history lines since we are starting a fresh project layout
                self.canvas.undo_stack.clear()
                self.canvas.redo_stack.clear()
                self.canvas.update()

    def save_file(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Your Masterpiece", "", "PNG Image (*.png);;JPEG Image (*.jpg);;All Files (*)"
        )
        if file_path:
            self.canvas.image.save(file_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PaintWindow()
    window.show()
    sys.exit(app.exec_())