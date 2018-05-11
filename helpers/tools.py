from django.core.exceptions import ObjectDoesNotExist

from base.models import TempUser, Question


def get_object_or_None(model, *args, **kwargs):
	try:
	    obj  = model.objects.get(*args, **kwargs)
	except ObjectDoesNotExist:
	    obj = False
	return obj


def session_check(request):
	if 'user' in request.session and request.session['user']:
		user_id = request.session.get('user')
		user = get_object_or_None(TempUser, id=user_id)
		return user
	else:
		return False
	return False

def student_session_check(request, question):
	res = False
	question = get_object_or_None(Question, pk=question)
	if question and question.status == 'closed':
		res = False
	else:
		if question.allow_anonymous:
			res = True
		elif not question.allow_anonymous:
			student_id = request.session.get('student', None)
			res = get_object_or_None(TempUser, id=student_id)
	return res
