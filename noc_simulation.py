import random
from collections import deque

# Define a router class to simulate processing units in wafer-scale NoC
class Router:
    def __init__(self, router_id, latency=1):
        self.router_id = router_id
        self.latency = latency
        self.east_port = None
        self.west_port = None
        self.north_port = None
        self.south_port = None
        self.up_port = None
        self.down_port = None
        self.failed = False  # Flag to indicate if the router has failed

# Define a simple link class to simulate links between routers
class Link:
    def __init__(self, link_id, latency=1):
        self.link_id = link_id
        self.latency = latency
        self.failed = False  # Flag to indicate if the link has failed

# Define the 3D mesh topology with fault tolerance
class Wafer3DMeshTopology:
    def __init__(self, num_rows, num_cols, num_layers, link_latency, router_latency, fault_probability=0.1):
        self.num_rows = num_rows  # Number of rows in X direction
        self.num_cols = num_cols  # Number of columns in Y direction
        self.num_layers = num_layers  # Number of layers in Z direction
        self.link_latency = link_latency
        self.router_latency = router_latency
        self.fault_probability = fault_probability  # Probability of faults in routers or links

    def createTopology(self):
        total_routers = self.num_rows * self.num_cols * self.num_layers
        routers = [Router(router_id=i, latency=self.router_latency) for i in range(total_routers)]
        links = []

        # Create mesh connections with fault injection
        for z in range(self.num_layers):
            for y in range(self.num_cols):
                for x in range(self.num_rows):
                    idx = z * (self.num_rows * self.num_cols) + y * self.num_rows + x
                    router = routers[idx]

                    # Connect east neighbor if it exists
                    if (x < self.num_rows - 1):
                        east_idx = idx + 1
                        if random.random() > self.fault_probability:
                            east_link = Link(link_id=idx, latency=self.link_latency)
                            router.east_port = east_link
                            routers[east_idx].west_port = east_link
                            links.append(east_link)
                        else:
                            print(f"Fault injected: East link at router {idx} failed")

                    # Connect south neighbor if it exists
                    if (y < self.num_cols - 1):
                        south_idx = idx + self.num_rows
                        if random.random() > self.fault_probability:
                            south_link = Link(link_id=idx, latency=self.link_latency)
                            router.south_port = south_link
                            routers[south_idx].north_port = south_link
                            links.append(south_link)
                        else:
                            print(f"Fault injected: South link at router {idx} failed")

                    # Connect down neighbor if it exists
                    if (z < self.num_layers - 1):
                        down_idx = idx + (self.num_rows * self.num_cols)
                        if random.random() > self.fault_probability:
                            down_link = Link(link_id=idx, latency=self.link_latency)
                            router.down_port = down_link
                            routers[down_idx].up_port = down_link
                            links.append(down_link)
                        else:
                            print(f"Fault injected: Down link at router {idx} failed")

        return routers, links

    def find_backup_route(self, src_router, dst_router):
        """Implements a simple Breadth-First Search (BFS) to find a backup route."""
        queue = deque([src_router])
        visited = set()

        while queue:
            current_router = queue.popleft()
            if current_router.router_id == dst_router.router_id:
                return True  # Path found

            visited.add(current_router.router_id)

            # Check available directions (if port and link are not failed)
            if current_router.east_port and not current_router.east_port.failed and (current_router.router_id + 1) not in visited:
                queue.append(routers[current_router.router_id + 1])

            if current_router.west_port and not current_router.west_port.failed and (current_router.router_id - 1) not in visited:
                queue.append(routers[current_router.router_id - 1])

            if current_router.south_port and not current_router.south_port.failed and (current_router.router_id + self.num_rows) not in visited:
                queue.append(routers[current_router.router_id + self.num_rows])

            if current_router.north_port and not current_router.north_port.failed and (current_router.router_id - self.num_rows) not in visited:
                queue.append(routers[current_router.router_id - self.num_rows])

            if current_router.up_port and not current_router.up_port.failed and (current_router.router_id + self.num_rows * self.num_cols) not in visited:
                queue.append(routers[current_router.router_id + self.num_rows * self.num_cols])

            if current_router.down_port and not current_router.down_port.failed and (current_router.router_id - self.num_rows * self.num_cols) not in visited:
                queue.append(routers[current_router.router_id - self.num_rows * self.num_cols])

        return False  # No path found

# Simulation parameters for a 3x3x3 3D mesh topology
num_rows = 3  # Number of rows in X direction
num_cols = 3  # Number of columns in Y direction
num_layers = 3  # Number of layers in Z direction
link_latency = 1
router_latency = 1
fault_probability = 0.1  # 10% chance of link failure

# Create the wafer-scale 3D mesh topology
topology = Wafer3DMeshTopology(num_rows, num_cols, num_layers, link_latency, router_latency, fault_probability)
routers, links = topology.createTopology()

# Testing fault-tolerant route finding
source_router = routers[0]  # Start from Router 0
destination_router = routers[10]  # Try to reach Router 10

if topology.find_backup_route(source_router, destination_router):
    print(f"Backup route found from Router {source_router.router_id} to Router {destination_router.router_id}")
else:
    print(f"No route found from Router {source_router.router_id} to Router {destination_router.router_id}")
