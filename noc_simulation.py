import random

# Define a router class to simulate processing units in wafer-scale NoC
class Router:
    def __init__(self, router_id, latency=1):
        self.router_id = router_id
        self.latency = latency
        self.east_port = None
        self.west_port = None
        self.north_port = None
        self.south_port = None

# Define a simple link class to simulate links between routers
class Link:
    def __init__(self, link_id, latency=1):
        self.link_id = link_id
        self.latency = latency

# Define the mesh topology
class WaferMeshTopology:
    def __init__(self, num_rows, link_latency, router_latency, fault_probability=0.1):
        self.num_rows = num_r0ows  # Set number of rows for the 2D mesh
        self.link_latency = link_latency
        self.router_latency = router_latency
        self.fault_probability = fault_probability  # Probability of faults in routers or links

    def createTopology(self):
        routers = [Router(router_id=i, latency=self.router_latency) for i in range(self.num_rows ** 2)]
        links = []

        # Create mesh connections with fault injection
        for i, router in enumerate(routers):
            # Connect east neighbor if it exists
            if (i % self.num_rows) != (self.num_rows - 1):
                if random.random() > self.fault_probability:
                    east_link = Link(link_id=i, latency=self.link_latency)
                    router.east_port = east_link
                    routers[i + 1].west_port = east_link
                    links.append(east_link)
                else:
                    print(f"Fault injected: East link at router {i} failed")

            # Connect south neighbor if it exists
            if i + self.num_rows < len(routers):
                if random.random() > self.fault_probability:
                    south_link = Link(link_id=i, latency=self.link_latency)
                    router.south_port = south_link
                    routers[i + self.num_rows].north_port = south_link
                    links.append(south_link)
                else:
                    print(f"Fault injected: South link at router {i} failed")

        return routers, links

# Traffic simulation class
class TrafficGenerator:
    def __init__(self, routers):
        self.routers = routers

    # Generate random traffic
    def random_traffic(self):
        src = random.choice(self.routers)
        dst = random.choice(self.routers)
        print(f"Random Traffic: Packet from Router {src.router_id} to Router {dst.router_id}")

    # Hotspot traffic (targeting a specific router)
    def hotspot_traffic(self, hotspot_id=0):
        dst = self.routers[hotspot_id]
        src = random.choice(self.routers)
        print(f"Hotspot Traffic: Packet from Router {src.router_id} to Router {dst.router_id}")

    # Uniform traffic pattern
    def uniform_traffic(self):
        for router in self.routers:
            dst = random.choice(self.routers)
            print(f"Uniform Traffic: Packet from Router {router.router_id} to Router {dst.router_id}")

# Define simulation parameters
num_rows = 4  # 4x4 mesh topology (16 nodes)
link_latency = 1
router_latency = 1
fault_probability = 0.1  # 10% chance of link failure

# Create the wafer-scale topology
topology = WaferMeshTopology(num_rows, link_latency, router_latency, fault_probability)
routers, links = topology.createTopology()

# Generate traffic patterns
traffic_gen = TrafficGenerator(routers)
traffic_gen.random_traffic()  # Generate random traffic
traffic_gen.hotspot_traffic(hotspot_id=0)  # Generate hotspot traffic
traffic_gen.uniform_traffic()  # Generate uniform traffic
