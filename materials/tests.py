from django.test import TestCase
from django.contrib.auth.models import Group
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User
from materials.models import Course, Lesson, Subscription


class LessonCRUDTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        self.user1 = User.objects.create(
            email='user1@test.com',
        )
        self.user1.set_password('testpass123')
        self.user1.save()
        
        self.user2 = User.objects.create(
            email='user2@test.com',
        )
        self.user2.set_password('testpass123')
        self.user2.save()
        
        self.moderator_group = Group.objects.create(name='Модераторы')
        self.moderator = User.objects.create(
            email='moderator@test.com',
        )
        self.moderator.set_password('testpass123')
        self.moderator.save()
        self.moderator.groups.add(self.moderator_group)
        
        self.course1 = Course.objects.create(
            name='Test Course 1',
            description='Test Description 1',
            owner=self.user1
        )
        
        self.course2 = Course.objects.create(
            name='Test Course 2',
            description='Test Description 2',
            owner=self.user2
        )
        
        self.lesson1 = Lesson.objects.create(
            name='Test Lesson 1',
            description='Test Description 1',
            course=self.course1,
            video_url='https://www.youtube.com/watch?v=test123',
            owner=self.user1
        )
        
        self.lesson2 = Lesson.objects.create(
            name='Test Lesson 2',
            description='Test Description 2',
            course=self.course2,
            video_url='https://youtu.be/test456',
            owner=self.user2
        )

    def test_create_lesson(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'name': 'New Lesson',
            'description': 'New Description',
            'course': self.course1.id,
            'video_url': 'https://www.youtube.com/watch?v=new123'
        }
        response = self.client.post('/api/lessons/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 3)

    def test_create_lesson_invalid_url(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'name': 'New Lesson',
            'description': 'New Description',
            'course': self.course1.id,
            'video_url': 'https://vimeo.com/test123'
        }
        response = self.client.post('/api/lessons/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_lessons_owner(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/lessons/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Lesson 1')

    def test_list_lessons_moderator(self):
        self.client.force_authenticate(user=self.moderator)
        response = self.client.get('/api/lessons/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_retrieve_lesson_owner(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/lessons/{self.lesson1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Lesson 1')

    def test_retrieve_lesson_not_owner(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/lessons/{self.lesson2.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_lesson_owner(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'name': 'Updated Lesson',
            'description': 'Updated Description',
            'course': self.course1.id,
            'video_url': 'https://www.youtube.com/watch?v=updated123'
        }
        response = self.client.patch(f'/api/lessons/{self.lesson1.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson1.refresh_from_db()
        self.assertEqual(self.lesson1.name, 'Updated Lesson')

    def test_update_lesson_moderator(self):
        self.client.force_authenticate(user=self.moderator)
        data = {
            'name': 'Updated by Moderator',
        }
        response = self.client.patch(f'/api/lessons/{self.lesson1.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson1.refresh_from_db()
        self.assertEqual(self.lesson1.name, 'Updated by Moderator')

    def test_update_lesson_not_owner(self):
        self.client.force_authenticate(user=self.user2)
        data = {
            'name': 'Hacked Lesson',
        }
        response = self.client.patch(f'/api/lessons/{self.lesson1.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_lesson_owner(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(f'/api/lessons/{self.lesson1.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 1)

    def test_delete_lesson_moderator(self):
        self.client.force_authenticate(user=self.moderator)
        response = self.client.delete(f'/api/lessons/{self.lesson1.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_lesson_not_owner(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.delete(f'/api/lessons/{self.lesson1.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class SubscriptionTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        self.user1 = User.objects.create(
            email='user1@test.com',
        )
        self.user1.set_password('testpass123')
        self.user1.save()
        
        self.user2 = User.objects.create(
            email='user2@test.com',
        )
        self.user2.set_password('testpass123')
        self.user2.save()
        
        self.course1 = Course.objects.create(
            name='Test Course 1',
            description='Test Description 1',
            owner=self.user1
        )
        
        self.course2 = Course.objects.create(
            name='Test Course 2',
            description='Test Description 2',
            owner=self.user2
        )

    def test_subscribe_to_course(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(f'/api/courses/{self.course1.id}/subscribe/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Subscription.objects.filter(user=self.user1, course=self.course1).exists())

    def test_subscribe_to_course_twice(self):
        self.client.force_authenticate(user=self.user1)
        Subscription.objects.create(user=self.user1, course=self.course1)
        response = self.client.post(f'/api/courses/{self.course1.id}/subscribe/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Subscription.objects.filter(user=self.user1, course=self.course1).count(), 1)

    def test_unsubscribe_from_course(self):
        self.client.force_authenticate(user=self.user1)
        Subscription.objects.create(user=self.user1, course=self.course1)
        response = self.client.delete(f'/api/courses/{self.course1.id}/unsubscribe/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Subscription.objects.filter(user=self.user1, course=self.course1).exists())

    def test_unsubscribe_from_course_not_subscribed(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(f'/api/courses/{self.course1.id}/unsubscribe/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_is_subscribed_in_course_serializer(self):
        self.client.force_authenticate(user=self.user1)
        Subscription.objects.create(user=self.user1, course=self.course1)
        response = self.client.get(f'/api/courses/{self.course1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_subscribed'])

    def test_is_not_subscribed_in_course_serializer(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/courses/{self.course1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_subscribed'])

    def test_subscribe_different_users(self):
        self.client.force_authenticate(user=self.user1)
        Subscription.objects.create(user=self.user1, course=self.course1)
        
        self.client.force_authenticate(user=self.user2)
        Subscription.objects.create(user=self.user2, course=self.course1)
        
        self.assertEqual(Subscription.objects.filter(course=self.course1).count(), 2)