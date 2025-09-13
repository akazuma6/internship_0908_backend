from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from .models import EmployeeProfile, Attendance, Break, RoleActivity

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']

class BreakSerializer(serializers.ModelSerializer):
    class Meta:
        model = Break
        fields = '__all__'

class RoleActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = RoleActivity
        fields = '__all__'

class AttendanceSerializer(serializers.ModelSerializer):
    breaks = BreakSerializer(many=True, read_only=True)
    role_activities = RoleActivitySerializer(many=True, read_only=True)

    class Meta:
        model = Attendance
        fields = ['id', 'employee', 'check_in', 'check_out', 'breaks', 'role_activities']

class EmployeeProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    hp = serializers.SerializerMethodField()
    current_role = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeProfile
        fields = ['id', 'user', 'employee_number', 'hp', 'current_role']

    def get_hp(self, obj):
        now = timezone.now()
        active_attendance = Attendance.objects.filter(employee=obj, check_out__isnull=True).order_by('-check_in').first()

        if not active_attendance:
            return None

        hp = 10.0

        # 【修正点】休憩終了(break_end)がNoneの場合の計算ロジックを修正
        total_break_seconds = sum([
            ((b.break_end or now) - b.break_start).total_seconds()
            for b in active_attendance.breaks.all()
        ])
        hp += (total_break_seconds / 3600) * 2

        # 役割ごとの消費
        for activity in active_attendance.role_activities.all():
            duration_hours = ((activity.end_time or now) - activity.start_time).total_seconds() / 3600
            if activity.role == RoleActivity.KITCHEN:
                hp -= duration_hours * 1
            elif activity.role == RoleActivity.HALL:
                hp -= duration_hours * 2
        
        return round(hp, 2)

    def get_current_role(self, obj):
        active_attendance = Attendance.objects.filter(employee=obj, check_out__isnull=True).order_by('-check_in').first()

        if active_attendance:
            active_role = RoleActivity.objects.filter(attendance=active_attendance, end_time__isnull=True).first()
            if active_role:
                return active_role.get_role_display()
        
        return None

