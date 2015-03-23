'''
Created on Mar 8, 2015

@author: root
'''
from base import APIHandler
from tornado_letv.tornado_basic_auth import require_basic_auth
from tornado.web import asynchronous
from componentNode.nodeOpers import NodeOpers


@require_basic_auth
class Node_Handler(APIHandler):
    
    node_opers = NodeOpers()
    
    def post(self):
        '''
        function: add component node to cluster
        url example: curl --user root:root -d "clusterName=jetty_cluster&dataNodeIp=192.168.116.129&dataNodeName=jetty_cluster_node_2[&dataNodeExternalPort=**]" "http://localhost:8888/cluster/node"
        '''
        requestParam = self.get_all_arguments()
        result = self.node_opers.createNode(requestParam)
        self.finish(result)


@require_basic_auth
class Node_Start_Handler(APIHandler):
    
    node_opers = NodeOpers()
    
    @asynchronous
    def post(self):
        '''
        function: start node
        url example: curl --user root:root -d "" "http://localhost:8888/node/start"
        '''
        result = self.node_opers.startNode()
        self.finish(result)


@require_basic_auth
class Node_Stop_Handler(APIHandler):
    
    node_opers = NodeOpers()
    
    def post(self):
        '''
        function: stop node
        url example: curl --user root:root -d "" "http://localhost:8888/node/stop"
        '''
        result = self.node_opers.stopNode()
        self.finish(result)

        