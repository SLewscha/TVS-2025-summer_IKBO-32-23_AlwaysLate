# Импортируем модуль системных функций и параметров
import sys
# Импортируем из фреймворка PyQt5 модули, необходимые для создания графического интерфейса приложения
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QPushButton, QTextEdit, QLineEdit
from PyQt5.QtCore import QThread, pyqtSignal
# Импортируем модуль, предоставляющий функционал для работы с сетевыми сокетами
import socket
# Импортируем модуль, необходимый для работы с данными в формате JSON
import json

# Добавленная поточность, понадобившаяся для
# реализации функционала программы на одном устройстве
#####################################
class ReceiverThread(QThread):
    data_received = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, ip, port):
        super().__init__()
        self.ip = ip
        self.port = port
    
    def run(self):
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            sock.bind((self.ip, self.port))
            sock.listen(1)
            sock.settimeout(10)
            
            conn, addr = sock.accept()
            data_json = conn.recv(2048).decode()
            data = json.loads(data_json)
            conn.close()
            sock.close()
            
            self.data_received.emit(data)
            
        except socket.timeout:
            if sock:
                sock.close()
            self.error_occurred.emit("Таймаут ожидания соединения")
        except Exception as e:
            if sock:
                sock.close()
            self.error_occurred.emit(f"Ошибка при получении данных: {str(e)}")
        finally:
            if sock:
                try:
                    sock.close()
                except:
                    pass
#####################################

# Создаем класс ReceiverWindow, наследник QMainWindow
class ReceiverWindow(QMainWindow):
    def __init__(self):
        # Вызываем конструктор родительского класса QMainWindow, от которого наследуется класс ReceiverWindow, тем самым позволяя использовать функционал и свойства, определенные в классе QMainWindow
        super().__init__()

        # Указываем заголовок данного окна
        self.setWindowTitle("Получатель")
        # Указываем размер окна
        self.setFixedSize(350, 400)

        # Создаем экземпляр класса QWidget
        central_widget = QWidget(self)
        # Устанавливаем центральный виджет для данного окна, который будет содержать другие элементы интерфейса
        self.setCentralWidget(central_widget)

        # Создаем экземпляр класса QVBoxLayout
        layout = QVBoxLayout()
        # Выстраиваем элементы внутри центрального виджета данного окна в вертикальном расположении
        central_widget.setLayout(layout)

        # Создаем виджет для текста
        label = QLabel("Окно получателя")
        # Устанавливаем виджет в соответствии с ранее установленным расположением
        layout.addWidget(label)

        # Аналогично предыдущему блоку, но с другим текстом
        label = QLabel("Введите IP-адрес для прослушивания:")
        layout.addWidget(label)

        # Создаем экземпляр класса виджета QLineEdit, предназначенного для ввода строки текста
        self.ip_input = QLineEdit()
        self.ip_input.setText("127.0.0.1")
        layout.addWidget(self.ip_input)

        # Вновь виджет для отображения строки текста
        label = QLabel("Введите порт:")
        layout.addWidget(label)

        # Вновь виджет для ввода строки текста
        self.port_input = QLineEdit()
        self.port_input.setText("12345")
        layout.addWidget(self.port_input)

        # Вновь строка текста
        label = QLabel("Информация о системе:")
        layout.addWidget(label)

        # Создаем экземпляр класса виджета QTextEdit, предназначенного для отображения и редактирования текста
        self.system_info_text = QTextEdit()
        # Устанавливает режим только для чтения
        self.system_info_text.setReadOnly(True)
        layout.addWidget(self.system_info_text)

        # Создаем кнопку с помощью конструктора QPushButton
        self.receive_button = QPushButton("Получить данные")
        # Устанавливаем соединение между сигналом нажатия кнопки и вызовом метода process_data
        self.receive_button.clicked.connect(self.process_data)
        layout.addWidget(self.receive_button)
        
        self.receiver_thread = None

    #Определяем метод, получающий введенные значения IP-адреса и порта, а также вызывающий методы receive_data_from_sender и show_system_info (см. блоки ниже)
    def process_data(self):
        # Создаем переменную, которая сохраняет текст, введенный пользователем в виджет QLineEdit с именем ip_input (соответствует IP-адресу компьютера-получателя)
        receiver_ip = self.ip_input.text()
        try:
        # Создаем переменную, которая сохраняет преобразованный в число текст, введенный пользователем в виджет QLineEdit с именем port_input (соответствует номеру порта)
            receiver_port = int(self.port_input.text()) + 1 #int(self.port_input.text()) Внесенная Ошибка №8
            ##################################################
            self.receive_button.setEnabled(False)
            self.system_info_text.setPlainText(f"Ожидание данных на {receiver_ip}:{receiver_port}...")
            self.receiver_thread = ReceiverThread(receiver_ip, receiver_port)
            self.receiver_thread.data_received.connect(self.show_system_info)
            self.receiver_thread.error_occurred.connect(self.show_error)
            self.receiver_thread.finished.connect(self.on_thread_finished)
            self.receiver_thread.start()
            ##################################################
        except ValueError:
            self.system_info_text.setPlainText("Ошибка: Некорректное значение порта")

    # Определяем метод, выводящий данные на экран
    def show_system_info(self, system_info):
        if "error" in system_info:
            self.system_info_text.setPlainText(system_info["error"])
        else:
        # Преобразуем системную информацию в формат JSON, добавив отступ в 4 пробела
            system_info_str = json.dumps(system_info, indent=4, ensure_ascii=False)
        # Присваиваем переменной system_info_text, являющейся объектом виджета, предназначенного для вывода строк, значение JSON-текста, содержащего системную информацию удаленного компьютера
            self.system_info_text.setPlainText(system_info_str)

    def show_error(self, error_message):
        self.system_info_text.setPlainText(error_message)
        
    def on_thread_finished(self):
        self.receive_button.setEnabled(True)

# Блок, оставленный на случай отдельного тестирования данной программы
if __name__ == "__main__":
    app = QApplication(sys.argv)
    receiver_window = ReceiverWindow()
    receiver_window.show()
    sys.exit(app.exec_())
