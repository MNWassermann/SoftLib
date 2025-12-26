# ruff: noqa: F403, F405
from peewee import *  
from observador import (Subject)

db = SqliteDatabase("base_libreria.db")


class BaseModel(Model):
    class Meta:
        database = db


class Libros(BaseModel):
    id = AutoField()
    titulo = CharField(unique=False)
    cantidad = IntegerField(unique=False)


class Editoriales(BaseModel):
    id = AutoField()
    nombre = CharField(unique=True)
    contacto = CharField(unique=True)


class Autores(BaseModel):
    id = AutoField()
    nombre = CharField(unique=True)


class Autores_Libros(BaseModel):
    id = AutoField()
    codigo_autor = ForeignKeyField(Autores, backref="libros")
    codigo_libro = ForeignKeyField(Libros, backref="autores_libros")


class Editoriales_Libros(BaseModel):
    id = AutoField()
    codigo_editorial = ForeignKeyField(Editoriales, backref="libros")
    codigo_libro = ForeignKeyField(Libros, backref="editoriales_libros")


try:
    db.connect()
    db.create_tables([Editoriales, Autores, Libros, Autores_Libros, Editoriales_Libros])
    db.close()

except OperationalError:
    print("Error al crear la tabla")

# ACORDATE DE HACER LAS EXCEPCIONES Y TRANSACCIONES PARA LAS CREACIONES, ACTUALIZACIONES Y BORRADOS


class baseDeDatos(Subject):
    def __init__(self) -> None:
        pass

    def existe_en_tabla(
        self,
        tabla: str,
        titulo_ingreso: str | None,
        editorial: str | None,
        autor: str | None,
    ) -> bool:
        """
        Determina si un dato existe en una tabla
        :param tabla: tabla a verificar
        :param titulo_ingreso: titulo del libro a buscar 
        :param editorial: nombre de la editorial a buscar
        :param autor: nombre del autor a buscar
        """

        if tabla == "Editoriales":
            res: bool = (
                Editoriales.select().where(Editoriales.nombre == editorial).exists()
            )
        elif tabla == "Autores":
            res: bool = Autores.select().where(Autores.nombre == autor).exists()
        else:
            res: bool = (
                Libros.select(Libros.id, Libros.cantidad)
                .join(Autores_Libros)
                .join(Autores)
                .switch(Libros)
                .join(Editoriales_Libros)
                .join(Editoriales)
                .where(
                    (Libros.titulo == titulo_ingreso)
                    & (Autores.nombre == autor)
                    & (Editoriales.nombre == editorial)
                )
            ).exists()
            self.notificar(tabla, titulo_ingreso, editorial, autor)
        return res

    def ingresar_editorial_o_autor(
        self, tabla: str, nombre: str, contacto: str | None
    ) -> None:
        """
        Ingresa un dato nuevo a las tablas Autores o Editoriales
        :param tabla: tabla del alta 
        :param editorial: nombre del autor o la editorial a añadir
        :param contacto: contacto de la editorial
        """
        try:
            with db.atomic():
                if tabla == "Autores":
                    Autores.insert(nombre=nombre).execute()
                else:
                    Editoriales.insert(nombre=nombre, contacto=contacto).execute()
                self.notificar(tabla, nombre, contacto)

        except OperationalError as e:
            print("Error en el ingreso:", e)

    def adquirir_libro_nuevo(
        self, titulo_ingreso: str, editorial: str, autor: str, cantidad_ingreso: int
    ) -> None:
        """
        Ingresa un dato nuevo a las tablas AutoresLibros, EditorialesLibros y Libros
        :param titulo_ingreso: titulo del libro 
        :param autores: nombre del autor a añadir
        :param editorial: nombre de la editorial a añadir
        :param cantidad_ingreso: cantidad de libros a adquirir
        """
        id_autor: int = Autores.get(Autores.nombre == autor).id
        id_editorial: int = Editoriales.get(Editoriales.nombre == editorial).id
        try:
            with db.atomic():
                id_libro: int = Libros.create(
                    titulo=titulo_ingreso, cantidad=cantidad_ingreso
                ).id
                Autores_Libros.create(codigo_autor=id_autor, codigo_libro=id_libro)
                Editoriales_Libros.create(
                    codigo_editorial=id_editorial, codigo_libro=id_libro
                )
            self.notificar(titulo_ingreso, editorial, autor, cantidad_ingreso)
        except OperationalError:
            print("Error alta libro nuevo")

    def adquirir_libro_existente(
        self,
        titulo_ingreso: str,
        editorial_ingreso: str,
        autor_ingreso: str,
        cantidad_ingreso: int,
    ) -> None:
        """
        Actualiza la cantidad de libros en forma de adquisición
        :param titulo_ingreso: titulo del libro 
        :param autor_ingreso: nombre del autor del libro
        :param editorial_ingreso: nombre de la editorial del ingreso
        :param cantidad_ingreso: cantidad de libros 
        """
        query = (
            Libros.select(Libros.id, Libros.cantidad)
            .join(Autores_Libros)
            .join(Autores)
            .switch(Libros)
            .join(Editoriales_Libros)
            .join(Editoriales)
            .where(
                (Libros.titulo == titulo_ingreso)
                & (Autores.nombre == autor_ingreso)
                & (Editoriales.nombre == editorial_ingreso)
            )
        )
        libro: Libros  # type hint
        libro = query.get()
        id_libro = libro.id
        cantidad_actual = libro.cantidad
        try:
            with db.atomic():
                Libros.update(
                    {Libros.cantidad: (cantidad_actual + cantidad_ingreso)}
                ).where(Libros.id == id_libro).execute()
                self.notificar(titulo_ingreso, editorial_ingreso, autor_ingreso, cantidad_ingreso)
        except OperationalError as e:
            print("Error con la adquisición de un libro existente: ", e)

    def venta(
        self,
        titulo_ingreso: str,
        editorial_ingreso: str,
        autor_ingreso: str,
        cantidad_venta: int,
    ) -> bool:
        """
        Actualiza la cantidad de libros en forma de venta
        :param titulo_ingreso: titulo del libro 
        :param autor_ingreso: nombre del autor del libro
        :param editorial_ingreso: nombre de la editorial del ingreso
        :param cantidad_ingreso: cantidad de libros 
        """
        venta_realizada: bool = True
        query = (
            Libros.select(Libros.id, Libros.cantidad)
            .join(Autores_Libros)
            .join(Autores)
            .switch(Libros)
            .join(Editoriales_Libros)
            .join(Editoriales)
            .where(
                (Libros.titulo == titulo_ingreso)
                & (Autores.nombre == autor_ingreso)
                & (Editoriales.nombre == editorial_ingreso)
            )
        )
        libro: Libros  # type hint
        libro = query.get()
        id_libro = libro.id
        cantidad_actual = libro.cantidad
        if cantidad_venta > cantidad_actual:
            venta_realizada = False
        else:
            try:
                with db.atomic():
                    Libros.update(
                        {Libros.cantidad: (cantidad_actual - cantidad_venta)}
                    ).where(Libros.id == id_libro).execute()
                    self.notificar(titulo_ingreso, editorial_ingreso, autor_ingreso, cantidad_venta)
            except Exception:
                print("Error en la venta")
        return venta_realizada

    def eliminar_libro(
        self, titulo: str | None, editorial: str | None, autor: str | None
    ) -> None:
        """
        Elimina un dato de la tabla Libros, AutoresLibros y EditorialesLibros
        :param titulo: titulo del libro 
        :param autor: nombre del autor del libro
        :param editorial: nombre de la editorial del libro 
        """
        query_libro = (
            Libros.select(Libros.id, Libros.cantidad)
            .join(Autores_Libros)
            .join(Autores)
            .switch(Libros)
            .join(Editoriales_Libros)
            .join(Editoriales)
            .where(
                (Libros.titulo == titulo)
                & (Autores.nombre == autor)
                & (Editoriales.nombre == editorial)
            )
        )
        query_autor = Autores.select(Autores.id).where(Autores.nombre == autor)
        query_editorial = Editoriales.select(Editoriales.id).where(
            Editoriales.nombre == editorial
        )

        id_libro = query_libro.get().id
        id_autor = query_autor.get().id
        id_editorial = query_editorial.get().id

        try:
            with db.atomic():
                Autores_Libros.delete().where(
                    (Autores_Libros.codigo_autor == id_autor)
                    & (Autores_Libros.codigo_libro == id_libro)
                ).execute()
                Editoriales_Libros.delete().where(
                    (Editoriales_Libros.codigo_editorial == id_editorial)
                    & (Editoriales_Libros.codigo_libro == id_libro)
                ).execute()
                Libros.delete().where(Libros.id == id_libro).execute()
                self.notificar(titulo, editorial, autor)
        except OperationalError as e:
            print("Error en la eliminación de un libro: ", e)

    def eliminar_autor(self, nombre: str) -> None:
        """
        Elimina todas las apariciones de un autor en Autores, AutoresLibros y Libros
        :param nombre: nombre del autor  
        """
        query_autor = Autores.select(Autores.id).where(Autores.nombre == nombre)
        id_autor = query_autor.get().id

        query_libros = Autores_Libros.select(Autores_Libros.id).where(
            Autores_Libros.codigo_autor == id_autor
        )

        for libro in query_libros:
            id_libro = libro.get().id
            try:
                with db.atomic():
                    Libros.delete().where(Libros.id == id_libro).execute()
            except OperationalError as e:
                print("Error borrado libros en autores: ", e)
        try:
            with db.atomic():
                Autores_Libros.delete().where(Autores_Libros.codigo_autor == id_autor).execute()
        except OperationalError as e:
            print("Error borrado relacion libros autores: ", e)

        try:
            with db.atomic():
                Autores.delete().where(Autores.id == id_autor).execute()
        except OperationalError as e:
            print("Error borrado autor en autores : ", e)
        self.notificar(nombre)

    def eliminar_editorial(self, nombre: str) -> None:
        """
        Elimina todas las apariciones de una editorial en Editoriales, EditorialesLibros y Libros
        :param nombre: nombre de la editorial  
        """
        
        query_editorial = Editoriales.select(Editoriales.id).where(
            Editoriales.nombre == nombre
        )
        id_editorial = query_editorial.get().id

        query_libros = Editoriales_Libros.select(Editoriales_Libros.id).where(
            Editoriales_Libros.codigo_editorial == id_editorial
        )

        for libro in query_libros:
            id_libro = libro.get().id
            try:
                with db.atomic():
                    Libros.delete().where(Libros.id == id_libro).execute()
            except OperationalError as e:
                print("Error borrado libros en editoriales: ", e)
        try:
            with db.atomic():
                Editoriales_Libros.delete().where(
                    Editoriales_Libros.codigo_editorial == id_editorial
                ).execute()
        except OperationalError as e:
            print("Error borrado relacion libros editoriales : ", e)

        try:
            with db.atomic():
                Editoriales.delete().where(Editoriales.id == id_editorial).execute()
        except OperationalError as e:
            print("Error borrado editorial en editoriales : ", e)
        self.notificar(nombre)

    def obtener_libros(self):
        """
        Obtiene los datos de la tabla Libros, cada titulo tiene a su autor y a su editorial
        """
        query = (
            Libros.select(
                Libros.titulo, Autores.nombre, Editoriales.nombre, Libros.cantidad
            )
            .join(Autores_Libros)
            .join(Autores)
            .switch(Libros)
            .join(Editoriales_Libros)
            .join(Editoriales)
        )
        return query

    def obtener_autores(self):
        """
        Retorna los nombres de los autores
        """
        return Autores.select(Autores.nombre)

    def obtener_editoriales(self):
        """
        Retorna los nombres de las editoriales
        """
        return Editoriales.select(Editoriales.nombre, Editoriales.contacto)
    
    def modificar_libro(self, 
                    titulo_actual: str, 
                    editorial_actual: str, 
                    autor_actual: str,
                    titulo_cambio: str):
        """
        Modifica el titulo de un libro
        :param titulo_actual: titulo previo al cambio
        :param editorial_actual: editorial del libro
        :param autor_actual: autor del libro
        :param titulo_cambio: titulo a ingresar
        """
        id_libro = (
            Libros.select(Libros.id)
            .join(Autores_Libros)
            .join(Autores)
            .switch(Libros)
            .join(Editoriales_Libros)
            .join(Editoriales)
            .where(
                (Libros.titulo == titulo_actual)
                & (Autores.nombre == autor_actual)
                & (Editoriales.nombre == editorial_actual)
            )
        ).get().id
        try:
            with db.atomic():
                Libros.update({Libros.titulo: titulo_cambio}).where(Libros.id == id_libro).execute()
        except OperationalError:
            print("Error en modificacion de libro")

    def modificar_autor(self,  
                    autor_actual: str,
                    autor_cambio: str):
        """
        Modifica el nombre de un autor
        :param autor_actual: nombre previo al cambio
        :param autor_cambio: nombre a ingresar
        """
        try:
            with db.atomic():
                Autores.update({Autores.nombre: autor_cambio}).where(Autores.nombre == autor_actual).execute()
                print("hola")
        except OperationalError:
            print("Error en modificacion de autor")
        self.notificar(autor_actual, autor_cambio)

    def modificar_editorial(self, 
                    editorial_actual: str, 
                    editorial_cambio: str,
                    contacto_cambio: str):
        """
        Modifica el nombre de una editorial
        :param editorial_actual: nombre previo al cambio
        :param editorial_cambio: nombre a ingresar
        :param contacto_cambio: contacto nuevo
        """
        try:
            with db.atomic():
                if contacto_cambio != "":
                    Editoriales.update({Editoriales.nombre: editorial_cambio,
                                        Editoriales.contacto: contacto_cambio}
                                        ).where(Editoriales.nombre == editorial_actual).execute()
                elif editorial_cambio != "":
                    Editoriales.update({Editoriales.nombre: editorial_cambio}
                                       ).where(Editoriales.contacto == contacto_cambio).execute()
                else: 
                    Editoriales.update({Editoriales.nombre: editorial_cambio}
                                       ).where(Editoriales.nombre == editorial_actual).execute()
    
        except OperationalError:
            print("Error en modificacion de libro")        
        self.notificar(editorial_actual, editorial_cambio, contacto_cambio)
        
