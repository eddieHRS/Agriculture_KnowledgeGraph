from django.shortcuts import render
import json
import os
from toolkit.img_match import get_similar_entity
from toolkit.pre_load import neo_con
from toolkit.pre_load import my_sql

class Test():

    leaf_node = set([])  # 初始化的叶子节点
    mcon_node = set([])  # 所有的具有mcon关系的左节点
    corr_node = set([])  # 会的知识点
    wron_node = set([])  # 不会的知识点
    question = None  # 该章节下的所有题目

    def __init__(self):
        print("create Test class ...")
    # 初始化工作
    def init_by_cp_id(self, cp_id):
        #根据cp_id初始化三个集合
        print("start init...")
        self.leaf_node = neo_con.getLeafByCpId(cp_id)
        self.mcon_node = neo_con.getMconByCpId(cp_id)
        self.question  = my_sql.selectQbyCpid(cp_id)
        # print(self.leaf_node)
        # print(self.mcon_node)
        print(self.question)

    def check_result(request):
        node_id = request.GET['node_id']

    # 根据当前的题目以及当前题目的状态产生下一道题目
    def next_q(curr_q, check_result):
        return