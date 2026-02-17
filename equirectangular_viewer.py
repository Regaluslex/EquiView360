import os
import sys
import math
import tkinter as tk
from tkinter import filedialog
from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtOpenGL import QGLWidget
from PyQt5.QtGui import QPainter, QFont
from PyQt5.QtWidgets import QLabel
from PIL import Image

class GLWidget(QGLWidget):
    def __init__(self, parent, image_path):
        super().__init__(parent)
        try:
            self.image = Image.open(image_path)
            self.image = self.image.convert("RGB")  # Ensure image is in RGB format
            self.image_width, self.image_height = self.image.size
        except FileNotFoundError:
            print(f"Error: Image file '{image_path}' not found.")
            sys.exit(1)
        except Exception as e:
            print(f"Error loading image: {e}")
            sys.exit(1)
        self.yaw = 0
        self.pitch = 0
        self.prev_dx = 0
        self.prev_dy = 0
        self.fov = 90
        self.moving = False
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.sphere = gluNewQuadric()  # Créé une seule fois
        self.image_path = image_path
        self.folder = os.path.dirname(image_path)
        self.filelist = [f for f in os.listdir(self.folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        self.current_index = self.filelist.index(os.path.basename(image_path)) if os.path.basename(image_path) in self.filelist else 0
        self.setFocusPolicy(QtCore.Qt.StrongFocus)  # Activer le focus
        self.label = QtWidgets.QLabel(self)
        self.label.setStyleSheet("QLabel { color: white; background: transparent; }")
        self.label.setFont(QFont("Arial", 12))
        self.label.move(10, 10)
        self.label.setMinimumWidth(300)
        self.update_label()
        
    def update_label(self):
        self.label.clear()
        file_name = os.path.basename(self.image_path)
        self.label.setText(f"File: {file_name}\nFOV: {self.fov:.1f}°")
        self.label.adjustSize()
        self.label.update()

    def initializeGL(self):
        glEnable(GL_TEXTURE_2D)
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.image_width, self.image_height, 0, GL_RGB, GL_UNSIGNED_BYTE, self.image.tobytes())
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        self.sphere = gluNewQuadric()
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(90, self.width()/self.height(), 0.1, 1000)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        self.label.update()

    def change_image(self, new_path):
        try:
            self.image = Image.open(new_path)
            self.image = self.image.convert("RGB")
            self.image_width, self.image_height = self.image.size
            glBindTexture(GL_TEXTURE_2D, self.texture)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.image_width, self.image_height, 0,
                         GL_RGB, GL_UNSIGNED_BYTE, self.image.tobytes())
            self.update()
            self.update_label()
        except FileNotFoundError:
            print(f"Error: Image file '{new_path}' not found.")
        except Exception as e:
            print(f"Erreur lors du changement d'image : {e}")

    def next_file(self):
        self.current_index = (self.current_index + 1) % len(self.filelist)
        new_path = os.path.join(self.folder, self.filelist[self.current_index])
        self.image_path = new_path
        self.change_image(new_path)
        self.update()
        self.update_label()
        print(new_path)

    def newpath(self):
        new_path = tk.filedialog.askopenfilename()
        self.image_path = new_path
        self.change_image(new_path)
        self.update()
        self.update_label()
        print(new_path)        

    def prev_file(self):
        self.current_index = (self.current_index - 1) % len(self.filelist)
        new_path = os.path.join(self.folder, self.filelist[self.current_index])
        self.image_path = new_path
        self.change_image(new_path)
        self.update()
        self.update_label()
        print(new_path)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        glRotatef(self.pitch, 1, 0, 0)
        glRotatef(self.yaw, 0, 1, 0)
        glRotatef(90, 1, 0, 0)
        glRotatef(-90, 0, 0, 1)
        gluQuadricTexture(self.sphere, True)
        gluSphere(self.sphere, 1, 100, 100)
        glPopMatrix()
          
    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.fov, self.width()/self.height(), 0.1, 1000)
        
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.mouse_x, self.mouse_y = event.pos().x(), event.pos().y()
            self.moving = True
            self.update_label()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.moving = False
            self.update_label()

    def mouseMoveEvent(self, event):
        if self.moving:
            dx = event.pos().x() - self.mouse_x 
            dy = event.pos().y() - self.mouse_y
            dx *= 0.1
            dy *= 0.1
            self.yaw -= dx
            self.pitch -= dy
            self.pitch = min(max(self.pitch, -90), 90)
            self.mouse_x, self.mouse_y = event.pos().x(), event.pos().y()
            self.update()
            
    def keyPressEvent(self, event):
        print(f"Key pressed: {event.key()}")  # Débogage
        if event.key() == QtCore.Qt.Key_O:
            self.newpath()
        elif event.key() == QtCore.Qt.Key_Left:
            self.prev_file()
        elif event.key() == QtCore.Qt.Key_Right:
            self.next_file()
        elif event.key() == QtCore.Qt.Key_Q:
            print("Fermeture de l'application...")
            sys.exit(0)
        else :
            self.update()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        self.fov -= delta * 0.1
        self.fov = max(30, min(self.fov, 90))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.fov, self.width()/self.height(), 0.1, 1000)
        self.update()
        self.update_label()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, image_path):
        super().__init__()
        self.setWindowTitle("Equirectangular 360° Viewer")
        self.setWindowIcon(QtGui.QIcon("icon.png"))
        self.gl_widget = GLWidget(self, image_path)
        self.setCentralWidget(self.gl_widget)
        self.gl_widget.setFocus() # Donner le focus au GLWidget

if __name__ == '__main__':
    if len(sys.argv) < 2:
        image_path = tk.filedialog.askopenfilename()
    else :
        image_path = sys.argv[1]
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(image_path)
    window.setGeometry(0, 0, 1080, 720)
    window.show()
    app.exec_()
