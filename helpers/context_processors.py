from base.models import TempUser
from .tools import session_check, student_session_check

def user_processor(request):
    user = session_check(request)
    if not user:
        user = request.session.get('student', None)
    return {'temp_user': user}