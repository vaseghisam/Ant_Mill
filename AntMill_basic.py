import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

rng = np.random.default_rng(7)

# ------------------------------------------------------------
# Simulation parameters
# ------------------------------------------------------------
T = 320
dt = 0.08
n_ants = 160
r0 = 1.55

# Landau-Stuart parameters for emergent ring mode Z
mu0 = -0.22
mu1 = 0.30
omega0 = 1.35
g1 = 1.0
g2 = 0.25
sigma_Z = 0.08

# Reduced local ring dynamics parameters
a_max = 2.8
sigma_r_loose = 0.12
sigma_r_tight = 0.025
sigma_phi = 0.10
v_explore = 0.55

# ------------------------------------------------------------
# Initial ant states
# ------------------------------------------------------------
theta = rng.uniform(0, 2 * np.pi, n_ants)
radius = rng.uniform(0.2, 2.6, n_ants)

# Complex order parameter Z = A exp(i psi)
Z = 0.03 * np.exp(1j * rng.uniform(0, 2 * np.pi))

# Histories
Z_abs_hist = np.zeros(T)
phase_hist = np.zeros(T)
strength_hist = np.zeros(T)
mu_hist = np.zeros(T)

hist_len = 8
xh = np.full((hist_len, n_ants), np.nan)
yh = np.full((hist_len, n_ants), np.nan)

# ------------------------------------------------------------
# Figure layout
# ------------------------------------------------------------
fig = plt.figure(figsize=(9.6, 7.2), dpi=100)

# Main animation panel
ax = fig.add_axes([0.06, 0.34, 0.48, 0.56])

# Right-side panels
ax2 = fig.add_axes([0.62, 0.74, 0.32, 0.11])    # |Z|
ax2.set_xlabel("")
ax_mu = fig.add_axes([0.62, 0.50, 0.32, 0.11])  # mu(t)
ax3 = fig.add_axes([0.62, 0.20, 0.32, 0.12])    # equations

# Bottom text panels
ax_txt_left = fig.add_axes([0.06, 0.08, 0.48, 0.18])
ax_txt_right = fig.add_axes([0.62, 0.08, 0.32, 0.15])

for axt in (ax_txt_left, ax_txt_right):
    axt.set_axis_off()
    axt.set_xlim(0, 1)
    axt.set_ylim(0, 1)

# ------------------------------------------------------------
# Main plot styling
# ------------------------------------------------------------
ax.set_title("Ant mill: emergence of a ring from cooperative mode selection")
ax.set_xlim(-3.0, 3.0)
ax.set_ylim(-3.0, 3.0)
ax.set_aspect("equal", adjustable="box")
ax.set_xticks([])
ax.set_yticks([])

phi_grid = np.linspace(0, 2 * np.pi, 500)
ring_x = r0 * np.cos(phi_grid)
ring_y = r0 * np.sin(phi_grid)

ring_line, = ax.plot([], [], lw=2)
ants = ax.scatter([], [], s=12)
tails, = ax.plot([], [], lw=1)

# ------------------------------------------------------------
# |Z| panel
# ------------------------------------------------------------
ax2.set_title("Order-parameter amplitude")
ax2.set_xlim(0, T - 1)
ax2.set_ylim(0, 1.05)
ax2.set_xlabel("frame")
ax2.set_ylabel(r"$|Z|$")
Z_line, = ax2.plot([], [], lw=2)
Z_marker, = ax2.plot([], [], marker="o")

# ------------------------------------------------------------
# mu(t) threshold panel
# ------------------------------------------------------------
ax_mu.set_title("Control parameter and threshold")
ax_mu.set_xlim(0, T - 1)
ax_mu.set_ylim(mu0 - 0.05, mu1 + 0.05)
ax_mu.set_xlabel("frame")
ax_mu.set_ylabel(r"$\mu$")
mu_line, = ax_mu.plot([], [], lw=2)
mu_marker, = ax_mu.plot([], [], marker="o")
mu_zero = ax_mu.axhline(0.0, lw=1, linestyle="--")

# ------------------------------------------------------------
# Equation panel
# ------------------------------------------------------------
ax3.set_title("Model equations used in the simulation")
ax3.axis("off")
eq_text = ax3.text(
    0.0, 0.98,
    (
        r"$dZ=\left[(\mu+i\omega_0)Z-(g_1+i g_2)|Z|^2Z\right]dt+\sigma_Z\,dW_Z$" "\n"
        r"$dr=-a(|Z|)(r-r_0)\,dt+\sigma_r(|Z|)\,dW_r$" "\n"
        r"$d\theta=\left[\omega(|Z|)+b(|Z|)(r-r_0)\right]dt+\sigma_\theta\,dW_\theta$"
    ),
    va="top",
    fontsize=9.5
)

# ------------------------------------------------------------
# Bottom text panels
# ------------------------------------------------------------
left_txt = ax_txt_left.text(
    0.0, 0.98, "",
    ha="left", va="top",
    fontsize=10,
    linespacing=1.35,
    wrap=True
)

right_txt = ax_txt_right.text(
    0.0, 0.98, "",
    ha="left", va="top",
    fontsize=10,
    linespacing=1.35,
    wrap=True
)

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
def mu_schedule(frame):
    """Control parameter slowly crosses onset."""
    s = frame / (T - 1)
    return mu0 + (mu1 - mu0) * (0.5 * (1 + np.tanh(6 * (s - 0.35))))

def emergence_strength(Z):
    """Map |Z| to [0, 1] as a visible ring-strength proxy."""
    A = np.abs(Z)
    scale = np.sqrt(max(g1, 1e-12) * max(mu1, 1e-12) + 1e-12)
    return A / scale

# ------------------------------------------------------------
# Animation functions
# ------------------------------------------------------------
def init():
    ring_line.set_data([], [])
    ants.set_offsets(np.empty((0, 2)))
    tails.set_data([], [])
    Z_line.set_data([], [])
    Z_marker.set_data([], [])
    mu_line.set_data([], [])
    mu_marker.set_data([], [])
    left_txt.set_text("")
    right_txt.set_text("")
    return (
        ring_line, ants, tails,
        Z_line, Z_marker,
        mu_line, mu_marker, mu_zero,
        eq_text, left_txt, right_txt
    )

def update(frame):
    global theta, radius, xh, yh, Z

    # --------------------------------------------------------
    # 1) Landau-Stuart SDE for emergent cooperative ring mode
    # --------------------------------------------------------
    mu = mu_schedule(frame)

    dWZ_re = rng.normal(0.0, np.sqrt(dt))
    dWZ_im = rng.normal(0.0, np.sqrt(dt))
    dWZ = dWZ_re + 1j * dWZ_im

    drift_Z = ((mu + 1j * omega0) * Z - (g1 + 1j * g2) * (np.abs(Z) ** 2) * Z)
    Z = Z + drift_Z * dt + sigma_Z * dWZ

    A = np.abs(Z)
    psi = np.angle(Z)
    strength = np.clip(emergence_strength(Z), 0.0, 1.0)

    # --------------------------------------------------------
    # 2) Ants slaved to the emergent mode
    # --------------------------------------------------------
    a_eff = a_max * strength
    sigma_r = sigma_r_loose * (1 - strength) + sigma_r_tight * strength
    omega_eff = (1 - strength) * v_explore + strength * (omega0 - g2 * A * A)

    dWr = rng.normal(0.0, np.sqrt(dt), n_ants)
    dWth = rng.normal(0.0, np.sqrt(dt), n_ants)

    radius = radius + (-a_eff * (radius - r0)) * dt + sigma_r * dWr
    b_eff = 0.8 * strength
    theta = theta + (omega_eff + b_eff * (radius - r0)) * dt + sigma_phi * dWth

    radius = np.clip(radius, 0.05, 3.0)

    # --------------------------------------------------------
    # 3) Positions and traces
    # --------------------------------------------------------
    x = radius * np.cos(theta)
    y = radius * np.sin(theta)

    xh[:] = np.roll(xh, -1, axis=0)
    yh[:] = np.roll(yh, -1, axis=0)
    xh[-1] = x
    yh[-1] = y

    m = max(2, int((0.05 + 0.95 * strength) * len(ring_x)))
    ring_line.set_data(ring_x[:m], ring_y[:m])
    ants.set_offsets(np.c_[x, y])

    tx, ty = [], []
    for i in range(n_ants):
        tx.extend(xh[:, i].tolist() + [np.nan])
        ty.extend(yh[:, i].tolist() + [np.nan])
    tails.set_data(tx, ty)

    # --------------------------------------------------------
    # 4) Diagnostics and text
    # --------------------------------------------------------
    Z_abs_hist[frame] = min(A, 1.05)
    phase_hist[frame] = psi
    strength_hist[frame] = strength
    mu_hist[frame] = mu

    if mu < 0 and strength < 0.20:
        stage = "Disordered exploratory phase"
    elif mu < 0:
        stage = "Fluctuating precritical organization"
    elif strength < 0.50:
        stage = "Post-threshold ring mode grows"
    elif strength < 0.80:
        stage = "Ants become slaved to the selected ring"
    else:
        stage = "Stable collective circular mill"

    left_txt.set_text(
        "The ring appears only as the cooperative mode amplitude grows.\n"
        f"Stage: {stage}.\n"
        f"Current values: |Z| = {A:.3f},   arg(Z) = {psi:.2f},   μ = {mu:.3f}."
    )

    Z_line.set_data(np.arange(frame + 1), Z_abs_hist[:frame + 1])
    Z_marker.set_data([frame], [Z_abs_hist[frame]])

    mu_line.set_data(np.arange(frame + 1), mu_hist[:frame + 1])
    mu_marker.set_data([frame], [mu_hist[frame]])

    right_txt.set_text(
        "The dashed line marks the critical threshold μ = 0.\n"
        "For μ < 0 the ring mode is damped;\n"
        "for μ > 0 it can grow and saturate.\n"
        "As |Z| increases, radial confinement toward $r_0$ strengthens."
    )

    return (
        ring_line, ants, tails,
        Z_line, Z_marker,
        mu_line, mu_marker, mu_zero,
        eq_text, left_txt, right_txt
    )

anim = FuncAnimation(
    fig,
    update,
    frames=T,
    init_func=init,
    interval=50,
    blit=True
)

anim.save("ant_mill_emergent_ring_sde_threshold.gif", writer=PillowWriter(fps=20))
