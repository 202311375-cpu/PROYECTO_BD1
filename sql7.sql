--- Ejecutar 1---

CREATE VIEW VistaPedidosProductos AS
SELECT 
    o.OrderID,
    p.ProductName,
    od.Quantity,
    od.UnitPrice,
    (od.Quantity * od.UnitPrice) AS TotalLinea
FROM Orders o
INNER JOIN [Order Details] od ON o.OrderID = od.OrderID
INNER JOIN Products p ON od.ProductID = p.ProductID;

---Ejecutar 2---

SELECT * FROM VistaPedidosProductos;