# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse
from django.core.exceptions import ValidationError

from helpers.tools import get_object_or_None
from helpers.tools import session_check, student_session_check

from .models import Emotion, Answer, TempUser, Question
from .forms import QuestionForm, AnswerForm, TempUserForm

from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.context_processors import csrf
from django.views.decorators.csrf import csrf_protect

from lti.contrib.django import DjangoToolProvider
from wheelproj.middleware.middleware_helper import SignatureValidator





def login(request):
    context = {}
    student = ''
    teacher = ''

    request.session['user'] = False
    request.session['student'] = False
    user = request.user
    user_type = user.user_type
    #context['create_user_form'] = TempUserForm()
    if request.method == 'POST':
        request_key = request.POST.get('oauth_consumer_key', None)
        timestamp = request.POST.get('oauth_timestamp', None)
        nonce = request.POST.get('oauth_nonce', None)

        tool_provider = DjangoToolProvider.from_django_request(request=request)
        validator = SignatureValidator(tool_provider)
        check_key = validator.check_client_key(request_key)
        if not check_key:
            logger.error("Invalid request: key check failed.")
            raise PermissionDenied
        check_req = validator.verify(request)
        if not check_req:
            logger.error("Invalid request: signature check failed.")
            raise PermissionDenied
        check_timestamp = validator.validate_timestamp_and_nonce(request_key, timestamp, nonce, request)
        if not check_timestamp:
            logger.error("Invalid request: timestamp check failed")

        code = request.POST.get('code', None)
        if user_type == 't':
            request.session['user'] = user.id
            request.session.set_expiry(1000)
            return redirect('base:dashboard')
        else:
            request.session['student'] = user.id
            request.session.set_expiry(600)
            return render(request, 'base/login_form.html', context)
    else:
        return render(request, 'base/login_form.html', context)

def login_student(request):
    context = {}
    code = request.POST.get('code')
    if request.method == 'POST':
        if code:
            questions = Question.objects.filter(code=code, status='open', is_active=True)
            if questions and questions.count() ==1:
                question = questions[0]
                context.update({'question':question})
                if not question.allow_anonymous:
                    student = request.POST.get('student', None)
                    if not student or student == '0':
                        msg= "You can't be anonymous in that session."
                        messages.error(request, msg)
                        context.update({'student':student})
                        return render(request, 'base/login_form.html', context)
                url = reverse('base:answer_page', args=[question.id])
                return redirect(url)
            else:
                msg = "Error! Either the session does not exist or it is already closed."
                messages.error(request, msg)
        return redirect('base:answer_page', question=question)
    else:
        return render(request, 'base/login_form.html', context)

def logout(request):
    #request.session['user'] = ''
    #request.session['student'] = ''
    return redirect('base:login')

@csrf_protect
def create_user(request):
    context = {}
    form = TempUserForm(request.POST)
    if form.is_valid():
        form.save()
        msg = 'A new user has been created.'
        messages.add_message(request, messages.INFO, msg)
    else:
        msg = 'There was an error creating your user. Choose another name.'
        messages.add_message(request, messages.ERROR, msg)
    return redirect('base:login')

def dashboard(request):
    context = {}
    context.update(csrf(request))
    user = session_check(request)
    if not user:
        return redirect('base:login')
    context['temp_user'] = user
    context['title'] = "Hello, {}!".format(user.name)
    context['latest_questions'] = user.latest_questions()
    return render(request, 'base/dashboard.html', context)

@csrf_protect
def answer_page(request, question):
    context = {}
    student = student_session_check(request, question)
    if not student:
        return redirect('base:login')
    question = get_object_or_404(Question, pk=question)
    context.update({
        'student':student,
        'question':question,
        'title': 'Answer Page',
        'form': AnswerForm(initial={'question':question})})
    if request.method == 'POST':
        valid = False
        form = AnswerForm(request.POST)
        student = request.POST.get('student', None)
        if not question.allow_anonymous:
            if student:
                form = AnswerForm(request.POST, student=student)
                valid = True
            else:
                msg = 'Error! This question requires a username.'
                context.update({'message':msg})
        else:
            valid = True

        if valid:
            if form.is_valid():
                instance = form.save(commit=False)
                other_text = request.POST.get('other_text', None)
                if not question.allow_anonymous:
                    student_obj = get_object_or_None(TempUser, id=student)
                    instance.created_by = student_obj
                if other_text:
                    instance.note = other_text
                instance.save()
                msg = 'Your answer has been recorded'
                context.update({'message': msg })

        context['form'] = form
    return render(request, 'base/answer_page.html', context)


## Answers
def answers_by_question_graph(request, question_id):
    user = session_check(request)
    if not user:
        return redirect('base:login')
    question = get_object_or_None(Question, id=question_id)
    context = {'title' : 'Answers: {}'.format(question.name)}
    answers = Answer.objects.filter(question=question, is_active=True)

    averages = []
    emotion_labels = []
    emotion_colors = []
    colors = []
    response_count = []
    for k, v in Emotion.EMOTION_COLORS:
        answers_per_emotion = answers.filter(emotion=k)
        intensity_list = answers_per_emotion.values_list('intensity', flat=True)
        response_count.append(answers_per_emotion.count())
        if intensity_list:
            intensity_average = sum(intensity_list)/ len(intensity_list)
        else:
            intensity_average = 0
        if k != 'none' and k != 'other':
            averages.append(intensity_average)
            colors.append(v)
            emotion_colors.append(k)
        emotion_labels.append(k)
    context.update({'total_count' : answers.count()})
    context.update({
                'count': json.dumps(response_count),
                'averages': json.dumps(averages),
                'emotion_all' : json.dumps(emotion_labels),
                'emotion_colors' : json.dumps(emotion_colors),
                'colors': json.dumps(colors),
                })
    return render(request, 'base/answers_graph.html', context)


def answer_list(request, *args, **kwargs):
    user = session_check(request)
    if not user:
        return redirect('base:login')
    context = {}
    mode, mode_id = '', ''
    if 'mode' in kwargs:
        mode= kwargs.get('mode')
        context['mode'] = True
    if 'mode_id' in kwargs:
        mode_id = kwargs.get('mode_id')
    tag = request.GET.get('tag', None)
    page = request.GET.get('page')

    questions = Question.objects.filter(created_by=user, is_active=True)
    tags = questions.values_list('tag', flat=True)
    tags = list(set(filter(None, tags)))
    context['tags'] = tags

    title = 'All Answers'
    answers = Answer.objects.filter(question__created_by__pk=user.id, is_active=True).order_by('-pk')
    date_from = request.GET.get('date_from', None)
    date_to = request.GET.get('date_to', None)
    if date_from:
        start_date = datetime.datetime.strptime(date_from, "%m/%d/%Y")
        answers = answers.filter(date__gte=start_date)
        context['date_from'] = date_from
    if date_to:
        end_date = datetime.datetime.strptime(date_to, "%m/%d/%Y")
        answers = answers.filter(date__lte=end_date)
        context['date_to'] = date_to

    if mode == 'question':
        question = get_object_or_None(Question, id=int(mode_id))
        title = 'Answers to Question: {}'.format(question.name)
        answers = answers.filter(question__id=int(mode_id))
        context['question'] = question
    elif (tag and tag != 'all') or mode == 'tag':
        if tag:
            mode_id = tag
        context['tag'] = mode_id
        title = 'Answers by Tag: {}'.format(mode_id)
        answers = answers.filter(question__tag=mode_id)
    page_objects = paginate(page, answers)
    context['title'] = title
    context['object_list'] = page_objects
    context['count'] = answers.count()
    context['mode'] = mode
    return render(request, 'base/answer_list.html', context)


def tag_list(request):
    context = {}
    user = session_check(request)
    if not user:
        return redirect('base:login')
    questions = Question.objects.filter(
                                    created_by=user, is_active=True).order_by(
                                    '-date').select_related('answer_set')

    tags = questions.values('tag').annotate(tag_count=Count('tag')).order_by('tag')
    context['title'] = "Tag List"
    context['tags'] = tags
    context['count'] = tags.count()
    return render(request, 'base/tag_list.html', context)


## Question
@csrf_protect
def create_question(request):
    context = {}
    context['title'] = 'Create a Question'
    user = session_check(request)
    if not user:
        return redirect('base:login')
    form = QuestionForm()
    context.update({'form': form})
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('base:question_list')
    return render(request, 'base/question_form.html', context)


@csrf_protect
def update_question(request, question_id):
    context = {}
    context['title'] = 'Update a Question'
    user = session_check(request)
    if not user:
        return redirect('base:login')
    question = get_object_or_404(Question, id=question_id)
    code = question.code
    form = QuestionForm(instance=question)
    context['question'] = question
    context.update({'form': form})
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()
            msg = 'Question {} has been updated!'.format(code)
            messages.success(request, msg)
            return redirect('base:question_list')
    return render(request, 'base/question_form.html', context)

@csrf_protect
def delete_question(request, question_id):
    context = {}
    user = session_check(request)
    if not user:
        return redirect('base:login')
    question = get_object_or_404(Question, id=question_id)
    code = question.code
    question.is_active = False
    question.save(update_fields=["is_active"])
    message = 'Question {} has been deleted'.format(code)
    messages.success(request, message)
    return redirect('base:question_list')


def question_list(request):
    context = {}
    tags = []
    title = "Question List"
    user = session_check(request)
    if not user:
		return redirect('base:login')
    questions = Question.objects.filter(created_by=user, is_active=True).order_by('-date')
    total = questions.count()
    tags = questions.values_list('tag', flat=True)
    tags = list(set(filter(None, tags)))
    tag = request.GET.get('tag', None)
    keyword = request.GET.get('keyword', None)
    page = request.GET.get('page', None)

    if tag and tag != 'all':
        questions = questions.filter(tag=tag)
        total_tag = questions.count()
        context.update({
                'total_tag': total_tag,
                'tag' : tag
                    })
    elif keyword:
        questions = questions.filter(Q(name__icontains=keyword)|Q(code__icontains=keyword))
        total_keyword = questions.count()
        context.update({
                    'total_keyword': total_keyword,
                    'keyword' : keyword
                    })

    for q in questions:
        q.answer_count = q.answer_set.filter(is_active=True).count()

    page_objects = paginate(page, questions)
    context.update({'object_list': page_objects,
                    'total' : total,
                    'tags' : tags,
                    'title' : title })
    return render(request, 'base/question_list.html', context)

def questions_by_tag(request, tag=False):
    context = {}
    user = session_check(request)
    if not user:
        return redirect('base:login')
    if tag:
        questions = Question.objects.filter(
                                created_by=user, tag=tag,
                                is_active=True).order_by('-date')
        for q in questions:
            answers = q.answer_set.filter(is_active=True)
            q.answer_count = answers.count()
        context.update({
            'title':'Question List by Tag: {}'.format(tag),
            'questions':questions,
            'total_tag': questions.count(),
            'tag':tag,
            })
    return render(request, 'base/question_list_by_tag.html', context)


def answers_by_tag_graph(request, tag=False):
    user = session_check(request)
    if not user:
        return redirect('base:login')
    context = {}
    if tag:
        context['tag'] = tag
        context.update({'title' : 'Tag: {}'.format(tag)})
        answers = Answer.objects.filter(question__created_by=user,
                                        question__tag=tag,
                                        is_active=True)

    averages = []
    emotion_labels = []
    colors = []
    response_count = []
    for k, v in Emotion.EMOTION_COLORS:
        answers_per_emotion = answers.filter(emotion=k)
        intensity_list = answers_per_emotion.values_list('intensity', flat=True)
        response_count.append(answers_per_emotion.count())
        if intensity_list:
            intensity_average = sum(intensity_list)/ len(intensity_list)
        else:
            intensity_average = 0
        averages.append(intensity_average)
        emotion_labels.append(k)
        colors.append(v)
    context.update({'total_count' : answers.count()})
    context.update({
                'count': json.dumps(response_count),
                'averages': json.dumps(averages),
                'emotion_labels' : json.dumps(emotion_labels),
                'colors': json.dumps(colors),
                })
    return render(request, 'base/answers_graph.html', context)

## Students
def answers_by_student(request, student_id):
    user = session_check(request)
    if not user:
        return redirect('base:login')
    page = request.GET.get('page')
    student = get_object_or_None(TempUser, id=student_id)
    context = {'title' : 'Student Responses: {}'.format(student.name)}
    answers = Answer.objects.filter(question__created_by__id=user.id,
                                    created_by=student, is_active=True).order_by('-date')
    page_objects = paginate(page, answers)
    context['object_list'] = page_objects
    context['student'] = student
    return render(request, 'base/answer_list.html', context)


def student_list(request):
    user = session_check(request)
    if not user:
        return redirect('base:login')
    context = {'title' : 'List of Students'}
    answers = Answer.objects.filter(question__created_by=user, is_active=True).order_by('-date')
    students_pk_list = list(set(answers.values_list('created_by', flat=True)))
    page = request.GET.get('page', 1)
    rows = []
    for student_id in students_pk_list:
        student = get_object_or_None(TempUser, id=student_id)
        answers_per_student = answers.filter(created_by__id=student_id).order_by('-date')
        latest_answer = answers_per_student.first()
        latest_question = latest_answer.question
        total_per_student = answers_per_student.count()
        student_name = student.name if student else 'Anonymous Users'
        rows.append({'name': student_name,
                    'count' :total_per_student,
                    'id' : student_id,
                    'latest_question' : latest_question,
                    'latest_answer' : latest_answer})
    page_objects = paginate(page, rows)
    context.update({'object_list' : page_objects})
    return render(request, 'base/student_list.html', context)


def answers_by_student_graph(request, student_id=None):
    user = session_check(request)
    if not user:
        return redirect('base:login')
    context = {}
    if student_id:
        student = get_object_or_None(TempUser, id=student_id)
        context.update({'title' : 'Student: {}'.format(student.name)})
        answers = Answer.objects.filter(question__created_by=user, created_by=student, is_active=True)
    else:
        student = 0
        context.update({'title' : 'Anonymous responses'})
        answers = Answer.objects.filter(question__created_by=user, created_by=None, is_active=True)
    context['student'] = student

    averages = []
    emotion_labels = []
    colors = []
    response_count = []
    for k, v in Emotion.EMOTION_COLORS:
        answers_per_emotion = answers.filter(emotion=k)
        intensity_list = answers_per_emotion.values_list('intensity', flat=True)
        response_count.append(answers_per_emotion.count())
        if intensity_list:
            intensity_average = sum(intensity_list)/ len(intensity_list)
        else:
            intensity_average = 0
        averages.append(intensity_average)
        emotion_labels.append(k)
        colors.append(v)
    context.update({'total_count' : answers.count()})
    context.update({
                'count': json.dumps(response_count),
                'averages': json.dumps(averages),
                'emotion_labels' : json.dumps(emotion_labels),
                'colors': json.dumps(colors),
                })
    return render(request, 'base/answers_graph.html', context)


def paginate(page, object_list, count_per_page=10):
    paginator = Paginator(object_list, count_per_page)
    try:
        objects = paginator.page(page)
    except PageNotAnInteger:
        objects = paginator.page(1)
    except EmptyPage:
        objects = paginator.page(paginator.num_pages)
    return objects


