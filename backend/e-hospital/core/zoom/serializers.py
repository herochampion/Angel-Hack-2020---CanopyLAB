from rest_framework import serializers
from core.zoom.models import Meeting

class MeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = (
            'uuid', 'host_id', 'topic', 'status', 'start_time', 'duration', 'timezone', 'agenda', 
            'created_at', 'start_url', 'join_url', 'zoomus_meeting_id', 'user_id'
        )