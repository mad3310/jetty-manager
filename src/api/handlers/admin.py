#-*- coding: utf-8 -*-
import os
import stat
import base64
import shutil
import logging

from utils.configFileOpers import ConfigFileOpers
from base import APIHandler
from tornado.options import options
from utils.exceptions import HTTPAPIError
from tornado_letv.tornado_basic_auth import require_basic_auth
from zk.zkOpers import ZkOpers


class AdminConf(APIHandler):
    
    confOpers = ConfigFileOpers()
    
    def post(self):
        '''
        function: admin conf
        url example: curl -d "zkAddress=10.204.8.211&zkPort=2181" "http://localhost:8888/admin/conf"
        '''
        requestParam = self.get_all_arguments()
        if requestParam != {}:
            self.confOpers.setValue(options.jetty_manager_property, requestParam)
            
        result = {}
        result.setdefault("message", "admin conf successful!")
        self.finish(result)


class AdminReset(APIHandler):
    
    def get(self):
        '''
        function: admin reset
        url example: curl --user root:root "http://localhost:8888/admin/reset"
        '''
        template_path=os.path.join(options.base_dir, "templates")
        config_path = os.path.join(options.base_dir, "config")
    
        clusterPropTemFileName = os.path.join(template_path,"cluster.property.template")
        dataNodePropTemFileName = os.path.join(template_path,"dataNode.property.template")
        nclusterManagerPropTemFileName = os.path.join(template_path,"jetty_manager.property.template")
    
        clusterPropFileName = os.path.join(config_path,"cluster.property")
        dataNodePropFileName = os.path.join(config_path,"dataNode.property")
        jettyManagerPropFileName = os.path.join(config_path,"jetty_manager.property")
        fileNameList = [clusterPropFileName,dataNodePropFileName,jettyManagerPropFileName]
    
        for fileName in fileNameList:
            if os.path.exists(fileName):
                os.chmod(fileName, stat.S_IWRITE)
                os.remove(fileName)
        
        shutil.copyfile(clusterPropTemFileName, clusterPropFileName)
        shutil.copyfile(dataNodePropTemFileName, dataNodePropFileName)
        shutil.copyfile(nclusterManagerPropTemFileName, jettyManagerPropFileName)
   
        result = {}
        result.setdefault("message", "admin reset successful!")
        self.finish(result)

        
class AdminUser(APIHandler):
    
    confOpers = ConfigFileOpers()
    
    def post(self):
        '''
        function: create admin user
        url example: curl -d "adminUser=root&adminPassword=root" "http://localhost:8888/admin/user"
        '''
        requestParam = {}
        args = self.request.arguments
        logging.info("args :"+ str(args))
        for key in args:
            value = args[key][0]
            if key == 'adminPassword':
                value = base64.encodestring(value).strip('\n')
            requestParam.setdefault(key,value)
        if requestParam['adminUser'] == '' or requestParam['adminPassword'] == '':
            raise HTTPAPIError(status_code=401, error_detail="username or password is empty",\
                               notification = "direct", \
                               log_message= "username or password is empty", \
                               response = "username or password is empty")
        if requestParam != {}:
            self.confOpers.setValue(options.cluster_property, requestParam)
        
        result = {}
        result.setdefault("message", "creating admin user successful!")
        self.finish(result)

 
@require_basic_auth
class Config(APIHandler):
    
    confOpers = ConfigFileOpers()
    
    def post(self):
        '''
        function: set the jetty configuration file
        url example: curl -d "k1=v1&k2=v2" "http://localhost:8888/jetty/config"
        '''
        requestParam = self.get_all_arguments()
        
        zkOper = ZkOpers()
        try:
            if requestParam != {}:
                self.confOpers.setValue(options.jetty_service_cnf, requestParam)
                source_text = self.confOpers.retrieve_full_text(options.jetty_service_cnf)
                zkOper.writeJettyCnf(source_text)
        finally:
            zkOper.close()
