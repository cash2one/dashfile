#!/usr/bin/python
from django.http import HttpResponse
from django.shortcuts import render_to_response
import time
def index(request):
    default_date = time.strftime('%Y-%m-%d',time.localtime())
    param = request.GET
    target = param.get('file')
    um_date = param.get('um_date',default_date)
    infile = '/home/work/data_unused_machine/'+um_date+'/02-00/'+target[6:] 
    outfile = '/home/work/dashboard/front/dashboard/templates/unused_machine_json.html'
    fin = open(infile)
    fout = open(outfile,'w')
    for f in fin:
        fout.write(f)
        fout.write('</br>')
    fin.close()
    fout.close()
    return render_to_response('unused_machine_json.html')
    
