from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django import forms
from .models import User, ReviewModel

class LoginForm(AuthenticationForm):
    """ログインフォーム"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label

class UserCreateForm(UserCreationForm):
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
    class Meta:
        model = User
        fields = ('username',)

class CreateForm(forms.ModelForm):
    class Meta:
        model = ReviewModel
        fields = (
            'user_title','user_review','user_name','user_value1','user_value2','user_value3','user_value4','user_value5',
            )

