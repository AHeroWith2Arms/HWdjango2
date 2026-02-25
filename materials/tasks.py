from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from materials.models import Course, Subscription
from users.models import User


@shared_task
def send_course_update_notifications(course_id: int) -> None:
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return

    subscriptions = Subscription.objects.filter(course=course).select_related('user')
    recipients = [sub.user.email for sub in subscriptions if sub.user.email]

    if not recipients:
        return

    subject = f'Обновление курса: {course.name}'
    message = f'Материалы курса \"{course.name}\" были обновлены.'

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipients,
        fail_silently=True,
    )


@shared_task
def deactivate_inactive_users() -> None:
    threshold = timezone.now() - timedelta(days=30)
    users = User.objects.filter(is_active=True).filter(
        last_login__lt=threshold
    ) | User.objects.filter(is_active=True, last_login__isnull=True)

    for user in users:
        user.is_active = False
        user.save(update_fields=['is_active'])

