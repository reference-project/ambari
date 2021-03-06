#!/usr/bin/env python
"""
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

Ambari Agent

"""

from resource_management.core.providers.package import PackageProvider
from resource_management.core import shell
from resource_management.core.shell import string_cmd_from_args_list
from resource_management.core.logger import Logger

INSTALL_CMD = {
  True: ['/usr/bin/yum', '-y', 'install'],
  False: ['/usr/bin/yum', '-d', '0', '-e', '0', '-y', 'install'],
}

REMOVE_CMD = {
  True: ['/usr/bin/yum', '-y', 'erase'],
  False: ['/usr/bin/yum', '-d', '0', '-e', '0', '-y', 'erase'],
}

CHECK_CMD = "installed_pkgs=`rpm -qa %s` ; [ ! -z \"$installed_pkgs\" ]"

class YumProvider(PackageProvider):
  def install_package(self, name, use_repos=[]):
    if not self._check_existence(name) or use_repos:
      cmd = INSTALL_CMD[self.get_logoutput()]
      if use_repos:
        enable_repo_option = '--enablerepo=' + ",".join(use_repos)
        cmd = cmd + ['--disablerepo=*', enable_repo_option]
      cmd = cmd + [name]
      Logger.info("Installing package %s ('%s')" % (name, string_cmd_from_args_list(cmd)))
      shell.checked_call(cmd, sudo=True, logoutput=self.get_logoutput())
    else:
      Logger.info("Skipping installing existent package %s" % (name))

  def upgrade_package(self, name, use_repos=[]):
    return self.install_package(name, use_repos)

  def remove_package(self, name):
    if self._check_existence(name):
      cmd = REMOVE_CMD[self.get_logoutput()] + [name]
      Logger.info("Removing package %s ('%s')" % (name, string_cmd_from_args_list(cmd)))
      shell.checked_call(cmd, sudo=True, logoutput=self.get_logoutput())
    else:
      Logger.info("Skipping removing non-existent package %s" % (name))

  def _check_existence(self, name):
    code, out = shell.call(CHECK_CMD % name)
    return not bool(code)
