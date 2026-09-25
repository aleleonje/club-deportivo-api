from sqlalchemy import create_engine, text
from .constants import DB_URL

COLUMNAS_CANCHA = 'id, nombre, id_deporte, precio_hora, techada, activa'

def obtener_conexion():
    motor = create_engine(DB_URL)
    return motor.connect()

def fila_a_dict(fila) -> dict:
    return dict(fila._mapping)

def ejecutar_consulta(sql: str, parametros: dict = None) -> list[dict]:
    with obtener_conexion() as conexion:
        resultado = conexion.execute(text(sql), parametros or {})

        return [fila_a_dict(fila) for fila in resultado]


def ejecutar_mutacion(sql: str, parametros: dict = None) -> int:
    with obtener_conexion() as conexion:
        with conexion.begin():
            resultado = conexion.execute(text(sql), parametros or {})

        return resultado.lastrowid or 0

def _condiciones_canchas(filtros: dict) -> tuple[str, dict]:
    condiciones = []
    parametros = {}

    if 'id_deporte' in filtros:
        condiciones.append('id_deporte = :id_deporte')
        parametros['id_deporte'] = filtros['id_deporte']

    if 'nombre' in filtros:
        condiciones.append('LOWER(nombre) LIKE :nombre')
        parametros['nombre'] = f"%{filtros['nombre'].lower()}%"

    if 'techada' in filtros:
        condiciones.append('techada = :techada')
        parametros['techada'] = filtros['techada']

    if 'activa' in filtros:
        condiciones.append('activa = :activa')
        parametros['activa'] = filtros['activa']

    where = f"WHERE {' AND '.join(condiciones)}" if condiciones else ''

    return where, parametros


def contar_canchas(filtros: dict) -> int:
    where, parametros = _condiciones_canchas(filtros)
    sql = f'SELECT COUNT(*) AS total FROM canchas {where}'
    filas = ejecutar_consulta(sql, parametros)

    return filas[0]['total']


def obtener_canchas(filtros: dict, limit: int, offset: int) -> list[dict]:
    where, parametros = _condiciones_canchas(filtros)
    sql = f"""
        SELECT {COLUMNAS_CANCHA}
        FROM canchas
        {where}
        ORDER BY id
        LIMIT :limit OFFSET :offset
    """

    return ejecutar_consulta(sql, {**parametros, 'limit': limit, 'offset': offset})


def obtener_cancha_por_id(id_cancha: int) -> dict:
    sql = f'SELECT {COLUMNAS_CANCHA} FROM canchas WHERE id = :id'
    filas = ejecutar_consulta(sql, {'id': id_cancha})

    return filas[0] if filas else {}


def existe_deporte(id_deporte: int) -> bool:
    sql = 'SELECT id FROM deportes WHERE id = :id'
    filas = ejecutar_consulta(sql, {'id': id_deporte})

    return len(filas) > 0


def cancha_tiene_reservas(id_cancha: int) -> bool:
    sql = 'SELECT id FROM reservas WHERE id_cancha = :id LIMIT 1'
    filas = ejecutar_consulta(sql, {'id': id_cancha})

    return len(filas) > 0


def insertar_cancha(nombre: str, id_deporte: int, precio_hora: int,
                    techada: bool, activa: bool) -> int:
    sql = """
          INSERT INTO canchas (nombre, id_deporte, precio_hora, techada, activa)
          VALUES (:nombre, :id_deporte, :precio_hora, :techada, :activa) \
          """

    return ejecutar_mutacion(sql, {
        'nombre': nombre,
        'id_deporte': id_deporte,
        'precio_hora': precio_hora,
        'techada': techada,
        'activa': activa,
    })


def actualizar_cancha_parcial(id_cancha: int, campos: dict) -> None:
    columnas = ', '.join(f'{campo} = :{campo}' for campo in campos)
    sql = f'UPDATE canchas SET {columnas} WHERE id = :id'

    ejecutar_mutacion(sql, {**campos, 'id': id_cancha})


def eliminar_cancha(id_cancha: int) -> None:
    sql = 'DELETE FROM canchas WHERE id = :id'

    ejecutar_mutacion(sql, {'id': id_cancha})



# Disponibilidad de canchas

def _condiciones_disponibilidad(filtros: dict) -> tuple[str, dict]:
    condiciones = [
        'c.activa = TRUE',
        """NOT EXISTS (
               SELECT 1
               FROM reservas r
               WHERE r.id_cancha            = c.id
                 AND r.estado               = 'confirmada'
                 AND r.fecha_hora_inicio    < :fin
                 AND r.fecha_hora_fin       > :inicio
           )""",
    ]
    parametros = {
        'inicio': filtros['inicio'],
        'fin': filtros['fin'],
    }

    if 'id_deporte' in filtros:
        condiciones.append('c.id_deporte = :id_deporte')
        parametros['id_deporte'] = filtros['id_deporte']

    if 'techada' in filtros:
        condiciones.append('c.techada = :techada')
        parametros['techada'] = filtros['techada']

    return f"WHERE {' AND '.join(condiciones)}", parametros


def contar_canchas_disponibles(filtros: dict) -> int:
    where, parametros = _condiciones_disponibilidad(filtros)
    sql = f'SELECT COUNT(*) AS total FROM canchas c {where}'
    filas = ejecutar_consulta(sql, parametros)

    return filas[0]['total']


def obtener_canchas_disponibles(filtros: dict, limit: int, offset: int) -> list[dict]:
    where, parametros = _condiciones_disponibilidad(filtros)
    sql = f"""
        SELECT c.id, c.nombre, c.id_deporte, c.precio_hora, c.techada, c.activa
        FROM canchas c
        {where}
        ORDER BY c.id
        LIMIT :limit OFFSET :offset
    """

    return ejecutar_consulta(sql, {**parametros, 'limit': limit, 'offset': offset})