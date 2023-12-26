from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.core.validators import validate_email
import re


from app.models import Tag, Profile, Answer


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(min_length=5, widget=forms.PasswordInput)

    def clean_username(self):
        data = self.cleaned_data.get('username')
        if not User.objects.filter(username__exact=data).exists():
            raise ValidationError("User doesn't exist")
        return data

class RegisterForm(forms.ModelForm):
    password = forms.CharField(min_length=5, widget=forms.PasswordInput)
    password_check = forms.CharField(min_length=5, widget=forms.PasswordInput)
    nickname = forms.CharField(min_length=5, required=True)
    #avatar = forms.ImageField(required=False, widget=forms.FileInput())
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        password = self.cleaned_data['password']
        password_check = self.cleaned_data['password_check']

        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')
        if User.objects.filter(username__exact=username).exists():
            raise ValidationError({'username': 'User already exists'})

        if password != password_check:
            raise ValidationError({'password': 'Passwords do not match', 'password_check': ''})

        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError({'email': 'Invalid email address'})



    def save(self, **kwargs):
        self.cleaned_data.pop('password_check')
        nickname = self.cleaned_data.pop('nickname')
        new_user = User.objects.create_user(**self.cleaned_data)
        new_user.save()
        new_profile = Profile(user=new_user, nickname=nickname)
        new_profile.save()
        return new_user


class AnswerForm(forms.Form):
    text = forms.CharField(max_length=200, widget=forms.Textarea(attrs={"placeholder": "Enter your answer here"}), label="")
    class Meta:
        model = Answer
        fields = ['text']

class AskForm(forms.Form):
    title = forms.CharField(max_length=50, widget=forms.TextInput(attrs={
        "placeholder": "How?"}))
    text = forms.CharField(max_length=500, widget=forms.Textarea(attrs={
        "placeholder": "And why?", "rows": 8}))
    tags = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        "placeholder": "SQL, C++"}))

    def clean_tags(self):
        tags = self.cleaned_data.get('tags', '')
        if not re.match(r'^[a-zA-Z, ]+$', tags):
            raise forms.ValidationError('Invalid characters in tags. Only latin letters and commas are allowed.')
        return tags
    def save(self):
        tag_titles = [tag.strip() for tag in self.cleaned_data["tags"].split(',')]
        tag_list = [Tag.objects.get_or_create(title=tag)[0] for tag in tag_titles]
        return tag_list


class SettingsForm(forms.ModelForm):
    nickname = forms.CharField(min_length=5, required=False, widget=forms.TextInput())
    email = forms.EmailField(required=False, widget=forms.EmailInput())
    avatar = forms.ImageField(required=False, widget=forms.FileInput())
    class Meta:
        model = User
        fields = ['email']

    def save(self, **kwargs):
        user = super().save(**kwargs)

        profile = user.profile
        received_avatar = self.cleaned_data.get('avatar')
        if received_avatar:
            profile.avatar = self.cleaned_data.get('avatar')
            profile.save()

        return user





















