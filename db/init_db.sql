CREATE DATABASE IF NOT EXISTS club_deportivo_db;
 USE club_deportivo_db;
   CREATE TABLE IF NOT EXISTS deportes (
           id INT AUTO_INCREMENT PRIMARY KEY,
           nombre VARCHAR (20) NOT NULL UNIQUE
       );
    INSERT IGNORE INTO deportes (nombre)
    VALUES ('Futbol'), ('Tenis'), ('Padel');

   CREATE TABLE IF NOT EXISTS canchas (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(20) NOT NULL,
        id_deporte INT NOT NULL,
        techada BOOLEAN NOT NULL DEFAULT FALSE,
        precio_hora INT NOT NULL,
        activa BOOLEAN NOT NULL DEFAULT TRUE,
        FOREIGN KEY (id_deporte) REFERENCES deportes(id)
    );

    -- ingreso de datos de ejemplo
    INSERT IGNORE INTO canchas (nombre, id_deporte, techada, precio_hora, activa)
      VALUES
     ('Cancha de futbol', 1, True, 1500000, TRUE),
     ('Cancha de tenis', 2, True, 1000000, TRUE);



   CREATE TABLE IF NOT EXISTS socios (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(60) NOT NULL,
        activo BOOLEAN DEFAULT TRUE,
        email VARCHAR(80) NOT NULL UNIQUE
    );
    -- ingreso de datos de ejemplo
    INSERT IGNORE INTO socios (nombre, activo, email)
        VALUES
        ('Sebastian', True, 'sebastian@gmail.com'),
        ('Pedro', True, 'pedro@gmail.com');

   CREATE TABLE IF NOT EXISTS reservas (
        id INT AUTO_INCREMENT PRIMARY KEY,
        id_socio INT NOT NULL,
        id_cancha INT NOT NULL,
        fecha_hora_inicio DATETIME(6) NOT NULL,
        fecha_hora_fin DATETIME(6) NOT NULL,
        estado VARCHAR(20) NOT NULL DEFAULT 'confirmada',
        precio_hora INT NOT NULL,
        precio_total INT NOT NULL,
        FOREIGN KEY (id_socio) REFERENCES socios(id),
        FOREIGN KEY (id_cancha) REFERENCES canchas(id)
   );

   -- ingreso de datos de ejemplo
   INSERT IGNORE INTO reservas (id_socio, id_cancha,fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, precio_total)
        VALUES
        (1, 1, '2027-10-15 18:00:00.000000', '2027-10-15 20:00:00.000000', 'confirmada', 1500000, 3000000);