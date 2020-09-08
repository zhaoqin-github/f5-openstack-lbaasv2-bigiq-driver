from neutron.extensions import agent


class NoEligibleBIGIQAgent(agent.AgentNotFound):
    message = ("No eligible BIG-IQ agent found "
               "for loadbalancer %(loadbalancer_id)s.")
