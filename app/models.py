from django.urls import reverse
from django_extensions.db.fields import AutoSlugField
from django.db.models import *
from django.db.models.signals import post_save
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.contrib.auth import models as auth_models
from django.contrib.auth.models import User
from django.db import models as models
from django_extensions.db import fields as extension_fields
from django.contrib.auth.models import User
from datetime import datetime
from django.dispatch import receiver


class Status(models.Model):
    STATUS_TYPES = (
        ('P', 'in preparation'),  # user can edit proposal
        ('S', 'submitted'),       # action by user - locked and waiting for action by UO
        ('U', 'user office checking'),  # accepted by UO, checking all documents, lenght, fast process  
        ('T', 'in technical review'),  # 
        ('W', 'waiting for panel'),
        ('R', 'in panel review'),
        ('D', 'by director'),
        ('A', 'accepted'), # 
        ('F', 'finished'), # done by user, lc, or uo - cannot plan new measurement anymore
        ('X', 'rejected'), # cannot plan measurement
        )
    #Fields
    date = DateTimeField(auto_now_add=True, editable=False)
    status = CharField(max_length=1, choices = STATUS_TYPES)
    remarks = models.TextField(max_length=5000)

    # Relationship Fields
    proposal = models.ForeignKey('app.Proposals', on_delete=models.PROTECT)
    user = models.ForeignKey('app.Contacts', on_delete=models.PROTECT)

    class Meta:
        ordering = ('-date',)


class Proposals(models.Model):

    PROPOSAL_TYPE = (
        ('S', 'standard'),
        ('L', 'long-term'),
        ('P', 'proof of concept'),
        ('T', 'test'),
        )
    # Fields
    slug = extension_fields.AutoSlugField(populate_from='name', blank=True, null=True)
    pid = CharField(max_length = 8, editable = False, default = None, null=True)
    created = DateTimeField(auto_now_add=True, editable=False)
    last_updated = DateTimeField(auto_now=True, editable=False)
    name = CharField(max_length=500)
    abstract = models.TextField(max_length=5000)
    scientific_bg = FileField(upload_to=".", blank=True, null=True)
    proposaltype = CharField(max_length=1, choices = PROPOSAL_TYPE, default = 'S')
    last_status = CharField(max_length=1, choices = Status.STATUS_TYPES, default='P')

    # Relationship Fields
    proposer =  models.ForeignKey(User, null=True, blank=True, on_delete=models.PROTECT)
    samples = models.ManyToManyField('app.Samples', blank=True)
    local_contact = models.ForeignKey('app.Contacts', related_name='proposal_local_contact', on_delete=models.PROTECT)
    coproposers = models.ManyToManyField('app.Contacts',  related_name='proposal_coporposals', blank=True)
    publications = models.ManyToManyField('app.Publications', blank=True)

    def save(self, *args, **kwargs):
        if not self.pid:
            #search for first free proposal number
            start = self.proposaltype + chr((datetime.now().year - 2019) % 26  + 65)
            qs = Proposals.objects.filter(pid__startswith = start).values_list('pid')
            maxpid = 0
            for p in qs:
                maxpid = max(maxpid, int(p[0][2:]))
            self.pid = "%s%03d" % (start, maxpid + 1)
        super(Proposals, self).save(*args, **kwargs)

    class Meta:
        ordering = ('-created',)
        permissions = (
            ("change_status", "Can set proposal to any status"),
            ("approve_technical", "Can submit technical comments"),
            ("takeover_panel", "Can put proposal to review"),
            ("approve_panel", "Can submit panel decision"),
            ("approve_director", "Can submit director approval"),
            ("finish_proposal", "Can finish approved proposal"),
        )

    def __unicode__(self):
        return u'%s' % self.slug

    def get_absolute_url(self):
        return reverse('app_proposals_detail', args=(self.slug,))


    def get_update_url(self):
        return reverse('app_proposals_update', args=(self.slug,))

    def __str__(self):
        return self.name


class Instruments(models.Model):

    # Fields
    name = CharField(max_length=255)
    slug = extension_fields.AutoSlugField(populate_from='name', blank=True)
    created = DateTimeField(auto_now_add=True, editable=False)
    last_updated = DateTimeField(auto_now=True, editable=False)
    public = BooleanField()
    active = BooleanField(default=True)
    description = TextField()
    time_to_schedule = models.DurationField()

    # Relationship Fields
    local_contacts = models.ForeignKey('app.Contacts', on_delete=models.PROTECT)
    admins = models.ForeignKey('app.Contacts', related_name='instrument_admins', on_delete=models.PROTECT)
    parameter_set = models.ForeignKey('app.InstrumentParameterSets', on_delete=models.PROTECT)

    class Meta:
        ordering = ('-created',)

    def __unicode__(self):
        return u'%s' % self.slug

    def get_absolute_url(self):
        return reverse('app_instruments_detail', args=(self.slug,))


    def get_update_url(self):
        return reverse('app_instruments_update', args=(self.slug,))





class Contacts(models.Model):
    # Fields
    name = CharField(max_length=500)
    created = DateTimeField(auto_now_add=True, editable=False)
    last_updated = DateTimeField(auto_now=True, editable=False)
    email = EmailField(unique=True)
    orcid = models.CharField(max_length=40,blank=True)

    # Relationship Fields
    uid = models.ForeignKey(User, on_delete=models.PROTECT, blank=True,null=True)
    affiliation = models.ForeignKey('app.Affiliations', on_delete=models.PROTECT)

    class Meta:
        ordering = ('-created',)

    def __unicode__(self):
        return u'%s' % self.name

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('app_contacts_detail', args=(self.pk,))


    def get_update_url(self):
        return reverse('app_contacts_update', args=(self.pk,))

    
@receiver(post_save, sender=User)
def update_email_in_contacts(sender, instance, created, **kwargs):
    try:
        if created:
            #try to connect with contacts
            contact = Contacts.objects.get(email=instance.email)
            contact.uid = instance
            contact.save()
        else:
            contact = Contacts.objects.get(uid=instance)
            if contact.email != instance.email:
                contact.email = instance.email
                contact.save()
    except ObjectDoesNotExist as e:
        pass
    



@receiver(post_save, sender=Contacts)
def update_email_in_user(sender, **kwargs):
    user = kwargs.get('instance').uid
    if user and user.email != kwargs.get('instance').email:
        user.email = kwargs.get('instance').email
        user.save()


class Affiliations(models.Model):

    # Fields
    created = DateTimeField(auto_now_add=True, editable=False)
    last_updated = DateTimeField(auto_now=True, editable=False)
    department = CharField(max_length=500)
    institution = CharField(max_length=500)
    address1 = CharField(max_length=500)
    address2 = CharField(max_length=500)
    city = CharField(max_length=255)

    # Relationship Fields
    country = models.ForeignKey('app.Countries', on_delete=models.PROTECT, blank=True,null=True )

    class Meta:
        ordering = ('-created',)

    def __unicode__(self):
        return u'%s' % self.pk

    def __str__(self):
        return ", ".join(list(filter(None, [self.department, self.institution, self.city])))

    def get_absolute_url(self):
        return reverse('app_affiliations_detail', args=(self.pk,))


    def get_update_url(self):
        return reverse('app_affiliations_update', args=(self.pk,))


class Countries(models.Model):

    # Fields
    name = CharField(max_length=255)
    iso = CharField(max_length=2, primary_key=True)


    class Meta:
        ordering = ('-pk',)

    def __unicode__(self):
        return u'%s' % self.pk

    def get_absolute_url(self):
        return reverse('app_countries_detail', args=(self.pk,))


    def get_update_url(self):
        return reverse('app_countries_update', args=(self.pk,))


class InstrumentRequest(models.Model):

    # Fields
    requested = models.DurationField(null=False)
    granted = models.DurationField()

    # Relationship Fields
    instrument = models.ForeignKey('app.Instruments', on_delete=models.PROTECT)
    propsal = models.ForeignKey('app.Proposals', on_delete=models.PROTECT)
    option = models.ForeignKey('app.Options', on_delete=models.PROTECT)
    shared_options = models.ManyToManyField('app.SharedOptions', )

    class Meta:
        ordering = ('-pk',)

    def __unicode__(self):
        return u'%s' % self.pk

    def get_absolute_url(self):
        return reverse('app_instrumentrequest_detail', args=(self.pk,))


    def get_update_url(self):
        return reverse('app_instrumentrequest_update', args=(self.pk,))


class Options(models.Model):

    # Fields
    name = CharField(max_length=255)
    slug = AutoSlugField(populate_from='name', blank=True)
    created = DateTimeField(auto_now_add=True, editable=False)
    last_updated = DateTimeField(auto_now=True, editable=False)
    active = BooleanField()

    # Relationship Fields
    instrument = models.ForeignKey('app.Instruments', on_delete=models.PROTECT)

    class Meta:
        ordering = ('-created',)

    def __unicode__(self):
        return u'%s' % self.slug

    def get_absolute_url(self):
        return reverse('app_options_detail', args=(self.slug,))


    def get_update_url(self):
        return reverse('app_options_update', args=(self.slug,))


class SharedOptions(models.Model):

    # Fields
    name = CharField(max_length=255)
    slug = AutoSlugField(populate_from='name', blank=True)
    created = DateTimeField(auto_now_add=True, editable=False)
    last_updated = DateTimeField(auto_now=True, editable=False)
    active = BooleanField()

    # Relationship Fields
    instruments = models.ManyToManyField('app.Instruments', )

    class Meta:
        ordering = ('-created',)

    def __unicode__(self):
        return u'%s' % self.slug

    def get_absolute_url(self):
        return reverse('app_sharedoptions_detail', args=(self.slug,))


    def get_update_url(self):
        return reverse('app_sharedoptions_update', args=(self.slug,))


class InstrumentParameterSets(models.Model):

    # Fields
    name = CharField(max_length=255)


    class Meta:
        ordering = ('-pk',)

    def __unicode__(self):
        return u'%s' % self.pk

    def get_absolute_url(self):
        return reverse('app_instrumentparametersets_detail', args=(self.pk,))


    def get_update_url(self):
        return reverse('app_instrumentparametersets_update', args=(self.pk,))


class InstrumentParameters(models.Model):

    # Fields
    name = CharField(max_length=255)
    description = TextField(max_length=1000)
    required = BooleanField()

    # Relationship Fields
    set = models.ForeignKey('app.InstrumentParameterSets', on_delete=models.PROTECT)

    class Meta:
        ordering = ('-pk',)

    def __unicode__(self):
        return u'%s' % self.pk

    def get_absolute_url(self):
        return reverse('app_instrumentparameters_detail', args=(self.pk,))


    def get_update_url(self):
        return reverse('app_instrumentparameters_update', args=(self.pk,))


class ParameterValues(models.Model):

    # Fields
    value = models.CharField(max_length=255)

    # Relationship Fields
    parameter = models.ForeignKey('app.InstrumentParameters', on_delete=models.PROTECT)
    request = models.ForeignKey('app.InstrumentRequest', on_delete=models.PROTECT)

    class Meta:
        ordering = ('-pk',)

    def __unicode__(self):
        return u'%s' % self.pk

    def get_absolute_url(self):
        return reverse('app_parametervalues_detail', args=(self.pk,))


    def get_update_url(self):
        return reverse('app_parametervalues_update', args=(self.pk,))


class Samples(models.Model):

    # Fields
    name = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    formula = models.CharField(max_length=255)
    mass = models.DecimalField(max_digits=10, decimal_places=3)
    volume = models.DecimalField(max_digits=10, decimal_places=3)
    description = models.TextField(max_length=1000)
    type = models.CharField(max_length=1, choices=(('S', 'Single crystal'), ('M', 'Polycrystal'), ('P', 'Powder'), ('L', 'Liquid'), ('A', 'Amorphous'),))

    # Relationship Fields
    owner = models.ForeignKey('app.Contacts', on_delete=models.PROTECT)

    class Meta:
        ordering = ('-created',)

    def __unicode__(self):
        return u'%s' % self.pk

    def get_absolute_url(self):
        return reverse('app_samples_detail', args=(self.pk,))


    def get_update_url(self):
        return reverse('app_samples_update', args=(self.pk,))


class SamplePhotos(models.Model):

    # Fields
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    url = models.ImageField(upload_to="upload/images/samples/")

    # Relationship Fields
    sample = models.ForeignKey('app.Samples', on_delete=models.PROTECT)

    class Meta:
        ordering = ('-created',)

    def __unicode__(self):
        return u'%s' % self.pk

    def get_absolute_url(self):
        return reverse('app_samplephotos_detail', args=(self.pk,))


    def get_update_url(self):
        return reverse('app_samplephotos_update', args=(self.pk,))


class SampleRemarks(models.Model):

    # Fields
    remark = models.TextField(max_length=1000)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)

    # Relationship Fields
    sample = models.ForeignKey('app.Samples', on_delete=models.PROTECT)
    creator = models.ForeignKey('app.Contacts', on_delete=models.PROTECT)

    class Meta:
        ordering = ('-created',)

    def __unicode__(self):
        return u'%s' % self.pk

    def get_absolute_url(self):
        return reverse('app_sampleremarks_detail', args=(self.pk,))


    def get_update_url(self):
        return reverse('app_sampleremarks_update', args=(self.pk,))


class Publications(models.Model):

    # Fields
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    link = models.CharField(max_length=255)
    year = models.PositiveSmallIntegerField(db_index=True)

    # Relationship Fields
    authors = models.ManyToManyField('app.Contacts', )

    class Meta:
        ordering = ('-created',)

    def __unicode__(self):
        return u'%s' % self.pk

    def get_absolute_url(self):
        return reverse('app_publications_detail', args=(self.pk,))


    def get_update_url(self):
        return reverse('app_publications_update', args=(self.pk,))


class Experiments(models.Model):

    # Fields
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    start = models.DateTimeField()
    end = models.DateTimeField()
    duration = models.DurationField()
    finalized = models.BooleanField()

    # Relationship Fields
    request = models.ForeignKey('app.InstrumentRequest', on_delete=models.PROTECT)
    local_contact = models.ForeignKey('app.Contacts', on_delete=models.PROTECT)
    instrument = models.ForeignKey('app.Instruments', on_delete=models.PROTECT)
    creator = models.ForeignKey('app.Contacts',  related_name='experiment_creator', on_delete=models.PROTECT)

    class Meta:
        ordering = ('-created',)

    def __unicode__(self):
        return u'%s' % self.pk

    def get_absolute_url(self):
        return reverse('app_experiments_detail', args=(self.pk,))


    def get_update_url(self):
        return reverse('app_experiments_update', args=(self.pk,))


class Slots(models.Model):

    # Fields
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    start = models.DateTimeField()
    end = models.DateTimeField()
    type = models.CharField(max_length=1, choices=(('M', 'Maintenance'), ('O', 'Instrument off'), ('F', 'Failure'), ('R', 'Repair'),))

    # Relationship Fields
    instrument = models.ForeignKey('app.Instruments', on_delete=models.PROTECT)
    creator = models.ForeignKey('app.Contacts', on_delete=models.PROTECT)

    class Meta:
        ordering = ('-created',)

    def __unicode__(self):
        return u'%s' % self.pk

    def get_absolute_url(self):
        return reverse('app_slots_detail', args=(self.pk,))


    def get_update_url(self):
        return reverse('app_slots_update', args=(self.pk,))


