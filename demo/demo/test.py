from django.shortcuts import render
import json
import os
from toolkit.img_match import get_similar_entity
from toolkit.pre_load import neo_con
from Model.Test_class import Test
#
# ret['cp_id'] = self.cp_id
#         ret['leaf_node'] = self.leaf_node
#         ret['mcon_node'] = self.mcon_node
#         ret['all_node'] = self.all_node
#         ret['corr_node'] = self.corr_node
#         ret['wron_node'] = self.wron_node
#         ret['question'] = self.question
t = Test()

def test(request):
    global t
    cp_id = request.GET["cp_id"]
    t.init_by_cp_id(cp_id)
    data = t.getQues()
    # 前端需要的数据包括 当前题目的所有信息
    print(data)
    # {'id': 8, 'cp_id': 1, 'q_stem': '71014TE
# ST', 'choice': 'C', 'answer': 'C', 'node
    # # _id': '71014'}
    return render(request, "mytest.html", data)

#接收前端返回的题目id和答案，更新数据
def receive_update(request):
    node_id = request.GET['node_id']
    question_id = request.GET['q_id']
    answer = request.GET['ans']
    print("receive_update的数据:node_id,q_id,ans")
    print(node_id, question_id, answer)
    global t
    t.updateStatus(node_id, question_id, answer)
    data = t.getQues()
    print("getQues in receive_update:")
    print(data)
    if data is None:
        # t.check_mcon()#所有能测试的题目全部测试完，需要对mcon更新
        print(t.getnodesAndEdges())
        return render(request, "testresult.html", {'ret': json.dumps(t.getnodesAndEdges())})
    else:
        return render(request, "mytest.html", data)
