from django.db import models


class Department(models.Model):
    """ 部门表
    普通字段:
        id, dep_name
    """

    id = models.AutoField(primary_key=True)
    department_name = models.CharField(max_length=16, blank=True, verbose_name='部门名称')

    def __str__(self):
        return self.department_name

    class Meta:
        verbose_name_plural = '部门表'


class Employee(models.Model):
    """ 用户信息表
    普通字段:
        id, username, password
    关联字段:
        department(多对一, to=Department.id)
    """

    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=32, verbose_name='用户名', unique=True)
    password = models.CharField(max_length=32, verbose_name='密码')

    department = models.ForeignKey(to='Department', to_field='id', verbose_name='部门', on_delete=True)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name_plural = '用户表'


class Admin(models.Model):
    """ 管理员表
    普通字段:
        username, password
    """

    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=32, verbose_name='用户名', unique=True)
    password = models.CharField(max_length=32, verbose_name='密码')

    def __str__(self):
        return self.username

    class Meta:
        verbose_name_plural = '管理员表'


class Questionnaire(models.Model):
    """ 问卷表
    普通字段:
        id, title, description
    关联字段:
        department(一对一, to=BanJi.id)
    """

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=32, verbose_name='问卷标题')
    description = models.CharField(max_length=512, verbose_name='问卷描述')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    admin = models.ForeignKey(to='Admin', to_field='id', verbose_name='创建人', on_delete=True)
    department = models.ForeignKey(to='Department', to_field='id', verbose_name='接受调查的部门', on_delete=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = '问卷表'


class Question(models.Model):
    """ 问题表
    普通字段:
        id, question_type, content
    关联字段:
        questionnaire(多对一, to=Questionnaire.id)
    """

    id = models.AutoField(primary_key=True)
    content = models.CharField(max_length=256, verbose_name='问题内容')

    question_type_choices = [
        (1, "单选"),
        (2, "多选"),
        (3, "打分"),
        (4, "建议"),
    ]
    question_type = models.IntegerField(choices=question_type_choices, verbose_name='问题类型')

    questionnaire = models.ForeignKey(to='Questionnaire', to_field='id', verbose_name='所属问卷', on_delete=True)

    def __str__(self):
        return self.content

    class Meta:
        verbose_name_plural = '问题表'


class Choice(models.Model):
    """ 问题选项表
    普通字段:
        id, 标题, 选项值
    关联字段:
        question(多对一， to=Question.id)
    """

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=32, verbose_name='选项标题')
    score = models.IntegerField(verbose_name='选项分数')

    question = models.ForeignKey(to='Question', to_field='id', verbose_name='所属问题', on_delete=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = '问题选项表'


class Answer(models.Model):
    """ 答案表
    普通字段:
        id, val, content
    关联字段:
        choice(多对一, to=Choice.id)
        employee(多对一, to=User.id)
        question(多对一, to=Question.id)
    """

    id = models.AutoField(primary_key=True)

    choice = models.ForeignKey(to="Choice", null=True, blank=True, on_delete=True, verbose_name="选择题对应选项")
    val = models.IntegerField(null=True, blank=True, verbose_name="打分题对应答案")
    content = models.CharField(max_length=255, null=True, blank=True, verbose_name='建议题对应答案')

    employee = models.ForeignKey(to='Employee', to_field='id', verbose_name='回答员工', on_delete=True)
    question = models.ForeignKey(to='Question', to_field='id', verbose_name='对应问题', on_delete=True)

    def __str__(self):
        return self.content

    class Meta:
        unique_together = (('employee', 'question'), )
        verbose_name_plural = '答案表'
