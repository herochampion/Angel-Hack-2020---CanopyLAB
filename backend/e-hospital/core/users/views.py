from datetime import timezone, datetime

from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.core import signing
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.views import APIView
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK, HTTP_201_CREATED
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.mixins import CreateModelMixin, ListModelMixin, UpdateModelMixin, DestroyModelMixin, RetrieveModelMixin
from rest_framework.decorators import action

from core.users.serializers import HospitalUserSerializer, LoginSerializer, UserTokenSerializer, WorkScheduleSerializer
from core.users.models import HospitalUser, LoginHistory
from core.users.authentications import ExpiringTokenAuthentication


class HospitalUserViewSet(GenericViewSet, ListModelMixin, UpdateModelMixin, RetrieveModelMixin):
    serializer_class = HospitalUserSerializer
    queryset = HospitalUser.objects.all()
    permission_class = [IsAuthenticated]
    authentication_class = [ExpiringTokenAuthentication]

    def list(self, request, *args, **kwargs):
        user = request.user
        if user.role == "doctor":
            return super(HospitalUserViewSet, self).list(request, *args, **kwargs)
        else:
            return Response(status=HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        user = request.user
        if user.role == "doctor":
            return super(HospitalUserViewSet, self).list(request, *args, **kwargs)
        else:
            return Response(status=HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=True, url_path='add-work-schedule')
    def add_work_schedule(self, request, *args, **kwargs):
        user = request.user
        if user.role == "doctor":
            serializer = WorkScheduleSerializer(data=request.data)
            if serializer.is_valid():
                from core.users.models import DoctorWorkSchedule
                from datetime import datetime, timezone
                start_time = serializer.validated_data['start_time']
                end_time = serializer.validated_data['end_time']

                if start_time > end_time:
                    return Response("Start time must be less than end time", status=HTTP_400_BAD_REQUEST)
                if start_time < datetime.now(timezone.utc):
                    return Response("Start time must be greater time now", status=HTTP_400_BAD_REQUEST)
                schedules = DoctorWorkSchedule.objects.filter(
                    user=request.user,
                    end_time__gte=datetime.now(timezone.utc)
                )

                for schedule in schedules:
                    if schedule.start_time <= start_time and schedule.end_time >= start_time:
                        return Response("Conflict the work schedule", status=HTTP_400_BAD_REQUEST)
                    elif schedule.start_time <= end_time and schedule.end_time >= end_time:
                        return Response("Conflict the work schedule", status=HTTP_400_BAD_REQUEST)
                    elif schedule.start_time > start_time and schedule.end_time < end_time:
                        return Response("Conflict the work schedule", status=HTTP_400_BAD_REQUEST)
                DoctorWorkSchedule.objects.create(
                    user=request.user,
                    start_time=start_time,
                    end_time=end_time
                )
                return Response(status=HTTP_201_CREATED)
            else:
                Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
        return Response(status=HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=False, url_path='get-work-schedule')
    def get_work_schedule(self, request, *args, **kwargs):
        user = request.user
        if user.role == "doctor":
            from core.users.models import DoctorWorkSchedule
            schedules = DoctorWorkSchedule.objects.filter(
                    user=request.user,
                    end_time__gte=datetime.now(timezone.utc)
            )

            schedules = sorted(schedules, key=lambda k: k.start_time)
            return Response(WorkScheduleSerializer(instance=schedules, many=True).data, status=HTTP_200_OK)
        return Response(status=HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_class = [AllowAny]
    request_serializer = LoginSerializer
    response_serializer = UserTokenSerializer

    def post(self, request):
        username = request.data.get('username', '')
        serializer = self.request_serializer(data=request.data)
        if serializer.is_valid():
            user = HospitalUser.objects.filter(username=username).first()
            if not user:
                return Response(status=HTTP_400_BAD_REQUEST)
            
            authenticated_user = authenticate(username=username, password=request.data.get('password', ''))
            if not authenticated_user:
                return Response(status=HTTP_400_BAD_REQUEST)

            token, created = Token.objects.get_or_create(user=user)

            if not created:
                token.created = datetime.now()
                token.save()
            if token and authenticated_user:
                login(request, authenticated_user)
                LoginHistory.objects.create(user=request.user, date=datetime.now())
            response = self.response_serializer(token)
            return Response(status=HTTP_200_OK, data=response.data)

        return Response(status=HTTP_400_BAD_REQUEST)

class PredictionUserAccessView(APIView):
    permission_class = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role == "doctor":
            from datetime import date, timedelta
            from django.db.models.functions import Concat, ExtractYear, ExtractMonth, ExtractDay
            from core.users.models import LoginHistory
            from django.db.models import DateTimeField, DateField, F, Count, Value, CharField
            from django.db.models.functions import Cast
            logins = LoginHistory.objects.all()
            logins = logins.annotate(
            time=Concat(
                ExtractYear('date'),
                Value('-'),
                ExtractMonth('date'),
                Value('-'),
                ExtractDay('date'),
                output_field=CharField()
                )
            )

            logins = logins.values('time').annotate(
                number=Count('user')
            ).order_by('time')
            total_logins = 0
            for login in logins:
                total_logins += login['number']
            average = int(total_logins / len(logins))
            return Response(status=HTTP_200_OK, data=[
                {"time": str(date.today() + timedelta(days=1)), "number": average},
                {"time": date.today() + timedelta(days=2), "number": average},
                {"time": date.today() + timedelta(days=3), "number": average}
            ])
        else:
            return Response(status=HTTP_400_BAD_REQUEST)

class SignUpViewSet(GenericViewSet, CreateModelMixin):
    permission_class = [AllowAny]
    serializer_class = HospitalUserSerializer
    queryset = HospitalUser.objects.all()

    def create(self, request, *args, **kwars):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = HospitalUser.objects.create(
                **serializer.validated_data
            )
            user.password = make_password(user.password)
            user.role = "patient"
            user.save()
            return Response(status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
