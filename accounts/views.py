import random
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from .models import UserProfile 
from .forms import CustomUserCreationForm
from django.contrib.auth.models import User
from user_portal.models import Profile
from social_django.utils import load_strategy
from social_core.exceptions import AuthForbidden
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseForbidden


def register(request):
    # Step 1: Registration details form
    if request.method == 'POST' and not request.session.get('pending_registration'):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')

            # Check for duplicate username or email
            if User.objects.filter(username=username).exists():
                form.add_error('username', "Username is already taken.")
            elif User.objects.filter(email=email).exists():
                form.add_error('email', "Email is already registered.")
            else:
                try:
                    full_name = request.POST.get('full_name', '').strip()
                    if not full_name:
                        form.add_error(None, "Full name is required.")
                        raise ValueError("Full name is missing.")
                    name_parts = full_name.split(' ', 1)
                    first_name = name_parts[0]
                    last_name = name_parts[1] if len(name_parts) > 1 else ''
                    phone = form.cleaned_data['phone']
                    password = form.cleaned_data['password1']
                    verification_code = f"{random.randint(100000, 999999)}"
                    # Set role to Alumni/Guest for all new registrations
                    request.session['pending_registration'] = {
                        'username': username,
                        'email': email,
                        'first_name': first_name,
                        'last_name': last_name,
                        'phone': phone,
                        'password': password,
                        'verification_code': verification_code,
                        'role': 'Alumni/Guest',
                    }
                    send_mail(
                        'Your Verification Code',
                        f'Your verification code is: {verification_code}',
                        settings.DEFAULT_FROM_EMAIL,
                        [email],
                        fail_silently=False,
                    )
                    return render(request, 'register.html', {'code_step': True})
                except Exception as e:
                    form.add_error(None, str(e))
        return render(request, 'register.html', {'form': form})

    # Step 2: Code verification form
    elif request.method == 'POST' and request.session.get('pending_registration'):
        code = request.POST.get('verification_code')
        pending = request.session['pending_registration']
        if code == pending['verification_code']:
            try:
                user = User.objects.create_user(
                    username=pending['username'],
                    email=pending['email'],
                    password=pending['password'],
                    first_name=pending['first_name'],
                    last_name=pending['last_name'],
                )
                Profile.objects.create(
                    user=user,
                    phone=pending['phone'],
                    role='Alumni/Guest',
                    course='',
                    is_verified=True,
                    verification_code=None
                )
                del request.session['pending_registration']
                messages.success(request, "Registration successful! Please log in.")
                return redirect('accounts:login')
            except Exception as e:
                messages.error(request, f"Error creating account: {e}")
                return redirect('accounts:register')
        else:
            messages.error(request, "Invalid verification code. Please try again.")
            return render(request, 'register.html', {'code_step': True})
    else:
        form = CustomUserCreationForm()
        return render(request, 'register.html', {'form': form})


# Role-based redirect view
@login_required
def role_redirect_view(request):
    if request.user.is_superuser:
        return redirect('superuser_dashboard')  # Replace with your superuser dashboard URL
    elif request.user.is_staff:
        return redirect('admin_dashboard')  # Replace with your admin dashboard URL
    else:
        return redirect('user_dashboard')  # Replace with your user dashboard URL

# Login view
def login_view(request):
    # Check for social-auth error in GET params
    social_auth_error = None
    error = request.GET.get('error')
    if error == 'forbidden':
        social_auth_error = 'Only @my.xu.edu.ph Google accounts are allowed.'

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)  # Pass the request to the form
        if form.is_valid():
            user = form.get_user()  # Get the user object
            login(request, user)
            messages.success(request, f"Welcome back {user.username}!")
            return redirect('home')  # Redirect to the home page or dashboard after successful login
        else:
            # Invalid login attempt, show error message
            form.add_error(None, "Invalid username or password.")
    else:
        form = AuthenticationForm()  # Create an empty form instance for GET request

    return render(request, 'login.html', {'form': form, 'social_auth_error': social_auth_error})  # Pass the form to the template

# Home redirect view after login based on user role
@login_required
def home_redirect(request):
    if request.user.is_superuser:
        return redirect('superuser_portal:superuser_dashboard')  # Superuser dashboard
    elif request.user.is_staff:
        return redirect('admin_portal:admin_dashboard')  # Admin dashboard
    else:
        return redirect('user_portal:user_dashboard')  # User dashboard


# User dashboard view (for logged-in users)
@login_required
def dashboard(request):
    return render(request, 'user_portal/dashboard.html')

def logout_view(request):
    logout(request)
    return redirect('login')  # Or wherever your login page is

def user_register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)

        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        id_upload = request.FILES.get('id_upload')

        if form.is_valid():
            user = form.save(commit=False)
            user.email = email
            user.save()

            UserProfile.objects.create(
                user=user,
                full_name=full_name,
                phone=phone,
                id_upload=id_upload
            )

            messages.success(request, "Registration successful! Please log in.")
            return redirect('accounts:login')
        else:
            messages.error(request, "Form submission failed. Please check your input.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})

def forbidden(request):
    """Render a user-friendly forbidden error page for social-auth forbidden logins."""
    return render(request, 'forbidden.html', status=403)

def google_auth_forbidden(request):
    """
    Custom error page for forbidden Google OAuth logins.
    Shows a user-friendly message if the email is not @my.xu.edu.ph.
    """
    return render(request, 'accounts/google_auth_forbidden.html')

