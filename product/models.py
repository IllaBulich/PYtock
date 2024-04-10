from django.db import models
from warehouses.models import Stock
from django.contrib.auth.models import User
from django.utils import timezone

class Product(models.Model):

    name = models.CharField('Название',max_length = 50)
    description = models.TextField('Описание')
    vendor_code = models.CharField('Артикул', max_length = 50)
    quantity_rack = models.IntegerField('Количество на одином стилаже')
    

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return f'/product/{self.id}'
    
    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"


class Item(models.Model):

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)

    quantity = models.IntegerField('Количество')
    purchase_price = models.FloatField('Стоймасть закупки')
    sales_price = models.FloatField('Стоймасть сбыта',blank=True, null=True)
    purchase_date = models.DateField('Дата поступления')
    sales_date = models.DateField('Дата сбыта', blank=True, null=True)
    sold = models.BooleanField('Сбыто', default = False)
    available = models.BooleanField('доступно', default = True)
    soldQuantity = models.IntegerField('Количество cбыто', default = 0)
    responsible = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    

    def get_current_amount(self):
        return self.quantity - self.soldQuantity
    
    def calculation_quantity_rack(self):
        return self.get_current_amount() / self.product.quantity_rack
    
    def get_absolute_url(self):
        return f'/product/item/{self.id}'
    
    def __str__(self):
        return f"{self.product} - {self.stock} - {self.quantity} - {self.purchase_price} - {self.sales_price} - {self.purchase_date} - {self.sales_date} - sold= {self.sold}  - available= {self.available} - {self.soldQuantity} - {self.responsible}"
    
    @classmethod
    def createSaleItem(cls, item_data):
        
        item = cls.objects.get(id=item_data['id'])
        if item.soldQuantity + item_data['quantity'] > item.quantity: 
            return "erorr"
        item.soldQuantity += item_data['quantity']
        if item.soldQuantity == item.quantity:
            item.available = False

        saleItem = cls()
        saleItem.product = item.product
        saleItem.stock = item.stock
        saleItem.quantity = item_data['quantity']
        saleItem.purchase_price = item.purchase_price
        saleItem.purchase_date = item.purchase_date
        saleItem.sales_price = item_data['cost']

        current_date = timezone.now().date()
        saleItem.sales_date = current_date

        saleItem.sold = True
        saleItem.available = False
        item.save()
        saleItem.save()
        
        print('item', item)
        return saleItem