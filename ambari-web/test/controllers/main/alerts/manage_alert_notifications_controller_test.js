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
var controller;
var helpers = require('test/helpers');

describe('App.ManageAlertNotificationsController', function () {

  beforeEach(function () {
    controller = App.ManageAlertNotificationsController.create({});
    sinon.stub(App.ajax, 'send');
  });

  afterEach(function () {
    App.ajax.send.restore();
  });

  describe('#alertNotifications', function () {

    beforeEach(function () {
      sinon.stub(App.AlertNotification, 'find', function () {
        return [1, 2, 3];
      });
    });

    afterEach(function () {
      App.AlertNotification.find.restore();
    });

    it("should return all alert notifications if controller isLoaded", function () {

      controller.set('isLoaded', true);
      expect(controller.get('alertNotifications')).to.eql([1, 2, 3]);
    });

    it("should return [] if controller isLoaded=false", function () {

      controller.set('isLoaded', false);
      expect(controller.get('alertNotifications')).to.eql([]);
    });

  });

  describe('#loadAlertNotifications()', function () {

    it("should send ajax request and set isLoaded to false", function () {

      controller.set('isLoaded', true);
      controller.loadAlertNotifications();
      expect(controller.get('isLoaded')).to.be.false;
    });

  });

  describe('#getAlertNotificationsSuccessCallback()', function () {

    beforeEach(function () {
      sinon.spy(App.alertNotificationMapper, 'map');
    });

    afterEach(function () {
      App.alertNotificationMapper.map.restore();
    });

    it("should call mapper and set isLoaded to true", function () {

      controller.set('isLoaded', false);
      controller.getAlertNotificationsSuccessCallback('test');
      expect(controller.get('isLoaded')).to.be.true;
      expect(App.alertNotificationMapper.map.calledWith('test')).to.be.true;
    });

  });

  describe('#getAlertNotificationsErrorCallback()', function () {

    it("should set isLoaded to true", function () {

      controller.set('isLoaded', false);
      controller.getAlertNotificationsSuccessCallback('test');
      expect(controller.get('isLoaded')).to.be.true;
    });

  });

  describe('#addAlertNotification()', function () {

    beforeEach(function () {
      sinon.stub(controller, 'showCreateEditPopup');
    });

    afterEach(function () {
      controller.showCreateEditPopup.restore();
    });

    it("should set value for inputFields and call showCreateEditPopup", function () {

      controller.set('inputFields', Em.Object.create({
        a: {
          value: '',
          defaultValue: 'a'
        },
        b: {
          value: '',
          defaultValue: 'b'
        },
        c: {
          value: '',
          defaultValue: 'c'
        },
        severityFilter: {
          value: [],
          defaultValue: ['OK', 'WARNING', 'CRITICAL', 'UNKNOWN']
        },
        global: {
          value: false
        },
        allGroups: Em.Object.create({
          value: 'custom'
        })
      }));
      controller.addAlertNotification();

      Em.keys(controller.get('inputFields')).forEach(function (key) {
        expect(controller.get('inputFields.' + key + '.value')).to.eql(controller.get('inputFields.' + key + '.defaultValue'));
      });
      expect(controller.showCreateEditPopup.calledOnce).to.be.true;
    });

  });

  describe('#editAlertNotification()', function () {

    beforeEach(function () {
      sinon.stub(controller, 'showCreateEditPopup', Em.K);
      sinon.stub(controller, 'fillEditCreateInputs', Em.K);
    });

    afterEach(function () {
      controller.showCreateEditPopup.restore();
      controller.fillEditCreateInputs.restore();
    });

    it("should call fillEditCreateInputs and showCreateEditPopup", function () {

      controller.editAlertNotification();

      expect(controller.fillEditCreateInputs.calledOnce).to.be.true;
      expect(controller.showCreateEditPopup.calledWith(true)).to.be.true;
    });

  });

  describe('#fillEditCreateInputs()', function () {

    it("should map properties from selectedAlertNotification to inputFields (ambari.dispatch.recipients ignored)", function () {

      controller.set('selectedAlertNotification', Em.Object.create({
        name: 'test_name',
        global: true,
        description: 'test_description',
        groups: ['test1', 'test2'],
        type: 'EMAIL',
        alertStates: ['OK', 'UNKNOWN'],
        properties: {
          'ambari.dispatch.recipients': [
            'test1@test.test',
            'test2@test.test'
          ],
          'customName': 'customValue',
          "mail.smtp.from" : "from",
          "ambari.dispatch.credential.username" : "user",
          "mail.smtp.host" : "s1",
          "mail.smtp.port" : "25",
          "mail.smtp.auth" : "true",
          "ambari.dispatch.credential.password" : "pass",
          "mail.smtp.starttls.enable" : "true"
        }
      }));

      controller.set('inputFields', Em.Object.create({
        name: {
          value: ''
        },
        groups: {
          value: []
        },
        global: {
          value: false
        },
        allGroups: {
          value: false
        },
        method: {
          value: ''
        },
        email: {
          value: ''
        },
        severityFilter: {
          value: []
        },
        description: {
          value: ''
        },
        SMTPServer: {
          value: ''
        },
        SMTPPort: {
          value: ''
        },
        SMTPUseAuthentication: {
          value: ''
        },
        SMTPUsername: {
          value: ''
        },
        SMTPPassword: {
          value: ''
        },
        SMTPSTARTTLS: {
          value: ''
        },
        emailFrom: {
          value: ''
        },
        version: {
          value: ''
        },
        OIDs: {
          value: ''
        },
        community: {
          value: ''
        },
        port: {
          value: ''
        },
        customProperties: [
          {name: 'customName', value: 'customValue1', defaultValue: 'customValue1'},
          {name: 'customName2', value: 'customValue1', defaultValue: 'customValue1'}
        ]
      }));

      controller.fillEditCreateInputs();

      expect(JSON.stringify(controller.get('inputFields'))).to.equal(JSON.stringify({
        name: {
          value: 'test_name'
        },
        groups: {
          value: ['test1', 'test2']
        },
        global: {
          value: true,
          disabled: true
        },
        allGroups: {
          value: 'all'
        },
        method: {
          value: 'EMAIL'
        },
        email: {
          value: 'test1@test.test, test2@test.test'
        },
        severityFilter: {
          value: ['OK', 'UNKNOWN']
        },
        description: {
          value: 'test_description'
        },
        SMTPServer: {
          value: 's1'
        },
        SMTPPort: {
          value: '25'
        },
        SMTPUseAuthentication: {
          value: "true"
        },
        SMTPUsername: {
          value: 'user'
        },
        SMTPPassword: {
          value: 'pass'
        },
        SMTPSTARTTLS: {
          value: "true"
        },
        emailFrom: {
          value: 'from'
        },
        version: {},
        OIDs: {},
        community: {},
        port: {},
        customProperties: [
          {name: 'customName', value: 'customValue', defaultValue: 'customValue'}
        ]
      }));

    });

  });

  describe("#showCreateEditPopup()", function () {

    beforeEach(function () {
      sinon.spy(App.ModalPopup, 'show');
    });

    afterEach(function () {
      App.ModalPopup.show.restore();
    });

    it("should open popup and set popup object to createEditPopup", function () {

      controller.showCreateEditPopup();
      expect(App.ModalPopup.show.calledOnce).to.be.true;

    });

    describe('#bodyClass', function () {

      var view;

      beforeEach(function () {

        view = controller.showCreateEditPopup().get('bodyClass').create({
          controller: Em.Object.create({
            inputFields: {
              global: {},
              allGroups: {}
            }
          }),
          groupSelect: Em.Object.create({
            selection: [],
            content: [{}, {}]
          })
        });

      });

      describe('#selectAllGroups', function () {

        it('should check inputFields.allGroups.value', function () {

          view.set('controller.inputFields.allGroups.value', 'all');
          view.selectAllGroups();
          expect(view.get('groupSelect.selection')).to.eql([]);

          view.set('controller.inputFields.allGroups.value', 'custom');
          view.selectAllGroups();
          expect(view.get('groupSelect.selection')).to.eql([{}, {}]);

        });

      });

      describe('#clearAllGroups', function () {

        it('should check inputFields.allGroups.value', function () {

          view.set('controller.inputFields.allGroups.value', 'custom');
          view.selectAllGroups();

          view.set('controller.inputFields.allGroups.value', 'all');
          view.clearAllGroups();
          expect(view.get('groupSelect.selection')).to.eql([{}, {}]);

          view.set('controller.inputFields.allGroups.value', 'custom');
          view.clearAllGroups();
          expect(view.get('groupSelect.selection')).to.eql([]);

        });

      });

    });

  });

  describe("#formatNotificationAPIObject()", function () {

    var inputFields = Em.Object.create({
      name: {
        value: 'test_name'
      },
      groups: {
        value: [{id: 1}, {id: 2}, {id: 3}]
      },
      allGroups: {
        value: 'custom'
      },
      global: {
        value: false
      },
      method: {
        value: 'EMAIL'
      },
      email: {
        value: 'test1@test.test, test2@test.test,test3@test.test , test4@test.test'
      },
      severityFilter: {
        value: ['OK', 'CRITICAL']
      },
      SMTPServer: {
        value: 's1'
      },
      SMTPPort: {
        value: '25'
      },
      SMTPUseAuthentication: {
        value: "true"
      },
      SMTPUsername: {
        value: 'user'
      },
      SMTPPassword: {
        value: 'pass'
      },
      SMTPSTARTTLS: {
        value: "true"
      },
      emailFrom: {
        value: 'from'
      },
      description: {
        value: 'test_description'
      },
      customProperties: [
        {name: 'n1', value: 'v1'},
        {name: 'n2', value: 'v2'}
      ]
    });

    it("should create object with properties from inputFields values", function () {

      controller.set('inputFields', inputFields);

      var result = controller.formatNotificationAPIObject();

      expect(JSON.stringify(result)).to.eql(JSON.stringify({
        AlertTarget: {
          name: 'test_name',
          description: 'test_description',
          global: false,
          notification_type: 'EMAIL',
          alert_states: ['OK', 'CRITICAL'],
          properties: {
            'ambari.dispatch.recipients': [
              'test1@test.test',
              'test2@test.test',
              'test3@test.test',
              'test4@test.test'
            ],
            "mail.smtp.host" : "s1",
            "mail.smtp.port" : "25",
            "mail.smtp.from" : "from",
            "mail.smtp.auth" : "true",
            "ambari.dispatch.credential.username" : "user",
            "ambari.dispatch.credential.password" : "pass",
            "mail.smtp.starttls.enable" : "true",
            'n1': 'v1',
            'n2': 'v2'
          },
          groups: [1,2,3]
        }
      }));
    });

    it('should ignore groups if global is true', function () {

      controller.set('inputFields', inputFields);
      controller.set('inputFields.allGroups.value', 'all');

      var result = controller.formatNotificationAPIObject();
      expect(Em.keys(result.AlertTarget)).to.not.contain('groups');

    });

  });

  describe('#createAlertNotification()', function () {

    it("should send ajax request", function () {

      controller.createAlertNotification();
      expect(App.ajax.send.calledOnce).to.be.true;
    });

  });

  describe('#createAlertNotificationSuccessCallback()', function () {

    beforeEach(function () {
      controller.set('createEditPopup', {
        hide: Em.K
      });
      sinon.stub(controller, 'loadAlertNotifications', Em.K);
      sinon.spy(controller.createEditPopup, 'hide');
    });

    afterEach(function () {
      controller.loadAlertNotifications.restore();
      controller.createEditPopup.hide.restore();
    });

    it("should call loadAlertNotifications and createEditPopup.hide", function () {

      controller.createAlertNotificationSuccessCallback();

      expect(controller.loadAlertNotifications.calledOnce).to.be.true;
      expect(controller.createEditPopup.hide.calledOnce).to.be.true;
    });

  });

  describe('#updateAlertNotification()', function () {

    it("should send ajax request", function () {

      controller.updateAlertNotification();
      expect(App.ajax.send.calledOnce).to.be.true;
    });

  });

  describe('#updateAlertNotificationSuccessCallback()', function () {

    beforeEach(function () {
      controller.set('createEditPopup', {
        hide: Em.K
      });
      sinon.stub(controller, 'loadAlertNotifications', Em.K);
      sinon.spy(controller.createEditPopup, 'hide');
    });

    afterEach(function () {
      controller.loadAlertNotifications.restore();
      controller.createEditPopup.hide.restore();
    });

    it("should call loadAlertNotifications and createEditPopup.hide", function () {

      controller.updateAlertNotificationSuccessCallback();

      expect(controller.loadAlertNotifications.calledOnce).to.be.true;
      expect(controller.createEditPopup.hide.calledOnce).to.be.true;
    });

  });

  describe('#deleteAlertNotification()', function () {

    beforeEach(function () {
      sinon.spy(App, 'showConfirmationPopup');
    });

    afterEach(function () {
      App.showConfirmationPopup.restore();
    });

    it("should show popup and send request on confirmation", function () {

      var popup = controller.deleteAlertNotification();

      expect(App.showConfirmationPopup.calledOnce).to.be.true;
      popup.onPrimary();
      expect(App.ajax.send.calledOnce).to.be.true;
    });

  });

  describe('#deleteAlertNotificationSuccessCallback()', function () {

    it("should call loadAlertNotifications, selectedAlertNotification.deleteRecord and set null to selectedAlertNotification", function () {

      var mockSelectedAlertNotification = {
        deleteRecord: Em.K
      };
      controller.set('selectedAlertNotification', mockSelectedAlertNotification);
      sinon.stub(controller, 'loadAlertNotifications', Em.K);
      sinon.spy(mockSelectedAlertNotification, 'deleteRecord');

      controller.deleteAlertNotificationSuccessCallback();

      expect(controller.loadAlertNotifications.calledOnce).to.be.true;
      expect(mockSelectedAlertNotification.deleteRecord.calledOnce).to.be.true;
      expect(controller.get('selectedAlertNotification')).to.equal(null);

      controller.loadAlertNotifications.restore();
      mockSelectedAlertNotification.deleteRecord.restore();
    });

  });

  describe('#duplicateAlertNotification()', function () {

    beforeEach(function () {
      sinon.stub(controller, 'fillEditCreateInputs', Em.K);
      sinon.stub(controller, 'showCreateEditPopup', Em.K);
    });

    afterEach(function () {
      controller.fillEditCreateInputs.restore();
      controller.showCreateEditPopup.restore();
    });

    it("should call fillEditCreateInputs and showCreateEditPopup", function () {

      controller.duplicateAlertNotification();

      expect(controller.fillEditCreateInputs.calledWith(true)).to.be.true;
      expect(controller.showCreateEditPopup.calledOnce).to.be.true;
    });

  });

  describe('#addCustomProperty', function () {

    beforeEach(function () {
      controller.set('inputFields.customProperties', []);
    });

    it('should add custom Property to customProperties', function () {

      controller.set('newCustomProperty', {name: 'n1', value: 'v1'});
      controller.addCustomProperty();
      helpers.nestedExpect([{name: 'n1', value: 'v1', defaultValue: 'v1'}], controller.get('inputFields.customProperties'));

    });

  });

  describe('#removeCustomPropertyHandler', function () {

    var c = {name: 'n2', value: 'v2', defaultValue: 'v2'};

    beforeEach(function () {
      controller.set('inputFields.customProperties', [
        {name: 'n1', value: 'v1', defaultValue: 'v1'},
        c,
        {name: 'n3', value: 'v3', defaultValue: 'v3'}
      ]);
    });

    it('should remove selected custom property', function () {

      controller.removeCustomPropertyHandler({context: c});
      helpers.nestedExpect(
        [
          {name: 'n1', value: 'v1', defaultValue: 'v1'},
          {name: 'n3', value: 'v3', defaultValue: 'v3'}
        ],
        controller.get('inputFields.customProperties')
      );

    });

  });

  describe('#addCustomPropertyHandler', function () {

    it('should clean up newCustomProperty on primary click', function () {

      controller.set('newCustomProperty', {name: 'n1', value: 'v1'});
      controller.addCustomPropertyHandler().onPrimary();
      expect(controller.get('newCustomProperty')).to.eql({name: '', value: ''});

    });

    describe('#bodyClass', function () {

      var view;

      beforeEach(function () {
        view = controller.addCustomPropertyHandler().get('bodyClass').create({
          parentView: Em.View.create(),
          controller: Em.Object.create({
            inputFields: Em.Object.create({
              customProperties: [
                {name: 'n1', value: 'v1', defaultValue: 'v1'}
              ]
            }),
            newCustomProperty: {name: '', value: ''}
          })
        });
      });

      describe('#errorHandler', function () {

        it('should fire invalid name', function () {

          view.set('controller.newCustomProperty.name', '!!');
          view.errorsHandler();
          expect(view.get('isError')).to.be.true;
          expect(view.get('parentView.disablePrimary')).to.be.true;
          expect(view.get('errorMessage.length') > 0).to.be.true;

        });

        it('should fire existing property name', function () {

          view.set('controller.newCustomProperty.name', 'n1');
          view.errorsHandler();
          expect(view.get('isError')).to.be.true;
          expect(view.get('parentView.disablePrimary')).to.be.true;
          expect(view.get('errorMessage.length') > 0).to.be.true;

        });

      });

    });

  });

});
