from ..db import ejecutar_consulta, ejecutar_mutacion


def construir_condiciones_socios(nombre: str = None, activo: bool = None) -> tuple[str, dict]:
    """
    Arma el WHERE del listado combinando con AND los filtros recibidos.
    El texto del WHERE es fijo: los valores del usuario viajan siempre como parametros.
    """
    condiciones = []
    parametros  = {}

    if nombre is not None:
        condiciones.append('LOWER(nombre) LIKE LOWER(:nombre)')
        parametros['nombre'] = f'%{nombre}%'

    if activo is not None:
        condiciones.append('activo = :activo')
        parametros['activo'] = activo

    if not condiciones:
        return '', parametros

    return 'WHERE ' + ' AND '.join(condiciones), parametros


def contar_socios(nombre: str = None, activo: bool = None) -> int:
    """Retorna cuantos socios cumplen los filtros (se usa para armar la paginacion)."""
    where, parametros = construir_condiciones_socios(nombre, activo)
    sql = f'SELECT COUNT(*) AS total FROM socios {where}'

    return ejecutar_consulta(sql, parametros)[0]['total']


def obtener_socios(nombre: str, activo: bool, limit: int, offset: int) -> list[dict]:
    """Retorna una pagina de socios que cumplen los filtros, ordenados por id."""
    where, parametros = construir_condiciones_socios(nombre, activo)
    sql = f"""
        SELECT id, nombre, email, activo
        FROM socios
        {where}
        ORDER BY id
        LIMIT :limit OFFSET :offset
    """

    parametros['limit']  = limit
    parametros['offset'] = offset

    return ejecutar_consulta(sql, parametros)


def obtener_socio_por_id(id_socio: int) -> dict:
    """Retorna el socio con el id dado, o un dict vacio si no existe."""
    sql   = 'SELECT id, nombre, email, activo FROM socios WHERE id = :id'
    filas = ejecutar_consulta(sql, {'id': id_socio})

    return filas[0] if filas else {}


def obtener_socio_por_email(email: str) -> dict:
    """Retorna el socio con el email dado (activo o no), o un dict vacio si no existe."""
    sql   = 'SELECT id, nombre, email, activo FROM socios WHERE email = :email'
    filas = ejecutar_consulta(sql, {'email': email})

    return filas[0] if filas else {}


def insertar_socio(nombre: str, email: str) -> int:
    """Inserta un socio nuevo, siempre activo, y retorna el id generado."""
    sql = """
        INSERT INTO socios (nombre, email, activo)
        VALUES (:nombre, :email, TRUE)
    """

    return ejecutar_mutacion(sql, {
        'nombre': nombre,
        'email':  email,
    })


def actualizar_socio(id_socio: int, nombre: str, email: str, activo: bool) -> None:
    """Guarda los datos completos de un socio existente."""
    sql = """
        UPDATE socios
        SET nombre = :nombre, email = :email, activo = :activo
        WHERE id = :id
    """

    ejecutar_mutacion(sql, {
        'id':     id_socio,
        'nombre': nombre,
        'email':  email,
        'activo': activo,
    })
