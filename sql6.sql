-- Eliminar detalles del pedido antes que el pedido 
DELETE FROM [Order Details]
WHERE OrderID = 11000;

-- Eliminar el pedido
DELETE FROM Orders
WHERE OrderID = 11000;