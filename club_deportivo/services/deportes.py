from ..repositories import deportes as repositorio_deportes


def construir_deporte_dto(deporte: dict) -> dict:
    """DTO publico de un deporte."""
    return {
        'id':     deporte['id'],
        'nombre': deporte['nombre'],
    }


def listar_deportes() -> dict:
    """Retorna todos los deportes precargados. No usa paginacion"""
    deportes = [construir_deporte_dto(fila) for fila in repositorio_deportes.obtener_deportes()]

    return {'deportes': deportes}