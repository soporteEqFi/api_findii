from models.user_model import *
from flask import request

mod_user = userModel()

class userController():

    def post_create_user(self):
        query = mod_user.create_user()
        return query
    
    def get_agent_info(self, cedula):
        query = mod_user.get_agent_info(cedula)
        return query
    
    def get_solicitante_info(self, cedula):
        query = mod_user.get_solicitante_info(cedula)
        return query
    
    def get_user_info(self, cedula):
        query = mod_user.get_user_info(cedula)
        return query
    
    def update_agent(self):
        query = mod_user.update_user()
        return query
    
    def all_users(self):
        # Obtener empresa_id del usuario desde el request
        empresa_id = None
        
        # Opción 1: Si viene en el request (middleware)
        if hasattr(request, 'empresa_id'):
            empresa_id = request.empresa_id
        
        # Opción 2: Si viene en el body JSON
        elif request.json:
            if 'empresa_id' in request.json:
                empresa_id = request.json['empresa_id']
            elif 'cedula' in request.json:
                # Obtener empresa del usuario por cédula
                from models.utils.auth.empresa_middleware import get_user_empresa_id
                empresa_id = get_user_empresa_id(request.json['cedula'])
        
        # Opción 3: Si viene en query params (GET)
        elif request.args.get('cedula'):
            from models.utils.auth.empresa_middleware import get_user_empresa_id
            empresa_id = get_user_empresa_id(request.args.get('cedula'))
        
        print(f"Empresa ID para usuarios: {empresa_id}")
        
        query = mod_user.get_all_users(empresa_id)
        return query
    
    def delete_user(self, id):
        query = mod_user.delete_user(id)
        return query