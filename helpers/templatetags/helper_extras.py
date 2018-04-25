from django import template

from django.forms import CheckboxInput
from django.forms import ClearableFileInput
from django.forms import FileInput

from helpers.tools import get_object_or_None

from base.models import TempUser


register = template.Library()


@register.filter(name='addcss')
def addcss(field, css):
    original_classes = field.field.widget.attrs.get('class')
    original_classes = original_classes + ' ' if original_classes else ''

    disallow =[
        FileInput().__class__.__name__,
        CheckboxInput().__class__.__name__,
        ClearableFileInput().__class__.__name__
    ]

    if field.field.widget.__class__.__name__ in disallow:
        css = css.replace("form-control", "")
        return field.as_widget(attrs={"class": original_classes + css})
    return field.as_widget(attrs={"class": original_classes + css})

def is_teacher(user):
    res = False
    try:
        if user and user.user_type and user.user_type == 't':
            res = True
    except:
        res=False
    return res 

def is_student(user):
    res = False
    try:
        if user and user.user_type and user.user_type == 's':
            res = True
    except:
        res=False
    return res 


@register.filter(name='user_type')
def user_type(user, group):
    if user and group == 't':
        return is_teacher(user)
    elif user and group == 's':
        print user, type(user), 'studuser'
        return is_student(user)
    else:
        return False

@register.simple_tag
def relative_url(value, field_name, urlencode=None):
    url = '?{}={}'.format(field_name, value)
    if urlencode:
        querystring = urlencode.split('&')
        filtered_querystring = filter(lambda p: p.split('=')[0] != field_name, querystring)
        encoded_querystring = '&'.join(filtered_querystring)
        url = '{}&{}'.format(url, encoded_querystring)
    return url

