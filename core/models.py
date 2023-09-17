from django.db import models

class Employee(models.Model):
    name = models.CharField(max_length=40,unique=True)
    age = models.IntegerField()
    department = models.CharField(max_length=40)


    
