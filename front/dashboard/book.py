from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render_to_response
from dashboard.models import StatMachine
from dashboard.models import StatInstance
import get
from django.core.cache import cache
def show(request):

    sm = StatMachine.objects.filter(cluster='beijing').values_list('all_machine').order_by("stat_time")
    print sm
    return render_to_response('latest_books.html',{'onebook':'this is a value'})

