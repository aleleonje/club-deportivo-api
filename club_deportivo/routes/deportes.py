import logging
from flask import Blueprint, jsonify, request
from ..utils import construir_error_api, ERROR_CODE_INTERNO
from ..validators.deportes import validar_parametros_listado_deportes
from ..services.deportes import listar_deportes

logger = logging.getLogger(__name__)

deportes_bp = Blueprint('deportes', __name__)


@deportes_bp.route('/deportes', methods=['GET'])
def get_deportes():
    try:
        validar_parametros_listado_deportes(request.args)
        respuesta = listar_deportes()
    except ValueError as e:
        status = e.args[1] if len(e.args) > 1 else 400

        return jsonify(e.args[0]), status

    return jsonify(respuesta), 200


@deportes_bp.errorhandler(Exception)
def manejar_error_inesperado(error):
    """Responde en JSON cualquier error no previsto de este endpoint"""
    logger.exception(f'Error inesperado en deportes: {error}')

    return jsonify(construir_error_api(
        code=ERROR_CODE_INTERNO,
        message='Error interno del servidor',
        description='Ocurrio un error inesperado al procesar la solicitud'
    )), 500