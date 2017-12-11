from django.shortcuts import render, HttpResponse

from json import dumps, loads

from survey.forms import LoginForm
from survey import models


def login(request):
    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'login.html', {'form': form})
    elif request.method == 'POST':           # 登陆验证开始
        form = LoginForm(data=request.POST)
        if not form.is_valid():              # 验证信息格式错误
            data = {'form_errors': form.errors}
            return HttpResponse(dumps(data))

        # 开始验证用户
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        employee_queryset = models.Employee.objects.filter(username=username, password=password)
        admin_queryset = models.Admin.objects.filter(username=username, password=password)
        if employee_queryset:
            request.session["user_id"] = employee_queryset[0].id
            request.session["username"] = employee_queryset[0].username
            request.session["role"] = 'employee'
            data = {'success': True, "location_href": '/'}
        elif admin_queryset:
            request.session["role"] = 'admin'
            request.session["user_id"] = admin_queryset[0].id
            data = {'success': True, "location_href": '/'}
        else:
            form.add_error(field='password', error="用户名或密码错误")
            data = {'success': False, "form_errors": form.errors}
        return HttpResponse(dumps(data))

