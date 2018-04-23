from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic.base import TemplateView

from . import views

urlpatterns = [
	url(r'^login/$',views.login, name='login'),
	url(r'^logout/$', views.logout, name='logout'),
    url(r'^create-user/$', views.create_user, name='create_user'),

	url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^(?P<question>\w+)/$', views.answer_page, name='answer_page'),
    url(r'^answer-list/$', views.answer_list, name='answer_list'),

    url(r'^answer-graph/(?P<question_id>\d+)/$', views.answers_by_question_graph, name='answer_graph'),

    url(r'^answer-list/(?P<mode>\w+)/' +
        '(?P<mode_id>\w+)/$', views.answer_list, name='answer_list_by_filter'),

    url(r'^create-question/$', views.create_question, name='create_question'),
    url(r'^view-question/(?P<question_id>\d+)/$', views.update_question, name='update_question'),
    url(r'^delete-question/(?P<question_id>\d+)/$', views.delete_question, name='delete_question'),
    url(r'^question-list/$', views.question_list, name='question_list'),
    url(r'^tags/list/$', views.tag_list, name='tag_list'),
    url(r'^tags/(?P<tag>\w+)/questions/$', views.questions_by_tag, name='questions_by_tag'),
    url(r'^tags/(?P<tag>\w+)/graphs/$', views.answers_by_tag_graph, name='answers_by_tag_graph'),

    url(r'^student-responses/(?P<student_id>\w+)/$', views.answers_by_student, name='answers_by_student'),
    url(r'^student-list/$', views.student_list, name='student_list'),
    url(r'^student-responses/graphs/(?P<student_id>\w+)/$', views.answers_by_student_graph, name='answers_by_student_graph'),


    url(r'^$', views.IndexView.as_view()),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^lti/', include('lti_provider.urls')),
    url(r'^assignment/1/', views.LTIAssignment1View.as_view()),
    url(r'^assignment/2/', views.LTIAssignment2View.as_view()),
]
