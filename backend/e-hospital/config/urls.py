"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from core.zoom.views import MeetingViewSet
from core.users.views import HospitalUserViewSet, LoginView, SignUpViewSet, PredictionUserAccessView

router = routers.SimpleRouter()

urlpatterns = [
    path('admin/', admin.site.urls),
]
router.register(
    r'zoom', MeetingViewSet, basename='meeting',
)

router.register(
    r'users', HospitalUserViewSet, basename='users',
)

router.register(
    r'signup', SignUpViewSet, basename='signup',
)

urlpatterns += [
    path('api/', include(router.urls)),
    path('api/login/', LoginView.as_view()),
]
