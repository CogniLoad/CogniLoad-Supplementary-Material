import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline
import matplotlib as mpl

# Set global font to Times New Roman
mpl.rcParams['font.family'] = 'serif'
mpl.rcParams['font.serif'] = ['Times New Roman']
plt.rcParams['axes.unicode_minus'] = False  

sns.set_theme(style="whitegrid")

# --- 1. Data Preparation (Identical) ---
data = {
    'repeat': {
        'Model': ['Qwen3-32B-true', 'Qwen3-235B-A22B-true', 'DeepSeek-R1-Distill-Qwen-32B-true', 'Qwen/Qwen2.5-32B-Instruct-false', 'Qwen3-235B-A22B-false', 'Qwen3-32B-false'],
        '0': [0.990740741, 0.997685185, 0.988317757, 0.708333333, 0.768518519, 0.726851852],
        '25': [0.997685185, 0.99537037, 0.995316159, 0.659722222, 0.760465116, 0.717592593],
        '50': [0.995359629, 0.993055556, 0.978971963, 0.631944444, 0.738927739, 0.715277778],
        '75': [0.993039443, 0.997685185, 0.98364486, 0.638888889, 0.718309859, 0.706018519],
        '100': [0.993055556, 0.99537037, 0.983529412, 0.634259259, 0.761124122, 0.703703704]
    },
    'contradictory': {
        'Model': ['Qwen3-32B-true', 'Qwen3-235B-A22B-true', 'DeepSeek-R1-Distill-Qwen-32B-true', 'Qwen/Qwen2.5-32B-Instruct-false', 'Qwen3-235B-A22B-false', 'Qwen3-32B-false'],
        '0': [0.990740741, 0.997685185, 0.988317757, 0.708333333, 0.768518519, 0.726851852],
        '1': [0.995359629, 0.997685185, 0.988290398, 0.699074074, 0.763888889, 0.717592593],
        '2': [0.99537037, 0.997685185, 0.983796296, 0.685185185, 0.72706977, 0.68287037],
        '3': [0.774418605, 0.921113689, 0.957244656, 0.594907407, 0.604651163, 0.527777778],
        '4': [0.157407407, 0.729166667, 0.392434988, 0.12037037, 0.131944444, 0.071759259]
    },
    'irrelevant': {
        'Model': ['Qwen3-32B-true', 'Qwen3-235B-A22B-true', 'DeepSeek-R1-Distill-Qwen-32B-true', 'Qwen/Qwen2.5-32B-Instruct-false', 'Qwen3-235B-A22B-false', 'Qwen3-32B-false'],
        '0': [0.990740741, 0.997685185, 0.988317757, 0.708333333, 0.768518519, 0.726851852],
        '1': [0.993039443, 0.997674419, 0.985948478, 0.708333333, 0.780092593, 0.736111111],
        '2': [0.995359629, 0.993055556, 0.988372093, 0.6875, 0.800925926, 0.726851852],
        '3': [0.993055556, 0.997685185, 0.993006993, 0.680555556, 0.763888889, 0.708333333],
        '4': [0.990719258, 0.997685185, 0.986046512, 0.664351852, 0.793981481, 0.706018519]
    },
    'ambiguity': {
        'Model': ['Qwen3-32B-true', 'Qwen3-235B-A22B-true', 'DeepSeek-R1-Distill-Qwen-32B-true', 'Qwen/Qwen2.5-32B-Instruct-false', 'Qwen3-235B-A22B-false', 'Qwen3-32B-false'],
        '0': [0.990740741, 0.997685185, 0.988317757, 0.708333333, 0.768518519, 0.726851852],
        '1': [0.988399072, 0.997679814, 0.988372093, 0.659722222, 0.75, 0.701388889],
        '2': [0.993055556, 1.0, 0.986046512, 0.671296296, 0.743055556, 0.689814815],
        '3': [0.990740741, 0.995359629, 0.98364486, 0.668981481, 0.740740741, 0.680555556],
        '4': [0.99537037, 0.997679814, 0.990588235, 0.673611111, 0.712962963, 0.6875]
    }
}

# --- 2. Data Processing ---
all_data_long = []
for category, cat_data in data.items():
    df = pd.DataFrame(cat_data)
    value_vars = [col for col in df.columns if col != 'Model']
    df_long = df.melt(id_vars='Model', value_vars=value_vars, var_name='Level', value_name='Accuracy')
    df_long['Category'] = category.capitalize()
    all_data_long.append(df_long)

df_all = pd.concat(all_data_long, ignore_index=True)

df_all['Accuracy'] = (df_all['Accuracy'] * 100).round(2)
df_all['Type'] = np.where(df_all['Model'].str.contains('true', case=False), 'Thinking Models', 'No-Thinking Models')

# --- 3. Plotting ---
categories = df_all['Category'].unique()

for category_name in categories:
    plt.figure(figsize=(5, 4))
    ax = plt.gca()

    category_data = df_all[df_all['Category'] == category_name]
    
    # Fix the order only for the 'repeat' scenario
    if category_name == 'Repeat':
        level_order = ['0', '25', '50', '75', '100']
    else:
        # For non-repeat scenarios, sort the Level to ensure '0' is first
        numerical_levels = [int(l) for l in category_data['Level'].unique()]
        numerical_levels.sort()
        level_order = [str(l) for l in numerical_levels]

    # Create a custom color palette
    custom_palette = ["#D5A19C", "#A0BADB", "#D1DBC5", "#A4CBCC", "#9999C9"]
    
    sns.violinplot(
        ax=ax,
        data=category_data,
        x='Level',
        y='Accuracy',
        order=level_order,
        inner='box',
        linewidth=1.5,
        palette=custom_palette,
        width=0.8
    )
    
    # Calculate Q1 and Q3 for each level
    q1_values = category_data.groupby('Level')['Accuracy'].quantile(0.25).reindex(level_order)
    q3_values = category_data.groupby('Level')['Accuracy'].quantile(0.75).reindex(level_order)
    x_points = np.arange(len(level_order))

    # Create smooth curves for the Q1 and Q3 boundaries
    if len(x_points) > 3:
        x_smooth = np.linspace(x_points.min(), x_points.max(), 300)
        
        spline_q1 = make_interp_spline(x_points, q1_values.values, k=3)
        y_smooth_q1 = spline_q1(x_smooth)
        
        spline_q3 = make_interp_spline(x_points, q3_values.values, k=3)
        y_smooth_q3 = spline_q3(x_smooth)
    else:
        # If there are fewer than 4 points, connect them directly without smoothing
        x_smooth = x_points
        y_smooth_q1 = q1_values.values
        y_smooth_q3 = q3_values.values

    # Plot the shaded area and boundary lines
    ax.fill_between(
        x_smooth, y_smooth_q1, y_smooth_q3,
        alpha=0.2, color="#457b9d"
    )
    
    ax.plot(x_smooth, y_smooth_q3, color="#D0A5D2", linestyle='-', linewidth=1.5, label='Reasoning LLMs')
    ax.plot(x_smooth, y_smooth_q1, color="#C18278", linestyle='--', linewidth=1.5, label='Non-reasoning LLMs')
    
    # --- Beautify the subplot ---
    ax.set_ylabel('Accuracy (%)', fontsize=19, fontname='Times New Roman',fontweight='bold')
    ax.set_xlabel(f'Level of {category_name} Load', fontsize=19, fontweight='bold', fontname='Times New Roman')
    
    ax.tick_params(axis='x', labelrotation=0, labelsize=17)
    ax.tick_params(axis='y', labelsize=17)
    
    # Ensure X and Y axis tick labels also use Times New Roman
    for label in ax.get_xticklabels():
        label.set_fontname('Times New Roman')
        label.set_fontweight('bold') 
    for label in ax.get_yticklabels():
        label.set_fontname('Times New Roman')
        label.set_fontweight('bold')

    # Keep the Y-axis limit
    ax.set_ylim(25, 100)

    # Set legend font to Times New Roman, make text 17pt and bold, and adjust box
    legend = ax.legend(
        loc='lower left',
        prop={'family': 'Times New Roman'},
        frameon=True,
        fancybox=True,
        shadow=True,
        fontsize=19,
        title_fontsize=19,
        borderpad=0.5,      # REDUCED: Padding between legend border and content (smaller value)
        labelspacing=0.5,   # REDUCED: Vertical space between legend entries (smaller value)
        handletextpad=0.5,
        handlelength=2.5
    )

    # Iterate through legend text to make them bold
    for text in legend.get_texts():
        text.set_fontweight('bold')
    
    plt.tight_layout()
    
    # Save each plot as a PDF
    plt.savefig(f'{category_name}_accuracy_plot.pdf')
    # Close the figure to free up memory
    plt.close()