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
import tempfile

__all__ = ["Script"]

import os
import sys
import json
import logging
import platform

from resource_management.libraries.resources import XmlConfig
from resource_management.libraries.resources import PropertiesFile
from resource_management.core.resources import File, Directory
from resource_management.core.source import InlineTemplate
from resource_management.core.environment import Environment
from resource_management.core.logger import Logger
from resource_management.core.exceptions import Fail, ClientComponentHasNoStatus, ComponentIsNotRunning
from resource_management.core.resources.packaging import Package
from resource_management.libraries.script.config_dictionary import ConfigDictionary, UnknownConfiguration

IS_WINDOWS = platform.system() == "Windows"
if IS_WINDOWS:
  from resource_management.libraries.functions.install_hdp_msi import install_windows_msi
  from resource_management.libraries.functions.reload_windows_env import reload_windows_env
  from resource_management.libraries.functions.zip_archive import archive_dir
else:
  from resource_management.libraries.functions.tar_archive import archive_dir

USAGE = """Usage: {0} <COMMAND> <JSON_CONFIG> <BASEDIR> <STROUTPUT> <LOGGING_LEVEL> <TMP_DIR>

<COMMAND> command type (INSTALL/CONFIGURE/START/STOP/SERVICE_CHECK...)
<JSON_CONFIG> path to command json file. Ex: /var/lib/ambari-agent/data/command-2.json
<BASEDIR> path to service metadata dir. Ex: /var/lib/ambari-agent/cache/common-services/HDFS/2.1.0.2.0/package
<STROUTPUT> path to file with structured command output (file will be created). Ex:/tmp/my.txt
<LOGGING_LEVEL> log level for stdout. Ex:DEBUG,INFO
<TMP_DIR> temporary directory for executable scripts. Ex: /var/lib/ambari-agent/data/tmp
"""

_PASSWORD_MAP = {"/configurations/cluster-env/hadoop.user.name":"/configurations/cluster-env/hadoop.user.password"}

def get_path_form_configuration(name, configuration):
  subdicts = filter(None, name.split('/'))

  for x in subdicts:
    if x in configuration:
      configuration = configuration[x]
    else:
      return None

  return configuration

class Script(object):
  """
  Executes a command for custom service. stdout and stderr are written to
  tmpoutfile and to tmperrfile respectively.
  Script instances share configuration as a class parameter and therefore
  different Script instances can not be used from different threads at
  the same time within a single python process

  Accepted command line arguments mapping:
  1 command type (START/STOP/...)
  2 path to command json file
  3 path to service metadata dir (Directory "package" inside service directory)
  4 path to file with structured command output (file will be created)
  """
  structuredOut = {}

  def put_structured_out(self, sout):
    Script.structuredOut.update(sout)
    try:
      with open(self.stroutfile, 'w') as fp:
        json.dump(Script.structuredOut, fp)
    except IOError:
      Script.structuredOut.update({"errMsg" : "Unable to write to " + self.stroutfile})

  def execute(self):
    """
    Sets up logging;
    Parses command parameters and executes method relevant to command type
    """
    logger, chout, cherr = Logger.initialize_logger()
    
    # parse arguments
    if len(sys.argv) < 7:
     logger.error("Script expects at least 6 arguments")
     print USAGE.format(os.path.basename(sys.argv[0])) # print to stdout
     sys.exit(1)

    command_name = str.lower(sys.argv[1])
    command_data_file = sys.argv[2]
    basedir = sys.argv[3]
    self.stroutfile = sys.argv[4]
    logging_level = sys.argv[5]
    Script.tmp_dir = sys.argv[6]

    logging_level_str = logging._levelNames[logging_level]
    chout.setLevel(logging_level_str)
    logger.setLevel(logging_level_str)

    # on windows we need to reload some of env variables manually because there is no default paths for configs(like
    # /etc/something/conf on linux. When this env vars created by one of the Script execution, they can not be updated
    # in agent, so other Script executions will not be able to access to new env variables
    if platform.system() == "Windows":
      reload_windows_env()

    try:
      with open(command_data_file, "r") as f:
        pass
        Script.config = ConfigDictionary(json.load(f))
        #load passwords here(used on windows to impersonate different users)
        Script.passwords = {}
        for k, v in _PASSWORD_MAP.iteritems():
          if get_path_form_configuration(k,Script.config) and get_path_form_configuration(v,Script.config ):
            Script.passwords[get_path_form_configuration(k,Script.config)] = get_path_form_configuration(v,Script.config)

    except IOError:
      logger.exception("Can not read json file with command parameters: ")
      sys.exit(1)
    # Run class method depending on a command type
    try:
      method = self.choose_method_to_execute(command_name)
      with Environment(basedir) as env:
        method(env)
    except ClientComponentHasNoStatus or ComponentIsNotRunning:
      # Support of component status checks.
      # Non-zero exit code is interpreted as an INSTALLED status of a component
      sys.exit(1)
    except Fail:
      logger.exception("Error while executing command '{0}':".format(command_name))
      sys.exit(1)


  def choose_method_to_execute(self, command_name):
    """
    Returns a callable object that should be executed for a given command.
    """
    self_methods = dir(self)
    if not command_name in self_methods:
      raise Fail("Script '{0}' has no method '{1}'".format(sys.argv[0], command_name))
    method = getattr(self, command_name)
    return method


  @staticmethod
  def get_config():
    """
    HACK. Uses static field to store configuration. This is a workaround for
    "circular dependency" issue when importing params.py file and passing to
     it a configuration instance.
    """
    return Script.config

  @staticmethod
  def get_password(user):
    return Script.passwords[user]

  @staticmethod
  def get_tmp_dir():
    """
    HACK. Uses static field to avoid "circular dependency" issue when
    importing params.py.
    """
    return Script.tmp_dir


  def install(self, env):
    """
    Default implementation of install command is to install all packages
    from a list, received from the server.
    Feel free to override install() method with your implementation. It
    usually makes sense to call install_packages() manually in this case
    """
    self.install_packages(env)


  if not IS_WINDOWS:
    def install_packages(self, env, exclude_packages=[]):
      """
      List of packages that are required< by service is received from the server
      as a command parameter. The method installs all packages
      from this list
      """
      config = self.get_config()
      try:
        package_list_str = config['hostLevelParams']['package_list']
        if isinstance(package_list_str, basestring) and len(package_list_str) > 0:
          package_list = json.loads(package_list_str)
          for package in package_list:
            if not package['name'] in exclude_packages:
              name = package['name']
              Package(name)
      except KeyError:
        pass  # No reason to worry

        # RepoInstaller.remove_repos(config)
      pass
  else:
    def install_packages(self, env, exclude_packages=[]):
      """
      List of packages that are required< by service is received from the server
      as a command parameter. The method installs all packages
      from this list
      """
      config = self.get_config()

      install_windows_msi(os.path.join(config['hostLevelParams']['jdk_location'], "hdp.msi"),
                          config["hostLevelParams"]["agentCacheDir"], "hdp.msi", self.get_password("hadoop"))
      pass

  def fail_with_error(self, message):
    """
    Prints error message and exits with non-zero exit code
    """
    print("Error: " + message)
    sys.stderr.write("Error: " + message)
    sys.exit(1)

  def start(self, env, rolling_restart=False):
    """
    To be overridden by subclasses
    """
    self.fail_with_error('start method isn\'t implemented')

  def stop(self, env, rolling_restart=False):
    """
    To be overridden by subclasses
    """
    self.fail_with_error('stop method isn\'t implemented')

  def pre_rolling_restart(self, env):
    """
    To be overridden by subclasses
    """
    pass

  def restart(self, env):
    """
    Default implementation of restart command is to call stop and start methods
    Feel free to override restart() method with your implementation.
    For client components we call install
    """
    config = self.get_config()
    componentCategory = None
    try :
      componentCategory = config['roleParams']['component_category']
    except KeyError:
      pass

    restart_type = ""
    if config is not None:
      command_params = config["commandParams"] if "commandParams" in config else None
      if command_params is not None:
        restart_type = command_params["restart_type"] if "restart_type" in command_params else ""
        if restart_type:
          restart_type = restart_type.encode('ascii', 'ignore')

    rolling_restart = restart_type.lower().startswith("rolling")

    if componentCategory and componentCategory.strip().lower() == 'CLIENT'.lower():
      if rolling_restart:
        self.pre_rolling_restart(env)

      self.install(env)
    else:
      # To remain backward compatible with older stacks, only pass rolling_restart if True.
      if rolling_restart:
        self.stop(env, rolling_restart=rolling_restart)
      else:
        self.stop(env)

      if rolling_restart:
        self.pre_rolling_restart(env)

      # To remain backward compatible with older stacks, only pass rolling_restart if True.
      if rolling_restart:
        self.start(env, rolling_restart=rolling_restart)
      else:
        self.start(env)

      if rolling_restart:
        self.post_rolling_restart(env)

  def post_rolling_restart(self, env):
    """
    To be overridden by subclasses
    """
    pass

  def configure(self, env):
    """
    To be overridden by subclasses
    """
    self.fail_with_error('configure method isn\'t implemented')

  def generate_configs_get_template_file_content(self, filename, dicts):
    config = self.get_config()
    content = ''
    for dict in dicts.split(','):
      if dict.strip() in config['configurations']:
        try:
          content += config['configurations'][dict.strip()]['content']
        except Fail:
          # 'content' section not available in the component client configuration
          pass

    return content

  def generate_configs_get_xml_file_content(self, filename, dict):
    config = self.get_config()
    return {'configurations':config['configurations'][dict],
            'configuration_attributes':config['configuration_attributes'][dict]}
    
  def generate_configs_get_xml_file_dict(self, filename, dict):
    config = self.get_config()
    return config['configurations'][dict]

  def generate_configs(self, env):
    """
    Generates config files and stores them as an archive in tmp_dir
    based on xml_configs_list and env_configs_list from commandParams
    """
    config = self.get_config()

    xml_configs_list = config['commandParams']['xml_configs_list']
    env_configs_list = config['commandParams']['env_configs_list']
    properties_configs_list = config['commandParams']['properties_configs_list']

    Directory(self.get_tmp_dir(), recursive=True)

    conf_tmp_dir = tempfile.mkdtemp(dir=self.get_tmp_dir())
    output_filename = os.path.join(self.get_tmp_dir(), config['commandParams']['output_file'])

    try:
      for file_dict in xml_configs_list:
        for filename, dict in file_dict.iteritems():
          XmlConfig(filename,
                    conf_dir=conf_tmp_dir,
                    **self.generate_configs_get_xml_file_content(filename, dict)
          )
      for file_dict in env_configs_list:
        for filename,dicts in file_dict.iteritems():
          File(os.path.join(conf_tmp_dir, filename),
               content=InlineTemplate(self.generate_configs_get_template_file_content(filename, dicts)))

      for file_dict in properties_configs_list:
        for filename, dict in file_dict.iteritems():
          PropertiesFile(os.path.join(conf_tmp_dir, filename),
            properties=self.generate_configs_get_xml_file_dict(filename, dict)
          )
      archive_dir(output_filename, conf_tmp_dir)
    finally:
      Directory(conf_tmp_dir, action="delete")
