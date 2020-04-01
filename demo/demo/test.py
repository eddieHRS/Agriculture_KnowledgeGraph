from django.shortcuts import render
import json
import os
from toolkit.img_match import get_similar_entity
from toolkit.pre_load import neo_con
from Model.Test_class import Test



def test(request):
    cp_id = request.GET["cp_id"]
    print(cp_id)
    t = Test()
    t.init_by_cp_id(cp_id)