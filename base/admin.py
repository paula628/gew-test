# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Question, TempUser, Answer

admin.site.register(Question)
admin.site.register(TempUser)
admin.site.register(Answer)

