from oslo_log import helpers as log_helpers
from oslo_log import log as logging
import oslo_messaging as messaging

from neutron.common import rpc

from f5_lbaasv2_bigiq_driver import constants

LOG = logging.getLogger(__name__)


class BIGIQAgentRPC(object):

    def __init__(self, driver=None):
        self.driver = driver
        self.topic = constants.TOPIC_LBAASV2_BIGIQ_AGENT
        self._create_rpc_publisher()

    def _create_rpc_publisher(self):
        self.topic = constants.TOPIC_LBAASV2_BIGIQ_AGENT
        target = messaging.Target(topic=self.topic,
                                  version=constants.RPC_API_VERSION)
        self._client = rpc.get_client(target, version_cap=None)

    def make_msg(self, method, **kwargs):
        return {'method': method,
                'namespace': constants.RPC_API_NAMESPACE,
                'args': kwargs}

    def call(self, context, msg, **kwargs):
        return self.__call_rpc_method(
            context, msg, rpc_method='call', **kwargs)

    def cast(self, context, msg, **kwargs):
        self.__call_rpc_method(context, msg, rpc_method='cast', **kwargs)

    def fanout_cast(self, context, msg, **kwargs):
        kwargs['fanout'] = True
        self.__call_rpc_method(context, msg, rpc_method='cast', **kwargs)

    def __call_rpc_method(self, context, msg, **kwargs):
        options = dict(
            ((opt, kwargs[opt])
             for opt in ('fanout', 'timeout', 'topic', 'version')
             if kwargs.get(opt))
        )
        if msg['namespace']:
            options['namespace'] = msg['namespace']

        if options:
            callee = self._client.prepare(**options)
        else:
            callee = self._client

        func = getattr(callee, kwargs['rpc_method'])
        return func(context, msg['method'], **msg['args'])

    @log_helpers.log_method_call
    def create_loadbalancer(self, context, host, loadbalancer, **kwargs):
        topic = '%s.%s' % (self.topic, host)
        return self.cast(
            context,
            self.make_msg(
                'create_loadbalancer',
                loadbalancer=loadbalancer,
                **kwargs
            ),
            topic=topic)

    @log_helpers.log_method_call
    def update_loadbalancer(
            self,
            context,
            host,
            old_loadbalancer,
            loadbalancer,
            **kwargs
    ):
        topic = '%s.%s' % (self.topic, host)
        return self.cast(
            context,
            self.make_msg(
                'update_loadbalancer',
                old_loadbalancer=old_loadbalancer,
                loadbalancer=loadbalancer,
                **kwargs
            ),
            topic=topic)

    @log_helpers.log_method_call
    def delete_loadbalancer(self, context, host, loadbalancer, **kwargs):
        topic = '%s.%s' % (self.topic, host)
        return self.cast(
            context,
            self.make_msg(
                'delete_loadbalancer',
                loadbalancer=loadbalancer,
                **kwargs
            ),
            topic=topic)

    @log_helpers.log_method_call
    def update_loadbalancer_stats(
            self,
            context,
            host,
            loadbalancer,
            **kwargs
    ):
        topic = '%s.%s' % (self.topic, host)
        return self.cast(
            context,
            self.make_msg(
                'update_loadbalancer_stats',
                loadbalancer=loadbalancer,
                **kwargs
            ),
            topic=topic)

    @log_helpers.log_method_call
    def create_listener(self, context, host, listener, **kwargs):
        topic = '%s.%s' % (self.topic, host)
        return self.cast(
            context,
            self.make_msg(
                'create_listener',
                listener=listener,
                **kwargs
            ),
            topic=topic)

    @log_helpers.log_method_call
    def update_listener(self, context, host, old_listener, listener, **kwargs):
        topic = '%s.%s' % (self.topic, host)
        return self.cast(
            context,
            self.make_msg(
                'update_listener',
                old_listener=old_listener,
                listener=listener,
                **kwargs
            ),
            topic=topic)

    @log_helpers.log_method_call
    def delete_listener(self, context, host, listener, **kwargs):
        topic = '%s.%s' % (self.topic, host)
        return self.cast(
            context,
            self.make_msg(
                'delete_listener',
                listener=listener,
                **kwargs
            ),
            topic=topic)

    @log_helpers.log_method_call
    def create_pool(self, context, host, pool, **kwargs):
        topic = '%s.%s' % (self.topic, host)
        return self.cast(
            context,
            self.make_msg(
                'create_pool',
                pool=pool,
                **kwargs
            ),
            topic=topic)

    @log_helpers.log_method_call
    def update_pool(self, context, host, old_pool, pool, **kwargs):
        topic = '%s.%s' % (self.topic, host)
        return self.cast(
            context,
            self.make_msg(
                'update_pool',
                old_pool=old_pool,
                pool=pool,
                **kwargs
            ),
            topic=topic)

    @log_helpers.log_method_call
    def delete_pool(self, context, host, pool, **kwargs):
        topic = '%s.%s' % (self.topic, host)
        return self.cast(
            context,
            self.make_msg(
                'delete_pool',
                pool=pool,
                **kwargs
            ),
            topic=topic)

    @log_helpers.log_method_call
    def create_member(self, context, host, member, **kwargs):
        topic = '%s.%s' % (self.topic, host)
        return self.cast(
            context,
            self.make_msg(
                'create_member',
                member=member,
                **kwargs
            ),
            topic=topic)

    @log_helpers.log_method_call
    def update_member(self, context, host, old_member, member, **kwargs):
        topic = '%s.%s' % (self.topic, host)
        return self.cast(
            context,
            self.make_msg(
                'update_member',
                old_member=old_member,
                member=member,
                **kwargs
            ),
            topic=topic)

    @log_helpers.log_method_call
    def delete_member(self, context, host, member, **kwargs):
        topic = '%s.%s' % (self.topic, host)
        return self.cast(
            context,
            self.make_msg(
                'delete_member',
                member=member,
                **kwargs
            ),
            topic=topic)

    @log_helpers.log_method_call
    def create_health_monitor(self, context, host, health_monitor, **kwargs):
        topic = '%s.%s' % (self.topic, host)
        return self.cast(
            context,
            self.make_msg(
                'create_health_monitor',
                health_monitor=health_monitor,
                **kwargs
            ),
            topic=topic)

    @log_helpers.log_method_call
    def update_health_monitor(
            self,
            context,
            host,
            old_health_monitor,
            health_monitor,
            **kwargs
    ):
        topic = '%s.%s' % (self.topic, host)
        return self.cast(
            context,
            self.make_msg(
                'update_health_monitor',
                old_health_monitor=old_health_monitor,
                health_monitor=health_monitor,
                **kwargs
            ),
            topic=topic)

    @log_helpers.log_method_call
    def delete_health_monitor(self, context, host, health_monitor, **kwargs):
        topic = '%s.%s' % (self.topic, host)
        return self.cast(
            context,
            self.make_msg(
                'delete_health_monitor',
                health_monitor=health_monitor,
                **kwargs
            ),
            topic=topic)

    @log_helpers.log_method_call
    def create_l7policy(self, context, host, l7policy, **kwargs):
        topic = '%s.%s' % (self.topic, host)
        return self.cast(
            context,
            self.make_msg(
                'create_l7policy',
                l7policy=l7policy,
                **kwargs
            ),
            topic=topic)

    @log_helpers.log_method_call
    def update_l7policy(self, context, host, old_l7policy, l7policy, **kwargs):
        topic = '%s.%s' % (self.topic, host)
        return self.cast(
            context,
            self.make_msg(
                'update_l7policy',
                old_l7policy=old_l7policy,
                l7policy=l7policy,
                **kwargs
            ),
            topic=topic)

    @log_helpers.log_method_call
    def delete_l7policy(self, context, host, l7policy, **kwargs):
        topic = '%s.%s' % (self.topic, host)
        return self.cast(
            context,
            self.make_msg(
                'delete_l7policy',
                l7policy=l7policy,
                **kwargs
            ),
            topic=topic)

    @log_helpers.log_method_call
    def create_l7rule(self, context, host, l7rule, **kwargs):
        topic = '%s.%s' % (self.topic, host)
        return self.cast(
            context,
            self.make_msg(
                'create_l7rule',
                l7rule=l7rule,
                **kwargs
            ),
            topic=topic)

    @log_helpers.log_method_call
    def update_l7rule(self, context, host, old_l7rule, l7rule, **kwargs):
        topic = '%s.%s' % (self.topic, host)
        return self.cast(
            context,
            self.make_msg(
                'update_l7rule',
                old_l7rule=old_l7rule,
                l7rule=l7rule,
                **kwargs
            ),
            topic=topic)

    @log_helpers.log_method_call
    def delete_l7rule(self, context, host, l7rule, **kwargs):
        topic = '%s.%s' % (self.topic, host)
        return self.cast(
            context,
            self.make_msg(
                'delete_l7rule',
                l7rule=l7rule,
                **kwargs
            ),
            topic=topic)
