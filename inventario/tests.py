# inventario/tests.py

from django.test import TestCase
from .models import Producto, Categoria

class ProductoModelTest(TestCase):

    def setUp(self):
        categoria = Categoria.objects.create(nombre='Test Category')
        Producto.objects.create(nombre='Test Product', descripcion='Test Description', precio=10.00, cantidad=5, categoria=categoria)

    def test_producto_str(self):
        producto = Producto.objects.get(id=1)
        expected_object_name = f'{producto.nombre}'
        self.assertEqual(str(producto), expected_object_name)

class CategoriaModelTest(TestCase):

    def setUp(self):
        Categoria.objects.create(nombre='Test Category')

    def test_categoria_str(self):
        categoria = Categoria.objects.get(id=1)
        expected_object_name = f'{categoria.nombre}'
        self.assertEqual(str(categoria), expected_object_name)
