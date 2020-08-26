import f5_lbaasv2_bigiq_driver
from f5_lbaasv2_bigiq_dirver.driver import BIGIQDriver

from oslo_log import log as logging

from neutron_lbaas.drivers import driver_base

VERSION = "1.0.0"
LOG = logging.getLogger(__name__)


class UndefinedEnvironment(Exception):
    pass


class F5BIGIQDriver(driver_base.LoadBalancerBaseDriver):

    def __init__(self, plugin, env='Project'):
        super(F5BIGIQDriver, self).__init__(plugin)

        self.load_balancer = LoadBalancerManager(self)
        self.listener = ListenerManager(self)
        self.pool = PoolManager(self)
        self.member = MemberManager(self)
        self.health_monitor = HealthMonitorManager(self)
        self.l7policy = L7PolicyManager(self)
        self.l7rule = L7RuleManager(self)

        if not env:
            msg = "F5LBaaSV2Driver cannot be intialized because the "\
                "environment is not defined. To set the environment, edit "\
                "neutron_lbaas.conf and append the environment name to the "\
                "service_provider class name."
            LOG.debug(msg)
            raise UndefinedEnvironment(msg)

        LOG.debug("F5LBaaSV2Driver: initializing, version=%s, impl=%s, env=%s"
                  % (VERSION, f5_lbaasv2_bigiq_driver.__version__, env))

        self.bigiq = BIGIQDriver(plugin, env)


class LoadBalancerManager(driver_base.BaseLoadBalancerManager):

    def create(self, context, lb):
        self.driver.bigiq.loadbalancer.create(context, lb)

    def update(self, context, old_lb, lb):
        self.driver.bigiq.loadbalancer.update(context, old_lb, lb)

    def delete(self, context, lb):
        self.driver.bigiq.loadbalancer.delete(context, lb)

    def refresh(self, context, lb):
        self.driver.bigiq.loadbalancer.refresh(context, lb)

    def stats(self, context, lb):
        return self.driver.bigiq.loadbalancer.stats(context, lb)


class ListenerManager(driver_base.BaseListenerManager):

    def create(self, context, listener):
        self.driver.bigiq.listener.create(context, listener)

    def update(self, context, old_listener, listener):
        self.driver.bigiq.listener.update(context, old_listener, listener)

    def delete(self, context, listener):
        self.driver.bigiq.listener.delete(context, listener)


class PoolManager(driver_base.BasePoolManager):

    def create(self, context, pool):
        self.driver.bigiq.pool.create(context, pool)

    def update(self, context, old_pool, pool):
        self.driver.bigiq.pool.update(context, old_pool, pool)

    def delete(self, context, pool):
        self.driver.bigiq.pool.delete(context, pool)


class MemberManager(driver_base.BaseMemberManager):

    def create(self, context, member):
        self.driver.bigiq.member.create(context, member)

    def update(self, context, old_member, member):
        self.driver.bigiq.member.update(context, old_member, member)

    def delete(self, context, member):
        self.driver.bigiq.member.delete(context, member)


class HealthMonitorManager(driver_base.BaseHealthMonitorManager):

    def create(self, context, health_monitor):
        self.driver.bigiq.healthmonitor.create(context, health_monitor)

    def update(self, context, old_health_monitor, health_monitor):
        self.driver.bigiq.healthmonitor.update(context, old_health_monitor,
                                               health_monitor)

    def delete(self, context, health_monitor):
        self.driver.bigiq.healthmonitor.delete(context, health_monitor)


class L7PolicyManager(driver_base.BaseL7PolicyManager):

    def create(self, context, l7policy):
        self.driver.bigiq.l7policy.create(context, l7policy)

    def update(self, context, old_l7policy, l7policy):
        self.driver.bigiq.l7policy.update(context, old_l7policy, l7policy)

    def delete(self, context, l7policy):
        self.driver.bigiq.l7policy.delete(context, l7policy)


class L7RuleManager(driver_base.BaseL7RuleManager):

    def create(self, context, l7rule):
        self.driver.bigiq.l7rule.create(context, l7rule)

    def update(self, context, old_l7rule, l7rule):
        self.driver.bigiq.l7rule.update(context, old_l7rule, l7rule)

    def delete(self, context, l7rule):
        self.driver.bigiq.l7rule.delete(context, l7rule)
