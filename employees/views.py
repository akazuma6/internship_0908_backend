from django.contrib.auth.models import User
from rest_framework import viewsets
from .models import EmployeeProfile, Attendance, Break, RoleActivity # RoleActivityをインポート
from .serializers import (
    UserSerializer, 
    EmployeeProfileSerializer, 
    AttendanceSerializer, 
    BreakSerializer,
    RoleActivitySerializer # RoleActivitySerializerをインポート
)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

class EmployeeProfileViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeProfileSerializer
    def get_queryset(self):
        queryset = EmployeeProfile.objects.all()
        employee_number = self.request.query_params.get('employee_number', None)
        if employee_number is not None:
            queryset = queryset.filter(employee_number=employee_number)
        return queryset

class AttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceSerializer
    def get_queryset(self):
        # ... (既存のコードは変更なし)
        queryset = Attendance.objects.all()
        employee_id = self.request.query_params.get('employee_profile', None)
        if employee_id is not None:
            queryset = queryset.filter(employee_id=employee_id)
        if self.action == 'list':
            latest = self.request.query_params.get('latest', None)
            if latest is not None and latest.lower() == 'true':
                return queryset.order_by('-check_in')[:1]
            return queryset.order_by('-check_in')[:10]
        return queryset

class BreakViewSet(viewsets.ModelViewSet):
    queryset = Break.objects.all()
    serializer_class = BreakSerializer

# 【新規追加】役割活動のためのAPIビュー
class RoleActivityViewSet(viewsets.ModelViewSet):
    queryset = RoleActivity.objects.all()
    serializer_class = RoleActivitySerializer

