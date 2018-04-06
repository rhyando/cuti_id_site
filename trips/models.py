from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import m2m_changed
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.utils import timezone
from annoying.fields import AutoOneToOneField
from django.db.models import signals
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from resizeimage import resizeimage


class Owner(models.Model):

    owner = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    reg_date = models.DateTimeField('date published',null=True, blank=True,)
    views = models.IntegerField(default=0)

    def __str__(self):
        return self.owner.username

@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    try:
        instance.owner.save()
    except AttributeError:
        owner = Owner.objects.create(owner=instance)
        owner.save()

    #if created:
    #    Owner.objects.create(owner=instance)
    #instance.Owner.save()

class Destination(models.Model):

    destination = models.CharField(max_length=200)
    description = models.TextField(max_length=1000, blank=True)
    reg_date = models.DateTimeField('date published')
    views = models.IntegerField(default=0)

    def __str__(self):
        return self.destination

def get_destination():
    return Destination.objects.get_or_create(id=1)

class SubDestination(models.Model):

    pardestination = models.ForeignKey(Destination, on_delete=models.CASCADE)
    subdestination = models.CharField(max_length=200)
    description = models.TextField(max_length=1000, blank=True)
    reg_date = models.DateTimeField('date published')
    views = models.IntegerField(default=0)

    def __str__(self):
        return self.subdestination

class Trip_Event(models.Model):

    DESTINATION = (
        ('KMO','KOMODO'),
        ('RJA','RAJAAMPAT'),
        ('DRW', 'DERAWAN')
    )

    trips_tittle = models.CharField(max_length=200)
    #destination = models.CharField(max_length=3, choices=DESTINATION)
    trip_destination = models.ManyToManyField(Destination, default="")
    start_date = models.DateTimeField('date start')
    end_date = models.DateTimeField('date end')
    pub_date = models.DateTimeField('date published')
    trip_owner = models.ForeignKey(Owner, on_delete=models.CASCADE, default="")
    file = models.FileField(upload_to="trip_media",null=True)
    views = models.IntegerField(default=0)

    def __str__(self):
        return self.trips_tittle

    def __iter__(self):
        for field_name in self._meta.get_all_field_names():
            value = getattr(self, field_name, None)
            yield (field_name, value)

    def save(self, *args, **kwargs):
        pil_image_obj = Image.open(self.file)
        w, h = pil_image_obj.size

        if max(w,h)>1024:
            new_image = resizeimage.resize_width(pil_image_obj, 1024)

            new_image_io = BytesIO()
            new_image.save(new_image_io, format='JPEG')

            temp_name = self.file.name
            self.file.delete(save=False)

            self.file.save(
                temp_name,
                content=ContentFile(new_image_io.getvalue()),
                save=False
            )

        super(Trip_Event, self).save(*args, **kwargs)

def trip_destination_changed(sender, **kwargs):
    if kwargs['instance'].trip_destination.count() > 2:
        raise ValidationError("You can't assign more than three regions")

#m2m_changed.connect(trip_destination_changed, sender=Trip_Event.trip_destination.through)

#class Trip_EventForm(ModelForm):
#    class Meta:
#        model = Trip_Event
#        fields = ['trips_tittle', 'destination', 'start_date', 'end_date', 'pub_date', 'owner', 'views']

class Choice(models.Model):
    trip = models.ForeignKey(Trip_Event, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text

    def __iter__(self):
        for field_name in self._meta.get_all_field_names():
            value = getattr(self, field_name, None)
            yield (field_name, value)

class ChoiceVote(models.Model):
    trip_vote = models.OneToOneField(Trip_Event, on_delete=models.CASCADE, primary_key=True)
    #trip_vote = models.ForeignKey(Trip_Event, on_delete=models.CASCADE)
    vote_recommended = models.IntegerField(default=0)
    vote_not_recommended = models.IntegerField(default=0)

    def __str__(self):
        return self.trip_vote.trips_tittle

def create_choicevote(sender, instance, created, **kwargs):
    """Create ModelB for every new ModelA."""
    if created:
        ChoiceVote.objects.create(trip_vote=instance)

signals.post_save.connect(create_choicevote, sender=Trip_Event, weak=False,
                          dispatch_uid='models.create_choicevote')

GENDER =  (
        ('M','Male'),
        ('F','Female')
    )

class Participant(models.Model):
    trip_participant = models.ForeignKey(Trip_Event, on_delete=models.CASCADE)
    #trip_vote = models.ForeignKey(Trip_Event, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    email = models.EmailField(max_length=70, unique=True)
    gender = models.CharField(max_length=1, choices=GENDER)
    reg_date = models.DateTimeField('date registered')

    def __str__(self):
        return self.trip_participant.trips_tittle + ' --- ' +self.full_name