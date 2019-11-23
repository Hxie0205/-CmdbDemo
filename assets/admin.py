from django.contrib import admin

# Register your models here.
from . import models
from django.http import HttpResponseRedirect


class AssetAdmin(admin.ModelAdmin):
    list_display = ("id", "sn", "create_date")
    filter_horizontal = ("tags",) #多对多的多选


class NewAssetApprovalZoneAdmin(admin.ModelAdmin):
    list_display = ['id', 'sn', 'asset_type', 'manufactory', 'model', 'ram_size', 'cpu_model', 'date', 'approved',
                    'approved_by', 'approved_date']
    list_filter = ('asset_type', 'date')
    actions = ["approve_selected_rows"]

    def approve_selected_rows(self, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        print("list--", selected)
        return HttpResponseRedirect("/asset/new_assets/approval/?ids=%s" % (",".join(selected)))

# for table in models.__all__:
#     admin.site.register(getattr(models, table))
admin.site.register(models.Asset,AssetAdmin)
admin.site.register(models.BusinessUnit)
admin.site.register(models.IDC)
admin.site.register(models.Server)
admin.site.register(models.NetworkDevice)
admin.site.register(models.SecurityDevice)
admin.site.register(models.Disk)
admin.site.register(models.NIC)
admin.site.register(models.CPU)
admin.site.register(models.RAM)
admin.site.register(models.RaidAdaptor)
admin.site.register(models.Contract)
admin.site.register(models.UserProfile)
admin.site.register(models.EventLog)
admin.site.register(models.Manufactory)
admin.site.register(models.Tag)
admin.site.register(models.NewAssetApprovalZone, NewAssetApprovalZoneAdmin)
