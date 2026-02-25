from rest_framework import serializers
from users.models import User, Payment
from materials.serializers import CourseSerializer, LessonSerializer


class PaymentSerializer(serializers.ModelSerializer):
    paid_course = CourseSerializer(read_only=True)
    paid_lesson = LessonSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = '__all__'


class PaymentStripeSerializer(serializers.Serializer):
    course_id = serializers.IntegerField(required=False, allow_null=True)
    lesson_id = serializers.IntegerField(required=False, allow_null=True)

    def validate(self, data):
        if not data.get('course_id') and not data.get('lesson_id'):
            raise serializers.ValidationError('Необходимо указать либо course_id, либо lesson_id')
        if data.get('course_id') and data.get('lesson_id'):
            raise serializers.ValidationError('Нельзя указать одновременно и course_id, и lesson_id')
        return data


class UserSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'first_name', 'last_name', 'phone', 'city', 'avatar', 'payments']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'phone', 'city']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user