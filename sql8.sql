---Ejecutar 1---

CREATE VIEW VistaVentasPorCliente AS
SELECT 
    c.CustomerID,
    c.CompanyName,
    SUM(od.Quantity * od.UnitPrice) AS TotalVentas
FROM Customers c
INNER JOIN Orders o ON c.CustomerID = o.CustomerID
INNER JOIN [Order Details] od ON o.OrderID = od.OrderID
GROUP BY c.CustomerID, c.CompanyName;

---Ejecutar 2---

SELECT * FROM VistaVentasPorCliente;