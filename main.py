import os
from typing import List
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel

# ==========================================
# 1. CONFIGURACIÓN DE BASE DE DATOS
# ==========================================
SQLALCHEMY_DATABASE_URL = "mssql+pyodbc://sa:1234@192.168.31.188/Northwind?driver=ODBC+Driver+17+for+SQL+Server"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


# ==========================================
# 2. MODELOS DE DATOS (PYDANTIC SCHEMAS)
# ==========================================

class PedidoCreate(BaseModel):
    CustomerID: str
    EmployeeID: int
    OrderDate: str
    ShipCountry: str
    ProductID: int
    UnitPrice: float
    Quantity: int
    Discount: float

class ClienteUpdate(BaseModel):
    Phone: str
    Address: str

class ReporteVentaCliente(BaseModel):
    Cliente: str
    TotalPedidos: int
    TotalVentas: float

class ReporteVentaEmpleado(BaseModel):
    Empleado: str
    TotalPedidos: int
    TotalVentas: float

class ReporteVentaAnioMes(BaseModel):
    Año: int
    Mes: int
    TotalVentas: float

class VistaPedidosProductos(BaseModel):
    OrderID: int
    ProductName: str
    Quantity: int
    UnitPrice: float
    TotalLinea: float

class VistaVentasPorCliente(BaseModel):
    CustomerID: str
    CompanyName: str
    TotalVentas: float

class HistorialPedido(BaseModel):
    OrderID: int
    OrderDate: str
    ProductName: str
    Quantity: int
    UnitPrice: float
    TotalLinea: float


# ==========================================
# 3. INICIALIZACIÓN DE LA APP
# ==========================================
app = FastAPI(title="API Northwind - Grupo 2", description="CRUD Avanzado con SQL Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not os.path.exists("static"):
    os.makedirs("static")

app.mount("/ui", StaticFiles(directory="static", html=True), name="static")


# ==========================================
# 4. RUTAS / ENDPOINTS
# ==========================================

@app.get("/")
def root():
    return RedirectResponse(url="/ui/index.html")


# --- CONSULTAS AVANZADAS ---

@app.get("/consultas/ventas-por-cliente", response_model=List[ReporteVentaCliente])
def ventas_por_cliente(db: Session = Depends(get_db)):
    query = text("""
        SELECT c.CompanyName AS Cliente, COUNT(o.OrderID) AS TotalPedidos, SUM(od.Quantity * od.UnitPrice) AS TotalVentas
        FROM Customers c
        INNER JOIN Orders o ON c.CustomerID = o.CustomerID
        INNER JOIN [Order Details] od ON o.OrderID = od.OrderID
        GROUP BY c.CompanyName
        ORDER BY TotalVentas DESC
    """)
    result = db.execute(query).fetchall()
    return [{"Cliente": row[0], "TotalPedidos": row[1], "TotalVentas": float(row[2])} for row in result]

@app.get("/consultas/ventas-por-empleado", response_model=List[ReporteVentaEmpleado])
def ventas_por_empleado(db: Session = Depends(get_db)):
    query = text("""
        SELECT e.FirstName + ' ' + e.LastName AS Empleado, COUNT(o.OrderID) AS TotalPedidos, SUM(od.Quantity * od.UnitPrice) AS TotalVentas
        FROM Employees e
        INNER JOIN Orders o ON e.EmployeeID = o.EmployeeID
        INNER JOIN [Order Details] od ON o.OrderID = od.OrderID
        GROUP BY e.FirstName, e.LastName
        ORDER BY TotalVentas DESC
    """)
    result = db.execute(query).fetchall()
    return [{"Empleado": row[0], "TotalPedidos": row[1], "TotalVentas": float(row[2])} for row in result]

@app.get("/consultas/ventas-por-anio-mes", response_model=List[ReporteVentaAnioMes])
def ventas_por_anio_mes(db: Session = Depends(get_db)):
    query = text("""
        SELECT YEAR(o.OrderDate) AS Año, MONTH(o.OrderDate) AS Mes, SUM(od.Quantity * od.UnitPrice) AS TotalVentas
        FROM Orders o
        INNER JOIN [Order Details] od ON o.OrderID = od.OrderID
        GROUP BY YEAR(o.OrderDate), MONTH(o.OrderDate)
        ORDER BY Año, Mes
    """)
    result = db.execute(query).fetchall()
    return [{"Año": row[0], "Mes": row[1], "TotalVentas": float(row[2])} for row in result]


# --- VISTAS ---

@app.get("/vistas/pedidos-productos", response_model=List[VistaPedidosProductos])
def vista_pedidos_productos(db: Session = Depends(get_db)):
    query = text("SELECT * FROM VistaPedidosProductos")
    result = db.execute(query).fetchall()
    return [{"OrderID": row[0], "ProductName": row[1], "Quantity": row[2], "UnitPrice": row[3], "TotalLinea": float(row[4])} for row in result]

@app.get("/vistas/ventas-por-cliente", response_model=List[VistaVentasPorCliente])
def vista_ventas_por_cliente(db: Session = Depends(get_db)):
    query = text("SELECT * FROM VistaVentasPorCliente")
    result = db.execute(query).fetchall()
    return [{"CustomerID": row[0], "CompanyName": row[1], "TotalVentas": float(row[2])} for row in result]


# --- PROCEDIMIENTOS ALMACENADOS ---

@app.get("/historial/{customer_id}", response_model=List[HistorialPedido])
def obtener_historial_cliente(customer_id: str, db: Session = Depends(get_db)):
    try:
        query = text("EXEC ObtenerHistorialPedidos @CustomerID = :cid")
        result = db.execute(query, {"cid": customer_id}).fetchall()
        return [
            {"OrderID": row[0], "OrderDate": str(row[1]), "ProductName": row[2], "Quantity": row[3], "UnitPrice": float(row[4]), "TotalLinea": float(row[5])}
            for row in result
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en SP: {str(e)}")


# --- OPERACIONES CRUD ---

@app.post("/pedidos/registrar-completo")
def registrar_pedido(pedido: PedidoCreate, db: Session = Depends(get_db)):
    try:
        sql = text("""
            EXEC RegistrarPedido 
            @CustomerID = :c_id, 
            @EmployeeID = :e_id, 
            @OrderDate = :o_date, 
            @ShipCountry = :country,
            @ProductID = :p_id, 
            @UnitPrice = :price, 
            @Quantity = :qty, 
            @Discount = :disc
        """)
        db.execute(sql, {
            "c_id": pedido.CustomerID,
            "e_id": pedido.EmployeeID,
            "o_date": pedido.OrderDate,
            "country": pedido.ShipCountry,
            "p_id": pedido.ProductID,
            "price": pedido.UnitPrice,
            "qty": pedido.Quantity,
            "disc": pedido.Discount
        })
        db.commit()
        return {"message": "✅ Pedido registrado exitosamente."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error al registrar: {str(e)}")

@app.put("/clientes/{customer_id}")
def actualizar_cliente(customer_id: str, datos: ClienteUpdate, db: Session = Depends(get_db)):
    try:
        query = text("UPDATE Customers SET Phone = :phone, Address = :addr WHERE CustomerID = :cid")
        result = db.execute(query, {"phone": datos.Phone, "addr": datos.Address, "cid": customer_id})
        db.commit()
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        return {"message": f"Datos del cliente {customer_id} actualizados."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/pedidos/{order_id}")
def eliminar_pedido(order_id: int, db: Session = Depends(get_db)):
    try:
        db.execute(text("DELETE FROM [Order Details] WHERE OrderID = :oid"), {"oid": order_id})
        result = db.execute(text("DELETE FROM Orders WHERE OrderID = :oid"), {"oid": order_id})
        db.commit()
        if result.rowcount == 0:
            return {"message": "El pedido no existe o ya fue eliminado."}
        return {"message": f"Pedido {order_id} eliminado correctamente (Cascada manual)."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
