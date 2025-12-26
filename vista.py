# ruff: noqa: F403, F405
from PyQt6.QtWidgets import *  # type: ignore
from PyQt6.QtCore import *  # type: ignore
from PyQt6.QtGui import *  # type: ignore


class DialogoInsercionDato(QDialog):
    """
    Diálogo utilizado por el alta de autores o editoriales
    """
    def __init__(self, campo: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Agregar " + campo)
        self.esEditorial: bool = False

        layout = QVBoxLayout()

        self.input_nombre = QLineEdit(self)

        boton_guardar = BotonPersonalizado("Guardar " + campo)
        boton_guardar.clicked.connect(self.accept)

        layout.addWidget(EtiquetasCustom(campo))
        layout.addWidget(self.input_nombre)
        if campo == "Editorial":
            self.input_contacto = QLineEdit(self)
            layout.addWidget(EtiquetasCustom("Contacto"))
            layout.addWidget(self.input_contacto)
            self.esEditorial = True
        layout.addWidget(boton_guardar)

        self.setLayout(layout)

    def guardar_datos(self) -> tuple[str, str]:
        nombre = self.input_nombre.text().strip()
        contacto = ""
        if self.esEditorial:
            contacto = self.input_contacto.text().strip()
        return (nombre, contacto)


class DialogoBorradoDato(QDialog):
    """
    Diálogo utilizado por la baja de libros, autores o editoriales
    """
    def __init__(self, campo: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Borrar " + campo)
        self.esLibro: bool = False

        layout = QVBoxLayout()

        self.input_nombre = QLineEdit(self)

        boton_guardar = BotonPersonalizado("Borrar " + campo)
        boton_guardar.clicked.connect(self.accept)

        layout.addWidget(EtiquetasCustom(campo))
        layout.addWidget(self.input_nombre)
        if campo == "Libro":
            self.input_editorial = QLineEdit(self)
            self.input_autor = QLineEdit(self)
            layout.addWidget(EtiquetasCustom("Editorial"))
            layout.addWidget(self.input_editorial)
            layout.addWidget(EtiquetasCustom("Autor"))
            layout.addWidget(self.input_autor)
            self.esLibro = True
        layout.addWidget(boton_guardar)

        self.setLayout(layout)

    def guardar_datos(self) -> tuple[str, str, str]:
        """
        Almacena los datos en una terna
        """
        nombre = self.input_nombre.text().strip()
        editorial, autor = "", ""
        if self.esLibro:
            editorial = self.input_editorial.text().strip()
            autor = self.input_autor.text().strip()
        return (nombre, editorial, autor)


class DialogoModificacion(QDialog):
    """
    Diálogo utilizado por la modificación de autores, libros o editoriales
    """
    def __init__(self, campo: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Modificar " + campo)
        self.esLibro: bool = False
        self.esEditorial: bool = False

        layout = QHBoxLayout()
        actual_layout = QVBoxLayout()
        cambio_layout = QVBoxLayout()
        boton_layout = QVBoxLayout()

        self.input_nombre_actual = QLineEdit(self)
        self.input_nombre_cambio = QLineEdit(self)

        boton_guardar_cambios = BotonPersonalizado("Modificar " + campo)
        boton_guardar_cambios.clicked.connect(self.accept)


        cambio_layout.addWidget(EtiquetasCustom(campo + " nuevo/a"))
        cambio_layout.addWidget(self.input_nombre_cambio)
        
        actual_layout.addWidget(EtiquetasCustom(campo + " actual"))
        actual_layout.addWidget(self.input_nombre_actual)
        if campo == "Libro":
            self.input_editorial_actual = QLineEdit(self)
            self.input_autor_actual = QLineEdit(self)
            actual_layout.addWidget(EtiquetasCustom("Editorial actual"))
            actual_layout.addWidget(self.input_editorial_actual)
            actual_layout.addWidget(EtiquetasCustom("Autor actual"))
            actual_layout.addWidget(self.input_autor_actual)

            cambio_layout.addStretch(10)

            self.esLibro = True
        elif campo == "Editorial":
            self.input_contacto_cambio = QLineEdit(self)
            cambio_layout.addWidget(EtiquetasCustom("Contacto nuevo"))
            cambio_layout.addWidget(self.input_contacto_cambio)
            actual_layout.addStretch(10)


            self.esEditorial = True
        boton_layout.addWidget(boton_guardar_cambios)

        layout.addLayout(actual_layout)
        layout.addLayout(cambio_layout)
        layout.addLayout(boton_layout)

        self.setLayout(layout)

    def guardar_datos(self) -> list[tuple]:
        """
        Almacena los datos en una lista de tuplas
        """
        retorno = []
        nombre_actual = self.input_nombre_actual.text().strip()
        nombre_cambio = self.input_nombre_cambio.text().strip()
        
        editorial_actual, autor_actual, contacto_cambio = "", "", ""

        if self.esLibro:
            editorial_actual = self.input_editorial_actual.text().strip()
            autor_actual = self.input_autor_actual.text().strip()

            retorno.append((nombre_actual, editorial_actual, autor_actual))
            retorno.append((nombre_cambio, contacto_cambio))
        elif self.esEditorial:
            contacto_cambio = self.input_contacto_cambio.text().strip()
            retorno.append((nombre_actual, editorial_actual, autor_actual))
            retorno.append((nombre_cambio, contacto_cambio))
        else:
            retorno.append((nombre_actual, editorial_actual, autor_actual))
            retorno.append((nombre_cambio, contacto_cambio))
        return retorno


class DialogoTreeview(QDialog):
    """
    Diálogo utilizado por la consulta de libros, autores o editoriales
    """
    def __init__(self, campo: str, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Consulta " + campo)

        layout = QVBoxLayout()

        self.tree = QTreeView()

        self.model = QStandardItemModel()
        if campo == "Autores":
            self.model.setHorizontalHeaderLabels(["Autor"])
        elif campo == "Editoriales":
            self.model.setHorizontalHeaderLabels(["Editorial", "Contacto"])
        else:
            self.model.setHorizontalHeaderLabels(
                ["Libro", "Autor", "Editorial", "Cantidad"]
            )
        self.tree.setModel(self.model)
        self.setLayout(layout)
        layout.addWidget(self.tree)


class CustomMessageBox(QMessageBox):
    """
    Pestaña de mensaje con distintos temas, dependiendo de la accion o codigo de error
    """
    def __init__(self, campo, parent=None):
        super().__init__(parent)
        if campo == "Error Campo Vacio":
            self.setIcon(QMessageBox.Icon.Critical)
            self.setText(
                "Hay campos vacíos \n Verifique que todos los campos han sido completados antes de Adquirir o Vender un libro"
            )
            self.setWindowTitle("Error")
        elif campo == "Operacion realizada con exito":
            self.setIcon(QMessageBox.Icon.Information)
            self.setText("¡Operación realizada con éxito!")
            self.setWindowTitle("Confirmación alta")
        elif "Falta" in campo:
            self.setWindowTitle("Error venta")
            self.setIcon(QMessageBox.Icon.Critical)
            if "Editorial" in campo:
                self.setText("La editorial no se encuentra registrada en la base")
            if "Libro" in campo:
                self.setText("El libro no se encuentra registrado en la base")
            if "Autor" in campo:
                self.setText("EL autor no se encuentra registrado en la base")
        elif campo == "Venta no realizada":
            self.setIcon(QMessageBox.Icon.Critical)
            self.setText("No hay libros suficientes para realizar esta venta")
            self.setWindowTitle("Error venta")
        elif campo == "Venta realizada":
            self.setIcon(QMessageBox.Icon.Information)
            self.setText("Venta realizada con éxito")
            self.setWindowTitle("Confirmación venta")
        elif campo == "Autor Existe":
            self.setIcon(QMessageBox.Icon.Information)
            self.setText("Este autor ya está registrado en la base")
            self.setWindowTitle("")
        elif campo == "Editorial Existe":
            self.setIcon(QMessageBox.Icon.Information)
            self.setText("Esta editorial ya está registrado en la base")
            self.setWindowTitle("")
        elif "Error De Formato" in campo:
            if "Autor" in campo:
                self.setIcon(QMessageBox.Icon.Information)
            self.setText(
                "Recuerde que los nombres y apellidos comienzan con mayúsculas y se separan con espacios"
            )
            self.setWindowTitle("")
        elif "Editorial" in campo:
            self.setIcon(QMessageBox.Icon.Information)
            self.setText("Recuerde que los nombres propios comienzan con mayúsculas")
            self.setWindowTitle("")


class LayoutHijo(QVBoxLayout):
    """
    Layout secundario de la pestaña principal
    """
    
    def __init__(
        self,
        etiqueta: QLabel,
        campo: QLineEdit | QSpinBox,
        boton: QPushButton | None = None,
    ) -> None:
        super().__init__()
        self.addWidget(etiqueta, alignment=Qt.AlignmentFlag.AlignTop)
        self.addWidget(campo, alignment=Qt.AlignmentFlag.AlignTop)
        self.addStretch(10)
        if boton is not None:
            self.addWidget(boton, alignment=Qt.AlignmentFlag.AlignTop)
            self.addStretch(10)


class MenuAutoresEditoriales(QMenu):
    """
    Caracterización de la pestaña de menú de autores y editoriales
    """
    def __init__(self, titulo: str, parent=None):
        super().__init__(titulo, parent)
        self.accion_alta = QAction("Alta", self)
        self.accion_baja = QAction("Baja", self)
        self.accion_modificaciones = QAction("Modificar", self)
        self.accion_consultas = QAction("Consultar", self)
        self.addActions(
            [
                self.accion_alta,
                self.accion_baja,
                self.accion_modificaciones,
                self.accion_consultas,
            ]
        )


class MenuLibros(QMenu):
    """
    Caracterización de la pestaña de menú de libros
    """
    def __init__(self, titulo: str, parent=None):
        super().__init__(titulo, parent)
        self.accion_baja = QAction("Baja", self)
        self.accion_modificaciones = QAction("Modificar", self)
        self.accion_consultas = QAction("Consultar", self)
        self.addActions(
            [self.accion_baja, self.accion_modificaciones, self.accion_consultas]
        )


class EtiquetasCustom(QLabel):
    """
    Creación de etiquetas para la pestaña principal
    """
    def __init__(self, texto: str) -> None:
        super().__init__(texto)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFont(QFont("Garamond", 10, QFont.Weight.Thin))


class BotonPersonalizado(QPushButton):
    """
    Creación de botones para la pestaña principal
    """
    def __init__(self, texto: str) -> None:
        super().__init__(texto)
        self.setFont(QFont("Garamond", 15, QFont.Weight.DemiBold))


class MainWindow(QMainWindow):
    """
    Pestaña principal
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SoftLib")
        self.resize(1000, 500)
        self.inicializar_widgets()

    def inicializar_widgets(self):
        self.crear_etiquetas()
        self.crear_campos_de_texto()
        self.crear_botones()
        self.organizacion_de_la_pagina()
        self.crear_barra_menu()

    def crear_barra_menu(self):
        barra_menu = QMenuBar(self)
        self.setMenuBar(barra_menu)

        # menu_titulo = CustomMenu("Titulo", self)
        self.menu_autor = MenuAutoresEditoriales("Autor", barra_menu)
        self.menu_editorial = MenuAutoresEditoriales("Editorial", barra_menu)
        self.menu_libros = MenuLibros("Libros", barra_menu)

        # barra_menu.addMenu(menu_titulo)
        barra_menu.addMenu(self.menu_autor)
        barra_menu.addMenu(self.menu_editorial)
        barra_menu.addMenu(self.menu_libros)

    def conectar_boton_alta(self, menu: MenuAutoresEditoriales, slot):
        menu.accion_alta.triggered.connect(slot)

    def conectar_boton_baja(self, menu: MenuAutoresEditoriales | MenuLibros, slot):
        menu.accion_baja.triggered.connect(slot)

    def conectar_boton_consultas(self, menu: MenuAutoresEditoriales | MenuLibros, slot):
        menu.accion_consultas.triggered.connect(slot)

    def conectar_boton_modificaciones(
        self, menu: MenuAutoresEditoriales | MenuLibros, slot
    ):
        menu.accion_modificaciones.triggered.connect(slot)

    def crear_botones(self):
        self.boton_adquirir = BotonPersonalizado("Adquirir \n Libro")
        self.boton_vender = BotonPersonalizado("Vender \n Libro")

    def conectar_boton_adquirir(self, slot):
        self.boton_adquirir.clicked.connect(slot)

    def conectar_boton_vender(self, slot):
        self.boton_vender.clicked.connect(slot)

    def crear_etiquetas(self):
        self.etiqueta_titulo = EtiquetasCustom("Título")
        self.etiqueta_autor = EtiquetasCustom("Autor")
        self.etiqueta_editorial = EtiquetasCustom("Editorial")
        self.etiqueta_cantidad = EtiquetasCustom("Cantidad")

    def crear_campos_de_texto(self):
        self.input_titulo = QLineEdit(self)
        self.input_autor = QLineEdit(self)
        self.input_editorial = QLineEdit(self)
        self.input_cantidad = QLineEdit(self)

    def organizacion_de_la_pagina(self):
        main_layout = QHBoxLayout()
        layout_titulo = LayoutHijo(
            self.etiqueta_titulo,
            self.input_titulo,
        )
        layout_autor = LayoutHijo(
            self.etiqueta_autor, self.input_autor, self.boton_adquirir
        )
        layout_editorial = LayoutHijo(
            self.etiqueta_editorial, self.input_editorial, self.boton_vender
        )
        layout_cantidad = LayoutHijo(self.etiqueta_cantidad, self.input_cantidad)

        main_layout.addLayout(layout_titulo)
        main_layout.addLayout(layout_autor)
        main_layout.addLayout(layout_editorial)
        main_layout.addLayout(layout_cantidad)

        pagina_inicial = QWidget()
        pagina_inicial.setLayout(main_layout)
        self.setCentralWidget(pagina_inicial)
    