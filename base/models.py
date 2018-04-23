# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
import random
import string

from django.db import models
from django.utils import timezone



class TempUser(models.Model):

    student = 's'
    teacher = 't'

    USER_TYPES = [
        (student, 'Student'),
        (teacher, 'Teacher')

        ]

    name = models.CharField(max_length=24, unique=True)
    user_type = models.CharField(max_length=4, choices=USER_TYPES)
    is_active = models.BooleanField(default=True)


    def __unicode__(self):
        return u'{} - {}'.format(self.user_type, self.name)


    def all_questions(self):
        questions = self.question_set.filter(is_active=True).order_by('-date')
        return questions

    @property
    def total_open_questions(self):
        total = self.all_questions().filter(status='open').count()
        return total

    def latest_questions(self):
        questions = self.all_questions()[:3]
        return questions


    @property
    def total_students(self):
        students = Answer.objects.filter(question__created_by__id=self.id,
                                        is_active=True).values_list('created_by__id').distinct()
        return students.count()


class BaseModel(models.Model):
    date = models.DateTimeField('date', default=timezone.now())
    created_by = models.ForeignKey(TempUser, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract=True



class Emotion(models.Model):
    
    hope = 'hope'
    interest = 'interest'
    surprise = 'surprise'
    sadness = 'sadness'
    fear = 'fear'
    shame = 'shame'
    guilt = 'guilt'
    envy = 'envy'
    disgust = 'disgust'
    contempt = 'contempt'
    anger = 'anger'
    pride = 'pride'
    elation = 'elation'
    joy = 'joy'
    satisfaction = 'satisfaction'
    relief = 'relief'
    

    EMOTION_CHOICES = [
        ('none', 'None'),
        ('other', 'Other'),
        (hope, 'Hope'),
        (interest, 'Interest'),
        (surprise, 'Surprise'),
        (sadness, 'Sadness'),
        (fear, 'Fear'),
        (shame, 'Shame'),
        (guilt, 'Guilt'),
        (envy, 'Envy'),
        (disgust, 'Disgust'),
        (contempt, 'Contempt'),
        (anger, 'Anger'),
        (pride, 'Pride'),
        (elation, 'Elation'),
        (joy, 'Joy'),
        (satisfaction, 'Satisfaction'),
        (relief, 'Relief'),

    ]

    EMOTION_COLORS = [
        (hope, '#b7f603'),
        (interest, '#51dc00'),
        (surprise, '#00ae00'),
        (sadness, '#01ebd2'),
        (fear, '#06e0e5'),
        (shame, '#0ca7f3'),
        (guilt, '#128aef'),
        (envy, '#1756ff'),
        (disgust, '#7131c8'),
        (contempt, '#aa338b'),
        (anger, '#c53969'),
        (pride, '#fb0000'),
        (elation, '#e04101'),
        (joy, '#f8881b'),
        (satisfaction, '#fafd00'),
        (relief, '#eafe0f'),

    ]



class Question(BaseModel):
    status_choices = [
        ('open', 'Open'),
        ('closed', 'Closed')
    ]

    tag = models.CharField(max_length=24, blank=True, null=True)
    name = models.CharField(max_length=128)
    allow_anonymous = models.BooleanField(default=False)
    code = models.CharField(max_length=12, blank=True, null=True, unique=True)
    status = models.CharField(max_length=18, choices=status_choices, default='open')
    ## add a language field?

    def __unicode__(self):
        return u'{0}'.format(self.name)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
        super(Question, self).save(*args, **kwargs)

    @property
    def response_count(self):
        total = self.answer_set.filter(is_active=True)
        return total.count()


class Answer(BaseModel):
    emotion = models.CharField(max_length=18, choices=Emotion.EMOTION_CHOICES)
    intensity = models.IntegerField()
    question = models.ForeignKey(Question)
    note = models.CharField(max_length=50, blank=True, null=True)


    def __unicode__(self):
        return u'{0} | {1}'.format(self.get_emotion_display(), self.intensity)





