---
type: entity
tags: [math, nonlinear-dynamics, chaos, physics]
created: 2026-05-23
sources: [pdf-misc-books]
---

# Nonlinear Dynamics & Chaos

## Definition

Nonlinear dynamics studies systems where the output is not proportional to the input — where small changes can cause disproportionately large effects. Chaos theory describes deterministic systems that exhibit unpredictable, aperiodic behavior due to **sensitive dependence on initial conditions** (the butterfly effect).

## Key Concepts

### One-Dimensional Flows
- **Fixed Points**: Stable (attractor) vs unstable (repeller)
- **Bifurcations**: Saddle-node, transcritical, pitchfork, period-doubling
- **Logistic Map**: xₙ₊₁ = r·xₙ·(1-xₙ) — period-doubling route to chaos

### Two-Dimensional Flows
- **Limit Cycles**: Closed periodic orbits
- **Poincaré-Bendixson Theorem**: Bounded trajectory in 2D must approach fixed point or limit cycle
- **Relaxation Oscillations**: Fast-slow systems (van der Pol oscillator)
- **Bifurcations in 2D**: Hopf bifurcation (birth of limit cycles)

### Chaos
- **Lorenz Equations**: The iconic chaotic system — σ·(y-x), x·(ρ-z)-y, xy-βz
- **Strange Attractors**: Fractal structure of chaotic attractors
- **Lyapunov Exponent**: Quantifies sensitivity to initial conditions
- **Fractal Dimension**: Quantifies strange attractor geometry

### Applications
- **Physics**: Pendulum, driven oscillator, fluid convection
- **Biology**: Predator-prey cycles, neural dynamics, cardiac rhythms
- **Chemistry**: Belousov-Zhabotinsky reaction
- **Engineering**: Josephson junctions, laser dynamics

## Related Pages

- [[entities/arm/computer-architecture]] — Computer simulation of dynamical systems
- [[datastructure-index]] — Numerical algorithms for ODE integration
- [[sys-prog-index]] — System programming for scientific computing

## Source Details

- [[sources/pdf-misc-books]] — Nonlinear Dynamics and Chaos (Strogatz, 2018)
