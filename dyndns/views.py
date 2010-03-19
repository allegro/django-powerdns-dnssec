# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from dyndns.auth import http_auth
from dyndns.models import Record
import re

@http_auth
def update(request):
    """
    Implement the DNS Update API as defined at:
        http://www.dyndns.com/developers/specs/syntax.html
    """
    try:
	#Parse variables from HTTP GET
	host_list=request.GET['hostname'].split(',',20)
	ip=request.GET['myip']
    except:
	## No hostnames were specified
	return render_to_response('dyndns/results.html',{'result_list': ['notfqdn']})
    try:
	## TODO: YES activates feature and turns on offline redirect for hostname (if set). NOCHG could be used to keep current state.
        offline = request.GET['offline']
    except:
	pass
    # Check that ip is the correct format
    if (re.match('\d+\\.\d+\\.\d+\\.\d+$', ip)) is None:
	return render_to_response('dyndns/results.html', {'result_list': ['notfqdn']})
    elif ip == '127.0.0.1':
        return render_to_response('dyndns/results.html', {'result_list': ['good 127.0.0.1']})
    else:
	results = []
	for host in host_list:
	    ## TODO:  Check that  hostname is in correct form and matches our domain(s)
	    #t=re.compile('\w{12}$')
	    #is_hostname=t.match(host)
	    ## return render_to_response('dyndns/results.html',{'error': 'notfqdn'})
	    try:
		## Update hostname it is exists in database
		h = Record.objects.get(name=host)
		h.content=ip
		h.save()
		results.append('good')
	    except :
		## Add hostname if it doesnt exist in database
		## TODO: Support more than one domain!
		h = Record(domain_id=1,type='A',name=host,content=ip,ttl=600,prio=1,change_date=1)
		h.save()
		results.append('good')
	return render_to_response('dyndns/results.html', {'result_list': results})

