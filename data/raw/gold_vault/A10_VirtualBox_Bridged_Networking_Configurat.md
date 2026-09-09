# A10. VirtualBox Bridged Networking Configuration

**Source:** KodeKloud / VirtualBox Documentation

VirtualBox provides several networking modes to connect virtual machines to the host and the outside world:

- **NAT (Network Address Translation):** The VM shares the host's IP address and uses a private subnet. It can access external networks, but external machines cannot initiate connections to the VM.
- **Bridged Mode:** The VM behaves like a physical device on the same network as the host. It obtains an IP address from the network's DHCP server and can communicate directly with other hosts on the same LAN.
- **Host-only:** Creates a private network between the host and VMs, isolated from the physical network.

To configure bridged networking:

1. Open the VM settings.
2. Navigate to the **Networking** tab.
3. Select **Adapter 1** and change the attachment type from NAT to **Bridged Adapter**.
4. Choose the host's physical network interface from the dropdown list (e.g., Ethernet or Wi-Fi adapter).
5. Start the VM; it will now receive an IP from the network's DHCP server.

Bridged mode is ideal for scenarios where the VM needs to provide services to the local network or when you want the VM to be fully integrated into the physical infrastructure.
