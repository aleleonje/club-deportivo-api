from datetime import datetime, timedelta, timezone

from ..constants import (
    ERROR_CODE_VALIDACION,
    HORA_APERTURA,
    HORA_CIERRE,
    DURACION_MINIMA_HORAS,
    DURACION_MAXIMA_HORAS,
    LIMIT_POR_DEFECTO,
    LIMIT_MAXIMO,
    LIMIT_MINIMO,
    OFFSET_POR_DEFECTO,
    CAMPOS_CANCHA_REQUERIDOS,
    CAMPOS_CANCHA_OPCIONALES,
    CAMPOS_CANCHA_EDITABLES,
)
from ..utils import construir_error_api

GMT_3 = timezone(timedelta(hours=-3))


# Funciones soporte

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


def _validar_nombre(valor) -> str:
    if not isinstance(valor, str):
        raise _error("El campo 'nombre' debe ser una cadena de texto")

    nombre = valor.strip()

    if not nombre:
        raise _error("El campo 'nombre' no puede quedar vacio")

    return nombre


def _validar_booleano(valor, nombre_campo: str) -> bool:
    if not isinstance(valor, bool):
        raise _error(f"El campo '{nombre_campo}' debe ser true o false")

    return valor


def _validar_campos_desconocidos(body: dict, permitidos: tuple) -> None:
    desconocidos = [campo for campo in body if campo not in permitidos]

    if desconocidos:
        raise _error(f"Campos desconocidos en el cuerpo: {', '.join(sorted(desconocidos))}")


def _parsear_entero_query(args, nombre_param: str) -> int:
    valor = args.get(nombre_param)

    if valor is None or not valor.lstrip('-').isdigit():
        raise _error(f"El parametro '{nombre_param}' debe ser un entero")

    return int(valor)


def _parsear_booleano_query(args, nombre_param: str) -> bool:
    valor = args.get(nombre_param)

    if valor not in ('true', 'false'):
        raise _error(f"El parametro '{nombre_param}' admite unicamente true o false")

    return valor == 'true'



# Identificador y cuerpos

def validar_id_cancha(valor: str) -> int:
    if not str(valor).isdigit() or int(valor) <= 0:
        raise _error(f"El identificador '{valor}' debe ser un entero positivo")

    return int(valor)


def validar_body_cancha(body: dict) -> dict:
    if not isinstance(body, dict):
        raise _error('El cuerpo debe ser un objeto JSON')

    _validar_campos_desconocidos(body, CAMPOS_CANCHA_REQUERIDOS + CAMPOS_CANCHA_OPCIONALES)

    faltantes = [campo for campo in CAMPOS_CANCHA_REQUERIDOS if campo not in body]

    if faltantes:
        raise _error(f"Faltan campos obligatorios: {', '.join(faltantes)}")

    return {
        'nombre': _validar_nombre(body['nombre']),
        'id_deporte': _validar_entero_positivo(body['id_deporte'], 'id_deporte'),
        'precio_hora': _validar_entero_positivo(body['precio_hora'], 'precio_hora'),
        'techada': _validar_booleano(body.get('techada', False), 'techada'),
        'activa': _validar_booleano(body.get('activa', True), 'activa'),
    }


def validar_body_cancha_patch(body: dict) -> dict:
    if not isinstance(body, dict):
        raise _error('El cuerpo debe ser un objeto JSON')

    if not body:
        raise _error('El cuerpo no puede estar vacio en una actualizacion')

    if 'id_deporte' in body:
        raise _error("El campo 'id_deporte' no puede modificarse una vez creada la cancha")

    _validar_campos_desconocidos(body, CAMPOS_CANCHA_EDITABLES)

    datos = {}

    if 'nombre' in body:
        datos['nombre'] = _validar_nombre(body['nombre'])

    if 'precio_hora' in body:
        datos['precio_hora'] = _validar_entero_positivo(body['precio_hora'], 'precio_hora')

    if 'techada' in body:
        datos['techada'] = _validar_booleano(body['techada'], 'techada')

    if 'activa' in body:
        datos['activa'] = _validar_booleano(body['activa'], 'activa')

    return datos


# Query params

def validar_paginacion(args) -> tuple[int, int]:
    limit = LIMIT_POR_DEFECTO
    offset = OFFSET_POR_DEFECTO

    if '_limit' in args:
        limit = _parsear_entero_query(args, '_limit')

        if limit < LIMIT_MINIMO or limit > LIMIT_MAXIMO:
            raise _error(f"El parametro '_limit' debe estar entre {LIMIT_MINIMO} y {LIMIT_MAXIMO}")

    if '_offset' in args:
        offset = _parsear_entero_query(args, '_offset')

        if offset < 0:
            raise _error("El parametro '_offset' debe ser mayor o igual a cero")

    return limit, offset


def validar_filtros_canchas(args) -> tuple[dict, int, int]:
    permitidos = ('id_deporte', 'nombre', 'techada', 'activa', '_limit', '_offset')
    _validar_campos_desconocidos(args, permitidos)

    filtros = {}

    if 'id_deporte' in args:
        filtros['id_deporte'] = _validar_entero_positivo(
            _parsear_entero_query(args, 'id_deporte'), 'id_deporte'
        )

    if 'nombre' in args:
        filtros['nombre'] = _validar_nombre(args.get('nombre'))

    if 'techada' in args:
        filtros['techada'] = _parsear_booleano_query(args, 'techada')

    if 'activa' in args:
        filtros['activa'] = _parsear_booleano_query(args, 'activa')

    limit, offset = validar_paginacion(args)

    return filtros, limit, offset


def _parsear_fecha(valor: str) -> datetime:
    try:
        return datetime.strptime(valor, '%Y-%m-%d')
    except (TypeError, ValueError):
        raise _error("El parametro 'fecha' debe tener formato YYYY-MM-DD")


def _parsear_hora_en_punto(valor: str, nombre_param: str) -> int:
    try:
        hora = datetime.strptime(valor, '%H:%M:%S')
    except (TypeError, ValueError):
        raise _error(f"El parametro '{nombre_param}' debe tener formato HH:MM:SS")

    if hora.minute or hora.second:
        raise _error(f"El parametro '{nombre_param}' debe indicar una hora en punto")

    return hora.hour


def validar_parametros_disponibilidad(args) -> tuple[dict, int, int]:
    permitidos = ('fecha', 'hora_inicio', 'hora_fin', 'id_deporte', 'techada', '_limit', '_offset')
    _validar_campos_desconocidos(args, permitidos)

    faltantes = [param for param in ('fecha', 'hora_inicio', 'hora_fin') if param not in args]

    if faltantes:
        raise _error(f"Faltan parametros obligatorios: {', '.join(faltantes)}")

    fecha = _parsear_fecha(args.get('fecha'))
    hora_inicio = _parsear_hora_en_punto(args.get('hora_inicio'), 'hora_inicio')
    hora_fin = _parsear_hora_en_punto(args.get('hora_fin'), 'hora_fin')

    if hora_inicio >= hora_fin:
        raise _error("'hora_inicio' debe ser anterior a 'hora_fin'")

    duracion = hora_fin - hora_inicio

    if duracion < DURACION_MINIMA_HORAS or duracion > DURACION_MAXIMA_HORAS:
        raise _error(
            f'El intervalo debe durar entre {DURACION_MINIMA_HORAS} y '
            f'{DURACION_MAXIMA_HORAS} horas completas'
        )

    if hora_inicio < HORA_APERTURA or hora_fin > HORA_CIERRE:
        raise _error(
            f'El intervalo debe estar dentro del horario del club '
            f'({HORA_APERTURA:02d}:00:00 a {HORA_CIERRE:02d}:00:00)'
        )

    inicio = fecha.replace(hour=hora_inicio, tzinfo=GMT_3)
    fin = fecha.replace(hour=hora_fin, tzinfo=GMT_3)

    if inicio <= datetime.now(GMT_3):
        raise _error('El intervalo consultado debe comenzar en el futuro')

    filtros: dict = {
        'inicio': inicio.replace(tzinfo=None),
        'fin': fin.replace(tzinfo=None),
    }

    if 'id_deporte' in args:
        filtros['id_deporte'] = _validar_entero_positivo(
            _parsear_entero_query(args, 'id_deporte'), 'id_deporte'
        )

    if 'techada' in args:
        filtros['techada'] = _parsear_booleano_query(args, 'techada')

    limit, offset = validar_paginacion(args)

    return filtros, limit, offset