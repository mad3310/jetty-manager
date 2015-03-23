'''
Created on Mar 13, 2015

@author: root
'''
import logging
import uuid
import json


from tornado.options import options
from zk.zkOpers import ZkOpers
from utils.exceptions import UserVisiableException
from componentCluster.baseClusterOpers import BaseClusterOpers
from utils.configFileOpers import ConfigFileOpers
from common.operType import OperType
from common.clusterStatus import ClusterStatus


class ClusterOpers(BaseClusterOpers):
    '''
    classdocs
    '''
    confOpers = ConfigFileOpers()

    def __init__(self):
        super(ClusterOpers, self).__init__()
        
    
    def createCluster(self, params):
        if params == {} or params is None:
            raise UserVisiableException("please set the componentNode info!")
        
        dataNodeInternalPort = params.get('dataNodeInternalPort')
        if dataNodeInternalPort:
            raise UserVisiableException("no need to set the dataNodeInternalPort param!")
        
        zkOper = ZkOpers()
        
        try:
            existCluster = zkOper.existCluster()
           
            if existCluster:
                raise UserVisiableException("server has belong to a componentCluster,should be not create new componentCluster!")
                
            clusterUUID = str(uuid.uuid1())
            params.setdefault("clusterUUID",clusterUUID)
            
            params.setdefault("dataNodeInternalPort", options.port)
            dataNodeExternalPort = params.get('dataNodeExternalPort')
            if dataNodeExternalPort is None or '' == dataNodeExternalPort:
                params.setdefault("dataNodeExternalPort",options.port)
            
            self.confOpers.setValue(options.cluster_property, params)
            self.confOpers.setValue(options.data_node_property, params)
                
            clusterProps = self.confOpers.getValue(options.cluster_property)
            dataNodeProprs = self.confOpers.getValue(options.data_node_property)
            
            zkOper.writeClusterInfo(clusterUUID, clusterProps)
            zkOper.writeDataNodeInfo(clusterUUID, dataNodeProprs)
        finally:
            zkOper.close()
            
        return clusterUUID
    
    
    
    def startCluster(self):
        zkOper = ZkOpers()
        
        try:
            existCluster =  zkOper.existCluster()
            if not existCluster:
                raise UserVisiableException("Jetty componentCluster does't exist")
        
            total_nodes = zkOper.retrieve_jetty_node_list() 
            started_nodes = zkOper.retrieve_started_nodes()
            if len(total_nodes) == len(started_nodes):
                raise UserVisiableException("all jetty nodes have started. No need to start them.")
            
            logging.info("all jetty nodes: %s" %(total_nodes))
            to_start_nodes = list(set(total_nodes) - set(started_nodes))
            logging.info("jetty needed to start: " + str(to_start_nodes))
            
            node_infos = []
            for node in to_start_nodes:
                info = zkOper.retrieve_jetty_node_info(node)
                node_infos.append(info)
        finally:
            zkOper.close()
        
        self.baseOpers(node_infos, OperType.start)
        
        result_dict = {'message':'cluster start processing, please wait for a moment!'}
        return result_dict
    
    
    
    def stopCluster(self):
        zkOper = ZkOpers()
        node_infos = []
        
        try:
            started_nodes_list = zkOper.retrieve_started_nodes()
            if not started_nodes_list:
                return {'message':'cluster has been stopped, no need to do this!'}
            for node in started_nodes_list:
                info = zkOper.retrieve_jetty_node_info(node)
                node_infos.append(info)
        finally:
            zkOper.close()
        
        self.baseOpers(node_infos, OperType.stop)
        result_dict = {'message':'cluster stop processing, please wait for a moment!'}
        return result_dict

    def syncExistedCluster(self, params):
        if params == {}:
            error_message = "please fill the cluster uuid!"
            raise UserVisiableException(error_message)
            
        clusterUUID = params['clusterUUID']
        zkOper = ZkOpers()
        try:
            existCluster = zkOper.existCluster(clusterUUID)
            if not existCluster:
                error_message = "Jetty componentCluster does't exist(cluster id:%s), \
                     please specify the right cluster uuid!"%(clusterUUID)
                raise UserVisiableException(error_message)
             
            data, _ = zkOper.retrieveClusterProp(clusterUUID)
            logging.info("data in zk %s" %(data))
            json_str_data = data.replace("'", "\"")
            dict_data = json.loads(json_str_data) 
            self.confOpers.setValue(options.cluster_property, dict_data)
        finally:
            zkOper.close()
            
    def retrieve_cluster_started_status(self):
        zkOper = ZkOpers()
        try:
            started_nodes = zkOper.retrieve_started_nodes()
            total_nodes = zkOper.retrieve_jetty_node_list()
        finally:
            zkOper.close()
             
        started_nodes_count = len(started_nodes)
        total_nodes_count = len(total_nodes)
        
        if started_nodes_count == total_nodes_count:
            return ClusterStatus.STARTED
        elif 0 != started_nodes_count:
            return ClusterStatus.STARTED_PART
        else:
            return ClusterStatus.STOP
        