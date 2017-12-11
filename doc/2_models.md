# 投票系统模型设计


## 思路
- 数据库用来存放数据，Django模型是用来生成数据库表的，因此要想设计模型，得分析好整个项目中需要存放和用到哪些数据
- 从功能的实现来对模型进行设计



#### 部门表
- 每一个员工都有其所属的部门，另外，每一个调查问卷都有一个对应的部门，并且一个部门可以对应多个调查问卷
- 部门表应有以下基本字段
    - id （主键）
    - name 

#### 管理员表与员工表
- 管理员和员工要想实现登录的功能，就必须再数据库中保存他们用来登录的相关信息。并且表中至少要有三个字段
    - id
    - username
    - password

- 员工表中，额外要有一个关联字段与部门表关联
    - ForeignKey: department



#### 问卷表
- 主页面要显示与问卷相关的详细信息，那么这些详细信息一定要保存在数据库中，对于每一个管理员创建的问卷对象来说，要想完整显示问卷信息表格;每一个问卷都有一个对应的管理员来创建的，并且一个管理员可以创建多个问卷，因此问卷应该与管理员之间建立多对一的外键关系。那么到目前位置，我们的问卷表中至少有以下字段
    - 普通字段
        - id（主键）
        - title 问卷名称
        - create_time 创建时间
    - 关联字段
        - ForeignKey: user 创建人
        - ForeignKey: department 部门

#### 问题表
- 员工要填写问卷的时候，问卷上肯定要有对应的问题，在实际中，这些问题对象的类型往往有很多种，比如单选、多选、打分（评价）、建议等，对于每一个问题来说他都有一个标题，这个标题就是我们常说的题干。每一个问题都属于一个问卷，多个问题可以对应一个问卷，因此再问题表中还要建立与问卷表的外键关系。
    - **注意：由于问题选项几乎是固定不变的，因此考虑到联表中跨表查询的性能损耗，我们可以使用choices来代替表，这样做我们只需要在问题表模型中创建一个映射关系即可**
- 那么我们的问题表应该至少具有下面字段
    - 普通字段
        - id（主键）
        - title 问题内容
        - type 问题类型
    - 关联字段
        - ForeignKey: questionnaire 问卷表

#### 选项表
- 对于问题类型为单选或者多选的问题对象来说，每一个问题对象有多个选项，并且每一个选项我们要对应一个分值，这样做是为了实现平均分及其他分数相关功能；另外，选项应该与问题对象之间建立多对一的外键关联关系，因为一个选择题不可能只有一个选项，否则就不是选择题了。那么到目前为止选项表就应该有以下几个字段
    - 普通字段
        - id （主键）
        - content 选项内容（比如： “A：非常满意”）
        - score  选项分值
    - 关联字段
        - ForeignKey: question 问题表

#### 答案表
- 员工填写完问卷之后，问卷的每一个问题肯定会对应一个答案，由于不同类型的问题对应的答案是不同的，因此为了方便，在每一个答案对象中设置三种类型的答案，比如对于打分题来说，就设置score字段作为答案，对于建议题来说，就设置文本字段来存储答案，对于选择题来说，就将该答案关联至选项表中的一条记录对象，有一个要注意的是，上面的三种字段必须设置默认值，在模型中要设置null参数，一般设置为None
    - **注意：每一个用户对于同一个题目只能回答一次，因此我们要让用户与一条答案（id）联合唯一**

- 主要字段如下
    - 普通字段
        - id（主键）
        - content 存储文本答案
        - score 存储打分题答案
    - 关联字段
        - ForeginKey: choice  存储选择题答案
        - ForeignKey: user 
    - 联合唯一
        - ("id", "user")



## 实现

```python
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


```
        
        
        
        
        
        
        
        
        
        
    
    
    
    
    
    
    

