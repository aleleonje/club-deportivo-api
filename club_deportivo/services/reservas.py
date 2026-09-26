from ..utils import construir_error_api
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
