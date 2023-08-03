import sys
import mysql.connector
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QFormLayout, QMessageBox, QTableView
from PyQt5.QtCore import QFile, QTextStream

# Configurar la conexión a la base de datos (reemplaza con tus propios datos)
DATABASE = "prueba"
USER = "root"
PASSWORD = ""
HOST = "localhost"
PORT = "3306"

# Función para conectar a la base de datos
def get_db():
    connection = mysql.connector.connect(
        database=DATABASE, user=USER, password=PASSWORD, host=HOST, port=PORT
    )
    return connection

# Función para crear un nuevo usuario con dirección
def create_user(user_data, address_data):
    try:
        # Insertar el usuario en la tabla "user"
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO usser (first_name, last_name, email, CONTRASENA) VALUES (%s, %s, %s, %s)",
                    (
                        user_data["first_name"],
                        user_data["last_name"],
                        user_data["email"],
                        user_data["CONTRASENA"],
                    ),
                )

                # Obtener el ID del usuario recién creado
                user_id = cur.lastrowid

        # Insertar la dirección en la tabla "address" vinculada al usuario
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO address (address1, address2, city, state, zip, country, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (
                        address_data["address1"],
                        address_data["address2"],
                        address_data["city"],
                        address_data["state"],
                        address_data["zip"],
                        address_data["country"],
                        user_id,
                    ),
                )

        return "User and address created successfully!"

    except Exception as e:
        return str(e)

# Función para obtener usuarios por país
def get_users_by_country(country):
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT u.id, u.first_name, u.last_name, u.email, a.address1, a.address2, a.city, a.state, a.zip, a.country FROM usser u INNER JOIN address a ON u.id = a.user_id WHERE a.country = %s",
                    (country,),
                )
                users = cur.fetchall()

        return users

    except Exception as e:
        return []

# Ventana principal de la aplicación
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("User Administration")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.create_user_form = QFormLayout()
        self.user_first_name = QLineEdit()
        self.user_last_name = QLineEdit()
        self.user_email = QLineEdit()
        self.user_CONTRASENA = QLineEdit()
        self.user_CONTRASENA.setEchoMode(QLineEdit.Password)
        self.create_user_form.addRow("First Name:", self.user_first_name)
        self.create_user_form.addRow("Last Name:", self.user_last_name)
        self.create_user_form.addRow("Email:", self.user_email)
        self.create_user_form.addRow("Password:", self.user_CONTRASENA)

        self.create_address_form = QFormLayout()
        self.address_address1 = QLineEdit()
        self.address_address2 = QLineEdit()
        self.address_city = QLineEdit()
        self.address_state = QLineEdit()
        self.address_zip = QLineEdit()
        self.address_country = QLineEdit()
        self.create_address_form.addRow("Address 1:", self.address_address1)
        self.create_address_form.addRow("Address 2:", self.address_address2)
        self.create_address_form.addRow("City:", self.address_city)
        self.create_address_form.addRow("State:", self.address_state)
        self.create_address_form.addRow("ZIP:", self.address_zip)
        self.create_address_form.addRow("Country:", self.address_country)

        self.create_button = QPushButton("Create User")
        self.create_button.clicked.connect(self.create_user)

        self.result_label = QLabel()

        self.layout = QVBoxLayout()
        self.layout.addLayout(self.create_user_form)
        self.layout.addLayout(self.create_address_form)
        self.layout.addWidget(self.create_button)
        self.layout.addWidget(self.result_label)

        self.central_widget.setLayout(self.layout)

        self.set_styles()

    def set_styles(self):
        # Cargar el archivo de estilos CSS
        stylesheet = QFile("style.qss")
        if stylesheet.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(stylesheet)
            self.setStyleSheet(stream.readAll())

    def create_user(self):
        user_data = {
            "first_name": self.user_first_name.text(),
            "last_name": self.user_last_name.text(),
            "email": self.user_email.text(),
            "CONTRASENA": self.user_CONTRASENA.text(),
        }

        address_data = {
            "address1": self.address_address1.text(),
            "address2": self.address_address2.text(),
            "city": self.address_city.text(),
            "state": self.address_state.text(),
            "zip": self.address_zip.text(),
            "country": self.address_country.text(),
        }

        response = create_user(user_data, address_data)

        self.result_label.setText(response)

# Ventana para obtener usuarios por país
class GetUsersWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Get Users by Country")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.country_line_edit = QLineEdit()
        self.get_users_button = QPushButton("Get Users")
        self.get_users_button.clicked.connect(self.get_users)

        self.table_view = QTableView()

        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel("Country:"))
        self.layout.addWidget(self.country_line_edit)
        self.layout.addWidget(self.get_users_button)
        self.layout.addWidget(self.table_view)

        self.central_widget.setLayout(self.layout)

        self.set_styles()

    def set_styles(self):
        # Cargar el archivo de estilos CSS
        stylesheet = QFile("style.qss")
        if stylesheet.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(stylesheet)
            self.setStyleSheet(stream.readAll())

    def get_users(self):
        country = self.country_line_edit.text()
        users = get_users_by_country(country)

        if not users:
            QMessageBox.information(self, "Information", "No users found for the given country.")
        else:
            model = QStandardItemModel(len(users), len(users[0]), self)
            model.setHorizontalHeaderLabels(
                ["ID", "First Name", "Last Name", "Email", "Address1", "Address2", "City", "State", "ZIP", "Country"]
            )

            for row, user in enumerate(users):
                for col, item in enumerate(user):
                    model.setItem(row, col, QStandardItem(str(item)))

            self.table_view.setModel(model)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()

    get_users_window = GetUsersWindow()
    get_users_window.show()

    sys.exit(app.exec_())
