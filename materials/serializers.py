from rest_framework import serializers
from materials.models import Course, Lesson, Subscription
from materials.validators import validate_youtube_url, YouTubeURLValidator


class LessonSerializer(serializers.ModelSerializer):
    video_url = serializers.URLField(validators=[validate_youtube_url], required=False, allow_null=True)

    class Meta:
        model = Lesson
        fields = '__all__'
        validators = [YouTubeURLValidator(field='video_url')]


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(user=request.user, course=obj).exists()
        return False

    class Meta:
        model = Course
        fields = '__all__' 
