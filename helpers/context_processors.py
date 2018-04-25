from base.models import TempUser
from .tools import session_check, student_session_check
from .tools import get_object_or_None

def user_processor(request):
    user = session_check(request)
    if not user:
        student_id = request.session.get('student', None)
        if student_id:
            user = get_object_or_None(TempUser, id=student_id)
        else:
            user = False
    return {'temp_user': user}