from django.http import HttpResponse


def customer_list(request):
    return HttpResponse("Customer list")
