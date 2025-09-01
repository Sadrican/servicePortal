from datetime import date

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from pyexpat.errors import messages

from .forms import LoginForm, WarrantyClaimForm

from .models import WarrantyClaim


# Create your views here.
def login_view(request):

    if request.method=="POST":

            username = request.POST.get("username")
            password = request.POST.get("password")
            user = authenticate(request, username=username,password=password)
            if user is not None:
                login(request,user)
                return redirect("portal:home")

            else:
                return render(request,"portal/login.html",{
                    "form": LoginForm(request.POST),
                    "error": "Invalid Credentials",
                })

    else:

        user = request.user
        if user.is_authenticated:
            return redirect("portal:home")
        else:
            return render(request,"portal/login.html",{
                "form":LoginForm,
            })


def logout_view(request):

    logout(request)
    return redirect("portal:login")

@login_required()
def home(request):
    if request.method=="GET":
        user =request.user
        return render(request, "portal/home_page.html")

    else:
        raise Exception("NİCE TRY YOU FUCKİNG FUCK")

@login_required()
def claims_page(request):
    user = request.user
    if request.method=="GET":
        if user.is_partner:
            return render(request,"portal/warranty_claims.html",{

                "claims": user.get_partner_claims()
            })
        else:
            claims = WarrantyClaim.objects.all()
            return render(request,"portal/warranty_claims.html",{
                "claims": claims
            })
    else:
        raise Exception("NİCE TRY YOU FUCKİNG FUCK")

def claim_details(request,claim_id):
    claim = WarrantyClaim.objects.get(pk=claim_id)
    return render(request,'portal/claim_details.html',{
        "claim":claim,
    })


def users(request):
    pass

def customers(request):
    pass

@login_required()
def create_claim(request):

    if request.method=="POST":
        form = WarrantyClaimForm(request.POST)
        if form.is_valid():
            claim = form.save(commit=False)
            claim.created_by = request.user
            claim.partner_service = request.user.partner_fields.partner_service
            claim.save()
            return redirect("portal:claims")
        else:
            return render(request,"portal/claim_form.html",{
                "form":form,
            })
    else:
        return render(request,"portal/claim_form.html",{
            "form":WarrantyClaimForm(),
        })

