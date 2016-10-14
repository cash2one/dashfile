# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [app_label]'
# into your database.
from __future__ import unicode_literals

from django.db import models


class AuthGroup(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    name = models.CharField(unique=True, max_length=80)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    group_id = models.IntegerField()
    permission_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'


class AuthPermission(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    name = models.CharField(max_length=50)
    content_type_id = models.IntegerField()
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'


class AuthUser(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField()
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=30)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=75)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    user_id = models.IntegerField()
    group_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'auth_user_groups'


class AuthUserUserPermissions(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    user_id = models.IntegerField()
    permission_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'


class DjangoAdminLog(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.IntegerField()
    change_message = models.TextField()
    content_type_id = models.IntegerField(blank=True, null=True)
    user_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    name = models.CharField(max_length=100)
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'


class DjangoMigrations(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class InsHistory(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    timestamp = models.DateTimeField()
    instance_id = models.CharField(max_length=128)
    cluster = models.CharField(max_length=16)
    command = models.CharField(max_length=256)
    externtion_port_begin = models.IntegerField()
    externtion_port_count = models.IntegerField()
    state = models.CharField(max_length=16)
    dynamic_data = models.CharField(max_length=5120)
    hostname = models.CharField(max_length=32)
    heart_beat = models.IntegerField()
    freeze = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'ins_history'


class InstanceFault(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    time = models.CharField(max_length=20)
    room = models.CharField(max_length=20)
    model = models.CharField(max_length=32)
    type = models.CharField(max_length=32)
    num = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'instance_fault'


class InstanceFaultNs(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    time = models.CharField(max_length=20)
    room = models.CharField(max_length=20)
    type = models.CharField(max_length=32)
    num = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'instance_fault_ns'


class KpiInstance(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    stat_time = models.CharField(max_length=20)
    cluster = models.CharField(max_length=20)
    per_24 = models.FloatField()
    per_day_30 = models.FloatField()
    per_latest_30 = models.FloatField()

    class Meta:
        managed = False
        db_table = 'kpi_instance'


class KpiMachine(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    stat_time = models.CharField(max_length=20)
    cluster = models.CharField(max_length=20)
    latest_24 = models.FloatField()
    day_30 = models.FloatField()
    latest_30 = models.FloatField()

    class Meta:
        managed = False
        db_table = 'kpi_machine'


class MacHistory(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    timestamp = models.DateTimeField()
    cluster = models.CharField(max_length=16)
    hostname = models.CharField(max_length=32)
    label = models.CharField(max_length=128, blank=True)
    available = models.IntegerField()
    type1 = models.CharField(max_length=32, blank=True)
    type2 = models.CharField(max_length=32, blank=True)
    type3 = models.CharField(max_length=32, blank=True)
    type4 = models.CharField(max_length=32, blank=True)
    type5 = models.CharField(max_length=32, blank=True)

    class Meta:
        managed = False
        db_table = 'mac_history'


class NsTotal(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    time = models.CharField(max_length=20)
    room = models.CharField(max_length=20)
    total = models.IntegerField()
    on_ns = models.IntegerField()
    live_rate = models.FloatField()

    class Meta:
        managed = False
        db_table = 'ns_total'


class StatAgent(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    stat_time = models.CharField(max_length=20, blank=True)
    cluster = models.CharField(max_length=20, blank=True)
    all_machine = models.IntegerField(blank=True, null=True)
    all_avail_rate = models.FloatField(blank=True, null=True)
    no_hard_err_machine = models.IntegerField(blank=True, null=True)
    no_hard_err_avail_rate = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'stat_agent'


class StatInstance(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    stat_time = models.CharField(max_length=20, blank=True)
    cluster = models.CharField(max_length=20, blank=True)
    module = models.CharField(max_length=100, blank=True)
    all_instance = models.IntegerField(blank=True, null=True)
    live_rate = models.FloatField(blank=True, null=True)
    naming_instance = models.IntegerField(blank=True, null=True)
    naming_live_rate = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'stat_instance'


class StatMachine(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    stat_time = models.CharField(max_length=20, blank=True)
    cluster = models.CharField(max_length=20, blank=True)
    label = models.CharField(max_length=100, blank=True)
    all_machine = models.IntegerField(blank=True, null=True)
    online_rate = models.FloatField(blank=True, null=True)
    hard_err_rate = models.FloatField(blank=True, null=True)
    soft_err_rate = models.FloatField(blank=True, null=True)
    no_err_rate = models.FloatField(blank=True, null=True)
    no_err_running_rate = models.FloatField(blank=True, null=True)
    running_rate = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'stat_machine'


class StatMachineNew(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    stat_time = models.CharField(max_length=20, blank=True)
    cluster = models.CharField(max_length=20, blank=True)
    label = models.CharField(max_length=100, blank=True)
    all_machine = models.IntegerField(blank=True, null=True)
    online_rate = models.FloatField(blank=True, null=True)
    hard_err_rate = models.FloatField(blank=True, null=True)
    soft_err_rate = models.FloatField(blank=True, null=True)
    no_err_rate = models.FloatField(blank=True, null=True)
    no_err_running_rate = models.FloatField(blank=True, null=True)
    running_rate = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'stat_machine_new'


class YjMachine(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    stat_time = models.CharField(max_length=20)
    cluster = models.CharField(max_length=20)
    ip = models.CharField(max_length=2048)
    fix_mac = models.IntegerField()
    handling = models.IntegerField()
    not_found = models.IntegerField()
    all_ok = models.IntegerField()
    fix_ser = models.IntegerField()
    handling_onser = models.IntegerField()
    lv2cetus = models.IntegerField()
    some_ser_err = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'yj_machine'
