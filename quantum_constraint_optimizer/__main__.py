from z3 import Optimize
from quantum_constraint_optimizer.constraint_generators.objectives import *
from quantum_constraint_optimizer.translators.qiskit_translator import model_to_QuantumCircuit, QuantumCircuit_to_Circuit, reliability_loader
from quantum_constraint_optimizer.datastructures import Qubit
from quantum_constraint_optimizer.datastructures.circuit import Circuit
from quantum_constraint_optimizer.testing.testing import correctness, improved_reliability
from qiskit import QuantumCircuit


# Collect reliabilities from an IBM Quantum Experience daily calibration
fname = "ibmq_16_melbourne.csv"
melbourne_rels = reliability_loader(fname)
# Manually encode qubit positions in grid lattice
positions = {0:(0,0), 1:(0,1), 2:(0,2), 3:(0,3), 4:(0,4), 5:(0,5), 6:(0,6), 7:(1,7), 8:(1,6), 9:(1,5), 10:(1,4), 11:(1,3), 12:(1,2), 13:(1,1), 14:(1,0)}
# Initialize Circuit
precirc = QuantumCircuit(5,5)
# Add gates to the circuit
precirc.cx(0,4)
precirc.cx(1,4)
precirc.cx(2,4)
precirc.measure(0,0)
precirc.measure(1,1)
precirc.measure(2,2)
precirc.measure(4,4)

def test(qcirc):
    #print(qcirc)
    print("Translate to Z3")
    circ = QuantumCircuit_to_Circuit(qcirc, melbourne_rels, positions)
    # Collect Constraints
    print("Create Constraint Generator")
    cons = circ.constraints()
    # New Optimizer
    s = Optimize()
    # Add constraints
    print("Add All constraints")
    for con in cons:
        s.add(con)
        #print(con)
    # Add reliability objective
    print("Add Objective")
    s.maximize(reliability_objective(circ))
    # Check and print
    print("Checking")
    sat = str(s.check())
    print(sat)
    if sat == "unsat":  
        raise Exception("unsat")

    print("Extracting Model")
    m = s.model()

    # Confirm that an improvement in reliability was made
    print("Reliability Checking")
    improved_reliability(m,s,melbourne_rels, qcirc)

    # Translate to qiskit QuantumCircuit
    print("Translate to Qiskit")
    rcirc = model_to_QuantumCircuit(m, circ)
    #print(rcirc)
    #improved_reliability(m,s,melbourne_rels, rcirc)

#test(precirc)
import os
qasmdir = "quantum_constraint_optimizer/testing/test_qasm/"
#test(QuantumCircuit.from_qasm_file(qasmdir+"BV4_unoptimized.qasm"))
for file in os.listdir(qasmdir):
    if not file.endswith(".qasm"): continue
    qcirc = QuantumCircuit.from_qasm_file(qasmdir+file)
    try:
        test(qcirc)
    except: 
        print(file)
        raise Exception