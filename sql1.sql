SELECT 
    c.CompanyName AS Cliente,
    COUNT(o.OrderID) AS TotalPedidos,
    SUM(od.Quantity * od.UnitPrice) AS TotalVentas
FROM Customers c
INNER JOIN Orders o ON c.CustomerID = o.CustomerID
INNER JOIN [Order Details] od ON o.OrderID = od.OrderID
GROUP BY c.CompanyName
ORDER BY TotalVentas DESC;