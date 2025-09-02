from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.utils.translation import gettext_lazy as _
from .forms import LoginForm, WarrantyClaimForm, WarrantyClaimReadOnlyForm, ClaimSparePartForm, ClaimLabourForm
from .models import WarrantyClaim, SparePart, Labour
import json


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
    if getattr(user, 'is_partner', False):
        claims = user.get_partner_claims()
    else:
        claims = WarrantyClaim.objects.all()
    return render(request, "portal/warranty_claims.html", {"claims": claims})

def claim_details(request, claim_id):
    """Show a read-only view of a specific claim with its parts and labours."""
    claim = get_object_or_404(
        WarrantyClaim.objects.prefetch_related(
            'parts__spare_part', 'labours__labour', 'customer', 'partner_service', 'created_by'
        ),
        pk=claim_id,
    )
    form = WarrantyClaimReadOnlyForm(instance=claim)
    return render(request, 'portal/claim_details.html', {"form": form, "claim": claim})



def users(request):
    pass

def customers(request):
    pass

@login_required()
def create_claim(request):
    """Create a new warranty claim with optional parts and labour items."""
    if request.method == "POST":
        form = WarrantyClaimForm(request.POST)
        if form.is_valid():
            claim = form.save(commit=False)
            claim.created_by = request.user
            claim.partner_service = request.user.partner_fields.partner_service
            claim.save()

            # Collect multiple spare parts added via client-side list (parts_json)
            parts_json = (request.POST.get('parts_json') or '').strip()
            created_parts_count = 0
            if parts_json:
                try:
                    parts = json.loads(parts_json)
                    if isinstance(parts, list):
                        for item in parts:
                            data = {
                                'stock_code': (item.get('stock_code') or '').strip(),
                                'quantity': item.get('quantity') or 1,
                                'currency': item.get('currency') or None,
                            }
                            if data['stock_code']:
                                sp_form = ClaimSparePartForm(data)
                                if sp_form.is_valid():
                                    try:
                                        sp_form.save(claim=claim)
                                        created_parts_count += 1
                                    except Exception:
                                        # ignore individual part errors to not block claim creation
                                        pass
                except Exception:
                    # invalid JSON, fall back to single form
                    pass

            # Fallback: if no parts_json or nothing created, try single inline spare part fields
            if created_parts_count == 0:
                sp_form = ClaimSparePartForm(request.POST)
                if sp_form.is_valid() and sp_form.cleaned_data.get('stock_code'):
                    try:
                        sp_form.save(claim=claim)
                        created_parts_count = 1
                    except Exception:
                        pass

            # Handle labours_json (multiple labour items)
            labours_json = (request.POST.get('labours_json') or '').strip()
            created_labours = 0
            if labours_json:
                try:
                    labs = json.loads(labours_json)
                    if isinstance(labs, list):
                        for item in labs:
                            data = {
                                'code': (item.get('code') or '').strip(),
                                'duration': item.get('duration') or 1,
                                'currency': item.get('currency') or None,
                            }
                            if data['code']:
                                lb_form = ClaimLabourForm(data)
                                if lb_form.is_valid():
                                    try:
                                        lb_form.save(claim=claim)
                                        created_labours += 1
                                    except Exception:
                                        pass
                except Exception:
                    pass

            # Enforce: at least one of parts or labour must be present
            if (created_parts_count + created_labours) == 0:
                form.add_error(None, _("Add at least one Spare Part or one Labour item."))
                return render(request, "portal/claim_form.html", {
                    "form": form,
                    "spare_form": ClaimSparePartForm(request.POST),
                    "labour_form": ClaimLabourForm(request.POST),
                    "parts_json": request.POST.get('parts_json', ''),
                    "labours_json": request.POST.get('labours_json', ''),
                })

            return redirect("portal:claims")
        # Form invalid
        return render(request, "portal/claim_form.html", {
            "form": form,
            "spare_form": ClaimSparePartForm(request.POST),
            "labour_form": ClaimLabourForm(request.POST),
            "parts_json": request.POST.get('parts_json', ''),
            "labours_json": request.POST.get('labours_json', ''),
        })

    # GET
    return render(request, "portal/claim_form.html", {
        "form": WarrantyClaimForm(),
        "spare_form": ClaimSparePartForm(),
        "labour_form": ClaimLabourForm(),
        "parts_json": "[]",
        "labours_json": "[]",
    })


def update_claim(request):
    pass

@login_required()
def part_info(request):
    """API: Return part description and unit price for a given stock_code and currency."""
    if request.method != 'GET':
        return HttpResponseBadRequest("Only GET is allowed")
    stock = (request.GET.get('stock_code') or '').strip()
    currency = (request.GET.get('currency') or '').strip() or SparePart.Currency.EUR
    if not stock:
        return HttpResponseBadRequest("Missing stock_code")
    try:
        spare = SparePart.objects.get(stock_code=stock)
    except SparePart.DoesNotExist:
        return HttpResponseNotFound("Stock code not found")
    unit = spare.get_price(currency) or 0
    return JsonResponse({
        'stock_code': spare.stock_code,
        'description': spare.description,
        'currency': currency,
        'unit_price': float(unit),
    })


@login_required()
def labour_info(request):
    """API: Return labour description and unit rate for a given code and currency."""
    if request.method != 'GET':
        return HttpResponseBadRequest("Only GET is allowed")
    code = (request.GET.get('code') or '').strip()
    currency = (request.GET.get('currency') or '').strip() or Labour.Currency.EUR
    if not code:
        return HttpResponseBadRequest("Missing code")
    try:
        lab = Labour.objects.get(code=code)
    except Labour.DoesNotExist:
        return HttpResponseNotFound("Labour code not found")
    rate = lab.get_rate(currency) or 0
    return JsonResponse({
        'code': lab.code,
        'description': lab.description,
        'currency': currency,
        'unit_rate': float(rate),
    })
