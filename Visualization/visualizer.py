import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
import matplotlib.patches as patches

from mock_data import generate_mock_data

def get_node_group(node_id, nodes):
    """
    Finds the leader ID (cluster head) of the group this node belongs to.
    """
    for n in nodes:
        if n.isLeader:
            # Check if it is the leader itself or if the node is in its members list
            if node_id == n.id or node_id in n.members or any(getattr(m, 'id', m) == node_id for m in n.members):
                return n.id
    return None

class NetworkVisualizer:
    def __init__(self, timeline):
        self.timeline = timeline
        self.num_steps = len(timeline)
        self.current_step = 0
        
        # State for interactions
        self.highlight_leader_id = None
        self.selected_node_id = None
        
        # Animation state
        self.is_playing = False
        
        # Color palette for groups (categorical colors)
        self.colors = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
        ]
        self.leader_color_map = {}
        
        # Setup Figure and Axes
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        plt.subplots_adjust(bottom=0.25)
        
        self.setup_plot()
        self.setup_slider()
        
        # Timer for animation
        self.timer = self.fig.canvas.new_timer(interval=1000)
        self.timer.add_callback(self.auto_step)
        
        self.setup_controls()
        
        # Connect click event
        self.fig.canvas.mpl_connect('pick_event', self.on_pick)
        
    def get_group_color(self, leader_id):
        if leader_id not in self.leader_color_map:
            color_idx = len(self.leader_color_map) % len(self.colors)
            self.leader_color_map[leader_id] = self.colors[color_idx]
        return self.leader_color_map[leader_id]

    def draw_step(self):
        self.ax.clear()
        
        self.ax.set_title(f"Wireless Sensor Network - Time Step {self.current_step}")
        self.ax.set_xlabel("X Coordinate")
        self.ax.set_ylabel("Y Coordinate")
        self.ax.set_xlim(0, 200)
        self.ax.set_ylim(0, 200)
        self.ax.grid(True, linestyle='--', alpha=0.6)
        
        nodes = self.timeline[self.current_step]
        
        # --- FUTURE PLACEHOLDER: active message passing links ---
        # TODO: Draw lines between nodes to represent active message passing links.
        # Example logic:
        # for node in nodes:
        #     if node.msgQueue:  # if node is communicating
        #         target_id = node.msgQueue[0]  # assuming some structure
        #         target = next((n for n in nodes if n.id == target_id), None)
        #         if target:
        #             self.ax.plot([node.x, target.x], [node.y, target.y], 'k--', alpha=0.5)
        # ---------------------------------------------------------
        
        x_coords = []
        y_coords = []
        colors = []
        sizes = []
        
        selected_node = None
        
        for node in nodes:
            x_coords.append(node.x)
            y_coords.append(node.y)
            
            if self.selected_node_id == node.id:
                selected_node = node
            
            # Base size: Leaders are bigger
            sizes.append(120 if node.isLeader else 60)
            
            group_leader = get_node_group(node.id, nodes)
            
            if not node.alive:
                colors.append('#333333') # Dark grey for dead nodes
            elif self.highlight_leader_id is not None:
                # Group Highlight Mode
                if group_leader == self.highlight_leader_id:
                    colors.append(self.get_group_color(group_leader))
                else:
                    colors.append('#d3d3d3') # Light grey for unhighlighted
            else:
                # Default View Mode
                if group_leader is not None:
                    colors.append(self.get_group_color(group_leader))
                else:
                    colors.append('#000000') # Unaffiliated
        
        # Plot nodes
        self.scatter = self.ax.scatter(x_coords, y_coords, c=colors, s=sizes, 
                                       picker=True, pickradius=5, edgecolors='black', zorder=3)
        
        # Annotate node IDs
        for node in nodes:
            self.ax.text(node.x + 2, node.y + 2, str(node.id), fontsize=9, zorder=4)
        
        # --- Interactions: Tooltip & Coverage Radius ---
        if selected_node:
            # Tooltip
            info_text = (f"ID: {selected_node.id}\n"
                         f"Role: {'Leader' if selected_node.isLeader else 'Member'}\n"
                         f"Pos: ({selected_node.x:.1f}, {selected_node.y:.1f})\n"
                         f"Energy: {selected_node.energy:.2f}\n"
                         f"Status: {'Alive' if selected_node.alive else 'Dead'}")
            
            props = dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9, edgecolor='gray')
            self.ax.text(0.05, 0.95, info_text, transform=self.ax.transAxes, fontsize=10,
                         verticalalignment='top', bbox=props, zorder=5)
            
            # Coverage Radius if leader
            if selected_node.isLeader:
                circle = patches.Circle((selected_node.x, selected_node.y), 20, 
                                        fill=False, color=self.get_group_color(selected_node.id), 
                                        linestyle='--', linewidth=1.5, zorder=2)
                self.ax.add_patch(circle)

        # --- FUTURE PLACEHOLDER: energy drop popups ---
        # TODO: Overlay a floating temporary popup text (e.g., "-2") near a 
        # transmitting node to visually indicate an energy drop.
        # Example logic:
        # for node in nodes:
        #     if hasattr(node, 'transmitted_recently') and node.transmitted_recently:
        #         self.ax.text(node.x, node.y + 5, "-2", color='red', fontsize=10, weight='bold', zorder=6)
        # ---------------------------------------------------------
        
        self.fig.canvas.draw_idle()

    def setup_plot(self):
        self.draw_step()
        
    def setup_slider(self):
        ax_slider = plt.axes([0.2, 0.1, 0.65, 0.03], facecolor='lightgoldenrodyellow')
        self.slider = Slider(ax_slider, 'Time Step', 0, self.num_steps - 1, 
                             valinit=0, valstep=1)
        self.slider.on_changed(self.update_slider)
        
    def setup_controls(self):
        # Previous button
        ax_prev = plt.axes([0.3, 0.025, 0.1, 0.04])
        self.btn_prev = Button(ax_prev, '< Prev', hovercolor='0.975')
        self.btn_prev.on_clicked(self.prev_step)
        
        # Play/Pause button
        ax_play = plt.axes([0.45, 0.025, 0.1, 0.04])
        self.btn_play = Button(ax_play, 'Play', hovercolor='0.975')
        self.btn_play.on_clicked(self.toggle_play)
        
        # Next button
        ax_next = plt.axes([0.6, 0.025, 0.1, 0.04])
        self.btn_next = Button(ax_next, 'Next >', hovercolor='0.975')
        self.btn_next.on_clicked(self.next_step)
        
        # Reset button
        ax_reset = plt.axes([0.8, 0.025, 0.1, 0.04])
        self.btn_reset = Button(ax_reset, 'Reset View', hovercolor='0.975')
        self.btn_reset.on_clicked(self.reset_view)
        
    def prev_step(self, event=None):
        if self.current_step > 0:
            self.slider.set_val(self.current_step - 1)
            
    def next_step(self, event=None):
        if self.current_step < self.num_steps - 1:
            self.slider.set_val(self.current_step + 1)
            
    def auto_step(self):
        if self.current_step < self.num_steps - 1:
            self.slider.set_val(self.current_step + 1)
        else:
            self.slider.set_val(0) # loop
            
    def toggle_play(self, event):
        if self.is_playing:
            self.is_playing = False
            self.btn_play.label.set_text('Play')
            self.timer.stop()
        else:
            self.is_playing = True
            self.btn_play.label.set_text('Pause')
            if self.current_step >= self.num_steps - 1:
                self.slider.set_val(0)
            self.timer.start()
        self.fig.canvas.draw_idle()

    def reset_view(self, event):
        self.highlight_leader_id = None
        self.selected_node_id = None
        self.draw_step()
        
    def update_slider(self, val):
        self.current_step = int(val)
        # Keep current selection if that node still exists, else reset
        nodes = self.timeline[self.current_step]
        if self.selected_node_id is not None:
            if not any(n.id == self.selected_node_id for n in nodes):
                self.selected_node_id = None
                self.highlight_leader_id = None
        self.draw_step()
        
    def on_pick(self, event):
        # matplotlib pick_event passes an ind array of all picked points
        if not len(event.ind): return
        
        ind = event.ind[0]
        nodes = self.timeline[self.current_step]
        clicked_node = nodes[ind]
        
        self.selected_node_id = clicked_node.id
        self.highlight_leader_id = get_node_group(clicked_node.id, nodes)
        
        self.draw_step()

if __name__ == "__main__":
    timeline_data = generate_mock_data()
    viz = NetworkVisualizer(timeline_data)
    plt.show()
