from datetime import datetime
from re import fullmatch
from urllib.parse import urlencode
import logging
from .constants import (
    ERROR_CODE_INVALID_BODY,
    ERROR_CODE_VALIDACION,
    LIMIT_POR_DEFECTO,
    LIMIT_MINIMO,
    LIMIT_MAXIMO,
    OFFSET_POR_DEFECTO,
)

logger = logging.getLogger(__name__)

OFFSET_MINIMO = 0

# Codigo para errores no previstos, por si la db no responde
ERROR_CODE_INTERNO = 'ERROR_INTERNO'

# Errores

def construir_error_api(code: str, message: str, description: str, level: str = 'error') -> dict:
    """Construye un payload de error compatible con el resto de la API."""
    return {
        'errors': [{
            'code': code,
            'message': message,
            'level': level,
            'description': description,
        }]
    }

# Validaciones de valores sueltos

def validar_entero(numero, nombre: str = 'numero') -> int:
    """Convierte a entero un valor recibido como texto (en la URL o en la query string)."""
    valor = str(numero)

    if not fullmatch(r'-?[0-9]+', valor):
        logger.warning(f"Valor numerico invalido: '{numero}' no puede convertirse a entero")

        raise ValueError(construir_error_api(
            code=ERROR_CODE_VALIDACION,
            message=f"Formato de '{nombre}' invalido",
            description=f"El valor '{numero}' no puede convertirse a un numero entero"
        ))

    return int(valor)


def validar_tipo_entero(valor, nombre: str) -> int:
    """
    Valida que un campo del cuerpo JSON sea un numero entero.
    Rechaza textos ("5"), decimales (5.0) y booleanos (en Python, True es un int).
    """
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise ValueError(construir_error_api(
            code=ERROR_CODE_VALIDACION,
            message=f"Tipo de '{nombre}' invalido",
            description=f"El campo '{nombre}' debe ser un numero entero"
        ))

    return valor


def validar_minimo(valor: int, minimo: int, nombre: str) -> int:
    if valor < minimo:
        logger.warning(f"Valor por debajo del minimo: '{nombre}' es {valor}, minimo esperado {minimo}")

        raise ValueError(construir_error_api(
            code=ERROR_CODE_VALIDACION,
            message='Valor por debajo del minimo permitido',
            description=f"El parametro '{nombre}' debe ser mayor o igual a {minimo}. Se recibio: {valor}"
        ))

    return valor


def validar_maximo(valor: int, maximo: int, nombre: str) -> int:
    if valor > maximo:
        logger.warning(f"Valor por encima del maximo: '{nombre}' es {valor}, maximo esperado {maximo}")

        raise ValueError(construir_error_api(
            code=ERROR_CODE_VALIDACION,
            message='Valor por encima del maximo permitido',
            description=f"El parametro '{nombre}' debe ser menor o igual a {maximo}. Se recibio: {valor}"
        ))

    return valor


def validar_string_no_vacio(valor, nombre: str) -> str:
    """Valida que el valor sea un texto con contenido y lo devuelve sin espacios en los extremos."""
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        raise ValueError(construir_error_api(
            code=ERROR_CODE_VALIDACION,
            message=f"Campo requerido: '{nombre}'",
            description=f"El campo '{nombre}' es obligatorio y no puede estar vacio"
        ))

    if not isinstance(valor, str):
        raise ValueError(construir_error_api(
            code=ERROR_CODE_VALIDACION,
            message=f"Tipo de '{nombre}' invalido",
            description=f"El campo '{nombre}' debe ser un texto"
        ))

    return valor.strip()


def validar_largo_maximo(valor: str, maximo: int, nombre: str) -> str:
    """Valida que un texto no supere la cantidad de caracteres de su columna en la base."""
    if len(valor) > maximo:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_VALIDACION,
            message='Texto demasiado largo',
            description=f"El campo '{nombre}' admite como maximo {maximo} caracteres. Se recibieron: {len(valor)}"
        ))

    return valor


def validar_booleano(valor, nombre: str) -> bool:
    """Valida un booleano del cuerpo JSON: solo admite true o false (sin comillas)."""
    if not isinstance(valor, bool):
        raise ValueError(construir_error_api(
            code=ERROR_CODE_VALIDACION,
            message=f"Tipo de '{nombre}' invalido",
            description=f"El campo '{nombre}' debe ser true o false"
        ))

    return valor


def validar_booleano_query(valor: str, nombre: str) -> bool:
    """Valida un filtro booleano de la query string: solo admite 'true' o 'false'."""
    if valor == 'true':
        return True

    if valor == 'false':
        return False

    raise ValueError(construir_error_api(
        code=ERROR_CODE_VALIDACION,
        message=f"Formato de '{nombre}' invalido",
        description=f"El parametro '{nombre}' solo admite los valores true o false. Se recibio: '{valor}'"
    ))


def validar_formato_fecha(fecha: str, formato: str, nombre: str = 'fecha') -> datetime:
    try:
        return datetime.strptime(fecha, formato)
    except ValueError:
        logger.warning(f"Formato de fecha invalido: '{fecha}' no cumple el formato '{formato}'")

        raise ValueError(construir_error_api(
            code=ERROR_CODE_VALIDACION,
            message=f"Formato de '{nombre}' invalido",
            description=f"El valor '{fecha}' no cumple el formato esperado '{formato}'"
        ))

# Validaciones del cuerpo y de la query string

def validar_body_json(body) -> dict:
    """Valida que el cuerpo de la solicitud sea un objeto JSON."""
    if not isinstance(body, dict):
        raise ValueError(construir_error_api(
            code=ERROR_CODE_INVALID_BODY,
            message='Cuerpo de la solicitud invalido',
            description='El cuerpo debe ser un objeto JSON valido con Content-Type application/json'
        ))

    return body


def validar_body_no_vacio(body: dict) -> dict:
    """Valida que el cuerpo de una actualizacion traiga al menos un campo."""
    if not body:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_VALIDACION,
            message='Cuerpo de la solicitud vacio',
            description='El cuerpo debe incluir al menos un campo para actualizar'
        ))

    return body


def validar_campos_permitidos(body: dict, permitidos: list[str]) -> None:
    """Rechaza los campos del cuerpo que no esten en la lista de permitidos."""
    desconocidos = [campo for campo in body if campo not in permitidos]

    if desconocidos:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_VALIDACION,
            message='Campos desconocidos en el cuerpo',
            description=f"Campos no permitidos: {', '.join(desconocidos)}. Se admiten: {', '.join(permitidos)}"
        ))


def validar_parametros_permitidos(args, permitidos: list[str]) -> None:
    """Rechaza los parametros de la query string desconocidos o enviados mas de una vez."""
    desconocidos = [parametro for parametro in args if parametro not in permitidos]

    if desconocidos:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_VALIDACION,
            message='Parametros desconocidos',
            description=f"Parametros no permitidos: {', '.join(desconocidos)}"
        ))

    repetidos = [parametro for parametro in args if len(args.getlist(parametro)) > 1]

    if repetidos:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_VALIDACION,
            message='Parametros repetidos',
            description=f"Cada parametro puede enviarse una sola vez: {', '.join(repetidos)}"
        ))

# Paginacion


def validar_paginacion(args) -> tuple[int, int]:
    """
    Valida _limit y _offset de la query string.
    Si no vienen, usa los valores por defecto. Retorna (limit, offset).
    """
    errores = []

    limit  = LIMIT_POR_DEFECTO
    offset = OFFSET_POR_DEFECTO

    if '_limit' in args:
        try:
            limit = validar_entero(args.get('_limit'), '_limit')
            limit = validar_minimo(limit, LIMIT_MINIMO, '_limit')
            limit = validar_maximo(limit, LIMIT_MAXIMO, '_limit')
        except ValueError as e:
            errores.extend(e.args[0]['errors'])

    if '_offset' in args:
        try:
            offset = validar_entero(args.get('_offset'), '_offset')
            offset = validar_minimo(offset, OFFSET_MINIMO, '_offset')
        except ValueError as e:
            errores.extend(e.args[0]['errors'])

    if errores:
        raise ValueError({'errors': errores})

    return limit, offset


def construir_link(base_url: str, parametros: dict, limit: int, offset: int) -> dict:
    """Arma un enlace HATEOAS que conserva los filtros aplicados."""
    query = {}

    for nombre, valor in parametros.items():
        if valor is None:
            continue

        if isinstance(valor, bool):
            valor = 'true' if valor else 'false'

        query[nombre] = valor

    query['_limit']  = limit
    query['_offset'] = offset

    return {'href': f'{base_url}?{urlencode(query)}'}


def construir_links_paginacion(base_url: str, parametros: dict,
                               limit: int, offset: int, total: int) -> dict:
    """
    Arma los enlaces _first, _prev, _next y _last de un listado.
    _prev no se incluye en la primera pagina y _next no se incluye en la ultima.
    """
    ultimo_offset = 0

    if total > 0:
        ultimo_offset = ((total - 1) // limit) * limit

    links = {'_first': construir_link(base_url, parametros, limit, 0)}

    if offset > 0:
        links['_prev'] = construir_link(base_url, parametros, limit, max(offset - limit, 0))

    if offset + limit < total:
        links['_next'] = construir_link(base_url, parametros, limit, offset + limit)

    links['_last'] = construir_link(base_url, parametros, limit, ultimo_offset)

    return links


def construir_respuesta_paginada(clave: str, items: list, base_url: str, parametros: dict,
                                 limit: int, offset: int, total: int) -> dict:
    """Arma la respuesta de un listado: los datos bajo una clave descriptiva y los enlaces."""
    return {
        clave:    items,
        '_links': construir_links_paginacion(base_url, parametros, limit, offset, total),
    }
