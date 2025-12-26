import re

patron_nombre_editorial = re.compile("[A-Z]{1}[a-z áéíóú]{1,}")
patron_nombre_autor = re.compile("[A-ZÁÉÍÓÚ][a-záéíóúñ]+(\\s[A-ZÁÉÍÓÚ][a-záéíóúñ]+)+")  


def formato_correcto_autor(nombre: str) -> bool:
    """
    Verifica que el campo de autor tenga el formato correcto.

    :param nombre: Nombre del autor.
    :type nombre: str
    :return: True si cumple con el formato, False en caso contrario.
    :rtype: bool
    """
    res: bool = True
    if re.match(patron_nombre_autor, nombre) is None:
        res = False
    return res


def formato_correcto_editorial(nombre: str) -> bool:
    """
    Verifica que el campo de editorial tenga el formato correcto
    :param nombre: nombre de la editorial
    """
    res: bool = True
    if re.match(patron_nombre_editorial, nombre) is None:
        res = False
    return res
