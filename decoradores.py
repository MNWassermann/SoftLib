from os import (getcwd, 
                path)
from datetime import datetime


dir_path: str = getcwd()
txt_name: str = "log.txt"
txt_path = dir_path + "/" + txt_name
def registro_de_log(funcion):
    def envoltura(self):
        ahora = datetime.now()
        str_a_devolver: str = ("Función " + funcion.__name__ +
                               " ejecutada el " + ahora.strftime("%d/%m/%y") +
                               " a las " + str(ahora.time()) + "\n")
        if not path.exists(txt_path):
            file = open(txt_path, "x")
            file.close()    
        
        file = open(txt_path, "a")
        file.write(str_a_devolver)
        file.close()
        
        return funcion(self)
    
    return envoltura
