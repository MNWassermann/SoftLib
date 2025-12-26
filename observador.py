from decoradores import txt_path

class Subject:

    observadores = []
    def agregar(self, obj):
        self.observadores.append(obj)
        print(type(obj))

    def quitar(self, obj):
        pass

    def notificar(self, *args):
        for obs in self.observadores:
            print(type(obs))
            obs.update(args)
    

class Observador:
    def update(self, ):
        raise NotImplementedError("Delegacion de actualización")
    

class ConcreteObserverA(Observador):
    def __init__(self, obj):
        self.observador_a = obj
        self.observador_a.agregar(self)

    def update(self, *args):
        params = []
        for i in args:
            for j in i:
                if j is not None:
                    params.append(j)
        str_a_devolver = "Parametros = " + str(params) + "\n"

        file = open(txt_path, "a")
        file.write(str_a_devolver)
        file.close()

