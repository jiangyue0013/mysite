from django.http import HttpResponse

# Create your views here.
def index(request):
    return HttpResponse("Hello, you're at the polls index. Name: Yue Jiang")