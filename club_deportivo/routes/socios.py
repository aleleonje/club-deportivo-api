import logging
from flask import Blueprint, jsonify, request
from ..utils import construir_error_api, validar_parametros_permitidos, ERROR_CODE_INTERNO
from ..validators.socios import validar_id_socio, validar_parametros_listado_socios
from ..services.socios import (
    listar_socios,
    buscar_socio_por_id,
    crear_socio,
    actualizar_socio,
)

logger = logging.getLogger(__name__)

socios_bp = Blueprint('socios', __name__)


@socios_bp.route('/socios', methods=['GET'])
def get_socios():
    try:
        parametros = validar_parametros_listado_socios(request.args)
        respuesta  = listar_socios(parametros, request.base_url)
    except ValueError as e:
        status = e.args[1] if len(e.args) > 1 else 400

        return jsonify(e.args[0]), status

    return jsonify(respuesta), 200


@socios_bp.route('/socios', methods=['POST'])
def post_socio():
    try:
        validar_parametros_permitidos(request.args, [])
        socio = crear_socio(request.get_json(silent=True))
    except ValueError as e:
        status = e.args[1] if len(e.args) > 1 else 400

        return jsonify(e.args[0]), status

    return jsonify(socio), 201, {'Location': f"{request.base_url}/{socio['id']}"}


@socios_bp.route('/socios/<id_socio>', methods=['GET'])
def get_socio(id_socio):
    try:
        validar_parametros_permitidos(request.args, [])
        socio = buscar_socio_por_id(validar_id_socio(id_socio))
    except ValueError as e:
        status = e.args[1] if len(e.args) > 1 else 400

        return jsonify(e.args[0]), status

    return jsonify(socio), 200


@socios_bp.route('/socios/<id_socio>', methods=['PATCH'])
def patch_socio(id_socio):
    try:
        validar_parametros_permitidos(request.args, [])
        socio = actualizar_socio(validar_id_socio(id_socio), request.get_json(silent=True))
    except ValueError as e:
        status = e.args[1] if len(e.args) > 1 else 400

        return jsonify(e.args[0]), status

    return jsonify(socio), 200


@socios_bp.errorhandler(Exception)
def manejar_error_inesperado(error):
    """Responde en JSON cualquier error no previsto de estos endpoints (por ejemplo, si la base no responde)."""
    logger.exception(f'Error inesperado en socios: {error}')

    return jsonify(construir_error_api(
        code=ERROR_CODE_INTERNO,
        message='Error interno del servidor',
        description='Ocurrio un error inesperado al procesar la solicitud'
    )), 500