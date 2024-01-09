from rest_framework.permissions import BasePermission,IsAdminUser
from rest_framework.permissions import DjangoModelPermissions

class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser
    


# class CustomDjangoModelPermissions(DjangoModelPermissions):
#     def has_permission(self, request, view):
#         if request.method == 'GET':
#             # Check for custom permission for GET method
#             if not request.user.has_perm('api.view_employee'):
#                 return False
#             # if not request.user.has_perm('api.view_timecycle'):
#             #     return False
        
#         # Check for default permissions (add, change, delete) for other methods
#         return super().has_permission(request, view)
    



class CustomDjangoModelPermissions(DjangoModelPermissions):
    def has_permission(self, request, view):
        # Check if the request method is GET
        if request.method == 'GET':
            # Check for custom permission for GET method
            has_employee_permission = request.user.has_perm('api.view_employee')
            has_timecycle_permission = request.user.has_perm('api.view_timecycle')

            # If the user has both permissions, allow access to both models
            if has_employee_permission and has_timecycle_permission:
                return True
            
            # Check for specific permissions and models
            model_name = view.queryset.model.__name__  # Get the model name
            if has_employee_permission and model_name == 'Employee':
                return True
            elif has_timecycle_permission and model_name == 'TimeCycle':
                return True
            
            # Deny access if no appropriate permissions are found for GET requests
            return False
        
        # For other request methods, use default DjangoModelPermissions logic
        return super().has_permission(request, view)

    

