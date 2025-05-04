from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from .models import UserProfile 
from .forms import CustomUserCreationForm
from django.contrib.auth.models import User


# User registration view
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome {user.username}!")
            return redirect('role_redirect')  # Redirect to role-based view
    else:
        form = UserCreationForm()
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

    return render(request, 'login.html', {'form': form})  # Pass the form to the template

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
        course = request.POST.get('course')
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
                course=course,
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
