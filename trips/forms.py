from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Trip_Event, Participant, Owner, Destination
from functools import partial
from django.utils import timezone

DateInput = partial(forms.DateInput, {'class': 'datepicker'})

class DateInputx(forms.DateInput):
    input_type = 'date'

class SignUpForm(UserCreationForm):
    birth_date = forms.DateField(widget=DateInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'birth_date', 'password1', 'password2', )

class NameForm(forms.Form):
    your_name = forms.CharField(label='Your name', max_length=100)

class Trip_EventForm(forms.ModelForm):
    class Meta:
        model = Trip_Event
        fields = ('trips_tittle', 'trip_destination', 'start_date', 'end_date', 'file')
        exclude = ["trip_owner"]
        #fields = ('trips_tittle', 'start_date', 'end_date', 'owner', 'file')
        widgets = {
            'start_date': DateInputx(),
            'end_date': DateInputx()
        }

class ParticipantForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ('trip_participant', 'full_name', 'email', 'gender')

class OwnerForm(forms.ModelForm):
    class Meta:
        model = Owner
        fields = ('owner',)


class DestinationForm(forms.ModelForm):
    class Meta:
        model = Destination
        fields = ('destination',)