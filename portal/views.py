from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotFound
from .forms import LoginForm, WarrantyClaimForm, WarrantyClaimReadOnlyForm, ClaimSparePartForm
from .models import WarrantyClaim, SparePart
import json


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

def claim_details(request, claim_id):
    claim = get_object_or_404(
        WarrantyClaim.objects.prefetch_related('parts__spare_part', 'customer', 'partner_service', 'created_by'),
        pk=claim_id
    )
    form = WarrantyClaimReadOnlyForm(instance=claim)
    return render(request, 'portal/claim_details.html', {
        "form": form,
        "claim": claim,
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
            # handle multiple spare parts added via client-side list (parts_json)
            parts_json = request.POST.get('parts_json', '').strip()
            created_any = False
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
                                        created_any = True
                                    except Exception:
                                        # ignore individual part errors to not block claim creation
                                        pass
                except Exception:
                    # invalid JSON, fall back to single form
                    pass
            # fallback: if no parts_json or nothing created, try single inline spare part fields
            if not created_any:
                sp_form = ClaimSparePartForm(request.POST)
                if sp_form.is_valid() and sp_form.cleaned_data.get('stock_code'):
                    try:
                        sp_form.save(claim=claim)
                    except Exception:
                        pass
            return redirect("portal:claims")
        else:
            sp_form = ClaimSparePartForm(request.POST)
            return render(request,"portal/claim_form.html",{
                "form":form,
                "spare_form": sp_form,
                "parts_json": request.POST.get('parts_json', ''),
            })
    else:
        return render(request,"portal/claim_form.html",{
            "form":WarrantyClaimForm(),
            "spare_form": ClaimSparePartForm(),
            "parts_json": "[]",
        })


def update_claim(request):
    pass

@login_required()
def part_info(request):
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
