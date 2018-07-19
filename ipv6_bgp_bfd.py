#!/usr/bin/env python

# import modules
# jsonrpclib for eAPI interfaces
# prettytable for easy formatting of output
# datetime and time for calculation of Up/Down Time
from jsonrpclib import Server
from prettytable import PrettyTable
import datetime
import time

# define function to take timestamp from BGP Up/Down time and convert from Linux Epoch Time
# to human readable format.
def up_down_time(sec):
    cur_time = time.time()
    delta = cur_time - sec
    m, s = divmod(delta, 60)
    h, m = divmod(m, 60)
    up_down = "%d:%02d:%02d" % (h, m, s)
    return up_down

# connect to eAPI via Linux Socket
switch = Server( "unix:/var/run/command-api.sock")

# run relavent commands to correlate output
show_ipv6_bgp_sum = switch.runCmds( 1,[ "show ipv6 bgp summary"])
show_bfd_neigh = switch.runCmds( 1,[ "show bfd neighbors"])
show_ipv6_neigh = switch.runCmds( 1,[ "show ipv6 neighbors"])
show_ipv6_neigh = show_ipv6_neigh[0]["ipV6Neighbors"]

# Define table headers to match output from 'show ip bgp neighbors bfd'
t = PrettyTable(["Neighbor", "Interface", "Up/Down", "State", "Flags"])

# loop through active IPv6 BGP neighbors and pull out status info
for bgp6_neighbor, bgp6_status in show_ipv6_bgp_sum[0]["vrfs"]["default"]["peers"].items():
    # Check if BGP IPv6 neighbor is in BFD IPv6 Table and if yes, pull out status
    if bgp6_neighbor in show_bfd_neigh[0]["vrfs"]["default"]["ipv6Neighbors"]:
        bfd6_status = show_bfd_neigh[0]["vrfs"]["default"]["ipv6Neighbors"][bgp6_neighbor]["peerStats"]
        # Check BFD status and set Flag based on that
        if bfd6_status[bfd6_status.keys()[0]]["status"] == "up":
            row = [bgp6_neighbor, bfd6_status.keys()[0],up_down_time(bgp6_status["upDownTime"]),bgp6_status["peerState"], "U"]
            t.add_row(row)
        elif bfd6_status[bfd6_status.keys()[0]]["status"] == "down":
            row = [bgp6_neighbor, bfd6_status.keys()[0],up_down_time(bgp6_status["upDownTime"]),bgp6_status["peerState"], "D"]
            t.add_row(row)
        else:
            row = [bgp6_neighbor, bfd6_status.keys()[0],up_down_time(bgp6_status["upDownTime"]),bgp6_status["peerState"], "I"]
            t.add_row(row)
    # If BGP neighbor is not in IPv6 BFD table, mark Flag accordingly
    else:
        for index in show_ipv6_neigh:
            if bgp6_neighbor == index["address"]:
                bgp6_interface = index["interface"]
                if bgp6_interface.startswith("Et"):
                    int_id = str(bgp6_interface.split("t")[1])
                    bgp6_interface = "Ethernet" + int_id
                row = [bgp6_neighbor, bgp6_interface ,up_down_time(bgp6_status["upDownTime"]),bgp6_status["peerState"], "N"]
                t.add_row(row)

# Print out Key and Table
print """
IPv6 BGP BFD Neighbor Table
Flags: U - BFD is enabled for BGP neighbor and BFD session state is UP
       I - BFD is enabled for BGP neighbor and BFD session state is INIT
       D - BFD is enabled for BGP neighbor and BFD session state is DOWN
       N - BFD is not enabled for BGP neighbor
"""
print t