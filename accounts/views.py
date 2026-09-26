from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def signup(request):

    if request.method == "POST":

        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()

            return redirect("login")

    else:

        form = UserCreationForm()

    return render(
        request,
        "registration/signup.html",
        {"form": form}
    )


@login_required
def dashboard(request):

    return render(
        request,
        "dashboard.html"
    )