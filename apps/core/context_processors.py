from django.conf import settings

def settings_export(request):
    return {
        'DEBUG': settings.DEBUG,
    }