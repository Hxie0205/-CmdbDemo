from django.shortcuts import render
import json
from .core import Asset
from . import models
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
@csrf_exempt
def asset_with_no_asset_id(request):
    if request.method == "POST":
        ass_handler = Asset(request)
        res = ass_handler.get_asset_id_by_sn()
        return HttpResponse(json.dumps(res, ensure_ascii=False))


def new_assets_approval(request):
    if request.method == "POST":
        request.POST = request.POST.copy()
        approved_asset_list = request.POST.get("approved_asset_list")
        approved_asset_list_objs = models.NewAssetApprovalZone.objects.filter(id__in=approved_asset_list)
        response_dict = {}
        for obj in approved_asset_list_objs:
            request.POST['asset_data'] = obj.data
            ass_handler = Asset(request)
            if ass_handler.data_is_valid_without_id():
                ass_handler.data_inject()
                obj.approved = True
                obj.save()
            response_dict[obj.id] = ass_handler.response
        return render(request, 'assets/new_assets_approval.html', {'response_dic': response_dict})
    ids = request.GET.get("ids")
    ids_list = ids.split(",")
    new_assets = models.NewAssetApprovalZone.objects.filter(id__in=ids_list)
    return render(request, "assets/new_assets_approval.html", {"new_assets": new_assets})
