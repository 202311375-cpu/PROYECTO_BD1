README – Proyecto Northwind (Guía Rápida)

Este sistema permite gestionar pedidos, clientes y reportes de ventas de la base de datos Northwind, usando una API en FastAPI y una interfaz web en HTML + Bootstrap.

COMO INICIAR EL SISTEMA

1. Instalar dependencias:
   pip install fastapi uvicorn sqlalchemy pyodbc pydantic
   
2. Ejecutar el servidor:
   uvicorn main:app --reload

3. Abrir la interfaz web:
   http://localhost:8000/ui/index.html

USO DEL SISTEMA (desde la interfaz)

La página principal contiene formularios para realizar todas las funciones:

1. Registrar Pedido
- Ingresa ID Cliente, ID Empleado e ID Producto.
- El sistema registra un pedido completo usando un procedimiento almacenado.

2. Actualizar Cliente
- Edita el teléfono y dirección mediante un formulario.

3. Eliminar Pedido
- Ingresa un OrderID → elimina pedido + detalles en cascada.

4. Consultas Avanzadas
- Botones para mostrar tablas con:
- Ventas por cliente
- Ventas por empleado
- Ventas por año y mes

5. Vistas SQL
- Permite visualizar:
  Vista de pedidos con productos
  Vista de ventas por cliente

6. Historial del Cliente
- Ingresa un CustomerID → muestra todas sus compras.
