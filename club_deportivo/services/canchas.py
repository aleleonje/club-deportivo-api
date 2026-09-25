from ..constants import (
    ERROR_CODE_CANCHA_NOT_FOUND,
    ERROR_CODE_DEPORTE_NOT_FOUND,
    ERROR_CODE_CANCHA_CON_RESERVAS,
)
from ..utils import construir_error_api
from ..validators.canchas import validar_body_cancha, validar_body_cancha_patch
from .. import db


def construir_cancha_dto(cancha: dict) -> dict:
    return {
        'id': cancha['id'],
        'nombre': cancha['nombre'],
        'id_deporte': cancha['id_deporte'],
        'precio_hora': cancha['precio_hora'],
        'techada': bool(cancha['techada']),
        'activa': bool(cancha['activa']),
    }


def _obtener_cancha_o_error(id_cancha: int) -> dict:
    cancha = db.obtener_cancha_por_id(id_cancha)

    if not cancha:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_CANCHA_NOT_FOUND,
            message='Cancha no encontrada',
            description=f"No existe una cancha con id '{id_cancha}'"
        ), 404)

    return cancha


def _validar_deporte_existente(id_deporte: int) -> None:
    if not db.existe_deporte(id_deporte):
        raise ValueError(construir_error_api(
            code=ERROR_CODE_DEPORTE_NOT_FOUND,
            message='Deporte no encontrado',
            description=f"No existe un deporte con id '{id_deporte}'"
        ), 404)


def listar_canchas(filtros: dict, limit: int, offset: int) -> tuple[list[dict], int]:
    canchas = db.obtener_canchas(filtros, limit, offset)
    total = db.contar_canchas(filtros)

    return [construir_cancha_dto(c) for c in canchas], total


def listar_canchas_disponibles(filtros: dict, limit: int, offset: int) -> tuple[list[dict], int]:
    canchas = db.obtener_canchas_disponibles(filtros, limit, offset)
    total = db.contar_canchas_disponibles(filtros)

    return [construir_cancha_dto(c) for c in canchas], total


def buscar_cancha_por_id(id_cancha: int) -> dict:
    cancha = db.obtener_cancha_por_id(id_cancha)

    if not cancha:
        return {}

    return construir_cancha_dto(cancha)


def crear_cancha(body: dict) -> dict:
    datos = validar_body_cancha(body)
    _validar_deporte_existente(datos['id_deporte'])

    nuevo_id = db.insertar_cancha(
        datos['nombre'],
        datos['id_deporte'],
        datos['precio_hora'],
        datos['techada'],
        datos['activa'],
    )

    return construir_cancha_dto(db.obtener_cancha_por_id(nuevo_id))


def actualizar_cancha_parcial(id_cancha: int, body: dict) -> dict:
    _obtener_cancha_o_error(id_cancha)

    datos = validar_body_cancha_patch(body)

    db.actualizar_cancha_parcial(id_cancha, datos)

    return construir_cancha_dto(db.obtener_cancha_por_id(id_cancha))


def eliminar_cancha_por_id(id_cancha: int) -> None:
    _obtener_cancha_o_error(id_cancha)

    if db.cancha_tiene_reservas(id_cancha):
        raise ValueError(construir_error_api(
            code=ERROR_CODE_CANCHA_CON_RESERVAS,
            message='La cancha tiene reservas asociadas',
            description=(
                f"No se puede eliminar la cancha con id '{id_cancha}' porque tiene "
                'reservas asociadas. Puede desactivarse mediante PATCH'
            )
        ), 409)

    db.eliminar_cancha(id_cancha)