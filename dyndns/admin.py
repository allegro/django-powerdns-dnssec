# -*- coding: utf-8 -*-
from django.contrib import admin
from dyndns.models import Record

class RecordAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'content')
    list_filter = ['type']
    search_fields  = ('name','content',)

admin.site.register(Record,RecordAdmin)
