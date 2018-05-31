from django import forms

from .models import Answer, Question, TempUser

class QuestionForm(forms.ModelForm):

    tag = forms.CharField(widget=forms.TextInput(attrs={'pattern':'[A-Za-z]+', 'title':'Enter alphanumeric characters only. '}))

    class Meta:
        model = Question
        fields = ('name', 'tag', 'allow_anonymous', 'status', 'submission', 'created_by')
        widgets = {
            'created_by': forms.HiddenInput()
        }



    def __init__(self, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = "Question"
        self.fields['submission'].label = "No. of submissions"
        self.fields['allow_anonymous'].required = False



class AnswerForm(forms.ModelForm):

    class Meta:
        model = Answer
        fields = ['emotion', 'intensity', 'question']
        widgets = {
            'emotion': forms.HiddenInput(),
            'intensity' : forms.HiddenInput(),
            'question' : forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        if 'student' in kwargs:
            self.student = kwargs.pop('student', None)
        super(AnswerForm, self).__init__(*args, **kwargs)


    def clean(self, *args, **kwargs):
        cleaned_data = self.cleaned_data
        question = cleaned_data.get('question')
        if not question.allow_anonymous:
            student = self.student if self.student else None
            answer = Answer.objects.filter(
                                        created_by__id=student,
                                        question__id=question.id,
                                        question__allow_anonymous=False,
                                        is_active=True)
            if answer.exists() and question.submission == 'single':
                raise forms.ValidationError('You have already answered this question')
        return cleaned_data



    def save(self, commit=True, *args, **kwargs):
        instance = super(AnswerForm, self).save(False)
        try:
            user = TempUser.objects.get(id=self.id)
            instance.created_by = user
        except:
            pass
        if commit:
            instance.save()
        return instance


class TempUserForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(TempUserForm, self).__init__(*args, **kwargs)
        self.fields['user_type'].choices = TempUser.USER_TYPES

    class Meta:
        model = TempUser
        fields = ['name', 'user_type']
        fields_required = ['name', 'user_type']



