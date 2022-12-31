from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QPixmap, QPainter, QPen


class PCAManualWidget(QWidget):
    def __init__(self, label_view: QLabel):
        super().__init__()
        self.image = None
        self.release = False
        self.drawing = False
        self.lastPoint = QPoint()
        self.image = label_view.pixmap()
        self.image_label = label_view

        self.points = []

    def mousePressEvent(self, event):
        r = self.image_label.pos()
        r2 = self.image_label.parent().pos()
        x0, y0 = r.x() + r2.x(), r.y() + r2.y()
        if event.button() == Qt.LeftButton:
            self.drawing = True
            pos = QPoint(event.pos().x() - x0, event.pos().y() - y0)
            self.lastPoint = pos

    def mouseMoveEvent(self, event):
        r = self.image_label.pos()
        r2 = self.image_label.parent().pos()
        x0, y0 = r.x() + r2.x(), r.y() + r2.y()

        if event.buttons() and Qt.LeftButton and (not self.release):
            painter = QPainter(self.image)
            painter.setPen(QPen(Qt.red, 3, Qt.SolidLine))
            pos = QPoint(event.pos().x() - x0, event.pos().y() - y0)
            painter.drawLine(self.lastPoint, pos)
            self.lastPoint = pos
            self.points.append((self.lastPoint.x(), self.lastPoint.y()))
            self.image_label.setPixmap(self.image)

    def setPixmap(self, pixmap: QPixmap):
        self.image = pixmap

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.release = True
            painter = QPainter(self.image)
            painter.setPen(QPen(Qt.red, 3, Qt.SolidLine))
            painter.drawLine(QPoint(self.points[0][0], self.points[0][1]),
                             QPoint(self.points[-1][0], self.points[-1][1]))
            self.image_label.setPixmap(self.image)

    def reset(self):
        self.image = None
        self.release = False
        self.drawing = False
        self.lastPoint = QPoint()
        self.points = []
