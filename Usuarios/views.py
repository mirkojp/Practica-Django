from django.shortcuts import render
from django.http import JsonResponse

from Productos.models import Funko
from Productos.serializers import FunkoSerializer


# Create your views here.
def get_funkos():
    funkos = Funko.objects.all()[:8]
    funkos_serializer = FunkoSerializer(funkos, many=True)
    return funkos_serializer.data

def home(request):
    funkos = get_funkos()
    return render(request, "home.html", {'funkos': funkos})