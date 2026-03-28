# Ant Mill Simulations

This repository contains two related simulation programs:

- `AntMill_basic.py` — a reduced synergetic model of ring emergence
- `AntMill_Advanced.py` — an extended model with continuous inflow, overload, inward spiral collapse, and central pile-up

---

## `AntMill_basic.py`

# Ant Mill (Basic): Emergent Ring from Cooperative Mode Selection

This program simulates an ant mill as the emergence of a **collective ring mode** rather than as a circle imposed by hand. The model is intentionally reduced and synergetic in spirit: a single complex order parameter

\[
Z = A e^{i\psi}
\]

governs the onset and growth of a cooperative circular mode, while individual ants are progressively **slaved** to that mode as its amplitude increases.

The script produces an animated GIF:

- `ant_mill_emergent_ring_sde_threshold.gif`

---

## Conceptual Idea

The simulation separates the dynamics into two levels:

1. **Collective mode selection**  
   A Landau–Stuart stochastic amplitude equation controls the growth of the ring mode:

   \[
   dZ=\left[(\mu+i\omega_0)Z-(g_1+i g_2)|Z|^2Z\right]dt+\sigma_Z\,dW_Z
   \]

   Here, the control parameter \(\mu(t)\) slowly crosses threshold. For \(\mu<0\), the ring mode is damped; for \(\mu>0\), the mode can grow and saturate.

2. **Individual ant dynamics near the selected ring**  
   Once the cooperative mode becomes strong, ants are increasingly pulled toward a preferred radius \(r_0\) and circulate around it:

   \[
   dr=-a(|Z|)(r-r_0)\,dt+\sigma_r(|Z|)\,dW_r
   \]

   \[
   d\theta=\left[\omega(|Z|)+b(|Z|)(r-r_0)\right]dt+\sigma_\theta\,dW_\theta
   \]

So the ring is not prescribed as a hard geometric constraint. It appears as the visible manifestation of a growing collective mode.

---

## What the Animation Shows

The figure has several coordinated panels:

- **Main panel**  
  Ants move in the plane, first in a loose exploratory state and later in a coherent rotating ring.

- **Order-parameter amplitude panel**  
  Tracks \(|Z|\), the strength of the collective ring mode.

- **Threshold panel**  
  Shows the control parameter \(\mu(t)\) crossing the instability threshold \(\mu=0\).

- **Equation panel**  
  Displays the reduced stochastic equations used in the simulation.

- **Text panels**  
  Explain the current dynamical regime:
  - disordered exploratory phase,
  - precritical organization,
  - post-threshold growth,
  - slaving to the ring,
  - stable circular mill.

---

## Why This Model Is Useful

This is a **minimal reduced model** designed to illustrate a specific idea:

- the ant mill as a **collective attractor**,
- the transition from disorder to circular organization,
- and the way microscopic motion can become subordinated to a low-dimensional macroscopic mode.

It is therefore best understood as a **synergetic normal-form simulation**, not as a full first-principles pheromone PDE solver.

---

## Parameters

Key parameters include:

- `T`, `dt` — total simulation length and time step
- `n_ants` — number of ants
- `r0` — preferred ring radius
- `mu0`, `mu1` — control parameter range
- `omega0` — intrinsic angular frequency of the collective mode
- `g1`, `g2` — nonlinear saturation terms in the Landau–Stuart equation
- `sigma_Z` — noise level in the order parameter
- `a_max` — maximum radial confinement strength
- `sigma_r_loose`, `sigma_r_tight`, `sigma_phi` — stochasticity in ant motion

---

## Requirements

Install the required Python packages:

pip install numpy matplotlib


⸻

Usage

Run the script directly:

python AntMill_basic.py

The program will save the GIF in the working directory.

⸻

Interpretation

This code is appropriate if you want a clean visual demonstration of:
	•	mode selection,
	•	threshold crossing,
	•	emergence of circular order,
	•	and the reduction of many-body motion to a collective pattern.

If you want a biologically richer model with continuous inflow, overload, inward spiral collapse, and central pile-up, see AntMill_Advanced.py.


## `AntMill_Advanced.py`

# Ant Mill (Advanced): Continuous Inflow, Overload, Inner Spiral, and Central Pile-Up

This program extends the basic ant-mill model by adding a second mechanism on top of cooperative ring selection:

1. **Biological ring selection** through a collective order parameter \(Z\)
2. **Mechanical overload dynamics** that push the mill inward, generate a spiral collapse, and create a central pile-up

The script produces an animated GIF:

- `ant_mill_continuous_inflow_inner_spiral.gif`

---

## Conceptual Idea

The advanced model treats the ant mill as the superposition of two processes.

### 1. Cooperative biological ring selection

As in the basic model, a Landau–Stuart stochastic amplitude equation governs the emergence of a collective ring mode:

\[
dZ=[(\mu+i\omega_0)Z-(g_1+i g_2)|Z|^2Z]dt+\sigma_Z\,dW_Z
\]

When the control parameter \(\mu\) crosses threshold, the ring mode grows and begins to organize the ants around a biologically selected radius \(r_0\).

### 2. Mechanical overload and collapse

Once too many ants accumulate in the ring, a second field becomes active:

\[
\Pi = \max\{0, N_{\rm ring}-N_c\}/N_c
\]

where \(N_{\rm ring}\) is the number of ants in the ring region and \(N_c\) is a capacity threshold.

This overload field modifies the radial and angular dynamics by introducing:

- inward mechanical pressure,
- spiral shear,
- centerward drift,
- and eventual pile formation near the center.

So the model goes beyond a stable circular mill and explores what happens when a continuously fed ring becomes overcrowded.

---

## What the Animation Shows

This script renders a **3D visualization** of the system with several coupled diagnostics.

### Main 3D Panel

- **Blue circle**: the biologically selected ring
- **Gray inner circle**: the pressure annulus where overload becomes active
- **Gold ants and trails**: live ants entering, circulating, and spiraling inward
- **Brown bars**: a discrete central pile formed by captured ants

### Diagnostic Panels

- **Order-parameter amplitude \(|Z|\)**  
  Measures the strength of the cooperative ring mode

- **Control parameter \(\mu(t)\)**  
  Shows the instability threshold for the biological ring

- **Overload field \(\Pi(t)\)**  
  Tracks how far the ring occupancy exceeds its capacity

- **Equation panel**  
  Summarizes the coupled reduced model:
  - cooperative mode growth,
  - radial force balance,
  - angular spiral dynamics,
  - overload activation

### Text Panels

These explain the current regime in terms of:

- ring growth,
- ongoing outer inflow,
- overload,
- inward spiral,
- central pile height,
- and the current population inside the ring.

---

## Dynamics Included in the Model

The advanced simulation includes:

- **continuous recruitment from outside**  
  Ants begin in an outer exploratory band and gradually feed into the system

- **ring attraction from outside**  
  As the cooperative mode strengthens, fed ants are drawn toward the ring

- **weak biological attraction from inside**  
  Inside the ring, biological organization alone is not enough to stabilize the system under overload

- **mechanical inward field**  
  Overcrowding creates an inward radial pressure centered inside the ring

- **spiral shear**  
  Inward motion remains rotational, so collapse occurs as a visible spiral rather than a straight radial fall

- **pairwise soft repulsion**  
  Ants repel one another weakly at short distances

- **central capture and deposition**  
  Ants spending long enough near the center are converted into a pile, visualized as growing bars

---

## Why This Model Is Useful

This version is designed for a richer interpretation of the ant mill:

- not only as a **stable emergent ring**,
- but as a **continuously fed, overloaded collective structure** that can deform into an inward spiral and central accumulation.

It is therefore useful if you want to visualize the transition from:

- self-organized ring formation  
to  
- crowding, internal mechanical stress, and collapse.

The model remains reduced and conceptual, but it adds a second field — overload \(\Pi\) — that lets the simulation express failure modes beyond simple circular persistence.

---

## Parameters

Important groups of parameters include:

### Cooperative Ring-Selection

- `r0`
- `mu0`, `mu1`
- `omega0`
- `g1`, `g2`
- `sigma_Z`

### Outer Inflow / Exploration

- `feed_radius_min`, `feed_radius_max`
- `v_in_base`, `v_in_active`
- `omega_outside`

### Biological Ring Attraction

- `a_out_max`
- `a_in_base`
- `sigma_r_loose`, `sigma_r_tight`, `sigma_phi`

### Mechanical Overload

- `ring_width`
- `ring_capacity`
- `pressure_gain`
- `pressure_alpha`
- `pressure_width`
- `center_pull_gain`
- `shear_gain`
- `repulsion_gain`

### Central Pile

- `center_capture_radius`
- `center_dwell_threshold`
- `pile_radius`
- `pile_nx`, `pile_ny`
- `pile_cell_height`
- `pile_height_cap`
- `pile_deposit_prob`

These can be tuned to emphasize either:

- long-lived ring organization, or
- rapid overload and collapse.

---

## Requirements

Install the required Python packages:

pip install numpy matplotlib

This script also uses Matplotlib’s 3D toolkit (mpl_toolkits.mplot3d), which ships with standard Matplotlib.

⸻

Usage

Run the script directly:

python AntMill_Advanced.py

The program will save the GIF in the working directory.

⸻

Interpretation

This advanced model is best read as a two-field reduced dynamics:
	•	a cooperative biological field selecting the ring,
	•	and a mechanical overload field driving collapse.

It is not a full first-principles solver of the coupled pheromone PDE and agent system, but a reduced-order model designed to visualize how:
	•	a ring can emerge from collective mode selection,
	•	persist under continuous inflow,
	•	become overcrowded,
	•	spiral inward,
	•	and build a central pile.

