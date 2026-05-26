from django.shortcuts import render


def page_not_found(request, exception):
    template = 'pages/404.html'
    return render(request, template, status=404)


def csrf_failure(request, reason=''):
    template = 'pages/403csrf.html'
    return render(request, template, status=403)


def server_error(request):
    template = 'pages/500.html'
    return render(request, template, status=500)


def trigger_error(request):
    raise Exception("Тестовая ошибка 500")
