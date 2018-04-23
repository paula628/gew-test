
import logging
import json

from collections import OrderedDict

from django.contrib import auth
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

#from timer import Timer

from django.middleware.csrf import CsrfViewMiddleware, get_token
from django.test import Client



logger = logging.getLogger(__name__)


class LTIAuthMiddleware(object):
    """
    Middleware for authenticating users via an LTI launch URL.
    If the request is an LTI launch request, then this middleware attempts to
    authenticate the username and signature passed in the POST data.
    If authentication is successful, the user is automatically logged in to
    persist the user in the session.
    If the request is not an LTI launch request, do nothing.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_request(self, request):
        print request.POST, 'xxxx'
        logger.debug('inside process_request %s' % request.path)
        # AuthenticationMiddleware is required so that request.user exists.
        if not hasattr(request, 'user'):
            logger.debug('improperly configured: requeset has no user attr')
            raise ImproperlyConfigured(
                "The Django LTI auth middleware requires the"
                " authentication middleware to be installed.  Edit your"
                " MIDDLEWARE_CLASSES setting to insert"
                " 'django.contrib.auth.middleware.AuthenticationMiddleware'"
                " before the PINAuthMiddleware class.")
        else:
            print 'user', request.user

        if request.method == 'POST' and request.POST.get('lti_message_type') == 'basic-lti-launch-request':
            user = auth.authenticate(request, username='escpdigital', password='escpdigital')
            print user, 'USeeerRRR'
            csrf_token = self.client.cookies['csrftoken'].value
            print csrf_token, 'csrf'

            if user is not None:
                # User is valid.  Set request.user and persist user in the session
                # by logging the user in.
                logger.debug('user was successfully authenticated; now log them in')
                request.user = user
                auth.login(request, user)
                lti_launch = {
                    'context_id': request.POST.get('context_id', None),
                    'context_label': request.POST.get('context_label', None),
                    'context_title': request.POST.get('context_title', None),
                    'context_type': request.POST.get('context_type', None),
                    'custom_canvas_account_id': request.POST.get('custom_canvas_account_id', None),
                    'custom_canvas_account_sis_id': request.POST.get('custom_canvas_account_sis_id', None),
                    'custom_canvas_api_domain': request.POST.get('custom_canvas_api_domain', None),
                    'custom_canvas_course_id': request.POST.get('custom_canvas_course_id', None),
                    'custom_canvas_membership_roles': request.POST.get('custom_canvas_membership_roles', '').split(','),
                    'custom_canvas_enrollment_state': request.POST.get('custom_canvas_enrollment_state', None),
                    'custom_canvas_user_id': request.POST.get('custom_canvas_user_id', None),
                    'custom_canvas_user_login_id': request.POST.get('custom_canvas_user_login_id', None),
                    'launch_presentation_css_url': request.POST.get('launch_presentation_css_url', None),
                    'launch_presentation_document_target': request.POST.get('launch_presentation_document_target', None),
                    'launch_presentation_height': request.POST.get('launch_presentation_height', None),
                    'launch_presentation_locale': request.POST.get('launch_presentation_locale', None),
                    'launch_presentation_return_url': request.POST.get('launch_presentation_return_url', None),
                    'launch_presentation_width': request.POST.get('launch_presentation_width', None),
                    'lis_course_offering_sourcedid': request.POST.get('lis_course_offering_sourcedid', None),
                    'lis_outcome_service_url': request.POST.get('lis_outcome_service_url', None),
                    'lis_person_contact_email_primary': request.POST.get('lis_person_contact_email_primary', None),
                    'lis_person_name_family': request.POST.get('lis_person_name_family', None),
                    'lis_person_name_full': request.POST.get('lis_person_name_full', None),
                    'lis_person_name_given': request.POST.get('lis_person_name_given', None),
                    'lis_person_sourcedid': request.POST.get('lis_person_sourcedid', None),
                    'lti_message_type': request.POST.get('lti_message_type', None),
                    'resource_link_description': request.POST.get('resource_link_description', None),
                    'resource_link_id': request.POST.get('resource_link_id', None),
                    'resource_link_title': request.POST.get('resource_link_title', None),
                    'roles': request.POST.get('roles', '').split(','),
                    'selection_directive': request.POST.get('selection_directive', None),
                    'tool_consumer_info_product_family_code': request.POST.get('tool_consumer_info_product_family_code', None),
                    'tool_consumer_info_version': request.POST.get('tool_consumer_info_version', None),
                    'tool_consumer_instance_contact_email': request.POST.get('tool_consumer_instance_contact_email', None),
                    'tool_consumer_instance_description': request.POST.get('tool_consumer_instance_description', None),
                    'tool_consumer_instance_guid': request.POST.get('tool_consumer_instance_guid', None),
                    'tool_consumer_instance_name': request.POST.get('tool_consumer_instance_name', None),
                    'tool_consumer_instance_url': request.POST.get('tool_consumer_instance_url', None),
                    'user_id': request.POST.get('user_id', None),
                    'user_image': request.POST.get('user_image', None),
                }
            setattr(request, 'LTI', request.session.get('LTI_LAUNCH', {}))
        else:
            print 'NOTT'