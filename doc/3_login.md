# 用户登录功能

## 功能细分
- 用户登录的功能由几个小部分构成
    1. 前端登录页面
    2. 前端ajax发送请求
    3. 后端验证
        - 验证提交数据是否合法
        - 验证用户是否存在
    4. 返回验证结果
        - 验证失败，返回错误信息，并在ajax的success对应回调函数中渲染页面
        - 验证成功，返回成功信息，并在回调函数中实现页面跳转功能


#### 1. 前端登录页面
- 登录页面的渲染使用到的是Django提供的form组件，form组件类我们单独定义在一个文件中，这里使用的是Form类，没有使用ModelForm，在后面问卷页面的渲染中我们会使用ModelForm。form类中定义如下

```python

from django.forms import Form, ModelForm
from django.forms import fields
from django.forms import widgets


class BaseInfoForm(Form):
    """ 基本用户信息form组件类

    """
    username = fields.CharField(required=True,
                                error_messages={'required': '用户名不能为空'},
                                widget=widgets.TextInput(attrs={'placeholder': '用户名',
                                                                'class': 'form-control',
                                                                'aria-describedby': "username"}))

    password = fields.CharField(required=True,
                                error_messages={'required': '密码不能为空'},
                                widget=widgets.PasswordInput(attrs={'placeholder': '密码',
                                                                    'class': 'form-control',
                                                                    'aria-describedby': "password"}))


class LoginForm(BaseInfoForm):
    """ 用于登录的form组件类

    """
    pass
```

- 注意，在widget参数中，我提供了`aria-describedby`参数，因为前端我们将会使用到BootStrap框架提供的form校验插件，另外其对应value的设置应该与字段名成一致，这虽然不是必需的，但是在渲染错误信息的时候，错误信息form.errors中存放的key就是字段名，所以在程序设计的过程中，一定要考虑程序的可扩展性和对后面功能的易用性

- login.html 内容如下

```html
{% load staticfiles %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>员工调查问卷系统</title>
    <link rel="stylesheet" href="{% static '/plugins/bootstrap/css/bootstrap.min.css' %}">
    <link rel="stylesheet" href="{% static '/css/login.css' %}">
</head>
<body>

<div class="container ">
    <div class="row my-style">
        <div class="col-md-4 col-md-offset-5">
            <p class="title">登陆后，接受爸爸的调查吧</p>
        </div>
    </div>
    <div class="row">
        <div class="col-md-4 col-md-offset-4">
            <!-- form 表单 -->
            <form class="form-horizontal" novalidate>
                {% csrf_token %}
                <div class="form-group">
                    <label for="id_username" class="col-sm-4 control-label text-justify">用户名</label>
                    <div class="col-sm-8">
                        {{ form.username }}
                        <span id="username" class="help-block my-display"></span>
                    </div>
                </div>
                <div class="form-group">
                    <label for="id_password" class="col-sm-4 control-label text-justify">密码</label>
                    <div class="col-sm-8">
                        {{ form.password }}
                        <span id="password" class="help-block"></span>
                    </div>
                </div>


                <div class="form-group">
                    <div class="col-sm-offset-2 col-sm-10">
                        <div class="checkbox">
                            <label>
                                <input type="checkbox"> 下次自动登录
                            </label>
                        </div>
                    </div>
                </div>
            </form>
            <div class="col-md-8 col-md-offset-5">
                    <button class="btn btn-default"  id="login" style="font-weight: bold;color: #904">登陆</button>
            </div>
        </div>
    </div>
</div>

<script src="{% static '/js/jquery-1.12.4.min.js' %}"></script>
<script src="{% static '/plugins/bootstrap/js/bootstrap.min.js' %}"></script>
<script src="{% static '/js/login.js' %}"></script>
</body>
</html>

```


- 注意,这里再引入静态文件的时候,使用的是Django提供的`staticfiles`组件,我们可以像使用url反响解析一样去生成静态文件的路径,不过要注意的是,参数中的路径需要以`/`开头


#### 2. 前端ajax发送请求
- 用户填写完数据之后,点击按钮就会出发其onclick事件，接着发送ajax请求给服务端，代码如下

```javascript
 $("#login").click(function () {
    // 发送Ajax请求
    $.ajax({
        url: "/survey/login/",
        type: "post",
        data: {
            username: $('#id_username').val(),
            password: $('#id_password').val(),
            "csrfmiddlewaretoken": $("input:hidden").val()
        },
        success: function (data) {
            data = JSON.parse(data);
            // 用户登陆成功
            if (data["success"]) {
                    window.location.href = data["location_href"];
            }

            // 用户登陆失败，渲染错误信息
            if (data["form_errors"]) {
                for (var key in data["form_errors"]) {
                    $("#" + key).text(data["form_errors"][key]);
                    $("#" + key).parent().parent().addClass('has-error');
                }
            }
        }
    });
 });
```

- 代码很简单,这里就不再解释


#### 3. 后端验证
- 后端验证用户提交数据的合法性是通过form组件来完成的
- **这里要注意，由于在设计模型的时候，将employee表与admin表分开了，那么在登录后，我们要在后端对管理员与用户进行区分验证**，代码如下


```python
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
```

- **注意，这里也可以使用Django提供的JsonResponse，如果使用了JsonResponse，那么前端ajax获取到的数据就不需要反序列化了**


