import socket
import logging

from ..discovery.hosts import RunningAsPodEvent

from ...core.events import handler
from ...core.events.types import Event, Vulnerability
from ...core.types import Hunter, AccessRisk, KubernetesCluster


class CapNetRawEnabled(Event, Vulnerability):
    """CAP_NET_RAW is enabled by default for pods, an attacker could potentially perform network attacks on other pods running on the same node"""
    def __init__(self):
        Vulnerability.__init__(self, KubernetesCluster, name="CAP_NET_RAW Enabled", category=AccessRisk)
    

@handler.subscribe(RunningAsPodEvent)
class PodCapabilitiesHunter(Hunter):
    """Pod Capabilities Hunter
    Checks for default enabled capabilities in a pod 
    """
    def __init__(self, event):
        self.event = event        

    def check_net_raw(self):
        logging.debug("Passive hunter's trying to open a RAW socket")
        try:
            # trying to open a raw socket without CAP_NET_RAW will raise PermissionsError
            s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
            s.close()
            logging.debug("Passive hunter's closing RAW socket")
            return True
        # python2 does not support PermissionError, should be sufficiant to say that 
        # NET_RAW is disabled by catching all exception. after we stop support for
        # python2, should replace to except PermissionError explicitly
        except:
            logging.debug("CAP_NET_RAW not enabled")

    def execute(self):
        if self.check_net_raw():
            self.publish_event(CapNetRawEnabled())