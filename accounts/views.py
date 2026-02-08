from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import User


def register_view(request):
    """
    إنشاء حساب جديد
    """
    if request.method == "POST":
        email = request.POST.get("email")
        username = request.POST.get("username")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "كلمتا المرور غير متطابقتين")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "البريد الإلكتروني مستخدم مسبقًا")
            return redirect("register")

        user = User.objects.create_user(
            email=email,
            username=username,
            password=password1
        )

        login(request, user)
        return redirect("catalog:catalog_home")  # غيرها حسب صفحتك الرئيسية

    return render(request, "account-templates/register.html")



def login_view(request):
    """
    تسجيل الدخول
    """
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect("catalog:catalog_home")
        else:
            messages.error(request, "بيانات الدخول غير صحيحة")

    return render(request, "account-templates/login.html")

