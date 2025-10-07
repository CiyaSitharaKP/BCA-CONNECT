from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login,logout
from django.http import HttpResponse,JsonResponse
from django.contrib.auth.models import User,Group
from a_app.models import *
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import datetime, timedelta
from collections import defaultdict

# Create your views here.

def loginpage(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        if not username or not password:
            return HttpResponse(
                '''<script>alert("Both username and password are required.");window.location="/"</script>'''
                )
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('/admin_welcome')
            if user.groups.filter(name = "staff").exists():
                return redirect('/staff_welcome')
            elif user.groups.filter(name = "student").exists():
                return redirect('/student_welcome')
            else :
                return HttpResponse('''<script>alert("You don’t have permission to access this system.");window.location="/"</script>''')
        else:
            return HttpResponse(
                '''<script>alert("Invalid username or password.");window.location="/"</script>'''
            )
    return render(request, 'login.html')

    
def logoutpage(request):
     logout(request)
     return redirect('/')
 
#ADMIN

@login_required(login_url="/")  
def admin_welcome(request):
    data = announcements.objects.all().order_by('-updated_at')[:5]
    return render(request,'a_welcome.html',{"data":data})

@login_required(login_url="/") 
def admin_add_staff(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        design = request.POST['design']
        dob = request.POST['dob']
        gender = request.POST.get('gen')
        phoneno = request.POST['phoneno']
        photo = request.FILES.get('photo')
        if not name or not email or not dob or not gender or not phoneno or not photo or not design:
            return HttpResponse(
                '''<script>alert("All fields are required.");window.location="/admin_add_staff"</script>'''
            )
        if staffdata.objects.filter( email = email ).exists():
            return HttpResponse(
                '''<script>alert("Staff already exists.");window.location="/admin_add_staff"</script>'''
            )
        data = User.objects.create_user(username=email,password=str(phoneno),email=email)
        g = Group.objects.get(name="staff")
        data.groups.add(g)
        g.save()
        ob = staffdata()
        ob.name = name
        ob.email = email
        ob.design = design
        ob.dob = dob
        ob.gender = gender
        ob.phoneno = phoneno
        ob.photo = photo
        ob.USER = data
        ob.save()
        return HttpResponse(
        '''<script>alert("New staff added successfully.");window.location="/admin_add_staff"</script>'''
        )
    else :
        return render(request,'a_addstaff.html')

@login_required(login_url="/") 
def admin_view_staff(request):
    data = staffdata.objects.all()
    return render(request,'a_viewstaff.html',{"data":data})

@login_required(login_url="/") 
def admin_edit_staff(request,id):
    ob = staffdata.objects.get(id=id) 
    f = ob.USER
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        design = request.POST['design']
        dob = request.POST['dob']
        gender = request.POST.get('gen')
        phoneno = request.POST['phoneno']
        photo = request.FILES.get('photo')
        ob.name = name
        ob.email = email
        ob.design = design
        ob.dob = dob
        ob.gender = gender
        if f.check_password(phoneno) is False:
            f.set_password(str(phoneno))
        if photo:
            ob.photo = photo  
        ob.save()
        f.username = email 
        f.email=email
        f.save()
        return HttpResponse(
        '''<script>alert("Data updated successfully.");window.location="/admin_view_staff"</script>'''
        )
    else :
        return render(request,'a_editstaff.html',{"data":ob})

@login_required(login_url="/") 
def admin_delete_staff(request,id):
    a = staffdata.objects.get(id=id)
    b = a.USER
    a.delete()
    b.delete()
    return HttpResponse(
        '''<script>alert("Data deleted successfully");window.location="/admin_view_staff"</script>'''
    )
    
@login_required(login_url="/") 
def admin_add_student(request):
    sems = semester.objects.all()
    years = academicyear.objects.all()
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        rollno = request.POST['rollno']
        dob = request.POST['dob']
        gender = request.POST.get('gen')
        phoneno = request.POST['phoneno']
        sem = request.POST['sem']
        year = request.POST['year']
        photo = request.FILES.get('photo')
        if not name or not email or not dob or not rollno or not gender or not phoneno or not sem or not photo or not year :
            return HttpResponse(
                '''<script>alert("All fields are required.");window.location="/admin_add_student"</script>'''
            )
        if studentdata.objects.filter(email=email).exists() or studentdata.objects.filter(rollno=rollno).exists():
            return HttpResponse(
                '''<script>alert("Student with this email or roll number already exists.");window.location="/admin_add_student"</script>'''
            )

        data = User.objects.create_user(username=email,password=str(phoneno),email=email)
        g = Group.objects.get(name="student")
        data.groups.add(g)
        g.save()
        ob = studentdata()
        ob.name = name
        ob.email = email
        ob.rollno = rollno
        ob.dob = dob
        ob.gender = gender
        ob.phoneno = phoneno
        ob.SEM = semester.objects.get(id=sem)
        ob.YEAR = academicyear.objects.get(id=year)
        ob.photo = photo
        ob.USER = data
        ob.save()
        return HttpResponse(
        '''<script>alert("New student added successfully.");window.location="/admin_add_student"</script>'''
        )
    else :
        return render(request,'a_addstudent.html',{"semesters":sems,"years":years})

@login_required(login_url="/") 
def admin_view_student(request):
    data = studentdata.objects.all()
    return render(request,'a_viewstudent.html',{"data":data})

@login_required(login_url="/") 
def admin_edit_student(request,id):
    sems = semester.objects.all()
    years = academicyear.objects.all()
    ob = studentdata.objects.get(id=id) 
    f = ob.USER
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        rollno = request.POST['rollno']
        dob = request.POST['dob']
        gender = request.POST.get('gen')
        phoneno = request.POST['phoneno']
        sem = request.POST['sem']
        year = request.POST['year']
        photo = request.FILES.get('photo')
        ob.name = name
        ob.email = email
        ob.rollno = rollno
        ob.dob = dob
        ob.gender = gender
        if f.check_password(phoneno) is False:
            f.set_password(str(phoneno))
        ob.SEM = semester.objects.get(id=sem)
        ob.YEAR = academicyear.objects.get(id=year)
        if photo:
            ob.photo = photo  
        ob.save()
        f.username = email 
        f.email=email
        f.save()
        return HttpResponse(
        '''<script>alert("Data updated successfully.");window.location="/admin_view_student"</script>'''
        )
    else :
        return render(request,'a_editstudent.html',{"data":ob,"semesters":sems,"years":years})

@login_required(login_url="/") 
def admin_delete_student(request,id):
    a = studentdata.objects.get(id=id)
    b = a.USER
    a.delete()
    b.delete()
    return HttpResponse(
        '''<script>alert("Data deleted successfully");window.location="/admin_view_student"</script>'''
    )
    
@login_required(login_url="/") 
def admin_add_subject(request):
    sems = semester.objects.all()
    if request.method == 'POST':
        code = request.POST['code']
        name = request.POST['name']
        sem = request.POST['sem']
        syllabus = request.POST['syllabus']
        if not name or not code or not syllabus or not sem :
            return HttpResponse(
                '''<script>alert("All fields are required.");window.location="/admin_add_subject"</script>'''
            )
        if subjectdata.objects.filter(code=code).exists():
            return HttpResponse('''<script>alert("Subject code already exists.");window.location="/admin_add_subject"</script>''')
        if subjectdata.objects.filter(name=name).exists():
            return HttpResponse('''<script>alert("Subject name already exists.");window.location="/admin_add_subject"</script>''')

        ob = subjectdata()
        ob.name = name
        ob.code = code
        ob.syllabus = syllabus
        ob.SEM = semester.objects.get(id=sem)
        ob.save()
        return HttpResponse(
        '''<script>alert("New subject added successfully.");window.location="/admin_add_subject"</script>'''
        )
    else :
        return render(request,'a_addsub.html',{"semesters":sems})

@login_required(login_url="/") 
def admin_view_subject(request):
    data = subjectdata.objects.all()
    return render(request,'a_viewsub.html',{"data":data})

@login_required(login_url="/") 
def admin_edit_subject(request,id):
    sems = semester.objects.all()
    staffs = staffdata.objects.all()
    ob = subjectdata.objects.get(id=id) 
    if request.method == 'POST':
        code = request.POST['code']
        name = request.POST['name']
        syllabus = request.POST['syllabus']
        staff = request.POST['staff']
        sem = request.POST['sem']
        ob.name = name
        ob.code = code
        ob.syllabus = syllabus
        ob.SEM = semester.objects.get(id=sem)
        if staff:
            ob.STAFF = staffdata.objects.get(id=staff)
        ob.save()
        return HttpResponse(
        '''<script>alert("Data updated successfully.");window.location="/admin_view_subject"</script>'''
        )
    else :
        return render(request,'a_editsub.html',{"data":ob,"semesters":sems,"staffs":staffs})

@login_required(login_url="/") 
def admin_delete_subject(request,id):
    subjectdata.objects.get(id=id).delete()
    return HttpResponse(
        '''<script>alert("Data deleted successfully");window.location="/admin_view_subject"</script>'''
    )
    
@login_required(login_url="/")
def admin_assign_subject(request):
    staffs = staffdata.objects.all()
    sems = semester.objects.all()
    if request.method == 'POST':
        staff = request.POST['staff']
        sub = request.POST['sub']
        if not sub or not staff:
            return HttpResponse(
                '''<script>alert("All fields are required.");window.location="/admin_assign_subject"</script>'''
            )
        ob = subjectdata.objects.get(id=sub)
        if ob.STAFF:
            return HttpResponse(
                f'''<script>alert("This subject is already assigned to {ob.STAFF.name}.");window.location="/admin_assign_subject"</script>'''
            )
        ob.STAFF = staffdata.objects.get(id=staff)
        ob.save()
        return HttpResponse(
            '''<script>alert("Subject assigned successfully.");window.location="/admin_assign_subject"</script>'''
        )
    else:
        return render(request, 'a_assignsub.html', {"staffs": staffs, "semesters": sems})
        
@login_required(login_url="/")
def get_subjects_by_semester_staff(request):
    sem_id = request.GET.get('sem_id')
    try:
        ob = semester.objects.get(id=sem_id)
        subjects = subjectdata.objects.filter(SEM=ob.sem)
        data = [{"id": s.id, "name": f"{s.code} - {s.name}"} for s in subjects]
        return JsonResponse(data, safe=False)
    except semester.DoesNotExist:
        return JsonResponse([], safe=False)



@login_required(login_url='/')
def admin_view_feedback(request):
    data = feedback.objects.all().order_by("-created_at")
    return render(request,'a_viewfeed.html',{"data":data})

@login_required(login_url='/')
def admin_reply_feedback(request):
    if request.method == "POST":
        f_id = request.POST['fId']
        reply = request.POST['reply']
        if not reply:
            return HttpResponse(
                '''<script>alert("Enter a valid reply");window.location="/admin_view_feedback"</script>'''
            )
        ob = feedback.objects.get(id=f_id)
        if ob.reply and ob.reply.strip():
            return HttpResponse(
                '''<script>alert("This feedback has already been replied to.");window.location="/admin_view_feedback"</script>'''
            )
        ob.reply = reply
        ob.save()
        return HttpResponse(
            '''<script>alert("Reply submitted successfully");window.location="/admin_view_feedback"</script>'''
        )


@login_required(login_url="/")
def admin_add_timetable(request):
    subs = subjectdata.objects.all()
    sems = semdata.objects.all()

    if request.method == 'POST':
        sem = request.POST['sem']
        day = request.POST['day']
        stime = request.POST['stime']
        etime = request.POST['etime']
        sub = request.POST['sub']

        if not sub or not day or not stime or not etime or not sem:
            return HttpResponse(
                '''<script>alert("All fields are required.");window.location="/admin_add_timetable"</script>'''
            )

        start_time = datetime.strptime(stime, "%H:%M").time()
        end_time = datetime.strptime(etime, "%H:%M").time()

        if start_time >= end_time:
            return HttpResponse(
                '''<script>alert("End time must be after start time.");window.location="/admin_add_timetable"</script>'''
            )

        overlaps = timetable.objects.filter(
            SEM_id=sem,
            day=day,
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exists()

        if overlaps:
            return HttpResponse(
                '''<script>alert("This time slot overlaps with an existing one for the selected semester.");window.location="/admin_add_timetable"</script>'''
            )

        ob = timetable()
        ob.day = day
        ob.start_time = stime
        ob.end_time = etime
        ob.SUBJECT = subjectdata.objects.get(id=sub)
        ob.SEM = semdata.objects.get(id=sem)
        ob.save()

        return HttpResponse(
            '''<script>alert("Timetable entry added successfully.");window.location="/admin_add_timetable"</script>'''
        )

    else:
        return render(request, 'a_addtt.html', {"subjects": subs, "semesters": sems})


@login_required(login_url="/")
def get_subjects_by_semester_tt(request):
    sem_id = request.GET.get('sem_id')
    try:
        ob = semdata.objects.get(id=sem_id)
        subjects = subjectdata.objects.filter(SEM=ob.SEM)
        data = [{"id": s.id, "name": f"{s.code} - {s.name}"} for s in subjects]
        return JsonResponse(data, safe=False)
    except semdata.DoesNotExist:
        return JsonResponse([], safe=False)
    
@login_required(login_url='/')
def admin_view_timetable(request):
    day_order = {
        "Monday": 1, "Tuesday": 2, "Wednesday": 3,
        "Thursday": 4, "Friday": 5, "Saturday": 6
    }
    semesters = semdata.objects.all()
    timetables = timetable.objects.select_related("SUBJECT", "SEM")
    timetables = sorted(timetables, key=lambda x: (day_order.get(x.day, 99), x.start_time))
    return render(request, "a_viewtt.html", {"semesters": semesters,"timetables": timetables})
    
@login_required(login_url='/')
def admin_edit_timetable(request, id):
    ob = timetable.objects.get(id=id)
    semesters = semdata.objects.all()
    subjects = subjectdata.objects.all()
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"] 
    if request.method == "POST":
        sem = request.POST['sem']
        day = request.POST['day']
        stime = request.POST['stime']
        etime = request.POST['etime']
        sub = request.POST['sub']
        if timetable.objects.filter(
            day=day,
            start_time=stime,
            end_time=etime,
            SEM_id=sem
        ).exclude(id=id).exists():
            return HttpResponse(
                '''<script>alert("This time slot is already assigned for the selected semester.");window.location="/admin_view_timetable"</script>'''
            )
        if timetable.objects.filter(
            day=day,
            start_time=stime,
            end_time=etime,
            SEM_id=sem,
            SUBJECT_id=sub
        ).exclude(id=id).exists():
            return HttpResponse(
                '''<script>alert("This subject is already scheduled at this time for the selected semester.");window.location="/admin_view_timetable"</script>'''
            )
        ob.day = day
        ob.start_time = stime
        ob.end_time = etime
        ob.SUBJECT = subjectdata.objects.get(id=sub)
        ob.SEM = semdata.objects.get(id=sem)
        ob.save()
        return HttpResponse(
            '''<script>alert("Updated successfully");window.location="/admin_view_timetable/";</script>'''
        )
    else:
        return render(request, 'a_edittt.html', {
            "data": ob,
            "semesters": semesters,
            "subjects": subjects,
            "days":days
        })

@login_required(login_url='/')
def admin_delete_timetable(request,id):
    timetable.objects.get(id = id).delete()
    return HttpResponse(
                '''<script>alert("Data deleted successfully");window.location="/admin_view_timetable"</script>'''
            )
    
@login_required(login_url='/')
def admin_add_calender(request):
    years = academicyear.objects.all()
    if request.method == 'POST':
        year = request.POST['year']
        title = request.POST['title']
        sdate = request.POST['sdate']
        edate = request.POST['edate']
        descrip = request.POST['descrip']
        if  not edate or not sdate or not title or not year: 
            return HttpResponse('''<script>alert("All fields are required");window.location="/admin_add_events"</script>''')
        if sdate > edate:
            return HttpResponse('''<script>alert("Start date cannot be after end date.");window.location="/admin_add_events"</script>''')
        if calender.objects.filter(YEAR_id=year, start_date=sdate, end_date=edate).exists():
            return HttpResponse('''<script>alert("Slot already assigned");window.location="/admin_add_events"</script>''')
        ob = calender()
        ob.YEAR = academicyear.objects.get(id=year)
        ob.start_date = sdate
        ob.end_date = edate
        ob.title = title
        ob.description = descrip
        ob.save()
        return HttpResponse(
                '''<script>alert("Event added successfully");window.location="/admin_add_events"</script>'''
            )
    else :
        return render(request,'a_addcal.html',{"years":years})
    
@login_required(login_url='/')
def admin_view__years(request):
    data = academicyear.objects.order_by('-year')
    return render(request, "a_viewyear.html", {"data": data})

   
@login_required(login_url='/')
def admin_view_calender(request, id):
    ob = academicyear.objects.get(id=id)
    start_year, end_year = map(int, ob.year.split('-'))
    years = list(range(start_year, end_year + 1))

    events = calender.objects.filter(YEAR__year=ob.year).order_by('start_date')

    event_list = []
    for event in events:
        current_day = event.start_date
        while current_day <= event.end_date:
            event_list.append({
                'event': event,
                'year': current_day.year,
                'month': current_day.month,
                'day': current_day.day
            })
            current_day += timedelta(days=1)
        
    day_range = range(1, 32)
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    return render(request, "a_viewcal.html", {
        "year": ob,
        "years": years,
        "months": months,
        "event_list": event_list,
        "events": events,
        "day_range": day_range  
    })


@login_required(login_url='/')
def admin_edit_calender(request,id):
    ob = calender.objects.get(id = id)
    years = academicyear.objects.all()
    if request.method == 'POST':
        year = request.POST['year']
        title = request.POST['title']
        sdate = request.POST['sdate']
        edate = request.POST['edate']
        descrip = request.POST['descrip']
        ob.YEAR = academicyear.objects.get(id=year)
        ob.start_date = sdate
        ob.end_date = edate
        ob.title = title
        ob.description = descrip
        ob.save()
        return HttpResponse(
                '''<script>alert("Event updated successfully");window.location="/admin_view_calender"</script>'''
            )
    else :
        return render(request,'a_editcal.html',{"data":ob,"years":years})

@login_required(login_url='/')
def admin_delete_calender(request,id):
    calender.objects.get(id = id).delete()
    return HttpResponse(
                '''<script>alert("Data deleted successfully");window.location="/admin_view_calender"</script>'''
            )

@login_required(login_url='/')
def admin_add_announce(request):
    if request.method == 'POST':
        title = request.POST['title']
        msg = request.POST['msg']
        if not title or not msg:
            return HttpResponse(
                '''<script>alert("All fields are required");window.location="/admin_add_announcements"</script>'''
            )
        ob = announcements()
        ob.title = title
        ob.message = msg
        ob.save()
        return HttpResponse(
                '''<script>alert("Data added successfully");window.location="/admin_add_announcements"</script>'''
            )
    else : 
        return render(request,'a_addannounce.html')

@login_required(login_url='/')
def admin_view_announce(request):
    data = announcements.objects.all()
    return render(request,'a_viewannounce.html',{"data":data})

@login_required(login_url='/')
def admin_edit_announce(request,id):
    ob = announcements.objects.get(id=id)
    if request.method == 'POST':
        title = request.POST['title']
        msg = request.POST['msg']
        ob.title = title
        ob.message = msg
        ob.save()
        return HttpResponse(
                '''<script>alert("Data updated successfully");window.location="/admin_view_announcements"</script>'''
            )
    else : 
        return render(request,'a_editannounce.html',{"data":ob})
    
@login_required(login_url='/')
def admin_delete_announce(request,id):
    announcements.objects.get(id = id).delete()
    return HttpResponse(
                '''<script>alert("Data deleted successfully");window.location="/admin_view_announcements"</script>'''
            )

   
@login_required(login_url="/") 
def admin_change_pass(request):
    if request.method == 'POST':
        currpass = request.POST['currpass']
        newpass = request.POST['newpass']
        conpass = request.POST['conpass']  
        user = request.user

        if not user.check_password(currpass):
            return HttpResponse(
            '''<script>alert("Current password is incorrect.");window.location="/admin_change_password"</script>'''
            )
        elif newpass != conpass:
            return HttpResponse(
            '''<script>alert("New password and confirm password do not match.");window.location="/admin_change_password"</script>'''
            )
        else:
            user.set_password(newpass)
            user.save()
            return HttpResponse(
                '''<script>alert("Password changed successfully");window.location="/"</script>'''
            )
    else :
        return render(request, 'a_changepass.html')
    
    
 #STAFF   
    
    
@login_required(login_url="/")  
def staff_welcome(request):
    data = announcements.objects.all().order_by('-updated_at')[:5]
    ob = staffdata.objects.get(USER = request.user)
    return render(request,'s_welcome.html',{"data":data,"ob":ob})

@login_required(login_url="/") 
def staff_view_profile(request):
    data = staffdata.objects.get(USER = request.user)
    return render(request,'s_viewprof.html',{"data":data})

@login_required(login_url="/") 
def staff_view_subject(request):
    a = staffdata.objects.get(USER = request.user)
    data = subjectdata.objects.filter(STAFF = a)
    return render(request,'s_viewsub.html',{"data":data})

@login_required(login_url='/')
def staff_add_notes(request):
    staff = staffdata.objects.get(USER=request.user)
    subs = subjectdata.objects.filter(STAFF=staff)
    sem_ids = subs.values_list('SEM_id', flat=True).distinct()
    sems = semester.objects.filter(id__in=sem_ids)

    if request.method == 'POST':
        sub = request.POST['sub']
        sem = request.POST['sem']
        file = request.FILES['file']
        topic = request.POST['topic']

        if not subs.filter(id=sub).exists():
            return HttpResponse(
                '''<script>alert("You are not assigned to this subject.");window.location="/staff_add_notes"</script>'''
            )

        if not sub or not file or not topic or not sem:
            return HttpResponse(
                '''<script>alert("All fields are required");window.location="/staff_add_notes"</script>'''
            )

        ob = studymaterials()
        ob.topic = topic
        ob.file = file
        ob.STAFF = staff
        ob.SUBJECT = subjectdata.objects.get(id=sub)
        ob.save()
        return HttpResponse(
            '''<script>alert("Study Materials added successfully");window.location="/staff_add_notes"</script>'''
        )

    return render(request, 's_addnotes.html', {
        "subjects": subs,
        "semesters": sems
    })


@login_required(login_url="/")
def get_subjects_by_semester_notes(request):
    sem_id = request.GET.get('sem_id')
    staff = staffdata.objects.get(USER = request.user)
    subjects = subjectdata.objects.filter(SEM_id=sem_id , STAFF = staff)
    data = [{"id": s.id, "name": f"{s.code} - {s.name}"} for s in subjects]
    return JsonResponse(data, safe=False)
    
@login_required(login_url='/')
def staff_view_notes(request):
    a = staffdata.objects.get(USER = request.user)
    data = studymaterials.objects.filter(STAFF = a)
    return render(request,'s_viewnotes.html',{"data":data})

@login_required(login_url='/')
def staff_edit_notes(request,id):
    staff = staffdata.objects.get(USER=request.user)
    subs = subjectdata.objects.filter(STAFF=staff)
    sem_ids = subs.values_list('SEM_id', flat=True).distinct()
    sems = semester.objects.filter(id__in=sem_ids)
    ob = studymaterials.objects.get(id = id)
    if request.method == 'POST':
        sub = request.POST['sub']
        file = request.FILES.get('file')
        topic = request.POST['topic']
        ob.topic = topic
        if file:
            ob.file = file 
        ob.STAFF = staffdata.objects.get(USER=request.user)
        ob.SUBJECT = subjectdata.objects.get(id = sub)
        ob.save()
        return HttpResponse(
                '''<script>alert("Study Materials updated successfully");window.location="/staff_view_notes"</script>'''
            )
    else :
        return render(request,'s_editnotes.html',{"subjects":subs,"semesters":sems,"data":ob})

@login_required(login_url='/')
def staff_delete_notes(request,id):
    studymaterials.objects.get(id = id).delete()
    return HttpResponse(
        '''<script>alert("Study Materials deleted successfully");window.location="/staff_view_notes"</script>'''
    )


@login_required(login_url='/')
def staff_add_assignments(request):
    staff = staffdata.objects.get(USER=request.user)
    subs = subjectdata.objects.filter(STAFF=staff)
    sem_ids = subs.values_list('SEM', flat=True).distinct()
    sems = semdata.objects.filter(SEM__in=sem_ids)

    if request.method == 'POST':
        sem = request.POST['sem']
        sub = request.POST['sub']
        title = request.POST['title']
        descrip = request.POST['descrip']
        deadline = request.POST['deadline']
        if not sem or not sub or not title or not descrip or not deadline:
            return HttpResponse(
                '''<script>alert("All the fields are required");window.location="/staff_add_assignments"</script>'''
            )
        if assignment.objects.filter(SUBJECT_id=sub , description=descrip).exists():
            return HttpResponse(
                '''<script>alert("Assignment already exists");window.location="/staff_add_assignments"</script>'''
            )
        ob = assignment()
        ob.title = title
        ob.description = descrip
        ob.deadline = deadline
        ob.SUBJECT = subjectdata.objects.get(id = sub)
        ob.STAFF = staffdata.objects.get(USER=request.user)
        ob.save()
        return HttpResponse(
                '''<script>alert("Assignment added successfully");window.location="/staff_add_assignments"</script>'''
            )
    else:
        return render(request,'s_addassign.html',{"semesters":sems,"subjects":subs})
    
@login_required(login_url="/")
def get_subjects_by_semester_assignments(request):
    sem_id = request.GET.get('sem_id')
    try:
        ob = semdata.objects.get(id=sem_id)
        staff = staffdata.objects.get(USER = request.user)
        subjects = subjectdata.objects.filter(SEM=ob.SEM  , STAFF=staff )
        data = [{"id": s.id, "name": f"{s.code} - {s.name}"} for s in subjects]
        return JsonResponse(data, safe=False)
    except semdata.DoesNotExist:
        return JsonResponse([], safe=False)


@login_required(login_url='/')
def staff_view_assignments(request):
    staff = staffdata.objects.get(USER = request.user)
    data = assignment.objects.filter(STAFF = staff)
    return render(request,'s_viewassign.html',{"data":data})


@login_required(login_url='/')
def staff_edit_assignments(request,id):
    staff = staffdata.objects.get(USER=request.user)
    subs = subjectdata.objects.filter(STAFF=staff)
    sem_ids = subs.values_list('SEM', flat=True).distinct()
    sems = semdata.objects.filter(SEM__in=sem_ids)
    ob = assignment.objects.get(id = id)
    if request.method == 'POST':
        sub = request.POST['sub']
        title = request.POST['title']
        descrip = request.POST['descrip']
        deadline = request.POST['deadline']
        ob.title = title
        ob.description = descrip
        ob.deadline = deadline
        ob.SUBJECT = subjectdata.objects.get(id = sub)
        ob.STAFF = staffdata.objects.get(USER=request.user)
        ob.save()
        return HttpResponse(
                '''<script>alert("Assignment updated successfully");window.location="/staff_view_assignments"</script>'''
            )
    else:
        return render(request,'s_editassign.html',{"semesters":sems,"subjects":subs,"data":ob})

@login_required(login_url='/')
def staff_delete_assignments(request,id):
    assignment.objects.get(id = id).delete()
    return HttpResponse(
                '''<script>alert("Assignment deleted successfully");window.location="/staff_view_assignments"</script>'''
            )

@login_required(login_url='/')
def staff_view_submitted_assignments(request,id):
    data = assignmentdata.objects.filter(ASSIGN_id=id)
    return render(request,'s_viewsubassign.html',{"data":data})

@login_required(login_url='/')
def staff_add_exam(request):
    staff = staffdata.objects.get(USER=request.user)
    subs = subjectdata.objects.filter(STAFF=staff)
    sem_ids = subs.values_list('SEM', flat=True).distinct()
    sems = semdata.objects.filter(SEM__in=sem_ids)

    if request.method == 'POST':
        sem_id = request.POST['sem']
        sub_id = request.POST['sub']
        title = request.POST['title']
        date = request.POST['date']
        time = request.POST['time']
        exam_type = request.POST['type']

        if not all([sem_id, sub_id, title, date, time, exam_type]):
            return HttpResponse(
                '''<script>alert("All fields are required");window.location="/staff_add_exams"</script>'''
            )

        if exam_type not in ['Monthly', 'Internal']:
            return HttpResponse(
                '''<script>alert("Invalid exam type");window.location="/staff_add_exams"</script>'''
            )

        if examdata.objects.filter(title=title, date=date, time=time, type=exam_type).exists():
            return HttpResponse(
                '''<script>alert("Exam already exists.");window.location="/staff_add_exams"</script>'''
            )

        sem_obj = semdata.objects.filter(id=sem_id).first()
        sub_obj = subjectdata.objects.filter(id=sub_id).first()

        if not sem_obj or not sub_obj:
            return HttpResponse(
                '''<script>alert("Invalid semester or subject selection.");window.location="/staff_add_exams"</script>'''
            )

        if sub_obj.SEM != sem_obj.SEM:
            return HttpResponse(
                '''<script>alert("Selected subject does not belong to the selected semester.");window.location="/staff_add_exams"</script>'''
            )

        ob = examdata()
        ob.title = title
        ob.date = date
        ob.time = time
        ob.type = exam_type
        ob.SUBJECT = sub_obj
        ob.SEMDATA = sem_obj
        ob.save()

        return HttpResponse(
            '''<script>alert("Exam added successfully");window.location="/staff_add_exams"</script>'''
        )

    return render(request, 's_addexam.html', {"semesters": sems, "subjects": subs})


            
@login_required(login_url='/')
def staff_view_exam(request):
    staff = staffdata.objects.get(USER = request.user)
    sub = subjectdata.objects.filter(STAFF = staff)
    data = examdata.objects.filter(SUBJECT__in = sub)
    return render(request,'s_viewexam.html',{"data":data})

@login_required(login_url='/')
def staff_edit_exam(request, id):
    staff = staffdata.objects.get(USER=request.user)
    subs = subjectdata.objects.filter(STAFF=staff)
    sem_ids = subs.values_list('SEM', flat=True).distinct()
    sems = semdata.objects.filter(SEM__in=sem_ids)
    ob = examdata.objects.get(id=id)

    if request.method == 'POST':
        sem_id = request.POST['sem']
        sub_id = request.POST['sub']
        exam_type = request.POST['type']
        title = request.POST['title']
        date = request.POST['date']
        time = request.POST['time']

        if not all([sem_id, sub_id, exam_type, title, date, time]):
            return HttpResponse(
                '''<script>alert("All fields are required");window.location="/staff_edit_exam/{0}"</script>'''.format(id)
            )

        sem_obj = semdata.objects.filter(id=sem_id).first()
        sub_obj = subjectdata.objects.filter(id=sub_id).first()

        if not sem_obj or not sub_obj:
            return HttpResponse(
                '''<script>alert("Invalid semester or subject selection.");window.location="/staff_edit_exam/{0}"</script>'''.format(id)
            )

        if sub_obj.SEM != sem_obj.SEM:
            return HttpResponse(
                '''<script>alert("Selected subject does not belong to the selected semester.");window.location="/staff_edit_exam/{0}"</script>'''.format(id)
            )

        ob.title = title
        ob.date = date
        ob.time = time
        ob.type = exam_type
        ob.SUBJECT = sub_obj
        ob.SEMDATA = sem_obj  
        ob.save()

        return HttpResponse(
            '''<script>alert("Exam updated successfully");window.location="/staff_view_exams"</script>'''
        )

    return render(request, 's_editexam.html', {
        "semesters": sems,
        "subjects": subs,
        "data": ob
    })


@login_required(login_url='/')
def staff_delete_exam(request,id):
    examdata.objects.get(id =id).delete()
    return HttpResponse(
                '''<script>alert("Exam deleted successfully");window.location="/staff_view_exams"</script>'''
            )


@login_required(login_url='/')
def staff_add_result(request):
    staff = staffdata.objects.get(USER=request.user)
    subs = subjectdata.objects.filter(STAFF=staff)
    sems = semdata.objects.filter(SEM__in=subs.values('SEM'), YEAR__in=studentdata.objects.values('YEAR'))

    context = {
        "semesters": sems,
        "subjects": subs,
    }

    if request.method == 'POST':
        sem_id = request.POST['sem']
        sub_id = request.POST['sub']
        exam_id = request.POST['exam']
        student_id = request.POST['student']
        exam_type = request.POST['exam_type']
        marks = request.POST['marks']
        remarks = request.POST['remarks']

        if not all([sem_id, sub_id, exam_id, student_id, exam_type, marks]):
            return HttpResponse(
                '''<script>alert("All fields are required");window.location="/staff_add_results"</script>'''
            )

        if not marks.isdigit():
            return HttpResponse(
                '''<script>alert("Marks must be a number");window.location="/staff_add_results"</script>'''
            )

        exam_obj = examdata.objects.get(id=exam_id)
        student_obj = studentdata.objects.get(id=student_id)

        if examresult.objects.filter(EXAM=exam_obj, STUDENT=student_obj).exists():
            return HttpResponse(
                '''<script>alert("Result already added for this exam and student");window.location="/staff_add_results"</script>'''
            )

        ob = examresult(EXAM=exam_obj, STUDENT=student_obj, marks=int(marks), remarks=remarks)
        ob.save()

        return HttpResponse(
            '''<script>alert("Result added successfully");window.location="/staff_add_results"</script>'''
        )

    return render(request, 's_addresults.html', context)


@login_required(login_url="/")
def get_exam_types_by_subject(request):
    sub_id = request.GET.get('sub_id')
    sem_id = request.GET.get('sem_id')  

    subject = subjectdata.objects.filter(id=sub_id).first()
    semdata_obj = semdata.objects.filter(id=sem_id).first()

    if subject and semdata_obj:
        types = examdata.objects.filter(
            SUBJECT=subject,
            SEMDATA=semdata_obj 
        ).values_list('type', flat=True).distinct()
        return JsonResponse(list(types), safe=False)

    return JsonResponse([], safe=False)

 
 
@login_required(login_url="/")
def get_exams_by_subject_and_type(request):
    sub_id = request.GET.get('sub_id')
    exam_type = request.GET.get('exam_type')
    sem_id = request.GET.get('sem_id')
    try:
        subject = subjectdata.objects.get(id=sub_id)
        semdata_obj = semdata.objects.get(id=sem_id)
        exams = examdata.objects.filter(SUBJECT=subject, SEMDATA=semdata_obj, type=exam_type)
        data = [{"id": e.id, "title": e.title} for e in exams]
        return JsonResponse(data, safe=False)
    except (subjectdata.DoesNotExist, semdata.DoesNotExist):
        return JsonResponse([], safe=False)


    
@login_required(login_url="/")
def get_students_by_semester(request):
    semdata_id = request.GET.get('sem_id')
    try:
        sem_data = semdata.objects.get(id=semdata_id)
        students = studentdata.objects.filter(SEM=sem_data.SEM, YEAR=sem_data.YEAR)
        data = [{"id": s.id, "name": f"{s.rollno} - {s.name}"} for s in students]
        return JsonResponse(data, safe=False)
    except semdata.DoesNotExist:
        return JsonResponse([], safe=False)

@login_required(login_url='/')
def staff_view_result(request):
    staff = staffdata.objects.get(USER=request.user)
    subjects = subjectdata.objects.filter(STAFF=staff)
    semesters = semdata.objects.filter(SEM__in=subjects.values_list('SEM', flat=True)).distinct()
    results = []

    if request.method == 'POST':
        sem_id = request.POST.get('sem_id')
        try:
            sem_entry = semdata.objects.get(id=sem_id)
            staff_subjects = subjectdata.objects.filter(STAFF=staff, SEM=sem_entry.SEM)
            students = studentdata.objects.filter(SEM=sem_entry.SEM, YEAR=sem_entry.YEAR)

            exam_results = examresult.objects.filter(
                STUDENT__in=students,
                EXAM__SUBJECT__in=staff_subjects,
                EXAM__SEMDATA=sem_entry 
            )

            results = [{
                "name": r.STUDENT.name,
                "rollno": r.STUDENT.rollno,
                "exam": r.EXAM.title,
                "type": r.EXAM.type,
                "subject": f"{r.EXAM.SUBJECT.code} - {r.EXAM.SUBJECT.name}",
                "marks": r.marks,
                "remarks": r.remarks or "-"
            } for r in exam_results]

        except semdata.DoesNotExist:
            results = []

    return render(request, 's_viewresult.html', {
        "semesters": semesters,
        "results": results
    })

   
@login_required(login_url='/')
def staff_view_feedback(request):
    data = feedback.objects.all().order_by("-created_at")
    return render(request,'s_viewfeed.html',{"data":data})

@login_required(login_url='/')
def staff_reply_feedback(request):
    if request.method == "POST":
        f_id = request.POST['fId']
        reply = request.POST['reply']
        if not reply :
            return HttpResponse(
                '''<script>alert("Enter a valid reply");window.location="/staff_view_feedback"</script>'''
            )
        ob = feedback.objects.get(id = f_id)
        ob.reply = reply 
        ob.save()
        return HttpResponse(
                '''<script>alert("Reply submitted successfully");window.location="/staff_view_feedback"</script>'''
            )

@login_required(login_url='/')
def staff_view_student_performance(request):
    staff = staffdata.objects.get(USER=request.user)
    subjects = subjectdata.objects.filter(STAFF=staff)
    sems = semdata.objects.filter(SEM__in=subjects.values_list('SEM', flat=True)).distinct()
    context = {
        'semesters': sems,
    }

    if request.method == 'POST':
        sem_id = request.POST['sem']
        student_id = request.POST['student']

        if not sem_id or not student_id:
            return HttpResponse(
                '''<script>alert("All fields are required");window.location="/staff_view_student_perf/"</script>'''
            )

        selected_sem = semdata.objects.filter(id=sem_id).first()
        selected_student = studentdata.objects.filter(id=student_id).first()

        if selected_sem and selected_student:
            subjects = subjectdata.objects.filter(SEM=selected_sem.SEM)
            assignments = assignmentdata.objects.filter(STUDENT=selected_student)

            all_results = examresult.objects.filter(STUDENT=selected_student)
            internal_results = all_results.filter(EXAM__type="Internal")
            regular_results = all_results.exclude(EXAM__type="Internal")

            context.update({
                'selected_student': selected_student,
                'selected_semester': selected_sem,
                'subjects': subjects,
                'assignments': assignments,
                'internal_results': internal_results,
                'regular_results': regular_results,
            })

    return render(request, 's_stperf.html', context)

           

@login_required(login_url='/')
def staff_subject_report(request):
    staff = staffdata.objects.get(USER=request.user)
    subjects = subjectdata.objects.filter(STAFF=staff)
    semesters = semdata.objects.filter(SEM__in=subjects.values_list('SEM', flat=True)).distinct()

    if request.method == 'POST':
        subject_id = request.POST.get('sub')

        if not subject_id:
            return HttpResponse(
                '''<script>alert("Invalid input");window.location="/staff_get_reports/"</script>'''
            )
        subject = subjectdata.objects.filter(id=subject_id, STAFF=staff).first()
        if not subject:
            return HttpResponse(
                '''<script>alert("Subject not found");window.location="/staff_get_reports/"</script>'''
            )
        exams = examdata.objects.filter(SUBJECT=subject)
        assignments = assignment.objects.filter(SUBJECT=subject, STAFF=staff)
        students = studentdata.objects.filter(SEM=subject.SEM, YEAR__in=semdata.objects.filter(SEM=subject.SEM).values('YEAR'))

        content = f"""
Subject Report
==============
Code     : {subject.code}
Name     : {subject.name}
Semester : {subject.SEM.sem}
Syllabus : {subject.syllabus or 'Not Provided'}

Exams Conducted
---------------
{chr(10).join([f" {e.title} on {e.date} ({e.type})" for e in exams]) or 'No exams conducted'}

Assignments Posted
------------------
{chr(10).join([f" {a.title} (Deadline: {a.deadline})" for a in assignments]) or 'No assignments posted'}

Students Enrolled
-----------------
{chr(10).join([f" {s.rollno} - {s.name}" for s in students]) or 'No students enrolled'}
        """.strip()

        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{subject.code}_Report.txt"'
        response.write(content)
        return response

    return render(request, 's_reports.html', {"semesters": semesters})

@login_required(login_url="/")
def get_subjects_by_semester_and_staff(request):
    semdata_id = request.GET.get('sem_id')
    staff = staffdata.objects.get(USER=request.user)
    if not semdata_id or not semdata.objects.filter(id=semdata_id).exists():
        return JsonResponse([], safe=False)
    sem_data = semdata.objects.get(id=semdata_id)
    subjects = subjectdata.objects.filter(SEM=sem_data.SEM, STAFF=staff)
    data = [{"id": s.id, "name": f"{s.code} - {s.name}"} for s in subjects]
    return JsonResponse(data, safe=False)

@login_required(login_url='/')
def staff_view__years(request):
    data = academicyear.objects.order_by('-year')
    return render(request, "s_viewyear.html", {"data": data})

#STUDENT
    
@login_required(login_url="/")  
def student_welcome(request):
    data = announcements.objects.all().order_by('-updated_at')[:5]
    ob = studentdata.objects.get(USER = request.user)
    return render(request,'st_welcome.html',{"data":data,"ob":ob})

@login_required(login_url="/") 
def student_view_profile(request):
    data = studentdata.objects.get(USER = request.user)
    return render(request,'st_viewprofile.html',{"data":data})
    
@login_required(login_url='/')   
def student_view_notes(request):
    st = studentdata.objects.get(USER=request.user)
    s = st.SEM
    subs = subjectdata.objects.filter(SEM=s)
    data = None  
    if request.method == 'POST':
        sub = request.POST.get('sub')
        if sub:
            data = studymaterials.objects.filter(SUBJECT_id=sub)
    return render(request, 'st_viewnotes.html', {"subjects": subs, "data": data})

    
@login_required(login_url='/')   
def student_view_subjects(request):
    st = studentdata.objects.get(USER = request.user)
    s = st.SEM
    subs = subjectdata.objects.filter(SEM = s)
    return render(request,'st_viewsub.html',{"data":subs})   
    
@login_required(login_url='/')
def student_view_timetable(request):
    st = studentdata.objects.get(USER=request.user)
    sem = semdata.objects.get(SEM=st.SEM, YEAR=st.YEAR)
    tt = timetable.objects.filter(SEM=sem).order_by('day', 'start_time')

    grouped_data = defaultdict(list)
    for entry in tt:
        grouped_data[entry.day].append(entry)

    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    ordered_data = [(day, grouped_data.get(day, [])) for day in day_order]

    return render(request, 'st_viewtt.html', {
        "ordered_data": ordered_data
    })


@login_required(login_url='/')
def student_view_assignments(request):
    st = studentdata.objects.get(USER=request.user)
    subs = subjectdata.objects.filter(SEM=st.SEM)
    data = []
    today = timezone.now().date()

    if request.method == 'POST':
        sub = request.POST.get('sub')
        if sub:
            for a in assignment.objects.filter(SUBJECT_id=sub):
                a.is_urgent = (a.deadline - today).days <= 3
                data.append(a)

    return render(request, 'st_viewassign.html', {"subjects": subs, "data": data})

@login_required(login_url='/')
def student_add_assignment(request):
    st = studentdata.objects.get(USER = request.user)
    s = st.SEM
    subs = subjectdata.objects.filter(SEM = s)
    assigns = assignment.objects.all()
    if request.method == 'POST':
        sub = request.POST['sub']
        assign = request.POST['assign']
        file = request.FILES['file']
        if not sub or not assign or not file:
            return HttpResponse(
                '''<script>alert("All fields are required");window.location="/student_add_assignments"</script>'''
            )
        if not file.name.lower().endswith(('.pdf', '.doc', '.docx', '.ppt', '.pptx')):
            return HttpResponse(
                '''<script>alert("Only document files are allowed");window.location="/student_add_assignments"</script>'''
            )

        ob = assignmentdata()
        ob.file = file
        ob.ASSIGN = assignment.objects.get(id = assign)
        ob.STUDENT = studentdata.objects.get(USER = request.user)
        ob.save()
        return HttpResponse(
                '''<script>alert("Assignment submitted successfully");window.location="/student_add_assignments"</script>'''
            )
    else:
        return render(request,'st_addassign.html',{"subjects":subs,"assigns":assigns})

@login_required(login_url='/')
def get_assignments_by_subject(request):
    sub_id = request.GET.get('sub_id')
    assignments = []
    if sub_id:
        assignments = assignment.objects.filter(SUBJECT_id=sub_id)
    data = [{"id": a.id, "title": a.title} for a in assignments]
    return JsonResponse(data, safe=False)


@login_required(login_url='/')
def student_view_result(request):
    student = studentdata.objects.get(USER=request.user)
    data = examresult.objects.filter(STUDENT=student)
    return render(request, 'st_viewresult.html', {"data": data})


@login_required(login_url='/')
def student_view_feedback(request):
    st = studentdata.objects.get(USER = request.user)
    data = feedback.objects.filter(STUDENT = st)
    return render(request,'st_viewfeed.html',{"data":data})

@login_required(login_url='/')
def student_add_feedback(request):
    if request.method == 'POST':
        msg = request.POST.get('feedback')
        if not msg:
            return HttpResponse(
                '''<script>alert("Enter your feedback");window.location="/student_add_feedback"</script>'''
            )
        ob = feedback()
        ob.message = msg
        ob.STUDENT = studentdata.objects.get(USER=request.user)  # Link to student
        ob.save()
        return HttpResponse(
            '''<script>alert("Feedback submitted successfully");window.location="/student_add_feedback"</script>'''
        )
    return render(request, 'st_addfeed.html')

@login_required(login_url='/')
def student_view_exams(request):
    student = studentdata.objects.get(USER=request.user)
    subjects = subjectdata.objects.filter(SEM=student.SEM)
    today = timezone.now().date()
    data = []

    for exam in examdata.objects.filter(SUBJECT__in=subjects).order_by('date'):
        exam.is_upcoming = 0 <= (exam.date - today).days <= 3
        data.append(exam)

    return render(request, 'st_viewexam.html', {"data": data})


@login_required(login_url='/')
def student_view_internal(request):
    student = studentdata.objects.get(USER=request.user)
    data = examresult.objects.filter(STUDENT=student, EXAM__type="Internal")
    return render(request, 'st_viewinternal.html', {"data": data})


@login_required(login_url='/')
def student_view_calendar(request):
    student = studentdata.objects.get(USER=request.user)
    a = student.YEAR.id
    ob = academicyear.objects.get(id=a)
    start_year, end_year = map(int, ob.year.split('-'))
    years = list(range(start_year, end_year + 1))

    events = calender.objects.filter(YEAR__year=ob.year).order_by('start_date')

    event_list = []
    for event in events:
        current_day = event.start_date
        while current_day <= event.end_date:
            event_list.append({
                'event': event,
                'year': current_day.year,
                'month': current_day.month,
                'day': current_day.day
            })
            current_day += timedelta(days=1)
        
    day_range = range(1, 32)

    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    return render(request, "st_viewcal.html", {
        "year": ob,
        "years": years,
        "months": months,
        "event_list": event_list,
        "events": events ,
        "day_range": day_range   
    })    