CREATE PROCEDURE RegistrarPedido
    @CustomerID VARCHAR(5),
    @EmployeeID INT,
    @OrderDate DATE,
    @ShipCountry VARCHAR(50),
    @ProductID INT,
    @UnitPrice MONEY,
    @Quantity INT,
    @Discount FLOAT
AS
BEGIN
    SET NOCOUNT ON;

    -- Insertar en Orders
    INSERT INTO Orders (CustomerID, EmployeeID, OrderDate, ShipCountry)
    VALUES (@CustomerID, @EmployeeID, @OrderDate, @ShipCountry);

    -- Obtener el OrderID generado (IDENT_CURRENT podría usarse)
    DECLARE @NewOrderID INT;
    SET @NewOrderID = SCOPE_IDENTITY();

    -- Insertar en Order Details
    INSERT INTO [Order Details] (OrderID, ProductID, UnitPrice, Quantity, Discount)
    VALUES (@NewOrderID, @ProductID, @UnitPrice, @Quantity, @Discount);
END;