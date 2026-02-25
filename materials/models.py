from django.db import models
from users.models import User


class Course(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    preview = models.ImageField(upload_to='courses/', blank=True, null=True, verbose_name='Превью')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses', verbose_name='Владелец', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Цена')

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ['id']

    def __str__(self):
        return self.name


class Lesson(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    preview = models.ImageField(upload_to='lessons/', blank=True, null=True, verbose_name='Превью')
    video_url = models.URLField(blank=True, null=True, verbose_name='Ссылка на видео')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons', verbose_name='Курс')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lessons', verbose_name='Владелец', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Цена')

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        ordering = ['id']

    def __str__(self):
        return self.name


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions', verbose_name='Пользователь')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='subscriptions', verbose_name='Курс')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        unique_together = ['user', 'course']

    def __str__(self):
        return f'{self.user.email} - {self.course.name}' 
