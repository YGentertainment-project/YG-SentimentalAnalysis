from django.shortcuts import render

# Create your views here.
def base(request):
    '''
    general page
    '''
    return render(request, 'clipping/clipping.html')