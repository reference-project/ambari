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

class TestJournalnode(RMFTestCase):
  COMMON_SERVICES_PACKAGE_DIR = "HDFS/2.1.0.2.0/package"
  STACK_VERSION = "2.0.6"

  def test_configure_default(self):
    self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/journalnode.py",
                       classname = "JournalNode",
                       command = "configure",
                       config_file = "default.json",
                       hdp_stack_version = self.STACK_VERSION,
                       target = RMFTestCase.TARGET_COMMON_SERVICES
    )
    self.assert_configure_default()
    self.assertNoMoreResources()

  def test_start_default(self):
    self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/journalnode.py",
                       classname = "JournalNode",
                       command = "start",
                       config_file = "default.json",
                       hdp_stack_version = self.STACK_VERSION,
                       target = RMFTestCase.TARGET_COMMON_SERVICES
    )
    self.assert_configure_default()
    self.assertResourceCalled('Directory', '/var/run/hadoop',
                              owner = 'hdfs',
                              group = 'hadoop',
                              mode = 0755
                              )
    self.assertResourceCalled('Directory', '/var/run/hadoop/hdfs',
                              owner = 'hdfs',
                              recursive = True,
                              )
    self.assertResourceCalled('Directory', '/var/log/hadoop/hdfs',
                              owner = 'hdfs',
                              recursive = True,
                              )
    self.assertResourceCalled('File', '/var/run/hadoop/hdfs/hadoop-hdfs-journalnode.pid',
                              action = ['delete'],
                              not_if='ls /var/run/hadoop/hdfs/hadoop-hdfs-journalnode.pid >/dev/null 2>&1 && ps -p `cat /var/run/hadoop/hdfs/hadoop-hdfs-journalnode.pid` >/dev/null 2>&1',
                              )
    self.assertResourceCalled('Execute', "/usr/bin/sudo su hdfs -l -s /bin/bash -c '[RMF_EXPORT_PLACEHOLDER]ulimit -c unlimited &&  /usr/lib/hadoop/sbin/hadoop-daemon.sh --config /etc/hadoop/conf start journalnode'",
        environment = {'HADOOP_LIBEXEC_DIR': '/usr/lib/hadoop/libexec'},
        not_if = 'ls /var/run/hadoop/hdfs/hadoop-hdfs-journalnode.pid >/dev/null 2>&1 && ps -p `cat /var/run/hadoop/hdfs/hadoop-hdfs-journalnode.pid` >/dev/null 2>&1',
    )
    self.assertNoMoreResources()

  def test_stop_default(self):
    self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/journalnode.py",
                       classname = "JournalNode",
                       command = "stop",
                       config_file = "default.json",
                       hdp_stack_version = self.STACK_VERSION,
                       target = RMFTestCase.TARGET_COMMON_SERVICES
    )
    self.assertResourceCalled('Directory', '/var/run/hadoop/hdfs',
                              owner = 'hdfs',
                              recursive = True,
                              )
    self.assertResourceCalled('Directory', '/var/log/hadoop/hdfs',
                              owner = 'hdfs',
                              recursive = True,
                              )
    self.assertResourceCalled('File', '/var/run/hadoop/hdfs/hadoop-hdfs-journalnode.pid',
                              action = ['delete'],
                              not_if='ls /var/run/hadoop/hdfs/hadoop-hdfs-journalnode.pid >/dev/null 2>&1 && ps -p `cat /var/run/hadoop/hdfs/hadoop-hdfs-journalnode.pid` >/dev/null 2>&1',
                              )
    self.assertResourceCalled('Execute', "/usr/bin/sudo su hdfs -l -s /bin/bash -c '[RMF_EXPORT_PLACEHOLDER]ulimit -c unlimited &&  /usr/lib/hadoop/sbin/hadoop-daemon.sh --config /etc/hadoop/conf stop journalnode'",
        environment = {'HADOOP_LIBEXEC_DIR': '/usr/lib/hadoop/libexec'},
        not_if = None,
    )
    self.assertResourceCalled('File', '/var/run/hadoop/hdfs/hadoop-hdfs-journalnode.pid',
                              action = ['delete'],
                              )
    self.assertNoMoreResources()

  def test_configure_secured(self):
    self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/journalnode.py",
                       classname = "JournalNode",
                       command = "configure",
                       config_file = "secured.json",
                       hdp_stack_version = self.STACK_VERSION,
                       target = RMFTestCase.TARGET_COMMON_SERVICES
    )
    self.assert_configure_secured()
    self.assertNoMoreResources()

  def test_start_secured(self):
    self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/journalnode.py",
                       classname = "JournalNode",
                       command = "start",
                       config_file = "secured.json",
                       hdp_stack_version = self.STACK_VERSION,
                       target = RMFTestCase.TARGET_COMMON_SERVICES
    )
    self.assert_configure_secured()
    self.assertResourceCalled('Directory', '/var/run/hadoop',
                              owner = 'hdfs',
                              group = 'hadoop',
                              mode = 0755
                              )
    self.assertResourceCalled('Directory', '/var/run/hadoop/hdfs',
                              owner = 'hdfs',
                              recursive = True,
                              )
    self.assertResourceCalled('Directory', '/var/log/hadoop/hdfs',
                              owner = 'hdfs',
                              recursive = True,
                              )
    self.assertResourceCalled('File', '/var/run/hadoop/hdfs/hadoop-hdfs-journalnode.pid',
                              action = ['delete'],
                              not_if='ls /var/run/hadoop/hdfs/hadoop-hdfs-journalnode.pid >/dev/null 2>&1 && ps -p `cat /var/run/hadoop/hdfs/hadoop-hdfs-journalnode.pid` >/dev/null 2>&1',
                              )
    self.assertResourceCalled('Execute', "/usr/bin/sudo su hdfs -l -s /bin/bash -c '[RMF_EXPORT_PLACEHOLDER]ulimit -c unlimited &&  /usr/lib/hadoop/sbin/hadoop-daemon.sh --config /etc/hadoop/conf start journalnode'",
        environment = {'HADOOP_LIBEXEC_DIR': '/usr/lib/hadoop/libexec'},
        not_if = 'ls /var/run/hadoop/hdfs/hadoop-hdfs-journalnode.pid >/dev/null 2>&1 && ps -p `cat /var/run/hadoop/hdfs/hadoop-hdfs-journalnode.pid` >/dev/null 2>&1',
    )
    self.assertNoMoreResources()

  def test_stop_secured(self):
    self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/journalnode.py",
                       classname = "JournalNode",
                       command = "stop",
                       config_file = "secured.json",
                       hdp_stack_version = self.STACK_VERSION,
                       target = RMFTestCase.TARGET_COMMON_SERVICES
    )
    self.assertResourceCalled('Directory', '/var/run/hadoop/hdfs',
                              owner = 'hdfs',
                              recursive = True,
                              )
    self.assertResourceCalled('Directory', '/var/log/hadoop/hdfs',
                              owner = 'hdfs',
                              recursive = True,
                              )
    self.assertResourceCalled('File', '/var/run/hadoop/hdfs/hadoop-hdfs-journalnode.pid',
                              action = ['delete'],
                              not_if='ls /var/run/hadoop/hdfs/hadoop-hdfs-journalnode.pid >/dev/null 2>&1 && ps -p `cat /var/run/hadoop/hdfs/hadoop-hdfs-journalnode.pid` >/dev/null 2>&1',
                              )
    self.assertResourceCalled('Execute', "/usr/bin/sudo su hdfs -l -s /bin/bash -c '[RMF_EXPORT_PLACEHOLDER]ulimit -c unlimited &&  /usr/lib/hadoop/sbin/hadoop-daemon.sh --config /etc/hadoop/conf stop journalnode'",
        environment = {'HADOOP_LIBEXEC_DIR': '/usr/lib/hadoop/libexec'},
        not_if = None,
    )
    self.assertResourceCalled('File', '/var/run/hadoop/hdfs/hadoop-hdfs-journalnode.pid',
                              action = ['delete'],
                              )
    self.assertNoMoreResources()

  def assert_configure_default(self):
    self.assertResourceCalled('Directory', '/grid/0/hdfs/journal',
                              owner = 'hdfs',
                              group = 'hadoop',
                              recursive = True,
                              recursive_permission = True
                              )
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
    self.assertResourceCalled('XmlConfig', 'core-site.xml',
                              owner = 'hdfs',
                              group = 'hadoop',
                              conf_dir = '/etc/hadoop/conf',
                              configurations = self.getConfig()['configurations']['core-site'],
                              configuration_attributes = self.getConfig()['configuration_attributes']['core-site'],
                              mode = 0644
                              )
    self.assertResourceCalled('File', '/etc/hadoop/conf/slaves',
                              content = Template('slaves.j2'),
                              owner = 'hdfs',
                              )
    self.assertResourceCalled('File', '/var/lib/ambari-agent/lib/fast-hdfs-resource.jar',
        content = StaticFile('fast-hdfs-resource.jar'),
    )

  def assert_configure_secured(self):
    self.assertResourceCalled('Directory', '/grid/0/hdfs/journal',
                              owner = 'hdfs',
                              group = 'hadoop',
                              recursive = True,
                              recursive_permission = True
                              )
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
    self.assertResourceCalled('XmlConfig', 'core-site.xml',
                              owner = 'hdfs',
                              group = 'hadoop',
                              conf_dir = '/etc/hadoop/conf',
                              configurations = self.getConfig()['configurations']['core-site'],
                              configuration_attributes = self.getConfig()['configuration_attributes']['core-site'],
                              mode = 0644
    )
    self.assertResourceCalled('File', '/etc/hadoop/conf/slaves',
                              content = Template('slaves.j2'),
                              owner = 'root',
                              )
    self.assertResourceCalled('File', '/var/lib/ambari-agent/lib/fast-hdfs-resource.jar',
        content = StaticFile('fast-hdfs-resource.jar'),
    )
