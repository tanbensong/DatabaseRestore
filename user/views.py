from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.views import View
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.hashers import make_password

from user.forms import UserForms, UserCenterForms
from user.models import User

# Create your views here.

class loginViews(View):
    """用户登陆"""
    template_name = "login.html"

    def get(self, request, *args, **kwargs):
        form = UserForms()

        return render(request, self.template_name, locals())
        
    def post(self, request, *args, **kwargs):
        form = UserForms(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            # 默认跳转到首页
            next_url = request.GET.get('next', reverse('home'))
            return redirect(next_url)

        return render(request, self.template_name, locals())


class logoutViews(View):
    """注销用户"""
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('/devops/login/')


class UserInfoViews(View):
    template_name = "userinfo.html"

    def get(self, request, *args, **kwargs):
        form = UserCenterForms()
        if request.user.is_authenticated:
            return render(request, self.template_name, locals())
        else:
            return redirect('/devops/login/')

    def post(self, request, *args, **kwargs):
        form = UserCenterForms()
        username = request.user
        oldPassword = request.POST.get('oldPassword')
        newPassword = request.POST.get('newPassword')
        confirmPassword = request.POST.get('confirmPassword')
        print(username, oldPassword, newPassword, confirmPassword)

        if confirmPassword != newPassword:
            errmsg = "两次密码输入不一致"
        
        user = authenticate(username=username, password=oldPassword)
        if user is not None:
            userinfo = User.objects.get(username=username)
            userinfo.password = make_password(newPassword)
            userinfo.save()

            return redirect('/devops/login/')
        else:
            errmsg = "用户密码错误"

        return render(request, self.template_name, locals())
