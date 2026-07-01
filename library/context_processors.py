from .models import OrganizationSetting

def organization_settings(request):
    try:
        org_data = OrganizationSetting.objects.first()
    except Exception:
        org_data = None
    return {
        'org_data': org_data
    }
