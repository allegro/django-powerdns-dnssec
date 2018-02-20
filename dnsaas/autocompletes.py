from django.contrib.auth import get_user_model

from dal import autocomplete


class UserAutocomplete(autocomplete.Select2QuerySetView):
    queryset = get_user_model().objects.all()
    model_field_name = 'username'

    def get_queryset(self):
        qs = self.queryset
        if self.q:
            qs = qs.filter(username__icontains=self.q)
        return qs
