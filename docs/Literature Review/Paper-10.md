# Paper 10: Quantum Machine Learning Algorithms for Anomaly Detection

## Bibliographic Information
- **Title**: Quantum machine learning algorithms for anomaly detection: A review
- **Authors**: Sebastiano Corli, Lorenzo Moro, Daniele Dragoni, Massimiliano Dispenza, Enrico Prati
- **Year**: 2024
- **Journal/Conference**: Future Generation Computer Systems / arXiv preprint arXiv:2408.11047
- **Publisher**: Elsevier
- **DOI**: 10.1016/j.future.2024.12.012
- **URL**: [https://arxiv.org/abs/2408.11047](https://arxiv.org/abs/2408.11047)

## Executive Summary
This paper reviews the state of the art in Quantum Machine Learning (QML) applied to anomaly detection. It categorizes algorithms into supervised, unsupervised, and reinforcement learning paradigms, evaluates computational complexity, and estimates the future hardware resources required for practical quantum speedup.

## Technical Summary
The authors present a structured review bridging quantum circuit formalisms with anomaly detection. It explains:
1. Mapping classical data to qubits using quantum feature maps.
2. Parameterized Quantum Circuits (PQCs) trained via classical optimization.
3. Specific architectures including Quantum Autoencoders (QAEs) and Quantum Support Vector Machines (QSVMs), profiling their theoretical performance against classical models.

## Architecture
- **Hybrid Classical-Quantum Architecture**:
  - **Classical Component**: Preprocesses network/image data, manages optimization gradients (e.g., COBYLA, Adam), and updates parameterized gate angles.
  - **Quantum Component**: Encodes vectors into qubits, runs unitary operations on Noisy Intermediate-Scale Quantum (NISQ) circuits, and measures output states to compute loss (reconstruction error or classification margins).

## Algorithms
- **Quantum Autoencoder (QAE)** (for unsupervised compression-based anomaly detection).
- **Quantum Support Vector Machine (QSVM)** (for kernel-based classification).
- **Quantum Convolutional Neural Network (QCNN)**.
- **Quantum Reinforcement Learning (QRL)**.

## Technologies
- **Quantum Simulators** (Qiskit, Pennylane), **NISQ** hardware processors, **Quantum Annealers**.

## Dataset
- MNIST, KDD99, and Large Hadron Collider (LHC) particle collision datasets.

## Experimental Results
- Simulator-based tests demonstrate that Quantum Autoencoders achieve comparable or higher reconstruction accuracy for out-of-distribution (anomalous) samples compared to classical autoencoders. Under specific conditions, QSVMs yield a quadratic speedup for kernel evaluations, though NISQ hardware limits the number of features that can be analyzed.

## Strengths
- Mathematically rigorous definitions of quantum speedup in security contexts.
- Detailed estimation of hardware resources (qubit count, gate depth, error rates) needed for future production scaling.

## Author Reported Limitations
- Noisy Intermediate-Scale Quantum (NISQ) hardware limitations (decoherence times, high gate error rates).
- **Barren Plateaus**: Gradient vanishing problems in high-dimensional Parameterized Quantum Circuits.
- High computational overhead of classical-to-quantum state preparation (amplitude encoding).

## Future Work
- Developing error mitigation and error correction strategies on NISQ hardware.
- Barren plateau avoidance techniques (e.g., local cost functions, layer-by-layer training).
- Benchmarking QML models on real-world industrial security log streams.

## Important Concepts
- **Quantum Feature Map**: The unitary operation that embeds classical vectors into the quantum Hilbert state space.
- **Barren Plateau**: The phenomenon where the gradient of the cost function vanishes exponentially with the number of qubits, making training impossible.

## Our Observations
- Confirms that production-grade QML for cloud logging is currently simulator-bound due to qubit limits. Therefore, a realistic project scope should focus on **quantum-aware migration planning and simulator-based validation** (e.g., testing liboqs PQC algorithms and simulating QAEs on small telemetry samples).

## Relevance to Our Research
- High. Direct justification of our hybrid research scope: we are not building raw QML algorithms for production, but rather formulating a "Quantum-Aware Security Planning" layer, testing PQC migration, and simulating future quantum anomaly detection.

## Possible Adoption
- Incorporating a simulation module within our verification plan using Qiskit to run a simple Quantum Autoencoder anomaly check on small sample sets.
