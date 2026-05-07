from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.db.models import Q
from .models import User


def register_view(request):
    """
    إنشاء حساب جديد
    """
    if request.method == "POST":
        email = (request.POST.get("email") or "").strip().lower()
        username = (request.POST.get("username") or "").strip()
        password1 = request.POST.get("password1") or ""
        password2 = request.POST.get("password2") or ""

        if not email or not username or not password1:
            messages.error(request, "جميع الحقول مطلوبة")
            return redirect("register")

        if password1 != password2:
            messages.error(request, "كلمتا المرور غير متطابقتين")
            return redirect("register")

        # استعلام واحد للتحقق من تكرار الإيميل أو اسم المستخدم
        existing = (
            User.objects.filter(Q(email=email) | Q(username__iexact=username))
            .values("email", "username")
            .first()
        )
        if existing:
            if existing["email"] == email:
                messages.error(request, "البريد الإلكتروني مستخدم مسبقًا")
            else:
                messages.error(request, "اسم المستخدم مستخدم مسبقًا")
            return redirect("register")

        try:
            validate_password(password1)
        except ValidationError as e:
            for err in e.messages:
                messages.error(request, err)
            return redirect("register")

        try:
            user = User.objects.create_user(
                email=email,
                username=username,
                password=password1,
            )
        except Exception:
            messages.error(request, "حدث خطأ أثناء إنشاء الحساب")
            return redirect("register")

        # ضمان نجاح المصادقة باستخدام USERNAME_FIELD = email
        user = authenticate(request, username=email, password=password1)
        if user is not None:
            login(request, user)
        return redirect("home")

    return render(request, "account-templates/register.html")


def login_view(request):
    """
    تسجيل الدخول
    """
    if request.method == "POST":
        email = (request.POST.get("email") or "").strip().lower()
        password = request.POST.get("password") or ""

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")
        messages.error(request, "بيانات الدخول غير صحيحة")

    return render(request, "account-templates/login.html")
