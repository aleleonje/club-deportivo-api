from flask import Blueprint

canchas_bp = Blueprint('canchas', __name__)

#Endpoints
@canchas_bp.route('/canchas', methods=['GET'])
def canchas():
    return "Endpoint canchas"