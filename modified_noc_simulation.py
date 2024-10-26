# modified_noc_simulation.py

import random
from collections import deque
from dataclasses import dataclass
from typing import Optional, List, Dict
import numpy as np

@dataclass
class Packet:
    """Represents a data packet in the network."""
    source_id: int
    destination_id: int
    creation_time: int
    size: int
    priority: int = 0
    current_hop_count: int = 0

class Router:
    """Enhanced router class with power and thermal modeling."""
    def __init__(self, router_id: int, latency: int = 1):
        self.router_id = router_id
        self.latency = latency
        self.ports: Dict[str, Optional['Link']] = {
            'east': None, 'west': None,
            'north': None, 'south': None,
            'up': None, 'down': None
        }
        self.failed = False
        self.buffer_size = 64  # Buffer size in packets
        self.current_buffer_usage = 0
        self.temperature = 25.0  # Initial temperature in Celsius
        self.power_consumption = 0.0  # Power consumption in Watts
        self.packet_queue = deque()
        self.power_state = 'idle'  # Track power state for consumption modeling
        self.fan_speed = 0  # Fan speed for cooling
        self.packet_loss_rate = 0.0

    def update_thermal_model(self, ambient_temp: float, neighboring_temps: List[float]):
        """Update router temperature based on power consumption and neighboring temperatures."""
        thermal_conductivity = 0.5
        self.temperature = (self.temperature +
                            thermal_conductivity * (sum(neighboring_temps) / len(neighboring_temps) - self.temperature) +
                            self.power_consumption * 0.1)

    def adjust_power_consumption(self, traffic_load=0.5):
        """Adjust power consumption based on router state and workload."""
        if self.failed:
            self.power_consumption = 0
        elif self.power_state == 'active':
            self.power_consumption = 5.0 * traffic_load
        elif self.power_state == 'idle':
            self.power_consumption = 1.0

    def update_temperature(self, ambient_temp=25.0, heat_transfer_coefficient=0.1):
        """Thermal model calculation with cooling effect based on fan speed."""
        heat_generated = self.power_consumption * 0.5
        cooling_effect = self.fan_speed * 0.1
        self.temperature += heat_generated - cooling_effect - heat_transfer_coefficient * (self.temperature - ambient_temp)

        # Adjust fan speed based on temperature
        if self.temperature > 70:
            self.fan_speed = min(self.fan_speed + 1, 5)
        elif self.temperature < 60:
            self.fan_speed = max(self.fan_speed - 1, 0)

    def update_state_based_on_conditions(self):
        """Dynamically update router state based on temperature and workload."""
        if self.temperature > 85:
            self.failed = True
        elif self.current_buffer_usage < self.buffer_size * 0.3:
            self.power_state = 'idle'
        else:
            self.power_state = 'active'
        self.adjust_power_consumption()

    def process_packet(self, packet: Packet) -> bool:
        """Process a packet and update power consumption."""
        if self.current_buffer_usage >= self.buffer_size:
            return False
        self.packet_queue.append(packet)
        self.current_buffer_usage += 1
        self.power_consumption += 0.1 * packet.size
        return True

    def handle_packet(self, packet: Packet, current_time: int):
        """Handle packet routing and update packet loss rate."""
        if self.failed or self.current_buffer_usage >= self.buffer_size:
            self.packet_loss_rate += 1 / (self.packet_loss_rate + 1)
            return
        self.current_buffer_usage += 1
        latency = self.calculate_latency(packet.creation_time, current_time)
        self.packet_loss_rate = getattr(self, 'packet_loss_rate', 0) + latency
        self.apply_backpressure()

    def calculate_latency(self, creation_time, current_time):
        """Simple latency calculation for packet transit time."""
        return current_time - creation_time

    def apply_backpressure(self):
        """Apply backpressure logic based on buffer utilization."""
        if self.current_buffer_usage >= self.buffer_size * 0.8:
            self.failed = True

class Link:
    """Enhanced link class with bandwidth and congestion modeling."""
    def __init__(self, link_id: int, latency: int = 1, bandwidth: float = 1.0):
        self.link_id = link_id
        self.latency = latency
        self.bandwidth = bandwidth
        self.utilization = 0.0
        self.failed = False
        self.current_load = 0

    def can_transmit(self, packet_size: int) -> bool:
        """Check if link can handle additional transmission."""
        return (self.current_load + packet_size) <= (self.bandwidth * 1024)

class Wafer3DMeshTopology:
    """3D mesh topology for NoC with enhanced thermal, power, and fault management."""
    def __init__(self, num_rows: int, num_cols: int, num_layers: int, link_latency: int, router_latency: int, fault_probability: float = 0.1):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.num_layers = num_layers
        self.link_latency = link_latency
        self.router_latency = router_latency
        self.fault_probability = fault_probability
        self.clock_cycle = 0
        self.total_packets_sent = 0
        self.total_packets_dropped = 0
        self.routers = []
        self.links = []

    def createTopology(self) -> tuple[List[Router], List[Link]]:
        """Create 3D topology with fault injection and monitoring."""
        total_routers = self.num_rows * self.num_cols * self.num_layers
        self.routers = [Router(router_id=i, latency=self.router_latency) for i in range(total_routers)]
        self.links = []
        
        for z in range(self.num_layers):
            for y in range(self.num_cols):
                for x in range(self.num_rows):
                    idx = self._get_router_index(x, y, z)
                    router = self.routers[idx]
                    self._connect_neighbors(router, x, y, z)

        return self.routers, self.links

    def _get_router_index(self, x: int, y: int, z: int) -> int:
        """Calculate router index from coordinates."""
        return z * (self.num_rows * self.num_cols) + y * self.num_rows + x

    def _connect_neighbors(self, router: Router, x: int, y: int, z: int) -> None:
        """Connect router to its neighbors with enhanced fault modeling."""
        directions = [('east', (1, 0, 0)), ('south', (0, 1, 0)), ('down', (0, 0, 1))]
        
        for direction, (dx, dy, dz) in directions:
            if self._is_valid_position(x + dx, y + dy, z + dz):
                neighbor_idx = self._get_router_index(x + dx, y + dy, z + dz)
                distance_factor = np.sqrt(dx * dx + dy * dy + dz * dz)
                fault_prob = self.fault_probability * distance_factor
                
                if random.random() > fault_prob:
                    bandwidth = 1.0 / distance_factor
                    link = Link(len(self.links), self.link_latency, bandwidth)
                    opposite_direction = self._get_opposite_direction(direction)
                    router.ports[direction] = link
                    self.routers[neighbor_idx].ports[opposite_direction] = link
                    self.links.append(link)

    def _is_valid_position(self, x: int, y: int, z: int) -> bool:
        """Check if position is within topology bounds."""
        return 0 <= x < self.num_rows and 0 <= y < self.num_cols and 0 <= z < self.num_layers

    def _get_opposite_direction(self, direction: str) -> str:
        """Get opposite direction for bidirectional connections."""
        opposites = {'east': 'west', 'west': 'east', 'north': 'south', 'south': 'north', 'up': 'down', 'down': 'up'}
        return opposites[direction]

    def simulate_network(self, num_cycles: int, packet_injection_rate: float = 0.1):
        """Simulate network behavior over time."""
        stats = {'latency': [], 'throughput': [], 'dropped_packets': 0, 'power_consumption': []}
        
        for _ in range(num_cycles):
            self.clock_cycle += 1
            if random.random() < packet_injection_rate:
                source = random.choice(self.routers)
                dest = random.choice(self.routers)
                if source.router_id != dest.router_id:
                    packet = Packet(source.router_id, dest.router_id, self.clock_cycle, random.randint(1, 10))
                    route = self.find_backup_route(source, dest)
                    if route:
                        self.total_packets_sent += 1
                        for router in route:
                            if not router.process_packet(packet):
                                stats['dropped_packets'] += 1
                                break
            total_power = 0
            for router in self.routers:
                total_power += router.power_consumption
                router.update_state_based_on_conditions()
                router.update_temperature()

            stats['power_consumption'].append(total_power)

            # Calculate latency and throughput
            avg_latency = np.mean([router.calculate_latency(packet.creation_time, self.clock_cycle)
                                   for router in self.routers if router.packet_queue])
            throughput = self.total_packets_sent / self.clock_cycle

            stats['latency'].append(avg_latency if avg_latency else 0)
            stats['throughput'].append(throughput)

        return stats

    def find_backup_route(self, source: Router, destination: Router) -> Optional[List[Router]]:
        """Finds a backup route between source and destination, avoiding failed routers and links."""
        visited = set()
        queue = deque([(source, [source])])

        while queue:
            current_router, path = queue.popleft()
            if current_router == destination:
                return path
            for direction, link in current_router.ports.items():
                if link and not link.failed:
                    next_router = self.get_neighbor_router(current_router, direction)
                    if next_router and next_router not in visited and not next_router.failed:
                        visited.add(next_router)
                        queue.append((next_router, path + [next_router]))
        return None

    def get_neighbor_router(self, router: Router, direction: str) -> Optional[Router]:
        """Returns neighboring router in a given direction."""
        x, y, z = self.get_router_position(router.router_id)
        if direction == 'east':
            x += 1
        elif direction == 'west':
            x -= 1
        elif direction == 'north':
            y -= 1
        elif direction == 'south':
            y += 1
        elif direction == 'up':
            z += 1
        elif direction == 'down':
            z -= 1
        if self._is_valid_position(x, y, z):
            return self.routers[self._get_router_index(x, y, z)]
        return None

    def get_router_position(self, router_id: int) -> tuple[int, int, int]:
        """Converts router ID back to 3D position."""
        layer_size = self.num_rows * self.num_cols
        z = router_id // layer_size
        y = (router_id % layer_size) // self.num_rows
        x = router_id % self.num_rows
        return x, y, z

    def inject_faults(self):
        """Randomly inject faults in routers and links based on probability."""
        for router in self.routers:
            if random.random() < self.fault_probability:
                router.failed = True
        for link in self.links:
            if random.random() < self.fault_probability:
                link.failed = True
