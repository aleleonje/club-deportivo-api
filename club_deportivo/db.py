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

TABLA_RESERVA = 'reservas'
TABLA_SOCIO = 'socios'
COLUMNAS_RESERVA = 'id, id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, precio_total'
 
 
def _condiciones_reservas(filtros: dict) -> tuple[str, dict]:
    condiciones = []
    parametros = {}
 
    if 'id_cancha' in filtros:
        condiciones.append('id_cancha = :id_cancha')
        parametros['id_cancha'] = filtros['id_cancha']
 
    if 'id_socio' in filtros:
        condiciones.append('id_socio = :id_socio')
        parametros['id_socio'] = filtros['id_socio']
 
    if 'estado' in filtros:
        condiciones.append('estado = :estado')
        parametros['estado'] = filtros['estado']
 
    if 'fecha_desde' in filtros:
        condiciones.append('DATE(fecha_hora_inicio) >= :fecha_desde')
        parametros['fecha_desde'] = filtros['fecha_desde']
 
    if 'fecha_hasta' in filtros:
        condiciones.append('DATE(fecha_hora_inicio) <= :fecha_hasta')
        parametros['fecha_hasta'] = filtros['fecha_hasta']
 
    where = f"WHERE {' AND '.join(condiciones)}" if condiciones else ''
 
    return where, parametros
 
 
def contar_reservas(filtros: dict) -> int:
    where, parametros = _condiciones_reservas(filtros)
    sql = f'SELECT COUNT(*) AS total FROM {TABLA_RESERVA} {where}'
    filas = ejecutar_consulta(sql, parametros)
 
    return filas[0]['total']
 
 
def obtener_reservas(filtros: dict, limit: int, offset: int) -> list[dict]:
    where, parametros = _condiciones_reservas(filtros)

    sql = f"""
        SELECT {COLUMNAS_RESERVA}
        FROM {TABLA_RESERVA}
        {where}
        ORDER BY id ASC
        LIMIT :limit OFFSET :offset
    """
 
    return ejecutar_consulta(sql, {**parametros, 'limit': limit, 'offset': offset})
 
# Funcion para eveitar superposiciones en una sola transaccion
 
def crear_reserva_atomica(id_socio: int, id_cancha: int, inicio, fin) -> dict:
    """
    Devuelve {'error': (code, status, description)} si algo falla, o {'reserva': {...}}.
    """
    with obtener_conexion() as conexion:
        with conexion.begin():
            cancha = conexion.execute(
                text('SELECT id, precio_hora, activa FROM canchas WHERE id = :id FOR UPDATE'),
                {'id': id_cancha}).mappings().first()
            if cancha is None:
                return {'error': ('ERROR_CANCHA_NO_ENCONTRADA', 404, f"No existe una cancha con id '{id_cancha}'")}
 
            socio = conexion.execute(
                text(f'SELECT id, activo FROM {TABLA_SOCIO} WHERE id = :id FOR UPDATE'),
                {'id': id_socio}).mappings().first()
            if socio is None:
                return {'error': ('ERROR_SOCIO_NO_ENCONTRADO', 404, f"No existe un socio con id '{id_socio}'")}
 
            if not cancha['activa']:
                return {'error': ('ERROR_ENTIDAD_INACTIVA', 409, 'La cancha está inactiva')}
            if not socio['activo']:
                return {'error': ('ERROR_ENTIDAD_INACTIVA', 409, 'El socio está inactivo')}
            solape_cancha = text(f"""
                SELECT 1 FROM {TABLA_RESERVA}
                WHERE id_cancha = :valor AND estado = 'confirmada'
                  AND fecha_hora_inicio < :fin AND fecha_hora_fin > :inicio
                LIMIT 1
            """)
            if conexion.execute(solape_cancha, {'valor': id_cancha, 'inicio': inicio, 'fin': fin}).first():
                return {'error': ('ERROR_SUPERPOSICION', 409,
                                  'La cancha ya tiene una reserva confirmada que se superpone con el intervalo')}
 
            solape_socio = text(f"""
                SELECT 1 FROM {TABLA_RESERVA}
                WHERE id_socio = :valor AND estado = 'confirmada'
                  AND fecha_hora_inicio < :fin AND fecha_hora_fin > :inicio
                LIMIT 1
            """)
            if conexion.execute(solape_socio, {'valor': id_socio, 'inicio': inicio, 'fin': fin}).first():
                return {'error': ('ERROR_SUPERPOSICION', 409,
                                  'El socio ya tiene una reserva confirmada que se superpone con el intervalo')}
 
            horas = int((fin - inicio).total_seconds() // 3600)
            precio_hora = cancha['precio_hora']
            precio_total = horas * precio_hora
 
            resultado = conexion.execute(text(f"""
                INSERT INTO {TABLA_RESERVA}
                    (id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, precio_total)
                VALUES (:id_socio, :id_cancha, :inicio, :fin, 'confirmada', :precio_hora, :precio_total)
            """), {'id_socio': id_socio, 'id_cancha': id_cancha, 'inicio': inicio, 'fin': fin,
                   'precio_hora': precio_hora, 'precio_total': precio_total})
 
            fila = conexion.execute(text(f'SELECT {COLUMNAS_RESERVA} FROM {TABLA_RESERVA} WHERE id = :id'),
                                    {'id': resultado.lastrowid}).mappings().first()
            return {'reserva': dict(fila)}


def obtener_reserva_por_id(id_reserva: int) -> dict:
    sql = f'SELECT {COLUMNAS_RESERVA} FROM {TABLA_RESERVA} WHERE id = :id'
    filas = ejecutar_consulta(sql, {'id': id_reserva})

    return filas[0] if filas else {}


def actualizar_estado_reserva(id_reserva: int, estado_actual: str, estado_nuevo: str) -> bool:
    """
    Cambia el estado solo si la reserva sigue en `estado_actual`.
    Retorna False si otro pedido la modifico mientras tanto (no se actualiza nada).
    """
    sql = f"""
        UPDATE {TABLA_RESERVA}
        SET estado = :estado_nuevo
        WHERE id = :id AND estado = :estado_actual
    """

    with obtener_conexion() as conexion:
        with conexion.begin():
            resultado = conexion.execute(text(sql), {
                'id': id_reserva,
                'estado_actual': estado_actual,
                'estado_nuevo': estado_nuevo,
            })

        return resultado.rowcount == 1
