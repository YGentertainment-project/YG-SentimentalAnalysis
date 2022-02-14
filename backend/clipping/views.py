from django.shortcuts import render

# Create your views here.
def base(request):
    '''
    general page
    '''
    # db연결 필요
    values = {
        'groups': ['그룹1', '그룹2'],
        'keywords': ['키워드1', '키워드2'],
    }
    return render(request, 'clipping/clipping.html', values)