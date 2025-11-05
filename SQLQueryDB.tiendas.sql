USE master;
GO

-- ==========================================
-- FORZAR ELIMINACIÓN DE LA BASE DE DATOS SI ESTÁ EN USO
-- ==========================================
IF EXISTS (SELECT name FROM sys.databases WHERE name = N'tiendas')
BEGIN
    ALTER DATABASE tiendas SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE tiendas;
END
GO

-- ==========================================
-- CREAR BASE DE DATOS NUEVA
-- ==========================================
CREATE DATABASE tiendas;
GO

USE tiendas;
GO

-- ============================================================
-- TABLA CLIENTES
-- ============================================================
CREATE TABLE clientes (
    id_cliente INT IDENTITY(1,1) PRIMARY KEY,
    nombre NVARCHAR(100),
    apellido NVARCHAR(100),
    dni CHAR(8),
    telefono VARCHAR(15),
    correo NVARCHAR(100),
    direccion NVARCHAR(150)
);
GO

-- ============================================================
-- TABLA PRODUCTOS
-- ============================================================
CREATE TABLE productos (
    id_producto INT IDENTITY(1,1) PRIMARY KEY,
    nombre NVARCHAR(100),
    categoria NVARCHAR(100),
    marca NVARCHAR(50),
    precio DECIMAL(10,2),
    stock INT
);
GO

-- ============================================================
-- TABLA PRESENTACION
-- ============================================================
CREATE TABLE presentacion (
    id_presentacion INT IDENTITY(1,1) PRIMARY KEY,
    tipo NVARCHAR(50),
    descripcion NVARCHAR(150)
);
GO

-- ============================================================
-- GRUPO 1: PEDIDOS (sin duplicar FK a CLIENTES)
-- ============================================================
CREATE TABLE pedido (
    id_pedido INT IDENTITY(1,1) PRIMARY KEY,
    fecha DATE,
    total DECIMAL(10,2)
);

CREATE TABLE clienPedido (
    id_cliente INT,
    id_pedido INT,
    PRIMARY KEY (id_cliente, id_pedido),
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
    FOREIGN KEY (id_pedido) REFERENCES pedido(id_pedido)
);
GO

-- ============================================================
-- GRUPO 2: PRODUCTOS Y VENTAS
-- ============================================================
CREATE TABLE productoXpresentacion (
    id_producto INT,
    id_presentacion INT,
    PRIMARY KEY (id_producto, id_presentacion),
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto),
    FOREIGN KEY (id_presentacion) REFERENCES presentacion(id_presentacion)
);

-- Si ya existe, la eliminamos primero
IF OBJECT_ID('clienXproducto', 'U') IS NOT NULL
    DROP TABLE clienXproducto;
GO

-- Crear nuevamente sin FK hacia clientes
CREATE TABLE clienXproducto (
    id_cliente INT,
    id_producto INT,
    cantidad INT,
    fecha DATE,
    PRIMARY KEY (id_cliente, id_producto),
    -- Se mantiene la FK hacia productos
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);
GO


CREATE TABLE ventas (
    id_venta INT IDENTITY(1,1) PRIMARY KEY,
    id_cliente INT,
    fecha DATE DEFAULT GETDATE(),
    total DECIMAL(10,2),
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
);

CREATE TABLE detalle_venta (
    id_detalle INT IDENTITY(1,1) PRIMARY KEY,
    id_venta INT,
    id_producto INT,
    cantidad INT,
    subtotal DECIMAL(10,2),
    FOREIGN KEY (id_venta) REFERENCES ventas(id_venta),
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);
GO

use tiendas;
go
-- CLIENTES
INSERT INTO clientes (nombre, apellido, dni, telefono, correo, direccion) VALUES
('Luis', 'Torres', '70581234', '987654321', 'luis.torres@gmail.com', 'Av. Los Incas 123'),
('María', 'Lopez', '70981235', '945672123', 'maria.lopez@hotmail.com', 'Calle Cusco 234'),
('Carlos', 'Perez', '71981236', '912345678', 'carlos.perez@yahoo.com', 'Jr. Grau 321'),
('Lucía', 'Gomez', '72981237', '911223344', 'lucia.gomez@gmail.com', 'Av. Los Andes 456'),
('Pedro', 'Ramos', '73981238', '999888777', 'pedro.ramos@gmail.com', 'Calle Lima 654'),
('Ana', 'Mendoza', '74981239', '988776655', 'ana.mendoza@hotmail.com', 'Urb. Primavera 987'),
('Miguel', 'Quispe', '75981240', '922111222', 'miguel.quispe@gmail.com', 'Av. Collasuyo 123'),
('Sandra', 'Flores', '76981241', '944333444', 'sandra.flores@gmail.com', 'Calle Sol 222'),
('Jorge', 'Castro', '77981242', '955666777', 'jorge.castro@hotmail.com', 'Jr. Puno 333'),
('Elena', 'Rojas', '78981243', '966999888', 'elena.rojas@gmail.com', 'Av. Garcilaso 444');

-- PRODUCTOS
INSERT INTO productos (nombre, categoria, marca, precio, stock) VALUES
('Laptop HP Pavilion', 'Computadora', 'HP', 2800.00, 10),
('Mouse Logitech M90', 'Periférico', 'Logitech', 45.00, 50),
('Teclado Redragon Kumara', 'Periférico', 'Redragon', 150.00, 25),
('Monitor Samsung 24"', 'Pantalla', 'Samsung', 600.00, 15),
('SSD Kingston 480GB', 'Almacenamiento', 'Kingston', 200.00, 30),
('Disco Duro Seagate 1TB', 'Almacenamiento', 'Seagate', 250.00, 20),
('Memoria RAM 8GB DDR4', 'Componente', 'Crucial', 180.00, 35),
('Tarjeta Gráfica GTX 1650', 'Componente', 'NVIDIA', 1200.00, 12),
('Procesador Ryzen 5 5600G', 'Componente', 'AMD', 950.00, 8),
('Placa Madre ASUS B550', 'Componente', 'ASUS', 780.00, 10);

-- PRESENTACION
INSERT INTO presentacion (tipo, descripcion) VALUES
('Caja', 'Producto nuevo sellado en caja original'),
('Bolsa', 'Producto en bolsa antiestática'),
('Blíster', 'Empaque tipo blíster transparente'),
('Unidad', 'Venta por unidad'),
('Pack', 'Incluye accesorios y cables'),
('OEM', 'Versión sin caja original'),
('Refurbished', 'Producto reacondicionado'),
('Bulk', 'Venta por volumen'),
('Edición limitada', 'Versión especial o limitada'),
('Bundle', 'Paquete promocional con varios productos');

-- VENTAS
INSERT INTO ventas (id_cliente, fecha, total) VALUES
(1, '2025-10-01', 45.50),
(2, '2025-10-01', 72.30),
(3, '2025-10-02', 23.90),
(4, '2025-10-02', 65.00),
(5, '2025-10-03', 110.20),
(6, '2025-10-03', 56.75),
(7, '2025-10-04', 89.40),
(8, '2025-10-04', 34.60),
(9, '2025-10-05', 98.10),
(10, '2025-10-05', 120.00);

-- DETALLE VENTA
INSERT INTO detalle_venta (id_venta, id_producto, cantidad, subtotal) VALUES
(1, 1, 2, 10.00),
(1, 3, 1, 5.50),
(2, 2, 3, 21.90),
(2, 5, 2, 50.40),
(3, 4, 1, 23.90),
(4, 1, 5, 15.00),
(4, 7, 2, 50.00),
(5, 8, 3, 45.60),
(5, 9, 2, 64.60),
(6, 10, 3, 56.75);

-- PEDIDOS
INSERT INTO pedido (id_pedido, fecha, total) VALUES
(1, '2025-10-02', '12'),
(2, '2025-10-03', '20'),
(3, '2025-10-04', '35'),
(4, '2025-10-05', '20'),
(5, '2025-10-06', '65'),
(6, '2025-10-06', '3'),
(7, '2025-10-07', '5'),
(8, '2025-10-07', '8'),
(9, '2025-10-08', '9'),
(10, '2025-10-09', '8');

INSERT INTO clienXproducto (id_cliente, id_producto, cantidad, fecha)
VALUES
(1, 1, 2, '2025-10-02'),
(2, 3, 1, '2025-10-03'),
(3, 5, 4, '2025-10-04'),
(4, 2, 2, '2025-10-05'),
(5, 8, 3, '2025-10-06'),
(6, 6, 1, '2025-10-07'),
(7, 7, 2, '2025-10-08'),
(8, 4, 1, '2025-10-09'),
(9, 9, 5, '2025-10-10'),
(10, 10, 2, '2025-10-11');
GO


select*
from clientes;