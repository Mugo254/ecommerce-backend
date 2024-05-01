from django.http import JsonResponse
import datetime

def get_current_year():
    current_year = datetime.datetime.now().year
    print("Current year:", current_year)

    return current_year

def error_404(request,exception):
    message=('The endpoint is not found')

    response = JsonResponse(data={'message':message,'status_code':404})
    response.status_code = 404
    return response

def error_500(request):
    message=('An error happened on us')

    response = JsonResponse(data={'message':message,'status_code':500})
    response.status_code = 500
    return response