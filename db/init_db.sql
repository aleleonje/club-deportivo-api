--Deportes
CREATE TABLE deportes (
    id     INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,

    CONSTRAINT uq_deportes_nombre UNIQUE (nombre)
) ENGINE = InnoDB;


-- Canchas
CREATE TABLE canchas (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    nombre      VARCHAR(100) NOT NULL,
    id_deporte  INT          NOT NULL,
    precio_hora INT          NOT NULL,
    techada     BOOLEAN      NOT NULL DEFAULT FALSE,
    activa      BOOLEAN      NOT NULL DEFAULT TRUE,

    CONSTRAINT fk_canchas_deporte
        FOREIGN KEY (id_deporte) REFERENCES deportes (id),
    CONSTRAINT ck_canchas_precio_hora CHECK (precio_hora > 0),
    CONSTRAINT ck_canchas_nombre      CHECK (TRIM(nombre) <> '')
) ENGINE = InnoDB;

CREATE INDEX ix_canchas_deporte ON canchas (id_deporte);
CREATE INDEX ix_canchas_activa  ON canchas (activa);

--Datos
INSERT INTO deportes (id, nombre) VALUES
    (1, 'Futbol'),
    (2, 'Tenis'),
    (3, 'Padel');

INSERT INTO canchas (nombre, id_deporte, precio_hora, techada, activa) VALUES
    ('Cancha 1 - Futbol 5',  1, 1000000, FALSE, TRUE),
    ('Cancha 2 - Futbol 11', 1, 1800000, FALSE, TRUE),
    ('Cancha 3 - Tenis',     2,  600000, FALSE, TRUE),
    ('Cancha 4 - Tenis',     2,  750000, TRUE,  TRUE),
    ('Cancha 5 - Padel',     3,  800000, TRUE,  TRUE),
    ('Cancha 6 - Padel',     3,  800000, TRUE,  FALSE);