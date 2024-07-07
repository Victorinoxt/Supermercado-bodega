# inventario/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from .models import Producto, Categoria, Venta, DetalleVenta
from .forms import ProductoForm, CategoriaForm, VentaForm, DetalleVentaForm

import csv
import io
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
import xlwt
from datetime import datetime, timedelta

@login_required
def agregar_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto agregado exitosamente.')
            return redirect('ver_inventario')
    else:
        form = ProductoForm()
    return render(request, 'inventario/agregar_producto.html', {'form': form})

@login_required
def ver_inventario(request):
    query = request.GET.get('q')
    categoria = request.GET.get('categoria')
    precio_min = request.GET.get('precio_min')
    precio_max = request.GET.get('precio_max')

    productos_list = Producto.objects.all()

    if query:
        productos_list = productos_list.filter(
            Q(nombre__icontains=query) | Q(descripcion__icontains=query)
        )

    if categoria:
        productos_list = productos_list.filter(categoria__id=categoria)

    if precio_min:
        productos_list = productos_list.filter(precio__gte=precio_min)

    if precio_max:
        productos_list = productos_list.filter(precio__lte=precio_max)

    paginator = Paginator(productos_list, 10)
    page_number = request.GET.get('page')
    productos = paginator.get_page(page_number)

    categorias = Categoria.objects.all()

    context = {
        'productos': productos,
        'query': query,
        'categorias': categorias,
        'categoria_selected': int(categoria) if categoria else None,
        'precio_min': precio_min,
        'precio_max': precio_max
    }

    return render(request, 'inventario/ver_inventario.html', context)

@login_required
def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado exitosamente.')
            return redirect('ver_inventario')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'inventario/editar_producto.html', {'form': form})

@login_required
def eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    producto.delete()
    messages.success(request, 'Producto eliminado exitosamente.')
    return redirect('ver_inventario')

@login_required
def agregar_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría agregada exitosamente.')
            return redirect('ver_categorias')
    else:
        form = CategoriaForm()
    return render(request, 'inventario/agregar_categoria.html', {'form': form})

@login_required
def ver_categorias(request):
    categorias = Categoria.objects.all()
    return render(request, 'inventario/ver_categorias.html', {'categorias': categorias})

@login_required
def editar_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría actualizada exitosamente.')
            return redirect('ver_categorias')
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, 'inventario/editar_categoria.html', {'form': form})

@login_required
def eliminar_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    categoria.delete()
    messages.success(request, 'Categoría eliminada exitosamente.')
    return redirect('ver_categorias')

def inicio(request):
    return redirect('ver_inventario')

@login_required
def exportar_pdf(request):
    productos = Producto.objects.all()
    context = {'productos': productos}
    html = render_to_string('inventario/exportar_pdf.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="inventario.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Hubo un error al generar el PDF')
    return response

@login_required
def exportar_excel(request):
    productos = Producto.objects.all()
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="inventario.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Inventario')

    row_num = 0
    columns = ['Nombre', 'Descripción', 'Precio', 'Cantidad', 'Categoría']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num])

    for producto in productos:
        row_num += 1
        ws.write(row_num, 0, producto.nombre)
        ws.write(row_num, 1, producto.descripcion)
        ws.write(row_num, 2, producto.precio)
        ws.write(row_num, 3, producto.cantidad)
        ws.write(row_num, 4, producto.categoria.nombre)

    wb.save(response)
    return response

@login_required
def reporte_ventas(request, periodo):
    hoy = datetime.now().date()
    
    if periodo == 'dia':
        ventas = Venta.objects.filter(fecha=hoy)
        periodo_str = hoy.strftime('%d/%m/%Y')
    elif periodo == 'mes':
        primer_dia_mes = hoy.replace(day=1)
        ventas = Venta.objects.filter(fecha__gte=primer_dia_mes, fecha__lte=hoy)
        periodo_str = hoy.strftime('%m/%Y')
    elif periodo == 'anio':
        primer_dia_anio = hoy.replace(month=1, day=1)
        ventas = Venta.objects.filter(fecha__gte=primer_dia_anio, fecha__lte=hoy)
        periodo_str = hoy.strftime('%Y')
    else:
        ventas = Venta.objects.none()
        periodo_str = ''

    total_ventas = ventas.aggregate(total=Sum('total'))['total'] or 0

    context = {
        'ventas': ventas,
        'periodo': periodo_str,
        'total_ventas': total_ventas,
    }
    
    return render(request, 'inventario/reporte_ventas.html', context)

@login_required
def agregar_venta(request):
    productos = Producto.objects.all()
    if request.method == 'POST':
        form = VentaForm(request.POST)
        if form.is_valid():
            venta = form.save(commit=False)
            venta.nombre_cliente = request.POST.get('nombre_cliente')
            venta.apellido_cliente = request.POST.get('apellido_cliente')
            venta.total = 0  # Inicializa el total en 0
            venta.save()
            total_venta = 0
            for producto_id, unidades in zip(request.POST.getlist('productos'), request.POST.getlist('unidades')):
                producto = get_object_or_404(Producto, id=producto_id)
                unidades = int(unidades)
                precio_total = producto.precio * unidades
                total_venta += precio_total
                DetalleVenta.objects.create(venta=venta, producto=producto, cantidad=unidades, precio_unitario=producto.precio, precio_total=precio_total)
            venta.total = total_venta  # Actualiza el total de la venta
            venta.save()
            messages.success(request, 'Venta realizada exitosamente.')
            return redirect('reporte_ventas', periodo='dia')
    else:
        form = VentaForm()
    return render(request, 'inventario/agregar_venta.html', {'form': form, 'productos': productos})

@login_required
def editar_venta(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)
    productos = Producto.objects.all()
    if request.method == 'POST':
        form = VentaForm(request.POST, instance=venta)
        if form.is_valid():
            venta = form.save(commit=False)
            DetalleVenta.objects.filter(venta=venta).delete()
            total_venta = 0
            for producto_id, unidades in zip(request.POST.getlist('productos'), request.POST.getlist('unidades')):
                producto = get_object_or_404(Producto, id=producto_id)
                unidades = int(unidades)
                precio_total = producto.precio * unidades
                total_venta += precio_total
                DetalleVenta.objects.create(venta=venta, producto=producto, cantidad=unidades, precio_unitario=producto.precio, precio_total=precio_total)
            venta.total = total_venta  # Actualiza el total de la venta
            venta.save()
            messages.success(request, 'Venta actualizada exitosamente.')
            return redirect('reporte_ventas', periodo='dia')
    else:
        form = VentaForm(instance=venta)
        detalles = DetalleVenta.objects.filter(venta=venta)
        detalle_venta_data = [{'producto': detalle.producto.id, 'cantidad': detalle.cantidad} for detalle in detalles]
    return render(request, 'inventario/editar_venta.html', {'form': form, 'productos': productos, 'detalle_venta_data': detalle_venta_data})

@login_required
def eliminar_venta(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)
    venta.delete()
    messages.success(request, 'Venta eliminada exitosamente.')
    return redirect('reporte_ventas', periodo='dia')

@login_required
def generar_factura(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)
    detalles = DetalleVenta.objects.filter(venta=venta)
    context = {'venta': venta, 'detalles': detalles}
    html = render_to_string('inventario/factura.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="factura_{venta.id}.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Hubo un error al generar el PDF')
    return response
