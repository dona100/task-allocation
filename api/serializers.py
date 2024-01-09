from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User,Group,Permission
from .models import Employee,TimeCycle,Allocation,OffDay

class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'is_staff')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password') 
        user = User.objects.create_user(**validated_data)
        user.is_staff = True  
        user.set_password(password)  
        user.save()
        return user
    
class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'  
    

        
class UserSerializer(serializers.ModelSerializer):
    # password = serializers.CharField(write_only=True)
    is_active = serializers.BooleanField(default=True)
    
    class Meta:
        model = User
        fields = ['id','username', 'password','is_active']
    def create(self, validated_data):
        # validated_data['is_active'] = True
        password = validated_data.pop('password')  
        user = User(**validated_data)
        user.set_password(password)  
        user.save()
        return user
    def update(self, instance, validated_data):
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)  # Hash the new password
        return super().update(instance, validated_data)
    
class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'
    
class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'

class TimeCycleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeCycle
        fields = ('id', 'time_cycle_name', 'start_date', 'end_date','is_active')


class AllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Allocation
        fields = ['id', 'employee', 'time_cycle','date', 'task']




class OffDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = OffDay
        fields = '__all__'