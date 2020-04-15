from django.shortcuts import render
import json
import os
from toolkit.img_match import get_similar_entity
from toolkit.pre_load import neo_con
from toolkit.pre_load import my_sql

class Test():
    leaf_node = []  # 初始化的叶子节点的node_id []
    mcon_node = []  # 所有的具有mcon关系的左节点的node_id []
    all_node  = {}  # 所有的节点的所有信息 {}
    corr_node = []  # 会的知识点的node_id []
    unknown_node = [] #没有测试过的知识点 []
    wron_node = []  # 不会的知识点的node_id []
    question  = {}  # 该章节下的所有题目 {}
    cp_id = 1

    def __init__(self):
        print("create Test class ...")

    # 初始化工作
    def init_by_cp_id(self, cp_id):
        print("start init...")
        self.cp_id = cp_id
        self.corr_node = []
        self.wron_node = []
        self.unknown_node = []
        self.leaf_node = self.unwrapNeo4j(neo_con.getLeafByCpId(cp_id))
        self.mcon_node = list(set(self.unwrapNeo4j(neo_con.getMconByCpId(cp_id))))
        self.all_node  = self.unwrapNeo4j(neo_con.getAllnodeByCpId(cp_id), onlynodeid=False)
        self.question  = self.unwrapMysql(my_sql.selectQbyCpid(cp_id))
        print(self.corr_node)

    #把neo4j返回的格式的数据 注意是返回的是n
    # onlynodeid 为True的话 ，只解析出 node_id 的[]
    # 解析成字典形式{node_id:[title,detail]}
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
               'corr_node': self.corr_node, 'wron_node': self.wron_node, 'question': self.question, 'unknown_node':self.unknown_node}
        return ret

    #显示页面需要的 nodes 和 edges数组
    def getnodesAndEdges(self):
        ret = {
            'nodes': [],
            'edges':[]
        }
        for num, v in self.all_node.items():
            ret['nodes'].append(
                {
                    'data':{
                        'id': num,
                        'title': v[0],
                        'detail': v[1],
                        'type': self.checkNodeType(num),
                    }
                }
            )
        #构造edges
        rea = ['con', 'mcon', 'pre', 'apre', 'opre']
        for r in rea:
            pair_nodes = neo_con.findNodeByRea(r, self.cp_id)
            for pn in pair_nodes:
                print(pn)
                ret['edges'].append(
                    {
                        'data': {
                            'id': pn['n1.num']+pn['n2.num'],
                            'type': r,
                            'source': pn['n1.num'],
                            'target': pn['n2.num'],
                        }
                    }
                )
        return ret

    def checkNodeType(self, node_id):
        type = "unknown_node"
        if node_id in self.corr_node:
            type = "corr_node"
        elif node_id in self.wron_node:
            type = "wron_node"
        return type
    #根据当前的data情况，生成选取的题目的数据
    def getQues(self):
        nid = self.find_nid()#找到第一个有题目的node_id
        print("nid:", nid)
        if nid: #如果该知识点没有对应的题目
            allQs = self.question[nid]
            allQs[0]['node_id'] = nid#增加node_id
            allQs[0]['node_detail'] = self.all_node[nid][1]
            return allQs[0]
        else:
            return None

    #找到有对应题目的node_id
    def find_nid(self):
        for n in self.leaf_node:
            if n in self.question.keys():
                self.leaf_node.remove(n)
                return n
            else:
                self.unknown_node.append(n)
                self.leaf_node.remove(n)
        return None
    # 根据传入的题目id和传入的答案更新数据状态
    def updateStatus(self, node_id, q_id, ans):
        print('inupdateStatus TestClass')
        check_result = self.check(node_id, q_id, ans)
        # print("check result:", check_result)
        if check_result:
            #该node_id测试正确的情况
            to_add_corr = self.get_chain(node_id, ['apre', 'pre', 'con'])
            print("to_add_corr")
            print(to_add_corr)
            self.corr_node = list(set(self.corr_node + to_add_corr))
            print(self.corr_node)
            for n in to_add_corr:
                if n in self.leaf_node:
                    self.leaf_node.remove(n)
        else:
            #该node_id测试不正确的情况
            to_add_wron = self.get_chain(node_id, ['opre', 'pre', 'con'])
            self.wron_node = list(set(self.wron_node + to_add_wron))
            for n in self.wron_node:
                if n in self.leaf_node:
                    self.leaf_node.remove(n)
        # 如果更新完了的时候 leaf_node为空,那么检查 mcon_node
        if not self.leaf_node:
            self.check_mcon()

    #需要修改 如果 a-mcon-mcon
    def check_mcon(self):
        print("starting check mcon...")
        print(self.mcon_node)

        for n in self.mcon_node:
            t = self.unwrapNeo4j(neo_con.getMconByNodeid(n))
            if set(t) < set(self.corr_node) and set(t) and t not in self.corr_node:
                # print("mcon add ", n)
                self.corr_node.append(n)
                print(self.corr_node)


    def check(self, node_id, q_id, ans):
        qs = self.question[node_id]
        # print("stert check answer")
        # print(node_id, ans, q_id)
        # print(qs)
        for q in qs:
            if int(q['id']) == int(q_id):
                if q['answer'] == ans:
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
                    temp = neo_con.getLIDByReaAndRId(r, n)
                    if temp:
                        t = self.unwrapNeo4j(temp)
                        append = append + t
            a = a + append
            b = append
        # print("chain")
        # print(a)
        return a