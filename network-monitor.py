# Project: Network Monitor Tool
# Application developed by: codewithj4ke - September 2024
# Learning Python programming with the assistance of AI and online courses

import tkinter as tk
from tkinter import ttk  # Import ttk for tabbed interface
import psutil
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import socket
import threading
import logging
import requests  # Add this import
from PIL import Image, ImageTk  # Add this import
from io import BytesIO  # Add this import


# Setup logging
logging.basicConfig(filename='system_monitor.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class SystemMonitor:
    def __init__(self, root):
        self.last_recv = None
        self.last_sent = None
        self.last_time = time.time()
        self.start_time = self.last_time
        self.times = []
        self.recv_data = []
        self.sent_data = []

        self.root = root
        self.setup_ui()
        self.start_update_thread()

    from PIL import Image, ImageTk
    import requests
    from io import BytesIO

    def setup_ui(self):
        self.root.title("Network Monitor Tool")
        self.root.geometry("1200x600")  # Set initial window size

        # Configure styles
        self.bg_color = "#2E3A43"
        self.fg_color = "#E0E0E0"
        self.button_bg = "#007ACC"
        self.button_fg = "#FFFFFF"
        self.header_font = ('Tahoma', 16)
        self.text_font = ('Tahoma', 10)
        self.button_font = ('Tahoma', 12, 'bold')
        self.plot_bg = '#1E2A32'  # Dark background for the plot
        self.plot_fg = '#E0E0E0'  # Light foreground for the plot

        # Root window configuration
        self.root.configure(bg=self.bg_color)

        # Create a frame for the text information
        self.info_frame = tk.Frame(self.root, bg=self.bg_color)
        self.info_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Create a frame for the header and logo
        self.header_frame = tk.Frame(self.info_frame, bg=self.bg_color)
        self.header_frame.grid(row=0, column=0, pady=(0, 5), sticky='w')

        # Load and add the logo image
        response = requests.get("https://cdn-icons-png.flaticon.com/512/2593/2593154.png")
        logo_image = Image.open(BytesIO(response.content))
        logo_image = logo_image.resize((40, 40))  # Adjust size as needed
        self.logo_photo = ImageTk.PhotoImage(logo_image)
        self.logo_label = tk.Label(self.header_frame, image=self.logo_photo, bg=self.bg_color)
        self.logo_label.pack(side=tk.LEFT)

        # Create a header label
        self.header_label = tk.Label(self.header_frame, text="Network Monitor Tool", font=self.header_font,
                                     bg=self.bg_color, fg=self.fg_color)
        self.header_label.pack(side=tk.LEFT, padx=10)

        # Create a text widget and a scrollbar
        self.text_widget = tk.Text(self.info_frame, wrap='word', height=25, width=50, font=self.text_font, bg='#1E2A32',
                                   fg=self.fg_color)
        self.text_widget.grid(row=1, column=0, sticky='nsew')

        self.scrollbar = tk.Scrollbar(self.info_frame, orient='vertical', command=self.text_widget.yview)
        self.scrollbar.grid(row=1, column=1, sticky='ns')

        self.text_widget.config(yscrollcommand=self.scrollbar.set)

        # Create a frame for the refresh button
        self.refresh_button_frame = tk.Frame(self.info_frame, bg=self.bg_color)
        self.refresh_button_frame.grid(row=2, column=0, pady=10, sticky='w')

        self.refresh_button = tk.Button(self.refresh_button_frame, text="Force Refresh", command=self.display_info,
                                        bg=self.button_bg, fg=self.button_fg, font=self.button_font)
        self.refresh_button.pack()

        # Create a frame for the plot
        self.plot_frame = tk.Frame(self.root, bg=self.bg_color)
        self.plot_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.fig, self.ax = plt.subplots(figsize=(8, 4), facecolor=self.plot_bg)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Configure tags for bold text
        self.text_widget.tag_configure('bold', font=('Helvetica', 12, 'bold'))

    def get_network_info(self):
        try:
            hostname = socket.gethostname()
            ip_addresses = [addr_info[4][0] for addr_info in socket.getaddrinfo(hostname, None)
                            if addr_info[4][0].startswith(('192.', '10.', '172.'))]
            return {'hostname': hostname, 'IP Address': ip_addresses}
        except Exception as e:
            logging.error(f"Error retrieving network info: {e}")
            return {'error': str(e)}

    def get_memory_info(self):
        try:
            mem = psutil.virtual_memory()
            return {
                'total_memory': f"{mem.total / (1024 ** 3):.2f} GB",
                'available_memory': f"{mem.available / (1024 ** 3):.2f} GB",
                'used_memory': f"{mem.used / (1024 ** 3):.2f} GB",
                'memory_percentage': f"{mem.percent}%"
            }
        except Exception as e:
            logging.error(f"Error retrieving memory info: {e}")
            return {'error': str(e)}

    def get_storage_info(self):
        try:
            partitions = psutil.disk_partitions()
            storage_info = []
            for partition in partitions:
                usage = psutil.disk_usage(partition.mountpoint)
                storage_info.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total': f"{usage.total / (1024 ** 3):.2f} GB",
                    'used': f"{usage.used / (1024 ** 3):.2f} GB",
                    'free': f"{usage.free / (1024 ** 3):.2f} GB",
                    'percent': f"{usage.percent}%"
                })
            return {'partitions': storage_info}
        except Exception as e:
            logging.error(f"Error retrieving storage info: {e}")
            return {'error': str(e)}

    def get_network_traffic(self):
        try:
            stats = psutil.net_io_counters()
            return stats.bytes_recv, stats.bytes_sent
        except Exception as e:
            logging.error(f"Error retrieving network traffic: {e}")
            return 0, 0

    def format_memory_info(self, memory_info):
        return (
            f"Total Memory: {memory_info['total_memory']}\n"
            f"Available Memory: {memory_info['available_memory']}\n"
            f"Used Memory: {memory_info['used_memory']}\n"
            f"Memory Percentage: {memory_info['memory_percentage']}\n"
        )

    def format_storage_info(self, storage_info):
        return '\n'.join(
            (f"Device: {partition['device']}\n"
             f"Mountpoint: {partition['mountpoint']}\n"
             f"Filesystem Type: {partition['fstype']}\n"
             f"Total: {partition['total']}\n"
             f"Used: {partition['used']}\n"
             f"Free: {partition['free']}\n"
             f"Percent Used: {partition['percent']}\n\n")
            for partition in storage_info['partitions']
        )

    def update_graph(self):
        try:
            current_recv, current_sent = self.get_network_traffic()
            current_time = time.time()

            if self.last_recv is not None and self.last_sent is not None:
                elapsed_time = current_time - self.last_time
                recv_rate = (current_recv - self.last_recv) / elapsed_time
                sent_rate = (current_sent - self.last_sent) / elapsed_time

                self.times.append(current_time - self.start_time)
                self.recv_data.append(recv_rate / 1e6)  # Convert bytes to MB
                self.sent_data.append(sent_rate / 1e6)  # Convert bytes to MB

                self.ax.clear()
                self.ax.plot(self.times, self.recv_data, label='Incoming Data (MB/s)', color='yellow')  # Yellow color
                self.ax.plot(self.times, self.sent_data, label='Outgoing Data (MB/s)', color='green')  # Green color
                self.ax.set_xlabel('Time (s)', color=self.plot_fg)
                self.ax.set_ylabel('Data Rate (MB/s)', color=self.plot_fg)
                self.ax.set_title('Live Network Traffic', color=self.plot_fg)
                self.ax.legend()
                self.ax.grid(True, color='gray', linestyle='--', linewidth=0.5)  # Add grid with color

                # Optional: Add annotation for recent data point
                if self.times:
                    self.ax.annotate(f'{self.recv_data[-1]:.2f} MB/s', xy=(self.times[-1], self.recv_data[-1]),
                                     xytext=(self.times[-1], self.recv_data[-1] + 0.5),
                                     color=self.plot_fg,  # Set annotation color
                                     arrowprops=dict(facecolor='#555555', edgecolor='none',
                                                     shrink=0.10))  # Lighter gray for arrow
                    self.ax.annotate(f'{self.sent_data[-1]:.2f} MB/s', xy=(self.times[-1], self.sent_data[-1]),
                                     xytext=(self.times[-1], self.sent_data[-1] + 0.10),
                                     color=self.plot_fg,  # Set annotation color
                                     arrowprops=dict(facecolor='#555555', edgecolor='none',
                                                     shrink=0.10))  # Lighter gray for arrow

                # Apply dark theme to the plot
                self.ax.set_facecolor(self.plot_bg)
                self.ax.xaxis.label.set_color(self.plot_fg)
                self.ax.yaxis.label.set_color(self.plot_fg)
                self.ax.tick_params(axis='both', colors=self.plot_fg)
                self.fig.patch.set_facecolor(self.plot_bg)

                self.update_text_widget()

            self.last_recv = current_recv
            self.last_sent = current_sent
            self.last_time = current_time

            self.canvas.draw()
        except Exception as e:
            logging.error(f"Error updating graph: {e}")

    def update_text_widget(self):
        try:
            # Save the current scroll position
            y_scroll_position = self.text_widget.yview()[0]

            self.text_widget.delete(1.0, tk.END)

            self.text_widget.insert(tk.END, "Network Information:\n", 'bold')
            network_info = self.get_network_info()
            for key, value in network_info.items():
                self.text_widget.insert(tk.END, f"{key.capitalize()}: {value}\n")

            self.text_widget.insert(tk.END, "\nCurrent Network Data Rates:\n", 'bold')
            current_recv, current_sent = self.get_network_traffic()
            recv_rate = (current_recv - self.last_recv) / (time.time() - self.last_time) / 1e6  # Convert bytes to MB
            sent_rate = (current_sent - self.last_sent) / (time.time() - self.last_time) / 1e6  # Convert bytes to MB
            self.text_widget.insert(tk.END, f"Incoming Data Rate: {recv_rate:.2f} MB/s\n")
            self.text_widget.insert(tk.END, f"Outgoing Data Rate: {sent_rate:.2f} MB/s\n")

            self.text_widget.insert(tk.END, "\nMemory Information:\n", 'bold')
            memory_info = self.get_memory_info()
            self.text_widget.insert(tk.END, self.format_memory_info(memory_info))

            self.text_widget.insert(tk.END, "\nStorage Information:\n", 'bold')
            storage_info = self.get_storage_info()
            self.text_widget.insert(tk.END, self.format_storage_info(storage_info))

            # Restore the scroll position
            self.text_widget.yview_moveto(y_scroll_position)
        except Exception as e:
            logging.error(f"Error updating text widget: {e}")

    def update_graph_thread(self):
        while True:
            self.update_graph()
            time.sleep(1)

    def start_update_thread(self):
        thread = threading.Thread(target=self.update_graph_thread, daemon=True)
        thread.start()

    def display_info(self):
        self.update_text_widget()
        self.refresh_button_frame.grid(row=2, column=0, pady=10, sticky='w')

if __name__ == "__main__":
    root = tk.Tk()
    monitor = SystemMonitor(root)
    root.mainloop()
