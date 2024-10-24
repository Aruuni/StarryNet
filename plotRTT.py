import os
import sys
import re
import matplotlib.pyplot as plt

def extract_rtt(directory, from_node, to_node):
    times = []
    rtts = []
    for second in range(1, 500):
        filename = f"ping-{from_node}-{to_node}_{second}.txt"
        filepath = os.path.join(directory, filename)
        
        if os.path.isfile(filepath):
            with open(filepath, 'r') as file:
                content = file.read()
                
                # Extract the average RTT using regex
                match = re.search(r'rtt min/avg/max/mdev = [\d\.]+/([\d\.]+)/[\d\.]+/[\d\.]+ ms', content)
                if match:
                    avg_rtt = float(match.group(1))
                    times.append(second)
                    rtts.append(avg_rtt)
    return times, rtts

# Command-line arguments
FROM1 = sys.argv[1] 
TO1 = sys.argv[2]
FROM2 = sys.argv[3]
TO2 = sys.argv[4] 
ORBITS = sys.argv[5]
SATS = sys.argv[6]


directory = f"starlink-{ORBITS}-{SATS}-550-53-grid-LeastDelay"
print(directory)

# Extract RTT for both flows
times1, rtts1 = extract_rtt(directory, FROM1, TO1)
times2, rtts2 = extract_rtt(directory, FROM2, TO2)

# Plotting the RTT over time for both flows
plt.figure(figsize=(10, 5))
plt.plot(times1, rtts1, marker='o', linestyle='-', color='b', label=f'Flow {FROM1} to {TO1}')
plt.plot(times2, rtts2, marker='s', linestyle='-', color='r', label=f'Flow {FROM2} to {TO2}')
plt.xlabel('Time (seconds)')
plt.ylabel('RTT (ms)')
plt.title('Average RTT Over Time')
plt.legend()
plt.grid(True)
plt.savefig('rtt_over_time.png')  # Save the plot as a PNG file
plt.show()