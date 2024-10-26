import random
from collections import deque
from dataclasses import dataclass
from typing import Optional, List, Set, Dict
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
        
    def update_thermal_model(self, ambient_temp: float, neighboring_temps: List[float]):
        """Update router temperature based on power consumption and neighboring temperatures."""
        thermal_conductivity = 0.5
        self.temperature = (self.temperature + 
                          thermal_conductivity * (sum(neighboring_temps) / len(neighboring_temps) - self.temperature) +
                          self.power_consumption * 0.1)  # Simplified thermal model
        
    def process_packet(self, packet: Packet) -> bool:
        """Process a packet and update power consumption."""
        if self.current_buffer_usage >= self.buffer_size:
            return False
        
        self.packet_queue.append(packet)
        self.current_buffer_usage += 1
        self.power_consumption += 0.1 * packet.size  # Simplified power model
        return True

class Link:
    """Enhanced link class with bandwidth and congestion modeling."""
    def __init__(self, link_id: int, latency: int = 1, bandwidth: float = 1.0):
        self.link_id = link_id
        self.latency = latency
        self.bandwidth = bandwidth  # GB/s
        self.utilization = 0.0
        self.failed = False
        self.current_load = 0
        
    def can_transmit(self, packet_size: int) -> bool:
        """Check if link can handle additional transmission."""
        return (self.current_load + packet_size) <= (self.bandwidth * 1024)  # Convert to MB

class Wafer3DMeshTopology:
    def __init__(self, num_rows: int, num_cols: int, num_layers: int,
                 link_latency: int, router_latency: int, fault_probability: float = 0.1):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.num_layers = num_layers
        self.link_latency = link_latency
        self.router_latency = router_latency
        self.fault_probability = fault_probability
        self.clock_cycle = 0
        self.total_packets_sent = 0
        self.total_packets_dropped = 0
        
    def createTopology(self) -> tuple[List[Router], List[Link]]:
        """Create topology with enhanced fault injection and monitoring."""
        total_routers = self.num_rows * self.num_cols * self.num_layers
        routers = [Router(router_id=i, latency=self.router_latency) 
                  for i in range(total_routers)]
        links = []
        
        # Create mesh connections with realistic fault modeling
        for z in range(self.num_layers):
            for y in range(self.num_cols):
                for x in range(self.num_rows):
                    idx = self._get_router_index(x, y, z)
                    router = routers[idx]
                    
                    # Connect neighbors with variable bandwidth based on distance
                    self._connect_neighbors(router, routers, links, x, y, z)
                    
        return routers, links
    
    def _get_router_index(self, x: int, y: int, z: int) -> int:
        """Calculate router index from coordinates."""
        return z * (self.num_rows * self.num_cols) + y * self.num_rows + x
    
    def _connect_neighbors(self, router: Router, routers: List[Router], 
                         links: List[Link], x: int, y: int, z: int) -> None:
        """Connect router to its neighbors with enhanced fault modeling."""
        directions = [
            ('east', (1, 0, 0)), ('south', (0, 1, 0)), ('down', (0, 0, 1))
        ]
        
        for direction, (dx, dy, dz) in directions:
            if self._is_valid_position(x + dx, y + dy, z + dz):
                neighbor_idx = self._get_router_index(x + dx, y + dy, z + dz)
                
                # Model link reliability based on distance
                distance_factor = np.sqrt(dx*dx + dy*dy + dz*dz)
                fault_prob = self.fault_probability * distance_factor
                
                if random.random() > fault_prob:
                    bandwidth = 1.0 / distance_factor  # Bandwidth decreases with distance
                    link = Link(len(links), self.link_latency, bandwidth)
                    
                    # Set bidirectional connections
                    opposite_direction = self._get_opposite_direction(direction)
                    router.ports[direction] = link
                    routers[neighbor_idx].ports[opposite_direction] = link
                    links.append(link)
    
    def _is_valid_position(self, x: int, y: int, z: int) -> bool:
        """Check if position is within topology bounds."""
        return (0 <= x < self.num_rows and 
                0 <= y < self.num_cols and 
                0 <= z < self.num_layers)
    
    @staticmethod
    def _get_opposite_direction(direction: str) -> str:
        """Get opposite direction for bidirectional connections."""
        opposites = {'east': 'west', 'west': 'east',
                    'north': 'south', 'south': 'north',
                    'up': 'down', 'down': 'up'}
        return opposites[direction]
    
    def find_backup_route(self, src_router: Router, dst_router: Router, 
                         max_hops: int = 20) -> List[Router]:
        """Enhanced routing algorithm with congestion awareness."""
        queue = deque([(src_router, [src_router])])
        visited = set()
        
        while queue:
            current_router, path = queue.popleft()
            if len(path) > max_hops:
                continue
                
            if current_router.router_id == dst_router.router_id:
                return path
                
            visited.add(current_router.router_id)
            
            # Check all available directions with congestion awareness
            for direction, link in current_router.ports.items():
                if not link or link.failed:
                    continue
                    
                next_router_id = self._get_next_router_id(current_router.router_id, direction)
                if next_router_id not in visited and link.can_transmit(packet_size=1):
                    next_router = routers[next_router_id]
                    new_path = path + [next_router]
                    queue.append((next_router, new_path))
        
        return []  # No path found

    def simulate_network(self, num_cycles: int, packet_injection_rate: float = 0.1):
        """Simulate network behavior over time."""
        stats = {
            'latency': [],
            'throughput': [],
            'dropped_packets': 0,
            'power_consumption': []
        }
        
        for _ in range(num_cycles):
            self.clock_cycle += 1
            
            # Generate new packets based on injection rate
            if random.random() < packet_injection_rate:
                source = random.choice(routers)
                dest = random.choice(routers)
                packet = Packet(source.router_id, dest.router_id, 
                              self.clock_cycle, random.randint(1, 10))
                
                # Try to send packet
                route = self.find_backup_route(source, dest)
                if route:
                    self.total_packets_sent += 1
                    # Simulate packet traversal
                    for router in route:
                        if not router.process_packet(packet):
                            stats['dropped_packets'] += 1
                            break
                
            # Update thermal and power models
            total_power = 0
            for router in routers:
                neighboring_temps = [
                    routers[i].temperature for i in self._get_neighbor_indices(router.router_id)
                ]
                router.update_thermal_model(25.0, neighboring_temps)
                total_power += router.power_consumption
                
            stats['power_consumption'].append(total_power)
            
        return stats

# Test the enhanced simulation
if __name__ == "__main__":
    # Initialize topology
    topology = Wafer3DMeshTopology(3, 3, 3, 1, 1, 0.1)
    routers, links = topology.createTopology()
    
    # Run simulation
    stats = topology.simulate_network(1000, 0.1)
    
    # Print results
    print(f"Simulation Results:")
    print(f"Total packets sent: {topology.total_packets_sent}")
    print(f"Packets dropped: {stats['dropped_packets']}")
    print(f"Average power consumption: {np.mean(stats['power_consumption']):.2f} W")