import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QPushButton,
    QFrame,
    QGridLayout,
    QDialog,
    QTextEdit,
)
from PyQt5.QtGui import QFont, QImage, QPixmap, QPainter, QColor
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer
import cv2
import sqlite3
from pyzbar.pyzbar import decode


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.total_data_displayed = 0
        self.max_data_displayed = 5

        self.initUI()
        self.initCamera()
        self.initDatabase()
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.reset_status_label)
        self.current_level = 1
        self.processed_qr_data = []

    def initUI(self):
        self.setWindowTitle("2D AGGREGATION")
        self.setGeometry(100, 100, 1300, 750)

        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)

        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        # Frame 1status
        frame1 = QFrame()
        frame1.setFixedSize(1300, 300)
        frame1.setStyleSheet("border: 0px solid black;")
        frame1_layout = QHBoxLayout()

        # Box 1 di Frame 1 (Kamera)
        frame1_layout1 = QVBoxLayout()
        self.camera_label = QLabel()
        self.camera_label.setFixedSize(250, 230)
        self.camera_label.setStyleSheet("border: 1px solid black;")
        frame1_layout1.addWidget(self.camera_label)

        # Label untuk teks "status scanned"
        self.label_status_scan = QLabel("SCAN STATUS")
        self.label_status_scan.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_status_scan.setFixedSize(250, 50)
        self.label_status_scan.setFont(QFont("Arial", 10, QFont.Bold))
        self.label_status_scan.setStyleSheet("background-color: lightgray; QFont.Bold;")
        frame1_layout1.addWidget(self.label_status_scan)

        frame1_layout.addLayout(frame1_layout1)

        # self.Box2_frame1 di Frame 1
        self.box2_frame1 = QFrame()
        self.box2_frame1.setFixedSize(1020, 280)
        self.box2_frame1.setStyleSheet("border: 1px solid black;")
        frame1_layout.addWidget(self.box2_frame1)

        # vertikal yanga ada di self.box2_frame1
        box2_layout = QVBoxLayout()

        # Label untuk teks "PLEASE SCAN LEVEL 1 (ADD)"
        label_scan_level = QLabel("PLEASE SCAN LEVEL 1 (ADD)")
        label_scan_level.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        label_scan_level.setFixedSize(970, 60)
        label_scan_level.setStyleSheet(
            "border: 0px solid black; background-color: yellow;"
        )
        label_scan_level.setFont(QFont("Arial", 15, QFont.Bold))
        box2_layout.addWidget(label_scan_level)  # Tambahkan label ke box1_layout1

        # self.Box1_box2_Frame1 vertikal dengan label di self.Box2_frame1
        self.box1_box2_frame1 = QFrame()
        self.box1_box2_frame1.setFixedSize(1000, 210)
        self.box1_box2_frame1.setStyleSheet(
            "border: 0px solid black;margin: 0px; padding: 0px;"
        )
        box2_layout.addWidget(self.box1_box2_frame1)

        # Horizontal yang ada di box1_box2_frame1
        box2_layout1 = QHBoxLayout()

        # self.Box1_box12_frame1 vertikal dengan label di self.Box2_frame1
        self.box1_box12_frame1 = QFrame()
        self.box1_box12_frame1.setFixedSize(770, 190)
        self.box1_box12_frame1.setStyleSheet(
            "border: 0px solid black; margin: 0px; padding: 0px;"
        )
        box2_layout1.addWidget(self.box1_box12_frame1)

        # vertikal yang ada di box1_box12_frame1
        box2_layout2 = QVBoxLayout()

        # Label untuk teks "SCAN SUMMARY"
        label_scan_summary = QLabel("SCAN SUMMARY")
        label_scan_summary.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        label_scan_summary.setFixedSize(750, 50)
        label_scan_summary.setStyleSheet(
            "border: 0px solid black; background-color: yellow; margin: 0px;"
        )
        label_scan_summary.setFont(QFont("Arial", 15, QFont.Bold))
        box2_layout2.addWidget(label_scan_summary)

        # Frame untuk grid layout
        grid_frame = QFrame()
        grid_frame.setFixedSize(750, 100)
        grid_frame.setStyleSheet("border: 1px solid black;")
        main_layout.addWidget(grid_frame)

        # Grid layout di dalam frame
        grid_layout = QGridLayout()
        grid_layout.setSpacing(0)  # Menghapus jarak antar sel

        # Box 1 (TOTAL LEVEL1)
        box1_grid = QLabel("TOTAL LEVEL1")
        box1_grid.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        box1_grid.setStyleSheet(
            "border: 1px solid black; background-color: lightyellow; margin: 0px; padding: 0px;"
        )
        box1_grid.setFont(QFont("Arial", 13, QFont.Bold))
        grid_layout.addWidget(box1_grid, 0, 0, 1, 1)  # Baris 0, Kolom 0

        # Box 2 (TOTAL LEVEL2)
        box2_grid = QLabel("TOTAL LEVEL2")
        box2_grid.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        box2_grid.setStyleSheet(
            "border: 1px solid black; background-color: lightyellow; margin: 0px; padding: 0px;"
        )
        box2_grid.setFont(QFont("Arial", 13, QFont.Bold))
        grid_layout.addWidget(box2_grid, 0, 1, 1, 1)  # Baris 0, Kolom 1

        # Box 3
        self.box3_grid = QLabel("0")
        self.box3_grid.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.box3_grid.setStyleSheet(
            "border: 1px solid black; background-color : lightgreen; margin: 0px; padding: 0px;"
        )
        self.box3_grid.setFont(QFont("Arial", 15, QFont.Bold))
        grid_layout.addWidget(self.box3_grid, 1, 0, 1, 1)  # Baris 1, Kolom 0

        # Box 4
        box4_grid = QLabel("1")
        box4_grid.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        box4_grid.setStyleSheet(
            "border: 1px solid black;background-color : lightgreen; margin: 0px; padding: 0px;"
        )
        box4_grid.setFont(QFont("Arial", 13, QFont.Bold))
        grid_layout.addWidget(box4_grid, 1, 1, 1, 1)  # Baris 1, Kolom 1

        grid_frame.setLayout(grid_layout)
        main_layout.addWidget(grid_frame)

        self.setLayout(main_layout)

        box2_layout2.addWidget(grid_frame)

        # self.Box2_box12_frame1 vertikal dengan label di self.Box2_frame1
        self.box2_box12_frame1 = QFrame()
        self.box2_box12_frame1.setFixedSize(190, 168)
        self.box2_box12_frame1.setStyleSheet("border: 0px solid black;")
        box2_layout1.addWidget(self.box2_box12_frame1)

        # vertikal yang ada di box2_box12_frame1
        box2_layout3 = QVBoxLayout()

        # self.Box2_box12_frame1 vertikal dengan label di self.Box2_frame1
        self.box12_box12_frame1 = QFrame()
        self.box12_box12_frame1.setFixedSize(170, 100)
        self.box12_box12_frame1.setStyleSheet("border: 0px solid black;")
        box2_layout3.addWidget(self.box12_box12_frame1)

        # Tombol "RESET"
        reset_button = QPushButton("RESET")
        reset_button.setFont(QFont("Arial", 13, QFont.Bold))
        reset_button.setFixedSize(170, 50)
        reset_button.setStyleSheet(
            "QPushButton {border: 1px solid black; border-radius: 5px;} QPushButton:hover {background-color: lightgreen;}"
        )
        reset_button.clicked.connect(
            self.reset_button_clicked
        )  # Menghubungkan dengan metode reset_button_clicked
        box2_layout3.addWidget(reset_button)  # Tambahkan tombol "RESET"
        box2_layout3.addWidget(reset_button)  # Tambahkan label ke box1_layout1

        self.box2_box12_frame1.setLayout(box2_layout3)
        self.box1_box12_frame1.setLayout(box2_layout2)
        self.box1_box2_frame1.setLayout(box2_layout1)
        self.box2_frame1.setLayout(box2_layout)

        frame1.setLayout(frame1_layout)

        # Frame 3
        frame3 = QFrame()
        frame3.setFixedSize(1300, 60)
        frame3.setStyleSheet("border: 0px solid black;")
        frame3_layout = QHBoxLayout(
            frame3
        )  # Gunakan QHBoxLayout untuk label horizontal

        # Label 1 (LEVEL1)
        label1 = QLabel("LEVEL1")
        label1.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        label1.setFont(QFont("Arial", 12, QFont.Bold))
        label1.setStyleSheet(
            "border: 1px solid black; background-color: lightyellow; font-weight: bold;"
        )
        label1.setFixedSize(200, 50)
        frame3_layout.addWidget(label1)  # Tambahkan label1 ke dalam layout

        # Label 2 (LEVEL2)
        label2 = QLabel("LEVEL2")
        label2.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        label2.setFont(QFont("Arial", 12, QFont.Bold))
        label2.setStyleSheet(
            "border: 1px solid black; background-color: lightyellow; font-weight: bold;"
        )
        label2.setFixedSize(200, 50)
        frame3_layout.addWidget(label2)  # Tambahkan label2 ke dalam layout

        # Di dalam metode __init__ Anda dapat menambahkan tombol "Lihat Data" seperti ini:
        self.view_data_button = QPushButton("Lihat Data")
        self.view_data_button.setFont(QFont("Arial", 12, QFont.Bold))
        self.view_data_button.setFixedSize(110, 35)
        self.view_data_button.setStyleSheet(
            "QPushButton {border: 1px solid black; border-radius: 5px;} QPushButton:hover {background-color: lightgreen;}"
        )
        self.view_data_button.clicked.connect(self.view_data_from_database)
        frame3_layout.addWidget(self.view_data_button)

        # Label 3 (LEVEL3)
        label3 = QLabel()
        label3.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        label3.setStyleSheet("border: 0px solid black;")
        label3.setFixedSize(920, 40)
        frame3_layout.addWidget(label3)  # Tambahkan label2 ke dalam layout

        # Frame 2
        frame2 = QFrame()
        frame2.setFixedSize(1300, 300)
        frame2.setStyleSheet("border: 1px solid black;")
        frame2_layout = QHBoxLayout()

        # Box 1 di Frame 2
        box1_frame2 = QFrame()
        box1_frame2.setFixedSize(310, 290)
        box1_frame2.setStyleSheet("border: 0px solid black;")
        box1_layout = QVBoxLayout()

        # Label untuk teks "CURRENT SCANNED"
        label_current_scanned = QLabel("CURRENT SCANNED")
        label_current_scanned.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        label_current_scanned.setFixedSize(300, 40)
        label_current_scanned.setStyleSheet(
            "border: 1px solid black; background-color: lightyellow;"
        )
        label_current_scanned.setFont(QFont("Arial", 13, QFont.Bold))

        # Box 1 di box1_Frame 2
        self.box11_frame2 = QFrame()
        self.box11_frame2.setFixedSize(300, 180)
        self.box11_frame2.setStyleSheet("border: 1px solid black;")

        # Tombol "ADD" dan "REMOVE" dalam satu baris horizontal
        button_layout = QHBoxLayout()
        # Ganti QPushButton "ADD" menjadi QLabel
        self.add_label = QLabel("ADD")
        self.add_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.add_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.add_label.setFixedSize(110, 35)
        self.add_label.setStyleSheet("border: 1px solid black; border-radius: 5px;")
        # Hapus koneksi untuk menghindari klik
        # self.add_label.clicked.connect(self.add_data_to_database)
        button_layout.addWidget(self.add_label)

        # Ganti QPushButton "REMOVE" menjadi QLabel
        self.remove_label = QLabel("REMOVE")
        self.remove_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.remove_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.remove_label.setFixedSize(110, 35)
        self.remove_label.setStyleSheet("border: 1px solid black; border-radius: 5px;")
        # Hapus koneksi untuk menghindari klik
        # self.remove_label.clicked.connect(self.remove_data_from_database)
        button_layout.addWidget(self.remove_label)

        box1_layout.addWidget(label_current_scanned)
        box1_layout.addWidget(self.box11_frame2)
        box1_layout.addLayout(button_layout)  # Mengganti tombol "ADD" dan "REMOVE"
        box1_frame2.setLayout(box1_layout)  # Mengatur layout box1_frame2

        # Box 2 vertikal
        box2_layout = QVBoxLayout()

        # Box21 di Frame 2
        box21_frame2 = QFrame()
        box21_frame2.setFixedSize(300, 100)
        box21_frame2.setStyleSheet("border: 1px solid black;")

        # Box21_frame2 menggunakan QGridLayout
        box21_layout = QGridLayout()
        box21_layout.setContentsMargins(0, 0, 0, 0)  # Menghapus margin
        box21_layout.setVerticalSpacing(0)  # Menghapus spasi vertikal

        # Label untuk teks "QTY SCANNED" (Row 1)
        label_qty_scanned = QLabel("QTY SCANNED")
        label_qty_scanned.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        label_qty_scanned.setStyleSheet(
            "border: 1px solid black; background-color: lightyellow;"
        )
        label_qty_scanned.setFont(QFont("Arial", 13, QFont.Bold))
        box21_layout.addWidget(
            label_qty_scanned, 0, 0, 1, 1
        )  # Baris 0, Kolom 0, 1 baris, 1 kolom

        # Label untuk teks "total_data_displayed/max_data_displayed" (Row 2)
        self.label_qty_value = QLabel(
            f"{self.total_data_displayed}/{self.max_data_displayed}"
        )
        self.label_qty_value.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_qty_value.setStyleSheet(
            "border: 1px solid black; background-color: lightgreen;"
        )
        self.label_qty_value.setFont(QFont("Arial", 15, QFont.Bold))
        box21_layout.addWidget(
            self.label_qty_value, 1, 0, 1, 1
        )  # Baris 1, Kolom 0, 1 baris, 1 kolom

        box21_frame2.setLayout(box21_layout)  # Terapkan layout ke box21_frame2

        # Box22_Frame2 dibuat vertikal
        box22_frame2 = QFrame()
        box22_frame2.setFixedSize(300, 70)
        box22_frame2.setStyleSheet("border: 0px solid black;")

        # Membuat layout horizontal untuk tombol CLEAR dan CLEAR PARTIAL
        button_layout = QHBoxLayout()

        # Tombol "CLEAR"
        clear_button = QPushButton("CLEAR")
        clear_button.setFont(QFont("Arial", 13, QFont.Bold))
        clear_button.setFixedSize(120, 40)
        clear_button.setStyleSheet(
            "QPushButton {border: 1px solid black; border-radius: 5px;} QPushButton:hover {background-color: lightgreen;}"
        )
        clear_button.clicked.connect(
            self.clear_button_clicked
        )  # Menghubungkan dengan metode clear_button_clicked
        button_layout.addWidget(clear_button)

        # Tombol "CLEAR PARTIAL"
        clear_partial_button = QPushButton("CLOSE PARTIAL")
        clear_partial_button.setFont(QFont("Arial", 13, QFont.Bold))
        clear_partial_button.setFixedSize(150, 40)
        clear_partial_button.setStyleSheet(
            "QPushButton {border: 1px solid black; border-radius: 5px;} QPushButton:hover {background-color: lightgreen;}"
        )
        button_layout.addWidget(clear_partial_button)

        # Terapkan layout horizontal ke box22_frame2
        box22_frame2.setLayout(button_layout)

        # Box23_Frame2 dibuat vertikal
        box23_frame2 = QFrame()
        box23_frame2.setFixedSize(300, 117)
        box23_frame2.setStyleSheet("border: 0px solid black;")

        box2_layout.addWidget(box21_frame2)
        box2_layout.addWidget(box22_frame2)
        box2_layout.addWidget(box23_frame2)

        # Box 3 di Frame 2
        box3_frame2 = QFrame()
        box3_frame2.setFixedSize(650, 300)
        box3_frame2.setStyleSheet("border: 0px solid black;")

        frame2_layout.addWidget(box1_frame2)  # Tambahkan box1_frame2
        frame2_layout.addLayout(box2_layout)
        frame2_layout.addWidget(box3_frame2)  # Tambahkan box3_frame2

        frame2.setLayout(frame2_layout)

        main_layout.addWidget(frame1)
        main_layout.addWidget(frame3)
        main_layout.addWidget(frame2)

    def initCamera(self):
        # Inisialisasi kamera
        self.capture = cv2.VideoCapture(0)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.updateFrame)
        self.timer.start(30)  # Mengupdate frame setiap 30 ms

    def initDatabase(self):
        # Inisialisasi database SQLite
        self.connection = sqlite3.connect("agregation.db")
        self.cursor = self.connection.cursor()
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS qr_codes (
                value_2d TEXT,
                level INTEGER,
                parent TEXT,
                scanned BOOLEAN,
                agg_time DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self.connection.commit()

        # Tambahkan data awal ke dalam database
        initial_data = [
            ("A001", 1),
            ("A002", 1),
            ("A003", 1),
            ("A004", 1),
            ("A005", 1),
            ("B001", 1),
            ("B002", 1),
            ("B003", 1),
            ("B004", 1),
            ("B005", 1),
            ("M001", 1),
            ("M002", 2),
            ("M003", 2),
            ("C001", 1),
        ]

        for data in initial_data:
            self.cursor.execute(
                """
                INSERT INTO qr_codes (value_2d, level, parent, scanned)
                VALUES (?, ?, NULL, 0)
                """,
                data,
            )

        self.connection.commit()

    def add_data_to_database(self):
        # Fungsi ini akan dipanggil ketika tombol "ADD" diklik
        # Ambil data QR code yang terdeteksi terakhir dari database
        self.cursor.execute(
            """
            SELECT value_2d FROM qr_codes WHERE scanned = 0 ORDER BY agg_time DESC LIMIT 1
            """
        )
        qr_data = self.cursor.fetchone()

        if qr_data:
            qr_data = qr_data[0]
            # Tambahkan data QR code ke database
            self.cursor.execute(
                "UPDATE qr_codes SET scanned = 1 WHERE value_2d = ?", (qr_data,)
            )
            self.connection.commit()

            # Tampilkan data QR code di box1_frame2
            self.update_box1_frame2(qr_data)

    def remove_data_from_database(self):
        # Fungsi ini akan dipanggil ketika tombol "REMOVE" diklik
        # Hapus data QR code yang memiliki status scanned = 1
        self.cursor.execute("DELETE FROM qr_codes WHERE scanned = 1")
        self.connection.commit()
        # Bersihkan tampilan di box1_frame2
        self.clear_box1_frame2()

    def check_qr_code_in_database(self, qr_data):
        # Query database untuk memeriksa keberadaan QRCode
        self.cursor.execute(
            "SELECT COUNT(*) FROM qr_codes WHERE value_2d = ? AND level = ?",
            (qr_data, 1),
        )
        count = self.cursor.fetchone()[0]
        return count > 0

    def updateFrame(self):
        # Ambil frame dari kamera
        ret, frame = self.capture.read()

        # Decode QR code (jika ada)
        decoded_objects = decode(frame)
        for obj in decoded_objects:
            qr_data = obj.data.decode("utf-8")

            # Periksa apakah data QRCode ada di database dan sesuai dengan level 1
            if self.check_qr_code_in_database(qr_data):
                # Periksa apakah QR code sudah pernah dipindai sebelumnya
                self.cursor.execute(
                    "SELECT scanned FROM qr_codes WHERE value_2d = ?", (qr_data,)
                )
                scanned = self.cursor.fetchone()[0]

                if not scanned:
                    # Tampilkan data QR code di box11_frame2
                    self.update_box1_frame2(qr_data)

                    # Ubah status scanned di database menjadi TRUE
                    self.cursor.execute(
                        "UPDATE qr_codes SET scanned = 1 WHERE value_2d = ?", (qr_data,)
                    )
                    self.connection.commit()

                # Perbarui label_status_scan menjadi "OK" dengan latar belakang hijau
                self.label_status_scan.setText("OK")
                self.label_status_scan.setStyleSheet(
                    "background-color: lightgreen; QFont.Bold;"
                )
                # Start status_timer untuk mengatur ulang status setelah 5 detik
                self.status_timer.start(1500)  # 1500 ms (3 detik)
            else:
                # Jika data QRCode tidak ada di database atau level tidak sesuai
                # Perbarui label_status_scan menjadi "INVALID" dengan latar belakang merah
                self.label_status_scan.setText("INVALID 2D DATA")
                self.label_status_scan.setStyleSheet(
                    "background-color: red; QFont.Bold;"
                )
                # Start status_timer untuk mengatur ulang status setelah 5 detik
                self.status_timer.start(1500)  # 1500 ms (3 detik)

        # Tampilkan frame kamera di box1_frame1
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(img)
        self.camera_label.setPixmap(pixmap)

    def reset_status_label(self):
        # Atur label_status_scan kembali ke status semula
        self.label_status_scan.setText("SCAN STATUS")
        self.label_status_scan.setStyleSheet("background-color: lightgray; QFont.Bold;")

        # Hentikan status_timer
        self.status_timer.stop()

    def check_qr_code_in_database(self, qr_data):
        # Query database untuk memeriksa keberadaan QRCode
        self.cursor.execute(
            "SELECT COUNT(*) FROM qr_codes WHERE value_2d = ?", (qr_data,)
        )
        count = self.cursor.fetchone()[0]
        return count > 0

    def update_box1_frame2(self, qr_data):
        # Tambahkan data QR code ke dalam list
        self.processed_qr_data.append(qr_data)

        # Buat label untuk data QR code baru
        label_qr_data = QLabel(qr_data)
        label_qr_data.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        label_qr_data.setFixedSize(250, 30)
        label_qr_data.setFont(QFont("Arial", 10))
        label_qr_data.setStyleSheet("background-color: lightgreen;")

        # Cek apakah box11_frame2 memiliki layout, jika tidak, buat layout baru
        if not self.box11_frame2.layout():
            box2_layout = QVBoxLayout()
            self.box11_frame2.setLayout(box2_layout)
        else:
            box2_layout = self.box11_frame2.layout()

        # Tambahkan label ke dalam layout di box11_frame2
        box2_layout.addWidget(label_qr_data)

        # Update angka di box3_grid
        count = len(self.processed_qr_data)
        self.box3_grid.setText(str(count))

        # Update label_qty_value
        self.total_data_displayed = count
        self.update_label_qty_value()

    def clear_box1_frame2(self):
        # Hapus semua widget yang ada di box11_frame2
        for i in reversed(range(self.box11_frame2.layout().count())):
            self.box11_frame2.layout().itemAt(i).widget().deleteLater()

        # Hapus semua data QR code yang telah diproses dari list
        self.processed_qr_data.clear()

        # Update label_qty_value
        self.total_data_displayed = 0
        self.update_label_qty_value()

    def update_label_qty_value(self):
        # Update label_qty_value dengan format "total_data_displayed/max_data_displayed"
        qty_text = f"{self.total_data_displayed}/{self.max_data_displayed}"
        self.label_qty_value.setText(qty_text)

    def clear_last_data(self):
        if self.processed_qr_data:
            # Hapus data QR code terakhir dari list
            last_data = self.processed_qr_data.pop()

            # Hapus widget label QR code terakhir dari box11_frame2
            last_label = (
                self.box11_frame2.layout()
                .itemAt(self.box11_frame2.layout().count() - 1)
                .widget()
            )
            last_label.deleteLater()

            # Update angka di box3_grid
            count = len(self.processed_qr_data)
            self.box3_grid.setText(str(count))

            # Update label_qty_value
            self.total_data_displayed = count
            self.update_label_qty_value()

    def clear_button_clicked(self):
        if self.processed_qr_data:
            # Hapus data QR code terakhir dari list
            last_data = self.processed_qr_data.pop()

            # Hapus widget label QR code terakhir dari box11_frame2
            last_label = (
                self.box11_frame2.layout()
                .itemAt(self.box11_frame2.layout().count() - 1)
                .widget()
            )
            last_label.deleteLater()

            # Update angka di box3_grid
            count = len(self.processed_qr_data)
            self.box3_grid.setText(str(count))

            # Update label_qty_value
            self.total_data_displayed = count
            self.update_label_qty_value()

            # Hapus data terakhir dari database
            self.cursor.execute("DELETE FROM qr_codes WHERE value_2d = ?", (last_data,))
            self.connection.commit()

    def reset_button_clicked(self):
        # Reset the 'scanned', 'parent', and 'agg_time' fields to their initial state
        self.cursor.execute(
            "UPDATE qr_codes SET scanned = 0, parent = NULL, agg_time = NULL"
        )
        self.connection.commit()

        # Clear the display in box1_frame2
        self.clear_box1_frame2()

        # Reset the label in box3_grid to 0
        self.box3_grid.setText("0")

    def view_data_from_database(self):
        # Membuat jendela dialog untuk menampilkan data
        dialog = QDialog(self)
        dialog.setWindowTitle("Data dari Database")
        dialog.setGeometry(200, 200, 800, 400)

        # Membuat tampilan data dari database
        data_text = QTextEdit(dialog)
        data_text.setGeometry(10, 10, 780, 340)

        # Mengambil data dari database
        self.cursor.execute("SELECT * FROM qr_codes")
        data = self.cursor.fetchall()

        # Menampilkan data dalam QTextEdit
        data_text.setPlainText("\n".join([str(row) for row in data]))

        # Menampilkan dialog
        dialog.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mywindow = MyWindow()
    mywindow.show()
    sys.exit(app.exec_())
