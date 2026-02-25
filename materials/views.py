from datetime import timedelta

from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from materials.models import Course, Lesson, Subscription
from materials.serializers import CourseSerializer, LessonSerializer
from materials.permissions import IsOwnerOrModerator, IsOwnerOrModeratorReadOnly
from materials.paginators import CourseLessonPagination
from materials.tasks import send_course_update_notifications


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrModerator]
    pagination_class = CourseLessonPagination

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Модераторы').exists():
            return Course.objects.all()
        return Course.objects.filter(owner=user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        course = self.get_object()
        previous_update = course.last_update
        now = timezone.now()

        serializer.save()

        if not previous_update or (now - previous_update) >= timedelta(hours=4):
            send_course_update_notifications.delay(course.id)

    @action(detail=True, methods=['post'], url_path='subscribe')
    def subscribe(self, request, pk=None):
        course = self.get_object()
        user = request.user
        
        subscription, created = Subscription.objects.get_or_create(
            user=user,
            course=course
        )
        
        if created:
            return Response({'message': 'Подписка оформлена'}, status=status.HTTP_201_CREATED)
        return Response({'message': 'Вы уже подписаны на этот курс'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'], url_path='unsubscribe')
    def unsubscribe(self, request, pk=None):
        course = self.get_object()
        user = request.user
        
        subscription = Subscription.objects.filter(user=user, course=course).first()
        
        if subscription:
            subscription.delete()
            return Response({'message': 'Подписка отменена'}, status=status.HTTP_200_OK)
        return Response({'message': 'Вы не подписаны на этот курс'}, status=status.HTTP_400_BAD_REQUEST)


class LessonListCreateView(ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrModeratorReadOnly]
    pagination_class = CourseLessonPagination

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Модераторы').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrModeratorReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Модераторы').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)

    def perform_update(self, serializer):
        lesson = self.get_object()
        course = lesson.course
        previous_update = course.last_update
        now = timezone.now()

        serializer.save()

        if not previous_update or (now - previous_update) >= timedelta(hours=4):
            course.last_update = now
            course.save(update_fields=['last_update'])
            send_course_update_notifications.delay(course.id)
