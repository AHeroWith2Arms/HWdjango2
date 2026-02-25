from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name='Email')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Телефон')
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name='Город')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Аватарка')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Наличные'),
        ('transfer', 'Перевод на счет'),
        ('stripe', 'Stripe'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments', verbose_name='Пользователь')
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата оплаты')
    paid_course = models.ForeignKey('materials.Course', on_delete=models.SET_NULL, null=True, blank=True, related_name='payments', verbose_name='Оплаченный курс')
    paid_lesson = models.ForeignKey('materials.Lesson', on_delete=models.SET_NULL, null=True, blank=True, related_name='payments', verbose_name='Оплаченный урок')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма оплаты')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, verbose_name='Способ оплаты')
    stripe_product_id = models.CharField(max_length=255, blank=True, null=True, verbose_name='ID продукта в Stripe')
    stripe_price_id = models.CharField(max_length=255, blank=True, null=True, verbose_name='ID цены в Stripe')
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True, verbose_name='ID сессии в Stripe')
    payment_url = models.URLField(blank=True, null=True, verbose_name='Ссылка на оплату')
    payment_status = models.CharField(max_length=50, blank=True, null=True, verbose_name='Статус оплаты')

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
        ordering = ['-payment_date']

    def clean(self):
        if not self.paid_course and not self.paid_lesson:
            raise ValidationError('Необходимо указать либо курс, либо урок')
        if self.paid_course and self.paid_lesson:
            raise ValidationError('Нельзя указать одновременно и курс, и урок')

    def __str__(self):
        if self.paid_course:
            return f'{self.user.email} - {self.paid_course.name} - {self.amount}'
        return f'{self.user.email} - {self.paid_lesson.name} - {self.amount}' 
