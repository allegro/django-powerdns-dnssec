# -*- coding: utf-8 -*-
from django.contrib import admin
from powerdns.models import Domain, Record

class RecordAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'content',)
    list_filter = ['type', 'change_date',]
    search_fields  = ('name','content',)

class DomainAdmin(admin.ModelAdmin):
    list_display = ('name', 'type',)
    list_filter = ['type', 'last_check',]
    search_fields  = ('name','type',)

admin.site.register(Domain,DomainAdmin)
admin.site.register(Record,RecordAdmin)
