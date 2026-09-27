import logging
from flask import Blueprint, jsonify, request

from ..constants import ERROR_CODE_INVALID_BODY
from ..utils import construir_error_api, construir_links_paginacion, ERROR_CODE_INTERNO
from ..validators.reservas import (
    validar_filtros_reservas,
    validar_body_reserva,
    validar_id_reserva,
    validar_body_estado,
)
from ..services import reservas as reservas_service

logger = logging.getLogger(__name__)

reservas_bp = Blueprint('reservas', __name__)
 
 
def _error_body_invalido():
    return jsonify(construir_error_api(
        code=ERROR_CODE_INVALID_BODY,
        message='Cuerpo de la solicitud invalido',
        description='El cuerpo debe ser un JSON valido con Content-Type application/json'
    )), 400
 
 
def _filtros_de_query():
    return {k: v for k, v in request.args.items() if k not in ('_limit', '_offset')}
 
 
@reservas_bp.route('/reservas', methods=['GET'])
def get_reservas():
    try:
        filtros, limit, offset = validar_filtros_reservas(request.args)
    except ValueError as e:
        return jsonify(e.args[0]), 400
 
    reservas, total = reservas_service.listar_reservas(filtros, limit, offset)
 
    return jsonify({
        'reservas': reservas,
        '_links': construir_links_paginacion(request.base_url, _filtros_de_query(), limit, offset, total),
    }), 200
 

@reservas_bp.route('/reservas', methods=['POST'])
def post_reserva():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return _error_body_invalido()
 
    try:
        datos = validar_body_reserva(body)
        reserva = reservas_service.crear_reserva(datos)
    except ValueError as e:
        status = e.args[1] if len(e.args) > 1 else 400
        return jsonify(e.args[0]), status
 
    respuesta = jsonify(reserva)
    respuesta.headers['Location'] = f"{request.base_url}/{reserva['id']}"
    return respuesta, 201


@reservas_bp.route('/reservas/<id>', methods=['GET'])
def get_reserva(id):
    try:
        id_reserva = validar_id_reserva(id)
        reserva = reservas_service.buscar_reserva_por_id(id_reserva)
    except ValueError as e:
        status = e.args[1] if len(e.args) > 1 else 400
        return jsonify(e.args[0]), status

    return jsonify(reserva), 200


@reservas_bp.route('/reservas/<id>/estado', methods=['PUT'])
def put_estado_reserva(id):
    try:
        id_reserva = validar_id_reserva(id)
    except ValueError as e:
        return jsonify(e.args[0]), 400

    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return _error_body_invalido()

    try:
        estado = validar_body_estado(body)
        reserva = reservas_service.cambiar_estado_reserva(id_reserva, estado)
    except ValueError as e:
        status = e.args[1] if len(e.args) > 1 else 400
        return jsonify(e.args[0]), status

    return jsonify(reserva), 200


@reservas_bp.errorhandler(Exception)
def manejar_error_inesperado(error):
    """Responde en JSON cualquier error no previsto de estos endpoints."""
    logger.exception(f'Error inesperado en reservas: {error}')

    return jsonify(construir_error_api(
        code=ERROR_CODE_INTERNO,
        message='Error interno del servidor',
        description='Ocurrio un error inesperado al procesar la solicitud'
    )), 500