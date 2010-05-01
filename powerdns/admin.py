# -*- coding: utf-8 -*-
from django.contrib import admin
from powerdns.models import Domain, Record, Supermaster

class RecordAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'content', 'ttl', 'prio', 'change_date',)
    list_filter = ['type', 'ttl',]
    search_fields  = ('name','content',)

class DomainAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'last_check', 'account',)
    list_filter = ['type', 'last_check', 'account',]
    search_fields  = ('name',)

class SupermasterAdmin(admin.ModelAdmin):
    list_display = ('ip', 'nameserver', 'account',)
    list_filter = ['ip', 'account',]
    search_fields  = ('ip', 'nameserver',)

admin.site.register(Domain,DomainAdmin)
admin.site.register(Record,RecordAdmin)
admin.site.register(Supermaster,SupermasterAdmin)
