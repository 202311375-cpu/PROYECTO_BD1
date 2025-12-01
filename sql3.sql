SELECT 
    YEAR(o.OrderDate) AS Año,
    MONTH(o.OrderDate) AS Mes,
    SUM(od.Quantity * od.UnitPrice) AS TotalVentas
FROM Orders o
INNER JOIN [Order Details] od ON o.OrderID = od.OrderID
GROUP BY YEAR(o.OrderDate), MONTH(o.OrderDate)
ORDER BY Año, Mes;