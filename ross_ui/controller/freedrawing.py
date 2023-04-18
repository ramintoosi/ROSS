from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPixmap, QPainter, QPen
from PyQt5.QtWidgets import QMainWindow


class FreeDrawing(QMainWindow):
    def __init__(self, image_path=None):
        super().__init__()
        self.drawing = False
        self.lastPoint = QPoint()
        self.image = QPixmap(image_path)
        self.resize(self.image.width(), self.image.height())
        self.show()
        self.points = []

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.image)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.lastPoint = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() and Qt.LeftButton and self.drawing:
            painter = QPainter(self.image)
            painter.setPen(QPen(Qt.red, 3, Qt.SolidLine))
            painter.drawLine(self.lastPoint, event.pos())
            self.lastPoint = event.pos()
            self.points.append((self.lastPoint.x(), self.lastPoint.y()))
            # print("points ", self.points[-1])
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button == Qt.LeftButton:
            self.drawing = False

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     mainMenu = FreeDrawing(image_path="test.png")
#     print(mainMenu.points)
#     sys.exit(app.exec_())
