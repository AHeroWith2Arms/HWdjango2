from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import User, Payment
from materials.models import Course, Lesson
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Создает тестовые платежи'

    def handle(self, *args, **options):
        users = User.objects.all()
        courses = Course.objects.all()
        lessons = Lesson.objects.all()

        if not users.exists():
            self.stdout.write(self.style.WARNING('Нет пользователей. Создайте пользователей сначала.'))
            return

        if not courses.exists() and not lessons.exists():
            self.stdout.write(self.style.WARNING('Нет курсов и уроков. Создайте их сначала.'))
            return

        payment_methods = ['cash', 'transfer']
        amounts = [Decimal('1000.00'), Decimal('2000.00'), Decimal('3000.00'), Decimal('5000.00'), Decimal('1500.00')]

        payments_created = 0

        for user in users[:5]:
            for _ in range(random.randint(2, 5)):
                if courses.exists() and random.choice([True, False]):
                    course = random.choice(courses)
                    Payment.objects.create(
                        user=user,
                        payment_date=timezone.now(),
                        paid_course=course,
                        paid_lesson=None,
                        amount=random.choice(amounts),
                        payment_method=random.choice(payment_methods)
                    )
                    payments_created += 1
                elif lessons.exists():
                    lesson = random.choice(lessons)
                    Payment.objects.create(
                        user=user,
                        payment_date=timezone.now(),
                        paid_course=None,
                        paid_lesson=lesson,
                        amount=random.choice(amounts),
                        payment_method=random.choice(payment_methods)
                    )
                    payments_created += 1

        self.stdout.write(self.style.SUCCESS(f'Успешно создано {payments_created} платежей'))