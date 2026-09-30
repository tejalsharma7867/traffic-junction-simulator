# Adaptive Traffic Junction Simulator

A Python-based traffic intersection simulator that compares fixed-time traffic signal control with a rule-based adaptive controller. The project combines a discrete-time traffic simulation, configurable traffic generation, signal-control logic, live performance statistics, an interactive Pygame visualizer, and a headless experiment runner.

## Overview

The simulator models a four-way intersection with traffic approaching from:

- North
- South
- East
- West

Vehicles are generated stochastically at configurable traffic intensities. A signal controller determines which axis receives a green signal, and the movement engine advances vehicles while enforcing stop lines and vehicle spacing.

The project provides two control strategies:

1. **Fixed-time control**
   - Uses a predetermined signal cycle.
   - North-South and East-West green phases have fixed durations.
   - Does not react to the current traffic queues.

2. **Adaptive control**
   - Measures the current queue on each axis.
   - Gives the next green phase to the axis with greater demand.
   - Dynamically chooses green duration.
   - Includes a fairness mechanism intended to prevent prolonged starvation of an approach.

The simulator also records average waiting time, maximum observed waiting time, average queue length, maximum queue length, throughput, and vehicles remaining in the system.

## Features

- Four-direction intersection simulation
- Fixed-time and adaptive signal controllers
- Low, medium, and high traffic-intensity presets
- Configurable directional traffic weights
- Seeded random traffic generation for reproducible experiments
- Vehicle queueing and collision-spacing constraints
- Signal phases:
  - `NS_GREEN`
  - `NS_YELLOW`
  - `EW_GREEN`
  - `EW_YELLOW`
  - `ALL_RED`
- Live statistics dashboard
- Interactive Pygame visualization
- Pause, resume, reset, mode switching, traffic-intensity switching, and simulation-speed controls
- Headless experiment runner
- CSV export for experiment results
- Unit tests covering simulation, controllers, movement, statistics, and experiment infrastructure

## Project Structure

```text
adaptive_traffic_junction/
├── main.py
├── settings.py
├── requirements.txt
├── run_experiments.py
│
├── core/
│   ├── simulation.py
│   ├── vehicle.py
│   ├── movement.py
│   ├── traffic_generator.py
│   └── stats.py
│
├── control/
│   ├── signal_state.py
│   ├── fixed_controller.py
│   └── adaptive_controller.py
│
├── ui/
│   ├── app.py
│   ├── renderer.py
│   ├── hud.py
│   ├── controls.py
│   └── theme.py
│
├── experiments/
│   └── experiment_runner.py
│
└── tests/
    ├── test_phase1.py
    ├── test_phase2.py
    ├── test_phase3.py
    ├── test_phase4.py
    ├── test_phase5.py
    ├── test_phase6.py
    ├── test_phase7.py
    ├── test_phase8.py
    └── test_exit.py
```

## Architecture

The system is separated into five main layers:

```text
Traffic Generator
       |
       v
Simulation Engine <---- Signal Controller
       |
       +---- Vehicle Movement
       |
       +---- Statistics Tracker
       |
       v
Pygame Renderer / HUD

Simulation Engine
       |
       v
Experiment Runner
       |
       v
CSV Results
```

### Core simulation

`core/simulation.py` owns the simulation state and advances the system in fixed time steps.

Each simulation tick performs the following sequence:

1. Generate new vehicles.
2. Update the signal controller.
3. Update vehicle movement.
4. Advance simulation time.
5. Update statistics.

The simulation runs at 20 ticks per simulated second.

### Traffic generation

`core/traffic_generator.py` generates vehicles using a seeded pseudo-random number generator.

The default traffic rates are approximately:

| Intensity | Rate per direction per second |
|---|---:|
| LOW | 0.25 |
| MEDIUM | 0.60 |
| HIGH | 1.10 |

Directional weights can be changed independently, allowing asymmetric traffic scenarios.

### Vehicle movement

`core/movement.py` manages:

- Approach movement
- Stop-line behavior
- Junction crossing
- Vehicle spacing
- Exit detection
- Waiting-time accumulation

Vehicles cannot enter the junction when their direction does not have a green signal. Vehicles in the same approach lane are constrained by the vehicle ahead.

### Fixed controller

`control/fixed_controller.py` cycles through:

```text
NS_GREEN
NS_YELLOW
ALL_RED
EW_GREEN
EW_YELLOW
ALL_RED
```

Default green duration is 6 seconds, yellow duration is 1.5 seconds, and all-red clearance is 0.5 seconds.

### Adaptive controller

`control/adaptive_controller.py` calculates demand using the current queue length on each axis:

```text
NS demand = N queue + S queue
EW demand = E queue + W queue
```

The controller selects the axis with the greater demand. Green duration is calculated as:

```text
green_time = min_green + demand * seconds_per_waiting_vehicle
```

The result is clamped between the configured minimum and maximum green times.

The implementation also checks maximum active waiting time. If an axis contains a vehicle that has waited longer than the fairness threshold, a demand bonus is added to that axis.

Default adaptive parameters:

| Parameter | Value |
|---|---:|
| Minimum green | 3.0 s |
| Maximum green | 12.0 s |
| Added time per waiting vehicle | 0.35 s |
| Fairness wait threshold | 15.0 s |
| Fairness bonus | 5 vehicles equivalent |

## Interactive Controls

The Pygame application provides:

| Control | Action |
|---|---|
| Pause / Resume | Stop or continue the simulation |
| Reset | Reset simulation state and random seed |
| Fixed | Switch to fixed-time control |
| Adaptive | Switch to adaptive control |
| Low | Low traffic intensity |
| Medium | Medium traffic intensity |
| High | High traffic intensity |
| Speed | Cycle through 1x, 2x, and 4x |

Keyboard shortcuts:

| Key | Action |
|---|---|
| `Space` | Pause / resume |
| `R` | Reset |
| `M` | Toggle fixed/adaptive mode |
| `1` | Low traffic |
| `2` | Medium traffic |
| `3` | High traffic |
| `S` | Cycle simulation speed |
| `Q` or `Esc` | Quit |

## Installation

Python 3.11 or newer is recommended.

Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

The project currently requires:

```text
pygame>=2.6.1
```

## Run the Simulator

From the project directory:

```bash
python main.py
```

The application opens an interactive four-way junction visualization.

## Run Headless Experiments

Run the default experiment matrix:

```bash
python run_experiments.py
```

Example with multiple seeds:

```bash
python run_experiments.py \
  --duration 60 \
  --seeds 42 43 44 \
  --intensities LOW MEDIUM HIGH \
  --modes fixed adaptive \
  --output results/experiment_results.csv
```

The experiment runner evaluates every requested combination of:

- Controller mode
- Traffic intensity
- Random seed

The resulting CSV contains throughput, waiting time, queue statistics, and remaining vehicles.

## Metrics

The simulator tracks:

### Throughput

Number of vehicles that successfully exit the junction.

### Average waiting time

Average waiting time for vehicles that have completed the simulation journey.

### Maximum observed waiting time

Maximum waiting time observed among completed and currently active vehicles.

### Average queue length

Average number of vehicles that have not yet entered the junction across sampled simulation ticks.

### Maximum queue length

Largest queue observed during the run.

### Vehicles remaining

Vehicles still active in the simulation when the experiment ends.

## Example Experimental Results

The included verification run used:

- 60 simulated seconds per experiment
- Seeds 42, 43, and 44
- LOW, MEDIUM, and HIGH traffic
- Both fixed and adaptive controllers

The three-seed averages were:

| Intensity | Mode | Avg wait | Avg queue | Max wait | Max queue | Passed | Remaining |
|---|---|---:|---:|---:|---:|---:|---:|
| LOW | Fixed | 3.68 s | 5.45 | 11.92 s | 12.33 | 54.67 | 7.33 |
| LOW | Adaptive | 3.87 s | 5.92 | 14.13 s | 12.33 | 50.67 | 11.33 |
| MEDIUM | Fixed | 5.00 s | 13.63 | 12.27 s | 23.33 | 121.67 | 21.67 |
| MEDIUM | Adaptive | 5.31 s | 14.92 | 15.73 s | 24.67 | 119.33 | 24.00 |
| HIGH | Fixed | 7.35 s | 38.27 | 43.48 s | 61.00 | 190.00 | 66.00 |
| HIGH | Adaptive | 8.16 s | 39.83 | 30.55 s | 62.67 | 189.33 | 66.67 |

These results are illustrative simulation outputs for the supplied implementation, not evidence that one controller is universally superior. Performance depends on the traffic-generation model, controller parameters, simulation duration, random seed, and other assumptions.

An important observation from the supplied experiment is that adaptive control reduced the maximum observed waiting time under the high-intensity scenarios while not consistently reducing average waiting time or queue length. This illustrates why multiple metrics are useful when evaluating traffic-control strategies.

## Testing

The repository contains unit tests organized by development phase. The verification run performed while preparing this documentation executed 54 tests:

- 52 tests passed.
- 2 UI-related test modules could not be imported in the documentation runtime because `pygame` was not installed in that runtime.

The headless simulation and experiment infrastructure were executable and produced deterministic results for repeated seeds.

For a fully local test run after installing dependencies:

```bash
python -m unittest discover -s tests -v
```

## Reproducibility

Experiments accept explicit random seeds:

```bash
python run_experiments.py --seeds 42 43 44
```

Using the same seed, traffic generation is repeatable. This makes it possible to compare controller behavior under the same generated traffic sequence.

## Design Decisions

### Discrete-time simulation

A fixed simulation step makes state updates predictable and makes experiments easier to reproduce.

### Controller abstraction

The simulation engine accepts a controller object. This separates signal-control policy from vehicle movement and allows additional controllers to be implemented without rewriting the simulation engine.

### Headless experiment mode

The experiment runner uses the same simulation and controller classes without opening the Pygame interface. This makes batch comparisons and CSV export possible.

### Statistics separation

Statistics are maintained independently from movement and signal control. This keeps measurement logic separate from the mechanisms being measured.

## Limitations

This is a simulation model rather than a calibrated real-world traffic model. Important simplifications include:

- A single lane representation per approach.
- Simplified vehicle dynamics.
- No pedestrian phase.
- No turning movements.
- No emergency-vehicle priority.
- No real-world road geometry.
- No sensor noise.
- No real traffic-camera input.
- Traffic generation is stochastic rather than learned from real traffic data.
- The adaptive controller is rule-based rather than machine-learning based.
- The experiment model uses synthetic traffic rather than a calibrated traffic dataset.

## Future Work

Possible extensions include:

1. Add left-turn and right-turn movements.
2. Support multiple lanes per approach.
3. Add pedestrian crossings and pedestrian phases.
4. Add emergency-vehicle priority.
5. Add configurable saturation flow and realistic car-following models.
6. Add real traffic datasets for calibration.
7. Compare additional controllers such as actuated control and optimization-based control.
8. Add automated charts to the experiment pipeline.
9. Add confidence intervals across many random seeds.
10. Add a web-based visualization layer.
11. Add reinforcement-learning-based signal control as a separate experimental controller.
12. Export simulation replays for later analysis.

## License

No license is specified in the supplied project archive. Add a license before distributing the project publicly if required.
