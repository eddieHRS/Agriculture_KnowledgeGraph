from py2neo import Graph, Node, Relationship, cypher, Path
import neo4j
class Neo4j():
	graph = None
	#所有的关系类型
	alltype = ['mocn', 'con', 'pre', 'apre', 'opre',]
	def __init__(self):
		print("create neo4j class ...")

	def connectDB(self):
		self.graph = Graph("http://localhost:7474", username="neo4j", password="980127")
	#answer的格式
	#[
	# 	{'id':'','title':'','detail':''},
	#    ……
	# ]

	#根据章节id确定标签之后，找出所有该标签下的所有节点
	def getAllnodeByCpId(self, cp_id):
		label = "C" + str(cp_id) + "_NODE"
		sql = "MATCH (n:" + label + ") return n;"
		answer = self.graph.run(sql).data()
		return answer

	#根据章节id确定标签之后，找出所有叶子结点
	def getLeafByCpId(self, cp_id):
		label = "C"+str(cp_id)+"_NODE"
		sql = "MATCH (n:" + label + ") where not (n)-->() return n;"
		answer = self.graph.run(sql).data()
		return answer

	#找到左节点的mcon的所有右节点
	def getMconByNodeid(self, nid):
		sql = "MATCH (n1:{num:"+nid+"} -[:RELATION {type:'mcon'}] -> n) RETURN n"
		answer = self.graph.run(sql).data()
		return answer

	#根据章节id确定标签之后，找出所有含mcon关系的结点
	def getMconByCpId(self, cp_id):
		label = "C" + str(cp_id) + "_NODE"
		sql = "MATCH (n:"+label+")-[:RELATION {type:'mcon'}] -> (n2:"+label+") RETURN n;"
		answer = self.graph.run(sql).data()
		return answer

	# 根据右节点的id和关系找到左节点的nodeid
	def getLIDByReaAndRId(self, rtype, rid):
		if rtype not in self.alltype:
			return None
		else:
			sql = "MATCH (n)-[:RELATION {type:'"+rtype+"'}] -> (n2:{num:"+rid+"}) RETURN n;"
			answer = self.graph.run(sql).data()
			return answer

	def matchItembyTitle(self, value):
		sql = "MATCH (n:Item { title: '" + str(value) + "' }) return n;"
		answer = self.graph.run(sql).data()
		return answer

	# 根据title值返回互动百科item
	def matchHudongItembyTitle(self,value):
		sql = "MATCH (n:HudongItem { title: '" + str(value) + "' }) return n;"
		try:
			answer = self.graph.run(sql).data()
		except:
			print(sql)
		return answer

	# 根据entity的名称返回关系
	def getEntityRelationbyEntity(self,value):
		answer = self.graph.run("MATCH (entity1) - [rel] -> (entity2)  WHERE entity1.title = \"" +str(value)+"\" RETURN rel,entity2").data()
		return answer

	#查找entity1及其对应的关系（与getEntityRelationbyEntity的差别就是返回值不一样）
	def findRelationByEntity(self,entity1):
		answer = self.graph.run("MATCH (n1 {title:\""+str(entity1)+"\"})- [rel] -> (n2) RETURN n1,rel,n2" ).data()
		# if(answer is None):
		# 	answer = self.graph.run("MATCH (n1:NewNode {title:\""+entity1+"\"})- [rel] -> (n2) RETURN n1,rel,n2" ).data()
		return answer

	#查找entity2及其对应的关系
	def findRelationByEntity2(self,entity1):
		answer = self.graph.run("MATCH (n1)- [rel] -> (n2 {title:\""+str(entity1)+"\"}) RETURN n1,rel,n2" ).data()

		# if(answer is None):
		# 	answer = self.graph.run("MATCH (n1)- [rel] -> (n2:NewNode {title:\""+entity1+"\"}) RETURN n1,rel,n2" ).data()
		return answer

	#根据entity1和关系查找enitty2
	def findOtherEntities(self,entity,relation):
		answer = self.graph.run("MATCH (n1 {title:\"" + str(entity) + "\"})- [rel {type:\""+str(relation)+"\"}] -> (n2) RETURN n1,rel,n2" ).data()
		#if(answer is None):
		#	answer = self.graph.run("MATCH (n1:NewNode {title:\"" + entity + "\"})- [rel:RELATION {type:\""+relation+"\"}] -> (n2) RETURN n1,rel,n2" ).data()

		return answer

	#根据entity2和关系查找enitty1
	def findOtherEntities2(self,entity,relation):
		answer = self.graph.run("MATCH (n1)- [rel {type:\""+str(relation)+"\"}] -> (n2 {title:\"" + str(entity) + "\"}) RETURN n1,rel,n2" ).data()
		#if(answer is None):
		#	answer = self.graph.run("MATCH (n1)- [rel:RELATION {type:\""+relation+"\"}] -> (n2:NewNode {title:\"" + entity + "\"}) RETURN n1,rel,n2" ).data()

		return answer

	#根据两个实体查询它们之间的最短路径
	def findRelationByEntities(self,entity1,entity2):
		answer = self.graph.run("MATCH (p1:HudongItem {title:\"" + str(entity1) + "\"}),(p2:HudongItem{title:\""+str(entity2)+"\"}),p=shortestpath((p1)-[rel:RELATION*]-(p2)) RETURN rel").evaluate()
		#answer = self.graph.run("MATCH (p1:HudongItem {title:\"" + entity1 + "\"})-[rel:RELATION]-(p2:HudongItem{title:\""+entity2+"\"}) RETURN p1,p2").data()
		
		if(answer is None):	
			answer = self.graph.run("MATCH (p1:HudongItem {title:\"" + str(entity1) + "\"}),(p2:NewNode {title:\""+str(entity2)+"\"}),p=shortestpath((p1)-[rel:RELATION*]-(p2)) RETURN p").evaluate()
		if(answer is None):
			answer = self.graph.run("MATCH (p1:NewNode {title:\"" + str(entity1) + "\"}),(p2:HudongItem{title:\""+str(entity2)+"\"}),p=shortestpath((p1)-[rel:RELATION*]-(p2)) RETURN p").evaluate()
		if(answer is None):
			answer = self.graph.run("MATCH (p1:NewNode {title:\"" + str(entity1) + "\"}),(p2:NewNode {title:\""+str(entity2)+"\"}),p=shortestpath((p1)-[rel:RELATION*]-(p2)) RETURN p").evaluate()
		#answer = self.graph.data("MATCH (n1:HudongItem {title:\"" + entity1 + "\"})- [rel] -> (n2:HudongItem{title:\""+entity2+"\"}) RETURN n1,rel,n2" )
		#if(answer is None):
		#	answer = self.graph.data("MATCH (n1:HudongItem {title:\"" + entity1 + "\"})- [rel] -> (n2:NewNode{title:\""+entity2+"\"}) RETURN n1,rel,n2" )
		#if(answer is None):
		#	answer = self.graph.data("MATCH (n1:NewNode {title:\"" + entity1 + "\"})- [rel] -> (n2:HudongItem{title:\""+entity2+"\"}) RETURN n1,rel,n2" )
		#if(answer is None):
		#	answer = self.graph.data("MATCH (n1:NewNode {title:\"" + entity1 + "\"})- [rel] -> (n2:NewNode{title:\""+entity2+"\"}) RETURN n1,rel,n2" )
		relationDict = []
		if(answer is not None):
			for x in answer:
				tmp = {}
				start_node = x.start_node
				end_node = x.end_node
				tmp['n1'] = start_node
				tmp['n2'] = end_node
				tmp['rel'] = x
				relationDict.append(tmp)		
		return relationDict

	#查询数据库中是否有对应的实体-关系匹配
	def findEntityRelation(self,entity1,relation,entity2):
		answer = self.graph.run("MATCH (n1:HudongItem {title:\"" + str(entity1) + "\"})- [rel:RELATION {type:\""+str(relation)+"\"}] -> (n2:HudongItem{title:\""+entity2+"\"}) RETURN n1,rel,n2" ).data()
		if(answer is None):
			answer = self.graph.run("MATCH (n1:HudongItem {title:\"" + str(entity1) + "\"})- [rel:RELATION {type:\""+str(relation)+"\"}] -> (n2:NewNode{title:\""+entity2+"\"}) RETURN n1,rel,n2" ).data()
		if(answer is None):
			answer = self.graph.run("MATCH (n1:NewNode {title:\"" + str(entity1) + "\"})- [rel:RELATION {type:\""+str(relation)+"\"}] -> (n2:HudongItem{title:\""+entity2+"\"}) RETURN n1,rel,n2" ).data()
		if(answer is None):
			answer = self.graph.run("MATCH (n1:NewNode {title:\"" + str(entity1) + "\"})- [rel:RELATION {type:\""+str(relation)+"\"}] -> (n2:NewNode{title:\""+entity2+"\"}) RETURN n1,rel,n2" ).data()

		return answer

