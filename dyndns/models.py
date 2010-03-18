from django.db import models

class Record(models.Model):
	domain_id = models.IntegerField()
	name = models.CharField(max_length=30)
	type=models.CharField(max_length=6)
	content=models.CharField(max_length=30)
	ttl=models.IntegerField()
	prio=models.IntegerField()
	change_date= models.IntegerField()
	def __unicode__(self):
        	return self.content
	def __unicode__(self):
        	return self.name
	class Meta:
		db_table = 'records'


