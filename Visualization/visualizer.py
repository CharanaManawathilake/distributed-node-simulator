import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
import matplotlib.patches as patches
from matplotlib.gridspec import GridSpec

def get_node_group(node_id, nodes):
    for n in nodes:
        if n.isLeader:
            if node_id == n.id or node_id in n.members or any(getattr(m, 'id', m) == node_id for m in n.members):
                return n.id
    return None

class NetworkVisualizer:
    def __init__(self, timeline):
        self.timeline = timeline
        self.current_step = 0
        self.highlight_leader_id = None
        self.selected_node_id = None
        self.is_playing = False
        self.is_paused = False
        self.is_realtime = False
        
        self.colors = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
        ]
        self.leader_color_map = {}
        
        self.fig = plt.figure(figsize=(14, 8))
        gs = GridSpec(1, 2, width_ratios=[3, 1], figure=self.fig)
        
        self.ax = self.fig.add_subplot(gs[0, 0])
        self.ax_table = self.fig.add_subplot(gs[0, 1])
        self.ax_table.axis('off') # Hiding axes for the table
        
        plt.subplots_adjust(bottom=0.25, left=0.05, right=0.95)
        
        self.timer = self.fig.canvas.new_timer(interval=1000)
        self.timer.add_callback(self.auto_step)
        
        self.setup_slider()
        self.setup_controls()
        
        self.fig.canvas.mpl_connect('pick_event', self.on_pick)
        
        if len(self.timeline) > 0:
            self.current_step = list(self.timeline.keys())[0]
            self.draw_step()

    def start_realtime(self):
        self.is_realtime = True
        plt.ion()
        self.btn_play.label.set_text('Pause')
        self.fig.show()

    def keep_open(self):
        self.is_realtime = False
        plt.ioff()
        self.btn_play.label.set_text('Play')
        self.fig.canvas.draw_idle()
        plt.show(block=True)

    def update_realtime(self, current_time):
        self.current_step = current_time
        
        max_time = max(self.timeline.keys()) if self.timeline else 0
        min_time = min(self.timeline.keys()) if self.timeline else 0
        
        self.slider.valmax = max_time
        self.slider.valmin = min_time
        self.slider.ax.set_xlim(min_time, max(max_time, min_time + 1))
        
        # Temporarily disconnecting slider to prevent infinite update loops and then set new value
        self.slider.eventson = False
        self.slider.set_val(current_time)
        self.slider.eventson = True
        
        self.draw_step()
        plt.pause(0.5)
        
        while self.is_paused:
            plt.pause(0.1)

    def get_group_color(self, leader_id):
        if leader_id not in self.leader_color_map:
            color_idx = len(self.leader_color_map) % len(self.colors)
            self.leader_color_map[leader_id] = self.colors[color_idx]
        return self.leader_color_map[leader_id]

    def draw_step(self):
        self.ax.clear()
        self.ax_table.clear()
        self.ax_table.axis('off')
        
        self.ax.set_title(f"Wireless Sensor Network - Time Step {self.current_step}")
        self.ax.set_xlabel("X Coordinate")
        self.ax.set_ylabel("Y Coordinate")
        self.ax.set_aspect('equal', adjustable='box') # To keep aspect ratio 1:1
        self.ax.grid(True, linestyle='--', alpha=0.6)
        
        if self.current_step not in self.timeline:
            self.fig.canvas.draw_idle()
            return
            
        nodes = self.timeline[self.current_step]
        
        x_coords = []
        y_coords = []
        colors = []
        sizes = []
        table_data = []
        
        selected_node = None
        
        node_dict = {n.id: n for n in nodes}
        
        # ======== message passing links ========
        for node in nodes:
            if hasattr(node, 'msgQueue') and node.msgQueue:
                for msg in node.msgQueue:
                    sender_id = getattr(msg, 'sender_id', None)
                    msg_type = getattr(msg, 'message_type', 'Msg')
                    if sender_id is not None and sender_id in node_dict:
                        sender = node_dict[sender_id]
                        
                        if sender_id != node.id:
                            self.ax.annotate(
                                '', xy=(node.x, node.y), xytext=(sender.x, sender.y),
                                arrowprops=dict(arrowstyle="->", color="purple", alpha=0.6, linestyle="dashed")
                            )
                            mid_x = (sender.x + node.x) / 2
                            mid_y = (sender.y + node.y) / 2
                            self.ax.text(mid_x, mid_y, msg_type, color='purple', fontsize=8, alpha=0.7)
        
        for node in nodes:
            x_coords.append(node.x)
            y_coords.append(node.y)
            
            if self.selected_node_id == node.id:
                selected_node = node
            
            sizes.append(120 if node.isLeader else 60)
            
            group_leader = get_node_group(node.id, nodes)
            
            if not node.alive:
                colors.append('#333333')
                status = 'Dead'
            else:
                status = 'Alive'
                if self.highlight_leader_id is not None:
                    if group_leader == self.highlight_leader_id:
                        colors.append(self.get_group_color(group_leader))
                    else:
                        colors.append('#d3d3d3')
                else:
                    if group_leader is not None:
                        colors.append(self.get_group_color(group_leader))
                    else:
                        colors.append('#000000')
            
            # data for the side table
            role = 'Leader' if node.isLeader else 'Member'
            table_data.append([node.id, role, f"{node.energy:.1f}", status])
        
        # ========== Plot nodes ==========
        if x_coords:
            self.scatter = self.ax.scatter(x_coords, y_coords, c=colors, s=sizes, 
                                           picker=True, pickradius=5, edgecolors='black', zorder=3)
            
            for node in nodes:
                self.ax.text(node.x + 2, node.y + 2, str(node.id), fontsize=9, zorder=4)
        
        # ======== Side Table =========
        if table_data:
            table_data.sort(key=lambda x: x[0]) # Sort by ID
            col_labels = ['ID', 'Role', 'Energy', 'Status']
            table = self.ax_table.table(cellText=table_data, colLabels=col_labels, loc='center', cellLoc='center')
            table.auto_set_font_size(False)
            table.set_fontsize(9)
            table.scale(1, 1.5)
            
            # Leader Rows are being highlighted
            for row_idx, row_data in enumerate(table_data):
                if row_data[1] == 'Leader':
                    for col_idx in range(len(col_labels)):
                        # row_idx + 1 because the 0th row is the header
                        table[(row_idx + 1, col_idx)].set_facecolor('#fff9c4') # Light yellow
                        
            self.ax_table.set_title("Node Energy Levels", pad=20)
        
        # ======== Tooltip & Coverage Radius ========
        if selected_node:
            info_text = (f"ID: {selected_node.id}\n"
                         f"Role: {'Leader' if selected_node.isLeader else 'Member'}\n"
                         f"Pos: ({selected_node.x:.1f}, {selected_node.y:.1f})\n"
                         f"Energy: {selected_node.energy:.2f}\n"
                         f"Status: {'Alive' if selected_node.alive else 'Dead'}")
            
            props = dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9, edgecolor='gray')
            self.ax.text(0.05, 0.95, info_text, transform=self.ax.transAxes, fontsize=10,
                         verticalalignment='top', bbox=props, zorder=5)
            
            if selected_node.isLeader:
                circle = patches.Circle((selected_node.x, selected_node.y), 20, 
                                        fill=False, color=self.get_group_color(selected_node.id), 
                                        linestyle='--', linewidth=1.5, zorder=2)
                self.ax.add_patch(circle)

        self.fig.canvas.draw_idle()

    def setup_slider(self):
        ax_slider = plt.axes([0.2, 0.1, 0.65, 0.03], facecolor='lightgoldenrodyellow')
        self.slider = Slider(ax_slider, 'Time Step', 0, 10, valinit=0, valstep=1)
        self.slider.on_changed(self.update_slider)
        
    def setup_controls(self):
        ax_prev = plt.axes([0.3, 0.025, 0.1, 0.04])
        self.btn_prev = Button(ax_prev, '< Prev', hovercolor='0.975')
        self.btn_prev.on_clicked(self.prev_step)
        
        ax_play = plt.axes([0.45, 0.025, 0.1, 0.04])
        self.btn_play = Button(ax_play, 'Play', hovercolor='0.975')
        self.btn_play.on_clicked(self.toggle_play)
        
        ax_next = plt.axes([0.6, 0.025, 0.1, 0.04])
        self.btn_next = Button(ax_next, 'Next >', hovercolor='0.975')
        self.btn_next.on_clicked(self.next_step)
        
        ax_reset = plt.axes([0.8, 0.025, 0.1, 0.04])
        self.btn_reset = Button(ax_reset, 'Reset View', hovercolor='0.975')
        self.btn_reset.on_clicked(self.reset_view)
        
    def prev_step(self, event=None):
        keys = sorted(list(self.timeline.keys()))
        if not keys: return
        try:
            idx = keys.index(self.current_step)
            if idx > 0:
                self.slider.set_val(keys[idx - 1])
        except ValueError:
            pass
            
    def next_step(self, event=None):
        keys = sorted(list(self.timeline.keys()))
        if not keys: return
        try:
            idx = keys.index(self.current_step)
            if idx < len(keys) - 1:
                self.slider.set_val(keys[idx + 1])
        except ValueError:
            pass
            
    def auto_step(self):
        keys = sorted(list(self.timeline.keys()))
        if not keys: return
        try:
            idx = keys.index(self.current_step)
            if idx < len(keys) - 1:
                self.slider.set_val(keys[idx + 1])
            else:
                self.slider.set_val(keys[0])
        except ValueError:
            pass
            
    def toggle_play(self, event):
        if self.is_realtime:
            self.is_paused = not self.is_paused
            if self.is_paused:
                self.btn_play.label.set_text('Play')
            else:
                self.btn_play.label.set_text('Pause')
            self.fig.canvas.draw_idle()
        else:
            if self.is_playing:
                self.is_playing = False
                self.btn_play.label.set_text('Play')
                self.timer.stop()
            else:
                self.is_playing = True
                self.btn_play.label.set_text('Pause')
                self.timer.start()
            self.fig.canvas.draw_idle()

    def reset_view(self, event):
        self.highlight_leader_id = None
        self.selected_node_id = None
        self.draw_step()
        
    def update_slider(self, val):
        if not self.timeline: return
        keys = list(self.timeline.keys())
        closest_key = min(keys, key=lambda k: abs(k - val))
        
        self.current_step = closest_key
        
        nodes = self.timeline[self.current_step]
        if self.selected_node_id is not None:
            if not any(n.id == self.selected_node_id for n in nodes):
                self.selected_node_id = None
                self.highlight_leader_id = None
        self.draw_step()
        
    def on_pick(self, event):
        if not len(event.ind): return
        
        ind = event.ind[0]
        nodes = self.timeline[self.current_step]
        clicked_node = nodes[ind]
        
        self.selected_node_id = clicked_node.id
        self.highlight_leader_id = get_node_group(clicked_node.id, nodes)
        
        self.draw_step()

if __name__ == "__main__":
    from mock_data import generate_mock_data
    timeline_data = generate_mock_data()
    timeline_dict = {i: nodes for i, nodes in enumerate(timeline_data)}
    viz = NetworkVisualizer(timeline_dict)
    plt.show()
