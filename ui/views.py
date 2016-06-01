# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template.context import RequestContext


def start_page(request):
    return render_to_response(
        'ui/index.html', {},
        context_instance=RequestContext(request),
    )
