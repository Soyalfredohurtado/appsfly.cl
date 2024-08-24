""" aca estan las funciones con fecha """
import datetime

fecha_hora_actual = datetime.datetime.now()
fecha_ = fecha_hora_actual.date()
hora_ = fecha_hora_actual.time()
fecha = fecha_.strftime("%d/%m/%Y")
hora = hora_.strftime("%H:%M")


def fecha_actual():
    """ retorna el dia de hoy """
    return fecha


def hora_actual():
    """ retorna la hora de hoy """
    return hora
