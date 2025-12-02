import os
from typing import List, Optional
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
# Asegúrate de que la IP y credenciales sean correctas
#SQLALCHEMY_DATABASE_URL = "mssql+pyodbc://sa:1234@192.168.31.188/Northwind?driver=ODBC+Driver+17+for+SQL+Server"
SQLALCHEMY_DATABASE_URL = (
    "mssql+pyodbc:///?odbc_connect="
    "DRIVER=ODBC+Driver+18+for+SQL+Server;"
    "SERVER=FABRIZIO\\SQLEXPRESS;"
    "DATABASE=Northwind;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

# Configuración del Engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependencia para obtener la sesión de BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()  # Rollback en caso de error general
        raise e
    finally:
        db.close()


# ==========================================
# 2. MODELOS DE DATOS (PYDANTIC SCHEMAS)
# ==========================================

# Input: Para registrar un pedido nuevo
class PedidoCreate(BaseModel):
    CustomerID: str
    EmployeeID: int
    OrderDate: str  # YYYY-MM-DD
    ShipCountry: str
    ProductID: int
    UnitPrice: float
    Quantity: int
    Discount: float


# Input: Para actualizar contacto de cliente
class ClienteUpdate(BaseModel):
    Phone: str
    Address: str


# Output: Para el reporte de ventas (Consulta 1)
class ReporteVentaCliente(BaseModel):
    Cliente: str
    TotalPedidos: int
    TotalVentas: float


# Output: Para el historial (Procedimiento Almacenado)
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

# --- A. Configuración CORS (Permitir conexión desde el navegador) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- B. Configuración de Archivos Estáticos (Frontend) ---
# Crea la carpeta 'static' si no existe para evitar errores
if not os.path.exists("static"):
    os.makedirs("static")

# Montar la carpeta 'static' en la URL '/ui'
app.mount("/ui", StaticFiles(directory="static", html=True), name="static")


# ==========================================
# 4. RUTAS / ENDPOINTS
# ==========================================

@app.get("/")
def root():
    # Redirige automáticamente al frontend
    return RedirectResponse(url="/ui/index.html")


# --- LECTURA (READ) ---

@app.get("/reportes/ventas-por-cliente", response_model=List[ReporteVentaCliente])
def obtener_ventas_por_cliente(db: Session = Depends(get_db)):
    """
    [Consulta 1 del Doc] Ventas por Cliente usando JOIN y GROUP BY.
    """
    query = text("""
        SELECT c.CompanyName                   AS Cliente,
               COUNT(o.OrderID)                AS TotalPedidos,
               SUM(od.Quantity * od.UnitPrice) AS TotalVentas
        FROM Customers c
        INNER JOIN Orders o ON c.CustomerID = o.CustomerID
        INNER JOIN [Order Details] od ON o.OrderID = od.OrderID
        GROUP BY c.CompanyName
        ORDER BY TotalVentas DESC
    """)
    
    result = db.execute(query).fetchall()

    return [
        {
            "Cliente": row.Cliente,
            "TotalPedidos": row.TotalPedidos,
            "TotalVentas": float(row.TotalVentas or 0)
        }
        for row in result
    ]


@app.get("/historial/{customer_id}", response_model=List[HistorialPedido])
def obtener_historial_cliente(customer_id: str, db: Session = Depends(get_db)):
    """
    [Procedimiento Almacenado] ObtenerHistorialPedidos
    """
    try:
        query = text("EXEC ObtenerHistorialPedidos @CustomerID = :cid")
        result = db.execute(query, {"cid": customer_id}).fetchall()

        return [
            {
                "OrderID": row[0],
                "OrderDate": str(row[1]),
                "ProductName": row[2],
                "Quantity": row[3],
                "UnitPrice": float(row[4] or 0),
                "TotalLinea": float(row[5] or 0)
            }
            for row in result
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en SP: {str(e)}")

# --- CREACIÓN (CREATE) ---

@app.post("/pedidos/registrar-completo")
def registrar_pedido(pedido: PedidoCreate, db: Session = Depends(get_db)):
    """
    [Procedimiento Almacenado] RegistrarPedido
    Inserta en Orders y Order Details usando una transacción SQL.
    """
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


# --- ACTUALIZACIÓN (UPDATE) ---

@app.put("/clientes/{customer_id}")
def actualizar_cliente(customer_id: str, datos: ClienteUpdate, db: Session = Depends(get_db)):
    """
    [Update Simple] Actualiza Teléfono y Dirección.
    """
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


# --- ELIMINACIÓN (DELETE) ---

@app.delete("/pedidos/{order_id}")
def eliminar_pedido(order_id: int, db: Session = Depends(get_db)):
    """
    [Integridad Referencial] Elimina primero detalles, luego cabecera.
    """
    try:
        # Paso 1: Eliminar detalles
        db.execute(text("DELETE FROM [Order Details] WHERE OrderID = :oid"), {"oid": order_id})

        # Paso 2: Eliminar cabecera
        result = db.execute(text("DELETE FROM Orders WHERE OrderID = :oid"), {"oid": order_id})

        db.commit()

        if result.rowcount == 0:
            return {"message": "El pedido no existe o ya fue eliminado."}

        return {"message": f"Pedido {order_id} eliminado correctamente (Cascada manual)."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))