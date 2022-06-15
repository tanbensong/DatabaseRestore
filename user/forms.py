from django import forms
from django.core.validators import RegexValidator
from django.contrib.auth import authenticate

from captcha.fields import CaptchaField


class UserForms(forms.Form):
    username = forms.CharField(
        max_length=100,
        label="用户名",
        widget=forms.TextInput(attrs={'autofocus': ''})
    )
    password = forms.CharField(
        max_length=100,
        label="密码",
        widget=forms.PasswordInput()
    )
    captcha = CaptchaField(label='验证码')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 添加默认 css
        for name,field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = '请输入{}'.format(field.label)

    def clean(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        user = authenticate(username=username, password=password)
        if user is None:
            raise forms.ValidationError('用户名或密码错误')
        else:
            self.cleaned_data['user'] = user

        return self.cleaned_data


class UserCenterForms(forms.Form):
    oldPassword = forms.CharField(
        max_length=100, label="旧密码",
        required=True,
        error_messages={'required':  "用户旧密码不能为空"},
        widget=forms.PasswordInput(attrs={'autofocus': ''})
    )
    newPassword = forms.CharField(
        max_length=100, label="新密码",
        required=True,
        min_length=8,
        error_messages={'required':  "密码不能为空", "min_length": "至少8位"},
        widget=forms.PasswordInput(),
        validators=[
            RegexValidator("^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{8,16}$", "密码是8到15位且需包含字母、数字")
        ],
    )
    confirmPassword = forms.CharField(
        max_length=100, label="确认密码",
        required=True,
        error_messages={'required':  "确认密码不能为空"},
        widget=forms.PasswordInput()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 添加默认 css placeholder
        for name,field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = '请输入{}'.format(field.label)
