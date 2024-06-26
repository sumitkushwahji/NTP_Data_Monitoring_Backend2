import ntplib
import matplotlib.pyplot as plt
import os

# Ensure 'ntpweb' static directory exists
static_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'ntpweb')
os.makedirs(static_dir, exist_ok=True)

def get_offset_and_delay_from_otherntp(server):
    ntp_client = ntplib.NTPClient()
    try:
        response = ntp_client.request(server)
        offset = response.offset
        delay = response.delay
        processing_time = response.tx_time - response.recv_time
        return offset, delay, processing_time
    except ntplib.NTPException as e:
        print(f"Error querying NTP server {server}: {e}")
        return 0, 0, 0

def main():
    other_ntp_servers = [
        'time.nplindia.org', 'time.nplindia.in',
        '14.139.60.103', '14.139.60.106', '14.139.60.107',
        'samay1.nic.in', 'samay2.nic.in', '157.20.66.8', '157.20.67.8', 
        'time.nist.gov', 'time.google.com', 'uk.pool.ntp.org', 'time.windows.com',
        'ptbtime1.ptb.de',  
    ]

    other_server_names = []
    offsets = []
    delays = []
    processing_times = []

    for server in other_ntp_servers:
        offset, delay, processing_time = get_offset_and_delay_from_otherntp(server)
        other_server_names.append(server)
        offsets.append(offset)
        delays.append(delay)
        processing_times.append(processing_time)

    plt.figure(figsize=(12, 6))
    plt.bar(other_server_names, offsets, color='green', alpha=0.7, label='Offset')
    plt.xlabel('NTP Servers', fontsize=16, fontweight='bold')
    plt.ylabel('Offset (seconds)', fontsize=16, fontweight='bold')
    plt.title('NTP Servers Offset Worldwide', fontsize=20, fontweight='bold')
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.yticks(fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(static_dir, 'offset_plot.png'), bbox_inches='tight')
    plt.close()

    plt.figure(figsize=(12, 6))
    plt.bar(other_server_names, delays, color='blue', alpha=0.7, label='Delay')
    plt.xlabel('NTP Servers', fontsize=16, fontweight='bold')
    plt.ylabel('Delay (seconds)', fontsize=16, fontweight='bold')
    plt.title('NTP Servers Delay', fontsize=20, fontweight='bold')
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.yticks(fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(static_dir, 'delay_plot.png'), bbox_inches='tight')
    plt.close()

    plt.figure(figsize=(12, 6))
    plt.bar(other_server_names, processing_times, color='pink', alpha=0.7, label='Processing Time')
    plt.xlabel('NTP Servers', fontsize=16, fontweight='bold')
    plt.ylabel('Processing Time (seconds)', fontsize=16, fontweight='bold')
    plt.title('NTP Servers Processing Time Worldwide', fontsize=20, fontweight='bold')
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.yticks(fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(static_dir, 'processing_time_plot.png'), bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    main()
