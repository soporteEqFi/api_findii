from models.modelo_inicio_sesion import *

mod_inicio_sesion = modeloIniciarSesion()

class iniciarSesionControlador():
    
    def inicio_de_sesion(self):
        print("🔍 DEBUG: Ejecutando inicio_de_sesion en controlador")
        # query = mod_inicio_sesion.iniciar_sesion()
        query = mod_inicio_sesion.iniciar_sesion_sin_auth()
        return query