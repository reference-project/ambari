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

package org.apache.ambari.server.controller;

import static org.eclipse.persistence.config.PersistenceUnitProperties.CREATE_JDBC_DDL_FILE;
import static org.eclipse.persistence.config.PersistenceUnitProperties.CREATE_ONLY;
import static org.eclipse.persistence.config.PersistenceUnitProperties.CREATE_OR_EXTEND;
import static org.eclipse.persistence.config.PersistenceUnitProperties.DDL_BOTH_GENERATION;
import static org.eclipse.persistence.config.PersistenceUnitProperties.DDL_GENERATION;
import static org.eclipse.persistence.config.PersistenceUnitProperties.DDL_GENERATION_MODE;
import static org.eclipse.persistence.config.PersistenceUnitProperties.DROP_AND_CREATE;
import static org.eclipse.persistence.config.PersistenceUnitProperties.DROP_JDBC_DDL_FILE;
import static org.eclipse.persistence.config.PersistenceUnitProperties.JDBC_DRIVER;
import static org.eclipse.persistence.config.PersistenceUnitProperties.JDBC_PASSWORD;
import static org.eclipse.persistence.config.PersistenceUnitProperties.JDBC_URL;
import static org.eclipse.persistence.config.PersistenceUnitProperties.JDBC_USER;
import static org.eclipse.persistence.config.PersistenceUnitProperties.THROW_EXCEPTIONS;

import java.lang.annotation.Annotation;
import java.security.SecureRandom;
import java.text.MessageFormat;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Properties;
import java.util.Set;

import org.apache.ambari.server.AmbariService;
import org.apache.ambari.server.EagerSingleton;
import org.apache.ambari.server.StaticallyInject;
import org.apache.ambari.server.actionmanager.ActionDBAccessor;
import org.apache.ambari.server.actionmanager.ActionDBAccessorImpl;
import org.apache.ambari.server.actionmanager.ExecutionCommandWrapper;
import org.apache.ambari.server.actionmanager.HostRoleCommandFactory;
import org.apache.ambari.server.actionmanager.HostRoleCommandFactoryImpl;
import org.apache.ambari.server.actionmanager.RequestFactory;
import org.apache.ambari.server.actionmanager.StageFactory;
import org.apache.ambari.server.configuration.Configuration;
import org.apache.ambari.server.controller.internal.ComponentResourceProvider;
import org.apache.ambari.server.controller.internal.HostComponentResourceProvider;
import org.apache.ambari.server.controller.internal.HostResourceProvider;
import org.apache.ambari.server.controller.internal.MemberResourceProvider;
import org.apache.ambari.server.controller.internal.RepositoryVersionResourceProvider;
import org.apache.ambari.server.controller.internal.ServiceResourceProvider;
import org.apache.ambari.server.controller.spi.ResourceProvider;
import org.apache.ambari.server.orm.DBAccessor;
import org.apache.ambari.server.orm.DBAccessorImpl;
import org.apache.ambari.server.orm.PersistenceType;
import org.apache.ambari.server.scheduler.ExecutionScheduler;
import org.apache.ambari.server.scheduler.ExecutionSchedulerImpl;
import org.apache.ambari.server.security.SecurityHelper;
import org.apache.ambari.server.security.SecurityHelperImpl;
import org.apache.ambari.server.state.Cluster;
import org.apache.ambari.server.state.Clusters;
import org.apache.ambari.server.state.Config;
import org.apache.ambari.server.state.ConfigFactory;
import org.apache.ambari.server.state.ConfigImpl;
import org.apache.ambari.server.state.Host;
import org.apache.ambari.server.state.Service;
import org.apache.ambari.server.state.ServiceComponent;
import org.apache.ambari.server.state.ServiceComponentFactory;
import org.apache.ambari.server.state.ServiceComponentHost;
import org.apache.ambari.server.state.ServiceComponentHostFactory;
import org.apache.ambari.server.state.ServiceComponentImpl;
import org.apache.ambari.server.state.ServiceFactory;
import org.apache.ambari.server.state.ServiceImpl;
import org.apache.ambari.server.state.cluster.ClusterFactory;
import org.apache.ambari.server.state.cluster.ClusterImpl;
import org.apache.ambari.server.state.cluster.ClustersImpl;
import org.apache.ambari.server.state.configgroup.ConfigGroup;
import org.apache.ambari.server.state.configgroup.ConfigGroupFactory;
import org.apache.ambari.server.state.configgroup.ConfigGroupImpl;
import org.apache.ambari.server.state.host.HostFactory;
import org.apache.ambari.server.state.host.HostImpl;
import org.apache.ambari.server.state.scheduler.RequestExecution;
import org.apache.ambari.server.state.scheduler.RequestExecutionFactory;
import org.apache.ambari.server.state.scheduler.RequestExecutionImpl;
import org.apache.ambari.server.state.stack.OsFamily;
import org.apache.ambari.server.state.svccomphost.ServiceComponentHostImpl;
import org.apache.ambari.server.view.ViewInstanceHandlerList;
import org.eclipse.jetty.server.SessionIdManager;
import org.eclipse.jetty.server.SessionManager;
import org.eclipse.jetty.server.session.HashSessionIdManager;
import org.eclipse.jetty.server.session.HashSessionManager;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.config.BeanDefinition;
import org.springframework.context.annotation.ClassPathScanningCandidateComponentProvider;
import org.springframework.core.type.filter.AnnotationTypeFilter;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.crypto.password.StandardPasswordEncoder;
import org.springframework.util.ClassUtils;
import org.springframework.web.filter.DelegatingFilterProxy;

import com.google.common.util.concurrent.AbstractScheduledService;
import com.google.common.util.concurrent.ServiceManager;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.inject.AbstractModule;
import com.google.inject.Scopes;
import com.google.inject.assistedinject.FactoryModuleBuilder;
import com.google.inject.name.Names;
import com.google.inject.persist.PersistModule;
import com.google.inject.persist.jpa.AmbariJpaPersistModule;

/**
 * Used for injection purposes.
 */
public class ControllerModule extends AbstractModule {
  private static Logger LOG = LoggerFactory.getLogger(ControllerModule.class);

  private final Configuration configuration;
  private final OsFamily os_family;
  private final HostsMap hostsMap;
  private boolean dbInitNeeded;
  private final Gson prettyGson = new GsonBuilder().serializeNulls().setPrettyPrinting().create();


  // ----- Constructors ------------------------------------------------------

  public ControllerModule() throws Exception {
    configuration = new Configuration();
    hostsMap = new HostsMap(configuration);
    os_family = new OsFamily(configuration);
  }

  public ControllerModule(Properties properties) throws Exception {
    configuration = new Configuration(properties);
    hostsMap = new HostsMap(configuration);
    os_family = new OsFamily(configuration);
  }


  // ----- ControllerModule --------------------------------------------------

  /**
   * Get the common persistence related configuration properties.
   *
   * @return the configuration properties
   */
  public static Properties getPersistenceProperties(Configuration configuration) {
    Properties properties = new Properties();

    // custom jdbc properties
    Map<String, String> custom = configuration.getDatabaseCustomProperties();

    if (0 != custom.size()) {
      for (Entry<String, String> entry : custom.entrySet()) {
        properties.setProperty("eclipselink.jdbc.property." + entry.getKey(),
            entry.getValue());
      }
    }

    switch (configuration.getPersistenceType()) {
      case IN_MEMORY:
        properties.setProperty(JDBC_URL, Configuration.JDBC_IN_MEMORY_URL);
        properties.setProperty(JDBC_DRIVER, Configuration.JDBC_IN_MEMROY_DRIVER);
        properties.setProperty(DDL_GENERATION, DROP_AND_CREATE);
        properties.setProperty(THROW_EXCEPTIONS, "true");
      case REMOTE:
        properties.setProperty(JDBC_URL, configuration.getDatabaseUrl());
        properties.setProperty(JDBC_DRIVER, configuration.getDatabaseDriver());
        break;
      case LOCAL:
        properties.setProperty(JDBC_URL, configuration.getLocalDatabaseUrl());
        properties.setProperty(JDBC_DRIVER, Configuration.JDBC_LOCAL_DRIVER);
        break;
    }
    return properties;
  }


  // ----- AbstractModule ----------------------------------------------------

  @Override
  protected void configure() {
    installFactories();

    final SessionIdManager sessionIdManager = new HashSessionIdManager();
    final SessionManager sessionManager = new HashSessionManager();
    sessionManager.setSessionPath("/");
    sessionManager.setSessionIdManager(sessionIdManager);
    bind(SessionManager.class).toInstance(sessionManager);
    bind(SessionIdManager.class).toInstance(sessionIdManager);

    bind(Configuration.class).toInstance(configuration);
    bind(OsFamily.class).toInstance(os_family);
    bind(HostsMap.class).toInstance(hostsMap);
    bind(PasswordEncoder.class).toInstance(new StandardPasswordEncoder());
    bind(DelegatingFilterProxy.class).toInstance(new DelegatingFilterProxy() {
      {
        setTargetBeanName("springSecurityFilterChain");
      }
    });
    bind(Gson.class).annotatedWith(Names.named("prettyGson")).toInstance(prettyGson);

    install(buildJpaPersistModule());

    bind(Gson.class).in(Scopes.SINGLETON);
    bind(SecureRandom.class).in(Scopes.SINGLETON);

    bind(Clusters.class).to(ClustersImpl.class);
    bind(AmbariCustomCommandExecutionHelper.class);
    bind(ActionDBAccessor.class).to(ActionDBAccessorImpl.class);
    bindConstant().annotatedWith(Names.named("schedulerSleeptime")).to(10000L);

    // This time is added to summary timeout time of all tasks in stage
    // So it's an "additional time", given to stage to finish execution before
    // it is considered as timed out
    bindConstant().annotatedWith(Names.named("actionTimeout")).to(600000L);

    bindConstant().annotatedWith(Names.named("dbInitNeeded")).to(dbInitNeeded);
    bindConstant().annotatedWith(Names.named("statusCheckInterval")).to(5000L);

    //ExecutionCommands cache size

    bindConstant().annotatedWith(Names.named("executionCommandCacheSize")).
        to(configuration.getExecutionCommandsCacheSize());

    bind(AmbariManagementController.class)
        .to(AmbariManagementControllerImpl.class);
    bind(AbstractRootServiceResponseFactory.class).to(RootServiceResponseFactory.class);
    bind(ExecutionScheduler.class).to(ExecutionSchedulerImpl.class);
    bind(DBAccessor.class).to(DBAccessorImpl.class);
    bind(ViewInstanceHandlerList.class).to(AmbariHandlerList.class);

    requestStaticInjection(ExecutionCommandWrapper.class);

    bindByAnnotation(null);
  }


  // ----- helper methods ----------------------------------------------------

  private PersistModule buildJpaPersistModule() {
    PersistenceType persistenceType = configuration.getPersistenceType();
    AmbariJpaPersistModule jpaPersistModule = new AmbariJpaPersistModule(Configuration.JDBC_UNIT_NAME);

    Properties persistenceProperties = getPersistenceProperties(configuration);

    if (!persistenceType.equals(PersistenceType.IN_MEMORY)) {
      persistenceProperties.setProperty(JDBC_USER, configuration.getDatabaseUser());
      persistenceProperties.setProperty(JDBC_PASSWORD, configuration.getDatabasePassword());

      switch (configuration.getJPATableGenerationStrategy()) {
        case CREATE:
          persistenceProperties.setProperty(DDL_GENERATION, CREATE_ONLY);
          dbInitNeeded = true;
          break;
        case DROP_AND_CREATE:
          persistenceProperties.setProperty(DDL_GENERATION, DROP_AND_CREATE);
          dbInitNeeded = true;
          break;
        case CREATE_OR_EXTEND:
          persistenceProperties.setProperty(DDL_GENERATION, CREATE_OR_EXTEND);
          break;
        default:
          break;
      }

      persistenceProperties.setProperty(DDL_GENERATION_MODE, DDL_BOTH_GENERATION);
      persistenceProperties.setProperty(CREATE_JDBC_DDL_FILE, "DDL-create.jdbc");
      persistenceProperties.setProperty(DROP_JDBC_DDL_FILE, "DDL-drop.jdbc");
    }

    jpaPersistModule.properties(persistenceProperties);

    return jpaPersistModule;
  }

  private void installFactories() {
    install(new FactoryModuleBuilder().implement(
        Cluster.class, ClusterImpl.class).build(ClusterFactory.class));
    install(new FactoryModuleBuilder().implement(
        Host.class, HostImpl.class).build(HostFactory.class));
    install(new FactoryModuleBuilder().implement(
        Service.class, ServiceImpl.class).build(ServiceFactory.class));


    install(new FactoryModuleBuilder()
        .implement(ResourceProvider.class, Names.named("host"), HostResourceProvider.class)
        .implement(ResourceProvider.class, Names.named("hostComponent"), HostComponentResourceProvider.class)
        .implement(ResourceProvider.class, Names.named("service"), ServiceResourceProvider.class)
        .implement(ResourceProvider.class, Names.named("component"), ComponentResourceProvider.class)
        .implement(ResourceProvider.class, Names.named("member"), MemberResourceProvider.class)
        .implement(ResourceProvider.class, Names.named("repositoryVersion"), RepositoryVersionResourceProvider.class)
        .build(ResourceProviderFactory.class));


    install(new FactoryModuleBuilder().implement(
        ServiceComponent.class, ServiceComponentImpl.class).build(
        ServiceComponentFactory.class));
    install(new FactoryModuleBuilder().implement(
        ServiceComponentHost.class, ServiceComponentHostImpl.class).build(
        ServiceComponentHostFactory.class));
    install(new FactoryModuleBuilder().implement(
        Config.class, ConfigImpl.class).build(ConfigFactory.class));
    install(new FactoryModuleBuilder().implement(
        ConfigGroup.class, ConfigGroupImpl.class).build(ConfigGroupFactory.class));
    install(new FactoryModuleBuilder().implement(RequestExecution.class,
        RequestExecutionImpl.class).build(RequestExecutionFactory.class));
    install(new FactoryModuleBuilder().build(StageFactory.class));
    install(new FactoryModuleBuilder().build(RequestFactory.class));

    bind(HostRoleCommandFactory.class).to(HostRoleCommandFactoryImpl.class);
    bind(SecurityHelper.class).toInstance(SecurityHelperImpl.getInstance());
  }

  /**
   * Initializes specially-marked interfaces that require injection.
   * <p/>
   * An example of where this is needed is with a singleton that is headless; in
   * other words, it doesn't have any injections but still needs to be part of
   * the Guice framework.
   * <p/>
   * A second example of where this is needed is when classes require static
   * members that are available via injection.
   * <p/>
   * If {@code beanDefinitions} is empty or null this will scan 
   * {@code org.apache.ambari.server} (currently) for any {@link EagerSingleton}
   * or {@link StaticallyInject} or {@link AmbariService} instances.
   *
   * @param beanDefinitions the set of bean definitions. If it is empty or
   *                        {@code null} scan will occur.
   *
   * @return the set of bean definitions that was found during scan if
   *         {@code beanDefinitions} was null or empty. Else original
   *         {@code beanDefinitions} will be returned.
   *
   */
  // Method is protected and returns a set of bean definitions for testing convenience.
  @SuppressWarnings("unchecked")
  protected Set<BeanDefinition> bindByAnnotation(Set<BeanDefinition> beanDefinitions) {
    List<Class<? extends Annotation>> classes = Arrays.asList(
        EagerSingleton.class, StaticallyInject.class, AmbariService.class);

    if (null == beanDefinitions || beanDefinitions.size() == 0) {
      ClassPathScanningCandidateComponentProvider scanner =
          new ClassPathScanningCandidateComponentProvider(false);

      // match only singletons that are eager listeners
      for (Class<? extends Annotation> cls : classes) {
        scanner.addIncludeFilter(new AnnotationTypeFilter(cls));
      }

      beanDefinitions = scanner.findCandidateComponents("org.apache.ambari.server");
    }

    if (null == beanDefinitions || beanDefinitions.size() == 0) {
      LOG.warn("No instances of {} found to register", classes);
      return beanDefinitions;
    }

    Set<com.google.common.util.concurrent.Service> services =
        new HashSet<com.google.common.util.concurrent.Service>();

    for (BeanDefinition beanDefinition : beanDefinitions) {
      String className = beanDefinition.getBeanClassName();
      Class<?> clazz = ClassUtils.resolveClassName(className,
          ClassUtils.getDefaultClassLoader());

      if (null != clazz.getAnnotation(EagerSingleton.class)) {
        bind(clazz).asEagerSingleton();
        LOG.debug("Binding singleton {} eagerly", clazz);
      }

      if (null != clazz.getAnnotation(StaticallyInject.class)) {
        requestStaticInjection(clazz);
        LOG.debug("Statically injecting {} ", clazz);
      }

      // Ambari services are registered with Guava
      if (null != clazz.getAnnotation(AmbariService.class)) {
        // safety check to ensure it's actually a Guava service
        if (!AbstractScheduledService.class.isAssignableFrom(clazz)) {
          String message = MessageFormat.format(
              "Unable to register service {0} because it is not an AbstractScheduledService",
              clazz);

          LOG.warn(message);
          throw new RuntimeException(message);
        }

        // instantiate the service, register as singleton via toInstance()
        AbstractScheduledService service = null;
        try {
          service = (AbstractScheduledService) clazz.newInstance();
          bind((Class<AbstractScheduledService>) clazz).toInstance(service);
          services.add(service);
          LOG.debug("Registering service {} ", clazz);
        } catch (Exception exception) {
          LOG.error("Unable to register {} as a service", clazz, exception);
          throw new RuntimeException(exception);
        }
      }
    }

    ServiceManager manager = new ServiceManager(services);
    bind(ServiceManager.class).toInstance(manager);

    return beanDefinitions;
  }
}