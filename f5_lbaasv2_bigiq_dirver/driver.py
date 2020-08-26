from oslo_config import cfg
from oslo_log import helpers as log_helpers
from oslo_log import log as logging

LOG = logging.getLogger(__name__)

OPTS = [
    cfg.StrOpt(
        'f5_bigiq_agent_scheduler',
        default=(
            'f5_lbaasv2_bigiq_dirver.agent_scheduler.TenantScheduler'
        ),
        help=('Driver to use for scheduling loadbalancer to a BIG-IQ agent')
    )
]

cfg.CONF.register_opts(OPTS)


class BIGIQDriver(object):

    def __init__(self, plugin=None, env=None):
        pass


class EntityManager(object):

    def __init__(self, driver):
        pass


class LoadBalancerManager(EntityManager):
    """LoadBalancerManager class handles Neutron LBaaS CRUD."""

    @log_helpers.log_method_call
    def create(self, context, loadbalancer):
        """Create a loadbalancer."""
        pass

    @log_helpers.log_method_call
    def update(self, context, old_loadbalancer, loadbalancer):
        """Update a loadbalancer."""
        pass

    @log_helpers.log_method_call
    def delete(self, context, loadbalancer):
        """Delete a loadbalancer."""
        self.driver.plugin.db.delete_loadbalancer(context, loadbalancer.id)

    @log_helpers.log_method_call
    def refresh(self, context, loadbalancer):
        """Refresh a loadbalancer."""
        pass

    @log_helpers.log_method_call
    def stats(self, context, loadbalancer):
        pass


class ListenerManager(EntityManager):
    """ListenerManager class handles Neutron LBaaS listener CRUD."""

    @log_helpers.log_method_call
    def create(self, context, listener):
        """Create a listener."""
        pass

    @log_helpers.log_method_call
    def update(self, context, old_listener, listener):
        """Update a listener."""
        pass

    @log_helpers.log_method_call
    def delete(self, context, listener):
        """Delete a listener."""
        pass


class PoolManager(EntityManager):
    """PoolManager class handles Neutron LBaaS pool CRUD."""

    @log_helpers.log_method_call
    def create(self, context, pool):
        """Create a pool."""
        pass

    @log_helpers.log_method_call
    def update(self, context, old_pool, pool):
        """Update a pool."""
        pass

    @log_helpers.log_method_call
    def delete(self, context, pool):
        """Delete a pool."""
        pass


class MemberManager(EntityManager):
    """MemberManager class handles Neutron LBaaS pool member CRUD."""

    @log_helpers.log_method_call
    def create(self, context, member):
        """Create a member."""
        pass

    @log_helpers.log_method_call
    def update(self, context, old_member, member):
        """Update a member."""
        pass

    @log_helpers.log_method_call
    def delete(self, context, member):
        """Delete a member."""
        pass


class HealthMonitorManager(EntityManager):
    """HealthMonitorManager class handles Neutron LBaaS monitor CRUD."""

    @log_helpers.log_method_call
    def create(self, context, health_monitor):
        """Create a health monitor."""
        pass

    @log_helpers.log_method_call
    def update(self, context, old_health_monitor, health_monitor):
        """Update a health monitor."""
        pass

    @log_helpers.log_method_call
    def delete(self, context, health_monitor):
        """Delete a health monitor."""
        pass


class L7PolicyManager(EntityManager):
    """L7PolicyManager class handles Neutron LBaaS L7 Policy CRUD."""

    @log_helpers.log_method_call
    def create(self, context, policy):
        """Create an L7 policy."""
        pass

    @log_helpers.log_method_call
    def update(self, context, old_policy, policy):
        """Update a policy."""
        pass

    @log_helpers.log_method_call
    def delete(self, context, policy):
        """Delete a policy."""
        pass


class L7RuleManager(EntityManager):
    """L7RuleManager class handles Neutron LBaaS L7 Rule CRUD."""

    @log_helpers.log_method_call
    def create(self, context, rule):
        """Create an L7 rule."""
        pass

    @log_helpers.log_method_call
    def update(self, context, old_rule, rule):
        """Update a rule."""
        pass

    @log_helpers.log_method_call
    def delete(self, context, rule):
        """Delete a rule."""
        pass
