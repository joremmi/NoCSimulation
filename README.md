
# 3D Network-on-Chip (NoC) Simulation

This project simulates a 3D Network-on-Chip (NoC) topology with enhanced fault tolerance, power management, and thermal-aware routing. The simulation allows for the injection of faults into routers and links, while also dynamically managing power consumption and handling thermal conditions. The simulation outputs key metrics such as latency, throughput, and power consumption, along with visualizations to understand the network's performance.

## Features

- **3D Mesh Topology**: Simulates a multi-layer 3D NoC.
- **Fault Tolerance**: Random faults injected into routers and links, with backup routing paths.
- **Power Management**: Adjusts power consumption based on router load and ambient temperature.
- **Thermal Management**: Routers adjust activity based on temperature thresholds.
- **Performance Metrics**: Tracks latency, throughput, and power consumption over simulation cycles.
- **Visualization**: Outputs graphs for latency, throughput, and power consumption trends.

## Project Structure

- **modified_noc_simulation.py**: Contains the `Wafer3DMeshTopology` class, the core logic of the NoC simulation, and power, fault, and thermal management.
- **run_simulation.py**: Initializes the topology, runs the simulation, and generates visualizations and statistics.
  
## Installation

### Requirements

- **Python 3.x**
- **matplotlib**: For generating plots.
- **numpy**: For efficient mathematical operations.

### Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/3D_NOC_Simulation.git
   cd 3D_NOC_Simulation
   ```

2. Install the required libraries:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Configure Simulation Parameters** in `run_simulation.py`:
   - `num_rows`, `num_cols`, `num_layers`: Dimensions of the 3D NoC grid.
   - `link_latency`, `router_latency`: Latency for links and routers.
   - `fault_probability`: Probability of fault injection.
   - `num_cycles`: Total simulation cycles.
   - `packet_injection_rate`: Rate of packet injection per cycle.

2. **Run the Simulation**:
   ```bash
   python run_simulation.py
   ```

3. **View Results**: The simulation will output plots for average latency, throughput, and power consumption. Final statistics are printed in the console.

## Example Output

The simulation outputs graphs for:
- **Average Latency**: Average time in cycles that packets spend in the network.
- **Throughput**: Number of packets successfully sent per cycle.
- **Power Consumption**: Total power consumption of the network in Watts.

Below is an example of the expected visual output:
![sim](https://github.com/user-attachments/assets/b03f8c3e-f44d-4b4f-bac1-dae326328478)


## Configuration Options

- **Fault Tolerance**: Routers and links have a certain probability of failure, simulating real-world degradation. Backup paths are used for rerouting when faults occur.
- **Thermal Management**: Routers adapt activity based on temperature. Routers approaching a critical temperature threshold may experience reduced packet throughput.
- **Power Management**: Power consumption is calculated based on router load and adjusted according to temperature.

## Code Overview

- `Wafer3DMeshTopology`: The main class for creating and managing the 3D NoC.
  - **Methods**:
    - `createTopology()`: Initializes routers and links.
    - `simulate_network()`: Runs the simulation for a set number of cycles.
    - `inject_faults()`: Randomly injects faults in routers and links.
    - `find_backup_route()`: Finds alternative paths to avoid faulty links.
    - `update_power_and_temperature()`: Adjusts power based on load and temperature.
  - **Classes**:
    - `Router`: Manages packet routing, power, and thermal adjustments.
    - `Link`: Represents connections between routers and manages latency and fault status.

## Future Work

- **Thermal Simulation Refinements**: Add more precise temperature fluctuation models.
- **Enhanced Fault Tolerance**: Explore machine learning models for predictive fault tolerance.
- **Network Load Balancing**: Implement dynamic load balancing algorithms.
