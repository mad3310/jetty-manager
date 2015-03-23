#!/usr/bin/env python
#-*- coding: utf-8 -*-

'''
Created on 2013-7-11

@author: asus
'''
import json
import logging
import threading

from utils.configFileOpers import ConfigFileOpers
from kazoo.client import KazooClient
from kazoo.exceptions import SessionExpiredError
from kazoo.handlers.threading import TimeoutError
from kazoo.retry import KazooRetry
from tornado.options import options
from utils import getClusterUUID, get_zk_address, get_dict_from_text


class ZkOpers(object):
    
    zk = None
    
    rootPath = "/letv/javaContainer/jetty"
    
    confOpers = ConfigFileOpers()
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        self.zkaddress, self.zkport = get_zk_address()
        self.retry = KazooRetry(max_tries=3, delay=0.5)
        self.zk = KazooClient(hosts=self.zkaddress+':'+str(self.zkport), connection_retry=self.retry)
        self.zk.start()
        #self.zk = self.ensureinstance()
        logging.info("instance zk client (%s:%s)" % (self.zkaddress, self.zkport))

    def close(self):
        try:
            self.zk.stop()
            self.zk.close()
            logging.info("stop the zk client successfully")
        except Exception, e:
            logging.error(e)

    def existCluster(self, uuid=None):
        self.zk.ensure_path(self.rootPath)
        cluster_uuids = self.zk.get_children(self.rootPath)
        
        if uuid is None:
            local_uuid = getClusterUUID()
        else:
            local_uuid = uuid
        
        if local_uuid in cluster_uuids:
            return True
        
        return False

    def __getClusterUUIDs(self):
        self.logger.debug(self.rootPath)
        try: 
            dataNodesName = self.zk.get_children(self.rootPath)
        except SessionExpiredError:
            dataNodesName = self.zk.get_children(self.rootPath)
        return dataNodesName

    def writeClusterInfo(self,clusterUUID,clusterProps):
        path = self.rootPath + "/" + clusterUUID
        self.zk.ensure_path(path)
        self.zk.set(path, str(clusterProps))#vesion need to write

    def retrieveClusterProp(self,clusterUUID):
        resultValue = {}
        path = self.rootPath + "/" + clusterUUID
        if self.zk.exists(path):
            resultValue = self.zk.get(path)
    
        return resultValue
    
    
    
    '''
    data componentNode
    '''
    def writeDataNodeInfo(self,clusterUUID,dataNodeProps):
        dataNodeName = dataNodeProps['dataNodeName']
        path = self.rootPath + "/" + clusterUUID + "/dataNode/" + dataNodeName
        self.zk.ensure_path(path)
        self.zk.set(path, str(dataNodeProps))#version need to write
 
    def retrieve_jetty_node_list(self):
        clusterUUID = getClusterUUID()
        path = self.rootPath + "/" + clusterUUID + "/dataNode"
        container_node_name_list = self.__return_children_to_list(path)
        return container_node_name_list

    def retrieve_jetty_node_info(self, container_node_name):
        clusterUUID = getClusterUUID()
        path = self.rootPath + "/" + clusterUUID + "/dataNode/" + container_node_name
        ip_dict = self.__retrieve_special_path_prop(path)
        return ip_dict
    
    '''
    started componentNode
    '''
    def write_started_node(self, container_node_name):
        clusterUUID = getClusterUUID()
        path = self.rootPath + "/" + clusterUUID + "/monitor_status/node/started/" + container_node_name
        self.zk.ensure_path(path)
    
    def remove_started_node(self, container_node_name):
        clusterUUID = getClusterUUID()
        path = self.rootPath + "/" + clusterUUID + "/monitor_status/node/started/" + container_node_name
        if self.zk.exists(path):
            self.zk.delete(path)
    
    def retrieve_started_nodes(self):
        #self.zk = self.ensureinstance()
        clusterUUID = getClusterUUID()
        path = self.rootPath + "/" + clusterUUID + "/monitor_status/node/started"
        started_nodes = self.__return_children_to_list(path)
        return started_nodes
    
    def lock_cluster_start_stop_action(self):
        lock_name = "cluster_start_stop"
        return self.__lock_base_action(lock_name)
    
    def unLock_cluster_start_stop_action(self, lock):
        self.__unLock_base_action(lock)
    
    '''
    @todo: currently, no used
    '''
    def unLock_aysnc_monitor_action(self, lock):
        self.__unLock_base_action(lock)
        
    def __lock_base_action(self, lock_name):
        clusterUUID = getClusterUUID()
        path = "%s/%s/lock/%s" % (self.rootPath, clusterUUID, lock_name) 
        lock = self.zk.Lock(path, threading.current_thread())
        isLock = lock.acquire(True,1)
        return (isLock,lock)
        
    def __unLock_base_action(self, lock):
        if lock is not None:
            lock.release()
    
    def __return_children_to_list(self, path):
        self.zk.ensure_path(path)
        children = self.zk.get_children(path)
        
        children_to_list = []
        if len(children) != 0:
            for i in range(len(children)):
                children_to_list.append(children[i])
        return children_to_list
    
    def __retrieve_special_path_prop(self,path):
        data = None
        
        if self.zk.exists(path):
            data,_ = self.zk.get(path)
            
        resultValue = {}
        if data != None and data != '':
            resultValue = self.__format_data(data)
            
        return resultValue
    
    def __format_data(self, data):
        local_data = data.replace("'", "\"").replace("[u\"", "[\"").replace(" u\"", " \"")
        formatted_data = json.loads(local_data)
        return formatted_data
        
if __name__ == "__main__":
    try:
        zkOpers = ZkOpers('127.0.0.1', 2181)
        path = "/letv/javaContainer/jetty/"
        # Print the version of a componentNode and its data
        data, stat = zkOpers.ensureinstance().get(path)
        #data, stat = zkOpers.zk.get(path)
        print("Version: %s, data: %s" % (stat.version, data.decode("utf-8")))

    # List the children
        while True:
            children = zkOpers.ensureinstance().get_children(path)
            #children = zkOpers.zk.get_children(path)
            print("There are %s children with names %s" % (len(children), children))
    except TimeoutError, e:
        print e
