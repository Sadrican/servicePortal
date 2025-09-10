# Python
# portal/context_processors.py


def layout_context(request):
    #sends every page those info if user is logged in
    user = request.user
    if user.is_authenticated:
        if user.is_partner:
            return {
                "isPartner": user.is_partner or user.is_partner_admin,
                "isAdmin": user.is_partner_admin or user.is_ssh_admin,
                "userRole": user.role,
                "psInfo": user.partner_fields.partner_service,
            }
        else:
            return {
                "isPartner": user.is_partner or user.is_partner_admin,
                "isAdmin": user.is_partner_admin or user.is_ssh_admin,
                "userRole": user.role,
            }
    else:
        return {}
