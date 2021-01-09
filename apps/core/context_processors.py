from django.conf import settings

def about(request):
    return {'ABOUT_URL': settings.ABOUT_URL}
