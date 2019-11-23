from django.db import models
from django.contrib.auth.models import User

__all__ = ["UserProfile", "Asset", "Server", "BusinessUnit", "SecurityDevice", "NetworkDevice", "Software", "CPU",
           "RAM", "Disk", "NIC", "RaidAdaptor","Manufactory", "Contract", "IDC", "Tag", "EventLog",
           "NewAssetApprovalZone"]
class UserProfile(User):
    ''''''
    name = models.CharField("姓名", max_length=32)
    token = models.CharField('token', max_length=128, default=None, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        super(User.Meta)
        verbose_name = '用户'
        verbose_name_plural = "用户"


class Asset(models.Model):
    '''资产信息表'''
    name = models.CharField(max_length=64, unique=True)
    asset_type_choices = (
        ('server', '服务器'),
        ('networkdevice', '网络设备'),
        ('storagedevice', '存储设备'),
        ('securitydevice', '安全设备'),
        ('securitydevice', '机房设备'),
        # ('switch', u'交换机'),
        # ('router', u'路由器'),
        # ('firewall', u'防火墙'),
        # ('storage', u'存储设备'),
        # ('NLB', u'NetScaler'),
        # ('wireless', u'无线AP'),
        ('software', '软件资产'),
        # ('others', u'其它类'),
    )
    asset_type = models.CharField(choices=asset_type_choices, max_length=64, default='server')
    business_unit = models.ForeignKey("BusinessUnit", blank=True, null=True, on_delete=models.CASCADE)
    sn = models.CharField('资产SN号', max_length=128, unique=True)
    manufactory = models.ForeignKey('Manufactory', verbose_name=u'制造商', null=True, blank=True, on_delete=models.CASCADE)
    management_ip = models.GenericIPAddressField(u'管理IP', blank=True, null=True)
    contract = models.ForeignKey('Contract', verbose_name=u'合同', null=True, blank=True, on_delete=models.CASCADE)
    trade_date = models.DateField('购买时间', null=True, blank=True)
    expire_date = models.DateField('过保修期', null=True, blank=True)
    price = models.FloatField(u'价格', null=True, blank=True)
    idc = models.ForeignKey('IDC', verbose_name='IDC机房', null=True, blank=True, on_delete=models.CASCADE)
    tags = models.ManyToManyField('Tag', blank=True)
    admin = models.ForeignKey('UserProfile', verbose_name='资产管理员', null=True, blank=True, on_delete=models.CASCADE)
    memo = models.TextField('备注', null=True, blank=True)
    create_date = models.DateTimeField(blank=True, auto_now_add=True)
    update_date = models.DateTimeField(blank=True, auto_now=True)

    class Meta:
        verbose_name = '资产总表'
        verbose_name_plural = '资产总表'

    def __str__(self):
        return '<id:%s name:%s>' % (self.id, self.name)


class Server(models.Model):
    '''服务器信息'''
    asset = models.OneToOneField(to='Asset', on_delete=models.CASCADE)
    sub_assset_type_choices = (
        (0, 'PC服务器'),
        (1, '刀片机'),
        (2, '小型机'),
    )
    sub_asset_type = models.SmallIntegerField(choices=sub_assset_type_choices, verbose_name="服务器类型", default=0)
    created_by_choices = (
        ('auto', 'Auto'),
        ('manual', 'Manual'),
    )
    created_by = models.CharField(choices=created_by_choices, max_length=32,
                                  default='auto')  # auto: auto created,   manual:created manually
    hosted_on = models.ForeignKey('self', related_name='hosted_on_server', blank=True, null=True,
                                  on_delete=models.CASCADE)  # for vitural server
    model = models.CharField(verbose_name='型号', max_length=128, null=True, blank=True)
    raid_type = models.CharField('raid类型', max_length=512, blank=True, null=True)
    os_type = models.CharField('操作系统类型', max_length=64, blank=True, null=True)
    os_distribution = models.CharField('发型版本', max_length=64, blank=True, null=True)
    os_release = models.CharField('操作系统版本', max_length=64, blank=True, null=True)

    class Meta:
        verbose_name = '服务器'
        verbose_name_plural = "服务器"
        # together = ["sn", "asset"]

    def __str__(self):
        return '%s sn:%s' % (self.asset.name, self.asset.sn)


class BusinessUnit(models.Model):
    '''业务线'''
    parent_unit = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name


class SecurityDevice(models.Model):
    '''
    安全设备表
    '''
    asset = models.OneToOneField(to='Asset', on_delete=models.CASCADE)
    sub_assset_type_choices = (
        (0, '防火墙'),
        (1, '入侵检测设备'),
        (2, '互联网网关'),
        (4, '运维审计系统'),
    )
    sub_asset_type = models.SmallIntegerField(choices=sub_assset_type_choices, verbose_name="安全设备类型", default=0)

    def __str__(self):
        return "%s" % self.asset.id


class NetworkDevice(models.Model):
    '''
    网络设备类型
    '''
    asset = models.OneToOneField(to='Asset', on_delete=models.CASCADE)
    sub_assset_type_choices = (
        (0, '路由器'),
        (1, '交换机'),
        (2, '负载均衡'),
        (4, 'VPN设备'),
    )
    sub_asset_type = models.SmallIntegerField(choices=sub_assset_type_choices, verbose_name="网络设备类型", default=0)

    vlan_ip = models.GenericIPAddressField('VlanIP', blank=True, null=True)
    intranet_ip = models.GenericIPAddressField('内网IP', blank=True, null=True)
    # sn = models.CharField(u'SN号',max_length=128,unique=True)
    # manufactory = models.CharField(verbose_name=u'制造商',max_length=128,null=True, blank=True)
    model = models.CharField('型号', max_length=128, null=True, blank=True)
    firmware = models.CharField("固件", max_length=64, blank=True, null=True)
    port_num = models.SmallIntegerField('端口个数', null=True, blank=True)
    device_detail = models.TextField('设置详细配置', null=True, blank=True)

    class Meta:
        verbose_name = '网络设备'
        verbose_name_plural = "网络设备"


class Software(models.Model):
    '''
    only save software which company purchased
    '''
    os_types_choice = (
        (0, 'OS'),
        (1, '办公\开发软件'),
        (2, '业务软件'),

    )
    license_num = models.IntegerField(verbose_name="授权数")
    # os_distribution_choices = (('windows','Windows'),
    #                            ('centos','CentOS'),
    #                            ('ubuntu', 'Ubuntu'))
    # type = models.CharField(u'系统类型', choices=os_types_choice, max_length=64,help_text=u'eg'. GNU/Linux',default=1)
    # distribution = models.CharField(u'发型版本', choices=os_distribution_choices,max_length=32,default='windows')
    version = models.CharField(u'软件/系统版本', max_length=64, help_text=u'eg. CentOS release 6.5 (Final)', unique=True)

    # language_choices = (('cn',u'中文'),
    #                     ('en',u'英文'))
    # language = models.CharField(u'系统语言',choices = language_choices, default='cn',max_length=32)
    # #version = models.CharField(u'版本号', max_length=64,help_text=u'2.6.32-431.3.1.el6.x86_64' )

    def __str__(self):
        return self.version

    class Meta:
        verbose_name = '软件/系统'
        verbose_name_plural = "软件/系统"


class CPU(models.Model):
    '''
    CPU信息表
    '''
    asset = models.OneToOneField(to='Asset', on_delete=models.CASCADE)
    cpu_model = models.CharField('CPU型号', max_length=128, blank=True)
    cpu_count = models.SmallIntegerField('物理cpu个数')
    cpu_core_count = models.SmallIntegerField('cpu核数')
    memo = models.TextField('备注', null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'CPU部件'
        verbose_name_plural = "CPU部件"

    def __str__(self):
        return self.cpu_model


class RAM(models.Model):
    '''
    内存
    '''
    asset = models.ForeignKey(to='Asset', on_delete=models.CASCADE)
    sn = models.CharField(verbose_name='SN号', max_length=128, blank=True)
    model = models.CharField('内存型号', max_length=64)
    slot = models.CharField('插槽', max_length=64)
    capacity = models.IntegerField('内存大小(MB)')
    memo = models.CharField('备注', max_length=128, blank=True, null=True)
    create_date = models.DateTimeField('创建时间', blank=True, null=True, auto_now_add=True)
    update_date = models.DateTimeField('更新时间', blank=True, null=True, )

    def __str__(self):
        return '%s:%s:%s' % (self.asset_id, self.slot, self.capacity)

    class Meta:
        verbose_name = 'RAM'
        verbose_name_plural = 'RAM'
        unique_together = ('sn', 'slot')

    auto_create_fields = ['sn', 'slot', 'model', 'capacity']


class Disk(models.Model):
    '''
    硬盘
    '''
    asset = models.ForeignKey(to='Asset', on_delete=models.CASCADE)
    sn = models.CharField('SN号', max_length=128, blank=True, null=True)
    slot = models.CharField('插槽位', max_length=64)
    manufactory = models.CharField('制造商', max_length=64, blank=True, null=True)
    model = models.CharField('磁盘型号', max_length=128, blank=True, null=True)
    capacity = models.FloatField('磁盘容量GB')
    disk_iface_choice = (
        ('SATA', 'SATA'),
        ('SAS', 'SAS'),
        ('SCSI', 'SCSI'),
        ('SSD', 'SSD'),
    )

    iface_type = models.CharField('接口类型', max_length=64, choices=disk_iface_choice, default='SATA')
    memo = models.CharField('备注', max_length=128, blank=True, null=True)
    create_date = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    update_date = models.DateTimeField(blank=True, null=True)
    auto_create_fields = ['sn', 'slot', 'manufactory', 'model', 'capacity', 'iface_type']

    class Meta:
        verbose_name = '硬盘'
        verbose_name_plural = '硬盘'
        unique_together = ('sn', 'slot')

    def __str__(self):
        return '%s:slot:%s capacity:%s' % (self.asset_id, self.slot, self.capacity)


class NIC(models.Model):
    '''
    网卡设备
    '''

    asset = models.ForeignKey(to='Asset', on_delete=models.CASCADE)
    name = models.CharField('网卡名', max_length=64, blank=True, null=True)
    sn = models.CharField('SN号', max_length=128, blank=True, null=True)
    model = models.CharField('网卡型号', max_length=128, blank=True, null=True)
    macaddress = models.CharField('MAC', max_length=64, unique=True)
    ipaddress = models.GenericIPAddressField('IP', blank=True, null=True)
    netmask = models.CharField(max_length=64, blank=True, null=True)
    bonding = models.CharField(max_length=64, blank=True, null=True)
    memo = models.CharField('备注', max_length=128, blank=True, null=True)
    create_date = models.DateTimeField(blank=True, auto_now_add=True)
    update_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '%s:%s' % (self.asset_id, self.macaddress)

    class Meta:
        verbose_name = '网卡'
        verbose_name_plural = "网卡"
        # unique_together = ("asset_id", "slot")
        # unique_together = ("asset", "macaddress")

    auto_create_fields = ['name', 'sn', 'model', 'macaddress', 'ipaddress', 'netmask', 'bonding']


class RaidAdaptor(models.Model):
    asset = models.ForeignKey('Asset', on_delete=models.CASCADE)
    name = models.CharField('raid卡名', max_length=64, blank=True, null=True)
    sn = models.CharField('SN号', max_length=128, blank=True, null=True)
    slot = models.CharField('插口', max_length=64)
    model = models.CharField('型号', max_length=64, blank=True, null=True)
    memo = models.TextField('备注', blank=True, null=True)
    create_date = models.DateTimeField(blank=True, auto_now_add=True)
    update_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ("asset", "slot")


class Manufactory(models.Model):
    manufactory = models.CharField('厂商名称', max_length=64, unique=True)
    support_num = models.CharField('支持电话', max_length=30, blank=True)
    memo = models.CharField('备注', max_length=128, blank=True)

    def __str__(self):
        return self.manufactory

    class Meta:
        verbose_name = '厂商'
        verbose_name_plural = "厂商"


class Contract(models.Model):
    sn = models.CharField('合同号', max_length=128, unique=True)
    name = models.CharField('合同名称', max_length=64)
    memo = models.TextField('备注', blank=True, null=True)
    price = models.IntegerField('合同金额')
    detail = models.TextField('合同详细', blank=True, null=True)
    start_date = models.DateField(blank=True)
    end_date = models.DateField(blank=True)
    license_num = models.IntegerField('license数量', blank=True)
    create_date = models.DateField(auto_now_add=True)
    update_date = models.DateField(auto_now=True)

    class Meta:
        verbose_name = '合同'
        verbose_name_plural = "合同"

    def __str__(self):
        return self.name


class IDC(models.Model):
    name = models.CharField(u'机房名称', max_length=64, unique=True)
    memo = models.CharField(u'备注', max_length=128, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '机房'
        verbose_name_plural = "机房"


class Tag(models.Model):
    name = models.CharField('Tag name', max_length=32, unique=True)
    creater = models.ForeignKey(to='UserProfile', on_delete=models.CASCADE)
    create_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name


class EventLog(models.Model):
    name = models.CharField(u'事件名称', max_length=100)
    event_type_choices = (
        (1, '硬件变更'),
        (2, '新增配件'),
        (3, '设备下线'),
        (4, '设备上线'),
        (5, '定期维护'),
        (6, '业务上线\更新\变更'),
        (7, '其它'),
    )
    event_type = models.SmallIntegerField(u'事件类型', choices=event_type_choices)
    asset = models.ForeignKey(to='Asset', on_delete=models.CASCADE)
    component = models.CharField('事件子项', max_length=255, blank=True, null=True)
    detail = models.TextField('事件详情')
    date = models.DateTimeField('事件时间', auto_now_add=True)
    user = models.ForeignKey('UserProfile', verbose_name='事件源', on_delete=models.CASCADE)
    memo = models.TextField('备注', blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '事件记录'
        verbose_name_plural = "事件记录"


class NewAssetApprovalZone(models.Model):
    sn = models.CharField(u'资产SN号', max_length=128, unique=True)
    asset_type_choices = (
        ('server', u'服务器'),
        ('switch', u'交换机'),
        ('router', u'路由器'),
        ('firewall', u'防火墙'),
        ('storage', u'存储设备'),
        ('NLB', u'NetScaler'),
        ('wireless', u'无线AP'),
        ('software', u'软件资产'),
        ('others', u'其它类'),
    )
    asset_type = models.CharField(choices=asset_type_choices, max_length=64, blank=True, null=True)
    manufactory = models.CharField(max_length=64, blank=True, null=True)
    model = models.CharField(max_length=128, blank=True, null=True)
    ram_size = models.IntegerField(blank=True, null=True)
    cpu_model = models.CharField(max_length=128, blank=True, null=True)
    cpu_count = models.IntegerField(blank=True, null=True)
    cpu_core_count = models.IntegerField(blank=True, null=True)
    os_distribution = models.CharField(max_length=64, blank=True, null=True)
    os_type = models.CharField(max_length=64, blank=True, null=True)
    os_release = models.CharField(max_length=64, blank=True, null=True)
    data = models.TextField(u'资产数据')
    date = models.DateTimeField(u'汇报日期', auto_now_add=True)
    approved = models.BooleanField(u'已批准', default=False)
    approved_by = models.ForeignKey('UserProfile', verbose_name='批准人', blank=True, null=True, on_delete=models.CASCADE)
    approved_date = models.DateTimeField(u'批准日期', blank=True, null=True)

    def __str__(self):
        return self.sn

    class Meta:
        verbose_name = '新上线待批准资产'
        verbose_name_plural = "新上线待批准资产"
