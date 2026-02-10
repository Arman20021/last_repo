from django.shortcuts import render, redirect
 
from django.contrib.auth.models import User,Group
from django.contrib.auth import login,   logout
from django.contrib.auth.tokens import default_token_generator
from users.forms import CustomRegistrationForm
from django.contrib import messages
from users.forms import LoginForm,AssignRoleForm,CreateGroupForm
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required,user_passes_test

# Create your views here.

#test for user
# Test for users
def is_admin(user):
    return user.groups.filter(name='CEO').exists()


def is_manager(user):
    return user.groups.filter(name='Manager').exists()

def is_participant(user):
    return user.groups.filter(name='Participant').exists()

from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator

def sign_up(request):
    form = CustomRegistrationForm()

    if request.method == 'POST':
        form = CustomRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.is_active = False
            user.save()

            # ✅ SEND EMAIL SAFELY (NON-BLOCKING)
            token = default_token_generator.make_token(user)
            activation_url = f"{settings.FRONTEND_URL}/users/activate/{user.id}/{token}/"

            subject = "Activate your account"
            message = f"""
Hi {user.username},

Please activate your account using the link below:
{activation_url}

Thank you
"""

            try:
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [user.email],
                    fail_silently=False,  # 🔑 CRITICAL
                )
            except Exception as e:
                print("Email failed:", e)

            messages.success(request, 'A confirmation email has been sent.')
            return redirect('sign-in')

    return render(request, 'registration/register.html', {"form": form})



def sign_in(request):
    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # 🔹 ROLE-BASED REDIRECTION
            if is_admin(user):
                return redirect('admin-dashboard')
            elif is_manager(user):
                return redirect('manager-dashboard')
            elif is_participant(user):
                return redirect('user-dashboard')
            else:
                return redirect('no-permission')

    return render(request, 'registration/login.html', {'form': form})

     

         

  

@login_required
def sign_out(request):
    if request.method == 'POST':
        logout(request)
        return redirect('sign-in')
    


def activate_user(request,user_id,token):
    try:
        user=User.objects.get(id=user_id)
        if default_token_generator.check_token(user,token):
                user.is_active=True
                user.save()
                return redirect('sign-in')
        else:
             return HttpResponse ("Invalid ID or token")
    except User.DoesNotExist:
         return HttpResponse("User not found")



@user_passes_test(is_admin, login_url='no-permission')
def admin_dashboard(request):
    users = User.objects.prefetch_related('groups')

    for user in users:
        groups = list(user.groups.all())  
        if groups:
            user.group_name = groups[0].name
        else:
            user.group_name = 'No Groups Assigned'

    return render(request, 'admin/dashboard.html', {'users': users})

@user_passes_test(is_admin,login_url='no-permission')
def assign_role(request, user_id):
    user = User.objects.get(id=user_id)
    form = AssignRoleForm()

    if request.method == 'POST':
        form = AssignRoleForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data.get('role')
            user.groups.clear()  # Remove old roles
            user.groups.add(role)
            messages.success(request, f"User {
                             user.username} has been assigned to the {role.name} role" 
                             )
            return redirect('admin-dashboard')

    return render(request, 'admin/assign_role.html', {"form": form})


@user_passes_test(is_admin,login_url='no-permission')
def create_group(request):
    form = CreateGroupForm()
    if request.method == 'POST':
        form = CreateGroupForm(request.POST)

        if form.is_valid():
            group = form.save()
            messages.success(request, f"Group {group.name} has been created successfully")
            return redirect('create-group')

    return render(request, 'admin/create_group.html', {'form': form})


@user_passes_test(is_admin,login_url='no-permission')
def group_list(request):
     groups=Group.objects.prefetch_related('permissions').all()
     return render(request,'admin/group_list.html',{'groups':groups})