import streamlit as st
import qiskit
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, execute, Aer
from qiskit.circuit.library import MCMT
import numpy as np
import matplotlib.pyplot as plt
import tempfile
import os

st.set_page_config(layout="wide")
# Function to simulate quantum circuit and plot results
def simulate_quantum_circuit(target_node_decimal_representation, number_of_bits_position_register, number_shots):   
    #Define Circuit
    position_register = number_of_bits_position_register
    coin_register = number_of_bits_position_register
    creg = qiskit.ClassicalRegister(position_register, 'c')
    qreg = qiskit.QuantumRegister(position_register+coin_register, 'q')
    circuit1 = qiskit.QuantumCircuit(qreg, creg)
    
    #Initialize position register
    for i in range(position_register):
        circuit1.h(i)

    #Negate controls of gate C^n(H^{n})
    target_binary_representation = bin(target_node_decimal_representation)[2:].zfill(number_of_bits_position_register)
    for i in reversed(range(number_of_bits_position_register)):
        bit = target_binary_representation[i]
        if bit == '0':
            circuit1.x(number_of_bits_position_register-(i+1))

    #Define gate C^n(H^{n}) in a new circuit to visualize it explicity
    circuit2 = MCMT('h', num_ctrl_qubits=position_register, num_target_qubits=coin_register)

    #Negate controls of gate C^n(H^{n})
    for i in reversed(range(number_of_bits_position_register)):
        if target_binary_representation[i] == '0':
            circuit2.x(number_of_bits_position_register-(i+1))

    #Merge circuits
    circuit = circuit1.compose(circuit2, qubits=list(range(position_register+coin_register)))

    #Add shift operator
    for i in range(position_register):
        circuit.cnot(position_register+i, i)
    
    #Add measurement operators to position register
    for i in range(position_register):
        circuit.measure(i, i)

    #Simulate quantum circuit
    sim = qiskit.Aer.get_backend('qasm_simulator')
    
    #Set number of shots
    job = execute(circuit, sim, shots=number_shots)

    #Change counts to probabilities
    counts = job.result().get_counts()
    factor = 1.0 / sum(counts.values())
    probabilities = {k: v*factor for k, v in counts.items()}

    # Save circuit diagram as image
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
        circuit.draw(output="mpl", filename=tmp_file.name)
        circuit_image_path = tmp_file.name

    return circuit_image_path, probabilities

# Streamlit UI
st.title("Search Complement Algorithm Simulation")

st.markdown('This algorithm reduces the probability of measuring the state associated to the target node')

# Input bars for setting variables
target_node_decimal_representation = st.number_input("Target Node", value=0, min_value=0, step=1)
number_of_bits_position_register = st.number_input("Number of Qubits of the Position Register", value=4, min_value=1, step=1)
number_of_shots = st.number_input("Number of Shots", value=50000, min_value=1, step=1000)

# Button to run simulation
if st.button("Run Simulation"):
    circuit_image_path, histogram = simulate_quantum_circuit(target_node_decimal_representation, number_of_bits_position_register, number_of_shots)
    st.write("Circuit Diagram:")
    st.image(circuit_image_path)
    st.write("Histogram:")
    fig = qiskit.visualization.plot_histogram(histogram)
    fig.set_size_inches(8, 4)
    st.pyplot(fig)