from django.shortcuts import render

# Create your views here.



def hero(request):

    return render(request, 'main/hero.html')

def about(request):
    
    return render(request, 'main/about.html')

def customer_dashboard(request):

    return render(request, 'dash/customer_dashboard.html')

