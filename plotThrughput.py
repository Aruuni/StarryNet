import json
import matplotlib.pyplot as plt
import sys

# Arguments
FROM = sys.argv[1]
TO = sys.argv[2]
FROM2 = sys.argv[3]
TO2 = sys.argv[4]
TIME = 2
ORBITS = sys.argv[5]
SATS = sys.argv[6]

# Paths to the JSON files for the first set of flows
file_path_set1 = 'starlink-%s-%s-550-53-grid-LeastDelay/perf-%s-%s_%s.txt' % (ORBITS, SATS, FROM, TO, TIME)

# Paths to the JSON files for the second set of flows
file_path_set2 = 'starlink-%s-%s-550-53-grid-LeastDelay/perf-%s-%s_%s.txt' % (ORBITS, SATS, FROM2, TO2, TIME)

# Initialize lists to store time and bits per second for both sets of flows
times_set1 = []
bps_set1 = []

times_set2 = []
bps_set2 = []

# Function to read and parse the JSON data from a file
def parse_json(file_path, times, bps):
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Extract the intervals data
    intervals = data.get("intervals", [])

    for interval in intervals:
        streams = interval.get("streams", [])
        if streams:
            start = interval["sum"]["start"]
            bps_value = streams[0].get("bits_per_second")
            bps_value = bps_value / 1e6  # Convert to Megabits per second
            if bps_value is not None:
                times.append(start)
                bps.append(bps_value)

# Parse the JSON data for both sets of flows
parse_json(file_path_set1, times_set1, bps_set1)
parse_json(file_path_set2, times_set2, bps_set2)

# Plotting the bits per second over time for both sets of flows
plt.figure(figsize=(10, 5))
plt.plot(times_set1, bps_set1, marker='o', linestyle='-', color='b', label='Flow Set 1 (%s to %s)' % (FROM, TO))
plt.plot(times_set2, bps_set2, marker='x', linestyle='--', color='r', label='Flow Set 2 (%s to %s)' % (FROM2, TO2))
plt.xlabel('Time (seconds)')
plt.ylabel('Megabits per second (Mbps)')
plt.title('Megabits per Second Over Time from Node ' + FROM + ' to Node ' + TO + ' and ' + FROM2 + ' to ' + TO2)
plt.legend()
plt.grid(True)
plt.savefig('bps_over_time.png')  # Save the plot as a PNG file
plt.show()
