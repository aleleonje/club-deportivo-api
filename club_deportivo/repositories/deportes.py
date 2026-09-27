from ..db import ejecutar_consulta


def obtener_deportes() -> list[dict]:
    """Retorna todos los deportes precargados, ordenados por id """
    sql = 'SELECT id, nombre FROM deportes ORDER BY id'

    return ejecutar_consulta(sql)