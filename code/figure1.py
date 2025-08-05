import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import matplotlib.ticker as mticker
from scipy.interpolate import make_interp_spline
import matplotlib as mpl

# Set global Times New Roman font
mpl.rcParams['font.family'] = 'Times New Roman'
mpl.rcParams['mathtext.fontset'] = 'stix'  # For mathematical text
mpl.rcParams['axes.unicode_minus'] = False  # Correctly display minus signs

# Disable seaborn's font override for consistency with mpl.rcParams
sns.set_theme(style="whitegrid") # Use a clean white grid style, but don't set font here

# --- Conceptual Data for Trends (same as your original code) ---
conceptual_load = np.linspace(0, 32000, 300)
pre_overload_x = 9500
post_overload_x = 18200

q3_points_x = np.array([0, 7000, 15000, 24000, 32000]) # Adjusted x-points for better curve control
q3_points_y = np.array([1, 0.95, 0.85, 0.55, 0.20])
q3_points_x, q3_points_y = zip(*sorted(zip(q3_points_x, q3_points_y)))
q3_points_x = np.array(q3_points_x)
q3_points_y = np.array(q3_points_y)
spl_q3 = make_interp_spline(q3_points_x, q3_points_y, k=3)
q3_conceptual_accuracy_interp = spl_q3(conceptual_load)

q1_points_x = np.array([0, 7000, 20000, 24000, 32000])
q1_points_y = np.array([1, 0.75, 0.60, 0.58, 0.55])
q1_points_x, q1_points_y = zip(*sorted(zip(q1_points_x, q1_points_y)))
q1_points_x = np.array(q1_points_x)
q1_points_y = np.array(q1_points_y)
spl_q1 = make_interp_spline(q1_points_x, q1_points_y, k=3)
q1_conceptual_accuracy_interp = spl_q1(conceptual_load)

# --- Plotting Setup ---
plt.figure(figsize=(12, 7))
ax = plt.gca()

# Plot Q3 trend
q3_std = 0.02
ax.plot(conceptual_load, q3_conceptual_accuracy_interp,
        color="#E0BBE4",
        linestyle='-',
        linewidth=2.0,
        label='Parametric Memory')
ax.fill_between(conceptual_load,
                q3_conceptual_accuracy_interp - q3_std,
                q3_conceptual_accuracy_interp + q3_std,
                color="#E0BBE4", alpha=0.2)

# Plot Q1 trend
q1_std = 0.03
ax.plot(conceptual_load, q1_conceptual_accuracy_interp,
        color="#957DAD",
        linestyle='-',
        linewidth=2.0,
        label='Contextual Memory')
ax.fill_between(conceptual_load,
                q1_conceptual_accuracy_interp - q1_std,
                q1_conceptual_accuracy_interp + q1_std,
                color="#957DAD", alpha=0.2)

# --- Adding Conceptual Decline Markers ---
# ax.axvline(x=pre_overload_x, color="#7DA2F6", linestyle='--', linewidth=2,
#            label='Intrinsic Cognitive Load')
# ax.axvline(x=post_overload_x, color='#f47a75', linestyle='--', linewidth=2,
#            label='Extraneous Cognitive Load')

# Define bounding box styles
bbox = dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor="#59A38B", alpha=0.8)
bbox1 = dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor="#d760ea", alpha=0.8)
bbox2 = dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor='#f47a75', alpha=0.8)

# Add text labels for vertical lines, explicitly setting fontname
ax.text(4000, 0.6, 'Early Overload', color="#59A38B", fontsize=27,
        ha='center', va='bottom', transform=ax.get_xaxis_transform(), bbox=bbox,
        fontname='Times New Roman',fontweight='bold') # Explicitly set fontname

ax.text(14000, 0.4, 'Mid Overload', color='#d760ea', fontsize=27,
        ha='center', va='bottom', transform=ax.get_xaxis_transform(), bbox=bbox1,
        fontname='Times New Roman',fontweight='bold') # Explicitly set fontname

ax.text(26500, 0.16, 'Full Overload', color='#f47a75', fontsize=27,
        ha='center', va='bottom', transform=ax.get_xaxis_transform(), bbox=bbox2,
        fontname='Times New Roman',fontweight='bold') # Explicitly set fontname

# --- Adding Background Shaded Regions ---
fine_grained_end = 8000
coarse_grained_end = 20000

ax.axvspan(0, fine_grained_end, color='green', alpha=0.1)
ax.axvspan(fine_grained_end, coarse_grained_end, color='blue', alpha=0.1)
ax.axvspan(coarse_grained_end, conceptual_load.max(), color='red', alpha=0.1)

# --- Beautifying the Plot ---
# Set labels with explicit font properties
ax.set_ylabel('Accuracy (%)', fontsize=24, fontweight='bold', fontname='Times New Roman')
ax.set_xlabel('Level of Cognitive Load', fontsize=24, fontweight='bold', fontname='Times New Roman')
ax.margins(x=0)

# Adjust x-axis ticks to match a "Sequence Length" style, explicitly setting font for tick labels
ax.set_xticks([0, 7000, 14000, 21000, 28000])
ax.set_xticklabels(['0', '1', '2', '3', '4'], fontsize=20, fontname='Times New Roman', fontweight='bold')

ax.set_ylim(-0.05, 1.05)
ax.set_yticks(np.arange(0, 1.1, 0.1))
ax.tick_params(axis='y', labelsize=20, labelfontfamily='Times New Roman', labelcolor='black')
for label in ax.get_yticklabels():
    label.set_fontweight('bold')
# Ensure grid is visible
ax.grid(True, linestyle=':', alpha=0.7)

# Prepare legend handles and labels
handles, labels = ax.get_legend_handles_labels()
unique_labels = {}
for h, l in zip(handles, labels):
    if l not in unique_labels:
        unique_labels[l] = h

order = ['Parametric Memory', 'Contextual Memory',
         'Intrinsic Cognitive Load', 'Extraneous Cognitive Load']

ordered_handles = [h for l in order for h, hl in zip(unique_labels.values(), unique_labels.keys()) if hl == l]
ordered_labels = [l for l in order if l in unique_labels.keys()]

# Move legend to lower left and adjust font size and family
legend = ax.legend(ordered_handles, ordered_labels, loc='lower left', fontsize=22, frameon=True, fancybox=True, shadow=True)
# Set font for legend text
for text in legend.get_texts():
    text.set_fontname('Times New Roman')
    text.set_weight('bold')

# Custom formatter to remove '%' but show as percentages
def percent_formatter(x, pos):
    return f'{int(x * 100)}'

ax.yaxis.set_major_formatter(mticker.FuncFormatter(percent_formatter))

plt.tight_layout()

# --- Export to PDF ---
plt.savefig('cognitive_load_trends.pdf', bbox_inches='tight')

plt.show()