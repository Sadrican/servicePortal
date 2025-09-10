from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render, redirect, get_object_or_404
from django.http import  HttpResponseBadRequest
from .forms import LoginForm, CreateWarrantyClaimForm, CreateClaimSparePartForm
from .models import WarrantyClaim
from .utility import get_sparepart_data

# Views for portal pages and APIs

def login_view(request):
    """Authenticate user and redirect to home; render login form on GET."""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("portal:home")
        # Invalid credentials: re-render with error and bound form
        return render(request, "portal/login.html", {
            "form": LoginForm(request.POST),
            "error": "Invalid Credentials",
        })

    # GET
    user = request.user
    if user.is_authenticated:
        return redirect("portal:home")
    return render(request, "portal/login.html", {
        "form": LoginForm,
    })


def logout_view(request):
    """Log the user out and redirect to login."""
    logout(request)
    return redirect("portal:login")

@login_required()
def home(request):
    """Render the portal home page; only GET supported."""
    if request.method == "GET":
        return render(request, "portal/home_page.html")
    return HttpResponseBadRequest("Only GET is allowed")

@login_required()
def claims_page(request):
    """List warranty claims. Partners see only their claims; admins see all."""
    if request.method != "GET":
        return HttpResponseBadRequest("Only GET is allowed")
    user = request.user
    if getattr(user, 'is_partner' or "is_partner_admin", False):
        claims = user.get_partner_claims()
    else:
        claims = WarrantyClaim.objects.all()
    return render(request, "portal/warranty_claims.html", {"claims": claims})

@login_required()
def claim_details(request, claim_id):
    """Show a read-only view of a specific claim with its parts and labours."""
    claim = get_object_or_404(WarrantyClaim, pk=claim_id)

    return render(request, "portal/claim_details.html", {
        "claim": claim,
        "parts": claim.spare_parts.all(),
    })





def users(request):
    pass

def customers(request):
    pass

@login_required()
def create_claim(request):
    """Create a new warranty claim with optional parts and labour items."""

    if request.method == "POST":
        form = CreateWarrantyClaimForm(request.POST)

        if form.is_valid():
            spare_part = form.clean_parts()
            print(spare_part)
            claim = form.save(commit=False)
            claim.created_by = request.user
            claim.partner_service = request.user.partner_fields.partner_service

            claim.save()
            return redirect("portal:claim_details", claim_id=claim.id)
        else:
            return render(request, "portal/claim_form.html", {
                "WarrantForm": form,
                "SparePartForm": CreateClaimSparePartForm(),
                "parts": get_sparepart_data()
            })

    else:
        warrant_form = CreateWarrantyClaimForm()
        spart_form = CreateClaimSparePartForm()
        parts = get_sparepart_data()
        parts_json = json.dumps(parts, cls=DjangoJSONEncoder)

        return render(request, "portal/claim_form.html", {
            "WarrantForm": warrant_form,
            "SparePartForm": spart_form,
            "parts": parts_json
        })



def update_claim(request):
    pass
