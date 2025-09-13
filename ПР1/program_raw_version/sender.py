# Импортируем модуль системных функций и параметров
import sys
# Импортируем из фреймворка PyQt5 модули, необходимые для создания графического интерфейса приложения
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QPushButton, QLineEdit, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal
# Импортируем модуль, предоставляющий функционал для работы с сетевыми сокетами
import socket
# Импортируем модуль, необходимый для работы с данными в формате JSON
import json
# Импортируем модуль, предоставляющий функционал для взаимодействия с системой через Windows Management Instrumentation
import wmi

# Добавленная поточность, понадобившаяся для
# реализации функционала программы на одном устройстве
############################################
class SenderThread(QThread):
    finished_signal = pyqtSignal(bool, str)
    
    def __init__(self, ip, port, data):
        super().__init__()
        self.ip = ip
        self.port = port
        self.data = data
        
    def run(self):
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((self.ip, self.port))
            data_json = json.dumps(self.data, ensure_ascii=False)
            sock.sendall(data_json.encode())
            self.finished_signal.emit(True, "Данные были успешно отправлены")
        except ConnectionRefusedError:
            self.finished_signal.emit(False, "Соединение отклонено. Убедитесь, что программа-получатель запущена")
        except socket.timeout:
            self.finished_signal.emit(False, "Таймаут соединения")
        except Exception as e:
            self.finished_signal.emit(False, f"Ошибка при отправке данных: {str(e)}")
            
        finally:
            if sock:
                try:
                    sock.close()
                except:
                    pass
############################################

# Создаем класс SenderWindow, наследник QMainWindow
class SenderWindow(QMainWindow):
    def __init__(self):
        # Вызываем конструктор родительского класса QMainWindow, от которого наследуется класс SenderWindow, тем самым позволяя использовать функционал и свойства, определенные в классе QMainWindow
        super().__init__()

        # Указываем заголовок данного окна
        self.setWindowTitle("Отправитель")
        # Указываем размер окна
        self.setFixedSize(350, 200)

        # Создаем экземпляр класса QWidget
        central_widget = QWidget(self)
        # Устанавливаем центральный виджет для данного окна, который будет содержать другие элементы интерфейса
        self.setCentralWidget(central_widget)

        # Создаем экземпляр класса QVBoxLayout
        layout = QVBoxLayout()
        # Выстраиваем элементы внутри центрального виджета данного окна в вертикальном расположении
        central_widget.setLayout(layout)

        # Создаем виджет для текста
        label = QLabel("Окно отправителя")
        # Устанавливаем виджет в соответствии с ранее установленным расположением
        layout.addWidget(label)

        # Аналогично предыдущему блоку, но с другим текстом
        label = QLabel("Введите IP-адрес получателя:")
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

        # Создаем кнопку с помощью конструктора QPushButton
        self.send_button = QPushButton("Отправить")
        # Устанавливаем соединение между сигналом нажатия кнопки и вызовом метода destination (см. блок ниже)
        self.send_button.clicked.connect(self.destination)
        layout.addWidget(self.send_button)
        
        self.sender_thread = None

    # Определяем метод, получающий введенные значения IP-адреса и порта, а также вызывающий метод отправки собранной информации
    def destination(self):
        # Создаем переменную, которая сохраняет текст, введенный пользователем в виджет QLineEdit с именем ip_input (соответствует IP-адресу удаленного компьютера)
        receiver_ip = self.ip_input.text()
        try:
        # Создаем переменную, которая сохраняет преобразованный в число текст, введенный пользователем в виджет QLineEdit с именем port_input (соответствует номеру порта)
            receiver_port = int(self.port_input.text()) + 1 #int(self.port_input.text()) Внесенная Ошибка №7
        # Создаем переменную, в которую сохраняется возвращаемое значение вызванного метода get_system_info
            data = self.get_system_info()
            
            self.send_button.setEnabled(False)
            
            self.sender_thread = SenderThread(receiver_ip, receiver_port, data)
            self.sender_thread.finished_signal.connect(self.on_send_finished)
            self.sender_thread.finished.connect(self.on_thread_finished)
            self.sender_thread.start()
            
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Некорректное значение порта")

    # Определяем метод, собирающий информацию о конфигурации компьютера
    def get_system_info(self):
        try:
        # Создаем экземпляр wmi для доступа к функциям, предоставляемым данным классом
            c = wmi.WMI()

        # Получаем информацию о процессоре с помощью WMI
        # Сперва создаем переменную для сохранения информации о процессоре, затем сохраняем в нее информацию о первом процессоре из списка
            processor_info = c.Win32_Processor()[0]
        # Записываем имя процессора из переменной processor_info
            processor_name = processor_info.Name
        # Записываем архитектуру процессора
            processor_architecture = processor_info.NumberOfCores #Architecture Внесенная Ошибка №1
        # записываем количество ядер процессора
            processor_cores = processor_info.Architecture #NumberOfCores Внесенная Ошибка №2

        # Аналогично предыдущему блоку, но для видеокарты
            gpu_info = c.Win32_VideoController()[0]
            gpu_name = gpu_info.Name
            gpu_resolution = (gpu_info.CurrentHorizontalResolution, gpu_info.CurrentVerticalResolution)
        
        # Аналогично предыдущему блоку, но для ОС
            os_info = c.Win32_OperatingSystem()[0]
            os_name = os_info.Caption
            os_version = os_info.Version

        # Создаем словарь с полученными данными
            system_info = {
                "Processor": {
                    "Name": processor_name,
                    "Architecture": processor_architecture,
                    "Cores": processor_cores
                },
                "OS": {#"GPU": { Внесенная Ошибка №5
                    "Name": gpu_name,
                    "Resolution": gpu_resolution
                },
                "GPU": {#"OS": { Внесенная Ошибка №6
                    "Name": os_name,
                    "Version": os_version
                }
            }

        # Устанавливаем словарь на роль возвращаемого значения
            return system_info
        except Exception as e:
            return {"error": f"Ошибка получения системой информации: {str(e)}"}

    def on_send_finished(self, success, message):
        if success:
            QMessageBox.information(self, "Успех", message)
        else:
            QMessageBox.warning(self, "Ошибка", message)
            
    def on_thread_finished(self):
        self.send_button.setEnabled(True)

# Блок, оставленный на случай отдельного тестирования данной программы
if __name__ == "__main__":
    app = QApplication(sys.argv)
    sender_window = SenderWindow()
    sender_window.show()
    sys.exit(app.exec_())
