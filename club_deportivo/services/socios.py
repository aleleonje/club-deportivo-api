import logging
from ..utils import construir_error_api, construir_respuesta_paginada
from ..validators.socios import validar_body_nuevo_socio, validar_body_actualizacion_socio
from ..repositories import socios as repositorio_socios

logger = logging.getLogger(__name__)

# Codigos de error propios de socios (mismo formato que los de canchas en constants.py)
ERROR_CODE_SOCIO_NOT_FOUND = 'ERROR_SOCIO_NO_ENCONTRADO'
ERROR_CODE_EMAIL_DUPLICADO = 'ERROR_EMAIL_DUPLICADO'


def construir_socio_dto(socio: dict) -> dict:
    """DTO publico de un socio."""
    return {
        'id':     socio['id'],
        'nombre': socio['nombre'],
        'email':  socio['email'],
        'activo': bool(socio['activo']),
    }


def listar_socios(parametros: dict, base_url: str) -> dict:
    """
    Retorna una pagina de socios filtrada y ordenada por id,
    junto con los enlaces para navegar entre paginas.
    """
    nombre = parametros['nombre']
    activo = parametros['activo']
    limit  = parametros['limit']
    offset = parametros['offset']

    total = repositorio_socios.contar_socios(nombre, activo)

    # Si el offset supera la cantidad de resultados, la pagina queda vacia
    socios = []

    if offset < total:
        filas  = repositorio_socios.obtener_socios(nombre, activo, limit, offset)
        socios = [construir_socio_dto(fila) for fila in filas]

    filtros = {
        'nombre': nombre,
        'activo': activo,
    }

    return construir_respuesta_paginada('socios', socios, base_url, filtros, limit, offset, total)


def buscar_socio_por_id(id_socio: int) -> dict:
    """Retorna el socio con el id dado. Si no existe, lanza un error 404."""
    socio = repositorio_socios.obtener_socio_por_id(id_socio)

    if not socio:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_SOCIO_NOT_FOUND,
            message='Socio no encontrado',
            description=f"No existe un socio con id '{id_socio}'"
        ), 404)

    return construir_socio_dto(socio)


def verificar_email_disponible(email: str, id_socio_actual: int = None) -> None:
    """
    Lanza un error 409 si el email ya pertenece a otro socio, este activo o no.
    Al actualizar, se pasa el id del socio para que su propio email no cuente como repetido.
    """
    existente = repositorio_socios.obtener_socio_por_email(email)

    if existente and existente['id'] != id_socio_actual:
        logger.warning(f"Email duplicado: '{email}' ya pertenece al socio {existente['id']}")

        raise ValueError(construir_error_api(
            code=ERROR_CODE_EMAIL_DUPLICADO,
            message='Email ya registrado',
            description=f"Ya existe un socio con el email '{email}'"
        ), 409)


def crear_socio(body: dict) -> dict:
    """
    Valida el body, verifica que el email no este registrado e inserta el socio.
    El servidor asigna el id y deja al socio activo. Retorna el socio creado.
    """
    datos = validar_body_nuevo_socio(body)

    verificar_email_disponible(datos['email'])

    nuevo_id = repositorio_socios.insertar_socio(datos['nombre'], datos['email'])

    return buscar_socio_por_id(nuevo_id)


def actualizar_socio(id_socio: int, body: dict) -> dict:
    """
    Verifica que el socio exista, valida el body y guarda los cambios.
    Los campos que no vienen en el body conservan su valor. Retorna el socio actualizado.
    """
    socio_actual = buscar_socio_por_id(id_socio)

    cambios = validar_body_actualizacion_socio(body)

    if 'email' in cambios:
        verificar_email_disponible(cambios['email'], id_socio)

    repositorio_socios.actualizar_socio(
        id_socio=id_socio,
        nombre=cambios.get('nombre', socio_actual['nombre']),
        email=cambios.get('email', socio_actual['email']),
        activo=cambios.get('activo', socio_actual['activo']),
    )

    return buscar_socio_por_id(id_socio)