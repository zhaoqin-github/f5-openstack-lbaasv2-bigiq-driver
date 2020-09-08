from neutron.common import rpc as neutron_rpc
from neutron.db import agents_db
from neutron.db.models import agent as agents_model
from neutron_lib import constants as plugin_constants

from neutron_lbaas.db.loadbalancer import models

from oslo_log import helpers as log_helpers
from oslo_log import log as logging

from f5_lbaasv2_bigiq_driver import constants


LOG = logging.getLogger(__name__)


class LBaaSv2PluginCallbacksRPC(object):
    """Agent to plugin RPC API."""

    def __init__(self, driver=None):
        """LBaaSv2PluginCallbacksRPC constructor."""
        self.driver = driver
        self.cluster_wide_agents = {}

    def create_rpc_listener(self):
        topic = constants.TOPIC_LBAASV2_BIGIQ_DRIVER

        self.conn = neutron_rpc.create_connection()

        self.conn.create_consumer(
            topic,
            [self, agents_db.AgentExtRpcCallback(self.driver.plugin.db)],
            fanout=False)
        self.conn.consume_in_threads()

    # change the admin_state_up of the an agent
    @log_helpers.log_method_call
    def set_agent_admin_state(self, context, admin_state_up, host=None):
        """Set the admin_up_state of an agent."""
        if not host:
            LOG.error('tried to set agent admin_state_up without host')
            return False
        with context.session.begin(subtransactions=True):
            query = context.session.query(agents_model.Agent)
            query = query.filter_by(
               agent_type=constants.LBAASV2_BIGIQ_AGENT_TYPE,
               host=host)
            try:
                agent = query.one_or_none()
                if agent is not None and \
                   not agent.admin_state_up == admin_state_up:
                    agent.admin_state_up = admin_state_up
                    context.session.add(agent)
            except Exception as exc:
                # Impossible to return multiple agents with same host
                LOG.error('query for agent produced: %s' % str(exc))
                return False
        return True

    @log_helpers.log_method_call
    def update_loadbalancer_stats(
            self, context, loadbalancer_id=None, stats=None):
        """Update service stats."""
        with context.session.begin(subtransactions=True):
            try:
                self.driver.plugin.db.update_loadbalancer_stats(
                    context, loadbalancer_id, stats
                )
            except Exception as e:
                LOG.error('Exception: update_loadbalancer_stats: %s',
                          e.message)

    @log_helpers.log_method_call
    def update_loadbalancer_status(self, context, loadbalancer_id=None,
                                   status=None, operating_status=None):
        """Agent confirmation hook to update loadbalancer status."""
        with context.session.begin(subtransactions=True):
            try:
                lb_db = self.driver.plugin.db.get_loadbalancer(
                    context,
                    loadbalancer_id
                )
                if (lb_db.provisioning_status ==
                        plugin_constants.PENDING_DELETE):
                    status = plugin_constants.PENDING_DELETE

                self.driver.plugin.db.update_status(
                    context,
                    models.LoadBalancer,
                    loadbalancer_id,
                    status,
                    operating_status
                )
            except Exception as e:
                LOG.error('Exception: update_loadbalancer_status: %s',
                          e.message)

    @log_helpers.log_method_call
    def loadbalancer_destroyed(self, context, loadbalancer_id=None):
        """Agent confirmation hook that loadbalancer has been destroyed."""
        self.driver.plugin.db.delete_loadbalancer(context, loadbalancer_id)

    @log_helpers.log_method_call
    def update_listener_status(self, context, listener_id=None,
                               provisioning_status=plugin_constants.ERROR,
                               operating_status=None):
        """Agent confirmation hook to update listener status."""
        with context.session.begin(subtransactions=True):
            try:
                listener_db = self.driver.plugin.db.get_listener(
                    context,
                    listener_id
                )
                if (listener_db.provisioning_status ==
                        plugin_constants.PENDING_DELETE):
                    provisioning_status = plugin_constants.PENDING_DELETE
                self.driver.plugin.db.update_status(
                    context,
                    models.Listener,
                    listener_id,
                    provisioning_status,
                    operating_status
                )
            except Exception as e:
                LOG.error('Exception: update_listener_status: %s',
                          e.message)

    @log_helpers.log_method_call
    def listener_destroyed(self, context, listener_id=None):
        """Agent confirmation hook that listener has been destroyed."""
        self.driver.plugin.db.delete_listener(context, listener_id)
        # TODO: remove lb agent bindings

    @log_helpers.log_method_call
    def update_pool_status(self, context, pool_id=None,
                           provisioning_status=plugin_constants.ERROR,
                           operating_status=None):
        """Agent confirmations hook to update pool status."""
        with context.session.begin(subtransactions=True):
            try:
                pool = self.driver.plugin.db.get_pool(
                    context,
                    pool_id
                )
                if (pool.provisioning_status !=
                        plugin_constants.PENDING_DELETE):
                    self.driver.plugin.db.update_status(
                        context,
                        models.PoolV2,
                        pool_id,
                        provisioning_status,
                        operating_status
                    )
            except Exception as e:
                LOG.error('Exception: update_pool_status: %s',
                          e.message)

    @log_helpers.log_method_call
    def pool_destroyed(self, context, pool_id=None):
        """Agent confirmation hook that pool has been destroyed."""
        self.driver.plugin.db.delete_pool(context, pool_id)

    @log_helpers.log_method_call
    def update_member_status(self, context, member_id=None,
                             provisioning_status=None,
                             operating_status=None):
        """Agent confirmations hook to update member status."""
        with context.session.begin(subtransactions=True):
            try:
                member = self.driver.plugin.db.get_pool_member(
                    context,
                    member_id
                )
                if (member.provisioning_status !=
                        plugin_constants.PENDING_DELETE):
                    self.driver.plugin.db.update_status(
                        context,
                        models.MemberV2,
                        member_id,
                        provisioning_status,
                        operating_status
                    )
            except Exception as e:
                LOG.error('Exception: update_member_status: %s',
                          e.message)

    @log_helpers.log_method_call
    def member_destroyed(self, context, member_id=None):
        """Agent confirmation hook that member has been destroyed."""
        self.driver.plugin.db.delete_member(context, member_id)

    @log_helpers.log_method_call
    def update_health_monitor_status(
            self, context, health_monitor_id,
            provisioning_status=plugin_constants.ERROR, operating_status=None):
        """Agent confirmation hook to update health monitor status."""
        with context.session.begin(subtransactions=True):
            try:
                health_monitor = self.driver.plugin.db.get_healthmonitor(
                    context,
                    health_monitor_id
                )
                if (health_monitor.provisioning_status !=
                        plugin_constants.PENDING_DELETE):
                    self.driver.plugin.db.update_status(
                        context,
                        models.HealthMonitorV2,
                        health_monitor_id,
                        provisioning_status,
                        operating_status
                    )
            except Exception as e:
                LOG.error('Exception: update_health_monitor_status: %s',
                          e.message)

    @log_helpers.log_method_call
    def health_monitor_destroyed(self, context, health_monitor_id=None):
        """Agent confirmation hook that health_monitor has been destroyed."""
        self.driver.plugin.db.delete_healthmonitor(context, health_monitor_id)

    @log_helpers.log_method_call
    def update_l7policy_status(self, context, l7policy_id=None,
                               provisioning_status=plugin_constants.ERROR,
                               operating_status=None):
        """Agent confirmation hook to update l7 policy status."""
        with context.session.begin(subtransactions=True):
            try:
                l7policy_db = self.driver.plugin.db.get_l7policy(
                    context,
                    l7policy_id
                )
                if (l7policy_db.provisioning_status ==
                        plugin_constants.PENDING_DELETE):
                    provisioning_status = plugin_constants.PENDING_DELETE
                self.driver.plugin.db.update_status(
                    context,
                    models.L7Policy,
                    l7policy_id,
                    provisioning_status,
                    operating_status
                )
            except Exception as e:
                LOG.error('Exception: update_l7policy_status: %s',
                          e.message)

    @log_helpers.log_method_call
    def l7policy_destroyed(self, context, l7policy_id=None):
        LOG.debug("l7policy_destroyed")
        """Agent confirmation hook that l7 policy has been destroyed."""
        self.driver.plugin.db.delete_l7policy(context, l7policy_id)

    @log_helpers.log_method_call
    def update_l7rule_status(self, context, l7rule_id=None, l7policy_id=None,
                             provisioning_status=plugin_constants.ERROR,
                             operating_status=None):
        """Agent confirmation hook to update l7 policy status."""
        with context.session.begin(subtransactions=True):
            try:
                l7rule_db = self.driver.plugin.db.get_l7policy_rule(
                    context,
                    l7rule_id,
                    l7policy_id
                )
                if (l7rule_db.provisioning_status ==
                        plugin_constants.PENDING_DELETE):
                    provisioning_status = plugin_constants.PENDING_DELETE
                self.driver.plugin.db.update_status(
                    context,
                    models.L7Rule,
                    l7rule_id,
                    provisioning_status,
                    operating_status
                )
            except Exception as e:
                LOG.error('Exception: update_l7rule_status: %s',
                          e.message)

    @log_helpers.log_method_call
    def l7rule_destroyed(self, context, l7rule_id):
        """Agent confirmation hook that l7 policy has been destroyed."""
        self.driver.plugin.db.delete_l7policy_rule(context, l7rule_id)
