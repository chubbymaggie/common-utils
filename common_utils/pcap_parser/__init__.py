import dpkt
import os
from ..simple_logging import *


class NetworkData(object):

    def __init__(self, target_data):
        """
            Create a new NetworkData object.
        :param target_data: data of the current object.
        :return: None
        """
        self.target_data = target_data
        self._is_input = False
        self._is_output = False

    @property
    def is_input(self):
        """
            Flag to indicate if this network data object is input
        :return: true/false depending on whether the current object is input.
        """
        return self._is_input

    @property
    def is_output(self):
        """
            Flag to indicate if this network data object is output
        :return: true/false depending on whether the current object is output.
        """
        return self._is_output

    @property
    def data(self):
        """
            Get data corresponding to current object.
        :return: data
        """
        return self.target_data


class InputData(NetworkData):
    """
        Represents Input data
    """

    def __init__(self, target_data):
        NetworkData.__init__(self, target_data)
        self._is_input = True


class OutputData(NetworkData):
    """
        Represents output data
    """

    def __init__(self, target_data):
        NetworkData.__init__(self, target_data)
        self._is_output = True


class TCPStream(object):
    """

    """

    def __init__(self, src_ip, dst_ip, data_pkts):
        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.data_pkts = data_pkts


class PcapParser(object):
    """

    """

    def __init__(self, target_pcap_file):
        """

        :param target_pcap_file:
        :return:
        """
        assert os.path.exists(target_pcap_file), "Provided PCAP File:" + str(target_pcap_file) + " does not exists"
        pcap_fp = open(target_pcap_file, 'rb')
        pcap_iter = dpkt.pcap.Reader(pcap_fp)
        self.all_pkts = list(pcap_iter)
        pcap_fp.close()

    def get_data_stream(self):
        """

        :return:
        """
        target_stream = None
        if len(self.all_pkts) > 0:
            first_eth_pkt = dpkt.ethernet.Ethernet(self.all_pkts[0][1])
            src_ip = first_eth_pkt.data.src
            dst_ip = first_eth_pkt.data.dst
            all_pkts = []
            for i in range(1, len(self.all_pkts)):
                curr_raw_pkt = dpkt.ethernet.Ethernet(self.all_pkts[i][1])
                curr_src = curr_raw_pkt.data.src
                curr_dst = curr_raw_pkt.data.dst
                curr_data = curr_raw_pkt.data.data.data
                if len(curr_data) > 0:
                    if curr_src == src_ip:
                        if curr_dst != dst_ip:
                            log_error("Got a packet whose destination is unknown:" + str(curr_dst) +
                                      ", Expected:" + str(dst_ip))
                        curr_data_pkt = InputData(curr_data)
                    else:
                        if curr_dst != src_ip:
                            log_error("Got a packet whose destination is unknown:" + str(curr_dst) +
                                      ", Expected:" + str(src_ip))
                        curr_data_pkt = OutputData(curr_data)
                    all_pkts.append(curr_data_pkt)
            target_stream = TCPStream(src_ip, dst_ip, all_pkts)

        return target_stream
