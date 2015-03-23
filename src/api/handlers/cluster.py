#-*- coding: utf-8 -*-

from base import APIHandler
from tornado_letv.tornado_basic_auth import require_basic_auth
from tornado.web import asynchronous
from componentCluster.clusterOpers import ClusterOpers
from common.clusterStatus import ClusterStatus

'''
Created on 2013-7-21

@author: asus
'''
class Sync_Handler(APIHandler):
    
    cluster_opers = ClusterOpers()
    
    def post(self):
        '''
        function: sync cluster info from zk to local properties file
        url example: curl -d "clusterUUID=***" "http://localhost:8888/cluster/sync"
        '''
        requestParam = self.get_all_arguments()
        self.cluster_opers.syncExistedCluster(requestParam)
        
        result = {}
        result.setdefault("message", "sync jetty to local successful!")
        self.finish(result)


@require_basic_auth
class Cluster_Handler(APIHandler):
    
    cluster_opers = ClusterOpers()
    
    def post(self):
        '''
        function: create cluster and add the first jetty node to cluster, info record to zk
        url example: curl --user root:root -d "clusterName=jetty_cluster&dataNodeIp=192.168.116.129&dataNodeName=jetty_cluster_node_1[&dataNodeExternalPort=**]" "http://localhost:8888/cluster"
        '''
        requestParam = self.get_all_arguments()
        clusterUUID = self.cluster_opers.createCluster(requestParam)
        
        result = {}
        result.setdefault("message", "create cluster successfully! (cluster uuid:%s)"%(clusterUUID))
        self.finish(result)
        
    def get(self):
        '''
        function: retrieve the cluster status
        url example: curl --user root:root "http://localhost:8888/cluster"
        '''
        cluster_status = self.cluster_opers.retrieve_cluster_started_status()
        
        result = {}
        if ClusterStatus.STARTED == cluster_status:
            result.setdefault("message", "cluster is available, cluster status is started!")
        elif ClusterStatus.STARTED_PART == cluster_status:
            result.setdefault("message", "cluster is available, but part of nodes are not started!")
        else:
            result.setdefault("message", "cluster is not available, cluster status is stopped!")
            
        self.finish(result)


@require_basic_auth
class Cluster_Start_Handler(APIHandler):
    
    cluster_opers = ClusterOpers()
    
    @asynchronous
    def post(self):
        '''
        function: start cluster
        url example: curl --user root:root -d "" "http://localhost:8888/cluster/start"
        '''

        result = self.cluster_opers.startCluster()
        self.finish(result)


@require_basic_auth    
class Cluster_Stop_Handler(APIHandler):
    
    cluster_opers = ClusterOpers()
    
    @asynchronous
    def post(self):
        '''
        function: stop cluster
        url example: curl --user root:root -d "" "http://localhost:8888/cluster/stop"
        '''
        result = self.cluster_opers.stopCluster()
        self.finish(result)

