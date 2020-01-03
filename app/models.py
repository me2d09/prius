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
from datetime import datetime, timedelta
from django.utils import formats
from django.dispatch import receiver
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from PyPDF2 import PdfFileReader
from django.core.exceptions import PermissionDenied

from pinax.notifications.models import send as notify_send
 



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
    remark = models.TextField(max_length=5000, default = '', blank=True)
    hiddenremark = models.TextField(max_length=5000, default = '', blank=True)

    # Relationship Fields
    proposal = models.ForeignKey('app.Proposals', on_delete=models.PROTECT)
    user =  models.ForeignKey(User, null=True, blank=True, on_delete=models.PROTECT)

    def getActionFromStatus(status):
        if status == 'TT': return 'technical review'
        if status == 'P': return 'created'
        if status == 'PR': return 'returned by panel'
        if status == 'XR': return 'rejected by panel'
        if status == 'XD': return 'rejected by director'
        if status == 'PU': return 'returned by user office'
    
        return {
            'P': 'preparation',
            'S': 'submitted',
            'U': 'useroffice takeover',
            'T': 'checked by useroffice',
            'W': 'technical review',
            'R': 'start review',
            'D': 'panel acceptance',
            'A': 'director approval',
            'F': 'finished',
            'X': 'rejected',
        }[status[0]]

    def prev_by_proposal(self):
        qs = Status.objects.filter(proposal=self.proposal).filter(date__lt=self.date)
        if len(qs) > 0:
            return qs[0].status
        else:
            return ''


    class Meta:
        ordering = ('-date',)
        permissions = (
            ("see_hidden_remarks", "Can see hidden remarks of whole status history"),
        )

    def save(self, *args, **kwargs):
        if not self.pk:
            prop = self.proposal
            prop.last_status = self.status
            prop.save()
        else:
            raise PermissionDenied
        super(Status, self).save(*args, **kwargs)


def validate_pdf_lenth(value):
    try:
        pdf = PdfFileReader(value.file)
    except:
        raise ValidationError(u'Error parsing PDF file - please check if the uploaded file is really PDF file format.')
        
    if pdf.getNumPages() > 2:
        raise ValidationError(u'Uploaded file has too many pages. Maximum allowed is 2.')

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
    scientific_bg = FileField(upload_to="userpdf", blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=['pdf']),validate_pdf_lenth])
    proposaltype = CharField(max_length=1, choices = PROPOSAL_TYPE, default = 'S')
    last_status = CharField(max_length=1, choices = Status.STATUS_TYPES, default='P')
    student = BooleanField(default = False)
    thesis_topic = CharField(max_length=1000, blank=True, null=True)
    grants = CharField(max_length=1000, blank=True, null=True)

    # Relationship Fields
    proposer =  models.ForeignKey(User, null=True, blank=True, on_delete=models.PROTECT)
    samples = models.ManyToManyField('app.Samples', blank=True)
    local_contacts = models.ManyToManyField('app.Contacts',  related_name='proposal_local_contacts', blank=True)
    reporter = models.ForeignKey('app.Contacts', related_name='proposal_reporter', on_delete=models.PROTECT, blank=True, null = True)
    supervisor = models.ForeignKey('app.Contacts', related_name='proposal_supervisor', on_delete=models.PROTECT, blank=True, null = True)
    coproposers = models.ManyToManyField('app.Contacts',  related_name='proposal_coporposals', blank=True)
    publications = models.ManyToManyField('app.Publications', blank=True)
    
    @property
    def local_contacts_short(self):
        if self.local_contacts.count() > 1:
            return "%s (+%d)" % (self.local_contacts.first().name, self.local_contacts.count() - 1)
        else:
            return self.local_contacts.first().name

    @property
    def people(self):
        coll = set(list(self.local_contacts.all()) + list(self.coproposers.all()) + [self.supervisor] + [self.proposer.contact])
        seen = set()
        ret = list()
        for item in coll:
            if item and not item.pk in seen:
                seen.add(item.pk)
                ret.append(item)
        return ret
    
    @property
    def users(self):
        return [x.uid for x in self.people if x.uid is not None]

    def save(self, *args, **kwargs):
        adding = self._state.adding
        if not self.pid or self.pid[0] != self.proposaltype:
            #search for first free proposal number
            start = self.proposaltype + chr((datetime.now().year - 2019) % 26  + 65)
            qs = Proposals.objects.filter(pid__startswith = start).values_list('pid')
            maxpid = 0
            for p in qs:
                maxpid = max(maxpid, int(p[0][2:]))
            self.pid = "%s%03d" % (start, maxpid + 1)
        old_prop = Proposals.objects.filter(pk=self.pk).first()
        super(Proposals, self).save(*args, **kwargs)
        #create a line in statuses table, if added
        if adding: 
            Status.objects.create(status="P", proposal=self, user=self.proposer)
        # send emails
        if old_prop and old_prop.last_status != self.last_status:
            s = old_prop.last_status + self.last_status
            if s in ["DA", "RP", "UP", "DX", "RX"]: #important change
                # send email to all coproposers
                coprop = [x.uid for x in self.coproposers.select_related("uid").all() if x.uid is not None]
                if self.supervisor and self.supervisor.uid:
                    coprop += [self.supervisor.uid]
                notify_send([self.proposer], 'X_proposal_important', extra_context = { 'proposal': self, 'action': s[1]})
                notify_send(coprop, 'x_proposal_important_team', extra_context = { 'proposal': self, 'action': s[1]})
            else:
                notify_send([x.uid for x in self.coproposers.select_related("uid").all() if x.uid is not None] + [self.proposer], 
                            'x_proposal_status_changed', extra_context = { 'proposal': self})

            if s == "DA" or s == "PA":
                notify_send([x.uid for x in self.local_contacts.select_related("uid").all() if x.uid is not None], 
                            'l_accepted', extra_context = { 'proposal': self})
                notify_send(User.objects.filter(groups__name='admins'), 
                            'a_accepted', extra_context = { 'proposal': self})
            elif s == "UT":
                notify_send([x.uid for x in self.local_contacts.select_related("uid").all() if x.uid is not None], 
                            'L_request_technical', extra_context = { 'proposal': self})
            elif s == "TW":
                notify_send(User.objects.filter(groups__name='panelhead'), 
                            'H_new_proposal', extra_context = { 'proposal': self})
            elif s == "WR":
                notify_send([self.reporter.uid], 
                            'P_request_review', extra_context = { 'proposal': self})
                pmembers = list(User.objects.filter(groups__name='panel'))
                pmembers.remove(self.reporter.uid)
                notify_send(pmembers, 
                            'p_request_comments', extra_context = { 'proposal': self})
            elif s == "RD" or s == "TD":
                notify_send(User.objects.filter(groups__name='director'), 
                            'D_accepted', extra_context = { 'proposal': self})
            elif s == "RX":
                notify_send(User.objects.filter(groups__name='director'), 
                            'd_rejected', extra_context = { 'proposal': self})
            elif s == "RP":
                notify_send(User.objects.filter(groups__name='director'), 
                            'd_returned', extra_context = { 'proposal': self})
            elif s == "PS":
                notify_send(User.objects.filter(groups__name='useroffice'), 
                            'U_submited', extra_context = { 'proposal': self})
                notify_send(User.objects.filter(groups__name='admins'), 
                            'a_submited', extra_context = { 'proposal': self})

            



    class Meta:
        ordering = ('-created',)
        permissions = (
            ("change_status", "Can set proposal to any status, edit proposal type anytime"),
            ("approve_technical", "Can submit technical comments"),
            ("takeover_panel", "Can assign a reviewer and submit any review"),
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
        return '%s %s' % (self.pid, self.name)



class Contacts(models.Model):
    # Fields
    name = CharField(max_length=500)
    created = DateTimeField(auto_now_add=True, editable=False)
    last_updated = DateTimeField(auto_now=True, editable=False)
    email = EmailField(unique=True)
    orcid = models.CharField(max_length=40,blank=True)
    description = CharField(max_length=500,blank=True)
    phone = CharField(max_length=20,blank=True)

    # Relationship Fields
    uid = models.OneToOneField(User, on_delete=models.CASCADE, blank=True,null=True, related_name='contact')
    affiliation = models.ForeignKey('app.Affiliations', on_delete=models.PROTECT)


    @property
    def nice_phone(self):
        if self.phone:
            if len(self.phone) == 3:
                return "<span title='(+420) 220 318 " + self.phone + "'>☎ " + self.phone + "</span>"
            elif len(self.phone) == 4:
                return "<span title='(+420) 951 55 " + self.phone + "'>☎ " + self.phone + "</span>"
            return "☎ " + self.phone
        return ""

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
    department = CharField(max_length=500, blank=True)
    institution = CharField(max_length=500)
    address1 = CharField(max_length=500, blank=True)
    address2 = CharField(max_length=500, blank=True)
    city = CharField(max_length=255, blank=True)

    # Relationship Fields
    country = models.ForeignKey('app.Countries', on_delete=models.PROTECT, blank=True,null=True )

    class Meta:
        ordering = ('-created',)

    def __unicode__(self):
        return u'%s' % self.pk

    def __str__(self):
        return ", ".join(list(filter(None, [self.department, self.institution, self.city, self.country.iso if self.country else None])))

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

    def __str__(self):
        return '%s (%s)' % (self.name, self.iso)

    def get_absolute_url(self):
        return reverse('app_countries_detail', args=(self.pk,))


    def get_update_url(self):
        return reverse('app_countries_update', args=(self.pk,))



class Instruments(models.Model):

    # Fields
    name = CharField(max_length=255)
    slug = extension_fields.AutoSlugField(populate_from='name', blank=True)
    created = DateTimeField(auto_now_add=True, editable=False)
    last_updated = DateTimeField(auto_now=True, editable=False)
    public = BooleanField(default=True)
    active = BooleanField(default=True)
    description = TextField()
    book_by_hour = BooleanField(default=False)
    start_hour = FloatField(blank=True, default=0.0)

    group = models.ForeignKey('app.InstrumentGroup', related_name='instruments', on_delete=models.PROTECT, default=None, null=True)

    class Meta:
        ordering = ('-created',)

    def __unicode__(self):
        return u'%s' % self.slug

    def __str__(self):
        return '%s' % self.name

    def get_absolute_url(self):
        return reverse('app_instruments_detail', args=(self.slug,))


    def get_update_url(self):
        return reverse('app_instruments_update', args=(self.slug,))


class InstrumentGroup(models.Model):

    name = CharField(max_length=255)
    created = DateTimeField(auto_now_add=True, editable=False)
    last_updated = DateTimeField(auto_now=True, editable=False)
    
    trained_users = models.ManyToManyField('app.Contacts',  related_name='trained_instrumentgroups', blank=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return '%s' % self.name


class Experiments(models.Model):

    # Fields
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    start = models.DateTimeField()
    end = models.DateTimeField()
    description = models.TextField(max_length=5000, default="")
    duration = models.DurationField(editable=False)

    # Relationship Fields
    proposal = models.ForeignKey('app.Proposals', on_delete=models.PROTECT, default=None)
    option = models.ManyToManyField('app.Options', blank=True)

    responsible = models.ForeignKey('app.Contacts', on_delete=models.PROTECT, related_name = "experiment_responsible", null=True)
    local_contact = models.ForeignKey('app.Contacts', on_delete=models.PROTECT, related_name = "experiment_lc")
    instrument = models.ForeignKey('app.Instruments', on_delete=models.PROTECT)
    creator = models.ForeignKey('app.Contacts',  related_name='experiment_creator', on_delete=models.PROTECT)

    @property
    def real_start(self):
        if self.instrument and not self.instrument.book_by_hour:
            return self.start + timedelta(hours = self.instrument.start_hour)
        else:
            return self.start

    @property
    def real_end(self):
        if self.instrument and not self.instrument.book_by_hour:
            return self.end + timedelta(days = 1, hours = self.instrument.start_hour)
        else:
            return self.end
    
    @property
    def all_options(self):
        return ', '.join([x.name for x in self.option.all()] + [x.shared_option.name for x in self.sharedoptionslot_set.all()])

    class Meta:
        ordering = ('-created',)

    def __unicode__(self):
        return u'%s' % self.pk

    def __str__(self):
        return "%s (%s - %s)" % (self.instrument.name, formats.date_format(self.real_start, "SHORT_DATETIME_FORMAT"), formats.date_format(self.real_end, "SHORT_DATETIME_FORMAT"))


    def get_absolute_url(self):
        return reverse('app_experiments_detail', args=(self.pk,))

    def get_update_url(self):
        return reverse('app_experiments_update', args=(self.pk,))

    def get_delete_url(self):
        return reverse('app_experiments_delete', args=(self.pk,))

    def save(self, *args, **kwargs):
        # calculate duration
        self.duration = self.end - self.start
        if not self.instrument.book_by_hour:
            self.duration += timedelta(days=1)

        old_slot = Experiments.objects.filter(pk=self.pk).first()
        super(Experiments, self).save(*args, **kwargs)

        #send notifications
        if not old_slot:  # new booking
            notify_send(self.proposal.users, 'x_booking_new', extra_context = { 'exp': self, 'proposal': self.proposal })
            notify_send([self.local_contact.uid], 'l_booking_lc', extra_context = { 'exp': self, 'proposal': self.proposal })
        else:
            reason = ""
            if old_slot.local_contact.pk != self.local_contact.pk:
                notify_send([self.local_contact.uid], 'l_booking_lc', extra_context = { 'exp': self, 'proposal': self.proposal })
                reason += f"Local contact changed: {old_slot.local_contact} --> {self.local_contact}"
                notify_send([old_slot.local_contact.uid], 'l_booking_lc_changed', extra_context = { 'exp': self, 'reason': reason, 'proposal': self.proposal })
            if self.start != old_slot.start or self.end != old_slot.end:
                reason += (f"Dates changed: {formats.date_format(old_slot.real_start, 'SHORT_DATETIME_FORMAT')}-{formats.date_format(old_slot.real_end, 'SHORT_DATETIME_FORMAT')}"  
                           f" --> {formats.date_format(self.real_start, 'SHORT_DATETIME_FORMAT')}-{formats.date_format(self.real_end, 'SHORT_DATETIME_FORMAT')}")
            if self.description != old_slot.description:
                reason += f"Description changed, new: {self.description}"
            if self.all_options != old_slot.all_options:
                reason += f"Options changed, new: {self.all_options}"
            if reason:
                notify_send([self.responsible.uid], 'X_booking_changed', extra_context = { 'exp': self, 'reason': reason, 'proposal': self.proposal })
                if old_slot.local_contact == self.local_contact:
                    notify_send([self.local_contact.uid], 'l_booking_lc_changed', extra_context = { 'exp': self, 'reason': reason, 'proposal': self.proposal })







class Options(models.Model):

    # Fields
    name = CharField(max_length=255)
    slug = AutoSlugField(populate_from='name', blank=True)
    created = DateTimeField(auto_now_add=True, editable=False)
    last_updated = DateTimeField(auto_now=True, editable=False)
    active = BooleanField(default=True)

    # Relationship Fields
    instrument = models.ForeignKey('app.Instruments', on_delete=models.PROTECT)

    class Meta:
        ordering = ('-created',)

    def __unicode__(self):
        return u'%s' % self.slug

    def __str__(self):
        return self.name

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

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('app_sharedoptions_detail', args=(self.slug,))


    def get_update_url(self):
        return reverse('app_sharedoptions_update', args=(self.slug,))



class SharedOptionSlot(models.Model):

    # Fields
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    start = models.DateTimeField()
    end = models.DateTimeField()
    duration = models.DurationField(editable=False)

    # Relationship Fields
    experiment = models.ForeignKey('app.Experiments', on_delete=models.CASCADE, default=None)
    shared_option = models.ForeignKey('app.SharedOptions', on_delete=models.PROTECT, default=None)

    @property
    def instrument(self):
        return self.experiment.instrument

    @property
    def proposal(self):
        return self.experiment.proposal
    
    @property
    def local_contact(self):
        return self.experiment.local_contact

    @property
    def responsible(self):
        return self.experiment.responsible

    @property
    def real_start(self):
        if self.instrument and not self.instrument.book_by_hour:
            return self.start + timedelta(hours = self.instrument.start_hour)
        else:
            return self.start

    @property
    def real_end(self):
        if self.instrument and not self.instrument.book_by_hour:
            return self.end + timedelta(days = 1, hours = self.instrument.start_hour)
        else:
            return self.end



    class Meta:
        ordering = ('-created',)

    def __unicode__(self):
        return u'%s' % self.pk

    def __str__(self):
        return "%s (%s - %s)" % (self.shared_option.name, formats.date_format(self.real_start, "SHORT_DATETIME_FORMAT"), formats.date_format(self.real_end, "SHORT_DATETIME_FORMAT"))

    def get_absolute_url(self):
        return reverse('app_sharedoptionslot_detail', args=(self.pk,))

    def get_update_url(self):
        return reverse('app_sharedoptionslot_update', args=(self.pk,))

    def save(self, *args, **kwargs):
        # calculate duration
        self.duration = self.end - self.start
        if not self.instrument.book_by_hour:
            self.duration += timedelta(days=1)
        super().save(*args, **kwargs)




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

