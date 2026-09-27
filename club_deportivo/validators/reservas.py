from datetime import datetime, timezone, timedelta
from re import fullmatch

from ..constants import (
    ERROR_CODE_VALIDACION,
    ESTADOS_RESERVA,
    CAMPOS_FILTRO_RESERVAS,
    HORA_APERTURA,
    HORA_CIERRE,
    DURACION_MINIMA_HORAS,
    DURACION_MAXIMA_HORAS,
    LIMIT_POR_DEFECTO,
    LIMIT_MAXIMO,
    LIMIT_MINIMO,
    OFFSET_POR_DEFECTO,
)
from ..utils import construir_error_api
 
GMT_3 = timezone(timedelta(hours=-3))

# Formato exigido por el enunciado: YYYY-MM-DDTHH:MM:SS.ffffff-03:00 (6 decimales)
PATRON_FECHA_HORA = r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}-03:00'

 
def _error(description: str) -> ValueError:
    return ValueError(construir_error_api(
        code=ERROR_CODE_VALIDACION,
        message='La solicitud es invalida',
        description=description
    ), 400)
 

def _validar_entero_positivo(valor, nombre_campo: str) -> int:
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise _error(f"El campo '{nombre_campo}' debe ser un entero mayor a cero")
    if valor <= 0:
        raise _error(f"El campo '{nombre_campo}' debe ser un entero mayor a cero")
    return valor
 
 
def _parsear_entero_query(args, nombre_param: str) -> int:
    valor = args.get(nombre_param)
    if valor is None or not valor.isdigit() or int(valor) <= 0:
        raise _error(f"El parametro '{nombre_param}' debe ser un entero positivo")
    return int(valor)
 
 
def _validar_campos_desconocidos(datos, permitidos: tuple) -> None:
    desconocidos = [campo for campo in datos if campo not in permitidos]
    if desconocidos:
        raise _error(f"Campos desconocidos: {', '.join(sorted(desconocidos))}")
 
 
def _parsear_fecha(valor: str, nombre_param: str):
    try:
        return datetime.strptime(valor, '%Y-%m-%d').date()
    except (TypeError, ValueError):
        raise _error(f"El parametro '{nombre_param}' debe tener formato YYYY-MM-DD")
 
 
def validar_paginacion(args) -> tuple[int, int]:
    limit, offset = LIMIT_POR_DEFECTO, OFFSET_POR_DEFECTO
 
    if '_limit' in args:
        limit = _parsear_entero_query(args, '_limit')
        if limit < LIMIT_MINIMO or limit > LIMIT_MAXIMO:
            raise _error(f"El parametro '_limit' debe estar entre {LIMIT_MINIMO} y {LIMIT_MAXIMO}")
 
    if '_offset' in args:
        valor = args.get('_offset')
        if not valor.isdigit():
            raise _error("El parametro '_offset' debe ser un entero mayor o igual a cero")
        offset = int(valor)
 
    return limit, offset

 
def validar_filtros_reservas(args) -> tuple[dict, int, int]:
    permitidos = CAMPOS_FILTRO_RESERVAS + ('_limit', '_offset')
    _validar_campos_desconocidos(args, permitidos)
 
    filtros = {}
 
    if 'id_cancha' in args:
        filtros['id_cancha'] = _parsear_entero_query(args, 'id_cancha')
 
    if 'id_socio' in args:
        filtros['id_socio'] = _parsear_entero_query(args, 'id_socio')
 
    if 'estado' in args:
        estado = args.get('estado')
        if estado not in ESTADOS_RESERVA:
            raise _error(f"El parametro 'estado' debe ser uno de: {', '.join(ESTADOS_RESERVA)}")
        filtros['estado'] = estado
 
    if 'fecha_desde' in args:
        filtros['fecha_desde'] = _parsear_fecha(args.get('fecha_desde'), 'fecha_desde')
 
    if 'fecha_hasta' in args:
        filtros['fecha_hasta'] = _parsear_fecha(args.get('fecha_hasta'), 'fecha_hasta')


    if 'fecha_desde' in filtros and 'fecha_hasta' in filtros:
        if filtros['fecha_desde'] > filtros['fecha_hasta']:
            raise _error("'fecha_desde' debe ser menor o igual a 'fecha_hasta'")
 
    limit, offset = validar_paginacion(args)
 
    return filtros, limit, offset
 
 
def validar_body_reserva(body: dict) -> dict:
    if not isinstance(body, dict):
        raise _error('El cuerpo debe ser un objeto JSON')
 
    campos_obligatorios = ('id_socio', 'id_cancha', 'fecha_hora_inicio', 'fecha_hora_fin')
    _validar_campos_desconocidos(body, campos_obligatorios)
 
    faltantes = [c for c in campos_obligatorios if c not in body]
    if faltantes:
        raise _error(f"Faltan campos obligatorios: {', '.join(faltantes)}")
 
    id_socio = _validar_entero_positivo(body['id_socio'], 'id_socio')
    id_cancha = _validar_entero_positivo(body['id_cancha'], 'id_cancha')
    inicio = _parsear_fecha_hora_iso(body['fecha_hora_inicio'], 'fecha_hora_inicio')
    fin = _parsear_fecha_hora_iso(body['fecha_hora_fin'], 'fecha_hora_fin')
 
    _validar_intervalo_reserva(inicio, fin)
 
    return {'id_socio': id_socio, 'id_cancha': id_cancha, 'inicio': inicio, 'fin': fin}
 
 
def _parsear_fecha_hora_iso(valor, nombre_campo):
   
    if not isinstance(valor, str) or not fullmatch(PATRON_FECHA_HORA, valor):
        raise _error(f"El campo '{nombre_campo}' debe tener formato YYYY-MM-DDTHH:MM:SS.ffffff-03:00")
    try:
        return datetime.strptime(valor[:-6], '%Y-%m-%dT%H:%M:%S.%f')
    except ValueError:
        raise _error(f"El campo '{nombre_campo}' debe tener formato YYYY-MM-DDTHH:MM:SS.ffffff-03:00")
 
 
def _validar_intervalo_reserva(inicio, fin) -> None:
    if inicio >= fin:
        raise _error("'fecha_hora_inicio' debe ser anterior a 'fecha_hora_fin'")
    if inicio.date() != fin.date():
        raise _error('La reserva no puede atravesar la medianoche')
    if inicio.minute or inicio.second or inicio.microsecond or fin.minute or fin.second or fin.microsecond:
        raise _error('Los horarios deben ser horas en punto')
    if inicio.hour < HORA_APERTURA or fin.hour > HORA_CIERRE:
        raise _error(f'El intervalo debe estar dentro del horario del club '
                     f'({HORA_APERTURA:02d}:00 a {HORA_CIERRE:02d}:00)')
    horas = (fin - inicio).total_seconds() / 3600
    if not DURACION_MINIMA_HORAS <= horas <= DURACION_MAXIMA_HORAS:
        raise _error(f'La reserva debe durar entre {DURACION_MINIMA_HORAS} y {DURACION_MAXIMA_HORAS} horas')
    if inicio <= datetime.now(GMT_3).replace(tzinfo=None):
        raise _error('La reserva debe comenzar en el futuro')


def validar_id_reserva(valor: str) -> int:
    if not fullmatch(r'[0-9]+', str(valor)) or int(valor) <= 0:
        raise _error(f"El identificador '{valor}' debe ser un entero positivo")

    return int(valor)


def validar_body_estado(body: dict) -> str:
    """Valida el body del PUT /reservas/{id}/estado: {"estado": "cancelada"}."""
    if not isinstance(body, dict):
        raise _error('El cuerpo debe ser un objeto JSON')

    if not body:
        raise _error("El cuerpo no puede estar vacio: debe incluir el campo 'estado'")

    _validar_campos_desconocidos(body, ('estado',))

    if 'estado' not in body:
        raise _error("Falta el campo obligatorio 'estado'")

    estado = body['estado']

    if not isinstance(estado, str) or estado not in ESTADOS_RESERVA:
        raise _error(f"Estado desconocido. Debe ser uno de: {', '.join(ESTADOS_RESERVA)}")

    return estado