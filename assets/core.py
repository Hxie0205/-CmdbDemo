#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "xh"
# Date: 2019/11/21
import json
from . import models
from django.core.exceptions import ObjectDoesNotExist


class Asset(object):
    def __init__(self, request):
        self.requset = request
        self.mandatory_fields = ['sn', 'asset_id', 'asset_type']  # 客户端汇报过来的数据必须携带这几个字段
        self.field_sets = {
            'asset': ['manufactory'],
            'server': ['model', 'cpu_count', 'cpu_core_count', 'cpu_model', 'raid_type', 'os_type', 'os_distribution',
                       'os_release'],
            'networkdevice': []
        }
        self.response = {
            "error": [],
            "info": [],
            "warning": [],
        }

    def response_msg(self, msg_type, key, msg):
        if msg_type in self.response:
            self.response[msg_type].append({key: msg})
        else:
            raise ValueError

    def mandatory_check(self, data, only_check_sn=False):
        for filed in self.mandatory_fields:
            if filed not in data:
                self.response_msg("error", "MandatoryCheckFailed",
                                  "The field [%s] is mandatory and not provided in your reporting data" % filed)
        else:
            if self.response["error"]: return False
        try:
            if not only_check_sn:
                self.asset_obj = models.Asset.objects.get(id=int(data['asset_id']), sn=data['sn'])
            else:
                self.asset_obj = models.Asset.objects.get(sn=data['sn'])
        except ObjectDoesNotExist as e:
            self.response_msg('error', 'AssetDataInvalid',
                              "Cannot find asset object in DB using asset id[%s] and sn[%s]" % (
                                  data["asset_id"], data["sn"]))
            self.waiting_approval = True
            return False

    def get_asset_id_by_sn(self):
        data = self.requset.POST.get("asset_data")
        if data:
            try:
                data = json.loads(data)
                if self.mandatory_check(data, only_check_sn=True):  # 条件为真说你该条资产已存在，只需要给客户端返回一个asset_id
                    response = {"asset_id": self.asset_obj.id}
                else:
                    if hasattr(self, "waiting_approval"):
                        response = {'need_aproval': "this is new asset,need IT admin approval to create new asset"}
                        self.clean_data = data
                        self.save_new_asset_to_approval_zone()
                        print(response)
                    else:
                        respone = self.response

            except ValueError as e:
                print(e)
                self.response_msg('error', 'AssetDataInvalid', str(e))
        else:
            self.response_msg('error', 'AssetDataInvalid', "The reported asset data is not valid or provided")
            response = self.response
        return response

    def save_new_asset_to_approval_zone(self):
        '''是新资产就存在待审批的临时资产表中'''
        asset_sn = self.clean_data.get("sn")
        asset_already_in_approval_zone = models.NewAssetApprovalZone.objects.get_or_create(
            sn=asset_sn,
            data=json.dumps(self.clean_data),
            manufactory=self.clean_data.get("manufactory"),
            model=self.clean_data.get('model'),
            asset_type=self.clean_data.get('asset_type'),
            ram_size=self.clean_data.get('ram_size'),
            cpu_model=self.clean_data.get('cpu_model'),
            cpu_count=self.clean_data.get('cpu_count'),
            cpu_core_count=self.clean_data.get('cpu_core_count'),
            os_distribution=self.clean_data.get('os_distribution'),
            os_release=self.clean_data.get('os_release'),
            os_type=self.clean_data.get('os_type'),
        )
        return True

    def data_is_valid_without_id(self):
        '''审批资产入库，首先在在Asset生成一条记录，取到asset id'''
        data = self.requset.POST.get('asset_data')
        if data:
            try:
                data = json.loads(data)
                asset_obj = models.Asset.objects.get_or_create(sn=data.get('sn'), name=data.get('sn'))
                data['asset_id'] = asset_obj[0].id
                self.mandatory_check(data)
                self.clean_data = data
                if not self.response["error"]:
                    return True
            except ValueError as e:
                self.response_msg('error', 'AssetDataInvalid', str(e))
        else:
            self.response_msg('error', 'AssetDataInvalid', "The reported asset data is not valid or provided")

    def __is_new_asset(self):
        '''做一个创建的资产的分发,'''
        if not hasattr(self.asset_obj, self.clean_data['asset_type']):
            return True
        else:
            return False

    def data_inject(self):
        if self.__is_new_asset():
            print('\033[32;1m---即将创建新资产----\033[0m')
            self.create_asset()
        else:
            print('\033[33;1m---asset already exist ,going to update----\033[0m')


    def create_asset(self):
        func = getattr(self, '_create_%s' % self.clean_data['asset_type'])
        create_obj = func()

    def __verify_field(self, data_set, filed_key, data_type, require=True):
        field_var = data_set.get(filed_key)
        if filed_key is not None:
            try:
                data_set[filed_key] = data_type(field_var)
            except ValueError as e:
                self.response_msg('error', 'InvalidField',
                                  "The field [%s]'s data type is invalid, the correct data type should be [%s] " % (
                                      filed_key, data_type))
        elif require == True:
            self.response_msg("error", 'LackOfField',
                              "The field [%s] has no value provided in your reporting data [%s]" % (
                              filed_key, data_set))

    def _create_server(self):
        self.__create_server_info()
        self.__create_or_update_manufactory()
        self.__create_cpu_component()
        self.__create_disk_component()
        self.__create_nic_component()
        self.__create_ram_component()

    def __create_server_info(self, igone_errs=False):
        try:
            self.__verify_field(self.clean_data, 'model', str)
            if not len(self.response["error"]) or igone_errs == True:
                data_set = {
                    "asset_id": self.asset_obj.id,
                    'raid_type': self.clean_data.get('raid_type'),
                    'model': self.clean_data.get('model'),
                    'os_type': self.clean_data.get('os_type'),
                    'os_distribution': self.clean_data.get('os_distribution'),
                    'os_release': self.clean_data.get('os_release')
                }
            obj = models.Server(**data_set)
            obj.save()
            return obj
        except Exception as e:
            self.response_msg('error', 'ObjectCreationException', 'Object [server] %s' % str(e))

    def __create_or_update_manufactory(self, igone_errs=False):
        try:
            self.__verify_field(self.clean_data, 'manufactory', str)
            if not len(self.response['error']) or igone_errs == True:
                manufactory = self.clean_data.get["manufactory"]
                obj_exist = models.Manufactory.objects.filter(manufactory=manufactory)
                if obj_exist:
                    obj = obj_exist
                else:
                    obj = models.Manufactory(manufactory=manufactory)
                    obj.save()
                self.asset_obj.manufactory = obj
                self.asset_obj.save()
        except Exception as e:
            self.response_msg('error', "ObjectCreateException", 'Object [manufactory] %s' % str(e))

    def __create_cpu_component(self, igone_errs=False):
        try:
            self.__verify_field(self.clean_data, 'cpu_model', str)
            self.__verify_field(self.clean_data, 'cpu_count', int)
            self.__verify_field(self.clean_data, 'cpu_core_count', int)
            if not len(self.response['error']) or igone_errs == True:
                data_set = {
                    "cpu_model": self.clean_data.get('cpu_model'),
                    "cpu_count": self.clean_data.get("cpu_count"),
                    "cpu_core_count": self.clean_data.get('cpu_core_count')
                }
                obj = models.CPU(**data_set)
                obj.save()
                log_msg = "Asset[%s] --> has added new [cpu] component with data [%s]" % (self.asset_obj, data_set)
                self.response_msg('info', 'NewComponentAdded', log_msg)
        except Exception as e:
            self.response_msg('error', 'ObjectCreationException', 'Object [cpu] %s' % str(e))

    def __create_disk_component(self, igone_errs=False):
        disk_info = self.clean_data.get('physical_disk')
        if disk_info:
            for disk_item in disk_info:
                try:
                    self.__verify_field(disk_item, "solt", str)
                    self.__verify_field(disk_item, "capacity", float)
                    self.__verify_field(disk_item, "iface_type", str)
                    self.__verify_field(disk_item, "model", str)
                    if not len(self.response['error']) or igone_errs:
                        data_set = {
                            "asset_id": self.asset_obj.id,
                            "sn": disk_item.get.get("sn"),
                            "solt": disk_item.get("solt"),
                            "capacity": disk_item.get('capacity'),
                            "iface_type": disk_item.get('iface_type'),
                            "model": disk_item.get('model'),
                            "manufactory": disk_item.get('manufactory')
                        }
                        obj = models.Disk(**data_set)
                        obj.save()
                except Exception as e:
                    self.response_msg('error', 'ObjectCreationException', 'Object [disk] %s' % str(e))
        else:
            self.response_msg('error', 'LackOfData', 'Disk info is not provied in your reporting data')

    def __create_nic_component(self, igone_errs=False):
        nic_info = self.clean_data.get("nic")
        if nic_info:
            for nic_item in nic_info:
                try:
                    self.__verify_field(nic_item, "macaddress", str)
                    if not len(self.response['error']):
                        data_set = {
                            'asset_id': self.asset_obj.id,
                            'name': nic_item.get('name'),
                            'sn': nic_item.get('sn'),
                            'macaddress': nic_item.get('macaddress'),
                            'ipaddress': nic_item.get('ipaddress'),
                            'bonding': nic_item.get('bonding'),
                            'model': nic_item.get('model'),
                            'netmask': nic_item.get('netmask'),
                        }

                        obj = models.NIC(**data_set)
                        obj.save()
                except Exception as e:
                    self.response_msg('error','ObjectCreationException','Object [nic] %s' % str(e))
        else:
            self.response_msg('error','LackOfData','NIC info is not provied in your reporting data')

    def __create_ram_component(self):
        ram_info = self.clean_data.get('ram')
        if ram_info:
            for ram_item in ram_info:
                try:
                    self.__verify_field(ram_item, "capactiy", int)
                    if not len(self.response['error']):
                        data_set = {
                            'asset_id': self.asset_obj.id,
                            'slot': ram_item.get('slot'),
                            'sn': ram_item.get('sn'),
                            'capacity': ram_item.get("capacity"),
                            'model': ram_item.get('model')
                        }
                        obj = models.RAM(**data_set)
                        obj.save()
                except Exception as e:
                    self.response_msg('error', 'ObjectCreationException', 'Object [ram] %s' % str(e))
        else:
            self.response_msg('error', 'LackOfData', 'RAM info is not provied in your reporting data')

