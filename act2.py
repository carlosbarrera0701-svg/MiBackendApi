import tkinter as tk
from tkinter import messagebox, simpledialog

ventana = tk.Tk()
ventana.title("Sistema de Registro de Ventas")
ventana.geometry("380x420")
ventana.config(padx=20, pady=20)


def registrar_ventas():

    try:
        cant_ventas = int(entry_num_ventas.get())
        if cant_ventas <= 0:
            messagebox.showerror("Error", "La cantidad de ventas debe ser mayor a cero.")
            return
    except ValueError:
        messagebox.showerror("Error", "Ingresa un número entero válido en la cantidad.")
        return

    ventas = []

    for i in range(1, cant_ventas + 1):
        importe = simpledialog.askfloat(
            "Registro de Venta", 
            f"Ingrese el importe de la Venta {i}:", 
            parent=ventana
        )
        
        if importe is None:
            messagebox.showwarning("Atención", "Proceso cancelado por el usuario.")
            return

        if importe <= 0:
            messagebox.showerror("Error", f"El importe de la Venta {i} debe ser mayor a cero.")
            return

        ventas.append(importe)

    total_vendido = sum(ventas)
    promedio_venta = total_vendido / cant_ventas
    venta_mas_alta = max(ventas)

    lbl_res_cantidad.config(text=f"Cantidad de ventas: {cant_ventas}")
    lbl_res_total.config(text=f"Total vendido: ${total_vendido:,.2f}")
    lbl_res_promedio.config(text=f"Promedio por venta: ${promedio_venta:,.2f}")
    lbl_res_mas_alta.config(text=f"Venta más alta: ${venta_mas_alta:,.2f}")

lbl_titulo = tk.Label(
    ventana, 
    text="SISTEMA DE REGISTRO DE VENTAS", 
    font=("Arial", 11, "bold")
)
lbl_titulo.pack(pady=10)

lbl_solicitud = tk.Label(ventana, text="¿Cuántas ventas quieres registrar?")
lbl_solicitud.pack(pady=5)

entry_num_ventas = tk.Entry(ventana, font=("Arial", 10), justify="center")
entry_num_ventas.pack(pady=5)

btn_registrar = tk.Button(
    ventana, 
    text="Registrar ventas", 
    command=registrar_ventas,
    bg="#2196F3",
    fg="white",
    font=("Arial", 10, "bold"),
    padx=10,
    pady=3
)
btn_registrar.pack(pady=15)

frame_res = tk.LabelFrame(ventana, text=" Resultados ", padx=10, pady=10)
frame_res.pack(fill="both", expand=True)

lbl_res_cantidad = tk.Label(frame_res, text="Cantidad de ventas: -", anchor="w")
lbl_res_cantidad.pack(fill="x", pady=2)

lbl_res_total = tk.Label(frame_res, text="Total vendido: $0.00", anchor="w")
lbl_res_total.pack(fill="x", pady=2)

lbl_res_promedio = tk.Label(frame_res, text="Promedio por venta: $0.00", anchor="w")
lbl_res_promedio.pack(fill="x", pady=2)

lbl_res_mas_alta = tk.Label(frame_res, text="Venta más alta: $0.00", anchor="w")
lbl_res_mas_alta.pack(fill="x", pady=2)

ventana.mainloop()