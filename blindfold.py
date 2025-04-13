"""blindfold: An automatic linux firewall configurator for invisibility against LAN scanners.
by senka"""

import argparse
import subprocess
import os
import sys
import re

def color_text(text, color):
    colors = {
        "red": "\033[91m",
        "reset": "\033[0m"        
    }
    return f"{colors.get(color, colors['reset'])}{text}{colors['reset']}"


def check_root():
    if os.geteuid() != 0:
        print(color_text("error: this script must be ran with sudo. :(", "red"))
        sys.exit(1)


def get_interfaces():
    try:
        output = subprocess.check_output(["ip", "link", "show"], 
                                         text=True)
        interfaces = re.findall(r'\d+: (\w+):', output)
        interfaces = [iface for iface in interfaces if iface != 'lo']
        return interfaces
    except subprocess.CalledProcessError as e:
        print(color_text(f"error: failed getting network interfaces: {e}", "red"))
        return []


def disable_arp(interface):
    try:
        subprocess.run(["sysctl", "-w", 
                       f"net.ipv4.conf.{interface}.arp_ignore=8"], 
                       check=True, stdout=subprocess.DEVNULL)
        subprocess.run(["sysctl", "-w", 
                       f"net.ipv4.conf.{interface}.arp_announce=2"], 
                       check=True, stdout=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError as e:
        print(color_text(f"error: failed disabling ARP for {interface}: {e}"))
        return False


def enable_arp(interface):
    try:
        subprocess.run(["sysctl", "-w", 
                       f"net.ipv4.conf.{interface}.arp_ignore=0"], 
                       check=True, stdout=subprocess.DEVNULL)
        subprocess.run(["sysctl", "-w", 
                       f"net.ipv4.conf.{interface}.arp_announce=0"], 
                       check=True, stdout=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError as e:
        print(color_text(f"error: failed enabling ARP for {interface}: {e}", "red"))
        return False


def disable_icmp():
    try:
        check = subprocess.run(
            ["iptables", "-C", "INPUT", "-p", "icmp", "-j", "DROP"], 
            stderr=subprocess.DEVNULL, 
            stdout=subprocess.DEVNULL
        )
        
        if check.returncode != 0:
            subprocess.run(
                ["iptables", "-A", "INPUT", "-p", "icmp", "-j", "DROP"], 
                check=True
            )
        return True
    except subprocess.CalledProcessError as e:
        print(color_text(f"error: failed disabling ICMP responses: {e}"))
        return False


def enable_icmp():
    try:
        check = subprocess.run(
            ["iptables", "-C", "INPUT", "-p", "icmp", "-j", "DROP"], 
            stderr=subprocess.DEVNULL, 
            stdout=subprocess.DEVNULL
        )
        
        if check.returncode == 0:
            subprocess.run(
                ["iptables", "-D", "INPUT", "-p", "icmp", "-j", "DROP"], 
                check=True
            )
        return True
    except subprocess.CalledProcessError as e:
        print(color_text(f"error enabling ICMP responses: {e}", "red"))
        return False


def save_firewall_rules():
    try:
        if os.path.exists("/usr/bin/iptables-save"):
            subprocess.run(["iptables-save", ">", "/etc/iptables/rules.v4"], 
                           shell=True, check=True)
            print("firewall rules saved successfully.")
            return True
        else:
            print("warning: iptables-save not found. Changes won't persist after reboot.")
            print("install iptables-persistent package to make changes permanent.")
            return False
    except subprocess.CalledProcessError as e:
        print(color_text(f"error: failed saving firewall rules: {e} :(", "red"))
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Enable/disable ARP and ICMP responses on Linux."
    )
    parser.add_argument(
        "--revert", 
        action="store_true", 
        help="Revert changes (enable ARP and ICMP responses)"
    )
    parser.add_argument(
        "--interface", 
        help="Specify network interface(s) (comma-separated). If not specified, all interfaces are affected."
    )
    parser.add_argument(
        "--save", 
        action="store_true", 
        help="Save iptables rules to persist after reboot"
    )
    parser.add_argument(
        "--only-arp",
        action="store_true",
        help="Only apply changes to ARP settings"
    )
    parser.add_argument(
        "--only-icmp",
        action="store_true",
        help="Only apply changes to ICMP settings"
    )
    args = parser.parse_args()

    check_root()

    if args.interface:
        interfaces = args.interface.split(',')
    else:
        interfaces = get_interfaces()
        if not interfaces:
            print(color_text("error: no network interfaces found. :(", "red"))
            return

    if args.revert:
        print(f"""by kvts
┓ ┓•   ┓┏  ┓ ┓
┣┓┃┓┏┓┏┫╋┏┓┃┏┫
┗┛┗┗┛┗┗┻┛┗┛┗┗┻
enabling ARP responses for interfaces:\n{' / '.join(interfaces)}""")

        if not args.only_icmp:
            for iface in interfaces:
                if enable_arp(iface):
                    print(f"| ARP enabled for {iface}")
                else:
                    print(color_text(f"error: failed to enable ARP for {iface} :(", "red"))

        if not args.only_arp:
            print("enabling ICMP responses...")
            if enable_icmp():
                print("| ICMP responses enabled")
            else:
                print(color_text("error: failed to enable ICMP responses :(", "red"))

    else:
        print(f"""by kvts 
┓ ┓•   ┓┏  ┓ ┓
┣┓┃┓┏┓┏┫╋┏┓┃┏┫
┗┛┗┗┛┗┗┻┛┗┛┗┗┻
disabling ARP/ICMP for interfaces:\n{' / '.join(interfaces)}""")

        if not args.only_icmp:
            for iface in interfaces:
                if disable_arp(iface):
                    print(f"| ARP disabled for {iface}")
                else:
                    print(color_text(f"error: failed to disable ARP for {iface}", "red"))

        if not args.only_arp:
            if disable_icmp():
                print("| ICMP responses disabled")
            else:
                print(color_text("error: failed to disable ICMP responses :(", "red"))

    if args.save:
        save_firewall_rules()


if __name__ == "__main__":
    main()
