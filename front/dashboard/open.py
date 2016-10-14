from django.http import HttpResponse
from django.shortcuts import render_to_response
def index(request):
    param = request.GET   
    stat_time = param['stat_time']
    cluster = param['cluster']
    infile = '/home/work/data/'+stat_time+'/'+cluster+'.machine_health.dump'
    outfile = '/home/work/dashboard/front/dashboard/templates/fault_machine.html'
    fin = open(infile)
    fout = open(outfile,'w')
    for f in fin:   
        f = f.replace(' ','&nbsp;')
        fout.write(f)
        fout.write('<br/>')
    fin.close()
    fout.close()
    return render_to_response('fault_machine.html')
