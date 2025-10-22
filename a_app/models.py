from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class staffdata(models.Model):
    name = models.CharField(max_length=600)
    email = models.EmailField()
    design = models.CharField(max_length=1000,default='Staff')
    dob = models.DateField()
    gender = models.CharField(max_length=600)
    phoneno = models.BigIntegerField()
    photo = models.ImageField(upload_to='staffs/')
    USER = models.OneToOneField(User, on_delete=models.CASCADE) 

class academicyear(models.Model):
    year = models.CharField(max_length=500)
    
class semester(models.Model):
    sem = models.IntegerField()

class semdata(models.Model):
    SEM = models.ForeignKey(semester,on_delete=models.CASCADE)
    YEAR = models.ForeignKey(academicyear,on_delete=models.CASCADE)
    
class subjectdata(models.Model):
    code = models.CharField(max_length=300)
    name = models.CharField(max_length=1000)
    syllabus = models.TextField(null=True, blank=True)
    STAFF = models.ForeignKey(staffdata,on_delete=models.CASCADE,null=True, blank=True)
    SEM = models.ForeignKey(semester,on_delete=models.CASCADE)

class studentdata(models.Model):
    name = models.CharField(max_length=600)
    email = models.EmailField()
    rollno = models.CharField(max_length=500)
    dob = models.DateField()
    gender = models.CharField(max_length=600)
    phoneno = models.BigIntegerField()
    SEM = models.ForeignKey(semester,on_delete=models.CASCADE)
    YEAR = models.ForeignKey(academicyear,on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='students/')
    USER = models.OneToOneField(User, on_delete=models.CASCADE) 
    
class feedback(models.Model):
    message = models.TextField()
    reply = models.TextField(null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)
    STUDENT = models.ForeignKey(studentdata,on_delete=models.CASCADE)
    
class announcements(models.Model):
    title = models.CharField(max_length=1000)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
class studymaterials(models.Model):
    topic = models.CharField(max_length=1000)
    file = models.FileField(upload_to='studymaterials/')
    date = models.DateTimeField(auto_now_add=True)
    STAFF = models.ForeignKey(staffdata,on_delete=models.CASCADE)
    SUBJECT = models.ForeignKey(subjectdata,on_delete=models.CASCADE)
    
class assignment(models.Model):
    title = models.CharField(max_length=1000)
    description = models.TextField()
    deadline = models.DateField()
    created_at = models.DateField(auto_now_add=True)
    SUBJECT = models.ForeignKey(subjectdata,on_delete=models.CASCADE)
    STAFF = models.ForeignKey(staffdata,on_delete=models.CASCADE)
    
class assignmentdata(models.Model):
    file = models.FileField(upload_to='assignments/')
    created_at = models.DateField(auto_now_add=True)
    ASSIGN = models.ForeignKey(assignment,on_delete=models.CASCADE)
    STUDENT = models.ForeignKey(studentdata,on_delete=models.CASCADE)
    
class examdata(models.Model):
    title = models.CharField(max_length=1000)
    date = models.DateField()
    time = models.TimeField()
    type = models.CharField(max_length=20)
    SUBJECT = models.ForeignKey(subjectdata,on_delete=models.CASCADE)
    SEMDATA = models.ForeignKey(semdata, on_delete=models.CASCADE)  
    
class examresult(models.Model):
    EXAM = models.ForeignKey(examdata, on_delete=models.CASCADE)
    STUDENT = models.ForeignKey(studentdata, on_delete=models.CASCADE)
    marks = models.IntegerField()
    remarks = models.TextField(null=True, blank=True)

class timetable(models.Model):
    day = models.CharField(max_length=20)
    start_time = models.TimeField()
    end_time = models.TimeField()
    SUBJECT = models.ForeignKey(subjectdata, on_delete=models.CASCADE)
    SEM = models.ForeignKey(semdata, on_delete=models.CASCADE)
    
class calender(models.Model):
    YEAR = models.ForeignKey(academicyear,on_delete=models.CASCADE)
    title = models.CharField(max_length=1000)
    description = models.TextField(blank=True , null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    
class attendance(models.Model):
    STUDENT = models.ForeignKey(studentdata, on_delete=models.CASCADE)
    date = models.DateField()
    is_present = models.BooleanField(default=False)
    STAFF = models.ForeignKey(staffdata, on_delete=models.CASCADE)
    SEM = models.ForeignKey(semester, on_delete=models.CASCADE)
    YEAR = models.ForeignKey(academicyear, on_delete=models.CASCADE)
    
    
