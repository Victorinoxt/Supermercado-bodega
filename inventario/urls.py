from django.urls import path
from . import views

urlpatterns = [
    path('agregar_producto/', views.agregar_producto, name='agregar_producto'),
    path('', views.ver_inventario, name='ver_inventario'),
    path('editar_producto/<int:producto_id>/', views.editar_producto, name='editar_producto'),
    path('eliminar_producto/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
    path('agregar_categoria/', views.agregar_categoria, name='agregar_categoria'),
    path('categorias/', views.ver_categorias, name='ver_categorias'),
    path('editar_categoria/<int:categoria_id>/', views.editar_categoria, name='editar_categoria'),
    path('eliminar_categoria/<int:categoria_id>/', views.eliminar_categoria, name='eliminar_categoria'),
    path('exportar_pdf/', views.exportar_pdf, name='exportar_pdf'),
    path('exportar_excel/', views.exportar_excel, name='exportar_excel'),
    path('reporte_ventas/<str:periodo>/', views.reporte_ventas, name='reporte_ventas'),
    path('agregar_venta/', views.agregar_venta, name='agregar_venta'),
    path('editar_venta/<int:venta_id>/', views.editar_venta, name='editar_venta'),
    path('eliminar_venta/<int:venta_id>/', views.eliminar_venta, name='eliminar_venta'),
    path('generar_factura/<int:venta_id>/', views.generar_factura, name='generar_factura'),
]
