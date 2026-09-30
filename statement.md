# Project Statement: Adaptive Traffic Junction Simulator

## 1. Problem Statement

Traffic signals at busy road junctions are commonly run on fixed timers. A fixed-time controller gives each direction the same green duration regardless of how many vehicles are actually waiting. When traffic is uneven, this leads to long queues on busy approaches, green time wasted on empty roads, and longer waiting times for drivers.

Testing better signal-control strategies on real roads is costly, slow, and risky. There is a need for a safe, repeatable, software-based environment where different control strategies can be compared under identical traffic conditions.

This project builds a Python simulator of a four-way junction that compares a **fixed-time signal controller** with a **rule-based adaptive controller** that responds to live queue lengths, and measures the difference using clear performance metrics.

## 2. Scope of the Project

### In scope

- Simulation of a four-way intersection with approaches from North, South, East and West.
- Discrete-time simulation (20 ticks per simulated second) with seeded random vehicle generation, so results are reproducible.
- Low, medium and high traffic-intensity presets, with configurable directional weights.
- Vehicle movement with stop lines, queueing and minimum spacing between vehicles.
- Two signal controllers:
  - **Fixed-time:** a predetermined cycle of green, yellow and all-red phases.
  - **Adaptive:** chooses the axis with greater queue demand, sets the green duration between a minimum and maximum, and includes a fairness bonus for long-waiting vehicles.
- Live statistics: average and maximum waiting time, average and maximum queue length, throughput, and vehicles remaining.
- An interactive Pygame visualization with a live dashboard and controls.
- A headless experiment runner that evaluates combinations of mode, intensity and seed, and exports results to CSV.
- Unit tests for the simulation, controllers, movement, statistics and experiment runner.

### Out of scope

- Turning movements (left and right turns) and multi-lane approaches.
- Pedestrian crossings and pedestrian signal phases.
- Emergency-vehicle priority.
- Calibration against real-world traffic data or real road geometry.
- Sensor noise, camera input, and machine-learning or reinforcement-learning controllers.

The simulator is a simplified model for learning and comparison. Its results are illustrative and do not prove that one controller is better in every real-world situation.

## 3. Target Users

- **Students and learners** studying programming, simulation, or traffic engineering concepts.
- **Instructors and evaluators** who need a clear, visual demonstration of adaptive versus fixed control.
- **Hobbyists and researchers** who want a small, extensible base for trying new signal-control ideas.
- **Developers** who want to add their own controllers through the controller abstraction without rewriting the simulation engine.

## 4. High-Level Features

1. **Four-way junction simulation** with stochastic, seed-controlled traffic generation.
2. **Fixed-time signal controller** with configurable green, yellow and all-red durations.
3. **Adaptive signal controller** that responds to queue lengths, scales green time to demand, and protects against starvation of any approach.
4. **Traffic intensity and direction weights** for modelling low, medium, high and uneven traffic.
5. **Realistic vehicle behaviour** including stopping at red, queueing and maintaining safe gaps.
6. **Live performance statistics** covering waiting time, queue length, throughput and remaining vehicles.
7. **Interactive Pygame visualizer** with pause/resume, reset, mode switching, intensity switching, speed control (1x, 2x, 4x) and keyboard shortcuts.
8. **Headless experiment runner** for batch comparisons across modes, intensities and seeds, with CSV export.
9. **Automated unit tests** organised by development phase.
