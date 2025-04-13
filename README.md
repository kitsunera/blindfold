# blindfold
### An automatic linux firewall configurator for invisibility against LAN scanners


## prerequisites
A keyboard, a mouse, internet, and [python](https://www.python.org/downloads/)
## how to use:
After downloading the script, go to the directory of the file and run
```
sudo python blindfold.py
```

This will automatically set up iptables rules to drop ICMP packets, and change the kernel's IPv4 configuration to ignore ARP packets, making you esentially invisible to typical scanners, thus making you immune to man-in-the-middle attacks, and/or other types of reconaissance.
### Note: some people may experience internet issues because of the ICMP blocker. If you are affected by this, only run the ARP blocker.
```
sudo python blindfold.py --only-arp
```
vice versa as well, if you only want to run the ICMP blocker, while keeping ARP responses unaffected (NOT RECOMMENDED)
```
sudo python blindfold.py --only-icmp
```


**to revert the changes, simply run:**
```
sudo python blindfold.py --revert
```
this will automatically restore and make your device public in the network.

## additional arguments
these are some additional arguments you can use, to allow more configuration on the network.

```
sudo python blindfold.py --save # saves your configuration persistently
# to block all requests, even after reboots.
```
this is especially useful if you require strong levels of stealth, loading up this configuration during startup.
you can also use `--interface` to select certain interfaces, (seperated via a comma if you have multiple to select)



# IMPORTANT
### this python code just automates multiple commands. You can do the same without the code, although being a bit more complex.

*wlan0 being an example interface.*
disabling ARP packets:<br>
`sysctl -w net.ipv4.conf.wlan0.arp_ignore=8`<br>
`sysctl -w net.ipv4.conf.wlan0.arp_announce=2`

disabling ICMP packets:<br>
`iptables -C INPUT -p icmp -j DROP`<br>
`iptables -A INPUT -p icmp -j DROP`

enabling ARP packets:<br>
`sysctl -w net.ipv4.conf.wlan0.arp_ignore=0`<br>
`sysctl -w net.ipv4.conf.wlan0.arp_announce=0`

enabling ICMP packets:<br>
`iptables -C INPUT -p icmp -j DROP`<br>
`iptables -D INPUT -p icmp -j DROP`


