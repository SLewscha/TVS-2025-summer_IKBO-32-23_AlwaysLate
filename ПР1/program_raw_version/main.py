# Импортируем модуль системных функций и параметров
import sys
# Импортируем из фреймворка PyQt5 модули, необходимые для создания графического интерфейса приложения
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton
# Импортируем классы окон "Отправителя" и "Получателя"
from sender import SenderWindow
from receiver import ReceiverWindow

# Создаем класс MainWindow, наследник QMainWindow
class MainWindow(QMainWindow):
    def __init__(self):
        # Вызываем конструктор родительского класса QMainWindow, от которого наследуется класс MainWindow, тем самым позволяя использовать функционал и свойства, определенные в классе QMainWindow
        super().__init__()

        # Указываем заголовок главного окна
        self.setWindowTitle("Приложение-сборщик")
        # Указываем размер окна
        self.setFixedSize(400, 100)

        # Создаем экземпляр класса QWidget
        central_widget = QWidget(self)
        # Устанавливаем центральный виджет для главного окна, который будет содержать другие элементы интерфейса
        self.setCentralWidget(central_widget)

        # Создаем экземпляр класса QVBoxLayout
        layout = QVBoxLayout()
        # Выстраиваем элементы внутри центрального виджета в вертикальном расположении
        central_widget.setLayout(layout)

        # Создаем кнопку с помощью конструктора QPushButton
        send_button = QPushButton("Открыть окно отправителя")
        # Устанавливаем соединение между сигналом нажатия кнопки и вызовом метода открытия окна отправителя
        send_button.clicked.connect(self.open_receiver_window) #(self.open_sender_window) Внесенная Ошибка №3
        # Устанавливаем кнопку в соответствии с ранее установленным расположением
        layout.addWidget(send_button)

        # Аналогично предыдущему блоку, но для окна получателя
        receive_button = QPushButton("Открыть окно получателя")
        receive_button.clicked.connect(self.open_sender_window) #(open_receiver_window) Внесенная Ошибка №4
        layout.addWidget(receive_button)

        # Создаем переменные для окон и устанавливаем их значение в None, то есть они еще не созданы
        self.sender_window = None
        self.receiver_window = None

    # Определяем метод создания экземпляра окна отправителя при условии, что оно еще не создано
    def open_sender_window(self):
        if self.sender_window is None:
            self.sender_window = SenderWindow()
            # Начало изменений
            ##########################
            self.sender_window.destroyed.connect(lambda: setattr(self, 'sender_window', None))
            ##########################
            # Конец изменений
        # Команда отображения окна на экране
        self.sender_window.show()

    # Аналогично предыдущему блоку, но для окна получателя
    def open_receiver_window(self):
        if self.receiver_window is None:
            self.receiver_window = ReceiverWindow()
            # Начало изменений
            ############################
            self.receiver_window.destroyed.connect(lambda: setattr(self, 'receiver_window', None))
            ############################
            # Конец изменений
        self.receiver_window.show()

# Условие, определяющее, запущен ли модуль как основной скрипт или как часть другой программы
if __name__ == "__main__":
    # Создаем экземпляр класса QApplication, управляющего главным потоком и основными настройками приложения с GUI
    app = QApplication(sys.argv)
    # Создаем экземпляр класса MainWindow, представляющего главное окно приложения и окно выбора функции программы по совместительству
    main_window = MainWindow()
    # Выводим главное окно на экран
    main_window.show()
    # Выполнение главного цикла приложения, который будет ожидать события и обрабатывать пользовательский ввод до тех пор, пока не будет вызвано sys.exit() или главное окно не будет закрыто
    sys.exit(app.exec_())
