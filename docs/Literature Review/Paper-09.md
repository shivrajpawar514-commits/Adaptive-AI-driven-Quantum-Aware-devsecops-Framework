# Paper 09: Attacks Prevention and Profiling in Cloud Computing

## Bibliographic Information
- **Title**: A Literature Review on Attacks Prevention and Profiling in Cloud Computing
- **Authors**: Nahid Eddermoug, Abdeljebar Mansour, Mohamed Azmi, Mohamed Sadik, Essaid Sabir, Hanane Bahassi
- **Year**: 2023
- **Journal/Conference**: Procedia Computer Science (Vol. 220, pp. 970-977)
- **Publisher**: Elsevier
- **DOI**: 10.1016/j.procs.2023.03.134
- **URL**: [https://doi.org/10.1016/j.procs.2023.03.134](https://doi.org/10.1016/j.procs.2023.03.134)

## Executive Summary
This paper conducts a literature review on attack prevention and threat profiling in cloud computing. It evaluates the limitations of traditional, signature-based and anomaly-based Intrusion Detection and Prevention Systems (IDPS), outlining how machine learning can be leveraged to profile threat behaviors.

## Technical Summary
The review addresses Host-based (HIDS) and Network-based (NIDS) intrusion systems, examining their placement within virtualized cloud structures (virtual machines, hypervisors, and VPC network switches). It evaluates the role of dimensionality reduction in improving the classification speed of ML models.

## Architecture
- **Multi-Level Sensor Layer**: Log agents deployed at the guest OS level, hypervisor level, and network virtualization switches.
- **Log Aggregator**: Consolidates alerts to run feature selection algorithms.
- **Profiling Engine**: Generates threat actor behavioral cards based on attack vectors (IP, port range, packet frequency, payload signature).

## Algorithms
- **Classical ML**: Support Vector Machines (SVM), Decision Trees, Random Forests, K-means.
- **Dimensionality Reduction**: Genetic Algorithms, Principal Component Analysis (PCA), wrapper feature selection methods.

## Technologies
- **Hypervisors** (Xen, KVM), **VPC networks**, standard **OS log daemons**.

## Dataset
- NSL-KDD, KDD99, and ISCX datasets.

## Experimental Results
- Synthesized data shows that using advanced feature selection techniques (e.g. genetic algorithms or information gain) reduces the feature dimensions of network packets, leading to up to a **40% reduction in processing latency** while maintaining classification accuracy above 94%.

## Strengths
- Detailed analysis of multi-level log collection (Guest OS, Hypervisor, and Network layers).
- Explicit focus on feature reduction to solve computational latency in active networks.

## Author Reported Limitations
- Traditional IDPSs fail to detect zero-day or novel attacks without generating massive volumes of false alarms.
- The "black-box" nature of complex machine learning models prevents administrators from validating classification rules.
- High computational overhead under heavy dynamic network load, leading to packet drops.

## Future Work
- Designing explainable AI (XAI) threat classifiers.
- Creating low-latency cloud-to-edge monitoring pipelines.
- Formulating dynamic, collaborative threat databases.

## Important Concepts
- **Threat Actor Profiling**: Characterizing the behavior of malicious actors based on temporal packet footprint.
- **Feature Selection Latency**: The computational bottleneck introduced during packet feature extraction and vector construction.

## Our Observations
- Confirms that high-dimensional logs significantly increase classification latency, which is a major constraint in cloud performance. local feature reduction is essential for runtime monitoring.

## Relevance to Our Research
- High. Directly aligns with our research question regarding maintaining acceptable performance while executing AI-based detection.

## Possible Adoption
- Incorporating a feature selection/dimensionality reduction pipeline inside our telemetry monitoring module to minimize latency.
