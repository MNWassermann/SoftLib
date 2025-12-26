import modelo
from decoradores import registro_de_log
from observador import (Subject, ConcreteObserverA) 
from vista import (
    MainWindow,
    DialogoInsercionDato,
    DialogoBorradoDato,
    DialogoModificacion,
    DialogoTreeview,
    CustomMessageBox,
)
from miRegex import formato_correcto_autor, formato_correcto_editorial
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QStandardItem
import sys



class Controlador:
    def __init__(self) -> None:
        self.app = QApplication(sys.argv)
        self.vista = MainWindow()
        self.db = modelo.baseDeDatos() 
        self.mi_observador = ConcreteObserverA(self.db)
        # BOTONES PAGINA PRINCIPAL

        self.vista.conectar_boton_vender(self.manejar_venta_libro)
        
        self.vista.conectar_boton_adquirir(self.manejar_alta_libro)

        # BOTONES MENU AUTORES
        
        self.vista.conectar_boton_alta(
            self.vista.menu_autor, self.alta_autor
        )
        
        self.vista.conectar_boton_baja(
            self.vista.menu_autor, self.baja_autor
        )
        
        self.vista.conectar_boton_modificaciones(
            self.vista.menu_autor, self.modificacion_autor
        )
        
        self.vista.conectar_boton_consultas(
            self.vista.menu_autor, self.consulta_autor
        )

        # BOTONES MENU EDITORIALES
        self.vista.conectar_boton_alta(
            self.vista.menu_editorial, self.alta_editorial
        )
        
        self.vista.conectar_boton_baja(
            self.vista.menu_editorial, self.baja_editoriales
        )
        
        self.vista.conectar_boton_modificaciones(
            self.vista.menu_editorial, self.modificacion_editoriales
        )
        
        self.vista.conectar_boton_consultas(
            self.vista.menu_editorial, self.consulta_editoriales
        )

        # BOTONES MENU LIBROS
        self.vista.conectar_boton_baja(
            self.vista.menu_libros, self.baja_libro
        )
        
        self.vista.conectar_boton_modificaciones(
            self.vista.menu_libros, self.modificacion_libro
        )
        self.vista.conectar_boton_consultas(
            self.vista.menu_libros, self.consulta_libro
        )


#FUNCIONES DE LIBROS
    @registro_de_log
    def manejar_alta_libro(self):
        """
        Este método controla la adquisición de un libro, exista previamente o no-
        """
        titulo: str = self.vista.input_titulo.text().strip()
        autor: str = self.vista.input_autor.text().strip()
        editorial: str = self.vista.input_editorial.text().strip()
        cantidad_str: str = self.vista.input_cantidad.text().strip()
        print(titulo, autor, editorial, cantidad_str)
        if not (titulo == "" or autor == "" or editorial == "" or cantidad_str == ""):
            cantidad: int = int(cantidad_str)

            existe_autor: bool = self.db.existe_en_tabla("Autores", None, None, autor)
            existe_editorial: bool = self.db.existe_en_tabla(
                "Editoriales", None, editorial, None
            )
            existe_libro: bool = self.db.existe_en_tabla("libros", titulo, editorial, autor)

            if not existe_autor:
                msg = CustomMessageBox("Falta Autor")
                msg.exec()
                print("Hola")
            elif not existe_editorial:
                msg = CustomMessageBox("Falta Editorial")
                msg.exec()
            elif existe_libro:
                self.db.adquirir_libro_existente(titulo, editorial, autor, cantidad)
                msg = CustomMessageBox("Operacion realizada con exito")
                msg.exec()
            else:
                self.db.adquirir_libro_nuevo(titulo, editorial, autor, cantidad)
                msg = CustomMessageBox("Operacion realizada con exito")
                msg.exec()            
        else:
            msg = CustomMessageBox("Error Campo Vacio")
            msg.exec()

    @registro_de_log
    def baja_libro(self) -> None:
        """
        Este método controla el borrado de un libro
        """
        dialogo = DialogoBorradoDato("Libro")
        accion = dialogo.exec()
        titulo, editorial, autor = dialogo.guardar_datos()
        titulo = titulo.strip()
        editorial = editorial.strip()
        autor = autor.strip()
        if (titulo != "") and (editorial != "") and (autor != ""):
            if not self.db.existe_en_tabla("Libros", titulo, editorial, autor):
                msg = CustomMessageBox("Falta Libro")
                msg.exec()
            else:
                # METER ALERTA DE BORRADO DE LIBRO
                self.db.eliminar_libro(titulo, editorial, autor)
                msg = CustomMessageBox("Operacion realizada con exito")
                msg.exec()
        elif not accion == dialogo.DialogCode.Rejected:
            msg = CustomMessageBox("Error Campo Vacio")
            msg.exec()

    @registro_de_log
    def modificacion_libro(self) -> None:
        """
        Este método controla la modificación de un libro
        """
        dialogo = DialogoModificacion("Libro")
        accion = dialogo.exec()
        retorno = dialogo.guardar_datos()
        titulo_actual, editorial_actual, autor_actual = retorno[0]
        titulo_cambio = retorno[1][0]

        if (titulo_actual != "") and (editorial_actual != "") and (autor_actual != ""):
            if not self.db.existe_en_tabla("Libros", titulo_actual, editorial_actual, autor_actual):
                msg = CustomMessageBox("Falta Libro")
                msg.exec()
            else:
                # METER ALERTA DE BORRADO DE LIBRO
                self.db.modificar_libro(
                    titulo_actual, 
                    editorial_actual, 
                    autor_actual,
                    titulo_cambio)
                msg = CustomMessageBox("Operacion realizada con exito")
                msg.exec()
        elif not accion == dialogo.DialogCode.Rejected:
            msg = CustomMessageBox("Error Campo Vacio")
            msg.exec()
    
    @registro_de_log
    def consulta_libro(self):
        """
        Este método controla la consulta de los libros
        """
        dialogo = DialogoTreeview("Libros")
        lista_libros = self.db.obtener_libros().tuples()

        for libro in lista_libros:
            fila_tree = [
                QStandardItem(libro[0]),
                QStandardItem(libro[1]),
                QStandardItem(libro[2]),
                QStandardItem(str(libro[3])),
            ]

            dialogo.model.appendRow(fila_tree)

        dialogo.exec()


#FUNCIONES DE AUTORES
    @registro_de_log
    def alta_autor(self) -> None:
        """
        Este método controla la adición de un autor
        """
        dialogo = DialogoInsercionDato("Autor")
        accion = dialogo.exec()
        nombre = dialogo.guardar_datos()[0].strip()
        if nombre != "" and formato_correcto_autor(nombre):
            if self.db.existe_en_tabla("Autores", None, None, nombre):
                msg = CustomMessageBox("Autor Existe")
                msg.exec()
            else:
                self.db.ingresar_editorial_o_autor("Autores", nombre, None)
                msg = CustomMessageBox("Operacion realizada con exito")
                msg.exec()
        elif not accion == dialogo.DialogCode.Rejected:
            if nombre == "":
                msg = CustomMessageBox("Error Campo Vacio")
                msg.exec()
            else:
                msg = CustomMessageBox("Error De Formato Autor")
                msg.exec()

    @registro_de_log
    def baja_autor(self):
        """
        Este método controla la eliminación de un autor de la base de datos
        """
        dialogo = DialogoBorradoDato("Autor")
        accion = dialogo.exec()
        nombre = dialogo.guardar_datos()[0].strip()
        if nombre != "" and formato_correcto_autor(nombre):
            if not self.db.existe_en_tabla("Autores", None, None, nombre):
                msg = CustomMessageBox("Falta Autor")
                msg.exec()
            else:
                # METER ACÁ UNA ALERTA QUE DIGA QUE SE VAN A BORRAR TOOOOOODOS LOS LIBROS ESCRITOS POR EL AUTOR
                self.db.eliminar_autor(nombre)
                msg = CustomMessageBox("Operacion realizada con exito")
                msg.exec()
        elif not accion == dialogo.DialogCode.Rejected:
            if nombre == "":
                msg = CustomMessageBox("Error Campo Vacio")
                msg.exec()
            else:
                msg = CustomMessageBox("Error De Formato Autor")
                msg.exec()
    
    
    @registro_de_log
    def consulta_autor(self):
        """
        Este método controla la consulta a la tabla Autores
        :returns: None
        """
        dialogo = DialogoTreeview("Autores")
        lista_autores = self.db.obtener_autores().tuples()
        if lista_autores != ():
            for libro in lista_autores:
                fila_tree = [QStandardItem(libro[0])]

                dialogo.model.appendRow(fila_tree)

        dialogo.exec()


    @registro_de_log
    def modificacion_autor(self):
        """
        Este método controla la modificación de un autor
        """
        dialogo = DialogoModificacion("Autor")
        accion = dialogo.exec()
        retorno = dialogo.guardar_datos()
        nombre_actual= retorno[0][0]
        nombre_cambio = retorno[1][0]

        if  (nombre_actual != ""):
            if not self.db.existe_en_tabla("Autores", None, None, nombre_actual):
                msg = CustomMessageBox("Falta Autor")
                msg.exec()
            else:
                self.db.modificar_autor(nombre_actual, 
                                   nombre_cambio)
                msg = CustomMessageBox("Operacion realizada con exito")
                msg.exec()
        elif not accion == dialogo.DialogCode.Rejected:
            msg = CustomMessageBox("Error Campo Vacio")
            msg.exec()

#FUNCIONES DE EDITORIALES

    @registro_de_log
    def alta_editorial(self) -> None:
        """
        Este método controla la adición de una editorial
        """
        dialogo = DialogoInsercionDato("Editorial")
        accion = dialogo.exec()
        nombre, contacto = dialogo.guardar_datos()
        nombre = nombre.strip()
        contacto = contacto.strip()
        if nombre != "" and contacto != "" and formato_correcto_editorial(nombre):
            if self.db.existe_en_tabla("Editoriales", None, nombre, None):
                msg = CustomMessageBox("Editorial Existe")
                msg.exec()
            else:
                self.db.ingresar_editorial_o_autor("Editoriales", nombre, contacto)
                msg = CustomMessageBox("Operacion realizada con exito")
                msg.exec()
        elif not accion == dialogo.DialogCode.Rejected:
            if formato_correcto_editorial(nombre):
                msg = CustomMessageBox("Error De Formato Editorial")
                msg.exec()
            else:
                msg = CustomMessageBox("Error Campo Vacio")
                msg.exec()

    @registro_de_log
    def baja_editoriales(self):
        """
        Este método controla la eliminación de una editorial de la base de datos
        """
        dialogo = DialogoBorradoDato("Editorial")
        accion = dialogo.exec()
        nombre = dialogo.guardar_datos()[0].strip()
        if nombre != "" and formato_correcto_editorial(nombre):
            if not self.db.existe_en_tabla("Editoriales", None, nombre, None):
                msg = CustomMessageBox("Falta Editorial")
                msg.exec()
            else:
                # METER ACÁ UNA ALERTA QUE DIGA QUE SE VAN A BORRAR TOOOOOODOS LOS LIBROS ESCRITOS POR EL AUTOR
                self.db.eliminar_editorial(nombre)
                msg = CustomMessageBox("Operacion realizada con exito")
                msg.exec()
        elif not accion == dialogo.DialogCode.Rejected:
            if nombre == "":
                msg = CustomMessageBox("Error Campo Vacio")
                msg.exec()
            else:
                msg = CustomMessageBox("Error De Formato Editorial")
                msg.exec()

    @registro_de_log
    def consulta_editoriales(self):
        """
        Este método controla la consulta a la tabla Editoriales
        """
        dialogo = DialogoTreeview("Editoriales")
        lista_editoriales = self.db.obtener_editoriales().tuples()
        if lista_editoriales != ():
            for libro in lista_editoriales:
                fila_tree = [QStandardItem(libro[0]), QStandardItem(libro[1])]

                dialogo.model.appendRow(fila_tree)

        dialogo.exec()
    
    @registro_de_log
    def modificacion_editoriales(self):
        """
        Este método controla la modificación de una editorial
        """
        dialogo = DialogoModificacion("Editorial")
        accion = dialogo.exec()
        retorno = dialogo.guardar_datos()
        nombre_actual = retorno[0][0]
        nombre_cambio, contacto_cambio = retorno[1]

        if  (nombre_actual != ""):
            if not self.db.existe_en_tabla("Editoriales", None, nombre_actual, None):
                msg = CustomMessageBox("Falta Editorial")
                msg.exec()
            else:
                self.db.modificar_editorial(nombre_actual, 
                                   nombre_cambio,
                                   contacto_cambio)
                msg = CustomMessageBox("Operacion realizada con exito")
                msg.exec()
        elif not accion == dialogo.DialogCode.Rejected:
            msg = CustomMessageBox("Error Campo Vacio")
            msg.exec()




#FUNCIONES VENTAS
    @registro_de_log
    def manejar_venta_libro(self):
        """
        Este método controla la venta de un libro
        """
        exito: bool = False
        titulo: str = self.vista.input_titulo.text().strip()
        autor: str = self.vista.input_autor.text().strip()
        editorial: str = self.vista.input_editorial.text().strip()
        cantidad_str: str = self.vista.input_cantidad.text().strip()

        if not (titulo == "" or autor == "" or editorial == "" or cantidad_str == ""):
            cantidad: int = int(cantidad_str)

            existe_autor: bool = self.db.existe_en_tabla("Autores", None, None, autor)

            existe_editorial: bool = self.db.existe_en_tabla(
                "Editoriales", None, editorial, None
            )
            existe_libro: bool = self.db.existe_en_tabla("Libros", titulo, editorial, autor)

            if existe_editorial and existe_autor and existe_libro:
                exito: bool = self.db.venta(titulo, editorial, autor, cantidad)
                if exito:
                    msg = CustomMessageBox("Venta realizada")
                    msg.exec()
                else:
                    msg = CustomMessageBox("Venta no realizada")
                    msg.exec()
            else:
                if not existe_autor:
                    msg = CustomMessageBox("Falta Autor db")
                    msg.exec()
                elif not existe_editorial:
                    msg = CustomMessageBox("Falta Editorial db")
                    msg.exec()
                elif not existe_libro:
                    msg = CustomMessageBox("Falta Libro db")
                    msg.exec()

        else:
            msg = CustomMessageBox("Error Campo Vacio")
            msg.exec()



if __name__ == "__main__":
    app_controlador = Controlador()
    app_controlador.vista.show()
    sys.exit(app_controlador.app.exec())
