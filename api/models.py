
from django.db import models

class Employee(models.Model):
    employee_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    contact_no = models.CharField(max_length=15)
    address = models.CharField(max_length=255)
    designation = models.CharField(max_length=100)
    is_active= models.BooleanField(default=True)


class TimeCycle(models.Model):
    time_cycle_name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active=models.BooleanField(default=False)
    
    def __str__(self):
        return self.time_cycle_name

class Allocation(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    time_cycle = models.ForeignKey(TimeCycle,on_delete=models.CASCADE)
    date = models.DateField()
    task = models.CharField(max_length=100, null=True, blank=True, default=None)

class OffDay(models.Model):
    date = models.DateField(unique=True)  # Store the date of the off day

    def __str__(self):
        return str(self.date)