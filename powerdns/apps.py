from django.apps import AppConfig
from django.conf import settings
from django.contrib.auth import get_user_model


class Powerdns(AppConfig):

    name = 'powerdns'
    verbose_name = 'PowerDNS'

    def ready(self):
        import autocomplete_light.shortcuts as al
        from powerdns.models import Domain, Record

        class AutocompleteAuthItems(al.AutocompleteGenericBase):
            choices = (
                Domain.objects.all(),
                Record.objects.all(),
            )
            search_fields = (
                ('name',),
                ('name',)
            )

        al.register(AutocompleteAuthItems)
        # This requires the user model to have username, first_name, and
        # last_name fields
        search_fields = getattr(settings, 'POWERDNS_USER_SEARCH_FIELDS',
                                ['username', 'first_name', 'last_name'])
        al.register(
            get_user_model(),
            search_fields=search_fields
        )
        al.register(Domain, search_fields=['name'])
        al.register(Record, search_fields=['name', 'content'])
