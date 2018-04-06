from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.forms import modelformset_factory, inlineformset_factory, BaseModelFormSet, BaseInlineFormSet
from django.utils import timezone
from django.db.models.query import EmptyQuerySet
from django.utils.http import is_safe_url
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

from .models import Choice, Trip_Event, ChoiceVote, Participant, Destination, Owner, SubDestination
from .forms import NameForm, Trip_EventForm, ParticipantForm, DestinationForm, SignUpForm

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.groups.add(Group.objects.get(name='OPERATOR'))
            user.owner.birth_date = form.cleaned_data.get('birth_date')
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return HttpResponseRedirect(reverse('trips:index'))
    else:
        form = SignUpForm()
    return render(request, 'trips/signup.html', {'form': form})

def index(request):
    destination_list = Destination.objects.all()
    latest_trip_event_list = Trip_Event.objects.order_by('-pub_date')[:5]
    context = {'latest_trip_event_list': latest_trip_event_list, 'destination_list': destination_list}
    return render(request, 'trips/index.html', context)

def detail(request, trip_event_id):
    trip_event = get_object_or_404(Trip_Event, pk=trip_event_id)
    trip_event.views += 1
    trip_event.save()
    return render(request, 'trips/detail.html', {'trip_event': trip_event})

#def dest(request, trip_event_id, trip_event_destination):
#    trip_event = get_object_or_404(Trip_Event, pk=trip_event_id)
#    dest_event = trip_event_destination
#    return render(request, 'trips/dest.html', {'trip_event': trip_event}, {'dest_event': dest_event})

def dest(request,  trip_event_destination):
    dest_event = trip_event_destination
    dest_event_obj = Destination.objects.get(destination=trip_event_destination)
    dest_event_obj.views += 1
    dest_event_obj.save()
    return render(request, 'trips/dest.html', {'dest_event': dest_event, 'dest_event_obj': dest_event_obj})

def dest_sub(request,  trip_event_subdestination):
    sub_dest_event = trip_event_subdestination
    sub_dest_event_obj = SubDestination.objects.get(subdestination=trip_event_subdestination)
    return render(request, 'trips/dest_sub.html', {'sub_dest_event': sub_dest_event, 'sub_dest_event_obj': sub_dest_event_obj})

def results(request, trip_event_id):
    trip_event = get_object_or_404(Trip_Event, pk=trip_event_id)
    return render(request, 'trips/results.html', {'trip_event': trip_event})

def results_vote(request, trip_event_id):
    trip_event = get_object_or_404(Trip_Event, pk=trip_event_id)
    return render(request, 'trips/results_vote.html', {'trip_event': trip_event})

def vote(request, trip_event_id):
    trip_event = get_object_or_404(Trip_Event, pk=trip_event_id)
    #return render(request, 'trips/vote.html', {'trip_event': trip_event})
    try:
        selected_choice = trip_event.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'trips/detail.html', {
            'question': trip_event,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('trips:results', args=(trip_event.id,)))


def votetrip(request, trip_event_id):
    trip_event = get_object_or_404(Trip_Event, pk=trip_event_id)
    trip_event_choicevote = trip_event.choicevote
    que = int(request.POST['choicevote'])
    que_name = trip_event_choicevote._meta.fields[que]
    #return render(request, 'trips/vote.html', {'trip_event': trip_event})
    try:
        selected_choice = getattr(trip_event_choicevote,que_name.name)
    except (KeyError, ChoiceVote.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'trips/detail.html', {
            'question': trip_event,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice += 1
        setattr(trip_event_choicevote,que_name.name,selected_choice)
        trip_event_choicevote.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('trips:results_vote', args=(trip_event.id,)))


def get_name(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = NameForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            name_display = form.cleaned_data['your_name']
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect(reverse('trips:your_name', args=(name_display,)))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = NameForm()

    return render(request, 'trips/name.html', {'form': form})

def your_name(request,name_display):
    name_display = name_display
    return render(request, 'trips/your_name.html', {'name_display': name_display})

def edit_trip_event(request):
    TripEventFormSet = modelformset_factory(Trip_Event, fields=('trips_tittle', 'trip_destination', 'start_date', 'end_date', 'pub_date', 'views'))
    if request.method == 'POST':
        formset = TripEventFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            # do something.
            return HttpResponseRedirect(reverse('trips:edit_trip_event'))
    else:
        formset = TripEventFormSet()
    return render(request, 'trips/edit_trip_event.html', {'formset': formset})

@login_required(login_url='/trips/login/')
def add_trip_event(request):
    #form = Trip_EventForm()
    #return render(request, 'trips/add_trip_event.html', {'form': form})

    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

    if request.method == "POST":
        form = Trip_EventForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.trip_owner = Owner.objects.get(owner=request.user)
            post.pub_date = timezone.now()
            post.view = 0
            post.save()
            form.save_m2m()

            return HttpResponseRedirect(reverse('trips:index'))
    else:
        form = Trip_EventForm()
    return render(request, 'trips/add_trip_event.html', {'form': form})

class BaseInlineAddOnlyFormSet(BaseInlineFormSet):
    def get_queryset(self):
        return EmptyQuerySet()

def add_participant(request, trip_event_id):
    #trip_event = get_object_or_404(Trip_Event, pk=trip_event_id)
    trip_event = Trip_Event.objects.get(pk=trip_event_id)
    queryset = Participant.objects.none()
    ParticipantFormSet = inlineformset_factory(Trip_Event, Participant, fields=('full_name','email','gender'),extra=1)
    #form = Trip_EventForm()
    #return render(request, 'trips/add_trip_event.html', {'form': form})

    if request.method == "POST":
        formset = ParticipantFormSet(request.POST, request.FILES, instance=trip_event)
        if formset.is_valid():
            for form in formset:
                post = form.save(commit=False)
                post.reg_date = timezone.now()
                post.save()
            formset.save()

            return HttpResponseRedirect(reverse('trips:add_participant', args=(trip_event.id,)))
    else:
        formset = ParticipantFormSet(instance=trip_event, queryset=queryset)
    #return render(request, 'trips/add_participant.html', {'form': form})
    return render(request, 'trips/add_participant.html', {'formset': formset, 'trip_event': trip_event})
    #return HttpResponseRedirect(reverse('trips:results_vote', {'form': form}, args=(trip_event.id,)))

def edit_participant(request, trip_event_id):
    #trip_event = get_object_or_404(Trip_Event, pk=trip_event_id)
    trip_event = Trip_Event.objects.get(pk=trip_event_id)
    #queryset = Participant.objects.none()
    ParticipantFormSet = inlineformset_factory(Trip_Event, Participant, fields=('full_name','email','gender'),extra=1)
    #form = Trip_EventForm()
    #return render(request, 'trips/add_trip_event.html', {'form': form})

    if request.method == "POST":
        formset = ParticipantFormSet(request.POST, request.FILES, instance=trip_event)
        if formset.is_valid():
            for form in formset:
                post = form.save(commit=False)
                post.reg_date = timezone.now()
                post.save()
            formset.save()

            return HttpResponseRedirect(reverse('trips:edit_participant', args=(trip_event.id,)))
    else:
        formset = ParticipantFormSet(instance=trip_event)
    #return render(request, 'trips/add_participant.html', {'form': form})
    return render(request, 'trips/edit_participant.html', {'formset': formset, 'trip_event': trip_event})
    #return HttpResponseRedirect(reverse('trips:results_vote', {'form': form}, args=(trip_event.id,)))


def add_destination(request):
    #form = Trip_EventForm()
    #return render(request, 'trips/add_trip_event.html', {'form': form})

    if request.method == "POST":
        form = DestinationForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.reg_date = timezone.now()
            post.view = 0
            post.save()
            #form.save_m2m()

            next = request.POST.get('next', '/')
            return HttpResponseRedirect(next)
            #return HttpResponseRedirect(reverse('trips:index'))
    else:
        form = DestinationForm()
    return render(request, 'trips/add_destination.html', {'form': form})

