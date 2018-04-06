from django.contrib import admin

from .models import Trip_Event, Choice, ChoiceVote, Participant, Destination, Owner, SubDestination

admin.site.register(Trip_Event)
admin.site.register(Choice)
admin.site.register(ChoiceVote)
admin.site.register(Participant)
admin.site.register(Destination)
admin.site.register(Owner)
admin.site.register(SubDestination)