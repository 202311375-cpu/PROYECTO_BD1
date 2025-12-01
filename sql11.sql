EXEC RegistrarPedido
    @CustomerID = 'ALFKI',      
    @EmployeeID = 3,           
    @OrderDate = '2025-11-20', 
    @ShipCountry = 'Germany',  
    @ProductID = 10,           
    @UnitPrice = 25.00,        
    @Quantity = 5,             
    @Discount = 0.15;


SELECT TOP 1 * FROM Orders ORDER BY OrderID DESC;


EXEC ObtenerHistorialPedidos @CustomerID = 'ALFKI';