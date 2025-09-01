# Python
# portal/context_processors.py


def partner_service_info(request):

    user = getattr(request, "user", None)
    if user and user.is_authenticated:
        # Only include for relevant roles; adjust as needed
        if hasattr(request, "ps_info"):
            return {"psInfo": request.ps_info}

        try:
            ps = user.partner_fields.partner_service
            request.ps_info = {
                "name": ps.name,
                "email": ps.email,
                "phone_number": ps.phone_number,
                "address": ps.address,
            }
        except Exception:
            request.ps_info = None
        return {"psInfo": request.ps_info}
    return {"psInfo": None}
