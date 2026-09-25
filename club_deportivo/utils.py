from urllib.parse import urlencode


def construir_error_api(code: str, message: str, description: str, level: str = 'error') -> dict:
    return {
        'errors': [{
            'code': code,
            'message': message,
            'level': level,
            'description': description,
        }]
    }


def _href(base_url: str, parametros: dict, limit: int, offset: int) -> dict:
    query = urlencode({**parametros, '_limit': limit, '_offset': offset})

    return {'href': f'{base_url}?{query}'}


def construir_links_paginacion(base_url: str, parametros: dict,
                               limit: int, offset: int, total: int) -> dict:
    ultimo_offset = max(0, ((max(total, 1) - 1) // limit) * limit)

    links = {
        '_first': _href(base_url, parametros, limit, 0),
        '_last': _href(base_url, parametros, limit, ultimo_offset),
    }

    if offset > 0:
        links['_prev'] = _href(base_url, parametros, limit, max(0, offset - limit))

    if offset + limit < total:
        links['_next'] = _href(base_url, parametros, limit, offset + limit)

    return links