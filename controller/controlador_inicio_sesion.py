from model.modelo_inicio_sesion import *

mod_inicio_sesion = modeloIniciarSesion()

class iniciarSesionControlador():
    
    def inicio_de_sesion(self):
        query = mod_inicio_sesion.iniciar_sesion()
        return query

    def user_create(self):
        query = mod_inicio_sesion.crear_usuario()
        return query