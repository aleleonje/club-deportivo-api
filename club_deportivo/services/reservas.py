from datetime import datetime

from ..constants import (
    ERROR_CODE_RESERVA_NOT_FOUND,
    ERROR_CODE_TRANSICION_NO_PERMITIDA,
    ESTADO_CONFIRMADA,
    ESTADO_CANCELADA,
    ESTADO_FINALIZADA,
)
from ..utils import construir_error_api
from ..validators.reservas import GMT_3
from .. import db

 
def _formatear_fecha(dt) -> str:
    return dt.strftime('%Y-%m-%dT%H:%M:%S.%f') + '-03:00'
 
 
def construir_reserva_dto(fila: dict) -> dict:
    return {
        'id': fila['id'],
        'id_socio': fila['id_socio'],
        'id_cancha': fila['id_cancha'],
        'fecha_hora_inicio': _formatear_fecha(fila['fecha_hora_inicio']),
        'fecha_hora_fin': _formatear_fecha(fila['fecha_hora_fin']),
        'estado': fila['estado'],
        'precio_hora': fila['precio_hora'],
        'precio_total': fila['precio_total'],
    }
 
  
def listar_reservas(filtros: dict, limit: int, offset: int) -> tuple[list[dict], int]:
    filas = db.obtener_reservas(filtros, limit, offset)
    total = db.contar_reservas(filtros)
 
    return [construir_reserva_dto(f) for f in filas], total
 
 
def crear_reserva(datos: dict) -> dict:
    resultado = db.crear_reserva_atomica(datos['id_socio'], datos['id_cancha'], datos['inicio'], datos['fin'])
 
    if 'error' in resultado:
        code, status, description = resultado['error']
        raise ValueError(construir_error_api(code=code, message=description, description=description), status)

    return construir_reserva_dto(resultado['reserva'])


def _obtener_reserva_o_error(id_reserva: int) -> dict:
    reserva = db.obtener_reserva_por_id(id_reserva)

    if not reserva:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_RESERVA_NOT_FOUND,
            message='Reserva no encontrada',
            description=f"No existe una reserva con id '{id_reserva}'"
        ), 404)

    return reserva


def _error_transicion(description: str) -> ValueError:
    return ValueError(construir_error_api(
        code=ERROR_CODE_TRANSICION_NO_PERMITIDA,
        message='Cambio de estado no permitido',
        description=description
    ), 409)


def buscar_reserva_por_id(id_reserva: int) -> dict:
    return construir_reserva_dto(_obtener_reserva_o_error(id_reserva))


def cambiar_estado_reserva(id_reserva: int, estado_nuevo: str) -> dict:
    """
    Aplica las transiciones de la seccion 3 del enunciado:
      confirmada -> cancelada   solo si el horario de inicio todavia no llego
      confirmada -> finalizada  solo si se alcanzo o supero el horario de fin
      cancelada y finalizada no pueden cambiar a otro estado
    Pedir el estado actual devuelve la reserva sin modificarla.
    """
    reserva = _obtener_reserva_o_error(id_reserva)
    estado_actual = reserva['estado']

    if estado_nuevo == estado_actual:
        return construir_reserva_dto(reserva)

    if estado_actual != ESTADO_CONFIRMADA:
        raise _error_transicion(f"Una reserva {estado_actual} no puede pasar a {estado_nuevo}")

    ahora = datetime.now(GMT_3).replace(tzinfo=None)

    if estado_nuevo == ESTADO_CANCELADA and ahora >= reserva['fecha_hora_inicio']:
        raise _error_transicion('Solo se puede cancelar una reserva cuyo horario de inicio todavia no llego')

    if estado_nuevo == ESTADO_FINALIZADA and ahora < reserva['fecha_hora_fin']:
        raise _error_transicion('Solo se puede finalizar una reserva cuando se alcanzo su horario de fin')

    if not db.actualizar_estado_reserva(id_reserva, estado_actual, estado_nuevo):
        raise _error_transicion('La reserva fue modificada por otra solicitud. Intente nuevamente')

    return construir_reserva_dto(db.obtener_reserva_por_id(id_reserva))
