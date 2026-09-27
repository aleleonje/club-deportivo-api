from re import fullmatch
from ..constants import ERROR_CODE_VALIDACION
from ..utils import (
    construir_error_api,
    validar_entero,
    validar_minimo,
    validar_string_no_vacio,
    validar_largo_maximo,
    validar_booleano,
    validar_booleano_query,
    validar_body_json,
    validar_body_no_vacio,
    validar_campos_permitidos,
    validar_parametros_permitidos,
    validar_paginacion,
)

# Campos y parametros que acepta cada endpoint (el resto se rechaza)
CAMPOS_NUEVO_SOCIO         = ['nombre', 'email']
CAMPOS_ACTUALIZACION_SOCIO = ['nombre', 'email', 'activo']
PARAMETROS_LISTADO_SOCIOS  = ['nombre', 'activo', '_limit', '_offset']

# Los identificadores son enteros positivos
ID_MINIMO = 1

# Largo maximo de las columnas de la tabla socios
MAX_LARGO_NOMBRE = 60
MAX_LARGO_EMAIL  = 80

# texto@dominio.extension, sin espacios
PATRON_EMAIL = r'[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}'


def validar_id_socio(id_raw) -> int:
    """Valida que el id recibido en la URL sea un entero positivo."""
    id_socio = validar_entero(id_raw, 'id')

    return validar_minimo(id_socio, ID_MINIMO, 'id')


def validar_nombre(nombre_raw) -> str:
    """Valida que el nombre sea un texto no vacio. Lo devuelve sin espacios en los extremos."""
    nombre = validar_string_no_vacio(nombre_raw, 'nombre')

    return validar_largo_maximo(nombre, MAX_LARGO_NOMBRE, 'nombre')


def validar_email(email_raw) -> str:
    """Valida el formato del email. Lo devuelve en minusculas y sin espacios en los extremos."""
    email = validar_string_no_vacio(email_raw, 'email').lower()
    email = validar_largo_maximo(email, MAX_LARGO_EMAIL, 'email')

    if not fullmatch(PATRON_EMAIL, email):
        raise ValueError(construir_error_api(
            code=ERROR_CODE_VALIDACION,
            message="Formato de 'email' invalido",
            description=f"El valor '{email}' no es un email valido (ejemplo: nombre@dominio.com)"
        ))

    return email


def validar_body_nuevo_socio(body) -> dict:
    """
    Valida el body del POST /socios.
    Acepta unicamente `nombre` y `email`, ambos obligatorios.
    """
    body = validar_body_json(body)

    errores = []

    nombre = None
    email  = None

    try:
        validar_campos_permitidos(body, CAMPOS_NUEVO_SOCIO)
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    try:
        nombre = validar_nombre(body.get('nombre'))
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    try:
        email = validar_email(body.get('email'))
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    if errores:
        raise ValueError({'errors': errores})

    return {
        'nombre': nombre,
        'email':  email,
    }


def validar_body_actualizacion_socio(body) -> dict:
    """
    Valida el body del PATCH /socios/{id}.
    Acepta `nombre`, `email` y `activo`, todos opcionales, pero al menos uno.
    Retorna solo los campos recibidos, ya validados.
    """
    body = validar_body_json(body)
    validar_body_no_vacio(body)

    errores = []
    cambios = {}

    try:
        validar_campos_permitidos(body, CAMPOS_ACTUALIZACION_SOCIO)
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    if 'nombre' in body:
        try:
            cambios['nombre'] = validar_nombre(body['nombre'])
        except ValueError as e:
            errores.extend(e.args[0]['errors'])

    if 'email' in body:
        try:
            cambios['email'] = validar_email(body['email'])
        except ValueError as e:
            errores.extend(e.args[0]['errors'])

    if 'activo' in body:
        try:
            cambios['activo'] = validar_booleano(body['activo'], 'activo')
        except ValueError as e:
            errores.extend(e.args[0]['errors'])

    if errores:
        raise ValueError({'errors': errores})

    return cambios


def validar_parametros_listado_socios(args) -> dict:
    """
    Valida la query string del GET /socios.
    Filtros opcionales: `nombre` y `activo`. Paginacion: `_limit` y `_offset`.
    """
    errores = []

    nombre = None
    activo = None
    limit  = None
    offset = None

    try:
        validar_parametros_permitidos(args, PARAMETROS_LISTADO_SOCIOS)
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    if 'nombre' in args:
        try:
            nombre = validar_string_no_vacio(args.get('nombre'), 'nombre')
        except ValueError as e:
            errores.extend(e.args[0]['errors'])

    if 'activo' in args:
        try:
            activo = validar_booleano_query(args.get('activo'), 'activo')
        except ValueError as e:
            errores.extend(e.args[0]['errors'])

    try:
        limit, offset = validar_paginacion(args)
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    if errores:
        raise ValueError({'errors': errores})

    return {
        'nombre': nombre,
        'activo': activo,
        'limit':  limit,
        'offset': offset,
    }