from django.http import HttpResponse
def index(request):
    param = request.GET   
    stat_time = param['stat_time']
    cluster = param['cluster']
    filename = '/home/work/data/'+stat_time+'/'+cluster+'.machine_health.dump'
    f = open(filename)
    data = f.read()
    f.close()
    response = HttpResponse(data)
    response['Content-Disposition'] = 'attachment; filename=%s' %filename
    return response
