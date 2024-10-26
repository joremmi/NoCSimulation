# test_congestion_and_performance.py

from modified_noc_simulation import Router, Packet  # Adjust import based on module name
import time

def test_congestion_and_performance():
    # Step 1: Initialize Routers
    router_A = Router(router_id=1)
    router_B = Router(router_id=2)
    
    # Step 2: Connect Routers (simplified for two routers)
    router_A.ports['east'] = router_B  # Basic directional connection for testing
    
    # Step 3: Generate Packets
    packets = [Packet(source_id=1, destination_id=2, creation_time=i, size=1) for i in range(20)]
    
    # Step 4: Simulate Packet Transmission
    for current_time, packet in enumerate(packets):
        router_A.handle_packet(packet, current_time)
        
        # Adjust router states and check metrics
        router_A.update_state_based_on_conditions()
        router_B.update_state_based_on_conditions()
        
        # Output Test Results
        print(f"Time {current_time}: Router A - Buffer Usage: {router_A.current_buffer_usage}, Temperature: {router_A.temperature}")
        print(f"Router A - Fan Speed: {router_A.fan_speed}, Power Consumption: {router_A.power_consumption}")
        print(f"Router A - Packet Loss Rate: {router_A.packet_loss_rate:.2%}")

        # Cool down time for simulation clarity
        time.sleep(0.1)  # Slows down simulation for readability

# Run the test
test_congestion_and_performance()

def test_network_performance():
    topology = Wafer3DMeshTopology(3, 3, 3, 1, 1, 0.1)
    routers, links = topology.createTopology()

    print("Starting enhanced simulation...")
    stats = topology.simulate_network(1000, 0.1)

    print("\nDetailed Simulation Results:")
    for router in routers:
        print(f"Router ID {router.router_id}:")
        print(f"  Temperature: {router.temperature:.2f} °C")
        print(f"  Power Consumption: {router.power_consumption:.2f} W")
        print(f"  Fan Speed: {router.fan_speed}")
        print(f"  State: {router.power_state}")
        print()

test_network_performance()
