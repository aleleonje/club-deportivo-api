# Club Deportivo API

## Motivación
El Club Deportivo Encuentro dispone de canchas de fútbol, tenis y pádel que sus socios pueden reservar. 
Actualmente, el personal recibe las solicitudes por teléfono y mensajes, y registra los turnos en una 
planilla compartida. 
Este procedimiento genera reservas superpuestas, dificultades para consultar los horarios disponibles y 
cancelaciones que no se reflejan correctamente. Además, los cambios de tarifas dificultan reconstruir el 
importe acordado para una reserva anterior. 
El club solicita una API que centralice la información de sus canchas y socios, permita gestionar reservas 
y conserve el historial de las operaciones. 

## Arquitectura
(Completar)

## Estructura del proyecto
(Completar)

## Requisitos previos

- Python 3.10+
- **Una** de las dos opciones para correr MySQL:
  - Docker + Docker Compose (recomendado), o
  - Una instalacion local de MySQL 8

## Configuracion

### 1. Variables de entorno

Copiar `.env.example` a `.env`. Se ajustan las variables de entorno según como se tenga configurado MySQL:

```bash
cp .env.example .env
```

```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=root
DB_NAME=club_deportivo_db
```

### 2. Base de datos MySQL

Eleg **una** de las dos opciones según lo que tengas instalado.

#### Opcion A: con Docker (recomendado)

`docker-compose.yml` levanta MySQL 8 y monta `db/init_db.sql` como script de inicializacion, creando la tabla e insertando los datos de ejemplo automaticamente la **primera** vez:

```bash
docker compose up -d
```

Verificar que el contenedor esté listo (puede tardar unos segundos):

```bash
docker compose logs -f mysql
# Buscar la linea: "ready for connections"
```

Apagar el contenedor manteniendo los datos en el volumen:

```bash
docker compose down
```

Apagar y **borrar** los datos (la proxima vez se vuelven a cargar los datos de `init_db.sql`):

```bash
docker compose down -v
```

#### Opcion B: con MySQL instalado localmente

Si ya tenes MySQL 8 corriendo en tu máquina (puerto `3306` por default):

1. Crear la base de datos y cargar el esquema + datos de ejemplo:

   ```bash
   # Linux / macOS / WSL
   mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS club_deportivo_db;"
   mysql -u root -p club_deportivo_db < db/init_db.sql
   ```

   ```powershell
   # Windows PowerShell
   mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS club_deportivo_db;"
   Get-Content db\init_db.sql | mysql -u root -p club_deportivo_db
   ```

2. Verificar que la tabla se haya creado:

   ```bash
   mysql -u root -p -e "USE club_deportivo_db; SHOW TABLES;"
   ```

   Deberías ver: `canchas`, `deporte`, `socio`, `reserva`.  (Completar)

3. Si tu usuario, password, puerto o nombre de base no coinciden con los defaults, actualiza el `.env` antes de levantar la API.

### 3. Entorno virtual, instalacion y ejecucion

El proyecto incluye scripts de setup que crean el entorno virtual, instalan las dependencias y levantan la API. Si marcara error, probar actualizar pip.

```bash
# Windows
./setup_virtualenv.bat

# Linux / macOS
chmod +x setup_virtualenv.sh
./setup_virtualenv.sh
```

Una vez iniciada, la API estara disponible en `http://localhost:5000/club_deportivo_api`