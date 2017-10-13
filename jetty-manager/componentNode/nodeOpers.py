'''
Created on Mar 13, 2015

@author: root
'''
from utils.invokeCommand import InvokeCommand
from tornado.options import options
from utils import retrieve_node_name
from common.abstractOpers import AbstractOpers
from zk.zkOpers import ZkOpers
from utils.exceptions import UserVisiableException
from utils import getClusterUUID
from utils.configFileOpers import ConfigFileOpers


class NodeOpers(AbstractOpers):
    '''
    classdocs
    '''
    invokeCommand = InvokeCommand()
    confOpers = ConfigFileOpers()

    def __init__(self):
        '''
        Constructor
        '''
        
    def createNode(self, params):
        if params == {} or params is None:
            raise UserVisiableException("please set the componentNode info!")
        
        dataNodeInternalPort = params.get('dataNodeInternalPort')
        if dataNodeInternalPort is not None:
            raise UserVisiableException("no need to set the dataNodeInternalPort param!")
            
        zkOper = ZkOpers()
        
        try:
            local_uuid = getClusterUUID()
            existCluster = zkOper.existCluster(local_uuid)
            if not existCluster:
                raise UserVisiableException("sync componentCluster info error! please check if sync uuid is right!")
                
            params.setdefault("dataNodeInternalPort", options.port)
            dataNodeExternalPort = params.get('dataNodeExternalPort')
            if dataNodeExternalPort is None or '' == dataNodeExternalPort:
                params.setdefault("dataNodeExternalPort", options.port)
            
            self.confOpers.setValue(options.data_node_property, params)
            dataNodeProprs = self.confOpers.getValue(options.data_node_property)
            zkOper.writeDataNodeInfo(local_uuid, dataNodeProprs)
            
        finally:
            zkOper.close()
        
        result = {}
        result.setdefault("message", "Configuration on this componentNode has been done successfully")    
        return result
    
    def startNode(self):
        _, ret_val = self.invokeCommand._runSysCmd(options.start_jetty)
        
        result = {}
        if ret_val != 0:
            result.setdefault("message", "start jetty failed")
        else:
            container_name =  retrieve_node_name()
            zkOper = ZkOpers()
            try:
                zkOper.write_started_node(container_name)
            finally:
                zkOper.close()
                
            result.setdefault("message", "start jetty successfully")
        
        return result
    
    def stopNode(self):
        _, ret_val = self.invokeCommand._runSysCmd(options.stop_jetty)
        
        result = {}
        if ret_val != 0:
            result.setdefault("message", "stop jetty failed")
        else:
            container_name = retrieve_node_name()
            
            zkOper = ZkOpers()
            try:
                zkOper.remove_started_node(container_name)
            finally:
                zkOper.close()
                
            result.setdefault("message", "stop jetty successfully")
        
        return result
