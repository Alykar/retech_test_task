from django.db.models.signals import post_save
from django.dispatch import receiver
import ctypes
from django.db import models
from django.conf import settings
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.hashers import (
    check_password, is_password_usable, make_password,
)
from django.contrib.auth import password_validation
from .managers import UserManager


class Organization(models.Model):
    """
        Organization.tag will be changed to hash(self.name + self.pk) on save
        Org tag is req to be unique, and used by workers to log in organization for it's
        Projects ToDoLists and Tasks.
    """
    name = models.CharField(verbose_name="Название", max_length=100)
    tag = models.CharField(verbose_name="Тэг", max_length=1000, unique=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='snippets', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Организация"
        verbose_name_plural = "Организации"


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email'), unique=True)
    first_name = models.CharField(_('name'), max_length=30, blank=True)
    last_name = models.CharField(_('surname'), max_length=30, blank=True)
    date_joined = models.DateTimeField(_('registered'), auto_now_add=True)
    is_active = models.BooleanField(_('is_active'), default=True)
    # this needed to get keys for User's organizations, so passwords may be different for each one
    organizations = models.ManyToManyField(Organization, related_name='employers', through='OrgUserPassword')
    # this will change time-to-time (prbbly bad practice) so i can check what org is currently active for each user
    active_org = models.ForeignKey(Organization, on_delete=models.DO_NOTHING, blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    @property
    def where_authenticated(self):
        """
        Always return True. This is a way to tell if the user has been
        authenticated in templates.
        """
        return self.active_org

    def reg_in_organization(self, raw_password, organization):
        """
        Use this to add new organizations when user regs in them
        :param raw_password: any hashable string
        :param organization: Organization model exemp.
        :return: None
        """
        obj = OrgUserPassword(user=self, organization=organization)
        obj.password = make_password(raw_password)
        obj._password = raw_password
        obj.save()


class JoinRequest(models.Model):
    """
    Join Req used to store data for Org.owner's, so they can manage who to add to their organization
    """
    org = models.ForeignKey(Organization, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class OrgUserPassword(models.Model):
    """
    Passwords for Organizations, where user was registered
    Probably should save passwords in hash, but i'm running out of time to change auth logic and save data as hash
    """
    org = models.ForeignKey(Organization, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    password = models.CharField(max_length=1000)
    _password = None

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self._password is not None:
            password_validation.password_changed(self._password, self)
            self._password = None

    def check_password(self, raw_password):
        """
        Return a boolean of whether the raw_password was correct. Handles
        hashing formats behind the scenes.
        """
        return check_password(raw_password, self.password)


class ToDoList(models.Model):
    """
    ToDoLists
    """
    name = models.CharField(verbose_name="Название", max_length=300)
    org = models.ForeignKey(Organization, verbose_name="Проект", on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Список дел"
        verbose_name_plural = "Списки дел"


class Task(models.Model):
    """
    (
    """
    STATUSES = (
        ("1", 'Не назначено'),
        ("2", 'Принято исполнителем'),
        ("3", 'В работе'),
        ("4", 'Отправлено на ревью'),
        ("5", 'Завершено'),
        ("6", 'Отправлено на доработку'),
        ("7", 'Отменено'),
    )
    PRIORITIES = (
        ("0", 'Низший'),
        ("1", 'Низкий'),
        ("2", 'Обычний'),
        ("3", 'Высокий'),
        ("4", 'Высочайший'),
        ("5", 'Срочно')
    )
    name = models.CharField(verbose_name="Название", max_length=1000)
    description = models.TextField(verbose_name="Описание", blank=True)
    status = models.CharField(verbose_name="Статус", serialize=STATUSES, default=1, max_length=1)
    priority = models.CharField(verbose_name="Приоритет", serialize=PRIORITIES, default=2, max_length=1)
    deadline = models.DateField(verbose_name="Дедлайн", blank=True)
    list = models.ForeignKey(ToDoList, verbose_name="Список", on_delete=models.CASCADE)
    worker = models.ForeignKey(User, verbose_name="Исполнитель",
                               on_delete=models.DO_NOTHING,
                               blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"


class Notifications(models.Model):
    """
    meh docstring here is not
    """
    # I wanted to use them to notify Users of actions, that they need to know (invite to org, change of task ex.)
    to = models.ForeignKey(User, verbose_name="Кому", on_delete=models.CASCADE)
    what = models.CharField(verbose_name="Тема", max_length=300)
    text = models.TextField(verbose_name="Текст", blank=True)
    task = models.ForeignKey(Task, verbose_name="Задание", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.what

    class Meta:
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"


@receiver(post_save, sender=Organization)
def get_org_tag(sender, instance, created, **kwargs):
    if created:
        instance.tag = ctypes.c_size_t(hash(f'{instance.name}id{instance.pk}')).value
        instance.save()
