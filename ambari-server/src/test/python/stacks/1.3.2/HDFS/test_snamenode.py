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
from ambari_commons import OSCheck
from mock.mock import MagicMock, patch

class TestSNamenode(RMFTestCase):

  def test_configure_default(self):
    self.executeScript("1.3.2/services/HDFS/package/scripts/snamenode.py",
                       classname = "SNameNode",
                       command = "configure",
                       config_file="default.json"
    )
    self.assert_configure_default()
    self.assertResourceCalled('File', '/etc/hadoop/conf/dfs.exclude',
                              owner = 'hdfs',
                              content = Template('exclude_hosts_list.j2'),
                              group = 'hadoop',
                              )
    self.assertNoMoreResources()

  def test_start_default(self):
    self.executeScript("1.3.2/services/HDFS/package/scripts/snamenode.py",
                       classname = "SNameNode",
                       command = "start",
                       config_file="default.json"
    )
    self.assert_configure_default()
    self.assertResourceCalled('File', '/etc/hadoop/conf/dfs.exclude',
                              owner = 'hdfs',
                              content = Template('exclude_hosts_list.j2'),
                              group = 'hadoop',
                              )
    self.assertResourceCalled('Directory', '/var/run/hadoop/hdfs',
                              owner = 'hdfs',
                              recursive = True,
                              )
    self.assertResourceCalled('Directory', '/var/log/hadoop/hdfs',
                              owner = 'hdfs',
                              recursive = True,
                              )
    self.assertResourceCalled('File', '/var/run/hadoop/hdfs/hadoop-hdfs-secondarynamenode.pid',
                              action = ['delete'],
                              not_if='ls /var/run/hadoop/hdfs/hadoop-hdfs-secondarynamenode.pid >/dev/null 2>&1 && ps -p `cat /var/run/hadoop/hdfs/hadoop-hdfs-secondarynamenode.pid` >/dev/null 2>&1',
                              )
    self.assertResourceCalled('Execute', "/usr/bin/sudo su hdfs -l -s /bin/bash -c '[RMF_EXPORT_PLACEHOLDER]ulimit -c unlimited &&  /usr/lib/hadoop/bin/hadoop-daemon.sh --config /etc/hadoop/conf start secondarynamenode'",
        environment = {'HADOOP_LIBEXEC_DIR': '/usr/lib/hadoop/libexec'},
        not_if = 'ls /var/run/hadoop/hdfs/hadoop-hdfs-secondarynamenode.pid >/dev/null 2>&1 && ps -p `cat /var/run/hadoop/hdfs/hadoop-hdfs-secondarynamenode.pid` >/dev/null 2>&1',
    )
    self.assertNoMoreResources()

  def test_stop_default(self):
    self.executeScript("1.3.2/services/HDFS/package/scripts/snamenode.py",
                       classname = "SNameNode",
                       command = "stop",
                       config_file="default.json"
    )
    self.assertResourceCalled('Directory', '/var/run/hadoop/hdfs',
                              owner = 'hdfs',
                              recursive = True,
                              )
    self.assertResourceCalled('Directory', '/var/log/hadoop/hdfs',
                              owner = 'hdfs',
                              recursive = True,
                              )
    self.assertResourceCalled('File', '/var/run/hadoop/hdfs/hadoop-hdfs-secondarynamenode.pid',
                              action = ['delete'],
                              not_if='ls /var/run/hadoop/hdfs/hadoop-hdfs-secondarynamenode.pid >/dev/null 2>&1 && ps -p `cat /var/run/hadoop/hdfs/hadoop-hdfs-secondarynamenode.pid` >/dev/null 2>&1',
                              )
    self.assertResourceCalled('Execute', "/usr/bin/sudo su hdfs -l -s /bin/bash -c '[RMF_EXPORT_PLACEHOLDER]ulimit -c unlimited &&  /usr/lib/hadoop/bin/hadoop-daemon.sh --config /etc/hadoop/conf stop secondarynamenode'",
        environment = {'HADOOP_LIBEXEC_DIR': '/usr/lib/hadoop/libexec'},
        not_if = None,
    )
    self.assertResourceCalled('File', '/var/run/hadoop/hdfs/hadoop-hdfs-secondarynamenode.pid',
                              action = ['delete'],
                              )
    self.assertNoMoreResources()

  def test_configure_secured(self):
    self.executeScript("1.3.2/services/HDFS/package/scripts/snamenode.py",
                       classname = "SNameNode",
                       command = "configure",
                       config_file="secured.json"
    )
    self.assert_configure_secured()
    self.assertResourceCalled('File', '/etc/hadoop/conf/dfs.exclude',
                              owner = 'hdfs',
                              content = Template('exclude_hosts_list.j2'),
                              group = 'hadoop',
                              )
    self.assertNoMoreResources()

  def test_start_secured(self):
    self.executeScript("1.3.2/services/HDFS/package/scripts/snamenode.py",
                       classname = "SNameNode",
                       command = "start",
                       config_file="secured.json"
    )
    self.assert_configure_secured()
    self.assertResourceCalled('File', '/etc/hadoop/conf/dfs.exclude',
                              owner = 'hdfs',
                              content = Template('exclude_hosts_list.j2'),
                              group = 'hadoop',
                              )
    self.assertResourceCalled('Directory', '/var/run/hadoop/hdfs',
                              owner = 'hdfs',
                              recursive = True,
                              )
    self.assertResourceCalled('Directory', '/var/log/hadoop/hdfs',
                              owner = 'hdfs',
                              recursive = True,
                              )
    self.assertResourceCalled('File', '/var/run/hadoop/hdfs/hadoop-hdfs-secondarynamenode.pid',
                              action = ['delete'],
                              not_if='ls /var/run/hadoop/hdfs/hadoop-hdfs-secondarynamenode.pid >/dev/null 2>&1 && ps -p `cat /var/run/hadoop/hdfs/hadoop-hdfs-secondarynamenode.pid` >/dev/null 2>&1',
                              )
    self.assertResourceCalled('Execute', "/usr/bin/sudo su hdfs -l -s /bin/bash -c '[RMF_EXPORT_PLACEHOLDER]ulimit -c unlimited &&  /usr/lib/hadoop/bin/hadoop-daemon.sh --config /etc/hadoop/conf start secondarynamenode'",
        environment = {'HADOOP_LIBEXEC_DIR': '/usr/lib/hadoop/libexec'},
        not_if = 'ls /var/run/hadoop/hdfs/hadoop-hdfs-secondarynamenode.pid >/dev/null 2>&1 && ps -p `cat /var/run/hadoop/hdfs/hadoop-hdfs-secondarynamenode.pid` >/dev/null 2>&1',
    )
    self.assertNoMoreResources()

  def test_stop_secured(self):
    self.executeScript("1.3.2/services/HDFS/package/scripts/snamenode.py",
                       classname = "SNameNode",
                       command = "stop",
                       config_file="secured.json"
    )
    self.assertResourceCalled('Directory', '/var/run/hadoop/hdfs',
                              owner = 'hdfs',
                              recursive = True,
                              )
    self.assertResourceCalled('Directory', '/var/log/hadoop/hdfs',
                              owner = 'hdfs',
                              recursive = True,
                              )
    self.assertResourceCalled('File', '/var/run/hadoop/hdfs/hadoop-hdfs-secondarynamenode.pid',
                              action = ['delete'],
                              not_if='ls /var/run/hadoop/hdfs/hadoop-hdfs-secondarynamenode.pid >/dev/null 2>&1 && ps -p `cat /var/run/hadoop/hdfs/hadoop-hdfs-secondarynamenode.pid` >/dev/null 2>&1',
                              )
    self.assertResourceCalled('Execute', "/usr/bin/sudo su hdfs -l -s /bin/bash -c '[RMF_EXPORT_PLACEHOLDER]ulimit -c unlimited &&  /usr/lib/hadoop/bin/hadoop-daemon.sh --config /etc/hadoop/conf stop secondarynamenode'",
        environment = {'HADOOP_LIBEXEC_DIR': '/usr/lib/hadoop/libexec'},
        not_if = None,
    )
    self.assertResourceCalled('File', '/var/run/hadoop/hdfs/hadoop-hdfs-secondarynamenode.pid',
                              action = ['delete'],
                              )
    self.assertNoMoreResources()

  def assert_configure_default(self):
    self.assertResourceCalled('Directory', '/etc/security/limits.d',
                              owner = 'root',
                              group = 'root',
                              recursive = True,
                              )
    self.assertResourceCalled('File', '/etc/security/limits.d/hdfs.conf',
                              content = Template('hdfs.conf.j2'),
                              owner = 'root',
                              group = 'root',
                              mode = 0644,
                              )
    self.assertResourceCalled('XmlConfig', 'hdfs-site.xml',
                              owner = 'hdfs',
                              group = 'hadoop',
                              conf_dir = '/etc/hadoop/conf',
                              configurations = self.getConfig()['configurations']['hdfs-site'],
                              configuration_attributes = self.getConfig()['configuration_attributes']['hdfs-site']
                              )
    self.assertResourceCalled('File', '/etc/hadoop/conf/slaves',
                              content = Template('slaves.j2'),
                              owner = 'hdfs',
                              )
    self.assertResourceCalled('Directory', '/hadoop/hdfs/namesecondary',
                              owner = 'hdfs',
                              group = 'hadoop',
                              mode = 0755,
                              recursive = True,
                              )

  def assert_configure_secured(self):
    self.assertResourceCalled('Directory', '/etc/security/limits.d',
                              owner = 'root',
                              group = 'root',
                              recursive = True,
                              )
    self.assertResourceCalled('File', '/etc/security/limits.d/hdfs.conf',
                              content = Template('hdfs.conf.j2'),
                              owner = 'root',
                              group = 'root',
                              mode = 0644,
                              )
    self.assertResourceCalled('XmlConfig', 'hdfs-site.xml',
                              owner = 'hdfs',
                              group = 'hadoop',
                              conf_dir = '/etc/hadoop/conf',
                              configurations = self.getConfig()['configurations']['hdfs-site'],
                              configuration_attributes = self.getConfig()['configuration_attributes']['hdfs-site']
                              )
    self.assertResourceCalled('File', '/etc/hadoop/conf/slaves',
                              content = Template('slaves.j2'),
                              owner = 'root',
                              )
    self.assertResourceCalled('Directory', '/hadoop/hdfs/namesecondary',
                              owner = 'hdfs',
                              group = 'hadoop',
                              mode = 0755,
                              recursive = True,
                              )
