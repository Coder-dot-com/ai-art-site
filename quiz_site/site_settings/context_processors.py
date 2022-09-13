from .models import SiteSettings

def get_site_email_logo(request):

    try:
        site_settings = (SiteSettings.objects.all()[0])

    except:
        print("Error setting site object")
        site_settings = None
    
    return dict(site=site_settings)

