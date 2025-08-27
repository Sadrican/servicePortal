from django.shortcuts import render
from .forms import LoginForm
# Create your views here.
def login(request):
    return render(request, 'portal/login.html',context={
        "form":LoginForm(),
    })

def logout(request):
    pass
def ssh_home(request):
    pass
def partner_home(request):
    pass

