import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QListWidget, QListWidgetItem, 
                             QFileDialog, QMessageBox, QAbstractItemView, QMenu, QLabel)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap, QImage, QTransform, QPainter, QColor, QFont, QPen
import fitz  # PyMuPDF

class DropListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dark_mode = False

    def paintEvent(self, event):
        super().paintEvent(event)
        # Dibujar la "Drop Zone" solo si la lista está vacía
        if self.count() == 0:
            painter = QPainter(self.viewport())
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setRenderHint(QPainter.TextAntialiasing)
            
            # Crear un margen interno responsivo para el recuadro
            rect = self.viewport().rect().adjusted(40, 40, -40, -40)
            
            # Paleta de colores minimalista sensible al tema
            if self.dark_mode:
                border_color = QColor("#555555")
                text_color = QColor("#888888")
            else:
                border_color = QColor("#cccccc")
                text_color = QColor("#7f8c8d")
                
            # 1. Dibujar el borde punteado (DashLine)
            pen = QPen(border_color, 2, Qt.DashLine)
            painter.setPen(pen)
            painter.drawRoundedRect(rect, 15, 15)
            
            # 2. Dibujar el texto principal
            painter.setPen(text_color)
            font_title = QFont("Arial", 16, QFont.Bold)
            painter.setFont(font_title)
            # Desplazamos el texto principal un poco hacia arriba
            painter.drawText(rect.adjusted(0, -20, 0, -20), Qt.AlignCenter, "Arrastra y suelta tus PDF aquí")
            
            # 3. Dibujar el texto secundario
            font_sub = QFont("Arial", 12)
            painter.setFont(font_sub)
            # Desplazamos el texto secundario un poco hacia abajo
            painter.drawText(rect.adjusted(0, 30, 0, 30), Qt.AlignCenter, "o utiliza el botón de añadir archivos")

class PDFMergerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Unificador de PDF")
        self.resize(900, 600)
        self.dark_mode = False

        self.setWindowIcon(self.create_pdf_icon())

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.toolbar_layout = QHBoxLayout()
        
        self.btn_add = QPushButton("Añadir Archivos PDF")
        self.btn_add.setCursor(Qt.PointingHandCursor)
        self.btn_add.clicked.connect(self.add_file_dialog)
        
        self.btn_theme_icon = QPushButton()
        self.btn_theme_icon.setCursor(Qt.PointingHandCursor)
        self.btn_theme_icon.setText("☀") 
        self.btn_theme_icon.clicked.connect(self.toggle_theme)

        self.btn_merge = QPushButton("Unir y Guardar PDF")
        self.btn_merge.setCursor(Qt.PointingHandCursor)
        self.btn_merge.clicked.connect(self.merge_pdfs)
        
        self.toolbar_layout.addWidget(self.btn_add)
        self.toolbar_layout.addStretch() 
        self.toolbar_layout.addWidget(self.btn_theme_icon)
        self.toolbar_layout.addWidget(self.btn_merge)
        
        self.layout.addLayout(self.toolbar_layout)

        self.list_widget = DropListWidget()
        self.list_widget.setViewMode(QListWidget.IconMode)
        self.list_widget.setIconSize(QSize(150, 200))
        self.list_widget.setSpacing(10)
        self.list_widget.setMovement(QListWidget.Snap)
        self.list_widget.setAcceptDrops(True)
        self.list_widget.setDragEnabled(True)
        self.list_widget.setDragDropMode(QAbstractItemView.InternalMove)
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.show_context_menu)
        
        self.layout.addWidget(self.list_widget)

        self.footer_label = QLabel("<i>Idea y Desarrollo Leandro Sesto - Todos los derechos reservados</i>")
        self.footer_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.footer_label)

        self.setAcceptDrops(True)
        self.apply_styles()

    def create_pdf_icon(self):
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        painter.setBrush(QColor("#e74c3c"))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(4, 4, 56, 56, 12, 12)
        
        painter.setPen(QColor("white"))
        font = QFont("Arial", 16, QFont.Bold)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "PDF")
        painter.end()
        
        return QIcon(pixmap)

    def apply_styles(self):
        button_style = """
            QPushButton { 
                background-color: #0052cc; 
                color: white; 
                border: none; 
                padding: 10px 15px; 
                border-radius: 5px; 
                font-weight: bold; 
            }
            QPushButton:hover { 
                background-color: #003d99; 
            }
        """
        icon_button_style_dark = """
            QPushButton { background-color: transparent; color: #f1c40f; border: none; font-size: 20px; font-weight: bold; padding: 5px; }
            QPushButton:hover { background-color: #3d3d3d; border-radius: 15px; }
        """
        icon_button_style_light = """
            QPushButton { background-color: transparent; color: #2c3e50; border: none; font-size: 20px; font-weight: bold; padding: 5px; }
            QPushButton:hover { background-color: #dfe1e6; border-radius: 15px; }
        """

        if self.dark_mode:
            self.setStyleSheet(f"""
                QMainWindow {{ background-color: #1e1e1e; }}
                DropListWidget {{ background-color: #2d2d2d; border: 1px solid #3d3d3d; color: #ffffff; outline: none; }}
                QLabel {{ color: #888888; font-size: 13px; margin-top: 5px; margin-bottom: 5px; }}
                {button_style}
            """)
            self.btn_theme_icon.setStyleSheet(icon_button_style_dark)
        else:
            self.setStyleSheet(f"""
                QMainWindow {{ background-color: #f4f5f7; }}
                DropListWidget {{ background-color: #ffffff; border: 1px solid #dfe1e6; color: #000000; outline: none; }}
                QLabel {{ color: #7f8c8d; font-size: 13px; margin-top: 5px; margin-bottom: 5px; }}
                {button_style}
            """)
            self.btn_theme_icon.setStyleSheet(icon_button_style_light)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.list_widget.dark_mode = self.dark_mode
        
        if self.dark_mode:
            self.btn_theme_icon.setText("☽")
        else:
            self.btn_theme_icon.setText("☀")
            
        self.apply_styles()
        self.list_widget.viewport().update()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            filepath = url.toLocalFile()
            self.process_file(filepath)

    def add_file_dialog(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Seleccionar Archivos", "", "Documentos PDF (*.pdf)")
        for f in files:
            self.process_file(f)

    def process_file(self, filepath):
        if not os.path.exists(filepath):
            return

        ext = filepath.lower().split('.')[-1]
        if ext != 'pdf':
            QMessageBox.warning(self, "Formato no válido", "Solo se admiten archivos en formato PDF.")
            return

        self.load_pdf_pages(filepath)

    def load_pdf_pages(self, filepath):
        try:
            doc = fitz.open(filepath)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5)) 
                
                img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
                qpixmap = QPixmap.fromImage(img)

                item = QListWidgetItem()
                item.setIcon(QIcon(qpixmap))
                item.setText(f"Pág. {page_num + 1}")
                item.setData(Qt.UserRole, {"file": filepath, "page": page_num, "rotation": 0, "original_pixmap": qpixmap})
                
                self.list_widget.addItem(item)
            doc.close()
        except Exception as e:
            QMessageBox.critical(self, "Error al leer PDF", str(e))

    def show_context_menu(self, pos):
        item = self.list_widget.itemAt(pos)
        if not item:
            return

        menu = QMenu()
        rotate_right = menu.addAction("Girar 90° a la derecha")
        delete_page = menu.addAction("Eliminar página")

        action = menu.exec_(self.list_widget.mapToGlobal(pos))
        
        if action == rotate_right:
            self.rotate_item(item)
        elif action == delete_page:
            row = self.list_widget.row(item)
            self.list_widget.takeItem(row)

    def rotate_item(self, item):
        data = item.data(Qt.UserRole)
        data["rotation"] = (data["rotation"] + 90) % 360
        
        transform = QTransform().rotate(data["rotation"])
        rotated_pixmap = data["original_pixmap"].transformed(transform, Qt.SmoothTransformation)
        item.setIcon(QIcon(rotated_pixmap))
        item.setData(Qt.UserRole, data)

    def merge_pdfs(self):
        if self.list_widget.count() == 0:
            QMessageBox.warning(self, "Vacío", "Añade al menos un archivo PDF para unificar.")
            return

        save_path, _ = QFileDialog.getSaveFileName(self, "Guardar PDF unificado", "Documento_Unificado.pdf", "PDF (*.pdf)")
        if not save_path:
            return

        try:
            output_doc = fitz.open()
            
            for index in range(self.list_widget.count()):
                item = self.list_widget.item(index)
                data = item.data(Qt.UserRole)
                
                src_doc = fitz.open(data["file"])
                output_doc.insert_pdf(src_doc, from_page=data["page"], to_page=data["page"])
                
                if data["rotation"] != 0:
                    last_page = output_doc[-1]
                    last_page.set_rotation(data["rotation"])
                    
                src_doc.close()

            output_doc.save(save_path)
            output_doc.close()
            
            QMessageBox.information(self, "Éxito", f"PDF unificado guardado correctamente en:\n{save_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error al generar PDF", str(e))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PDFMergerApp()
    window.show()
    sys.exit(app.exec_())
