import tkinter as tk
from tkinter import simpledialog
import serial
import threading
import queue

class XYZController(tk.Tk):
    def __init__(self, queue, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.queue = queue

        self.title("XYZ Stage Controller")
        self.geometry("400x200")

        self.step_size = tk.DoubleVar(self, value=1.0)

        self.label = tk.Label(self, text="Step size:")
        self.label.pack()

        self.entry = tk.Entry(self, textvariable=self.step_size)
        self.entry.pack()

        self.bind('<Left>', self.move_left)
        self.bind('<Right>', self.move_right)
        self.bind('<Up>', self.move_up)
        self.bind('<Down>', self.move_down)
        self.bind('<Prior>', self.move_z_up)  # Page Up
        self.bind('<Next>', self.move_z_down)  # Page Down

        self.focus_set()  # To direct all key events to the main window

    def send_gcode(self, command):
        self.queue.put(command)

    def move_left(self, event):
        step = -self.step_size.get()  # Negative for left movement
        self.send_gcode(f'G0 X{step}')

    def move_right(self, event):
        step = self.step_size.get()
        self.send_gcode(f'G0 X{step}')

    def move_up(self, event):
        step = self.step_size.get()
        self.send_gcode(f'G0 Y{step}')

    def move_down(self, event):
        step = -self.step_size.get()  # Negative for downward movement
        self.send_gcode(f'G0 Y{step}')

    def move_z_up(self, event):
        step = self.step_size.get()
        self.send_gcode(f'G0 Z{step}')

    def move_z_down(self, event):
        step = -self.step_size.get()  # Negative for downward movement
        self.send_gcode(f'G0 Z{step}')

def serial_worker(port, baudrate, q):
    try:
        ser = serial.Serial(port, baudrate)
        while True:
            command = q.get(True)  # This will block until an item is available
            ser.write(command.encode('utf-8'))
            q.task_done()
    except serial.SerialException as e:
        print(f"Could not open port {port}: {e}")
    except Exception as e:
        print(f"Exception in serial_worker: {e}")

if __name__ == "__main__":
    serial_queue = queue.Queue()
    serial_thread = threading.Thread(target=serial_worker, args=('COM3', 115200, serial_queue))  # Change 'COM3' to your Arduino's port
    serial_thread.setDaemon(True)
    serial_thread.start()

    app = XYZController(serial_queue)
    app.mainloop()
