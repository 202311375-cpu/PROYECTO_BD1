SELECT 
    e.FirstName + ' ' + e.LastName AS Empleado,
    COUNT(o.OrderID) AS TotalPedidos,
    SUM(od.Quantity * od.UnitPrice) AS TotalVentas
FROM Employees e
INNER JOIN Orders o ON e.EmployeeID = o.EmployeeID
INNER JOIN [Order Details] od ON o.OrderID = od.OrderID
GROUP BY e.FirstName, e.LastName
ORDER BY TotalVentas DESC;