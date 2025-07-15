DROP TABLE IF EXISTS detalle_pedido;
DROP TABLE IF EXISTS pedidos;
DROP TABLE IF EXISTS productos;
DROP TABLE IF EXISTS clientes;

CREATE TABLE clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    documento TEXT NOT NULL UNIQUE,
    telefono TEXT,
    direccion TEXT,
    email TEXT UNIQUE
);

CREATE TABLE productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    sabor TEXT NOT NULL,
    gramaje TEXT NOT NULL,
    precio_unitario REAL NOT NULL
);

CREATE TABLE pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL,
    forma_entrega TEXT,
    estado TEXT DEFAULT 'registrado',
    fecha_hora TEXT NOT NULL,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
);

CREATE TABLE detalle_pedido (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pedido_id INTEGER NOT NULL,
    producto_id INTEGER NOT NULL,
    cantidad INTEGER NOT NULL,
    observaciones TEXT,
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
    FOREIGN KEY (producto_id) REFERENCES productos(id)
);

-- Catalogo de productos
INSERT INTO productos (nombre, sabor, gramaje, precio_unitario) VALUES
('Papas', 'Natural', '30g', 1300),
('Papas', 'Natural', '50g', 1800),
('Papas', 'Natural', '70g', 2500),

('Papas', 'Limón', '30g', 1300),
('Papas', 'Limón', '50g', 1800),
('Papas', 'Limón', '70g', 2500),

('Papas', 'Limón pimienta', '30g', 1300),
('Papas', 'Limón pimienta', '50g', 1800),
('Papas', 'Limón pimienta', '70g', 2500),

('Papas', 'Mayonesa', '30g', 1300),
('Papas', 'Mayonesa', '50g', 1800),
('Papas', 'Mayonesa', '70g', 2500),

('Papas', 'Pollo', '30g', 1300),
('Papas', 'Pollo', '50g', 1800),
('Papas', 'Pollo', '70g', 2500),

('Papas', 'BBQ picante', '30g', 1300),
('Papas', 'BBQ picante', '50g', 1800),
('Papas', 'BBQ picante', '70g', 2500),

('Plátano', 'Verde natural', '50g', 1800),
('Plátano', 'Verde natural', '70g', 2500),

('Plátano', 'Verde limón', '50g', 1800),
('Plátano', 'Verde limón', '70g', 2500),

('Plátano', 'Maduro natural', '50g', 1800),
('Plátano', 'Maduro natural', '70g', 2500),

('Plátano', 'Maduro limón', '50g', 1800),
('Plátano', 'Maduro limón', '70g', 2500),

('Chicharrón', 'Natural', '35g', 2200),

('Chicharrón', 'Limón', '35g', 2200),

('Extrudos', 'Aros limón', '50g', 1700),

('Extrudos', 'Rosquillas limón', '50g', 1700),

('Extrudos', 'Tocineta miel', '50g', 1700),

('Extrudos', 'Chicharrin natural', '50g', 1700),

('Extrudos', 'Chicharrin limón', '50g', 1700);


-- Clientes de ejemplo
INSERT INTO clientes (nombre, documento, telefono, direccion, email) VALUES
('Luis Rodríguez', '123456789', '3124567890', 'Cra 45 #12-34', 'luis@example.com');

-- Pedidos
INSERT INTO pedidos (cliente_id, forma_entrega, estado, fecha_hora) VALUES
(1, 'Domicilio', 'registrado', '2025-06-25 10:00:00');

-- Detalle de pedidos
INSERT INTO detalle_pedido (pedido_id, producto_id, cantidad, observaciones) VALUES
(1, 1, 2, 'Sin sal');

