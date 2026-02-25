from rest_framework import serializers
from urllib.parse import urlparse


def validate_youtube_url(value):
    if value:
        parsed_url = urlparse(value)
        allowed_domains = ['youtube.com', 'www.youtube.com', 'youtu.be']
        
        if parsed_url.netloc not in allowed_domains:
            raise serializers.ValidationError(
                'Разрешены только ссылки на youtube.com'
            )
    
    return value


class YouTubeURLValidator:
    def __init__(self, field='video_url'):
        self.field = field

    def __call__(self, attrs):
        field_value = attrs.get(self.field)
        if field_value:
            parsed_url = urlparse(field_value)
            allowed_domains = ['youtube.com', 'www.youtube.com', 'youtu.be']
            
            if parsed_url.netloc not in allowed_domains:
                raise serializers.ValidationError(
                    {self.field: 'Разрешены только ссылки на youtube.com'}
                )
        
        return attrs