# ipv6-bgp-bfd

This is a very simple eAPI script to emulate the output of 'show ip bgp neighbors bfd' for IPv6 BGP neighbors.  It is written to run locally on an Arista switch by connecting to eAPI using the unix-socket method.  To enable this, simply do the following...

~~~~
management api http-commands
   protocol unix-socket
   no shutdown
~~~~

From there, simply load the script into the flash: of the switch and invoke it either by using bash or, better yet, creating an alias!

~~~~
alias ipv6_bgp_bfd bash python /mnt/flash/ipv6_bgp_bfd.py
~~~~
