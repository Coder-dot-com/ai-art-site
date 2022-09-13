from django.http import HttpResponse
from django.shortcuts import render
from quiz_backend.views import _session

# Create your views here.
def receive_fbp_post(request):
    print(request)
    print(request.POST)

    fbp = request.POST['fbp']
    print("fbp is")
    print(fbp)


    #Now need to pass fbp on to session
    try:
        session = _session(request)
    
        session.latest_fbp = str(fbp)
        session.save()

    except Exception as e:
        print(e)

    return HttpResponse("Recieved")