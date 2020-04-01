from django.shortcuts import render
import json
import os
from toolkit.img_match import get_similar_entity
from toolkit.pre_load import neo_con
from toolkit.pre_load import my_sql

class Test():
    leaf_node = None  # 初始化的叶子节点的node_id []
    mcon_node = None  # 所有的具有mcon关系的左节点的node_id []
    all_node  = None  # 所有的节点的所有信息 {}
    corr_node = None  # 会的知识点的node_id []
    wron_node = None  # 不会的知识点的node_id []
    question  = None  # 该章节下的所有题目 {}
    cp_id = None

    def __init__(self):
        print("create Test class ...")

    # 初始化工作
    def init_by_cp_id(self, cp_id):
        print("start init...")
        self.cp_id = cp_id
        self.leaf_node = self.unwrapNeo4j(neo_con.getLeafByCpId(cp_id))
        self.mcon_node = self.unwrapNeo4j(neo_con.getMconByCpId(cp_id))
        self.all_node  = self.unwrapNeo4j(neo_con.getAllnodeByCpId(cp_id), onlynodeid=False)
        self.question  = self.unwrapMysql(my_sql.selectQbyCpid(cp_id))
        # print(self.leaf_node)
        # print(self.question)

    #把neo4j返回的格式的数据 注意是返回的是n
    # onlynodeid 为True的话 ，只解析出 node_id 的[]
    # 解析成字典形式{node_id:(title,detail)}
    def unwrapNeo4j(self, data, onlynodeid = True):
        if onlynodeid:
            ret = []
            for i in data:
                ret.append(i['n']['num'])
        else:
            ret = {}
            for i in data:
                ret[str(i['n']['num'])] = [i['n']['title'], i['n']['detail']]
        return ret

    #把mysql返回的题目数据转成 {node_id:[{id: cp_id: q_stem: choice: answer:}]}
    def unwrapMysql(self, data):
        ret = {}
        for i in data:
            t = {
                'id': i[0],
                'cp_id': i[2],
                'q_stem': i[3],
                'choice': i[4],
                'answer': i[5]
            }
            if str(i[1]) in ret.keys():
                ret[str(i[1])].append(t)
            else:
                ret[str(i[1])] = [t]
        return ret

    def getData(self):
        ret = {'cp_id': self.cp_id, 'leaf_node': self.leaf_node, 'mcon_node': self.mcon_node, 'all_node': self.all_node,
               'corr_node': self.corr_node, 'wron_node': self.wron_node, 'question': self.question}
        return ret

    #根据当前的data情况，生成选取的题目的数据
    def getQues(self):
        if not self.leaf_node:
            return None
        else:
            # print(self.question)
            nid = self.leaf_node[0]
            allQs = self.question[nid]
            if allQs: #如果该知识点没有对应的题目
                allQs[0]['node_id'] = nid#增加node_id
                allQs[0]['node_detail'] = self.all_node[nid][1]
                print("生成的题目：")
                print(allQs[0])
                return allQs[0]
            else:
                a = self.leaf_node[0]
                self.corr_node.append(a)
                self.leaf_node.remove(a)
                self.getQues()

    # 根据传入的题目id和传入的答案更新数据状态
    def updateStatus(self, node_id, q_id, ans):
        check_result = self.check(node_id, q_id, ans)
        if check_result:
            #该node_id测试正确的情况
            to_add_corr = [node_id] + self.get_chain(node_id, ['apre', 'pre', 'con'])
            self.corr_node = self.corr_node + to_add_corr
            for n in to_add_corr:
                if n in self.leaf_node:
                    self.leaf_node.remove(n)
        else:
            #该node_id测试不正确的情况
            to_add_wron = [node_id] + self.get_chain(node_id, ['opre', 'pre', 'con'])
            self.wron_node = self.wron_node + to_add_wron
            for n in self.wron_node:
                if n in self.leaf_node:
                    self.leaf_node.remove(n)
        # 如果更新完了的时候 leaf_node为空,那么检查 mcon_node
        if not self.leaf_node:
            for n in self.mcon_node:
                t = self.unwrapNeo4j(neo_con.get_mcon(n))
                if set(t) < set(self.corr_node) and set(t):
                    self.corr_node.append(n)

    def check(self, node_id, q_id, ans):
        for q in self.question[node_id]:
            if q['id'] == q_id:
                if q['ans'] == ans:
                    return True
        return False

    #从node开始往前，满足rel_list中关系的所有节点
    def get_chain(self, node_id, rel_list):
        a = [node_id]
        b = [node_id]
        while b:
            append = []
            for n in b:
                for r in rel_list:
                    t = self.unwrapNeo4j(neo_con.getLIDByReaAndRId(r, n))
                    append = append + t
            a = a + append
            b = append
        return a