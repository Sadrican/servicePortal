from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
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
                    "viewLogin": True,
                })

    else:

        user = request.user
        if user.is_authenticated:
            return redirect("portal:home")
        else:
            return render(request,"portal/login.html",{
                "form":LoginForm,
                "viewLogin":True,
            })


def logout_view(request):

    logout(request)
    return redirect("portal:login")

@login_required()
def home(request):
    if request.method=="GET":
        user =request.user
        return render(request, "portal/homePage.html", context={
            "isPartner": user.is_partner,
            "userRole": user.role,
        })

    else:
        raise Exception("NİCE TRY YOU FUCKİNG FUCK")

@login_required()
def claims_page(request):
    user = request.user
    if request.method=="GET":
        if user.is_partner:
            return render(request,"portal/warranty_claims.html",{

                "userRole": user.role,
                "claims": user.get_partner_claims()
            })
        else:
            claims = WarrantyClaim.objects.all()
            return render(request,"portal/warranty_claims.html",{
                "isPartner": user.is_partner,
                "userRole": user.role,
                "claims": claims
            })
    else:
        raise Exception("NİCE TRY YOU FUCKİNG FUCK")

def claim_details(request,claim_id):
    user = request.user
    claim = WarrantyClaim.objects.get(pk=claim_id)
    return render(request,'portal/claim_details.html',{
        "claim":claim,
        "userRole": user.role,
    })


def users(request):
    pass

def customers(request):
    pass

@login_required()
def create_claim(request):
    user = request.user
    if not getattr(user, 'is_partner', False):
        return HttpResponseForbidden('Only Partner users can create claims.')

    if request.method == 'POST':
        form = WarrantyClaimForm(request.POST, user=user)
        if form.is_valid():
            claim = form.save(commit=False)
            # Set partner_service and createdBy from current user
            try:
                claim.partner_service = user.partner_fields.partner_service
            except Exception:
                return HttpResponseForbidden('Partner Service not associated with user.')
            claim.createdBy = user
            claim.save()
            return redirect('portal:claims')
    else:
        form = WarrantyClaimForm(user=user)

    return render(request, 'portal/claim_form.html', {
        'form': form,
        'userRole': user.role,
        'isPartner': user.is_partner,
    })