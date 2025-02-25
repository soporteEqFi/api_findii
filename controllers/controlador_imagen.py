from models.insertar_imagen import *

modimagen = insertar()

class insertar_imagen_controlador():

    def insertar_imagen(self):
        query = modimagen.insertar_imagen()
        return query