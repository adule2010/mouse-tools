print("Loading lib")
import sys
import os
import datetime
import traceback
import tkinter as tk
from tkinter import ttk
import win32api, win32con
import keyboard
import threading
import time
import random
import math
import darkdetect
from PIL import Image, ImageTk
import json
import webbrowser
print("Loading log feature")
LOG_FILE = None

def setup_logging():
    global LOG_FILE
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(log_dir, exist_ok=True)

    LOG_FILE = os.path.join(log_dir, 'log.txt')

    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        f.write(f"Log started: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    class LoggerWriter:
        def __init__(self, filename):
            self.filename = filename
            self.stdout = sys.stdout if sys.stdout else None
            self.stderr = sys.stderr if sys.stderr else None

        def write(self, message):
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(self.filename, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {message}\n")
                f.flush()
        
            if self.stdout:
                try:
                    self.stdout.write(message)
                except Exception:
                    pass

        def flush(self):
            if self.stdout:
                try:
                    self.stdout.flush()
                except Exception:
                    pass


def log_message(message):
    """
    Log a message to the log file.
    If logging hasn't been set up, it will set up logging first.
    """
    global LOG_FILE
    if LOG_FILE is None:
        setup_logging()
    
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {message}\n")
            f.flush()
        print(message)
    except Exception as e:
        print(f"Error logging message: {e}")
        print(message)

log_message("Log system is runing")
log_message("Program is starting")

class AutoClickerWithJigglerGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Mouse Tools")
        self.master.geometry("350x600")
        self.master.resizable(False, False)

        self.is_dark_mode = darkdetect.isDark()
        self.setup_theme()

        self.notebook = ttk.Notebook(master)
        self.notebook.pack(expand=True, fill='both')

        self.auto_clicker_tab = ttk.Frame(self.notebook)
        self.jiggler_tab = ttk.Frame(self.notebook)
        self.settings_tab = ttk.Frame(self.notebook)
        self.info_tab = ttk.Frame(self.notebook)
        self.donate_tab = ttk.Frame(self.notebook)
        self.feedback_tab = ttk.Frame(self.notebook)

        # Default values
        self.clicking = False
        self.jiggling = False
        self.click_speed = 1
        self.mouse_button = "left"  
        self.jiggle_speed = 0.2
        self.speed_change_step = 10
        self.jiggler_mode = tk.StringVar(value="Circle")  
        
        # Languages
        self.language_names = {
            "cs": "Čeština",
            "en": "English"
        }
        self.language = tk.StringVar()
        try:
            with open('data.json', 'r') as f:
                settings = json.load(f)
                saved_language = settings.get('language', 'en')
                if saved_language in self.language_names.values():
                    for code, name in self.language_names.items():
                        if name == saved_language:
                            saved_language = code
                            break
                self.language.set(saved_language)
        except (FileNotFoundError, json.JSONDecodeError):
            self.language.set('en')

        def on_language_change(*args):
            current_language = self.language.get()
            if current_language in self.language_names.values():
                for code, name in self.language_names.items():
                    if name == current_language:
                        self.language.set(code)
                        break
            
            self.update_language()

        self.language.trace_add('write', on_language_change)

        self.translations = {
            "cs": {
                "auto_clicker": "Auto Clicker",
                "jiggler": "Jiggler",
                "settings": "Nastavení",
                "info": "Info",
                "donate": "Darovat",
                "feedback": "Zpětná vazba",
                "mouse_button": "levý",
                "jiggler_mode": "Kruh",
                "hotkeys": """Klávesové zkratky:
F6: Zapnout/Zastavit Autoclicker
F7: Zvýšit rychlost
F8: Snížit rychlost
F9: Zapnout/Zastavit Jiggler
F10: Přepnout mezi levým a pravým tlačítkem myši

Verze: 1.0.0""",
                "donate_text": """Pokud se vám program líbí a chcete podpořit jeho vývoj, 
můžete přispět libovolnou částkou prostřednictvím PayPal.

Vaše podpora pomáhá:
- Udržovat a vylepšovat tento nástroj
- Vyvíjet nové funkce
- Opravovat chyby
- Podpořit vývojáře

Děkujeme za vaši štědrost!""",
                "click_speed": "Rychlost klikání (ms)",
                "start_auto_clicker": "Zapnout Autoclicker",
                "stop_auto_clicker": "Zastavit Autoclicker",
                "jiggler_speed": "Rychlost jiggleru (s)",
                "start_jiggler": "Start Jiggler",
                "stop_jiggler": "Stop Jiggler",
                "speed_change_step": "Změna rychlosti při stisku F7/F8 (ms)",
                "save_settings": "Uložit všechna nastavení",
                "open_feedback_form": "Otevřít formulář",
                "feedback_text": """Chcete-li poskytnout zpětnou vazbu nebo nahlásit chybu, 
klikněte na tlačítko níže a vyplňte formulář.

Vážíme si vašeho názoru""",
                "keyboard_shortcuts": "Klávesové zkratky:",
                "language": "Language:",
                "f6_shortcut": "F6: Zapnout/Zastavit Autoclicker",
                "f7_shortcut": "F7: Zvýšit rychlost",
                "f8_shortcut": "F8: Snížit rychlost",
                "f9_shortcut": "F9: Zapnout/Zastavit Jiggler",
                "f10_shortcut": "F10: Přepnout mezi levým a pravým tlačítkem myši",
                "version": "Verze:",
                "donate": "Darovat",
                "donate_text_start": "Pokud se vám program líbí",
                "feedback_text_start": "Chcete-li poskytnout zpětnou vazbu",
                "support_helps": "Vaše podpora pomáhá:",
                "thank_you": "Děkujeme za vaši štědrost!",
                "appreciate_feedback": "Vážíme si vašeho názoru",
                "maintain_tool": "Udržovat a vylepšovat tento nástroj",
                "develop_features": "Vyvíjet nové funkce",
                "fix_bugs": "Opravovat chyby",
                "support_developer": "Podpořit vývojáře"
            },
            "en": {
                "auto_clicker": "Auto Clicker",
                "jiggler": "Jiggler",
                "settings": "Settings",
                "info": "Info",
                "donate": "Donate",
                "feedback": "Feedback",
                "mouse_button": "left",
                "jiggler_mode": "Circle",
                "hotkeys": """Hotkeys:
F6: Toggle Auto Clicker
F7: Increase Speed
F8: Decrease Speed
F9: Toggle Jiggler
F10: Switch Mouse Button

Version 1.0.0""",
                "donate_text": """If you like the program and want to support its development, 
you can contribute any amount through PayPal.

Your support helps:
- Maintain and improve this tool
- Develop new features
- Fix bugs
- Support the developer

Thank you for your generosity!""",
                "click_speed": "Click Speed (ms)",
                "start_auto_clicker": "Start Auto Clicker",
                "stop_auto_clicker": "Stop Auto Clicker",
                "jiggler_speed": "Jiggler Speed (s)",
                "start_jiggler": "Start Jiggler",
                "stop_jiggler": "Stop Jiggler",
                "speed_change_step": "Speed Change Step (ms)",
                "save_settings": "Save All Settings",
                "open_feedback_form": "Open Feedback Form",
                "feedback_text": """If you want to provide feedback or report a bug, 
click the button below and fill out the form.

We appreciate your feedback""",
                "keyboard_shortcuts": "Keyboard Shortcuts:",
                "language": "Language:",
                "f6_shortcut": "F6: Start/Stop Auto Clicker",
                "f7_shortcut": "F7: Increase Speed",
                "f8_shortcut": "F8: Decrease Speed",
                "f9_shortcut": "F9: Start/Stop Jiggler",
                "f10_shortcut": "F10: Switch between Left and Right Mouse Button",
                "version": "Version:",
                "donate": "Donate",
                "donate_text_start": "If you like the program",
                "feedback_text_start": "If you want to provide feedback",
                "support_helps": "Your support helps:",
                "thank_you": "Thank you for your generosity!",
                "appreciate_feedback": "We appreciate your feedback",
                "maintain_tool": "Maintain and improve this tool",
                "develop_features": "Develop new features",
                "fix_bugs": "Fix bugs",
                "support_developer": "Support the developer"
            }
        }

        self.load_settings()

        self.notebook.add(self.auto_clicker_tab, text=self.translations[self.language.get()]["auto_clicker"])
        self.notebook.add(self.jiggler_tab, text=self.translations[self.language.get()]["jiggler"])
        self.notebook.add(self.settings_tab, text=self.translations[self.language.get()]["settings"])
        self.notebook.add(self.info_tab, text=self.translations[self.language.get()]["info"])
        self.notebook.add(self.donate_tab, text=self.translations[self.language.get()]["donate"])
        self.notebook.add(self.feedback_tab, text=self.translations[self.language.get()]["feedback"])

        self.setup_auto_clicker_tab()
        self.setup_jiggler_tab()
        self.setup_settings_tab()
        self.setup_info_tab()
        self.setup_donate_tab()
        self.setup_feedback_tab()

        self.setup_hotkeys()

        self.dvd_mode = False
        self.dvd_x = 0
        self.dvd_y = 0
        self.dvd_dx = 5
        self.dvd_dy = 5
        self.screen_width = win32api.GetSystemMetrics(0)
        self.screen_height = win32api.GetSystemMetrics(1)

    def load_settings(self):
        settings_path = os.path.join(os.path.dirname(__file__), 'data.json')
        try:
            with open(settings_path, 'r') as f:
                settings = json.load(f)
            
            self.click_speed = settings.get('click_speed', 1)
            self.mouse_button = settings.get('mouse_button', 'levý')
            self.jiggle_speed = settings.get('jiggle_speed', 0.2)
            self.speed_change_step = settings.get('speed_change', 10)
            self.jiggler_mode.set(settings.get('jiggler_mode', 'Kruh'))
            
            language = settings.get('language', 'cs')
            self.language.set(language)
        except (json.JSONDecodeError, IOError, FileNotFoundError):
            # Defualt lang
            self.language.set('en')

    def save_settings(self):
        try:
            click_speed = float(self.click_speed_entry.get())
            jiggle_speed = float(self.jiggle_speed_entry.get())
            speed_change_step = int(self.step_entry.get())
        except ValueError:
            click_speed = self.click_speed
            jiggle_speed = self.jiggle_speed
            speed_change_step = self.speed_change_step

        settings = {
            'click_speed': click_speed,
            'mouse_button': self.mouse_button,
            'jiggle_speed': jiggle_speed,
            'speed_change': speed_change_step,
            'jiggler_mode': self.jiggler_mode.get(),
            'language': self.language.get()
        }

        settings_path = os.path.join(os.path.dirname(__file__), 'data.json')
        with open(settings_path, 'w') as f:
            json.dump(settings, f, indent=4)

        self.click_speed = click_speed
        self.jiggle_speed = jiggle_speed
        self.speed_change_step = speed_change_step

    def setup_theme(self):
        bg_color = '#363636' if self.is_dark_mode else '#ffffff'
        fg_color = '#ffffff' if self.is_dark_mode else '#000000'
        entry_bg = '#333333' if self.is_dark_mode else '#f5f5f5'

        self.style = ttk.Style()
        self.style.configure('TNotebook', background=bg_color)
        self.style.configure('TFrame', background=bg_color)
        self.style.configure('TLabel', background=bg_color, foreground=fg_color)
        self.master.configure(bg=bg_color)

    def setup_auto_clicker_tab(self):
        speed_label = ttk.Label(self.auto_clicker_tab, text=self.translations[self.language.get()]["click_speed"])
        speed_label.pack(pady=(20, 5))

        self.click_speed_entry = tk.Entry(self.auto_clicker_tab, width=10, justify='center')
        self.click_speed_entry.insert(0, str(self.click_speed))
        self.click_speed_entry.pack(pady=5)

        self.button_var = tk.StringVar(value="left")
        button_menu = ttk.OptionMenu(self.auto_clicker_tab, self.button_var, "left", "left", "right")
        button_menu.pack(pady=5)

        self.click_button = ttk.Button(self.auto_clicker_tab, text=self.translations[self.language.get()]["start_auto_clicker"], command=self.toggle_clicking)
        self.click_button.pack(pady=20)

    def setup_jiggler_tab(self):
        modes = ["Circle", "Random", "Square", "DVD"]
        mode_menu = ttk.OptionMenu(self.jiggler_tab, self.jiggler_mode, self.jiggler_mode.get(), *modes)
        mode_menu.pack(pady=20)

        speed_label = ttk.Label(self.jiggler_tab, text=self.translations[self.language.get()]["jiggler_speed"])
        speed_label.pack(pady=(20, 5))

        self.jiggle_speed_entry = tk.Entry(self.jiggler_tab, width=10, justify='center')
        self.jiggle_speed_entry.insert(0, str(self.jiggle_speed))
        self.jiggle_speed_entry.pack(pady=5)

        self.jiggle_button = ttk.Button(self.jiggler_tab, text=self.translations[self.language.get()]["start_jiggler"], command=self.toggle_jiggling)
        self.jiggle_button.pack(pady=20)

    def setup_settings_tab(self):
        step_label = ttk.Label(self.settings_tab, text=self.translations[self.language.get()]["speed_change_step"])
        step_label.pack(pady=(20, 5))

        self.step_entry = tk.Entry(self.settings_tab, width=10, justify='center')
        self.step_entry.insert(0, str(self.speed_change_step))
        self.step_entry.pack(pady=5)

        save_button = ttk.Button(self.settings_tab, text=self.translations[self.language.get()]["save_settings"], command=self.save_settings)
        save_button.pack(pady=10)

        language_label = ttk.Label(self.settings_tab, text=self.translations[self.language.get()]["language"])
        language_label.pack(pady=(20, 5))

        language_menu = ttk.OptionMenu(self.settings_tab, 
                                       self.language, 
                                       self.language_names[self.language.get()], 
                                       *self.language_names.values())
        language_menu.pack(pady=5)

        def on_language_change(*args):
            current_language = self.language.get()
            if current_language in self.language_names.values():
                for code, name in self.language_names.items():
                    if name == current_language:
                        self.language.set(code)
                        break
            
            self.update_language()

    def setup_info_tab(self):
        info_text = self.translations[self.language.get()]["hotkeys"]
        info_label = ttk.Label(self.info_tab, text=info_text, justify=tk.LEFT)
        info_label.pack(pady=20)

    def setup_donate_tab(self):
        donate_text = self.translations[self.language.get()]["donate_text"]

        text_widget = tk.Text(self.donate_tab, wrap=tk.WORD, height=10, width=50, 
                               font=('Arial', 10), padx=20, pady=20)
        text_widget.insert(tk.END, donate_text)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(pady=(20, 10))

        donate_button = ttk.Button(self.donate_tab, 
                                   text=self.translations[self.language.get()]["donate"], 
                                   command=self.open_paypal_donation)
        donate_button.pack(pady=20)

    def setup_feedback_tab(self):
        feedback_text = self.translations[self.language.get()]["feedback_text"]

        feedback_label = ttk.Label(self.feedback_tab, text=feedback_text, justify=tk.LEFT)
        feedback_label.pack(pady=20)

        feedback_button = ttk.Button(self.feedback_tab, 
                                     text=self.translations[self.language.get()]["open_feedback_form"], 
                                     command=self.open_feedback_form)
        feedback_button.pack(pady=20)

    def setup_hotkeys(self):
        keyboard.add_hotkey('f6', self.toggle_clicking)
        keyboard.add_hotkey('f7', lambda: self.change_speed(-self.speed_change_step))
        keyboard.add_hotkey('f8', lambda: self.change_speed(self.speed_change_step))
        keyboard.add_hotkey('f9', self.toggle_jiggling)
        keyboard.add_hotkey('f10', self.toggle_mouse_button)

    def toggle_clicking(self):
        if not self.clicking:
            self.clicking = True
            self.click_thread = threading.Thread(target=self.auto_click, daemon=True)
            self.click_thread.start()
            
            self.click_button.config(text=self.translations[self.language.get()]["stop_auto_clicker"])
        else:
            self.clicking = False
            if hasattr(self, 'click_thread'):
                self.click_thread.join()
            
            self.click_button.config(text=self.translations[self.language.get()]["start_auto_clicker"])

    def toggle_jiggling(self):
        self.jiggling = not self.jiggling
        if self.jiggling:
            threading.Thread(target=self.jiggle_mouse, daemon=True).start()
            self.jiggle_button.config(text=self.translations[self.language.get()]["stop_jiggler"])
        else:
            self.jiggle_button.config(text=self.translations[self.language.get()]["start_jiggler"])

    def jiggle_mouse(self):
        center_x, center_y = win32api.GetCursorPos()
        radius = 50
        speed = float(self.jiggle_speed_entry.get())
        angle = 0
        step = 0

        while self.jiggling:
            mode = self.jiggler_mode.get()

            if mode == "Circle":
                x = center_x + int(radius * math.cos(angle))
                y = center_y + int(radius * math.sin(angle))
                angle += 0.1

            elif mode == "Square":
                size = 100
                steps_per_side = 20
                distance_per_step = size // steps_per_side

                if step < steps_per_side:
                    x, y = center_x + step * distance_per_step, center_y
                elif step < 2 * steps_per_side:
                    x, y = center_x + size, center_y + (step - steps_per_side) * distance_per_step
                elif step < 3 * steps_per_side:
                    x, y = center_x + size - (step - 2 * steps_per_side) * distance_per_step, center_y + size
                else:
                    x, y = center_x, center_y + size - (step - 3 * steps_per_side) * distance_per_step

                step = (step + 1) % (4 * steps_per_side)

            elif mode == "Random":
                x = center_x + random.randint(-50, 50)
                y = center_y + random.randint(-50, 50)

            elif mode == "DVD":
                self.dvd_x += self.dvd_dx
                self.dvd_y += self.dvd_dy

                if self.dvd_x < 0 or self.dvd_x > self.screen_width:
                    self.dvd_dx *= -1
                if self.dvd_y < 0 or self.dvd_y > self.screen_height:
                    self.dvd_dy *= -1

                x, y = self.dvd_x, self.dvd_y

            win32api.SetCursorPos((x, y))
            time.sleep(speed)

    def auto_click(self):
        while self.clicking:
            self.fast_click()
            time.sleep(float(self.click_speed_entry.get()) / 1000)

    def fast_click(self):
        x, y = win32api.GetCursorPos()
        if self.mouse_button == "left":
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
        elif self.mouse_button == "right":
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, x, y, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, x, y, 0, 0)

    def change_speed(self, amount):
        try:
            current_speed = int(self.click_speed_entry.get())
            new_speed = max(1, current_speed + amount)
            self.click_speed_entry.delete(0, tk.END)
            self.click_speed_entry.insert(0, str(new_speed))
        except ValueError:
            pass

    def toggle_mouse_button(self):
        if self.mouse_button == "left":
            self.mouse_button = "right"
            self.button_var.set("right")
        else:
            self.mouse_button = "left"
            self.button_var.set("left")

        print(f"{self.mouse_button}")

    def open_paypal_donation(self):
        donation_url = "https://www.paypal.com/donate/?hosted_button_id=92H53ECRCTXK8"
        webbrowser.open(donation_url)

    def open_feedback_form(self):
        feedback_url = "https://docs.google.com/forms/d/1bNI0kServ5rZZeYZ-RsWOk6YJz3qhR06RH-WESrtG4w/"
        webbrowser.open(feedback_url)

    def update_all_widgets_language(self, parent, current_language):
        """
        Recursively update language for all widgets in a given parent
        """
        log_message(f"Updating language for {parent} to {current_language}")
        
        widgets_processed = 0
        
        text_mappings = {
            "labels_buttons": [
                {
                    "cs_texts": [
                        "Rychlost klikání (ms):", "Rychlost jiggleru (s):", 
                        "Změna rychlosti při stisku F7/F8 (ms)", 
                        "Zapnout Autoclicker", "Zastavit Autoclicker", 
                        "Zapnout Jiggler", "Zastavit Jiggler", 
                        "Uložit všechna nastavení", "Otevřít formulář",
                        "Klávesové zkratky:", "Language:",
                        "F6: Zapnout/Zastavit Autoclicker",
                        "F7: Zvýšit rychlost", "F8: Snížit rychlost",
                        "F9: Zapnout/Zastavit Jiggler", 
                        "F10: Přepnout mezi levým a pravým tlačítkem myši",
                        "Verze:", "Darovat", "Start Jiggler"
                    ],
                    "en_texts": [
                        "Click Speed (ms):", "Jiggler Speed (s):", 
                        "Speed Change Step (ms)", 
                        "Start Auto Clicker", "Stop Auto Clicker", 
                        "Start Jiggler", "Stop Jiggler", 
                        "Save All Settings", "Open Feedback Form",
                        "Keyboard Shortcuts:", "Language:",
                        "F6: Start/Stop Auto Clicker",
                        "F7: Increase Speed", "F8: Decrease Speed",
                        "F9: Start/Stop Jiggler", 
                        "F10: Switch between Left and Right Mouse Button",
                        "Version:", "Donate", "Start Jiggler"
                    ],
                    "translation_keys": [
                        "click_speed", "jiggler_speed", "speed_change_step", 
                        "start_auto_clicker", "stop_auto_clicker", 
                        "start_jiggler", "stop_jiggler", 
                        "save_settings", "open_feedback_form",
                        "keyboard_shortcuts", "language",
                        "f6_shortcut", "f7_shortcut", "f8_shortcut", 
                        "f9_shortcut", "f10_shortcut",
                        "version", "donate", "start_jiggler"
                    ]
                }
            ],
            "text_descriptions": [
                {
                    "cs_texts": [
                        "Pokud se vám program líbí", 
                        "Chcete-li poskytnout zpětnou vazbu",
                        "Vaše podpora pomáhá:",
                        "Děkujeme za vaši štědrost!",
                        "Vážíme si vašeho názoru",
                        "Udržovat a vylepšovat tento nástroj",
                        "Vyvíjet nové funkce",
                        "Opravovat chyby",
                        "Podpořit vývojáře"
                    ],
                    "en_texts": [
                        "If you like the program", 
                        "If you want to provide feedback",
                        "Your support helps:",
                        "Thank you for your generosity!",
                        "We appreciate your feedback",
                        "Maintain and improve this tool",
                        "Develop new features",
                        "Fix bugs",
                        "Support the developer"
                    ],
                    "translation_keys": [
                        "donate_text_start", 
                        "feedback_text_start", 
                        "support_helps", 
                        "thank_you", 
                        "appreciate_feedback",
                        "maintain_tool",
                        "develop_features",
                        "fix_bugs",
                        "support_developer"
                    ]
                }
            ]
        }
        
        def translate_text(text, current_language):
            """Helper function to translate individual text"""
            for mapping in text_mappings["labels_buttons"] + text_mappings["text_descriptions"]:
                for i, (cs_text, en_text) in enumerate(zip(mapping["cs_texts"], mapping["en_texts"])):
                    if text.strip() in [cs_text.strip(), en_text.strip()]:
                        return self.translations[current_language][mapping["translation_keys"][i]]
            return text
        
        def update_widget_text(widget, current_language):
            nonlocal widgets_processed
            
            try:
                if isinstance(widget, (ttk.Label, tk.Label, ttk.Button, tk.Button)):
                    original_text = widget.cget('text')
                    new_text = translate_text(original_text, current_language)
                    
                    if original_text != new_text:
                        log_message(f"Updating widget from '{original_text}' to '{new_text}'")
                        widget.config(text=new_text)
                        widgets_processed += 1
                
                elif isinstance(widget, (tk.Text, tk.Label)):
                    content = widget.get('1.0', tk.END).strip() if hasattr(widget, 'get') else widget.cget('text')
                    
                    new_content = content
                    for mapping in text_mappings["text_descriptions"]:
                        for i, (cs_text, en_text) in enumerate(zip(mapping["cs_texts"], mapping["en_texts"])):
                            if cs_text.strip() in new_content or en_text.strip() in new_content:
                                new_content = new_content.replace(
                                    cs_text, 
                                    self.translations[current_language][mapping["translation_keys"][i]]
                                ).replace(
                                    en_text, 
                                    self.translations[current_language][mapping["translation_keys"][i]]
                                )
                    
                    if new_content != content:
                        log_message(f"Updating text from '{content}' to '{new_content}'")
                        
                        if hasattr(widget, 'delete'):
                            widget.delete('1.0', tk.END)
                            widget.insert(tk.END, new_content)
                        else:
                            widget.config(text=new_content)
                        
                        widgets_processed += 1
            except Exception as e:
                log_message(f"Error processing widget {widget}: {e}")
        
        def traverse_widgets(parent_widget):
            nonlocal widgets_processed
            
            for widget in parent_widget.winfo_children():
                update_widget_text(widget, current_language)
                
                if widget.winfo_children():
                    traverse_widgets(widget)
        
        traverse_widgets(parent)
        
        log_message(f"Total widgets processed in {parent}: {widgets_processed}")
        return widgets_processed

    def update_language(self, *args):
        """
        Update the entire application language, including all widgets and tabs
        """
        try:
            current_language = self.language.get()
            log_message(f"Starting language update to: {current_language}")
            

            tabs_to_update = [
                self.auto_clicker_tab, 
                self.jiggler_tab, 
                self.settings_tab, 
                self.info_tab, 
                self.donate_tab, 
                self.feedback_tab
            ]
            
            total_widgets_processed = 0
            
            for tab_frame in tabs_to_update:
                if tab_frame and tab_frame.winfo_exists():
                    try:
                        widgets_in_tab = self.update_all_widgets_language(tab_frame, current_language)
                        total_widgets_processed += widgets_in_tab
                    except Exception as frame_error:
                        log_message(f"Error updating tab {tab_frame}: {frame_error}")
            
            language_vars = {
                "mouse_button": "mouse_button",
                "jiggler_mode": "jiggler_mode"
            }
            
            for var_name, translation_key in language_vars.items():
                try:
                    var = getattr(self, var_name, None)
                    
                    if hasattr(var, 'set'):
                        var.set(self.translations[current_language][translation_key])
                    elif isinstance(var, str):
                        setattr(self, var_name, 
                                self.translations[current_language][translation_key])
                except Exception as var_error:
                    log_message(f"Error updating variable {var_name}: {var_error}")
            
            try:
                if hasattr(self, 'save_settings') and callable(self.save_settings):
                    self.save_settings()
                else:
                    log_message("save_settings method not found or not callable")
            except Exception as save_error:
                log_message(f"Error saving settings: {save_error}")
            
            log_message(f"Total widgets processed across all tabs: {total_widgets_processed}")
            log_message(f"Language update completed to: {current_language}")
            
            if hasattr(self, 'master') and self.master.winfo_exists():
                self.master.update_idletasks()
        
        except Exception as global_error:
            log_message(f"Critical error in language update: {global_error}")


def splash_screen():
    splash = tk.Tk()
    splash.overrideredirect(True)
    
    splash_image = Image.open("splash.png")
    splash_photo = ImageTk.PhotoImage(splash_image)
    
    screen_width = splash.winfo_screenwidth()
    screen_height = splash.winfo_screenheight()
    image_width = splash_image.width
    image_height = splash_image.height
    
    x = (screen_width - image_width) // 2
    y = (screen_height - image_height) // 2
    
    splash.geometry(f"{image_width}x{image_height}+{x}+{y}")
    
    splash_label = tk.Label(splash, image=splash_photo)
    splash_label.image = splash_photo
    splash_label.pack()
    
    splash.update()
    
    splash.after(2000, splash.destroy)
    splash.mainloop()

def main():
    log_file = setup_logging()
    
    log_message("This program is made by Progres Studio")
    log_message(f"Logging to: {log_file}")
    
    splash_screen()
    log_message("Program loaded")
    
    root = tk.Tk()
    root.iconbitmap("favicon.ico")
    
    try:
        app = AutoClickerWithJigglerGUI(root)
        root.mainloop()
    except Exception as e:
        log_message("Critical error occurred:")
        log_message(traceback.format_exc())

if __name__ == "__main__":
    main()