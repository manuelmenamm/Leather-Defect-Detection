from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QTextEdit, QGroupBox, QFormLayout, QFileDialog, QComboBox, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtGui import QPixmap, QImageReader, QWheelEvent
from PyQt5.QtCore import QThread, pyqtSignal, Qt
import sys
from Predictions import predict_defect
from Api_calls import call_openai_api

class ImageViewer(QGraphicsView):
    def __init__(self, parent=None):
        super(ImageViewer, self).__init__(parent)
        self._zoom = 0

    def wheelEvent(self, event: QWheelEvent):
        # Zoom Factor
        zoomInFactor = 1.25
        zoomOutFactor = 1 / zoomInFactor

        # Save the scene pos
        oldPos = self.mapToScene(event.pos())

        # Zoom
        if event.angleDelta().y() < 0:
            zoomFactor = zoomInFactor
            self._zoom += 1
        else:
            if self._zoom > 0:
                zoomFactor = zoomOutFactor
                self._zoom -= 1
            else:
                return  # Ignore the event if we're already zoomed out to the max

        self.scale(zoomFactor, zoomFactor)

        # Get the new position
        newPos = self.mapToScene(event.pos())

        # Move scene to old position
        delta = newPos - oldPos
        self.translate(delta.x(), delta.y())

class PredictThread(QThread):
    result_signal = pyqtSignal(bool, str)

    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path

    def run(self):
        # Call the predict_defect function
        is_defect, defect_type = predict_defect(self.image_path)

        # Emit the result
        self.result_signal.emit(is_defect, defect_type)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Set a stylesheet to change the GUI colors and font
        self.setStyleSheet("""
            QWidget {
                font: 15px;
                background: #333;
                color: #fff;
            }
            QLineEdit, QTextEdit {
                background: #555;
                color: #ddd;
                border: 2px solid #888;
                border-radius: 5px;
            }
            QPushButton {
                background: #06f;
                color: #fff;
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background: #05c;
            }
            QGroupBox {
                font: bold 18px;
                border: 2px solid #aaa;
                border-radius: 5px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)

        # Create a QVBoxLayout instance
        main_layout = QVBoxLayout()

        # Create a QGroupBox instance for the input form
        input_group = QGroupBox("Enter Leather Image")
        input_layout = QFormLayout()

        # Create a QPushButton instance for image selection
        self.select_image_button = QPushButton("Select Image")
        self.select_image_button.clicked.connect(self.select_image)
        input_layout.addRow(QLabel("Image:"), self.select_image_button)

        # Create a ImageViewer instance to display the image
        self.image_view = ImageViewer()
        self.image_scene = QGraphicsScene()
        self.image_view.setScene(self.image_scene)
        input_layout.addRow(self.image_view)

        # Create a QLabel instance to display the status of image upload
        self.image_status = QLabel("")
        input_layout.addRow(self.image_status)

        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)

        # Create a QPushButton instance that calls the OpenAI API when clicked
        button = QPushButton("Evaluate Defect")
        button.clicked.connect(self.get_reply)
        main_layout.addWidget(button)

        # Create a QGroupBox instance for the output
        output_group = QGroupBox("Recommendations")
        output_layout = QVBoxLayout()

        # Create a QTextEdit instance to display the results of the model
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        output_layout.addWidget(QLabel("Prediction:"))
        output_layout.addWidget(self.result_text)

        # Create a QTextEdit instance to display the results of the API call
        self.api_result_text = QTextEdit()
        self.api_result_text.setReadOnly(True)
        output_layout.addWidget(QLabel("AI recommendation:"))
        output_layout.addWidget(self.api_result_text)

        output_group.setLayout(output_layout)
        main_layout.addWidget(output_group)

        # Set the layout on the application's window
        self.setLayout(main_layout)

    def select_image(self):
        # Open a file dialog and get the selected image path
        self.image_path, _ = QFileDialog.getOpenFileName()
        if self.image_path:
            self.image_status.setText("Image uploaded successfully! Press 'Evaluate Defect' to get analysis and recommendations.")
            
            # Clear the previous results
            self.result_text.clear()
            self.api_result_text.clear()

            # Display the image
            pixmap = QPixmap(self.image_path)
            self.image_item = QGraphicsPixmapItem(pixmap)
            self.image_scene.addItem(self.image_item)

            # Fit the image within the view
            self.image_view.fitInView(self.image_scene.itemsBoundingRect(), Qt.KeepAspectRatio)

    def get_reply(self):
        # Create a new thread for prediction
        self.predict_thread = PredictThread(self.image_path)
        self.predict_thread.result_signal.connect(self.display_result)
        self.predict_thread.start()

    def display_result(self, is_defect, defect_type):
        # Convert the boolean to a string and concatenate it with the defect type
        if is_defect:
            result = 'Your leather has a ' + defect_type + ' defect'
        
        else:
            result = 'Your leather is non-defective. Congrats!'

        # Display the results in the QTextEdit
        self.result_text.setText(result)

        if is_defect:
            api_result = call_openai_api(is_defect, defect_type)
            self.api_result_text.setText(api_result)

def create_gui():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    create_gui()