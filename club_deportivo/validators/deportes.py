from ..utils import validar_parametros_permitidos

# GET /deportes no tiene filtros ni paginacion=cualquier parametro se rechaza
PARAMETROS_LISTADO_DEPORTES = []


def validar_parametros_listado_deportes(args) -> None:
    """Valida que el GET /deportes no reciba parametros en la query string."""
    validar_parametros_permitidos(args, PARAMETROS_LISTADO_DEPORTES)