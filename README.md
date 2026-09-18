DIGITAL TWIN

> **A configurable AI-powered industrial platform that detects machine faults, evaluates machine health, identifies production bottlenecks, simulates possible outcomes, and supports intelligent production recovery through a live Digital Twin.**

---

## 📌 Project Overview

Manufacturing machine failures can affect the entire production line by reducing machine capacity, increasing queues, creating bottlenecks, and causing production delays.

This project provides an **end-to-end intelligent industrial monitoring and recovery platform** that connects machine-level AI with production-level decision making.

The system combines:

* 📡 Real-time Data Acquisition
* 🧠 ANN-based Fault Detection
* 📊 ML-based Machine Health Assessment
* 🌐 3D Production Digital Twin
* 🚧 Bottleneck Detection
* 🔮 What-if Simulation
* 👨‍🔧 Human-first Recovery
* 🔄 Automatic Workload Reallocation
* 🤖 AI-assisted Alert Explanation
* 🖥️ Operator Dashboard
* 🛠️ Developer Workspace

The architecture is **configuration-driven**, allowing the same platform to support different manufacturing industries. The initial configurations are **Electronics/PCB Manufacturing** and **Automobile Manufacturing**.

---

# 🎯 Problem

Traditional industrial monitoring systems often stop at:

```text
Sensor Data → Fault Detection → Alert
```

However, a machine fault can create a chain of production problems:

```text
Machine Fault
     ↓
Reduced Machine Health
     ↓
Reduced Capacity
     ↓
Queue Growth
     ↓
Production Bottleneck
     ↓
Production Impact
```

The proposed system connects these stages and provides a mechanism to evaluate and respond to production disruptions.

---

# 💡 Proposed Solution

Our platform follows:

```text
Real-Time Data
      ↓
ANN Fault Detection
      +
ML Machine Health
      ↓
Digital Twin
      ↓
Bottleneck Detection
      ↓
What-if Simulation
      ↓
Human Correction
      ↓
Recovery Decision
      ↓
Workload Reallocation
      ↓
Digital Twin Update
```

This allows the system to move from **fault detection to production-aware recovery**.

---

# 🏗️ System Architecture

```text
                    ┌──────────────────────┐
                    │  DEVELOPER WORKSPACE │
                    │ Monitor / Configure  │
                    └──────────┬───────────┘
                               │
                               ▼
                 ┌──────────────────────────┐
                 │         LAYER 1          │
                 │ Data Acquisition &       │
                 │ Communication             │
                 └────────────┬─────────────┘
                              │
                     ┌────────┴────────┐
                     ▼                 ▼
              ┌────────────┐    ┌────────────┐
              │  LAYER 2A  │    │  LAYER 2B  │
              │    ANN     │    │     ML     │
              │   Fault    │    │  Machine   │
              │ Detection  │    │   Health   │
              └─────┬──────┘    └─────┬──────┘
                    └────────┬─────────┘
                             ▼
                 ┌──────────────────────────┐
                 │         LAYER 3          │
                 │ Digital Twin             │
                 │ Bottleneck Detection     │
                 │ What-if Simulation        │
                 └────────────┬─────────────┘
                              ▼
                 ┌──────────────────────────┐
                 │         LAYER 4          │
                 │ Decision & Recovery      │
                 │ AI Alert Explanation     │
                 └────────────┬─────────────┘
                              ▼
                 ┌──────────────────────────┐
                 │    USER / OPERATOR       │
                 │       DASHBOARD          │
                 └──────────────────────────┘
```

The platform maintains **four processing layers**. The Developer Workspace and User Dashboard are separate workspaces and are not additional processing layers.

---

# 🧩 Core Components

## 1️⃣ Layer 1 — Data Acquisition & Communication

Responsible for collecting and exposing real-time machine information.

### Sensor Data

* Current
* Temperature
* Vibration
* RPM

Sensor data is designed around an MQTT-based real-time stream.

### Machine / Production Data

* Machine ID
* Status
* Processing time
* Capacity
* Utilization
* Queue length
* Throughput
* Availability

The acquisition layer supports simulated real-time data for development and can later be connected to actual industrial data sources.

---

## 2️⃣ Layer 2A — ANN Fault Detection

Uses an **Artificial Neural Network** to determine:

> **What fault is occurring?**

Initial fault classes include:

* NORMAL
* MOTOR OVERLOAD
* MOTOR OVERHEAT
* MECHANICAL / BEARING FAULT

Input features include:

```text
Current
Temperature
Vibration
RPM
```

The ANN produces a structured fault event containing the machine, fault type, confidence, severity, timestamp, and sensor information.

---

## 3️⃣ Layer 2B — ML Machine Health

Layer 2B is separate from the ANN.

### ANN

**What fault is occurring?**

### ML

**How healthy is the machine overall?**

Machine health states:

```text
HEALTHY
DEGRADED
CRITICAL
```

The model can use production and sensor features such as utilization, processing time, queue length, throughput, capacity, availability, temperature, vibration, current, and RPM.

---

## 4️⃣ Layer 3 — Digital Twin + Bottleneck + What-if

Layer 3 creates a live representation of the manufacturing environment.

The Digital Twin tracks:

* Machine status
* Capacity
* Processing time
* Utilization
* Queue
* Throughput
* Availability
* Health
* Fault/degradation state

### 🌐 3D Digital Twin

The production line is represented as an interactive 3D environment where:

* Products/materials move between machines
* Machine activity reflects production state
* Queues accumulate around affected machines
* Faults visibly affect production
* Recovery changes the production behavior

### 🚧 Bottleneck Detection

Bottlenecks are evaluated using multiple production indicators rather than utilization alone.

### 🔮 What-if Simulation

The system can evaluate scenarios such as:

* Machine remains degraded
* Machine becomes unavailable
* Reduced machine capacity
* Increased processing time
* Workload shifted to an alternative machine

Simulation results include metrics such as throughput, queue, delay, utilization, and affected machines.

---

## 5️⃣ Layer 4 — Decision & Recovery

Layer 4 connects machine problems with production recovery.

### Human-First Recovery

```text
Fault Detected
      ↓
Operator Notified
      ↓
Human Correction Window
      ↓
   ┌───────────────┐
   │               │
Corrected       Timeout
   │               │
   ▼               ▼
Resume       Evaluate Recovery
Operation         ↓
             What-if Simulation
                  ↓
           Workload Reallocation
```

The recovery engine evaluates machine compatibility, availability, capacity, queue, processing time, and What-if results before workload reallocation.

---

# 🤖 AI "Understand This Alert"

When an important machine anomaly occurs, the operator can select:

### **UNDERSTAND THIS ALERT**

The system presents verified information about:

* What happened
* Detected fault
* Sensor evidence
* Machine health
* Production impact
* Human correction window
* Recovery status
* Alternative machine
* What-if simulation result

The explanation component is designed to use backend-provided information rather than independently inventing machine states, sensor values, causes, or recovery decisions.

---

# 🖥️ User / Operator Dashboard

The operator dashboard provides a simplified view of the production environment.

### Main Features

* 🌐 Live 3D Digital Twin
* 📊 Production metrics
* 🏭 Machine status
* ❤️ Machine health
* ⚠️ Fault alerts
* 🚧 Bottleneck information
* 📦 Queue visualization
* 👨‍🔧 Human correction timer
* 🔄 Recovery status
* 🔮 What-if results
* 🤖 Understand This Alert

The dashboard is designed to display backend results without exposing technical implementation details such as MQTT, ANN architecture, Python services, or simulation internals.

---

# 🛠️ Developer Workspace

A separate workspace is provided for developers and engineers.

It provides visibility into:

* Layer 1 status
* MQTT stream
* Machine-data source
* ANN service/model
* ML service/model
* Digital Twin
* What-if simulation
* Recovery engine
* Backend/API health
* Logs
* Model versions
* Industry configuration

It is **not a fifth processing layer**.

---

# 🏭 Multi-Industry Configuration

The platform uses a **configuration-driven architecture**.

## Electronics / PCB Manufacturing

```text
M1 → Component Placement
M2 → Soldering
M3 → Inspection
M4 → Testing
M5 → Packaging
```

## Automobile Manufacturing

```text
M1 → Welding
M2 → Painting
M3 → Assembly
M4 → Testing
M5 → Packaging
```

Switching the industry changes the configured machines, production flow, parameters, models, and dashboard information while keeping the same core architecture.

---

# 🧪 Demonstration Scenario

The system can demonstrate a complete machine-fault-to-recovery cycle:

```text
All Machines Healthy
        ↓
M4 Starts Degrading
        ↓
Material Movement Slows
        ↓
Queue Increases
        ↓
ANN Detects Fault
        ↓
ML Health → DEGRADED
        ↓
Triage → HIGH
        ↓
M4 Identified as Bottleneck
        ↓
Human Correction Timer
        ↓
Correction Timeout
        ↓
What-if Evaluation
        ↓
Alternative Machine Identified
        ↓
Workload Reallocated
        ↓
Digital Twin Updates
        ↓
Production Metrics Change
```

This deterministic demo sequence is designed for clear project evaluation and hackathon demonstration.

---

# 💻 Technology Stack

| Area                  | Technologies                      |
| --------------------- | --------------------------------- |
| Programming           | Python, TypeScript                |
| Frontend              | React                             |
| 3D Visualization      | Three.js / React Three Fiber      |
| Communication         | MQTT                              |
| Real-Time Integration | WebSocket-ready architecture      |
| AI                    | Artificial Neural Network         |
| Machine Learning      | ML-based health assessment        |
| Simulation            | SimPy / Discrete-Event Simulation |
| Data Format           | JSON                              |
| Backend Communication | APIs / WebSockets                 |

---

# 📂 Repository Structure

```text
industrial-ai-platform/
│
├── layer1_data_acquisition/
├── layer2a_ann_fault_detection/
├── layer2b_ml_machine_health/
├── layer3_digital_twin/
├── layer4_decision_recovery/
│
├── developer_workspace/
├── user_dashboard/
│
├── configurations/
│   ├── electronics/
│   └── automobile/
│
└── README.md
```

Each processing layer is independently modular and can be developed and tested before full system integration.

---

# 🚀 How to Run

### Backend

```bash
git clone <repository-url>

cd industrial-ai-platform

pip install -r requirements.txt
```

Run the individual layers according to their respective project directories.

### User Dashboard

```bash
cd user_dashboard

npm install

npm run dev
```

The frontend is designed to use simulated/demo data before the backend services are connected.

---

# 🔗 Integration Flow

```text
Layer 1
   │
   ├──────────► Layer 2A ANN
   │
   └──────────► Layer 2B ML
                    │
                    ▼
              Layer 3 Digital Twin
                    │
                    ▼
              Layer 4 Recovery
                    │
                    ▼
             User Dashboard
```

The Developer Workspace communicates with the backend separately for system monitoring and configuration.

---

# ✨ Key Features

| Feature                    | Description                             |
| -------------------------- | --------------------------------------- |
| 📡 Real-Time Monitoring    | Continuous machine and production data  |
| 🧠 ANN Fault Detection     | Identifies machine fault types          |
| 📊 ML Health Assessment    | Determines overall machine health       |
| 🌐 Digital Twin            | Live 3D representation of production    |
| 🚧 Bottleneck Detection    | Identifies production constraints       |
| 🔮 What-if Simulation      | Evaluates hypothetical scenarios        |
| 👨‍🔧 Human-First Recovery | Gives operators correction time         |
| 🔄 Workload Reallocation   | Supports production recovery            |
| 🤖 Alert Explanation       | Provides structured fault context       |
| 🏭 Multi-Industry          | Electronics + Automobile configurations |
| 🛠️ Developer Workspace    | Backend monitoring and configuration    |

---

# 🎯 Project Objectives

1. Detect machine faults using Artificial Neural Networks.
2. Assess overall machine health using Machine Learning.
3. Represent production using a live Digital Twin.
4. Identify production bottlenecks.
5. Evaluate production scenarios using What-if simulation.
6. Provide a human-first fault correction workflow.
7. Support production recovery through workload reallocation.
8. Provide understandable AI-assisted alert information.
9. Support multiple manufacturing industries through configuration.
10. Maintain a modular architecture suitable for future industrial integration.

---

# 🔮 Future Scope

* Real industrial IoT sensor integration
* PLC integration
* OPC-UA connectivity
* Edge AI deployment
* Predictive maintenance
* Energy monitoring
* Multi-factory Digital Twins
* Advanced production optimization
* Cloud deployment
* Additional manufacturing industries

---

# 👥 Team

| Member   | Responsibility                       |
| -------- | ------------------------------------ |
| Member 1 | Layer 1 — Data Acquisition           |
| Member 2 | Layer 2A — ANN Fault Detection       |
| Member 3 | Layer 2B — ML Machine Health         |
| Member 4 | Layer 3 — Digital Twin & Simulation  |
| Member 5 | Layer 4 — Recovery & Decision        |
| Member 6 | User Dashboard / Developer Workspace |

> Replace the member names and responsibilities above with your actual team details.

---

# 🏆 Project Highlights

### From Detection → Understanding → Simulation → Recovery

This project does not stop at identifying a machine fault.

It connects:

**Machine Data → AI Detection → Machine Health → Production Impact → Digital Twin → What-if Analysis → Human Response → Recovery**

The result is a configurable architecture for **AI-driven industrial monitoring and production recovery**.

---

## 📜 Project Status

**🚧 Prototype / Hackathon Project**

Developed as a modular industrial AI platform with configurable support for Electronics/PCB and Automobile manufacturing.

---

## 📄 License

This project is developed for academic and hackathon purposes.
