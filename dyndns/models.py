from django.db import models

class Domain(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=255)
    master = models.CharField(max_length=128)
    last_check = models.IntegerField()
    type = models.CharField(max_length=6)
    notified_serial = models.IntegerField()
    account = models.CharField(max_length=40)
    def __unicode__(self):
        return self.name
    class Meta:
        db_table = u'domains'

class Record(models.Model):                                                                                                                                 
    id = models.IntegerField(primary_key=True)                                                                                                               
    domain = models.ForeignKey(Domains)                                                                                                                      
    name = models.CharField(max_length=255)                                                                                                                  
    type = models.CharField(max_length=6)
    content = models.CharField(max_length=255)
    ttl = models.IntegerField()
    prio = models.IntegerField()
    change_date = models.IntegerField()
    def __unicode__(self):
        return self.name
    class Meta:
        db_table = u'records'

class Supermaster(models.Model):
    ip = models.CharField(max_length=25)
    nameserver = models.CharField(max_length=255)
    account = models.CharField(max_length=40)
    class Meta:
        db_table = u'supermasters'

