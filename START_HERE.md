# Industrial AI — Integrated Start

## Fastest way (Windows)

Double-click **START_ALL.bat**.

The launcher starts:

- Layer 1 UI — http://127.0.0.1:5173
- Layer 2A UI — http://127.0.0.1:5174
- Layer 3 Digital Twin UI — http://127.0.0.1:8765
- Layer 4 UI — http://127.0.0.1:5176
- **Unified Portal — http://127.0.0.1:8090**

You only need to use the Unified Portal during the demo. Each layer is embedded there and can also be opened in a new tab.

## Command-line alternative

```bat
python run_all.py
```

## Architecture

Layer 1 (Data Acquisition) → Layer 2A (ANN Fault Detection) → Layer 3 (Digital Twin / What-if) → Layer 4 (Decision & Recovery)

The original layer folders are preserved. The integration launcher only orchestrates their existing UIs, which makes the combined build less fragile.

## Layer 1 API note

Layer 1's backend API is separate from its demo UI and requires its Python dependencies plus an MQTT broker. To run it from `layer1_data_acquisition`:

```bat
pip install -r requirements.txt
python main.py
```

Its API docs then appear at http://127.0.0.1:8000/docs.
