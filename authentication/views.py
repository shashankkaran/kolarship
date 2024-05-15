from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages, auth
from django.core.mail import EmailMessage, send_mail
from logins import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth import authenticate, login, logout
from . tokens import generate_token
from django.db.models import Q
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import csv
import os
from django.conf import settings
from django.contrib import messages
from .models import Scholarship
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt




def scholarship_list(request):
    if not Scholarship.objects.exists():
        with open('templates/SchollarShips in India.csv', 'r', newline='', encoding='latin-1') as csvfile:
            content = csvfile.read()
            cleaned_content = content.replace('\xa0', ' ')
            reader = csv.DictReader(cleaned_content.splitlines())
            for row in reader:
                Scholarship.objects.create(
                    Name=row['Name'],
                    Eligibility=row['Eligibility'],
                    Eligible=row['Eligible'],
                    Links_online_application=row['Links_online_application'],
                    Contacts_offline_applications=row['Contacts_offline_applications'],
                    Special_Categories=row['Special_Categories'],
                    Scholarship_Fellowship=row['Scholarship_Fellowship'],
                    Level=row['Level'],
                    State=row['State'],
                    Application_Period=row['Application_Period']
                )

    scholarships_data = Scholarship.objects.all()
    return render(request, 'authentication/scholarship_list.html', {'scholarships_data': scholarships_data})

# Create your views here.
def home(request):
    return render(request, "authentication/home.html")

def index(request):
    return render(request, "authentication/index.html")

def guide(request):
    return render(request, 'authentication/Guide.html')

def open_applications_view(request):
    current_month = timezone.now().strftime('%B')  # Get the current month
    open_applications_data = Scholarship.objects.filter(
        Application_Period__icontains=current_month,
    ) | Scholarship.objects.filter(
        Application_Period__icontains='Always Open',
    )

    return render(request, 'authentication/open_applications.html', {'open_applications_data': open_applications_data})
@csrf_exempt
def signup(request):
    if request.method == "POST":
        username=request.POST['username']
        fname=request.POST['fname']
        lname=request.POST['lname']
        email=request.POST['email']
        mobile=request.POST['mobile']
        password1=request.POST['password1']
        password2=request.POST['password2']
        designation=request.POST['designation']
        institute=request.POST['institute']
        address=request.POST['address']
        state=request.POST['state']
        pin=request.POST['pin']


        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('home')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect('home')
        
        if password1!=password2:
            messages.error(request, "Incorrect Password")
            return redirect('home')

        myuser=User.objects.create_superuser(username,email,password1)
        myuser.first_name=fname
        myuser.last_name=lname

        myuser.is_active = False
        myuser.is_superuser = True
        myuser.save()
        messages.success(request, "Account created Sucessfully. Please check your email to confirm your email address in order to activate your account.")
        
        subject="Welcome to Scholarship/Fellowship!"
        message = "Hello " + myuser.first_name + "!! \n" + "Thank you for visiting our website\n. We have also sent you a confirmation email, please confirm your email address. \nThanking You"        
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)

        current_site = get_current_site(request)
        email_subject = "Confirm your Scholarship/Fellowship Login!!"
        message2 = render_to_string('email_confirmation.html',{
            
            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser)
        })
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email],
        )
        email.fail_silently = True
        email.send()

        return redirect('signin')
    
    return render(request, "authentication/signup.html")

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@csrf_exempt
def signin(request):
    if request.method == "POST":
        username = request.POST['username']
        password1 = request.POST['password1']

        user = authenticate(username=username, password=password1)

        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('edit_page')  # Redirect to the edit page for superuser
            else:
                fname = user.first_name
                return render(request, "authentication/index.html", {'fname': fname})
        else:
            messages.error(request, "Bad Credentials!")
            return redirect('home')  # Redirect to home if login fails

    return render(request, "authentication/signin.html")


@csrf_protect
@login_required
def edit_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            Name = request.POST.get('Name')
            Eligibility = request.POST.get('Eligibility')
            Eligible = request.POST.get('Eligible')
            Links_online_application = request.POST.get('Links_online_application')
            Contacts_offline_applications = request.POST.get('Contacts_offline_applications')
            Scholarship_Fellowship = request.POST.get('Scholarship_Fellowship')
            Level = request.POST.get('Level')
            State = request.POST.get('State')
            Application_Period = request.POST.get('Application_Period')

            if not Name:
                messages.error(request, "Name cannot be empty.")
                return redirect('edit_page')

            Scholarship.objects.create(
                Name=Name,
                Eligibility=Eligibility,
                Eligible=Eligible,
                Links_online_application=Links_online_application,
                Contacts_offline_applications=Contacts_offline_applications,
                Scholarship_Fellowship=Scholarship_Fellowship,
                Level=Level,
                State=State,
                Application_Period=Application_Period
            )

            update_csv_file()

            messages.success(request, "New data added successfully.")
            return redirect('edit_page')

        elif action == 'delete':
            name_to_delete = request.POST.get('name_to_delete')
            if not name_to_delete:
                messages.error(request, "Name to delete cannot be empty.")
                return redirect('edit_page')

            scholarship_to_delete = Scholarship.objects.filter(Name=name_to_delete).first()
            if scholarship_to_delete:

                return render(request, 'authentication/confirm_delete.html', {'scholarship_to_delete': scholarship_to_delete})
            else:
                messages.error(request, "Scholarship not found for deletion.")
                return redirect('edit_page')

    return render(request, "authentication/edit.html")
@csrf_exempt
@login_required
def confirm_delete(request):
    if request.method == 'POST':
        scholarship_id = request.POST.get('scholarship_id')

        scholarship_to_delete = Scholarship.objects.filter(id=scholarship_id).first()

        if scholarship_to_delete:

            scholarship_to_delete.delete()

            update_csv_file()

            messages.success(request, "Scholarship deleted successfully.")
            return redirect('index')

    messages.error(request, "Deletion failed.")
    return redirect('edit_page')

def update_csv_file():
    csv_file_path = 'templates/SchollarShips in India.csv'
    print(f"Updating CSV file: {csv_file_path}")

    with open(csv_file_path, 'w', newline='', encoding='latin-1') as csvfile:
        fieldnames = ['Name', 'Eligibility', 'Eligible', 'Links_online_application',
                      'Contacts_offline_applications', 'Special_Categories', 'Scholarship_Fellowship',
                      'Level', 'State', 'Application_Period']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        scholarships_data = Scholarship.objects.all()
        for scholarship in scholarships_data:
            writer.writerow({
                'Name': scholarship.Name,
                'Eligibility': scholarship.Eligibility,
                'Eligible': scholarship.Eligible,
                'Links_online_application': scholarship.Links_online_application,
                'Contacts_offline_applications': scholarship.Contacts_offline_applications,
                'Special_Categories': scholarship.Special_Categories,
                'Scholarship_Fellowship': scholarship.Scholarship_Fellowship,
                'Level': scholarship.Level,
                'State': scholarship.State,
                'Application_Period': scholarship.Application_Period
            })

def signout(request):
    logout(request)
    messages.success(request, "Logged out Successfully!")
    return redirect('home')

def central(request):
    scholarships_data = Scholarship.objects.filter(Level='Central')
    return render(request, "authentication/central.html", {'scholarships_data': scholarships_data})

def central_result(request):
    selected_category = request.GET.get('category')
    special_categories = request.GET.get('special_categories')  
    qualification = request.GET.get('qualification')
    scholarships_data = Scholarship.objects.filter(Level='Central')

    if selected_category:
        scholarships_data = scholarships_data.filter(Q(Scholarship_Fellowship=selected_category))

    if special_categories:
        scholarships_data = scholarships_data.filter(Q(Special_Categories__contains=special_categories) |
                                                     Q(Special_Categories__contains=f'{special_categories} &'))
    
    if qualification:
        scholarships_data  = scholarships_data.filter(Q(Eligible__contains=qualification) |
                                                      Q(Eligible__contains=f'{qualification} &'))
    
    if not (selected_category or special_categories or qualification):
        return render(request, 'authentication/central.html')

    return render(request, 'authentication/central_result.html', {'scholarships_data': scholarships_data})

def state(request):
    scholarships_data = Scholarship.objects.filter(Level='State')
    return render(request, 'authentication/state.html',  {'scholarships_data': scholarships_data})

def state_result(request):
    selected_category = request.GET.get('category')  
    special_categories = request.GET.get('special_categories')
    state = request.GET.get('state')  
    qualification = request.GET.get('qualification')

    scholarships_data = Scholarship.objects.filter(Level='State')

    if selected_category:
        scholarships_data = scholarships_data.filter(Q(Scholarship_Fellowship=selected_category))

    if special_categories:
        scholarships_data = scholarships_data.filter(Q(Special_Categories__contains=special_categories) |
                                                     Q(Special_Categories__contains=f'{special_categories} &'))

    if state:
        scholarships_data = scholarships_data.filter(State=state)

    if qualification:
        scholarships_data  = scholarships_data.filter(Q(Eligible__contains=qualification) |
                                                      Q(Eligible__contains=f'{qualification} &'))

    if not (selected_category or special_categories or state or qualification):
        return render(request, 'authentication/state.html')

    return render(request, 'authentication/state_result.html', {'scholarships_data': scholarships_data})




def private(request):
    scholarships_data = Scholarship.objects.filter(Level='Private Organisation')
    return render(request, "authentication/private.html", {'scholarships_data': scholarships_data})

def private_result(request):
    selected_category = request.GET.get('category')  
    special_categories = request.GET.get('special_categories')  
    qualification = request.GET.get('qualification')
    scholarships_data = Scholarship.objects.filter(Level='Private Organisation')

    if selected_category:
        scholarships_data = scholarships_data.filter(Q(Scholarship_Fellowship=selected_category))

    if special_categories:
        scholarships_data = scholarships_data.filter(Q(Special_Categories__contains=special_categories) |
                                                     Q(Special_Categories__contains=f'{special_categories} &'))
        
    if qualification:
        scholarships_data  = scholarships_data.filter(Q(Eligible__contains=qualification) |
                                                      Q(Eligible__contains=f'{qualification} &'))
    
    if not (selected_category or special_categories or qualification):
        return render(request, 'authentication/private.html')

    return render(request, 'authentication/private_result.html', {'scholarships_data': scholarships_data})

def international(request):
    scholarships_data = Scholarship.objects.filter(Level='International Organisation')
    return render(request, "authentication/international.html", {'scholarships_data': scholarships_data})

def international_result(request):
    selected_category = request.GET.get('category')  
    special_categories = request.GET.get('special_categories')  
    qualification = request.GET.get('qualification')
    scholarships_data = Scholarship.objects.filter(Level='International Organisation')

    if selected_category:
        scholarships_data = scholarships_data.filter(Q(Scholarship_Fellowship=selected_category))

    if special_categories:
        scholarships_data = scholarships_data.filter(Q(Special_Categories__contains=special_categories) |
                                                     Q(Special_Categories__contains=f'{special_categories} &'))
        
    if qualification:
        scholarships_data  = scholarships_data.filter(Q(Eligible__contains=qualification) |
                                                      Q(Eligible__contains=f'{qualification} &'))

    if not (selected_category or special_categories or qualification):
        return render(request, 'authentication/international.html')

    return render(request, 'authentication/international_result.html', {'scholarships_data': scholarships_data})

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode('utf-8')
        myuser=User.objects.get(pk=uid)

    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser=None

    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active=True
        myuser.save()
        login(request,myuser)
        messages.success(request, "Your Account has been activated!!")
        return redirect('home')
    else:
        return render(request, 'activation_failed.html')
    
def result(request):
    return render(request, "authentication/result.html")

def search_result(request):
    search_query = request.GET.get('search')
    scholarships_data = Scholarship.objects.filter(Name__icontains=search_query)
    return render(request, 'authentication/search_result.html', {'scholarships_data': scholarships_data})

def central_search_result(request):
    search_query = request.GET.get('search')
    central_data = Scholarship.objects.filter(Level='Central', Name__icontains=search_query)
    return render(request, 'authentication/search_result.html', {'central_data': central_data})

def state_search_result(request):
    search_query = request.GET.get('search')
    state_data = Scholarship.objects.filter(Level='State', Name__icontains=search_query)
    return render(request, 'authentication/search_result.html', {'state_data': state_data})

def private_search_result(request):
    search_query = request.GET.get('search')
    private_data = Scholarship.objects.filter(Level='Private Organisation', Name__icontains=search_query)
    return render(request, 'authentication/search_result.html', {'private_data': private_data})

def international_search_result(request):
    search_query = request.GET.get('search')
    international_data = Scholarship.objects.filter(Level='International Organisation', Name__icontains=search_query)
    return render(request, 'authentication/search_result.html', {'international_data': international_data})

