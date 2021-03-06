/**
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

var App = require('app');
require('views/wizard/controls_view');

describe('App.ServiceConfigRadioButtons', function () {

  describe('#didInsertElement', function () {

    var view = App.ServiceConfigRadioButtons.create({
        categoryConfigsAll: [],
        controller: Em.Object.create({
          wizardController: Em.Object.create({})
        }),
        serviceConfig: Em.Object.create({
          value: null
        })
      }),
      cases = [
        {
          wizardControllerName: 'addServiceController',
          serviceConfigValue: 'New MySQL Database',
          onOptionsChangeCalledTwice: true,
          handleDBConnectionPropertyCalledTwice: false,
          title: 'Add Service Wizard, New MySQL Database'
        },
        {
          wizardControllerName: 'addServiceController',
          serviceConfigValue: 'Existing MySQL Database',
          onOptionsChangeCalledTwice: false,
          handleDBConnectionPropertyCalledTwice: true,
          title: 'Add Service Wizard, Existing MySQL Database'
        },
        {
          wizardControllerName: 'installerController',
          serviceConfigValue: 'New MySQL Database',
          onOptionsChangeCalledTwice: true,
          handleDBConnectionPropertyCalledTwice: false,
          title: 'Install Wizard, New MySQL Database'
        },
        {
          wizardControllerName: 'installerController',
          serviceConfigValue: 'Existing MySQL Database',
          onOptionsChangeCalledTwice: false,
          handleDBConnectionPropertyCalledTwice: true,
          title: 'Install Wizard, Existing MySQL Database'
        },
        {
          wizardControllerName: null,
          serviceConfigValue: null,
          onOptionsChangeCalledTwice: false,
          handleDBConnectionPropertyCalledTwice: false,
          title: 'Service Configs Page'
        }
      ];

    beforeEach(function () {
      sinon.stub(view, 'onOptionsChange', Em.K);
      sinon.stub(view, 'handleDBConnectionProperty', Em.K);
    });

    afterEach(function () {
      view.onOptionsChange.restore();
      view.handleDBConnectionProperty.restore();
    });

    cases.forEach(function (item) {
      it(item.title, function () {
        view.set('controller.wizardController.name', item.wizardControllerName);
        view.set('serviceConfig.value', item.serviceConfigValue);
        view.didInsertElement();
        expect(view.onOptionsChange.calledTwice).to.equal(item.onOptionsChangeCalledTwice);
        expect(view.handleDBConnectionProperty.calledTwice).to.equal(item.handleDBConnectionPropertyCalledTwice);
      });
    });

  });

  describe('#databaseNameProperty', function () {

    var view = App.ServiceConfigRadioButtons.create({
        serviceConfig: Em.Object.create(),
        categoryConfigsAll: [
          {
            name: 'ambari.hive.db.schema.name',
            value: 'db0'
          },
          {
            name: 'sink.db.schema.name',
            value: 'db1'
          },
          {
            name: 'oozie.db.schema.name',
            value: 'db2'
          }
        ]
      }),
      cases = [
        {
          serviceName: 'HIVE',
          value: 'db0'
        },
        {
          serviceName: 'HDFS',
          value: 'db1'
        },
        {
          serviceName: 'OOZIE',
          value: 'db2'
        }
      ];

    cases.forEach(function (item) {
      it(item.serviceName, function () {
        view.set('serviceConfig.serviceName', item.serviceName);
        expect(view.get('databaseNameProperty.value')).to.equal(item.value);
        expect(view.get('databaseName')).to.equal(item.value);
      });
    });

    it('default case', function () {
      view.set('serviceConfig.serviceName', 'YARN');
      expect(view.get('databaseNameProperty')).to.be.null;
      expect(view.get('databaseName')).to.be.null;
    });

  });

  describe('#hostNameProperty', function () {

    var view = App.ServiceConfigRadioButtons.create({
        serviceConfig: Em.Object.create(),
        categoryConfigsAll: [
          {
            name: 'hive_ambari_host',
            value: 'h0'
          },
          {
            name: 'hive_existing_mysql_host',
            value: 'h1'
          },
          {
            name: 'hive_existing_postgresql_host',
            value: 'h2'
          },
          {
            name: 'hive_existing_oracle_host',
            value: 'h3'
          },
          {
            name: 'hive_existing_mssql_server_host',
            value: 'h4'
          },
          {
            name: 'hive_existing_mssql_server_2_host',
            value: 'h5'
          },
          {
            name: 'hive_hostname',
            value: 'h6'
          },
          {
            name: 'sink_existing_mssql_server_host',
            value: 'h7'
          },
          {
            name: 'sink_existing_mssql_server_2_host',
            value: 'h8'
          },
          {
            name: 'sink.dbservername',
            value: 'h9'
          },
          {
            name: 'oozie_ambari_host',
            value: 'h10'
          },
          {
            name: 'oozie_existing_mysql_host',
            value: 'h11'
          },
          {
            name: 'oozie_existing_postgresql_host',
            value: 'h12'
          },
          {
            name: 'oozie_existing_oracle_host',
            value: 'h13'
          },
          {
            name: 'oozie_existing_mssql_server_host',
            value: 'h14'
          },
          {
            name: 'oozie_existing_mssql_server_2_host',
            value: 'h15'
          },
          {
            name: 'oozie_hostname',
            value: 'h16'
          }
        ]
      }),
      cases = [
        {
          serviceName: 'HIVE',
          value: 'New MySQL Database',
          expected: 'h0'
        },
        {
          serviceName: 'HIVE',
          value: 'Existing MySQL Database',
          expected: 'h1'
        },
        {
          serviceName: 'HIVE',
          value: Em.I18n.t('services.service.config.hive.oozie.postgresql'),
          expected: 'h2'
        },
        {
          serviceName: 'HIVE',
          value: 'Existing Oracle Database',
          expected: 'h3'
        },
        {
          serviceName: 'HIVE',
          value: 'Existing MSSQL Server database with integrated authentication',
          expected: 'h4'
        },
        {
          serviceName: 'HIVE',
          value: 'Existing MSSQL Server database with sql auth',
          expected: 'h5'
        },
        {
          serviceName: 'HIVE',
          value: 'default case',
          expected: 'h6'
        },
        {
          serviceName: 'HDFS',
          value: 'Existing MSSQL Server database with integrated authentication',
          expected: 'h7'
        },
        {
          serviceName: 'HDFS',
          value: 'Existing MSSQL Server database with sql auth',
          expected: 'h8'
        },
        {
          serviceName: 'HDFS',
          value: 'default case',
          expected: 'h9'
        },
        {
          serviceName: 'OOZIE',
          value: 'New Derby Database',
          expected: 'h10'
        },
        {
          serviceName: 'OOZIE',
          value: 'Existing MySQL Database',
          expected: 'h11'
        },
        {
          serviceName: 'OOZIE',
          value: Em.I18n.t('services.service.config.hive.oozie.postgresql'),
          expected: 'h12'
        },
        {
          serviceName: 'OOZIE',
          value: 'Existing Oracle Database',
          expected: 'h13'
        },
        {
          serviceName: 'OOZIE',
          value: 'Existing MSSQL Server database with integrated authentication',
          expected: 'h14'
        },
        {
          serviceName: 'OOZIE',
          value: 'Existing MSSQL Server database with sql auth',
          expected: 'h15'
        },
        {
          serviceName: 'OOZIE',
          value: 'default case',
          expected: 'h16'
        }
      ];

    before(function () {
      sinon.stub(view, 'handleDBConnectionProperty', Em.K);
    });

    after(function () {
      view.handleDBConnectionProperty.restore();
    });

    cases.forEach(function (item) {
      it(item.serviceName + ', ' + item.value, function () {
        view.get('serviceConfig').setProperties({
          serviceName: item.serviceName,
          value: item.value
        });
        expect(view.get('hostNameProperty.value')).to.equal(item.expected);
        expect(view.get('hostName')).to.equal(item.expected);
      });
    });

  });

  describe('#onOptionsChange', function () {

    var view = App.ServiceConfigRadioButtons.create({
        hostName: null,
        databaseName: null,
        connectionUrl: Em.Object.create(),
        dbClass: Em.Object.create(),
        serviceConfig: Em.Object.create(),
        categoryConfigsAll: [
          Em.Object.create({
            name: 'javax.jdo.option.ConnectionUserName'
          }),
          Em.Object.create({
            name: 'javax.jdo.option.ConnectionPassword'
          }),
          Em.Object.create({
            name: 'oozie.service.JPAService.jdbc.username'
          }),
          Em.Object.create({
            name: 'oozie.service.JPAService.jdbc.password'
          }),
          Em.Object.create({
            name: 'sink.dblogin'
          }),
          Em.Object.create({
            name: 'sink.dbpassword'
          })
        ],
        parentView: Em.Object.create({
          serviceConfigs: [
            {
              name: 'hive_database_type',
              value: null
            }
          ]
        }),
        configs: [{}]
      }),
      cases = [
        {
          serviceName: 'HIVE',
          serviceConfigValue: 'New MySQL Database',
          databaseName: 'db0',
          hostName: 'h0',
          connectionUrlValue: 'jdbc:mysql://h0/db0?createDatabaseIfNotExist=true',
          dbClassValue: 'com.mysql.jdbc.Driver',
          isAuthVisibleAndRequired: true,
          hiveDbTypeValue: 'mysql'
        },
        {
          serviceName: 'HIVE',
          serviceConfigValue: Em.I18n.t('services.service.config.hive.oozie.postgresql'),
          databaseName: 'db1',
          hostName: 'h1',
          connectionUrlValue: 'jdbc:postgresql://h1:5432/db1',
          dbClassValue: 'org.postgresql.Driver',
          isAuthVisibleAndRequired: true,
          hiveDbTypeValue: 'postgres'
        },
        {
          serviceName: 'HIVE',
          serviceConfigValue: 'Existing MySQL Database',
          databaseName: 'db2',
          hostName: 'h2',
          connectionUrlValue: 'jdbc:mysql://h2/db2?createDatabaseIfNotExist=true',
          dbClassValue: 'com.mysql.jdbc.Driver',
          isAuthVisibleAndRequired: true,
          hiveDbTypeValue: 'mysql'
        },
        {
          serviceName: 'HIVE',
          serviceConfigValue: 'Existing MSSQL Server database with sql auth',
          databaseName: 'db3',
          hostName: 'h3',
          connectionUrlValue: 'jdbc:sqlserver://h3;databaseName=db3',
          dbClassValue: 'com.microsoft.sqlserver.jdbc.SQLServerDriver',
          isAuthVisibleAndRequired: true,
          hiveDbTypeValue: 'mssql'
        },
        {
          serviceName: 'HIVE',
          serviceConfigValue: 'Existing Oracle Database',
          databaseName: 'db4',
          hostName: 'h4',
          connectionUrlValue: 'jdbc:oracle:thin:@//h4:1521/db4',
          dbClassValue: 'oracle.jdbc.driver.OracleDriver',
          isAuthVisibleAndRequired: true,
          hiveDbTypeValue: 'oracle'
        },
        {
          serviceName: 'HIVE',
          serviceConfigValue: 'Existing MSSQL Server database with integrated authentication',
          databaseName: 'db5',
          hostName: 'h5',
          connectionUrlValue: 'jdbc:sqlserver://h5;databaseName=db5;integratedSecurity=true',
          dbClassValue: 'com.microsoft.sqlserver.jdbc.SQLServerDriver',
          isAuthVisibleAndRequired: false,
          hiveDbTypeValue: 'mssql'
        },
        {
          serviceName: 'OOZIE',
          serviceConfigValue: 'New Derby Database',
          databaseName: 'db6',
          hostName: 'h6',
          connectionUrlValue: 'jdbc:derby:${oozie.data.dir}/${oozie.db.schema.name}-db;create=true',
          dbClassValue: 'org.apache.derby.jdbc.EmbeddedDriver',
          isAuthVisibleAndRequired: true
        },
        {
          serviceName: 'OOZIE',
          serviceConfigValue: 'Existing MySQL Database',
          databaseName: 'db7',
          hostName: 'h7',
          connectionUrlValue: 'jdbc:mysql://h7/db7',
          dbClassValue: 'com.mysql.jdbc.Driver',
          isAuthVisibleAndRequired: true
        },
        {
          serviceName: 'OOZIE',
          serviceConfigValue: Em.I18n.t('services.service.config.hive.oozie.postgresql'),
          databaseName: 'db8',
          hostName: 'h8',
          connectionUrlValue: 'jdbc:postgresql://h8:5432/db8',
          dbClassValue: 'org.postgresql.Driver',
          isAuthVisibleAndRequired: true
        },
        {
          serviceName: 'OOZIE',
          serviceConfigValue: 'Existing MSSQL Server database with sql auth',
          databaseName: 'db9',
          hostName: 'h9',
          connectionUrlValue: 'jdbc:sqlserver://h9;databaseName=db9',
          dbClassValue: 'com.microsoft.sqlserver.jdbc.SQLServerDriver',
          isAuthVisibleAndRequired: true
        },
        {
          serviceName: 'OOZIE',
          serviceConfigValue: 'Existing Oracle Database',
          databaseName: 'db10',
          hostName: 'h10',
          connectionUrlValue: 'jdbc:oracle:thin:@//h10:1521/db10',
          dbClassValue: 'oracle.jdbc.driver.OracleDriver',
          isAuthVisibleAndRequired: true
        },
        {
          serviceName: 'OOZIE',
          serviceConfigValue: 'Existing MSSQL Server database with integrated authentication',
          databaseName: 'db11',
          hostName: 'h11',
          connectionUrlValue: 'jdbc:sqlserver://h11;databaseName=db11;integratedSecurity=true',
          dbClassValue: 'com.microsoft.sqlserver.jdbc.SQLServerDriver',
          isAuthVisibleAndRequired: false
        },
        {
          serviceName: 'HDFS',
          serviceConfigValue: 'Existing MSSQL Server database with sql auth',
          databaseName: 'db12',
          hostName: 'h12',
          connectionUrlValue: 'jdbc:sqlserver://h12;databaseName=db12',
          dbClassValue: 'com.microsoft.sqlserver.jdbc.SQLServerDriver',
          isAuthVisibleAndRequired: true
        },
        {
          serviceName: 'HDFS',
          serviceConfigValue: 'Existing MSSQL Server database with integrated authentication',
          databaseName: 'db13',
          hostName: 'h13',
          connectionUrlValue: 'jdbc:sqlserver://h13;databaseName=db13;integratedSecurity=true',
          dbClassValue: 'com.microsoft.sqlserver.jdbc.SQLServerDriver',
          isAuthVisibleAndRequired: false
        }
      ],
      serviceAuthPropsMap = {
        HIVE: ['javax.jdo.option.ConnectionUserName', 'javax.jdo.option.ConnectionPassword'],
        OOZIE: ['oozie.service.JPAService.jdbc.username', 'oozie.service.JPAService.jdbc.password'],
        HDFS: ['sink.dblogin', 'sink.dbpassword']
      };

    before(function () {
      sinon.stub(view, 'handleDBConnectionProperty', Em.K);
    });

    after(function () {
      view.handleDBConnectionProperty.restore();
    });

    cases.forEach(function (item) {
      it(item.serviceName + ', ' + item.serviceConfigValue, function () {
        view.get('serviceConfig').setProperties({
          serviceName: item.serviceName,
          value: item.serviceConfigValue
        });
        view.setProperties({
          databaseName: item.databaseName,
          hostName: item.hostName
        });
        expect(view.get('connectionUrl.value')).to.equal(item.connectionUrlValue);
        expect(view.get('dbClass.value')).to.equal(item.dbClassValue);
        serviceAuthPropsMap[item.serviceName].forEach(function (propName) {
          expect(view.get('categoryConfigsAll').findProperty('name', propName).get('isVisible')).to.equal(item.isAuthVisibleAndRequired);
          expect(view.get('categoryConfigsAll').findProperty('name', propName).get('isRequired')).to.equal(item.isAuthVisibleAndRequired);
        });
        if (item.serviceName == 'HIVE') {
          expect(view.get('parentView.serviceConfigs').findProperty('name', 'hive_database_type').value).to.equal(item.hiveDbTypeValue);
        }
      });
    });

  });

});

describe('App.ServiceConfigRadioButton', function () {

  describe('#disabled', function () {

    var cases = [
      {
        wizardControllerName: 'addServiceController',
        value: 'New MySQL Database',
        title: 'Add Service Wizard, new database',
        disabled: false
      },
      {
        wizardControllerName: 'installerController',
        value: 'New MySQL Database',
        title: 'Install Wizard, new database',
        disabled: false
      },
      {
        wizardControllerName: 'addServiceController',
        value: 'Existing MySQL Database',
        title: 'Add Service Wizard, existing database',
        disabled: false
      },
      {
        wizardControllerName: 'installerController',
        value: 'Existing MySQL Database',
        title: 'Install Wizard, existing database',
        disabled: false
      },
      {
        wizardControllerName: null,
        value: 'New MySQL Database',
        title: 'No installer, new database',
        disabled: true
      },
      {
        wizardControllerName: null,
        value: 'Existing MySQL Database',
        title: 'No installer, existing database',
        disabled: false
      }
    ];

    cases.forEach(function (item) {
      it(item.title, function () {
        var view = App.ServiceConfigRadioButton.create({
          parentView: Em.Object.create({
            serviceConfig: Em.Object.create()
          }),
          controller: Em.Object.create({
            wizardController: Em.Object.create({
              name: null
            })
          })
        });
        view.set('value', item.value);
        view.set('controller.wizardController.name', item.wizardControllerName);
        view.set('parentView.serviceConfig.isEditable', true);
        expect(view.get('disabled')).to.equal(item.disabled);
      });
    });

    it('parent view is disabled', function () {
      var view = App.ServiceConfigRadioButton.create({
        parentView: Em.Object.create({
          serviceConfig: Em.Object.create()
        })
      });
      view.set('parentView.serviceConfig.isEditable', false);
      expect(view.get('disabled')).to.be.true;
    });

  });

});

describe('App.CheckDBConnectionView', function () {

  describe('#masterHostName', function () {

    var cases = [
        {
          serviceName: 'OOZIE',
          value: 'h0'
        },
        {
          serviceName: 'HDFS',
          value: 'h1'
        },
        {
          serviceName: 'HIVE',
          value: 'h2'
        }
      ],
      categoryConfigsAll = [
        Em.Object.create({
          name: 'oozieserver_host',
          value: 'h0'
        }),
        Em.Object.create({
          name: 'hadoop_host',
          value: 'h1'
        }),
        Em.Object.create({
          name: 'hive_ambari_host',
          value: 'h2'
        })
      ];

    cases.forEach(function (item) {
      it(item.serviceName, function () {
        var view = App.CheckDBConnectionView.create({
          parentView: {
            service: {
              serviceName: item.serviceName
            },
            categoryConfigsAll: categoryConfigsAll
          }
        });
        expect(view.get('masterHostName')).to.equal(item.value);
      });
    });

  });

});