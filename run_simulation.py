from modified_noc_simulation import Wafer3DMeshTopology
import matplotlib.pyplot as plt

# Initialize parameters for simulation
num_rows, num_cols, num_layers = 4, 4, 4
link_latency, router_latency = 1, 1
fault_probability = 0.05
num_cycles = 1000
packet_injection_rate = 0.05

# Initialize network topology
network = Wafer3DMeshTopology(num_rows, num_cols, num_layers, link_latency, router_latency, fault_probability)
network.createTopology()

# Run the simulation
stats = network.simulate_network(num_cycles, packet_injection_rate)

# Plot results
plt.figure(figsize=(12, 8))

# Latency plot
plt.subplot(3, 1, 1)
plt.plot(stats['latency'], label='Average Latency')
plt.xlabel("Simulation Cycle")
plt.ylabel("Latency (cycles)")
plt.title("Average Latency Over Time")
plt.legend()

# Throughput plot
plt.subplot(3, 1, 2)
plt.plot(stats['throughput'], label='Throughput')
plt.xlabel("Simulation Cycle")
plt.ylabel("Throughput (packets/cycle)")
plt.title("Throughput Over Time")
plt.legend()

# Power Consumption plot
plt.subplot(3, 1, 3)
plt.plot(stats['power_consumption'], label='Total Power Consumption')
plt.xlabel("Simulation Cycle")
plt.ylabel("Power Consumption (Watts)")
plt.title("Power Consumption Over Time")
plt.legend()

plt.tight_layout()
plt.show()

# Print final statistics
print("Final Simulation Statistics:")
print(f"Total Packets Sent: {network.total_packets_sent}")
print(f"Total Packets Dropped: {stats['dropped_packets']}")
print(f"Average Latency: {sum(stats['latency']) / len(stats['latency']):.2f}")
print(f"Average Throughput: {sum(stats['throughput']) / len(stats['throughput']):.2f}")
print(f"Average Power Consumption: {sum(stats['power_consumption']) / len(stats['power_consumption']):.2f} W")
