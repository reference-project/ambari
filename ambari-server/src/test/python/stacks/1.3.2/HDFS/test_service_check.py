#!/usr/bin/env python

'''
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
from stacks.utils.RMFTestCase import *
import resource_management.libraries.functions
from mock.mock import MagicMock, call, patch

@patch.object(resource_management.libraries.functions, "get_unique_id_and_date", new = MagicMock(return_value=''))
class TestServiceCheck(RMFTestCase):
  def test_service_check_default(self):
    self.executeScript("1.3.2/services/HDFS/package/scripts/service_check.py",
                        classname="HdfsServiceCheck",
                        command="service_check",
                        config_file="default.json"
    )
    
    self.assert_service_check()
    self.assertNoMoreResources()
    
  def test_service_check_secured(self):
    self.executeScript("1.3.2/services/HDFS/package/scripts/service_check.py",
                        classname="HdfsServiceCheck",
                        command="service_check",
                        config_file="secured.json"
    )
    self.assertResourceCalled('Execute', "/usr/bin/kinit -kt /etc/security/keytabs/smokeuser.headless.keytab ambari-qa",user='ambari-qa')
    self.assert_service_check()
    self.assertNoMoreResources()
        
  def assert_service_check(self):
    self.assertResourceCalled('ExecuteHadoop', 'dfsadmin -safemode get | grep OFF',
                              logoutput = True,
                              tries = 20,
                              conf_dir = '/etc/hadoop/conf',
                              try_sleep = 15,
                              user = 'ambari-qa',
                              )
    self.assertResourceCalled('ExecuteHadoop', 'fs -mkdir /tmp ; hadoop fs -chmod 777 /tmp',
                              conf_dir = '/etc/hadoop/conf',
                              logoutput = True,
                              not_if = "/usr/bin/sudo su ambari-qa -l -s /bin/bash -c '[RMF_EXPORT_PLACEHOLDER]hadoop fs -test -e /tmp'",
                              try_sleep = 3,
                              tries = 5,
                              user = 'ambari-qa',
                              )
    self.assertResourceCalled('ExecuteHadoop', 'fs -rm /tmp/; hadoop fs -put /etc/passwd /tmp/',
                              logoutput = True,
                              tries = 5,
                              conf_dir = '/etc/hadoop/conf',
                              try_sleep = 3,
                              user = 'ambari-qa',
                              )
    self.assertResourceCalled('ExecuteHadoop', 'fs -test -e /tmp/',
                              logoutput = True,
                              tries = 5,
                              conf_dir = '/etc/hadoop/conf',
                              try_sleep = 3,
                              user = 'ambari-qa',
                              )
    self.assertNoMoreResources()