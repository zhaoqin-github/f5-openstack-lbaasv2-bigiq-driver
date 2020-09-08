import os
import sys

from oslo_config import cfg
from oslo_log import helpers as log_helpers
from oslo_log import log as logging

from neutron.db.models import agent as agents_db
from neutron_lbaas import agent_scheduler

from neutron_lib import constants as q_const
from neutron_lib.callbacks import events
from neutron_lib.callbacks import registry
from neutron_lib.callbacks import resources

from f5_lbaasv2_bigiq_driver import agent_rpc
from f5_lbaasv2_bigiq_driver import constants
from f5_lbaasv2_bigiq_driver import exceptions
from f5_lbaasv2_bigiq_driver import plugin_rpc

LOG = logging.getLogger(__name__)

OPTS = [
    cfg.StrOpt(
        'f5_bigiq_agent_scheduler',
        default=(
            'f5_lbaasv2_bigiq_driver.agent_scheduler.TenantScheduler'
        ),
        help=('Driver to use for scheduling loadbalancer to a BIG-IQ agent')
    )
]

cfg.CONF.register_opts(OPTS)


class BIGIQDriver(object):

    def __init__(self, plugin=None):
        """Driver initialization."""
        if not plugin:
            LOG.error('Required LBaaS Driver and Core Driver Missing')
            sys.exit(1)

        self.plugin = plugin
        self.agent_rpc = agent_rpc.BIGIQAgentRPC(self)
        self.plugin_rpc = plugin_rpc.LBaaSv2PluginCallbacksRPC(self)

        self.loadbalancer = LoadBalancerManager(self)
        self.listener = ListenerManager(self)
        self.pool = PoolManager(self)
        self.member = MemberManager(self)
        self.health_monitor = HealthMonitorManager(self)
        self.l7policy = L7PolicyManager(self)
        self.l7rule = L7RuleManager(self)

        # self.q_client = \
        #    neutron_client.F5NetworksNeutronClient(self.plugin)

        # add this agent RPC to the neutron agent scheduler
        # mixins agent_notifiers dictionary for it's env
        self.plugin.agent_notifiers.update({
            q_const.AGENT_TYPE_LOADBALANCER: self.agent_rpc
        })

        registry.subscribe(self._bindRegistryCallback(),
                           resources.PROCESS,
                           events.AFTER_INIT)

    def _bindRegistryCallback(self):
        # Defines a callback function with name tied to driver env. Need to
        # enusre unique name, as registry callback manager references callback
        # functions by name.
        def post_fork_callback(resources, event, trigger):
            LOG.debug("F5DriverV2 received post neutron child "
                      "fork notification pid(%d) print trigger(%s)" % (
                          os.getpid(), trigger))
            self.plugin_rpc.create_rpc_listener()

        # post_fork_callback.__name__ += '_' + str(self.env)
        return post_fork_callback


class EntityManager(object):

    def __init__(self, driver):
        self.driver = driver
        self.create_entity_rpc = None
        self.update_entity_rpc = None
        self.delete_entity_rpc = None

    def _locate_bigiq_agent(self, context, loadbalancer_id):
        binding = self.driver.plugin.db.get_agent_hosting_loadbalancer(
            context, loadbalancer_id
        )

        if binding is None:
            raise exceptions.NoEligibleBIGIQAgent(
                loadbalancer_id=loadbalancer_id
            )

        agent = binding['agent']
        if not agent['alive'] or not agent['admin_state_up']:
            raise exceptions.BIGIQAgentIsNotAlive(
                loadbalancer_id=loadbalancer_id
            )

        return agent

    @log_helpers.log_method_call
    def create(self, context, entity, **kwargs):
        """Create an entity."""
        loadbalancer = kwargs['loadbalancer']

        host = kwargs.get('host')
        if not host:
            agent = self._locate_bigiq_agent(context, loadbalancer.id)
            host = agent['host']

        rpc_kwargs = {}
        if entity is not loadbalancer:
            rpc_kwargs['loadbalancer'] = loadbalancer.to_api_dict()

        self.create_entity_rpc(context, host, entity.to_api_dict(),
                               **rpc_kwargs)

    @log_helpers.log_method_call
    def update(self, context, old_entity, entity, **kwargs):
        """Update an entity."""
        loadbalancer = kwargs['loadbalancer']

        host = kwargs.get('host')
        if not host:
            agent = self._locate_bigiq_agent(context, loadbalancer.id)
            host = agent['host']

        rpc_kwargs = {}
        if entity is not loadbalancer:
            rpc_kwargs['loadbalancer'] = loadbalancer.to_api_dict()

        self.update_entity_rpc(context, host, old_entity.to_api_dict(),
                               entity.to_api_dict(), **rpc_kwargs)

    @log_helpers.log_method_call
    def delete(self, context, entity, **kwargs):
        """Delete an entity."""
        loadbalancer = kwargs['loadbalancer']

        host = kwargs.get('host')
        if not host:
            agent = self._locate_bigiq_agent(context, loadbalancer.id)
            host = agent['host']

        rpc_kwargs = {}
        if entity is not loadbalancer:
            rpc_kwargs['loadbalancer'] = loadbalancer.to_api_dict()

        self.delete_entity_rpc(context, host, entity.to_api_dict(),
                               **rpc_kwargs)


class LoadBalancerManager(EntityManager):
    """LoadBalancerManager class handles Neutron LBaaS CRUD."""

    def __init__(self, driver):
        super(LoadBalancerManager, self).__init__(driver)
        self.create_entity_rpc = self.driver.agent_rpc.create_loadbalancer
        self.update_entity_rpc = self.driver.agent_rpc.update_loadbalancer
        self.delete_entity_rpc = self.driver.agent_rpc.delete_loadbalancer

    def _schedule_bigiq_agent(self, context, loadbalancer_id, active=True):
        # TODO: agent scheduler
        query = context.session.query(agents_db.Agent)
        query = query.filter_by(agent_type=constants.LBAASV2_BIGIQ_AGENT_TYPE,
                                admin_state_up=active)
        agents = [agent for agent in query]
        if len(agents) > 0:
            # Bind loadbalancer with agent
            binding = agent_scheduler.LoadbalancerAgentBinding()
            binding.agent = agents[0]
            binding.loadbalancer_id = loadbalancer_id
            context.session.add(binding)
            return agents[0]
        else:
            raise exceptions.NoEligibleBIGIQAgent(
                loadbalancer_id=loadbalancer_id
            )

    @log_helpers.log_method_call
    def create(self, context, loadbalancer):
        """Create a loadbalancer."""
        agent = self._schedule_bigiq_agent(context, loadbalancer.id)
        super(LoadBalancerManager, self).create(
                context, loadbalancer, loadbalancer=loadbalancer,
                host=agent['host'])

    @log_helpers.log_method_call
    def update(self, context, old_loadbalancer, loadbalancer):
        """Update a loadbalancer."""
        super(LoadBalancerManager, self).update(
                context, old_loadbalancer, loadbalancer,
                loadbalancer=loadbalancer)

    @log_helpers.log_method_call
    def delete(self, context, loadbalancer):
        """Delete a loadbalancer."""
        super(LoadBalancerManager, self).delete(
                context, loadbalancer, loadbalancer=loadbalancer)

    @log_helpers.log_method_call
    def refresh(self, context, loadbalancer):
        """Refresh a loadbalancer."""
        pass

    @log_helpers.log_method_call
    def stats(self, context, loadbalancer):
        pass


class ListenerManager(EntityManager):
    """ListenerManager class handles Neutron LBaaS listener CRUD."""

    def __init__(self, driver):
        super(ListenerManager, self).__init__(driver)
        self.create_entity_rpc = self.driver.agent_rpc.create_listener
        self.update_entity_rpc = self.driver.agent_rpc.update_listener
        self.delete_entity_rpc = self.driver.agent_rpc.delete_listener

    @log_helpers.log_method_call
    def create(self, context, listener):
        """Create a listener."""
        loadbalancer = listener.loadbalancer
        super(ListenerManager, self).create(
            context, listener, loadbalancer=loadbalancer)

    @log_helpers.log_method_call
    def update(self, context, old_listener, listener):
        """Update a listener."""
        loadbalancer = listener.loadbalancer
        super(ListenerManager, self).update(
            context, old_listener, listener, loadbalancer=loadbalancer)

    @log_helpers.log_method_call
    def delete(self, context, listener):
        """Delete a listener."""
        loadbalancer = listener.loadbalancer
        super(ListenerManager, self).delete(
            context, listener, loadbalancer=loadbalancer)


class PoolManager(EntityManager):
    """PoolManager class handles Neutron LBaaS pool CRUD."""

    def __init__(self, driver):
        super(PoolManager, self).__init__(driver)
        self.create_entity_rpc = self.driver.agent_rpc.create_pool
        self.update_entity_rpc = self.driver.agent_rpc.update_pool
        self.delete_entity_rpc = self.driver.agent_rpc.delete_pool

    @log_helpers.log_method_call
    def create(self, context, pool):
        """Create a pool."""
        loadbalancer = pool.loadbalancer
        super(PoolManager, self).create(
            context, pool, loadbalancer=loadbalancer)

    @log_helpers.log_method_call
    def update(self, context, old_pool, pool):
        """Update a pool."""
        loadbalancer = pool.loadbalancer
        super(PoolManager, self).update(
            context, old_pool, pool, loadbalancer=loadbalancer)

    @log_helpers.log_method_call
    def delete(self, context, pool):
        """Delete a pool."""
        loadbalancer = pool.loadbalancer
        super(PoolManager, self).delete(
            context, pool, loadbalancer=loadbalancer)


class MemberManager(EntityManager):
    """MemberManager class handles Neutron LBaaS pool member CRUD."""

    def __init__(self, driver):
        super(MemberManager, self).__init__(driver)
        self.create_entity_rpc = self.driver.agent_rpc.create_member
        self.update_entity_rpc = self.driver.agent_rpc.update_member
        self.delete_entity_rpc = self.driver.agent_rpc.delete_member

    @log_helpers.log_method_call
    def create(self, context, member):
        """Create a member."""
        loadbalancer = member.pool.loadbalancer
        super(MemberManager, self).create(
            context, member, loadbalancer=loadbalancer)

    @log_helpers.log_method_call
    def update(self, context, old_member, member):
        """Update a member."""
        loadbalancer = member.pool.loadbalancer
        super(MemberManager, self).update(
            context, old_member, member, loadbalancer=loadbalancer)

    @log_helpers.log_method_call
    def delete(self, context, member):
        """Delete a member."""
        loadbalancer = member.pool.loadbalancer
        super(MemberManager, self).delete(
            context, member, loadbalancer=loadbalancer)


class HealthMonitorManager(EntityManager):
    """HealthMonitorManager class handles Neutron LBaaS monitor CRUD."""
    def __init__(self, driver):
        super(HealthMonitorManager, self).__init__(driver)
        self.create_entity_rpc = self.driver.agent_rpc.create_health_monitor
        self.update_entity_rpc = self.driver.agent_rpc.update_health_monitor
        self.delete_entity_rpc = self.driver.agent_rpc.delete_health_monitor

    @log_helpers.log_method_call
    def create(self, context, health_monitor):
        """Create a health monitor."""
        loadbalancer = health_monitor.pool.loadbalancer
        super(HealthMonitorManager, self).create(
            context, health_monitor, loadbalancer=loadbalancer)

    @log_helpers.log_method_call
    def update(self, context, old_health_monitor, health_monitor):
        """Update a health monitor."""
        loadbalancer = health_monitor.pool.loadbalancer
        super(HealthMonitorManager, self).update(
            context, old_health_monitor, health_monitor,
            loadbalancer=loadbalancer)

    @log_helpers.log_method_call
    def delete(self, context, health_monitor):
        """Delete a health monitor."""
        loadbalancer = health_monitor.pool.loadbalancer
        super(HealthMonitorManager, self).delete(
            context, health_monitor, loadbalancer=loadbalancer)


class L7PolicyManager(EntityManager):
    """L7PolicyManager class handles Neutron LBaaS L7 Policy CRUD."""

    def __init__(self, driver):
        super(L7PolicyManager, self).__init__(driver)
        self.create_entity_rpc = self.driver.agent_rpc.create_l7policy
        self.update_entity_rpc = self.driver.agent_rpc.update_l7policy
        self.delete_entity_rpc = self.driver.agent_rpc.delete_l7policy

    @log_helpers.log_method_call
    def create(self, context, policy):
        """Create an L7 policy."""
        loadbalancer = policy.listener.loadbalancer
        super(L7PolicyManager, self).create(
            context, policy, loadbalancer=loadbalancer)

    @log_helpers.log_method_call
    def update(self, context, old_policy, policy):
        """Update a policy."""
        loadbalancer = policy.listener.loadbalancer
        super(L7PolicyManager, self).update(
            context, old_policy, policy, loadbalancer=loadbalancer)

    @log_helpers.log_method_call
    def delete(self, context, policy):
        """Delete a policy."""
        loadbalancer = policy.listener.loadbalancer
        super(L7PolicyManager, self).delete(
            context, policy, loadbalancer=loadbalancer)


class L7RuleManager(EntityManager):
    """L7RuleManager class handles Neutron LBaaS L7 Rule CRUD."""
    def __init__(self, driver):
        super(L7RuleManager, self).__init__(driver)
        self.create_entity_rpc = self.driver.agent_rpc.create_l7rule
        self.update_entity_rpc = self.driver.agent_rpc.update_l7rule
        self.delete_entity_rpc = self.driver.agent_rpc.delete_l7rule

    @log_helpers.log_method_call
    def create(self, context, rule):
        """Create an L7 rule."""
        loadbalancer = rule.policy.listener.loadbalancer
        super(L7RuleManager, self).create(
            context, rule, loadbalancer=loadbalancer)

    @log_helpers.log_method_call
    def update(self, context, old_rule, rule):
        """Update a rule."""
        loadbalancer = rule.policy.listener.loadbalancer
        super(L7RuleManager, self).update(
            context, old_rule, rule, loadbalancer=loadbalancer)

    @log_helpers.log_method_call
    def delete(self, context, rule):
        """Delete a rule."""
        loadbalancer = rule.policy.listener.loadbalancer
        super(L7RuleManager, self).delete(
            context, rule, loadbalancer=loadbalancer)
