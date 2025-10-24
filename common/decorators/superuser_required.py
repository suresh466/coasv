from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect


def superuser_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if request.user.is_superuser:
            return view(request, *args, **kwargs)
        messages.error(request, "Unauthorized action!")
        referer = request.META.get("HTTP_REFERER")
        if referer:
            return redirect(referer)
        else:
            return redirect("/admin/login/")

    return wrapper
