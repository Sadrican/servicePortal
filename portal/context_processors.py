# Python
# portal/context_processors.py


def layout_context(request):
        user = getattr(request, "user", None)
        is_partner = getattr(user, "is_partner", False)() if callable(getattr(user, "is_partner", None)) else getattr(
            user, "is_partner", False)
        ps_info = getattr(getattr(user, "partner_fields", None), "partner_service", None)

        return {
            "isPartner": bool(is_partner),
            "psInfo": ps_info,
            "userRole": getattr(getattr(user, "role", None), "label", None) or getattr(user, "role", None),
            "viewLogin": not (user and user.is_authenticated),
        }
