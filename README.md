ECG-6-Derivations-System
This repository contains a complete bioinstrumentation solution for capturing, filtering, and visualizing Electrocardiogram (ECG) signals. The project integrates custom hardware acquisition with a high-performance software interface. It calculates the 6 frontal leads (I, II, III, aVR, aVL, and aVF) in real-time based on Einthoven’s Law.



Developed and tested at UPIBI - Instituto Politécnico Nacional, this system has been validated in real-world scenarios, successfully capturing and processing physiological signals with high accuracy.


🚀 Key Technical Features
Hardware Interface: Optimized ESP32 firmware for high-speed analog-to-digital conversion (ADC) at a sampling rate of 333.33 Hz.

Digital Signal Processing (DSP): Implementation of a 4th Order Butterworth Bandpass Filter (0.5 Hz - 40 Hz) using Second-Order Sections (SOS) for numerical stability and baseline wander removal.

Real-Time GUI: A custom-built Python interface using Tkinter and Matplotlib for live signal plotting and diagnostic visualization.

Advanced Lead Computation: Mathematical derivation of augmented limb leads (aVR, aVL, aVF) and Lead III, ensuring physiological accuracy.

📂 Repository Structure
/firmware: Source code for the ESP32 microcontroller.

/software: Python scripts for the Graphical User Interface and DSP algorithms.


/docs: Technical documentation and theoretical background on bioinstrumentation.

/tests: Scripts for signal validation and comparison using Einthoven’s Law.

🛠️ Installation & Usage
Requirements: Python 3.8+, an ESP32, and an analog instrumentation circuit (e.g., AD8232).

Install Dependencies:

Bash

pip install numpy scipy matplotlib pyserial Pillow
Upload Firmware: Flash the code provided in the /firmware folder to your ESP32.

Run Interface:

Bash

python InterfazECG.py
⚖️ License & Disclaimer
License: This project is licensed under the MIT License.

Disclaimer: This project is for educational and research purposes only. It is not a medical device and should not be used for clinical diagnosis or treatment.

About the Author

José Luis Valencia Rivera 

Biomedical Engineer | Software Developer | Digital Systems Specialist 

Specialized in hardware-software integration for the clinical sector and medical signal acquisition.
