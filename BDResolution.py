import ctypes
import psutil
import time
import os
import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import threading
import xml.etree.ElementTree as ET

class DEVMODE(ctypes.Structure):
    _fields_ = [("dmDeviceName", ctypes.c_wchar * 32),
                ("dmSpecVersion", ctypes.c_ushort),
                ("dmDriverVersion", ctypes.c_ushort),
                ("dmSize", ctypes.c_ushort),
                ("dmDriverExtra", ctypes.c_ushort),
                ("dmFields", ctypes.c_ulong),
                ("dmPosition", ctypes.c_long * 2),
                ("dmDisplayOrientation", ctypes.c_ulong),
                ("dmDisplayFixedOutput", ctypes.c_ulong),
                ("dmColor", ctypes.c_short),
                ("dmDuplex", ctypes.c_short),
                ("dmYResolution", ctypes.c_short),
                ("dmTTOption", ctypes.c_short),
                ("dmCollate", ctypes.c_short),
                ("dmFormName", ctypes.c_wchar * 32),
                ("dmLogPixels", ctypes.c_ushort),
                ("dmBitsPerPel", ctypes.c_ulong),
                ("dmPelsWidth", ctypes.c_ulong),
                ("dmPelsHeight", ctypes.c_ulong),
                ("dmDisplayFlags", ctypes.c_ulong),
                ("dmDisplayFrequency", ctypes.c_ulong),
                ("dmICMMethod", ctypes.c_ulong),
                ("dmICMIntent", ctypes.c_ulong),
                ("dmMediaType", ctypes.c_ulong),
                ("dmDitherType", ctypes.c_ulong),
                ("dmReserved1", ctypes.c_ulong),
                ("dmReserved2", ctypes.c_ulong),
                ("dmPanningWidth", ctypes.c_ulong),
                ("dmPanningHeight", ctypes.c_ulong)]

default_app_path = r"C:\Program Files (x86)\bloodstrike\Engine\Binaries\Win64\BloodStrike.exe"
current_app_path = default_app_path
current_resolution = (1920, 1080)
current_refresh_rate = 165
stop_on_close = False
monitoring_active = False
monitor_thread = None

def set_resolution(width, height, refresh_rate):
    try:
        devmode = DEVMODE()
        devmode.dmSize = ctypes.sizeof(DEVMODE)
        devmode.dmPelsWidth = width
        devmode.dmPelsHeight = height
        devmode.dmDisplayFrequency = refresh_rate
        devmode.dmFields = 0x00000001 | 0x00000040  # dmPelsWidth, dmPelsHeight, dmDisplayFrequency
        
        result = ctypes.windll.user32.ChangeDisplaySettingsW(ctypes.byref(devmode), 0)
        if result != 0:
            raise ctypes.WinError(result)
    except Exception as e:
        raise RuntimeError(f"Erro ao alterar resolução: {str(e)}")

def reset_resolution():
    try:
        result = ctypes.windll.user32.ChangeDisplaySettingsW(None, 0)
        if result != 0:
            raise ctypes.WinError(result)
    except Exception as e:
        raise RuntimeError(f"Erro ao restaurar resolução: {str(e)}")

def save_config():
    try:
        root = ET.Element("config")
        ET.SubElement(root, "app_path").text = current_app_path
        ET.SubElement(root, "resolution_width").text = str(current_resolution[0])
        ET.SubElement(root, "resolution_height").text = str(current_resolution[1])
        ET.SubElement(root, "refresh_rate").text = str(current_refresh_rate)
        
        tree = ET.ElementTree(root)
        tree.write("config.xml")
    except Exception as e:
        raise RuntimeError(f"Erro ao salvar configuração: {str(e)}")

def load_config():
    global current_app_path, current_resolution, current_refresh_rate
    try:
        if os.path.exists("config.xml"):
            tree = ET.parse("config.xml")
            root = tree.getroot()
            
            current_app_path = root.find("app_path").text
            current_resolution = (int(root.find("resolution_width").text), int(root.find("resolution_height").text))
            current_refresh_rate = int(root.find("refresh_rate").text)
    except Exception as e:
        raise RuntimeError(f"Erro ao carregar configuração: {str(e)}")

def monitor_app(app_path, width, height, refresh_rate, terminal):
    global current_app_path, current_resolution, current_refresh_rate, stop_on_close, monitoring_active
    app_name = os.path.basename(app_path).lower()
    app_running = False
    
    monitoring_active = True
    while monitoring_active:
        try:
            new_app_running = False
            for proc in psutil.process_iter(['name']):
                if proc.info['name'].lower() == app_name:
                    new_app_running = True
                    break
            
            if new_app_running:
                if not app_running:
                    msg = f"{app_name} está rodando! Alterando resolução para {width}x{height} a {refresh_rate}Hz...\n"
                    terminal.insert(tk.END, msg)
                    set_resolution(width, height, refresh_rate)
                    current_app_path = app_path
                    current_resolution = (width, height)
                    current_refresh_rate = refresh_rate
                    app_running = True
            else:
                if app_running:
                    msg = f"{app_name} não está rodando. Restaurando configuração original.\n"
                    terminal.insert(tk.END, msg)
                    reset_resolution()
                    
                    if stop_on_close:
                        msg = "O monitoramento foi interrompido porque o aplicativo foi fechado e a opção para parar o monitoramento automaticamente está selecionada.\n"
                        terminal.insert(tk.END, msg)
                        terminal.see(tk.END)
                        terminal.update()
                        break
                    app_running = False
            
            terminal.see(tk.END)
            terminal.update()
            time.sleep(5)
        except Exception as e:
            terminal.insert(tk.END, f"Erro: {str(e)}\n")
            terminal.see(tk.END)
            terminal.update()
    
    save_config()
    terminal.insert(tk.END, "Monitoramento interrompido.\n")
    terminal.see(tk.END)
    terminal.update()

def start_monitoring():
    global monitor_thread
    try:
        resolution = entry_resolution.get().strip().split('x')
        if len(resolution) != 2 or not resolution[0].isdigit() or not resolution[1].isdigit():
            raise ValueError("Resolução inválida. Use o formato Largura x Altura.")

        width, height = map(int, resolution)
        refresh_rate = int(entry_refresh_rate.get().replace('Hz', '').strip())

        if width <= 0 or height <= 0 or refresh_rate <= 0:
            raise ValueError("Largura, altura e taxa de atualização devem ser valores positivos.")

        if monitor_thread and monitor_thread.is_alive():
            stop_monitoring()

        monitor_thread = threading.Thread(target=monitor_app, args=(current_app_path, width, height, refresh_rate, terminal))
        monitor_thread.daemon = True
        monitor_thread.start()
        
        terminal.insert(tk.END, f"Monitoramento iniciado para {os.path.basename(current_app_path)} com resolução {width}x{height} a {refresh_rate}Hz.\n")
        terminal.see(tk.END)
        terminal.update()
    except ValueError as ve:
        terminal.insert(tk.END, f"Erro de validação: {ve}\n")
    except Exception as e:
        terminal.insert(tk.END, f"Erro ao iniciar o monitoramento: {str(e)}\n")

def select_app_path():
    global current_app_path

    messagebox.showinfo("Trocar Aplicativo", "Selecione um novo caminho para o aplicativo. As configurações atuais serão salvas.")
    
    app_path = filedialog.askopenfilename(filetypes=[("Executable files", "*.exe"), ("All files", "*.*")])
    if app_path:
        current_app_path = app_path
        terminal.insert(tk.END, f"Aplicativo trocado para: {current_app_path}\n")
        terminal.see(tk.END)
        terminal.update()

def toggle_stop_on_close():
    global stop_on_close
    stop_on_close = stop_on_close_var.get()

def stop_monitoring():
    global monitoring_active
    if monitoring_active:
        monitoring_active = False
        if monitor_thread:
            monitor_thread.join()
        terminal.insert(tk.END, "Monitoramento interrompido pelo usuário.\n")
        terminal.see(tk.END)
        terminal.update()

def close_app():
    if monitoring_active:
        if messagebox.askokcancel("Confirmar Fechamento", "O monitoramento está ativo. Deseja interrompê-lo antes de fechar o aplicativo?"):
            stop_monitoring()
    root.quit()

load_config()

root = tk.Tk()
root.title("BDResolution")

root.resizable(False, False)

tk.Label(root, text="Resolução:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
entry_resolution = tk.Entry(root, width=20)
entry_resolution.grid(row=0, column=1, padx=5, pady=5)
entry_resolution.insert(0, f"{current_resolution[0]}x{current_resolution[1]}")

tk.Label(root, text="Taxa de Atualização:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
entry_refresh_rate = tk.Entry(root, width=10)
entry_refresh_rate.grid(row=1, column=1, padx=5, pady=5)
entry_refresh_rate.insert(0, f"{current_refresh_rate}Hz")

stop_on_close_var = tk.BooleanVar(value=stop_on_close)
tk.Checkbutton(root, text="Parar monitoramento automaticamente quando o aplicativo for fechado", variable=stop_on_close_var, command=toggle_stop_on_close).grid(row=2, column=0, columnspan=2, padx=5, pady=10)

terminal = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=20)
terminal.grid(row=3, column=0, columnspan=3, padx=5, pady=10)

button_frame = tk.Frame(root)
button_frame.grid(row=4, column=0, columnspan=3, padx=5, pady=10)

start_button = tk.Button(button_frame, text="Iniciar", command=start_monitoring)
start_button.grid(row=0, column=0, padx=5)

stop_button = tk.Button(button_frame, text="Parar", command=stop_monitoring)
stop_button.grid(row=0, column=1, padx=5)

select_button = tk.Button(button_frame, text="Trocar Aplicativo", command=select_app_path)
select_button.grid(row=0, column=2, padx=5)

close_button = tk.Button(button_frame, text="Fechar", command=close_app)
close_button.grid(row=0, column=3, padx=5)

root.mainloop()
