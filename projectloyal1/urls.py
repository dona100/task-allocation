"""projectloyal1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path
from api.views import UserLoginView,UserView,UserListView,UserRoleCreateView,UserRoleListView,AdminView,EmployeeDetailView,EmployeeListCreateView
from api.views import UserToUserrole,PermissionView,UserrolePermissionView,get_employee_permissions,TimeCycleDetail,TimeCycleList,get_timecycle_permissions,TimeCycleTaskAllocation,AllocationUpdate,AllocationDelete,AllocationAPIView,OffDayListCreateView,OffDayDeleteView,ActiveTimeCycle
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from rest_framework.authtoken.views import ObtainAuthToken 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/admin/', AdminView.as_view(), name='admin'),
    path('api/user/login/', UserLoginView.as_view(), name='user-view'),
    path('api/users/', UserView.as_view(), name='user'),
    path('api/users/all/', UserListView.as_view(), name='user_list'),
    path('api/users/<int:user_id>/', UserView.as_view(), name='user'),
    path('api/user-roles/create/', UserRoleCreateView.as_view(), name='user_role_create'),
    path('api/user-roles/all/', UserRoleListView.as_view(), name='user-roles-list'),
    path('api/user-roles/<int:group_pk>/', UserRoleCreateView.as_view(), name='user_role'),
    path("jwt/token/",TokenObtainPairView.as_view()),
    path("jwt/token/refresh/",TokenRefreshView.as_view()),
    path("token/",ObtainAuthToken.as_view()),
    path('api/employees/', EmployeeListCreateView.as_view()),
    path('api/employees/all/', EmployeeListCreateView.as_view()),
    path('api/employees/<int:employee_id>/', EmployeeDetailView.as_view()),

    path('api/user-to-userrole/<int:user_pk>/<int:group_pk>/', UserToUserrole.as_view(), name='user-to-userrole'),
    path('api/permissions/',PermissionView.as_view(), name='permission'),
    path('api/permissions/<int:permission_id>/',PermissionView.as_view(), name='permission'),
    path('api/employee-permissions/', get_employee_permissions, name='get_employee_permissions'),
    path('api/userrole-permission/<int:group_pk>/<int:permission_pk>/',UserrolePermissionView.as_view(), name='userrole-permission'),
    path('api/userrole-permission/<int:group_pk>/',UserrolePermissionView.as_view(), name='userrole-permission-list'),
    path('api/time-cycle/', TimeCycleList.as_view()),
    
    path('api/time-cycle/<int:time_cycle_id>/', TimeCycleDetail.as_view()),
    path('api/timecycle-permissions/', get_timecycle_permissions, name='get_timecycle_permissions'),
    path('api/timecycle/<int:time_cycle_id>/allocate/', TimeCycleTaskAllocation.as_view(), name='allocate-timecycle'),
    path('api/allocation/add/', AllocationUpdate.as_view(), name='update-allocation'),
    path('api/allocation/remove/',AllocationDelete.as_view(), name='delete-allocation'),
    path('api/allocations/<int:time_cycle_id>/', AllocationAPIView.as_view(), name='allocation-list'),
    path('api/offdays/', OffDayListCreateView.as_view(), name='offday-list-create'),
    path('api/offdays/<int:pk>/', OffDayDeleteView.as_view(), name='offday-delete'),
    path('api/active-time-cycle/', ActiveTimeCycle.as_view(), name='active-time-cycle'),
]