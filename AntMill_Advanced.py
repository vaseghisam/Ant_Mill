import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

# ============================================================
# Ant mill with two superposed mechanisms:
# 1) biological ring selection by the cooperative order parameter Z
# 2) mechanical inward spiral and central pileup under overload
#    with continuous feeding from outside
# ============================================================

rng = np.random.default_rng(7)

# ------------------------------------------------------------
# Global parameters
# ------------------------------------------------------------
T = 460
dt = 0.05
n_ants = 340

# --- Cooperative ring-selection parameters
r0 = 1.55
mu0 = -0.22
mu1 = 0.30
omega0 = 1.08
g1 = 1.0
g2 = 0.16
sigma_Z = 0.030

# --- Outer inflow / exploration
feed_radius_min = 2.15
feed_radius_max = 2.85
v_in_base = 0.020
v_in_active = 0.080
omega_outside = 0.22

# --- Biological ring attraction
a_out_max = 1.35          # attraction from outside toward ring
a_in_base = 0.85          # weak inner attraction when not overloaded
sigma_r_loose = 0.055
sigma_r_tight = 0.010
sigma_phi = 0.040

# --- Ring overload / mechanics
ring_width = 0.18
ring_capacity = 56
pressure_gain = 0.22      # main inward pressure strength
pressure_alpha = 0.82     # pressure annulus center = alpha*r0
pressure_width = 0.17
center_pull_gain = 0.16   # deeper inward pull once already inside
shear_gain = 1.00         # keeps inward motion spiral-like
repulsion_gain = 0.008
ant_radius = 0.060

# --- Center capture / pile
center_capture_radius = 0.32
center_dwell_threshold = 16
pile_radius = 0.75
pile_nx = 13
pile_ny = 13
pile_cell_height = 0.050
pile_height_cap = 2.7
pile_deposit_prob = 0.18

# --- Visualization
max_z_visual = 3.0
trail_len = 10

# ------------------------------------------------------------
# State variables
# ------------------------------------------------------------
theta = rng.uniform(0, 2 * np.pi, n_ants)
radius = rng.uniform(feed_radius_min, feed_radius_max, n_ants)

# All ants are alive; "fed" means they have entered the ring-seeking flow
alive = np.ones(n_ants, dtype=bool)
fed = np.zeros(n_ants, dtype=bool)
center_dwell = np.zeros(n_ants, dtype=int)

# complex order parameter
Z = 0.02 * np.exp(1j * rng.uniform(0, 2 * np.pi))
mass = rng.uniform(0.9, 1.1, n_ants)

# trails
xh = np.full((trail_len, n_ants), np.nan)
yh = np.full((trail_len, n_ants), np.nan)
zh = np.full((trail_len, n_ants), np.nan)

# discrete pile grid
px = np.linspace(-pile_radius, pile_radius, pile_nx + 1)
py = np.linspace(-pile_radius, pile_radius, pile_ny + 1)
pcx = 0.5 * (px[:-1] + px[1:])
pcy = 0.5 * (py[:-1] + py[1:])
PCX, PCY = np.meshgrid(pcx, pcy, indexing="xy")
pile_counts = np.zeros((pile_ny, pile_nx), dtype=float)
cell_dx = px[1] - px[0]
cell_dy = py[1] - py[0]

# histories
Z_abs_hist = np.zeros(T)
mu_hist = np.zeros(T)
Pi_hist = np.zeros(T)
occ_hist = np.zeros(T)
pile_peak_hist = np.zeros(T)

# ------------------------------------------------------------
# Figure layout
# ------------------------------------------------------------
fig = plt.figure(figsize=(11.0, 7.8), dpi=100)

ax = fig.add_axes([0.05, 0.31, 0.54, 0.60], projection="3d")
ax2 = fig.add_axes([0.64, 0.77, 0.30, 0.09])    # |Z|
ax_mu = fig.add_axes([0.64, 0.60, 0.30, 0.09])  # mu
ax_p = fig.add_axes([0.64, 0.44, 0.30, 0.09])   # Pi
ax3 = fig.add_axes([0.64, 0.13, 0.30, 0.20])    # equations
ax_txt_left = fig.add_axes([0.05, 0.05, 0.54, 0.18])
ax_txt_right = fig.add_axes([0.64, 0.04, 0.30, 0.10])

for axt in (ax_txt_left, ax_txt_right):
    axt.set_axis_off()
    axt.set_xlim(0, 1)
    axt.set_ylim(0, 1)

# ------------------------------------------------------------
# Main 3D styling
# ------------------------------------------------------------
ax.set_title("Ant mill with continuous inflow and overload-driven inner spiral")
ax.set_xlim(-3, 3)
ax.set_ylim(-3, 3)
ax.set_zlim(0, max_z_visual)
ax.set_box_aspect((1, 1, 0.58))
ax.set_xticks([])
ax.set_yticks([])
ax.set_zticks([])
ax.view_init(elev=30, azim=-58)

ax.xaxis.set_pane_color((0.95, 0.95, 0.95, 1.0))
ax.yaxis.set_pane_color((0.95, 0.95, 0.95, 1.0))
ax.zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))

ring_color = "#1f4e79"
pressure_color = "#555555"
live_ant_color = "#d4a72c"
trail_color = "#8c6d1f"
pile_color = "#6b4f2a"

phi_grid = np.linspace(0, 2 * np.pi, 400)

ring_x = r0 * np.cos(phi_grid)
ring_y = r0 * np.sin(phi_grid)
ring_z = np.zeros_like(ring_x)

r_press = pressure_alpha * r0
press_x = r_press * np.cos(phi_grid)
press_y = r_press * np.sin(phi_grid)
press_z = np.zeros_like(press_x)

ring_line, = ax.plot(ring_x, ring_y, ring_z, lw=2.2, color=ring_color, alpha=0.10)
pressure_line, = ax.plot(press_x, press_y, press_z, lw=1.8, color=pressure_color, alpha=0.05)

ants3d = None
tails3d = None
pile_bars = []

# ------------------------------------------------------------
# Right panels
# ------------------------------------------------------------
ax2.set_title("Order-parameter amplitude")
ax2.set_xlim(0, T - 1)
ax2.set_ylim(0, 1.05)
ax2.set_xlabel("")
ax2.set_ylabel(r"$|Z|$")
Z_line, = ax2.plot([], [], lw=2, color=ring_color)
Z_marker, = ax2.plot([], [], marker="o", color=ring_color)

ax_mu.set_title("Control parameter and threshold")
ax_mu.set_xlim(0, T - 1)
ax_mu.set_ylim(mu0 - 0.05, mu1 + 0.05)
ax_mu.set_xlabel("")
ax_mu.set_ylabel(r"$\mu$")
mu_line, = ax_mu.plot([], [], lw=2, color="#444444")
mu_marker, = ax_mu.plot([], [], marker="o", color="#444444")
mu_zero = ax_mu.axhline(0.0, lw=1, linestyle="--", color="#888888")

ax_p.set_title("Overload field")
ax_p.set_xlim(0, T - 1)
ax_p.set_ylim(0, 1.05)
ax_p.set_xlabel("frame")
ax_p.set_ylabel(r"$\Pi$")
P_line, = ax_p.plot([], [], lw=2, color=pressure_color)
P_marker, = ax_p.plot([], [], marker="o", color=pressure_color)

ax3.set_title("Two-field model")
ax3.axis("off")
eq_text = ax3.text(
    0.0, 0.98,
    (
        r"$dZ=[(\mu+i\omega_0)Z-(g_1+i g_2)|Z|^2Z]dt+\sigma_Z\,dW_Z$" "\n"
        r"$dr_i=[F_{\rm bio}(r_i,|Z|,\Pi)+F_{\rm mech}(r_i,\Pi)]dt+\sigma_r\,dW_i$" "\n"
        r"$d\theta_i=[\omega_{\rm flow}+\Omega_{\rm spiral}(r_i,\Pi)]dt+\sigma_\theta\,dW_i$" "\n"
        r"$\Pi=\max\{0,N_{\rm ring}-N_c\}/N_c$" "\n"
        r"$F_{\rm mech}(r,\Pi)\sim -\Pi\,e^{-(r-\alpha r_0)^2/(2w^2)}-\Pi\,H(r_0-r)$"
    ),
    va="top",
    fontsize=8.3
)

left_txt = ax_txt_left.text(
    0.0, 0.98, "",
    ha="left", va="top",
    fontsize=10, linespacing=1.35, wrap=True
)

right_txt = ax_txt_right.text(
    0.0, 0.98, "",
    ha="left", va="top",
    fontsize=9.2, linespacing=1.30, wrap=True
)

# ------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------
def mu_schedule(frame):
    s = frame / (T - 1)
    return mu0 + (mu1 - mu0) * (0.5 * (1 + np.tanh(6 * (s - 0.24))))

def emergence_strength(z):
    A = np.abs(z)
    scale = np.sqrt(max(g1, 1e-12) * max(mu1, 1e-12) + 1e-12)
    return A / scale

def pairwise_soft_repulsion(x, y, body_r, gain, active_mask):
    n = len(x)
    fx = np.zeros(n)
    fy = np.zeros(n)
    idx = np.where(active_mask)[0]
    for ii in idx:
        dx = x[ii] - x[idx]
        dy = y[ii] - y[idx]
        dist2 = dx * dx + dy * dy
        dist = np.sqrt(dist2 + 1e-10)
        overlap = 2 * body_r - dist
        mask = (overlap > 0) & (dist > 1e-8)
        if np.any(mask):
            fx[ii] += np.sum(gain * overlap[mask] * dx[mask] / dist[mask])
            fy[ii] += np.sum(gain * overlap[mask] * dy[mask] / dist[mask])
    return fx, fy

def rebuild_pile_bars():
    global pile_bars
    for bar in pile_bars:
        try:
            bar.remove()
        except Exception:
            pass
    pile_bars = []

    heights = np.minimum(pile_counts * pile_cell_height, pile_height_cap)
    mask = heights > 0
    if not np.any(mask):
        return

    xs = PCX[mask] - 0.45 * cell_dx
    ys = PCY[mask] - 0.45 * cell_dy
    zs = np.zeros(np.sum(mask))
    dx = np.full(np.sum(mask), 0.90 * cell_dx)
    dy = np.full(np.sum(mask), 0.90 * cell_dy)
    dz = heights[mask]

    bars = ax.bar3d(
        xs, ys, zs, dx, dy, dz,
        color=pile_color, shade=True, alpha=0.95, zsort="average"
    )
    pile_bars.append(bars)

def respawn_ant(i):
    radius[i] = rng.uniform(feed_radius_min, feed_radius_max)
    theta[i] = rng.uniform(0, 2 * np.pi)
    fed[i] = False
    alive[i] = True
    center_dwell[i] = 0

# ------------------------------------------------------------
# Animation functions
# ------------------------------------------------------------
def init():
    global ants3d, tails3d

    Z_line.set_data([], [])
    Z_marker.set_data([], [])
    mu_line.set_data([], [])
    mu_marker.set_data([], [])
    P_line.set_data([], [])
    P_marker.set_data([], [])

    left_txt.set_text("")
    right_txt.set_text("")

    rebuild_pile_bars()

    if ants3d is not None:
        ants3d.remove()
    ants3d = ax.scatter([], [], [], s=12, color=live_ant_color, depthshade=True)

    if tails3d is not None:
        tails3d.remove()
    tails3d = ax.scatter([], [], [], s=2, color=trail_color, alpha=0.24, depthshade=False)

    return (
        ring_line, pressure_line, ants3d, tails3d,
        Z_line, Z_marker,
        mu_line, mu_marker, mu_zero,
        P_line, P_marker,
        eq_text, left_txt, right_txt,
        *pile_bars
    )

def update(frame):
    global theta, radius, Z, ants3d, tails3d, pile_counts, alive, center_dwell, fed, xh, yh, zh

    # --------------------------------------------------------
    # 1) Cooperative order parameter
    # --------------------------------------------------------
    mu = mu_schedule(frame)
    dWZ = rng.normal(0.0, np.sqrt(dt)) + 1j * rng.normal(0.0, np.sqrt(dt))
    drift_Z = ((mu + 1j * omega0) * Z - (g1 + 1j * g2) * (np.abs(Z) ** 2) * Z)
    Z = Z + drift_Z * dt + sigma_Z * dWZ

    A = np.abs(Z)
    strength = np.clip(emergence_strength(Z), 0.0, 1.0)

    ring_line.set_alpha(0.10 + 0.72 * strength)

    # --------------------------------------------------------
    # 2) Continuous feeding from outside
    # --------------------------------------------------------
    active = alive.copy()
    feed_rate = (1 - strength) * 0.015 + strength * v_in_active

    feed_candidates = active & (~fed)
    if np.any(feed_candidates):
        idx = np.where(feed_candidates)[0]
        chosen = idx[rng.random(idx.size) < feed_rate]
        fed[chosen] = True

    # --------------------------------------------------------
    # 3) Outside flow and biological attraction
    # --------------------------------------------------------
    sigma_r = sigma_r_loose * (1 - strength) + sigma_r_tight * strength
    dWr = rng.normal(0.0, np.sqrt(dt), n_ants)
    dWth = rng.normal(0.0, np.sqrt(dt), n_ants)

    outer = active & (~fed)
    fed_alive = active & fed

    # outside ants: inward drifting feed flow
    v_in = (1 - strength) * v_in_base + strength * v_in_active
    radius[outer] += (-v_in) * dt + 0.04 * dWr[outer]
    theta[outer] += omega_outside * dt + 0.05 * dWth[outer]

    # fed ants outside ring: strong attraction toward ring
    outside_ring = fed_alive & (radius >= r0)
    F_bio_out = -a_out_max * strength * (radius[outside_ring] - r0)
    radius[outside_ring] += F_bio_out * dt + sigma_r * dWr[outside_ring]
    theta[outside_ring] += (omega0 * strength + 0.22) * dt + sigma_phi * dWth[outside_ring]

    # --------------------------------------------------------
    # 4) Compute overload
    # --------------------------------------------------------
    x = radius * np.cos(theta)
    y = radius * np.sin(theta)

    ring_mask = fed_alive & (np.abs(radius - r0) < ring_width)
    N_ring = np.sum(ring_mask)
    Pi = max(0.0, N_ring - ring_capacity) / ring_capacity

    pressure_line.set_alpha(0.05 + 0.85 * min(Pi, 1.0))

    # --------------------------------------------------------
    # 5) Inside-ring competition:
    #    weak biological inner pull versus mechanical inward field
    # --------------------------------------------------------
    inside_ring = fed_alive & (radius < r0)

    # biological attraction from inside is sharply weakened by overload
    inner_bio_scale = (1.0 - min(Pi, 1.0)) ** 2
    F_bio_in = a_in_base * strength * inner_bio_scale * (r0 - radius[inside_ring])

    # mechanical inward field centered just inside the ring
    pressure_annulus = np.exp(-((radius[inside_ring] - pressure_alpha * r0) ** 2) / (2 * pressure_width ** 2))
    F_mech_ann = -pressure_gain * Pi * pressure_annulus

    # additional deeper pull toward center once already well inside
    inner_gate = 1.0 / (1.0 + np.exp(8.0 * (radius[inside_ring] - 0.85 * r0)))
    F_mech_center = -center_pull_gain * Pi * inner_gate

    radius[inside_ring] += (F_bio_in + F_mech_ann + F_mech_center) * dt + sigma_r * dWr[inside_ring]

    # keep inward motion visibly spiral
    Omega_spiral = shear_gain * Pi * inner_gate
    theta[inside_ring] += (omega0 * strength + 0.20 + Omega_spiral) * dt + sigma_phi * dWth[inside_ring]

    # --------------------------------------------------------
    # 6) Soft steric repulsion
    # --------------------------------------------------------
    x = radius * np.cos(theta)
    y = radius * np.sin(theta)

    fx_rep, fy_rep = pairwise_soft_repulsion(x, y, ant_radius, repulsion_gain, active)

    rr = np.sqrt(x * x + y * y) + 1e-10
    erx = x / rr
    ery = y / rr
    etx = -y / rr
    ety = x / rr

    radial_rep = fx_rep * erx + fy_rep * ery
    tangential_rep = fx_rep * etx + fy_rep * ety

    radius[active] += radial_rep[active] * dt
    theta[active] += 0.10 * tangential_rep[active] * dt

    radius[active] = np.clip(radius[active], 0.03, 3.0)

    # --------------------------------------------------------
    # 7) Central capture and discrete pile
    # --------------------------------------------------------
    x = radius * np.cos(theta)
    y = radius * np.sin(theta)

    trapped = active & (radius < center_capture_radius)
    center_dwell[active & ~trapped] = 0
    center_dwell[trapped] += 1

    eligible = np.where(trapped & (center_dwell >= center_dwell_threshold))[0]
    if eligible.size > 0:
        convert_mask = rng.random(eligible.size) < pile_deposit_prob
        to_convert = eligible[convert_mask]

        for i in to_convert:
            if (-pile_radius <= x[i] <= pile_radius) and (-pile_radius <= y[i] <= pile_radius):
                ix = np.searchsorted(px, x[i], side="right") - 1
                iy = np.searchsorted(py, y[i], side="right") - 1
                if 0 <= ix < pile_nx and 0 <= iy < pile_ny:
                    pile_counts[iy, ix] = min(
                        pile_counts[iy, ix] + mass[i],
                        pile_height_cap / pile_cell_height
                    )
                    alive[i] = False
                    center_dwell[i] = 0

    # immediate respawn outside keeps continued source active
    dead_idx = np.where(~alive)[0]
    for i in dead_idx:
        respawn_ant(i)

    rebuild_pile_bars()

    # --------------------------------------------------------
    # 8) Heights above pile and trails
    # --------------------------------------------------------
    z_live = np.zeros(n_ants)
    live_idx = np.where(alive)[0]
    for i in live_idx:
        if (-pile_radius <= x[i] <= pile_radius) and (-pile_radius <= y[i] <= pile_radius):
            ix = np.searchsorted(px, x[i], side="right") - 1
            iy = np.searchsorted(py, y[i], side="right") - 1
            if 0 <= ix < pile_nx and 0 <= iy < pile_ny:
                z_live[i] = min(pile_counts[iy, ix] * pile_cell_height, pile_height_cap)

    xh = np.roll(xh, -1, axis=0)
    yh = np.roll(yh, -1, axis=0)
    zh = np.roll(zh, -1, axis=0)

    xh[-1] = np.where(alive, x, np.nan)
    yh[-1] = np.where(alive, y, np.nan)
    zh[-1] = np.where(alive, z_live + 0.03, np.nan)

    tail_x = xh[:, alive].ravel()
    tail_y = yh[:, alive].ravel()
    tail_z = zh[:, alive].ravel()

    # --------------------------------------------------------
    # 9) Update artists
    # --------------------------------------------------------
    if ants3d is not None:
        ants3d.remove()
    ants3d = ax.scatter(
        x[alive], y[alive], z_live[alive] + 0.03,
        s=12, color=live_ant_color, depthshade=True
    )

    if tails3d is not None:
        tails3d.remove()
    tails3d = ax.scatter(
        tail_x, tail_y, tail_z,
        s=2, color=trail_color, alpha=0.24, depthshade=False
    )

    # --------------------------------------------------------
    # 10) Diagnostics and text
    # --------------------------------------------------------
    Z_abs_hist[frame] = min(A, 1.05)
    mu_hist[frame] = mu
    occ_hist[frame] = N_ring
    Pi_hist[frame] = min(Pi, 1.0)
    pile_peak = np.max(np.minimum(pile_counts * pile_cell_height, pile_height_cap))
    pile_peak_hist[frame] = pile_peak

    mean_r = np.mean(radius[alive]) if np.any(alive) else 0.0

    if mu < 0 and strength < 0.20:
        stage = "Precritical wandering"
    elif mu > 0 and Pi <= 1e-6:
        stage = "Biological ring forms"
    elif Pi > 1e-6 and mean_r > 0.55:
        stage = "Mechanical inward spiral develops"
    else:
        stage = "Central capture and pileup"

    left_txt.set_text(
        "This version adds a continuous outer source of ants. The cooperative dynamics selects\n"
        "the blue ring, but only from outside. Once the ring overload Π becomes positive,\n"
        "the inner biological pull is weakened and the mechanical inward field dominates inside\n"
        "the ring, producing a visible spiral collapse toward the center.\n"
        f"Stage: {stage}.\n"
        f"|Z| = {A:.3f},   μ = {mu:.3f},   N_ring = {N_ring},   Π = {Pi:.3f},   peak pile height = {pile_peak:.2f}."
    )

    right_txt.set_text(
        "Blue circle: biologically selected ring.\n"
        "Gray inner circle: mechanical pressure annulus.\n"
        "Gold trajectories: live ants from the continuing outer inflow.\n"
        "Brown bars: discrete central pile."
    )

    Z_line.set_data(np.arange(frame + 1), Z_abs_hist[:frame + 1])
    Z_marker.set_data([frame], [Z_abs_hist[frame]])
    mu_line.set_data(np.arange(frame + 1), mu_hist[:frame + 1])
    mu_marker.set_data([frame], [mu_hist[frame]])
    P_line.set_data(np.arange(frame + 1), Pi_hist[:frame + 1])
    P_marker.set_data([frame], [Pi_hist[frame]])

    return (
        ring_line, pressure_line, ants3d, tails3d,
        Z_line, Z_marker,
        mu_line, mu_marker, mu_zero,
        P_line, P_marker,
        eq_text, left_txt, right_txt,
        *pile_bars
    )

anim = FuncAnimation(
    fig,
    update,
    frames=T,
    init_func=init,
    interval=45,
    blit=False
)

anim.save("ant_mill_continuous_inflow_inner_spiral.gif", writer=PillowWriter(fps=22))