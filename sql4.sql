-- Insertar nuevo cliente
INSERT INTO Customers (CustomerID, CompanyName, ContactName, ContactTitle, Address, City, PostalCode, Country)
VALUES ('NEW01', 'Empresa Nueva', 'Juan Pérez', 'Gerente', 'Calle 123', 'Lima', '12345', 'Peru');

-- Insertar nuevo pedido para el cliente
INSERT INTO Orders (CustomerID, EmployeeID, OrderDate, ShipCountry)
VALUES ('NEW01', 5, GETDATE(), 'Peru');

-- Obtener el último OrderID insertado (dependiendo del sistema gestor de BD)

-- Insertar detalle del pedido (ejemplo, con OrderID 11000)
INSERT INTO [Order Details] (OrderID, ProductID, UnitPrice, Quantity, Discount)
VALUES (11000, 42, 15.00, 10, 0);