import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc
from datetime import datetime

# =========================
# CONEXIÓN A SQL SERVER
# =========================
def conectar_bd():
    try:
        conexion = pyodbc.connect(
            'DRIVER={SQL Server};SERVER=localhost;DATABASE=tiendas;Trusted_Connection=yes;'
        )
        return conexion
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo conectar a la base de datos:\n{e}")
        return None

# =========================
# FUNCIONES CRUD MEJORADAS
# =========================

# CLIENTES
def cargar_clientes():
    try:
        for fila in tabla_clientes.get_children():
            tabla_clientes.delete(fila)
        conexion = conectar_bd()
        if conexion:
            cursor = conexion.cursor()
            cursor.execute("SELECT id_cliente, nombre, apellido, dni, telefono, correo, direccion FROM clientes")
            for fila in cursor.fetchall():
                # Asegurar que todos los valores sean strings
                fila_convertida = [str(valor) if valor is not None else "" for valor in fila]
                tabla_clientes.insert("", tk.END, values=fila_convertida)
            conexion.close()
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar clientes:\n{e}")

def agregar_cliente():
    try:
        # Validaciones
        if not all([entry_nombre.get(), entry_apellido.get(), entry_dni.get()]):
            messagebox.showwarning("Advertencia", "Nombre, Apellido y DNI son obligatorios")
            return
        
        if len(entry_dni.get()) != 8 or not entry_dni.get().isdigit():
            messagebox.showwarning("Advertencia", "El DNI debe tener 8 dígitos numéricos")
            return
        
        conexion = conectar_bd()
        if conexion:
            cursor = conexion.cursor()
            try:
                # Verificar si el DNI ya existe
                cursor.execute("SELECT id_cliente FROM clientes WHERE dni = ?", (entry_dni.get(),))
                if cursor.fetchone():
                    messagebox.showwarning("Advertencia", "Ya existe un cliente con este DNI")
                    return
                
                cursor.execute("""
                    INSERT INTO clientes (nombre, apellido, dni, telefono, correo, direccion)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    entry_nombre.get().strip().title(),
                    entry_apellido.get().strip().title(),
                    entry_dni.get(),
                    entry_telefono.get() or None,
                    entry_correo.get().lower() or None,
                    entry_direccion.get() or None
                ))
                conexion.commit()
                messagebox.showinfo("Éxito", "Cliente agregado correctamente.")
                limpiar_campos_cliente()
                cargar_clientes()
                cargar_clientes_combo()
                cargar_clientes_pedido_combo()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo agregar el cliente:\n{e}")
            finally:
                conexion.close()
    except Exception as e:
        messagebox.showerror("Error", f"Error inesperado:\n{e}")

def actualizar_cliente():
    try:
        seleccionado = tabla_clientes.focus()
        if not seleccionado:
            messagebox.showwarning("Atención", "Selecciona un cliente para actualizar.")
            return
        
        if not all([entry_nombre.get(), entry_apellido.get(), entry_dni.get()]):
            messagebox.showwarning("Advertencia", "Nombre, Apellido y DNI son obligatorios")
            return
        
        id_cliente = tabla_clientes.item(seleccionado)['values'][0]
        conexion = conectar_bd()
        if conexion:
            cursor = conexion.cursor()
            try:
                # Verificar si el DNI ya existe en otro cliente
                cursor.execute("SELECT id_cliente FROM clientes WHERE dni = ? AND id_cliente != ?", 
                              (entry_dni.get(), int(id_cliente)))
                if cursor.fetchone():
                    messagebox.showwarning("Advertencia", "Ya existe otro cliente con este DNI")
                    return
                
                cursor.execute("""
                    UPDATE clientes 
                    SET nombre=?, apellido=?, dni=?, telefono=?, correo=?, direccion=?
                    WHERE id_cliente=?
                """, (
                    entry_nombre.get().strip().title(),
                    entry_apellido.get().strip().title(),
                    entry_dni.get(),
                    entry_telefono.get() or None,
                    entry_correo.get().lower() or None,
                    entry_direccion.get() or None,
                    int(id_cliente)
                ))
                conexion.commit()
                messagebox.showinfo("Éxito", "Cliente actualizado correctamente.")
                limpiar_campos_cliente()
                cargar_clientes()
                cargar_clientes_combo()
                cargar_clientes_pedido_combo()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar el cliente:\n{e}")
            finally:
                conexion.close()
    except Exception as e:
        messagebox.showerror("Error", f"Error inesperado:\n{e}")

def eliminar_cliente():
    try:
        seleccionado = tabla_clientes.focus()
        if not seleccionado:
            messagebox.showwarning("Atención", "Selecciona un cliente para eliminar.")
            return
        
        if messagebox.askyesno("Confirmar", "¿Estás seguro de eliminar este cliente?"):
            id_cliente = tabla_clientes.item(seleccionado)['values'][0]
            conexion = conectar_bd()
            if conexion:
                cursor = conexion.cursor()
                try:
                    # Verificar si el cliente tiene ventas relacionadas
                    cursor.execute("SELECT COUNT(*) FROM ventas WHERE id_cliente = ?", (int(id_cliente),))
                    if cursor.fetchone()[0] > 0:
                        messagebox.showwarning("Error", "No se puede eliminar el cliente porque tiene ventas registradas.")
                        return
                    
                    # Verificar si el cliente tiene pedidos relacionados
                    cursor.execute("SELECT COUNT(*) FROM clienPedido WHERE id_cliente = ?", (int(id_cliente),))
                    if cursor.fetchone()[0] > 0:
                        # Eliminar primero las relaciones en clienPedido
                        cursor.execute("DELETE FROM clienPedido WHERE id_cliente = ?", (int(id_cliente),))
                    
                    # Verificar si el cliente tiene registros en clienXproducto
                    cursor.execute("SELECT COUNT(*) FROM clienXproducto WHERE id_cliente = ?", (int(id_cliente),))
                    if cursor.fetchone()[0] > 0:
                        # Eliminar primero las relaciones en clienXproducto
                        cursor.execute("DELETE FROM clienXproducto WHERE id_cliente = ?", (int(id_cliente),))
                    
                    # Ahora eliminar el cliente
                    cursor.execute("DELETE FROM clientes WHERE id_cliente = ?", (int(id_cliente),))
                    conexion.commit()
                    messagebox.showinfo("Éxito", "Cliente eliminado correctamente.")
                    cargar_clientes()
                    cargar_clientes_combo()
                    cargar_clientes_pedido_combo()
                    
                except Exception as e:
                    conexion.rollback()
                    if 'FK_' in str(e):
                        messagebox.showerror("Error", 
                            "No se puede eliminar el cliente porque tiene registros relacionados.\n"
                            "Elimine primero los registros relacionados en otras tablas.")
                    else:
                        messagebox.showerror("Error", f"No se pudo eliminar el cliente:\n{str(e)}")
                finally:
                    conexion.close()
    except Exception as e:
        messagebox.showerror("Error", f"Error inesperado:\n{e}")

def cargar_cliente_seleccionado(event):
    try:
        seleccionado = tabla_clientes.focus()
        if seleccionado:
            datos = tabla_clientes.item(seleccionado)['values']
            limpiar_campos_cliente()
            entry_nombre.insert(0, datos[1])
            entry_apellido.insert(0, datos[2])
            entry_dni.insert(0, datos[3])
            entry_telefono.insert(0, datos[4] if datos[4] else "")
            entry_correo.insert(0, datos[5] if datos[5] else "")
            entry_direccion.insert(0, datos[6] if datos[6] else "")
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar cliente seleccionado:\n{e}")

def limpiar_campos_cliente():
    entry_nombre.delete(0, tk.END)
    entry_apellido.delete(0, tk.END)
    entry_dni.delete(0, tk.END)
    entry_telefono.delete(0, tk.END)
    entry_correo.delete(0, tk.END)
    entry_direccion.delete(0, tk.END)

# PRODUCTOS
def cargar_productos():
    try:
        for fila in tabla_productos.get_children():
            tabla_productos.delete(fila)
        conexion = conectar_bd()
        if conexion:
            cursor = conexion.cursor()
            cursor.execute("SELECT id_producto, nombre, categoria, marca, precio, stock FROM productos")
            for fila in cursor.fetchall():
                # Convertir todos los valores a strings
                fila_convertida = [str(valor) if valor is not None else "" for valor in fila]
                tabla_productos.insert("", tk.END, values=fila_convertida)
            conexion.close()
        cargar_productos_pedido_combo()
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar productos:\n{e}")

def agregar_producto():
    try:
        if not all([entry_prod_nombre.get(), entry_prod_precio.get()]):
            messagebox.showwarning("Advertencia", "Nombre y Precio son obligatorios")
            return
        
        try:
            precio = float(entry_prod_precio.get())
            stock = int(entry_prod_stock.get() or 0)
            if precio <= 0:
                messagebox.showwarning("Advertencia", "El precio debe ser mayor a 0")
                return
            if stock < 0:
                messagebox.showwarning("Advertencia", "El stock no puede ser negativo")
                return
        except ValueError:
            messagebox.showwarning("Advertencia", "Precio y Stock deben ser valores numéricos")
            return
        
        conexion = conectar_bd()
        if conexion:
            cursor = conexion.cursor()
            try:
                cursor.execute("""
                    INSERT INTO productos (nombre, categoria, marca, precio, stock)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    entry_prod_nombre.get().strip(),
                    entry_prod_categoria.get().strip() or "General",
                    entry_prod_marca.get().strip() or "Sin marca",
                    precio,
                    stock
                ))
                conexion.commit()
                messagebox.showinfo("Éxito", "Producto agregado correctamente.")
                limpiar_campos_producto()
                cargar_productos()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo agregar el producto:\n{e}")
            finally:
                conexion.close()
    except Exception as e:
        messagebox.showerror("Error", f"Error inesperado:\n{e}")

def actualizar_producto():
    try:
        seleccionado = tabla_productos.focus()
        if not seleccionado:
            messagebox.showwarning("Atención", "Selecciona un producto para actualizar.")
            return
        
        if not all([entry_prod_nombre.get(), entry_prod_precio.get()]):
            messagebox.showwarning("Advertencia", "Nombre y Precio son obligatorios")
            return
        
        id_producto = tabla_productos.item(seleccionado)['values'][0]
        
        try:
            precio = float(entry_prod_precio.get())
            stock = int(entry_prod_stock.get() or 0)
        except ValueError:
            messagebox.showwarning("Advertencia", "Precio y Stock deben ser valores numéricos")
            return
        
        conexion = conectar_bd()
        if conexion:
            cursor = conexion.cursor()
            try:
                cursor.execute("""
                    UPDATE productos 
                    SET nombre=?, categoria=?, marca=?, precio=?, stock=?
                    WHERE id_producto=?
                """, (
                    entry_prod_nombre.get().strip(),
                    entry_prod_categoria.get().strip() or "General",
                    entry_prod_marca.get().strip() or "Sin marca",
                    precio,
                    stock,
                    int(id_producto)
                ))
                conexion.commit()
                messagebox.showinfo("Éxito", "Producto actualizado correctamente.")
                limpiar_campos_producto()
                cargar_productos()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar el producto:\n{e}")
            finally:
                conexion.close()
    except Exception as e:
        messagebox.showerror("Error", f"Error inesperado:\n{e}")

def eliminar_producto():
    try:
        seleccionado = tabla_productos.focus()
        if not seleccionado:
            messagebox.showwarning("Atención", "Selecciona un producto para eliminar.")
            return
        
        if messagebox.askyesno("Confirmar", "¿Estás seguro de eliminar este producto?"):
            id_producto = tabla_productos.item(seleccionado)['values'][0]
            conexion = conectar_bd()
            if conexion:
                cursor = conexion.cursor()
                try:
                    # Verificar si el producto tiene ventas relacionadas en detalle_venta
                    cursor.execute("SELECT COUNT(*) FROM detalle_venta WHERE id_producto = ?", (int(id_producto),))
                    if cursor.fetchone()[0] > 0:
                        messagebox.showwarning("Error", "No se puede eliminar el producto porque tiene ventas registradas.")
                        return
                    
                    # Verificar si el producto tiene registros en productoXpresentacion
                    cursor.execute("SELECT COUNT(*) FROM productoXpresentacion WHERE id_producto = ?", (int(id_producto),))
                    if cursor.fetchone()[0] > 0:
                        # Eliminar primero las relaciones en productoXpresentacion
                        cursor.execute("DELETE FROM productoXpresentacion WHERE id_producto = ?", (int(id_producto),))
                    
                    # Verificar si el producto tiene registros en clienXproducto
                    cursor.execute("SELECT COUNT(*) FROM clienXproducto WHERE id_producto = ?", (int(id_producto),))
                    if cursor.fetchone()[0] > 0:
                        # Eliminar primero las relaciones en clienXproducto
                        cursor.execute("DELETE FROM clienXproducto WHERE id_producto = ?", (int(id_producto),))
                    
                    # Ahora eliminar el producto
                    cursor.execute("DELETE FROM productos WHERE id_producto = ?", (int(id_producto),))
                    conexion.commit()
                    messagebox.showinfo("Éxito", "Producto eliminado correctamente.")
                    cargar_productos()
                    
                except Exception as e:
                    conexion.rollback()
                    if 'FK_' in str(e):
                        messagebox.showerror("Error", 
                            "No se puede eliminar el producto porque tiene registros relacionados.\n"
                            "Elimine primero los registros relacionados en otras tablas.")
                    else:
                        messagebox.showerror("Error", f"No se pudo eliminar el producto:\n{str(e)}")
                finally:
                    conexion.close()
    except Exception as e:
        messagebox.showerror("Error", f"Error inesperado:\n{e}")

def cargar_producto_seleccionado(event):
    try:
        seleccionado = tabla_productos.focus()
        if seleccionado:
            datos = tabla_productos.item(seleccionado)['values']
            limpiar_campos_producto()
            entry_prod_nombre.insert(0, datos[1])
            entry_prod_categoria.insert(0, datos[2] if datos[2] else "")
            entry_prod_marca.insert(0, datos[3] if datos[3] else "")
            entry_prod_precio.insert(0, datos[4] if datos[4] else "")
            entry_prod_stock.insert(0, datos[5] if datos[5] else "")
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar producto seleccionado:\n{e}")

def limpiar_campos_producto():
    entry_prod_nombre.delete(0, tk.END)
    entry_prod_categoria.delete(0, tk.END)
    entry_prod_marca.delete(0, tk.END)
    entry_prod_precio.delete(0, tk.END)
    entry_prod_stock.delete(0, tk.END)

# VENTAS
def cargar_ventas():
    try:
        for fila in tabla_ventas.get_children():
            tabla_ventas.delete(fila)
        conexion = conectar_bd()
        if conexion:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT v.id_venta, 
                       COALESCE(c.nombre + ' ' + c.apellido, 'Sin cliente') as cliente, 
                       v.fecha, v.total 
                FROM ventas v 
                LEFT JOIN clientes c ON v.id_cliente = c.id_cliente
                ORDER BY v.fecha DESC
            """)
            for fila in cursor.fetchall():
                fila_convertida = [str(valor) if valor is not None else "" for valor in fila]
                tabla_ventas.insert("", tk.END, values=fila_convertida)
            conexion.close()
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar ventas:\n{e}")

def crear_venta():
    try:
        if not combo_cliente_venta.get() or not entry_venta_total.get():
            messagebox.showwarning("Advertencia", "Cliente y Total son obligatorios")
            return
        
        try:
            total = float(entry_venta_total.get())
            if total <= 0:
                messagebox.showwarning("Advertencia", "El total debe ser mayor a 0")
                return
        except ValueError:
            messagebox.showwarning("Advertencia", "El total debe ser un valor numérico")
            return
        
        conexion = conectar_bd()
        if conexion:
            cursor = conexion.cursor()
            try:
                # Obtener ID del cliente seleccionado
                cliente_nombre = combo_cliente_venta.get()
                id_cliente = None
                if cliente_nombre != "Sin cliente":
                    cursor.execute("SELECT id_cliente FROM clientes WHERE nombre + ' ' + apellido = ?", (cliente_nombre,))
                    resultado = cursor.fetchone()
                    if resultado:
                        id_cliente = resultado[0]
                
                cursor.execute("""
                    INSERT INTO ventas (id_cliente, fecha, total)
                    VALUES (?, GETDATE(), ?)
                """, (id_cliente, total))
                conexion.commit()
                messagebox.showinfo("Éxito", "Venta registrada correctamente.")
                limpiar_campos_venta()
                cargar_ventas()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo registrar la venta:\n{e}")
            finally:
                conexion.close()
    except Exception as e:
        messagebox.showerror("Error", f"Error inesperado:\n{e}")

def cargar_clientes_combo():
    try:
        combo_cliente_venta['values'] = []
        conexion = conectar_bd()
        if conexion:
            cursor = conexion.cursor()
            cursor.execute("SELECT nombre, apellido FROM clientes ORDER BY nombre")
            clientes = [f"{fila[0]} {fila[1]}" for fila in cursor.fetchall()]
            combo_cliente_venta['values'] = ["Sin cliente"] + clientes
            conexion.close()
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar clientes en combo:\n{e}")

def limpiar_campos_venta():
    combo_cliente_venta.set("")
    entry_venta_total.delete(0, tk.END)

# PEDIDOS
def cargar_pedidos():
    try:
        for fila in tabla_pedidos.get_children():
            tabla_pedidos.delete(fila)
        conexion = conectar_bd()
        if conexion:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT p.id_pedido, p.fecha, p.total, 
                       COALESCE(c.nombre + ' ' + c.apellido, 'Sin cliente') as cliente
                FROM pedido p
                LEFT JOIN clienPedido cp ON p.id_pedido = cp.id_pedido
                LEFT JOIN clientes c ON cp.id_cliente = c.id_cliente
                ORDER BY p.fecha DESC
            """)
            for fila in cursor.fetchall():
                fila_convertida = [str(valor) if valor is not None else "" for valor in fila]
                tabla_pedidos.insert("", tk.END, values=fila_convertida)
            conexion.close()
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar pedidos:\n{e}")

def cargar_clientes_pedido_combo():
    try:
        combo_cliente_pedido['values'] = []
        conexion = conectar_bd()
        if conexion:
            cursor = conexion.cursor()
            cursor.execute("SELECT id_cliente, nombre, apellido FROM clientes ORDER BY nombre")
            clientes = [(f"{fila[1]} {fila[2]}", fila[0]) for fila in cursor.fetchall()]
            combo_cliente_pedido['values'] = ["Sin cliente"] + [cliente[0] for cliente in clientes]
            combo_cliente_pedido.clientes_dict = {cliente[0]: cliente[1] for cliente in clientes}
            conexion.close()
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar clientes en combo pedido:\n{e}")

def cargar_productos_pedido_combo():
    try:
        combo_producto_pedido['values'] = []
        conexion = conectar_bd()
        if conexion:
            cursor = conexion.cursor()
            cursor.execute("SELECT id_producto, nombre, precio, stock FROM productos ORDER BY nombre")
            productos = [(f"{fila[1]} - S/.{fila[2]:.2f} (Stock: {fila[3]})", fila[0], fila[2], fila[3]) for fila in cursor.fetchall()]
            combo_producto_pedido['values'] = [producto[0] for producto in productos]
            combo_producto_pedido.productos_dict = {producto[0]: (producto[1], producto[2], producto[3]) for producto in productos}
            conexion.close()
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar productos en combo pedido:\n{e}")

def agregar_producto_pedido():
    try:
        producto_seleccionado = combo_producto_pedido.get()
        cantidad_str = entry_cantidad_pedido.get()
        
        if not producto_seleccionado or not cantidad_str:
            messagebox.showwarning("Advertencia", "Selecciona un producto y ingresa la cantidad")
            return
        
        try:
            cantidad = int(cantidad_str)
            if cantidad <= 0:
                messagebox.showwarning("Advertencia", "La cantidad debe ser mayor a 0")
                return
        except ValueError:
            messagebox.showwarning("Advertencia", "La cantidad debe ser un número entero")
            return
        
        # Obtener información del producto
        producto_info = combo_producto_pedido.productos_dict.get(producto_seleccionado)
        if not producto_info:
            messagebox.showwarning("Advertencia", "Producto no válido")
            return
        
        id_producto, precio, stock = producto_info
        
        # Verificar stock
        if cantidad > stock:
            messagebox.showwarning("Advertencia", f"Stock insuficiente. Solo hay {stock} unidades disponibles")
            return
        
        # Calcular subtotal
        subtotal = precio * cantidad
        
        # Agregar a la tabla temporal
        tabla_productos_pedido.insert("", tk.END, values=(
            producto_seleccionado.split(" - ")[0],  # Solo el nombre
            cantidad,
            f"S/.{precio:.2f}",
            f"S/.{subtotal:.2f}"
        ))
        
        # Actualizar total
        actualizar_total_pedido()
        
        # Limpiar campos
        entry_cantidad_pedido.delete(0, tk.END)
        combo_producto_pedido.set("")
    except Exception as e:
        messagebox.showerror("Error", f"Error al agregar producto al pedido:\n{e}")

def actualizar_total_pedido():
    try:
        total = 0.0
        for item in tabla_productos_pedido.get_children():
            valores = tabla_productos_pedido.item(item)['values']
            subtotal_str = valores[3].replace("S/.", "").strip()
            total += float(subtotal_str)
        
        entry_total_pedido.delete(0, tk.END)
        entry_total_pedido.insert(0, f"{total:.2f}")
    except Exception as e:
        messagebox.showerror("Error", f"Error al actualizar total del pedido:\n{e}")

def eliminar_producto_pedido():
    try:
        seleccionado = tabla_productos_pedido.selection()
        if not seleccionado:
            messagebox.showwarning("Advertencia", "Selecciona un producto para eliminar")
            return
        
        for item in seleccionado:
            tabla_productos_pedido.delete(item)
        
        actualizar_total_pedido()
    except Exception as e:
        messagebox.showerror("Error", f"Error al eliminar producto del pedido:\n{e}")

def limpiar_pedido():
    try:
        for item in tabla_productos_pedido.get_children():
            tabla_productos_pedido.delete(item)
        combo_cliente_pedido.set("")
        entry_total_pedido.delete(0, tk.END)
        entry_cantidad_pedido.delete(0, tk.END)
        combo_producto_pedido.set("")
    except Exception as e:
        messagebox.showerror("Error", f"Error al limpiar pedido:\n{e}")

def crear_pedido():
    try:
        if not tabla_productos_pedido.get_children():
            messagebox.showwarning("Advertencia", "Agrega al menos un producto al pedido")
            return
        
        try:
            total = float(entry_total_pedido.get())
            if total <= 0:
                messagebox.showwarning("Advertencia", "El total debe ser mayor a 0")
                return
        except ValueError:
            messagebox.showwarning("Advertencia", "Total no válido")
            return
        
        conexion = conectar_bd()
        if conexion:
            cursor = conexion.cursor()
            try:
                # Insertar pedido
                cursor.execute("INSERT INTO pedido (fecha, total) VALUES (GETDATE(), ?)", total)
                cursor.execute("SELECT @@IDENTITY")
                id_pedido = cursor.fetchone()[0]
                
                # Asociar cliente si se seleccionó uno
                cliente_nombre = combo_cliente_pedido.get()
                if cliente_nombre != "Sin cliente" and cliente_nombre:
                    id_cliente = combo_cliente_pedido.clientes_dict.get(cliente_nombre)
                    if id_cliente:
                        cursor.execute("INSERT INTO clienPedido (id_cliente, id_pedido) VALUES (?, ?)", 
                                     (id_cliente, id_pedido))
                
                conexion.commit()
                messagebox.showinfo("Éxito", f"Pedido #{id_pedido} creado correctamente")
                limpiar_pedido()
                cargar_pedidos()
                
            except Exception as e:
                conexion.rollback()
                messagebox.showerror("Error", f"No se pudo crear el pedido:\n{e}")
            finally:
                conexion.close()
    except Exception as e:
        messagebox.showerror("Error", f"Error inesperado:\n{e}")

def ver_detalle_pedido():
    try:
        seleccionado = tabla_pedidos.focus()
        if not seleccionado:
            messagebox.showwarning("Advertencia", "Selecciona un pedido para ver el detalle")
            return
        
        id_pedido = tabla_pedidos.item(seleccionado)['values'][0]
        
        conexion = conectar_bd()
        if conexion:
            cursor = conexion.cursor()
            try:
                # Obtener información del pedido
                cursor.execute("""
                    SELECT p.id_pedido, p.fecha, p.total, 
                           COALESCE(c.nombre + ' ' + c.apellido, 'Sin cliente') as cliente
                    FROM pedido p
                    LEFT JOIN clienPedido cp ON p.id_pedido = cp.id_pedido
                    LEFT JOIN clientes c ON cp.id_cliente = c.id_cliente
                    WHERE p.id_pedido = ?
                """, int(id_pedido))
                pedido_info = cursor.fetchone()
                
                if not pedido_info:
                    messagebox.showwarning("Advertencia", "Pedido no encontrado")
                    return
                
                # Construir mensaje de detalle
                detalle = f"📋 DETALLE DEL PEDIDO #{pedido_info[0]}\n\n"
                detalle += f"📅 Fecha: {pedido_info[1]}\n"
                detalle += f"👤 Cliente: {pedido_info[3]}\n"
                detalle += f"💰 Total: S/.{pedido_info[2]:.2f}\n\n"
                detalle += "ℹ️ Los detalles de productos se registran en el sistema"
                
                messagebox.showinfo(f"Detalle Pedido #{id_pedido}", detalle)
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el detalle:\n{e}")
            finally:
                conexion.close()
    except Exception as e:
        messagebox.showerror("Error", f"Error inesperado:\n{e}")

# REPORTES
def generar_reporte_ventas():
    try:
        conexion = conectar_bd()
        if conexion:
            cursor = conexion.cursor()
            
            # Ventas totales
            cursor.execute("SELECT COUNT(*), SUM(total) FROM ventas")
            total_ventas, total_ingresos = cursor.fetchone()
            total_ingresos = total_ingresos or 0
            
            # Pedidos totales
            cursor.execute("SELECT COUNT(*), SUM(total) FROM pedido")
            total_pedidos, total_pedidos_monto = cursor.fetchone()
            total_pedidos_monto = total_pedidos_monto or 0
            
            # Productos más vendidos
            cursor.execute("""
                SELECT TOP 5 p.nombre, SUM(dv.cantidad) as total_vendido
                FROM detalle_venta dv
                JOIN productos p ON dv.id_producto = p.id_producto
                GROUP BY p.nombre
                ORDER BY total_vendido DESC
            """)
            productos_mas_vendidos = cursor.fetchall()
            
            # Clientes más frecuentes
            cursor.execute("""
                SELECT TOP 5 c.nombre + ' ' + c.apellido as cliente, COUNT(*) as compras
                FROM ventas v
                JOIN clientes c ON v.id_cliente = c.id_cliente
                WHERE c.id_cliente IS NOT NULL
                GROUP BY c.nombre, c.apellido
                ORDER BY compras DESC
            """)
            clientes_frecuentes = cursor.fetchall()
            
            # Productos con bajo stock
            cursor.execute("""
                SELECT TOP 5 nombre, stock 
                FROM productos 
                WHERE stock < 10 
                ORDER BY stock ASC
            """)
            productos_bajo_stock = cursor.fetchall()
            
            conexion.close()
            
            # Mostrar reporte
            reporte = f"""📊 REPORTE GENERAL 📊

💰 VENTAS:
   📈 Total Ventas: {total_ventas}
   💵 Ingresos por Ventas: S/. {total_ingresos:,.2f}

📋 PEDIDOS:
   📦 Total Pedidos: {total_pedidos}
   💰 Monto en Pedidos: S/. {total_pedidos_monto:,.2f}

🏆 PRODUCTOS MÁS VENDIDOS:
"""
            for i, producto in enumerate(productos_mas_vendidos, 1):
                reporte += f"   {i}. {producto[0]}: {producto[1]} unidades\n"
            
            reporte += "\n👥 CLIENTES MÁS FRECUENTES:\n"
            for i, cliente in enumerate(clientes_frecuentes, 1):
                reporte += f"   {i}. {cliente[0]}: {cliente[1]} compras\n"
            
            if productos_bajo_stock:
                reporte += "\n⚠️ PRODUCTOS CON BAJO STOCK:\n"
                for producto in productos_bajo_stock:
                    reporte += f"   • {producto[0]}: {producto[1]} unidades\n"
            
            messagebox.showinfo("Reporte General", reporte)
    except Exception as e:
        messagebox.showerror("Error", f"Error al generar reporte:\n{e}")

# =========================
# INTERFAZ GRÁFICA
# =========================
ventana = tk.Tk()
ventana.title("🏪 Sistema de Gestión - Tiendas")
ventana.geometry("1400x900")
ventana.configure(bg="#f0f8ff")

# Configurar estilo
style = ttk.Style()
style.configure("TButton", padding=6, relief="flat", background="#ccc")
style.configure("TLabel", background="#f0f8ff")
style.configure("TFrame", background="#f0f8ff")

# NOTEBOOK (PESTAÑAS)
notebook = ttk.Notebook(ventana)
notebook.pack(fill="both", expand=True, padx=10, pady=10)

# PESTAÑA CLIENTES (mantener igual)
frame_clientes = ttk.Frame(notebook)
notebook.add(frame_clientes, text="👥 Clientes")

frame_form_cliente = ttk.LabelFrame(frame_clientes, text="📝 Datos del Cliente")
frame_form_cliente.pack(fill="x", padx=10, pady=5)

tk.Label(frame_form_cliente, text="Nombre*:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
entry_nombre = tk.Entry(frame_form_cliente, width=20)
entry_nombre.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_form_cliente, text="Apellido*:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
entry_apellido = tk.Entry(frame_form_cliente, width=20)
entry_apellido.grid(row=0, column=3, padx=5, pady=5)

tk.Label(frame_form_cliente, text="DNI*:").grid(row=0, column=4, padx=5, pady=5, sticky="e")
entry_dni = tk.Entry(frame_form_cliente, width=15)
entry_dni.grid(row=0, column=5, padx=5, pady=5)

tk.Label(frame_form_cliente, text="Teléfono:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
entry_telefono = tk.Entry(frame_form_cliente, width=20)
entry_telefono.grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame_form_cliente, text="Correo:").grid(row=1, column=2, padx=5, pady=5, sticky="e")
entry_correo = tk.Entry(frame_form_cliente, width=20)
entry_correo.grid(row=1, column=3, padx=5, pady=5)

tk.Label(frame_form_cliente, text="Dirección:").grid(row=1, column=4, padx=5, pady=5, sticky="e")
entry_direccion = tk.Entry(frame_form_cliente, width=20)
entry_direccion.grid(row=1, column=5, padx=5, pady=5)

frame_botones_cliente = ttk.Frame(frame_clientes)
frame_botones_cliente.pack(fill="x", padx=10, pady=5)

tk.Button(frame_botones_cliente, text="➕ Agregar Cliente", command=agregar_cliente, bg="#76c893", width=15).pack(side="left", padx=5)
tk.Button(frame_botones_cliente, text="✏️ Actualizar Cliente", command=actualizar_cliente, bg="#ffca3a", width=15).pack(side="left", padx=5)
tk.Button(frame_botones_cliente, text="🗑️ Eliminar Cliente", command=eliminar_cliente, bg="#ff595e", width=15).pack(side="left", padx=5)
tk.Button(frame_botones_cliente, text="🧹 Limpiar Campos", command=limpiar_campos_cliente, bg="#8ac6fc", width=15).pack(side="left", padx=5)
tk.Button(frame_botones_cliente, text="🔄 Actualizar Lista", command=cargar_clientes, bg="#1982c4", width=15).pack(side="left", padx=5)

frame_tabla_clientes = ttk.Frame(frame_clientes)
frame_tabla_clientes.pack(fill="both", expand=True, padx=10, pady=5)

columnas_clientes = ("ID", "Nombre", "Apellido", "DNI", "Teléfono", "Correo", "Dirección")
tabla_clientes = ttk.Treeview(frame_tabla_clientes, columns=columnas_clientes, show="headings", height=12)
for col in columnas_clientes:
    tabla_clientes.heading(col, text=col)
    tabla_clientes.column(col, width=120)

scroll_clientes = ttk.Scrollbar(frame_tabla_clientes, orient="vertical", command=tabla_clientes.yview)
tabla_clientes.configure(yscrollcommand=scroll_clientes.set)
scroll_clientes.pack(side="right", fill="y")
tabla_clientes.pack(fill="both", expand=True)
tabla_clientes.bind("<<TreeviewSelect>>", cargar_cliente_seleccionado)

# PESTAÑA PRODUCTOS (mantener igual)
frame_productos = ttk.Frame(notebook)
notebook.add(frame_productos, text="📦 Productos")

frame_form_producto = ttk.LabelFrame(frame_productos, text="📝 Datos del Producto")
frame_form_producto.pack(fill="x", padx=10, pady=5)

tk.Label(frame_form_producto, text="Nombre*:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
entry_prod_nombre = tk.Entry(frame_form_producto, width=20)
entry_prod_nombre.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_form_producto, text="Categoría:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
entry_prod_categoria = tk.Entry(frame_form_producto, width=20)
entry_prod_categoria.grid(row=0, column=3, padx=5, pady=5)

tk.Label(frame_form_producto, text="Marca:").grid(row=0, column=4, padx=5, pady=5, sticky="e")
entry_prod_marca = tk.Entry(frame_form_producto, width=20)
entry_prod_marca.grid(row=0, column=5, padx=5, pady=5)

tk.Label(frame_form_producto, text="Precio*:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
entry_prod_precio = tk.Entry(frame_form_producto, width=20)
entry_prod_precio.grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame_form_producto, text="Stock:").grid(row=1, column=2, padx=5, pady=5, sticky="e")
entry_prod_stock = tk.Entry(frame_form_producto, width=20)
entry_prod_stock.grid(row=1, column=3, padx=5, pady=5)

frame_botones_producto = ttk.Frame(frame_productos)
frame_botones_producto.pack(fill="x", padx=10, pady=5)

tk.Button(frame_botones_producto, text="➕ Agregar Producto", command=agregar_producto, bg="#76c893", width=15).pack(side="left", padx=5)
tk.Button(frame_botones_producto, text="✏️ Actualizar Producto", command=actualizar_producto, bg="#ffca3a", width=15).pack(side="left", padx=5)
tk.Button(frame_botones_producto, text="🗑️ Eliminar Producto", command=eliminar_producto, bg="#ff595e", width=15).pack(side="left", padx=5)
tk.Button(frame_botones_producto, text="🧹 Limpiar Campos", command=limpiar_campos_producto, bg="#8ac6fc", width=15).pack(side="left", padx=5)
tk.Button(frame_botones_producto, text="🔄 Actualizar Lista", command=cargar_productos, bg="#1982c4", width=15).pack(side="left", padx=5)

frame_tabla_productos = ttk.Frame(frame_productos)
frame_tabla_productos.pack(fill="both", expand=True, padx=10, pady=5)

columnas_productos = ("ID", "Nombre", "Categoría", "Marca", "Precio", "Stock")
tabla_productos = ttk.Treeview(frame_tabla_productos, columns=columnas_productos, show="headings", height=12)
for col in columnas_productos:
    tabla_productos.heading(col, text=col)
    tabla_productos.column(col, width=120)

scroll_productos = ttk.Scrollbar(frame_tabla_productos, orient="vertical", command=tabla_productos.yview)
tabla_productos.configure(yscrollcommand=scroll_productos.set)
scroll_productos.pack(side="right", fill="y")
tabla_productos.pack(fill="both", expand=True)
tabla_productos.bind("<<TreeviewSelect>>", cargar_producto_seleccionado)

# PESTAÑA VENTAS (mantener igual)
frame_ventas = ttk.Frame(notebook)
notebook.add(frame_ventas, text="💰 Ventas")

frame_form_venta = ttk.LabelFrame(frame_ventas, text="📝 Registrar Venta")
frame_form_venta.pack(fill="x", padx=10, pady=5)

tk.Label(frame_form_venta, text="Cliente*:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
combo_cliente_venta = ttk.Combobox(frame_form_venta, width=25, state="readonly")
combo_cliente_venta.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_form_venta, text="Total*:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
entry_venta_total = tk.Entry(frame_form_venta, width=20)
entry_venta_total.grid(row=0, column=3, padx=5, pady=5)

frame_botones_venta = ttk.Frame(frame_ventas)
frame_botones_venta.pack(fill="x", padx=10, pady=5)

tk.Button(frame_botones_venta, text="💰 Registrar Venta", command=crear_venta, bg="#76c893", width=15).pack(side="left", padx=5)
tk.Button(frame_botones_venta, text="🧹 Limpiar Campos", command=limpiar_campos_venta, bg="#ffca3a", width=15).pack(side="left", padx=5)
tk.Button(frame_botones_venta, text="🔄 Actualizar Lista", command=cargar_ventas, bg="#1982c4", width=15).pack(side="left", padx=5)
tk.Button(frame_botones_venta, text="📊 Generar Reporte", command=generar_reporte_ventas, bg="#9c89b8", width=15).pack(side="left", padx=5)

frame_tabla_ventas = ttk.Frame(frame_ventas)
frame_tabla_ventas.pack(fill="both", expand=True, padx=10, pady=5)

columnas_ventas = ("ID", "Cliente", "Fecha", "Total")
tabla_ventas = ttk.Treeview(frame_tabla_ventas, columns=columnas_ventas, show="headings", height=12)
for col in columnas_ventas:
    tabla_ventas.heading(col, text=col)
    tabla_ventas.column(col, width=150)

scroll_ventas = ttk.Scrollbar(frame_tabla_ventas, orient="vertical", command=tabla_ventas.yview)
tabla_ventas.configure(yscrollcommand=scroll_ventas.set)
scroll_ventas.pack(side="right", fill="y")
tabla_ventas.pack(fill="both", expand=True)

# PESTAÑA PEDIDOS (mantener igual)
frame_pedidos = ttk.Frame(notebook)
notebook.add(frame_pedidos, text="📋 Pedidos")

frame_form_pedido = ttk.LabelFrame(frame_pedidos, text="🛒 Crear Nuevo Pedido")
frame_form_pedido.pack(fill="x", padx=10, pady=5)

tk.Label(frame_form_pedido, text="Cliente:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
combo_cliente_pedido = ttk.Combobox(frame_form_pedido, width=25, state="readonly")
combo_cliente_pedido.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_form_pedido, text="Producto:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
combo_producto_pedido = ttk.Combobox(frame_form_pedido, width=30, state="readonly")
combo_producto_pedido.grid(row=0, column=3, padx=5, pady=5)

tk.Label(frame_form_pedido, text="Cantidad:").grid(row=0, column=4, padx=5, pady=5, sticky="e")
entry_cantidad_pedido = tk.Entry(frame_form_pedido, width=10)
entry_cantidad_pedido.grid(row=0, column=5, padx=5, pady=5)

frame_botones_producto_pedido = ttk.Frame(frame_form_pedido)
frame_botones_producto_pedido.grid(row=1, column=0, columnspan=6, pady=5)

tk.Button(frame_botones_producto_pedido, text="➕ Agregar Producto", command=agregar_producto_pedido, bg="#76c893", width=15).pack(side="left", padx=5)
tk.Button(frame_botones_producto_pedido, text="🗑️ Quitar Producto", command=eliminar_producto_pedido, bg="#ff595e", width=15).pack(side="left", padx=5)

frame_tabla_productos_pedido = ttk.Frame(frame_form_pedido)
frame_tabla_productos_pedido.grid(row=2, column=0, columnspan=6, pady=5, sticky="ew")

columnas_productos_pedido = ("Producto", "Cantidad", "Precio Unitario", "Subtotal")
tabla_productos_pedido = ttk.Treeview(frame_tabla_productos_pedido, columns=columnas_productos_pedido, show="headings", height=6)
for col in columnas_productos_pedido:
    tabla_productos_pedido.heading(col, text=col)
    tabla_productos_pedido.column(col, width=120)

scroll_productos_pedido = ttk.Scrollbar(frame_tabla_productos_pedido, orient="vertical", command=tabla_productos_pedido.yview)
tabla_productos_pedido.configure(yscrollcommand=scroll_productos_pedido.set)
scroll_productos_pedido.pack(side="right", fill="y")
tabla_productos_pedido.pack(fill="both", expand=True)

frame_total_pedido = ttk.Frame(frame_form_pedido)
frame_total_pedido.grid(row=3, column=0, columnspan=6, pady=5)

tk.Label(frame_total_pedido, text="Total del Pedido:", font=("Arial", 10, "bold")).pack(side="left", padx=5)
entry_total_pedido = tk.Entry(frame_total_pedido, width=15, font=("Arial", 10, "bold"))
entry_total_pedido.pack(side="left", padx=5)

frame_botones_pedido = ttk.Frame(frame_pedidos)
frame_botones_pedido.pack(fill="x", padx=10, pady=5)

tk.Button(frame_botones_pedido, text="✅ Crear Pedido", command=crear_pedido, bg="#76c893", width=15).pack(side="left", padx=5)
tk.Button(frame_botones_pedido, text="🧹 Limpiar Todo", command=limpiar_pedido, bg="#ffca3a", width=15).pack(side="left", padx=5)
tk.Button(frame_botones_pedido, text="📋 Ver Detalle", command=ver_detalle_pedido, bg="#1982c4", width=15).pack(side="left", padx=5)
tk.Button(frame_botones_pedido, text="🔄 Actualizar Lista", command=cargar_pedidos, bg="#9c89b8", width=15).pack(side="left", padx=5)

frame_tabla_pedidos = ttk.Frame(frame_pedidos)
frame_tabla_pedidos.pack(fill="both", expand=True, padx=10, pady=5)

columnas_pedidos = ("ID", "Fecha", "Total", "Cliente")
tabla_pedidos = ttk.Treeview(frame_tabla_pedidos, columns=columnas_pedidos, show="headings", height=12)
for col in columnas_pedidos:
    tabla_pedidos.heading(col, text=col)
    tabla_pedidos.column(col, width=150)

scroll_pedidos = ttk.Scrollbar(frame_tabla_pedidos, orient="vertical", command=tabla_pedidos.yview)
tabla_pedidos.configure(yscrollcommand=scroll_pedidos.set)
scroll_pedidos.pack(side="right", fill="y")
tabla_pedidos.pack(fill="both", expand=True)

# BARRA DE ESTADO
frame_estado = ttk.Frame(ventana)
frame_estado.pack(fill="x", side="bottom")
estado = tk.Label(frame_estado, text="Sistema de Gestión Tiendas - Listo", 
                 bd=1, relief=tk.SUNKEN, anchor=tk.W)
estado.pack(fill="x")

# INICIALIZACIÓN
def inicializar():
    try:
        cargar_clientes()
        cargar_productos()
        cargar_ventas()
        cargar_pedidos()
        cargar_clientes_combo()
        cargar_clientes_pedido_combo()
        cargar_productos_pedido_combo()
        estado.config(text="Sistema cargado correctamente - Base de datos: tiendas")
    except Exception as e:
        messagebox.showerror("Error", f"Error al inicializar el sistema:\n{e}")

# Ejecutar inicialización
ventana.after(100, inicializar)
ventana.mainloop()