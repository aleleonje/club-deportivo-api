import os
from dotenv import load_dotenv

load_dotenv()

# Constantes
BASE_URL = '/club_deportivo_api'

# Codigos de error
ERROR_CODE_INVALID_BODY = 'ERROR_BODY_INVALIDO'
ERROR_CODE_VALIDACION = 'ERROR_VALIDACION'
ERROR_CODE_CANCHA_NOT_FOUND = 'ERROR_CANCHA_NO_ENCONTRADA'
ERROR_CODE_DEPORTE_NOT_FOUND = 'ERROR_DEPORTE_NO_ENCONTRADO'
ERROR_CODE_CANCHA_CON_RESERVAS = 'ERROR_CANCHA_CON_RESERVAS'

# Horario de atención del club (horas en punto, GMT-3)
HORA_APERTURA = 8
HORA_CIERRE = 23

# Duración permitida de un intervalo reservable, en horas completas
DURACION_MINIMA_HORAS = 1
DURACION_MAXIMA_HORAS = 3

# Zona horaria fija del contrato: GMT-3
ZONA_HORARIA_OFFSET = '-03:00'

# Paginación
LIMIT_POR_DEFECTO = 10
LIMIT_MAXIMO = 100
LIMIT_MINIMO = 1
OFFSET_POR_DEFECTO = 0

# Campos aceptados por los endpoints de canchas
CAMPOS_CANCHA_REQUERIDOS = ('nombre', 'id_deporte', 'precio_hora')
CAMPOS_CANCHA_OPCIONALES = ('techada', 'activa')
CAMPOS_CANCHA_EDITABLES  = ('nombre', 'precio_hora', 'techada', 'activa')

# Configuración de la base de datos MySQL
DB_HOST     = os.getenv('DB_HOST', 'localhost')
DB_PORT     = int(os.getenv('DB_PORT', '3306'))
DB_USER     = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'root')
DB_NAME     = os.getenv('DB_NAME', 'club_deportivo_db')
DB_URL      = f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# Errores en reservas
ERROR_CODE_SOCIO_NOT_FOUND   = 'ERROR_SOCIO_NO_ENCONTRADO'
ERROR_CODE_ENTIDAD_INACTIVA  = 'ERROR_ENTIDAD_INACTIVA'
ERROR_CODE_SUPERPOSICION     = 'ERROR_SUPERPOSICION'

# Filtros aceptados por GET/reservas
CAMPOS_FILTRO_RESERVAS = ('id_cancha', 'id_socio', 'estado', 'fecha_desde', 'fecha_hasta')