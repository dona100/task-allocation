
from rest_framework.views import APIView,View
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from api.serializers import UserSerializer,AdminSerializer,EmployeeSerializer,PermissionSerializer,GroupSerializer,TimeCycleSerializer,AllocationSerializer,OffDaySerializer
from api.models import Employee,TimeCycle,Allocation,OffDay
from django.contrib.auth.models import User,Group,Permission
from rest_framework.permissions import IsAuthenticated,IsAdminUser,DjangoModelPermissions,AllowAny
from rest_framework.decorators import authentication_classes,permission_classes,api_view
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import TokenAuthentication
from .permissions import IsSuperUser,CustomDjangoModelPermissions
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import date,timedelta,datetime


class AdminView(APIView):
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated,IsSuperUser]
    def post(self, request):
        serializer = AdminSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(is_staff=True)  # Ensure is_staff is set to True
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserLoginView(APIView):
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated,AllowAny]
    def get(self, request):
        user = request.user  # Assuming you're using authentication and want to get the current user
        serializer = UserSerializer(user)
        return Response(serializer.data)

    
class UserRoleCreateView(APIView):
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated,IsAdminUser]

    def get(self, request, group_pk):
        try:
            group = get_object_or_404(Group, pk=group_pk)
            users_in_group = group.user_set.all()
            user_data = [{'id': user.id, 'username': user.username} for user in users_in_group]
            return Response(user_data, status=status.HTTP_200_OK)
        except Group.DoesNotExist:
            return Response({"error": f"User role with pk {group_pk} not found."}, status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request):
        serializer =GroupSerializer(data=request.data)
        if serializer.is_valid():
            role_name = serializer.validated_data['name']
            existing_role = Group.objects.filter(name=role_name).first()
            if existing_role:
                return Response({"error": "User role already exists."}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response({"message": "User role created successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserRoleListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        user_roles = Group.objects.all()
        serializer = GroupSerializer(user_roles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    
class UserView(APIView):
    authentication_classes=[JWTAuthentication]
    permission_classes = [IsAuthenticated,IsAdminUser ]
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def get(self, request, user_id):
        user = self.get_user(user_id)
        if user:
            serializer = UserSerializer(user)
            return Response(serializer.data)
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self,request,user_id):
        user = self.get_user(user_id)
        if user:
            serializer = UserSerializer(user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, user_id):
        user = self.get_user(user_id)
        if user:
            user.is_active = False  # Logical deactivation of user account
            user.save()
            return Response({"message": "User deactivated"},status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    def patch(self, request, user_id):
        user = self.get_user(user_id)
        if user:
            user.is_active = True  # Activate the user account
            user.save()
            return Response({"message": "User reactivated"}, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)
    
class UserListView(APIView):
    authentication_classes= [JWTAuthentication]
    permission_classes= [IsAuthenticated,IsAdminUser]
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class UserToUserrole(APIView):
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated,IsAdminUser]
    def put(self, request, user_pk, group_pk):
        try:
            user = User.objects.get(pk=user_pk)
            group = Group.objects.get(pk=group_pk)

            # Add user to the group
            group.user_set.add(user)

            # Grant permissions associated with the group to the user
            group_permissions = group.permissions.all()
            for permission in group_permissions:
                user.user_permissions.add(permission)

            return Response({"message": f"User {user_pk} added to user role {group_pk} successfully with group permissions granted."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": f"User with pk {user_pk} not found."}, status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response({"error": f"User role with pk {group_pk} not found."}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, user_pk, group_pk):
        try:
            user = User.objects.get(pk=user_pk)
            group = Group.objects.get(pk=group_pk)

            # Remove user from the group
            group.user_set.remove(user)

            # Revoke permissions associated with the group from the user
            group_permissions = group.permissions.all()
            user_permissions = user.user_permissions.all()

            for permission in group_permissions:
                # Check if the user has the same permission from other groups
                permission_in_other_groups = Group.objects.filter(permissions=permission).exclude(pk=group_pk).exists()
                
                if permission_in_other_groups:
                    # Check if the user is included in other groups with the same permission
                    other_groups = Group.objects.filter(permissions=permission).exclude(pk=group_pk)
                    for other_group in other_groups:
                        if user in other_group.user_set.all():
                            # If the user is in another group with the same permission, skip revoking
                            continue

                # If the permission is not assigned via any other group or user isn't in those groups, revoke it
                if permission in user_permissions:
                    user.user_permissions.remove(permission)

            return Response({"message": f"User {user_pk} removed from user role {group_pk} successfully with permissions selectively revoked."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": f"User with pk {user_pk} not found."}, status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response({"error": f"User role with pk {group_pk} not found."}, status=status.HTTP_404_NOT_FOUND)
    
class EmployeeListCreateView(APIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated,IsAdminUser | CustomDjangoModelPermissions]
    def get(self, request):
        employees = Employee.objects.all()
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = EmployeeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EmployeeDetailView(APIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated,IsAdminUser | CustomDjangoModelPermissions]
    def get_employee(self, employee_id):
        try:
            return Employee.objects.get(pk=employee_id)
        except Employee.DoesNotExist:
            return None

    def get(self, request, employee_id):
        employee = self.get_employee(employee_id)
        if not employee:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = EmployeeSerializer(employee)
        return Response(serializer.data)

    def put(self, request, employee_id):
        employee = self.get_employee(employee_id)
        if not employee:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = EmployeeSerializer(employee, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, employee_id):
        employee = self.get_employee(employee_id)
        if not employee:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)

        employee.is_active = False
        employee.save()
        return Response({"message": "Employee deactivated"}, status=status.HTTP_204_NO_CONTENT)    

    
class PermissionView(APIView):
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated,IsAdminUser]
    def get(self, request):
        permissions = Permission.objects.all()
        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data)
    
    def delete(self, request, permission_id):
        try:
            permission = Permission.objects.get(pk=permission_id)
        except Permission.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        permission.delete()
        return Response({"message": "Permission deleted"},status=status.HTTP_204_NO_CONTENT)

@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated,IsAdminUser])
@api_view(['GET'])
def get_employee_permissions(request):
    try:
        
        content_type = ContentType.objects.get_for_model(Employee)
        default_permissions = Permission.objects.filter(content_type=content_type)

        permissions_data = []
        for permission in default_permissions:
            permission_data = {
                "id": permission.id,
                "codename": permission.codename,
               
            }
            permissions_data.append(permission_data)

        return Response({"employee_permissions": permissions_data}, status=status.HTTP_200_OK)
    except ContentType.DoesNotExist:
        return Response({"error": "Model content type not found"}, status=status.HTTP_404_NOT_FOUND)
    

class UserrolePermissionView(APIView):
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated,IsAdminUser]
    def get(self, request, group_pk):
        try:
            group = Group.objects.get(pk=group_pk)
        except Group.DoesNotExist:
            return Response("Userrole not found", status=status.HTTP_404_NOT_FOUND)

        permissions = group.permissions.all()
        permission_data = []
        
        for permission in permissions:
            content_type = ContentType.objects.get_for_model(permission.content_type.model_class())
            permission_data.append({
                'id': permission.id,
                'codename': permission.codename,
                'name': permission.name,
                'content_type': {
                    'app_label': content_type.app_label,
                    'model': content_type.model
                }
            })

        return Response(permission_data, status=status.HTTP_200_OK)
    
    def post(self, request, group_pk, permission_pk):
        try:
            group = Group.objects.get(pk=group_pk)
        except Group.DoesNotExist:
            return Response("Userrole not found", status=status.HTTP_404_NOT_FOUND)

        try:
            permission = Permission.objects.get(pk=permission_pk)
        except Permission.DoesNotExist:
            return Response(f"Permission with ID {permission_pk} not found", status=status.HTTP_404_NOT_FOUND)

        # Add permission to the group
        group.permissions.add(permission)

        # Get users within the group
        users = group.user_set.all()

        # Assign the permission to each user
        for user in users:
            user.user_permissions.add(permission)

        return Response("Permission added to the userrole and users", status=status.HTTP_200_OK)
    
    def delete(self, request, group_pk, permission_pk):
        try:
            group = Group.objects.get(pk=group_pk)
        except Group.DoesNotExist:
            return Response("Userrole not found", status=status.HTTP_404_NOT_FOUND)

        try:
            permission = Permission.objects.get(pk=permission_pk)
        except Permission.DoesNotExist:
            return Response(f"Permission with ID {permission_pk} not found", status=status.HTTP_404_NOT_FOUND)
        other_groups_with_permission = Group.objects.filter(permissions=permission).exclude(pk=group_pk)

        if other_groups_with_permission.exists():
            users = group.user_set.all()
            for user in users:
                if permission in user.user_permissions.all():
                        # Check if the user is included in other groups with the same permission
                    other_groups = Group.objects.filter(permissions=permission).exclude(pk=group_pk)
                    for other_group in other_groups:
                        if user in other_group.user_set.all():
                                # If the user is in another group with the same permission, skip revoking
                            break
                    else:
                            # If the user is not in any other group with the same permission, revoke it
                        user.user_permissions.remove(permission)

                # Remove permission from the group
            group.permissions.remove(permission)
            
        else:
                # Remove permission from the group
            group.permissions.remove(permission)

                # Get users within the group
            users = group.user_set.all()

                # Revoke the permission from each user
            for user in users:
                user.user_permissions.remove(permission)

        return Response("Permission removed from the userrole and users", status=status.HTTP_200_OK)


# class TimeCycleList(APIView):
#     queryset = TimeCycle.objects.all()
#     serializer_class = TimeCycleSerializer
#     authentication_classes=[JWTAuthentication]
#     permission_classes=[IsAuthenticated,AllowAny]
#     def get(self, request):
#         time_cycles = TimeCycle.objects.all()
#         serializer = TimeCycleSerializer(time_cycles, many=True)
#         return Response(serializer.data)
    
class TimeCycleList(APIView):
    queryset = TimeCycle.objects.all()
    serializer_class = TimeCycleSerializer
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated,IsAdminUser | CustomDjangoModelPermissions]
    def get(self, request):
        time_cycles = TimeCycle.objects.all()
        serializer = TimeCycleSerializer(time_cycles, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TimeCycleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TimeCycleDetail(APIView):
    queryset = TimeCycle.objects.all()
    serializer_class = TimeCycleSerializer
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated,IsAdminUser | CustomDjangoModelPermissions]
    def get_object(self, time_cycle_id):
        try:
            return TimeCycle.objects.get(id=time_cycle_id)
        except TimeCycle.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND

    def get(self, request, time_cycle_id):
        time_cycle = self.get_object(time_cycle_id)
        serializer = TimeCycleSerializer(time_cycle)
        return Response(serializer.data)

    def put(self, request, time_cycle_id):
        time_cycle = self.get_object(time_cycle_id)
        
        current_date = timezone.now().date()
        if time_cycle.end_date < current_date:
            return Response({"message": "Cannot update an ended time-cycle."}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = TimeCycleSerializer(time_cycle, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, time_cycle_id):
        time_cycle = self.get_object(time_cycle_id)
        current_date = timezone.now().date()
        if time_cycle.end_date < current_date or time_cycle.is_active:
            return Response({"message": "Cannot delete an ended or active time-cycle."}, status=status.HTTP_400_BAD_REQUEST)
        Allocation.objects.filter(time_cycle=time_cycle).delete()
        time_cycle.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated,IsAdminUser])
@api_view(['GET'])    
def get_timecycle_permissions(request):
    try:
       
        content_type = ContentType.objects.get_for_model(TimeCycle)
        default_permissions = Permission.objects.filter(content_type=content_type)

        permissions_data = []
        for permission in default_permissions:
            permission_data = {
                "id": permission.id,
                "codename": permission.codename,
                
            }
            permissions_data.append(permission_data)

        return Response({"time_cycle_permissions": permissions_data}, status=status.HTTP_200_OK)
    except ContentType.DoesNotExist:
        return Response({"error": "Model content type not found"}, status=status.HTTP_404_NOT_FOUND)
    
    
class TimeCycleTaskAllocation(APIView):
    queryset = Allocation.objects.all()
    serializer_class = AllocationSerializer
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated,IsAdminUser | CustomDjangoModelPermissions]
    def post(self, request, time_cycle_id):
        time_cycle = TimeCycle.objects.get(id=time_cycle_id)
        days_within_cycle = self.get_days_within_cycle(time_cycle)
        employees = Employee.objects.all()

        for day in days_within_cycle:
            self.allocate_tasks_for_day(day, employees, time_cycle)

        return Response({'message': 'Allocations created successfully.'}, status=status.HTTP_201_CREATED)

    def get_days_within_cycle(self, time_cycle):
        days_within_cycle = [time_cycle.start_date + timedelta(days=x) for x in range((time_cycle.end_date - time_cycle.start_date).days + 1)]
        return days_within_cycle

    def allocate_tasks_for_day(self, day, employees, time_cycle):
        for employee in employees:
            # Check if allocation already exists for this day and employee
            existing_allocation = Allocation.objects.filter(employee=employee, date=day, time_cycle=time_cycle).exists()
            if not existing_allocation:
                Allocation.objects.create(employee=employee, date=day, task=None, time_cycle=time_cycle)
    def delete(self, request, time_cycle_id):
        try:
            time_cycle = TimeCycle.objects.get(id=time_cycle_id)
            Allocation.objects.filter(time_cycle=time_cycle).delete()
            # Optionally,  delete the time cycle itself
            # time_cycle.delete()
            return Response({'message': 'Time cycle and its allocations deleted successfully.'}, status=status.HTTP_200_OK)
        except TimeCycle.DoesNotExist:
            return Response({'message': 'Time cycle does not exist.'}, status=status.HTTP_404_NOT_FOUND)

class AllocationUpdate(APIView):
    queryset = Allocation.objects.all()
    serializer_class = AllocationSerializer
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated,IsAdminUser | CustomDjangoModelPermissions]
    def put(self, request):
        try:
            employee_name = request.data.get('employee_name')
            allocation_date_str = request.data.get('allocation_date')  # Get allocation date as string
            
            # Convert allocation_date from string to datetime.date
            allocation_date = datetime.strptime(allocation_date_str, '%Y-%m-%d').date()
            
            current_date = date.today()  # Get the current date
            
            # Check if the allocation date is after the current date
            if allocation_date <= current_date:
                return Response({'message': 'Allocation date must be after the current date.'}, status=status.HTTP_400_BAD_REQUEST)

            allocation = Allocation.objects.filter(employee__employee_name=employee_name, date=allocation_date).first()
            
            if not allocation:
                return Response({'message': 'Allocation not found.'}, status=status.HTTP_404_NOT_FOUND)

            serializer = AllocationSerializer(allocation, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(task=request.data.get('task'))
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)



class AllocationDelete(APIView):
    queryset = Allocation.objects.all()
    serializer_class = AllocationSerializer
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated,IsAdminUser | CustomDjangoModelPermissions]
    def put(self, request):
        try:
            employee_name = request.data.get('employee_name')
            allocation_date_str = request.data.get('allocation_date')  # Get allocation date as string
            
            # Convert allocation_date from string to datetime.date
            allocation_date = datetime.strptime(allocation_date_str, '%Y-%m-%d').date()
            
            current_date = date.today()  # Get the current date
            
            # Check if the allocation date is after the current date
            if allocation_date <= current_date:
                return Response({'message': 'Allocation date must be after the current date.'}, status=status.HTTP_400_BAD_REQUEST)
            
            allocation = Allocation.objects.filter(employee__employee_name=employee_name, date=allocation_date).first()
            
            if not allocation:
                return Response({'message': 'Allocation not found.'}, status=status.HTTP_404_NOT_FOUND)

            allocation.task = None
            allocation.save()

            serializer = AllocationSerializer(allocation)
            return Response(serializer.data)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)





class AllocationAPIView(APIView):
    queryset = Allocation.objects.all()
    serializer_class = AllocationSerializer
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated,AllowAny]
    def get(self, request, time_cycle_id):
        try:
            # Fetch all employees and their allocations for a specific time cycle
            employees = Employee.objects.all()
            
            employee_allocations = []
            for employee in employees:
                # Get allocations for each employee in the specified time cycle
                # allocations = Allocation.objects.filter(employee=employee, time_cycle_id=time_cycle_id)
                allocations = Allocation.objects.filter(employee=employee, time_cycle_id=time_cycle_id).exclude(date__in=OffDay.objects.values_list('date', flat=True))
                # Structure allocations for each day using the 'task' field
                days_allocations = []
                for allocation in allocations:
                    days_allocations.append({
                        'date': allocation.date.strftime('%Y-%m-%d'),
                        'task': allocation.task  # Use 'task' field instead of 'active'
                    })
                
                # Structure employee's allocation data
                employee_data = {
                    'employee': {
                        'id': employee.id,
                        'name': employee.employee_name,  
                        'is_active':employee.is_active
                    },
                    'days': days_allocations
                }
                employee_allocations.append(employee_data)

            return Response(employee_allocations)
        except Allocation.DoesNotExist:
            return Response({"message": "Allocations not found for the given time cycle"}, status=404)

class OffDayListCreateView(generics.ListCreateAPIView):
    queryset = OffDay.objects.all()
    serializer_class = OffDaySerializer
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated,IsAdminUser | CustomDjangoModelPermissions]

class OffDayDeleteView(generics.DestroyAPIView):
    queryset = OffDay.objects.all()
    serializer_class = OffDaySerializer
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated,IsAdminUser | CustomDjangoModelPermissions]

class ActiveTimeCycle(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, AllowAny]

    def get(self, request):
        current_date = date.today()
        active_cycle = TimeCycle.objects.filter(start_date__lte=current_date, end_date__gte=current_date).first()

        if active_cycle:
            serializer = TimeCycleSerializer(active_cycle)
            return Response(serializer.data)
        else:
            return Response({"message": "No active time cycle found"}, status=404)

        

    





