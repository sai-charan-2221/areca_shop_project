from django.db import models


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Plate', 'Plate'),
        ('Spoon', 'Spoon'),
        ('Fork', 'Fork'),
        ('Bowl', 'Bowl'),
        ('Cup', 'Cup'),
        ('Knife', 'Knife')

    ]
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    price = models.FloatField()
    image = models.ImageField(upload_to='products/')
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

