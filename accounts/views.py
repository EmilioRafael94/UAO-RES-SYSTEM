import random
import uuid
import secrets
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect, get_object_or_404
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
from django.http import HttpResponseForbidden, Http404
from django.utils import timezone
from datetime import timedelta
from django.core.cache import cache
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def register(request):
    if request.method == 'POST' and not request.session.get('pending_registration'):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')

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


@login_required
def role_redirect_view(request):
    if request.user.is_superuser:
        return redirect('superuser_dashboard')
    elif request.user.is_staff:
        return redirect('admin_dashboard')
    else:
        return redirect('user_dashboard')

def login_view(request):
    social_auth_error = None
    error = request.GET.get('error')
    if error == 'forbidden':
        social_auth_error = 'Only @my.xu.edu.ph Google accounts are allowed.'

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back {user.username}!")
            return redirect('home')
        else:
            form.add_error(None, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form, 'social_auth_error': social_auth_error})

@login_required
def home_redirect(request):
    if request.user.is_superuser:
        return redirect('superuser_portal:superuser_dashboard')
    elif request.user.is_staff:
        return redirect('admin_portal:admin_dashboard')
    else:
        return redirect('user_portal:user_dashboard')


@login_required
def dashboard(request):
    return render(request, 'user_portal/dashboard.html')

def logout_view(request):
    logout(request)
    return redirect('login')

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

def forgot_password(request):
    """
    Handle the forgot password functionality for @gmail.com users.
    Google OAuth users do not need this as Google manages their password.
    """
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        
        if not email.endswith('@gmail.com'):
            messages.success(request, "If an account with that email exists, a password reset link has been sent.")
            return render(request, 'forgot_password.html')
            
        try:
            user = User.objects.get(email=email)
            
            try:
                social_user = user.social_auth.filter(provider='google-oauth2').first() if hasattr(user, 'social_auth') else None
                if social_user:
                    messages.success(request, "If an account with that email exists, a password reset link has been sent.")
                    return render(request, 'forgot_password.html')
            except:
                pass
                
            token = secrets.token_urlsafe(32)
            
            cache_key = f'password_reset_{token}'
            reset_data = {
                'user_id': user.id,
                'email': email,
                'expiry': timezone.now() + timedelta(hours=24)
            }
            cache.set(cache_key, reset_data, timeout=60*60*24)
            
            reset_url = request.build_absolute_uri(f'/accounts/reset-password/{token}/')
            
            subject = "Password Reset Request"
            html_content = render_to_string('password_reset_email.html', {
                'user': user,
                'reset_url': reset_url,
            })
            text_content = strip_tags(html_content)
            
            try:
                send_mail(
                    subject,
                    text_content,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    html_message=html_content,
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Failed to send password reset email: {e}")
                
        except User.DoesNotExist:
            pass
        
        messages.success(request, "If an account with that email exists, a password reset link has been sent.")
        return render(request, 'forgot_password.html')
        
    return render(request, 'forgot_password.html')


def reset_password(request, token):
    """Handle the password reset with a valid token."""
    cache_key = f'password_reset_{token}'
    reset_data = cache.get(cache_key)
    
    if not reset_data:
        messages.error(request, "Invalid or expired password reset link. Please request a new one.")
        return redirect('accounts:forgot_password')
        
    if timezone.now() > reset_data['expiry']:
        cache.delete(cache_key)
        messages.error(request, "This password reset link has expired. Please request a new one.")
        return redirect('accounts:forgot_password')
    
    try:
        user = User.objects.get(id=reset_data['user_id'], email=reset_data['email'])
    except User.DoesNotExist:
        cache.delete(cache_key)
        messages.error(request, "Invalid reset link. Please request a new one.")
        return redirect('accounts:forgot_password')
    
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if not password or len(password) < 8:
            messages.error(request, "Please enter a valid password (minimum 8 characters).")
            return render(request, 'reset_password.html', {'token': token})
            
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'reset_password.html', {'token': token})
            
        user.set_password(password)
        user.save()
        
        cache.delete(cache_key)
        
        try:
            current_time = timezone.now()
            subject = "Your Password Has Been Reset"
            html_content = render_to_string('password_reset_notification_email.html', {
                'user': user,
                'timestamp': current_time,
            })
            text_content = strip_tags(html_content)
            
            send_mail(
                subject,
                text_content,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_content,
                fail_silently=True,
            )
        except Exception as e:
            print(f"Failed to send password reset notification: {e}")
        
        messages.success(request, "Your password has been reset successfully. You can now log in with your new password.")
        return redirect('accounts:login')
    
    return render(request, 'reset_password.html', {'token': token})

