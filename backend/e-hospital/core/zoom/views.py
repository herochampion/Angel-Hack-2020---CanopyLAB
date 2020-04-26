from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.response import Response
from core.zoom.serializers import MeetingSerializer
from django.utils.translation import gettext as _
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from zoomus import ZoomClient
import json
from datetime import datetime
from core.zoom.models import Meeting
from core.users.authentications import ExpiringTokenAuthentication


ZOOM_API_KEY = 'lHQN-cU-Rhyb2H4FabnIDQ'
ZOOM_API_SECRET = 'fjkBKLVZgaZGp6z6HVCfYWXdaRfiY6EX1VMQ'
MEETING_DURATION = 60
# Create your views here.
class MeetingViewSet(viewsets.ModelViewSet):
    serializer_class = MeetingSerializer
    permissions_classes = [AllowAny]
    authentication_class = [ExpiringTokenAuthentication]
    CREATE_ERROR = _('Error while creating meeting.')
    
    @action(methods=['post'], detail=False, url_path='create-meeting')
    def create_meeting(self, request, *args, **kwargs):
        """
        Create meeting on zoomus and also in database
        Examle params:
        {
            "unit_id": 123,
            "user_id": 123,
            "topic": "Example meeting",
            "start_time": "2020-01-01T00:00:00Z",
            "duration": 60,
            "timezone": "Asia/Bangkok",
            "password": "",
            "agenda": "Example meeting",
            "recurrence": {
                "type": 1,
                "repeat_interval": 1,
                "weekly_days": 1,
                "end_date_time": "2020-01-01T00:00:00Z"
            },
            "settings": {
                "alternative_hosts": "",
                "audio": "both",
                "auto_recording": "local",
                "enforce_login": false,
                "host_video": true,
                "join_before_host": false,
                "mute_upon_entry": true,
                "participant_video": false,
                "waiting_room": false
            }
        }
        """
        from datetime import datetime, timezone, timedelta
        from django.db.models import Min, F
        from core.users.models import HospitalUser
        from core.users.models import DoctorWorkSchedule

        meetings = Meeting.objects.filter(
            user_id=request.user.pk,
            end_time__gte=datetime.now(timezone.utc)
        )
        if meetings:
            return Response({'error': 'You has already created meeting room'}, status=status.HTTP_400_BAD_REQUEST)
        meetings = Meeting.objects.filter(
            end_time__gte=datetime.now(timezone.utc)
        )
        meetings = meetings.values('doctor_id').annotate(
            last_meeting=Min(F('end_time'))
        ).order_by('last_meeting')
        all_doctors = HospitalUser.objects.filter(
            role="doctor"
        )
        tmp_schedules = {}
        for doctor in all_doctors:
            tmp_schedules.update(
                {doctor.pk: {"data": None, "doctor_id": doctor.pk}}
            )
        for meeting in meetings:
            tmp_schedules.update(
                {meeting['doctor_pk']: {"data": meeting, "doctor_id": meeting['doctor_pk'], }}
            )
        available_schedules = []
        for tmp_schedule in tmp_schedules.values():
            if tmp_schedule["data"]:
                schedules = DoctorWorkSchedule.objects.filter(user__pk=tmp_schedule['doctor_id'], end_time__gte=tmp_schedule['data']['last_meeting']).order_by('end_time')
                for schedule in schedules:
                    if tmp_schedule['data']['start_time'] < datetime.now(timezone.utc) and datetime.now(timezone.utc) + timedelta(minutes=MEETING_DURATION) < tmp_schedule['data']['end_time']:
                        start_time = datetime.now(timezone.utc)
                        end_time = datetime.now(timezone.utc) + timedelta(minutes=MEETING_DURATION)
                        available_schedules.append({"doctor": schedule.user, "start_time": start_time, "end_time": end_time})
                    elif tmp_schedule['data']['start_time'] > datetime.now(timezone.utc) and tmp_schedule['data']['start_time'] + timedelta(minutes=MEETING_DURATION) < tmp_schedule['data']['end_time']:
                        start_time = tmp_schedule['data']['start_time']
                        end_time = tmp_schedule['data']['start_time'] + timedelta(minutes=MEETING_DURATION)
                        available_schedules.append({"doctor": schedule.user, "start_time": start_time, "end_time": end_time})
            else:
                schedules = DoctorWorkSchedule.objects.filter(user__pk=tmp_schedule['doctor_id'], end_time__gte=datetime.now(timezone.utc)).order_by('end_time')
                for schedule in schedules:
                    if schedule.start_time < datetime.now(timezone.utc) and datetime.now(timezone.utc) + timedelta(minutes=MEETING_DURATION) < schedule.end_time:
                        start_time = datetime.now(timezone.utc)
                        end_time = datetime.now(timezone.utc) + timedelta(minutes=MEETING_DURATION)
                        available_schedules.append({"doctor": schedule.user, "start_time": start_time, "end_time": end_time})
                    elif schedule.start_time > datetime.now(timezone.utc) and schedule.start_time + timedelta(minutes=MEETING_DURATION) < schedule.end_time:
                        start_time = schedule.start_time
                        end_time = schedule.start_time + timedelta(minutes=MEETING_DURATION)
                        available_schedules.append({"doctor": schedule.user, "start_time": start_time, "end_time": end_time})

        if not available_schedules:
            return Response({'error': 'All doctors are buzy'}, status=status.HTTP_400_BAD_REQUEST)

        available_schedules = sorted(available_schedules, key=lambda x: x['start_time'])

        #get parameters
        data = self.request.data
        user_id = request.user.pk
        
        client = ZoomClient(ZOOM_API_KEY, ZOOM_API_SECRET)

        user_list_response = client.user.list()
        user_list = json.loads(user_list_response.content.decode("utf-8"))

        for user in user_list['users']:
            zoom_user_id = user['id']

        data['user_id'] = zoom_user_id
        data['start_time'] = start_time
        data['duration'] = MEETING_DURATION
        zoom_meeting_data = data

        try:
            #create meeting on zoomus
            response = client.meeting.create(**zoom_meeting_data)
            zoom_meeting = json.loads(client.meeting.create(**zoom_meeting_data).content.decode("utf-8"))
            print(zoom_meeting)
            #create meeting in database
            zoom_meeting['zoomus_meeting_id'] = zoom_meeting.pop('id')
            # zoom_meeting['unit_id'] = unit_id
            zoom_meeting['user_id'] = user_id
            zoom_meeting['end_time'] = end_time
            zoom_meeting.pop('type')
            zoom_meeting.pop('settings')
            
            print(Meeting.objects.all())
            meeting = Meeting.objects.create(**zoom_meeting)
            print("meeting", meeting)
        except Exception as error:
            print(error)
            return Response({'error': self.CREATE_ERROR}, status=status.HTTP_400_BAD_REQUEST)

        data = MeetingSerializer(instance=meeting).data
        return Response(data, status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=False, url_path='get-meetings')
    def get_meetings(self, request):
        """
        Get all meetings of user
        params: no
        """

        client = ZoomClient(ZOOM_API_KEY, ZOOM_API_SECRET)

        user_list_response = client.user.list()
        user_list = json.loads(user_list_response.content.decode('utf-8'))

        for user in user_list['users']:
            user_id = user['id']

        meetings = json.loads(client.meeting.list(user_id=user_id).content.decode('utf-8'))

        return Response(status=status.HTTP_200_OK, data=meetings)

    @action(methods=['post'], detail=False, url_path='get-meeting-detail')
    def get_meeting_detail(self, request):
        """
        Get meeting detail
        Params: id: int, host_id: text
        """
        data = self.request.data

        client = ZoomClient(ZOOM_API_KEY, ZOOM_API_SECRET)

        meetings = json.loads(client.meeting.get(**data).content)

        return Response(status=status.HTTP_200_OK, data=meetings)

    @action(methods=['post'], detail=False, url_path='delete-meeting')
    def delete_meeting(self, request):
        """
        Delete a meeting on zoomus and DB
        params: id: bigint
        """

        client = ZoomClient(ZOOM_API_KEY, ZOOM_API_SECRET)

        id = request.data.get('id', None)
        client.meeting.delete(id=id)

        meeting = Meeting.objects.filter(zoomus_meeting_id=id).first()
        if meeting:
            deleted = meeting.delete()

        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({'error': _('Error while deleting meeting.')}, status=status.HTTP_400_BAD_REQUEST)
