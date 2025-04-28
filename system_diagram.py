import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Create figure and axis
fig, ax = plt.subplots(figsize=(14, 10))

# Set background color
ax.set_facecolor('#f5f5f5')

# Remove axis ticks and labels
ax.set_xticks([])
ax.set_yticks([])

# Define colors
colors = {
    'raspberry_pi': '#CD6155',
    'bluetooth': '#5499C7',
    'receiver': '#5DADE2',
    'video': '#58D68D',
    'audio': '#F4D03F',
    'nav_system': '#AF7AC5',
    'arrow': '#34495E',
    'background': '#EAECEE',
    'function': '#D5F5E3',
    'loop': '#FADBD8'
}

# Draw Raspberry Pi box
rpi_rect = patches.Rectangle((0.1, 0.7), 0.25, 0.2, linewidth=2, edgecolor=colors['raspberry_pi'], 
                            facecolor=colors['background'], alpha=0.8)
ax.add_patch(rpi_rect)
ax.text(0.225, 0.85, 'Raspberry Pi', ha='center', va='center', fontsize=12, fontweight='bold')
ax.text(0.225, 0.8, 'raspberry_pi_sender.py', ha='center', va='center', fontsize=10, style='italic')

# Draw Bluetooth Receiver box
bt_rect = patches.Rectangle((0.45, 0.7), 0.25, 0.2, linewidth=2, edgecolor=colors['bluetooth'], 
                           facecolor=colors['background'], alpha=0.8)
ax.add_patch(bt_rect)
ax.text(0.575, 0.85, 'Bluetooth Receiver', ha='center', va='center', fontsize=12, fontweight='bold')
ax.text(0.575, 0.8, 'bluetooth_receiver.py', ha='center', va='center', fontsize=10, style='italic')

# Draw Video Processor box
video_rect = patches.Rectangle((0.25, 0.4), 0.25, 0.2, linewidth=2, edgecolor=colors['video'], 
                              facecolor=colors['background'], alpha=0.8)
ax.add_patch(video_rect)
ax.text(0.375, 0.55, 'Video Processor', ha='center', va='center', fontsize=12, fontweight='bold')
ax.text(0.375, 0.5, 'video_processor.py', ha='center', va='center', fontsize=10, style='italic')

# Draw Audio Processor box
audio_rect = patches.Rectangle((0.65, 0.4), 0.25, 0.2, linewidth=2, edgecolor=colors['audio'], 
                              facecolor=colors['background'], alpha=0.8)
ax.add_patch(audio_rect)
ax.text(0.775, 0.55, 'Audio Processor', ha='center', va='center', fontsize=12, fontweight='bold')
ax.text(0.775, 0.5, 'audio_processor.py', ha='center', va='center', fontsize=10, style='italic')

# Draw Navigation System box
nav_rect = patches.Rectangle((0.45, 0.1), 0.25, 0.2, linewidth=2, edgecolor=colors['nav_system'], 
                            facecolor=colors['background'], alpha=0.8)
ax.add_patch(nav_rect)
ax.text(0.575, 0.25, 'Navigation System', ha='center', va='center', fontsize=12, fontweight='bold')
ax.text(0.575, 0.2, 'navigation_system.py', ha='center', va='center', fontsize=10, style='italic')

# Draw arrows
# Raspberry Pi to Bluetooth Receiver
arrow1 = patches.FancyArrowPatch((0.35, 0.8), (0.45, 0.8), connectionstyle="arc3,rad=0", 
                                arrowstyle='->', linewidth=2, color=colors['arrow'])
ax.add_patch(arrow1)

# Bluetooth Receiver to Video Processor
arrow2 = patches.FancyArrowPatch((0.5, 0.7), (0.375, 0.6), connectionstyle="arc3,rad=-0.2", 
                                arrowstyle='->', linewidth=2, color=colors['arrow'])
ax.add_patch(arrow2)

# Bluetooth Receiver to Audio Processor
arrow3 = patches.FancyArrowPatch((0.65, 0.7), (0.775, 0.6), connectionstyle="arc3,rad=0.2", 
                                arrowstyle='->', linewidth=2, color=colors['arrow'])
ax.add_patch(arrow3)

# Video Processor to Navigation System
arrow4 = patches.FancyArrowPatch((0.375, 0.4), (0.5, 0.3), connectionstyle="arc3,rad=-0.2", 
                                arrowstyle='->', linewidth=2, color=colors['arrow'])
ax.add_patch(arrow4)

# Audio Processor to Navigation System
arrow5 = patches.FancyArrowPatch((0.775, 0.4), (0.65, 0.3), connectionstyle="arc3,rad=0.2", 
                                arrowstyle='->', linewidth=2, color=colors['arrow'])
ax.add_patch(arrow5)

# Add data flow labels
ax.text(0.4, 0.83, 'Video & Audio Data', ha='center', va='center', fontsize=8)
ax.text(0.4, 0.62, 'Video Frames', ha='center', va='center', fontsize=8)
ax.text(0.75, 0.62, 'Audio Data', ha='center', va='center', fontsize=8)
ax.text(0.4, 0.32, 'Position Updates', ha='center', va='center', fontsize=8)
ax.text(0.75, 0.32, 'Voice Commands', ha='center', va='center', fontsize=8)

# Add function details
# Raspberry Pi functions
functions_rpi = [
    'VideoCapture.read_frame()',
    'AudioCapture.read_audio()',
    'BluetoothSender.send_video_frame()',
    'BluetoothSender.send_audio_data()'
]
func_box_rpi = patches.Rectangle((0.02, 0.45), 0.2, 0.15, linewidth=1, edgecolor='gray', 
                                facecolor=colors['function'], alpha=0.8)
ax.add_patch(func_box_rpi)
ax.text(0.12, 0.57, 'Key Functions:', ha='center', va='center', fontsize=8, fontweight='bold')
for i, func in enumerate(functions_rpi):
    ax.text(0.12, 0.55 - i*0.02, func, ha='center', va='center', fontsize=7)

# Bluetooth Receiver functions
functions_bt = [
    'BluetoothReceiver.start_server()',
    '_accept_connections()',
    '_handle_client()',
    '_handle_video_data()',
    '_handle_audio_data()'
]
func_box_bt = patches.Rectangle((0.78, 0.75), 0.2, 0.15, linewidth=1, edgecolor='gray', 
                               facecolor=colors['function'], alpha=0.8)
ax.add_patch(func_box_bt)
ax.text(0.88, 0.87, 'Key Functions:', ha='center', va='center', fontsize=8, fontweight='bold')
for i, func in enumerate(functions_bt):
    ax.text(0.88, 0.85 - i*0.02, func, ha='center', va='center', fontsize=7)

# Video Processor functions
functions_video = [
    'StellaVSLAMProcessor.start_processing()',
    '_process_frames()',
    '_process_single_frame()',
    'get_current_position()'
]
func_box_video = patches.Rectangle((0.02, 0.2), 0.2, 0.15, linewidth=1, edgecolor='gray', 
                                  facecolor=colors['function'], alpha=0.8)
ax.add_patch(func_box_video)
ax.text(0.12, 0.32, 'Key Functions:', ha='center', va='center', fontsize=8, fontweight='bold')
for i, func in enumerate(functions_video):
    ax.text(0.12, 0.3 - i*0.02, func, ha='center', va='center', fontsize=7)

# Audio Processor functions
functions_audio = [
    'AudioToTextConverter.start_processing()',
    '_process_audio()',
    '_convert_audio_to_text()',
    '_identify_command()',
    '_execute_command()'
]
func_box_audio = patches.Rectangle((0.78, 0.2), 0.2, 0.15, linewidth=1, edgecolor='gray', 
                                  facecolor=colors['function'], alpha=0.8)
ax.add_patch(func_box_audio)
ax.text(0.88, 0.32, 'Key Functions:', ha='center', va='center', fontsize=8, fontweight='bold')
for i, func in enumerate(functions_audio):
    ax.text(0.88, 0.3 - i*0.02, func, ha='center', va='center', fontsize=7)

# Add loop details
# Raspberry Pi loops
loops_rpi = [
    'Main loop: Capture & send frames/audio',
    '_video_sender_thread loop',
    '_audio_sender_thread loop'
]
loop_box_rpi = patches.Rectangle((0.02, 0.05), 0.2, 0.1, linewidth=1, edgecolor='gray', 
                                facecolor=colors['loop'], alpha=0.8)
ax.add_patch(loop_box_rpi)
ax.text(0.12, 0.13, 'Key Loops:', ha='center', va='center', fontsize=8, fontweight='bold')
for i, loop in enumerate(loops_rpi):
    ax.text(0.12, 0.11 - i*0.02, loop, ha='center', va='center', fontsize=7)

# Bluetooth Receiver loops
loops_bt = [
    '_accept_connections loop',
    '_handle_client loop'
]
loop_box_bt = patches.Rectangle((0.78, 0.95), 0.2, 0.05, linewidth=1, edgecolor='gray', 
                               facecolor=colors['loop'], alpha=0.8)
ax.add_patch(loop_box_bt)
ax.text(0.88, 0.98, 'Key Loops:', ha='center', va='center', fontsize=8, fontweight='bold')
for i, loop in enumerate(loops_bt):
    ax.text(0.88, 0.96 - i*0.02, loop, ha='center', va='center', fontsize=7)

# Video Processor loops
loops_video = [
    '_process_frames loop'
]
loop_box_video = patches.Rectangle((0.25, 0.25), 0.15, 0.05, linewidth=1, edgecolor='gray', 
                                  facecolor=colors['loop'], alpha=0.8)
ax.add_patch(loop_box_video)
ax.text(0.325, 0.28, 'Key Loops:', ha='center', va='center', fontsize=8, fontweight='bold')
ax.text(0.325, 0.26, loops_video[0], ha='center', va='center', fontsize=7)

# Audio Processor loops
loops_audio = [
    '_process_audio loop'
]
loop_box_audio = patches.Rectangle((0.65, 0.25), 0.15, 0.05, linewidth=1, edgecolor='gray', 
                                  facecolor=colors['loop'], alpha=0.8)
ax.add_patch(loop_box_audio)
ax.text(0.725, 0.28, 'Key Loops:', ha='center', va='center', fontsize=8, fontweight='bold')
ax.text(0.725, 0.26, loops_audio[0], ha='center', va='center', fontsize=7)

# Add queues
queue_video = patches.Ellipse((0.45, 0.55), 0.05, 0.05, linewidth=1, edgecolor='black', 
                             facecolor='white', alpha=0.8)
ax.add_patch(queue_video)
ax.text(0.45, 0.55, 'Q', ha='center', va='center', fontsize=8, fontweight='bold')
ax.text(0.45, 0.51, 'video_queue', ha='center', va='center', fontsize=7)

queue_audio = patches.Ellipse((0.65, 0.55), 0.05, 0.05, linewidth=1, edgecolor='black', 
                             facecolor='white', alpha=0.8)
ax.add_patch(queue_audio)
ax.text(0.65, 0.55, 'Q', ha='center', va='center', fontsize=8, fontweight='bold')
ax.text(0.65, 0.51, 'audio_queue', ha='center', va='center', fontsize=7)

# Add title
ax.text(0.5, 0.97, 'NavSystem Bluetooth Integration - Technical Architecture', 
       ha='center', va='center', fontsize=16, fontweight='bold')

# Add legend
legend_elements = [
    patches.Patch(facecolor=colors['background'], edgecolor=colors['raspberry_pi'], label='Raspberry Pi Component'),
    patches.Patch(facecolor=colors['background'], edgecolor=colors['bluetooth'], label='Bluetooth Component'),
    patches.Patch(facecolor=colors['background'], edgecolor=colors['video'], label='Video Processing Component'),
    patches.Patch(facecolor=colors['background'], edgecolor=colors['audio'], label='Audio Processing Component'),
    patches.Patch(facecolor=colors['background'], edgecolor=colors['nav_system'], label='Navigation System Component'),
    patches.Patch(facecolor=colors['function'], edgecolor='gray', label='Key Functions'),
    patches.Patch(facecolor=colors['loop'], edgecolor='gray', label='Key Loops'),
    patches.Ellipse((0, 0), 1, 1, facecolor='white', edgecolor='black', label='Data Queue')
]
ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.02), 
         ncol=4, fontsize=8)

# Add data flow description
data_flow_text = """
Data Flow:
1. Raspberry Pi captures video frames and audio data
2. Data is sent via Bluetooth to the NavSystem Bluetooth Receiver
3. Receiver routes video frames to video_queue and audio data to audio_queue
4. Video Processor consumes frames from video_queue, processes them for stella vslam, and updates position
5. Audio Processor consumes data from audio_queue, converts to text, and interprets commands
6. Both processors update the Navigation System with position data and commands
"""
props = dict(boxstyle='round', facecolor='white', alpha=0.7)
ax.text(0.02, 0.95, data_flow_text, transform=ax.transAxes, fontsize=8,
       verticalalignment='top', bbox=props)

# Set axis limits
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)

# Add border
for spine in ax.spines.values():
    spine.set_visible(True)
    spine.set_color('black')
    spine.set_linewidth(1)

# Save the figure
plt.savefig('/home/ubuntu/bluetooth_system_diagram.png', dpi=300, bbox_inches='tight')
plt.close()
