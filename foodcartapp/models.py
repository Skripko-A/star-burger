
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import F, Sum, CharField, ForeignKey
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):
    def with_price(self):
        orders = self.prefetch_related('products').annotate(
            total_price=Sum(F('products__price') * F('products__quantity'))
        )
        return orders


class OrderStatusChoice(models.TextChoices):
    MANAGER = u'M', 'Менеджер'
    PICKER = u'P', 'Сборщик'
    COURIER = u'C', 'Курьер'
    ARCHIVE = u'A', 'Архив'
    

class OrderPaymentType(models.TextChoices):
    ONLINE = u'O', 'Онлайн'
    TERMINAL = u'T', 'Картой курьеру'
    CASH = u'C', 'Наличными курьеру'


class Order(models.Model):
    firstname = CharField(
        max_length=25,
        verbose_name='Имя'
        )
    
    lastname = CharField(
        max_length=25,
        verbose_name='Фамилия'
        )
    
    phonenumber = PhoneNumberField(
        db_index=True,
        verbose_name='номер телефона',
        region='RU')
    
    address = models.TextField(
        db_index=True,
        verbose_name='адрес'
        )
    
    status = models.CharField(
        verbose_name='Статус',
        max_length=2,
        choices=OrderStatusChoice.choices,
        default=OrderStatusChoice.MANAGER,
        db_index=True,
    )

    comment = models.TextField(
        verbose_name='Комментарий к заказу',
        blank=True
    )

    created_at = models.DateTimeField(
        verbose_name='Время создания заказа',
        auto_now_add=True,
        db_index=True,
        )

    called_at = models.DateTimeField(
        verbose_name='Время звонка менеджера',
        db_index=True,
        null=True,
        blank=True,
        )

    delivered_at = models.DateTimeField(
        verbose_name='Время доставки заказа',
        db_index=True,
        null=True,
        blank=True,
    )
    
    payment_type = models.CharField(
        verbose_name='Способ оплаты',
        max_length=2,
        db_index=True,
        choices=OrderPaymentType.choices,
    )

    restaurant = ForeignKey(
        Restaurant,
        related_name='orders',
        verbose_name='Ресторан',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    restaurants = models.ManyToManyField(
        Restaurant,
        verbose_name='Рестораны', 
        related_name='ready_in_restaurants'
        )

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f'{self.firstname}, т. {self.phonenumber}'


class OrderProduct(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='products'
        )
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='products'
        )
    
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(0),
                    MaxValueValidator(100)]
                    )
    
    price = models.DecimalField(
        verbose_name='цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
        )

    def __str__(self):
        return f'{self.quantity} x {self.product.name} x {self.price} in Order {self.order.id}'
