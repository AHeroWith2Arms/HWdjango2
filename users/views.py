from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
from materials.models import Course, Lesson
from users.models import Payment, User
from users.serializers import PaymentSerializer, UserSerializer, UserRegistrationSerializer, PaymentStripeSerializer
from users.services import create_stripe_product, create_stripe_price, create_stripe_session, retrieve_stripe_session


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['paid_course', 'paid_lesson', 'payment_method']
    ordering_fields = ['payment_date']
    ordering = ['-payment_date']

    @action(detail=False, methods=['post'], url_path='create-payment-intent')
    def create_payment_intent(self, request):
        """
        Создание платежа через Stripe.
        
        Принимает course_id или lesson_id, создает продукт и цену в Stripe,
        создает сессию оплаты и возвращает ссылку на оплату.
        """
        serializer = PaymentStripeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        course_id = serializer.validated_data.get('course_id')
        lesson_id = serializer.validated_data.get('lesson_id')

        if course_id:
            try:
                course = Course.objects.get(id=course_id)
                product_name = course.name
                product_description = course.description or ''
                amount = course.price if hasattr(course, 'price') else 0
            except Course.DoesNotExist:
                return Response({'error': 'Курс не найден'}, status=status.HTTP_404_NOT_FOUND)
        else:
            try:
                lesson = Lesson.objects.get(id=lesson_id)
                product_name = lesson.name
                product_description = lesson.description or ''
                amount = lesson.price if hasattr(lesson, 'price') else 0
            except Lesson.DoesNotExist:
                return Response({'error': 'Урок не найден'}, status=status.HTTP_404_NOT_FOUND)

        if amount <= 0:
            return Response({'error': 'Цена должна быть больше нуля'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = create_stripe_product(product_name, product_description)
            price = create_stripe_price(product.id, float(amount))

            success_url = f"{settings.FRONTEND_URL or 'http://localhost:8000'}/payment/success?session_id={{CHECKOUT_SESSION_ID}}"
            cancel_url = f"{settings.FRONTEND_URL or 'http://localhost:8000'}/payment/cancel"

            session = create_stripe_session(price.id, success_url, cancel_url)

            payment = Payment.objects.create(
                user=user,
                paid_course_id=course_id if course_id else None,
                paid_lesson_id=lesson_id if lesson_id else None,
                amount=amount,
                payment_method='stripe',
                stripe_product_id=product.id,
                stripe_price_id=price.id,
                stripe_session_id=session.id,
                payment_url=session.url,
                payment_status=session.payment_status,
            )

            response_serializer = PaymentSerializer(payment)
            return Response({
                'payment': response_serializer.data,
                'payment_url': session.url
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='check-status')
    def check_status(self, request, pk=None):
        """
        Проверка статуса платежа в Stripe.
        
        Получает актуальный статус платежа из Stripe и обновляет его в базе данных.
        """
        payment = self.get_object()

        if not payment.stripe_session_id:
            return Response({'error': 'Платеж не связан со Stripe'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            session = retrieve_stripe_session(payment.stripe_session_id)
            payment.payment_status = session.payment_status
            payment.save()

            response_serializer = PaymentSerializer(payment)
            return Response({
                'payment': response_serializer.data,
                'stripe_status': session.payment_status
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        return UserSerializer

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)