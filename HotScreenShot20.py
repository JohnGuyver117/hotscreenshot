import pyautogui
import os
import time
import threading
import customtkinter as ctk
import subprocess
from tkinter import filedialog, Canvas, scrolledtext
from fpdf import FPDF

class ScreenshotApp:
    def __init__(self, master):
        self.master = master
        master.title("Hot Screen Shooter versie 0.9")

        # Initialisatie van variabelen
        self.screenshot_count = 0
        self.screenshots = []
        self.running = False  # Toestand om te zien of de sessie actief is
        self.screenshot_region = None  # Gebied voor screenshots
        self.delay = 5  # Standaardvertraging
        self.timer_thread = None
        
        #Scherm opbouw
        ctk.set_appearance_mode("System")  # Kies tussen "Light", "Dark", "System"
        ctk.set_default_color_theme("blue")  # Kies een kleurthema
        
        ico_path = "favicon.ico"  # Vervang dit door het pad naar je icoonbestand
        master.iconbitmap(ico_path)

        # Hoofdframe
        self.main_frame = ctk.CTkFrame(master)
        self.main_frame.pack(padx=20, pady=20)

        # Doelmap
        self.label_directory = ctk.CTkLabel(self.main_frame, text="Doelmap:")
        self.label_directory.grid(row=0, column=0, sticky='w',pady=10)

        self.entry_directory = ctk.CTkEntry(self.main_frame, width=300)
        self.entry_directory.grid(row=0, column=1, sticky='w', padx=5)

        self.button_browse = ctk.CTkButton(self.main_frame, text="Bladeren", command=self.browse_directory)
        self.button_browse.grid(row=0, column=1, sticky='w', padx=350)

        # Naam van de sessie
        self.label_session_name = ctk.CTkLabel(self.main_frame, text="Naam van de screenshotsessie:")
        self.label_session_name.grid(row=1, column=0, sticky='w')

        self.entry_session_name = ctk.CTkEntry(self.main_frame, width=300)
        self.entry_session_name.grid(row=1, column=1, sticky='w', padx=5)

        # Selecteer methode
        self.label_timing = ctk.CTkLabel(self.main_frame, text="Selecteer methode:")
        self.label_timing.grid(row=2, column=0, sticky='w',pady=10)

        self.var_timing = ctk.StringVar(value='timed') #standaard is Timed
        self.radio_hotkey = ctk.CTkRadioButton(self.main_frame, text='Sneltoets "S"', variable=self.var_timing, value='hotkey')
        self.radio_hotkey.grid(row=2, column=1, sticky='w',pady=10)
        self.radio_timed = ctk.CTkRadioButton(self.main_frame, text='Getimed', variable=self.var_timing, value='timed')
        self.radio_timed.grid(row=2, column=1, sticky='w',padx=120, pady=10)

        # Delay for screenshots
        self.label_delay = ctk.CTkLabel(self.main_frame, text="Neem screenshot elke " + str(self.delay) + " seconden:")
        self.label_delay.grid(row=4, column=0, sticky='w')

        self.entry_delay = ctk.CTkEntry(self.main_frame, width=50)
        self.entry_delay.insert(0, str(self.delay))
        self.entry_delay.grid(row=4, column=1, sticky='w')

        # Timer label
        self.timer_label = ctk.CTkLabel(self.main_frame, text="Volgende screenshot in: 5 seconden", font=("Helvetica", 14))
        self.timer_label.grid(row=4, column=1, sticky='w', padx=70)

        # Buttons
        self.button_start = ctk.CTkButton(self.main_frame, text="Start Sessie", command=self.start_session)
        self.button_start.grid(row=5, column=0, padx=5, pady=15, sticky='w')

        self.button_stop = ctk.CTkButton(self.main_frame, text="Stop Sessie", command=self.stop_session, state=ctk.DISABLED)
        self.button_stop.grid(row=5, column=1, pady=5, sticky='w')

        self.button_take_screenshot = ctk.CTkButton(self.main_frame, text="Neem Screenshot (s)", command=self.take_screenshot)
        self.button_take_screenshot.grid(row=5, column=1, padx=160, sticky='w')

        self.button_new_selection = ctk.CTkButton(self.main_frame, text="Nieuwe selectie maken (n)", command=self.open_selection)
        self.button_new_selection.grid(row=6, column=0, sticky='w', padx=5)

        self.button_new_selection_screenshot = ctk.CTkButton(self.main_frame, text="Nieuwe selectie en screenshot Maken", command=self.open_selection)
        self.button_new_selection_screenshot.grid(row=6, column=1, sticky='w')

        self.button_generate_pdf = ctk.CTkButton(self.main_frame, text="Genereer PDF (g)", command=self.create_pdf)
        self.button_generate_pdf.grid(row=7, column=0, padx=5, pady=5, sticky='w')

        self.button_open_pdf = ctk.CTkButton(self.main_frame, text="Open PDF (o)", command=self.open_pdf)
        self.button_open_pdf.grid(row=7, column=1, pady=5, sticky='w')

        # Logging Textbox
        self.log_text = scrolledtext.ScrolledText(self.main_frame, width=60, height=10, state='disabled')
        self.log_text.grid(row=8, column=0, columnspan=3, padx=5, pady=5, sticky='w')

        # Copyright
        current_time = time.localtime()
        if current_time.tm_year > 2025:
            copyrightTekst = "Copyright: J.P. Kloosterman / JohnGuyver117 (MIT license) 2025" + str(current_time.tm_year)  + "."
        else:
            copyrightTekst = "Copyright: J.P. Kloosterman / JohnGuyver117 (MIT license) 2025."
        self.label_copyright = ctk.CTkLabel(self.main_frame, text=copyrightTekst)
        self.label_copyright.grid(row=9, column=1)

        # Bind de sneltoets voor screenshots
        self.master.bind('<s>', lambda event: self.take_screenshot())
        self.master.bind('<S>', lambda event: self.take_screenshot())

        # Bind de sneltoets voor Nieuwe Secletie
        self.master.bind('<n>', lambda event: self.open_selection())
        self.master.bind('<N>', lambda event: self.open_selection())

        # Bind de sneltoets voor PDF openen
        self.master.bind('<o>', lambda event: self.open_pdf())
        self.master.bind('<O>', lambda event: self.open_pdf())

        # Bind de sneltoets voor PDF generatie
        self.master.bind('<g>', lambda event: self.create_pdf())
        self.master.bind('<G>', lambda event: self.create_pdf())

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.entry_directory.delete(0, ctk.END)
            self.entry_directory.insert(0, directory)

    def log(self, message):
        """Voeg een bericht toe aan het logvenster."""
        self.log_text.configure(state='normal')
        self.log_text.insert(ctk.END, message + '\n')
        self.log_text.yview(ctk.END)  # Scroll naar beneden om het nieuwste bericht zichtbaar te maken
        self.log_text.configure(state='disabled')

    def take_screenshot(self):
        """Neem een screenshot van het geselecteerde gebied."""
        if self.screenshot_region:
            img = pyautogui.screenshot(region=self.screenshot_region)
        else:
            img = pyautogui.screenshot()

        screenshot_name = f"{self.entry_session_name.get()}_{self.screenshot_count + 1}.png"
        screenshot_path = os.path.join(self.entry_directory.get(), screenshot_name)
        img.save(screenshot_path)
        self.screenshots.append(screenshot_path)
        self.log(f'Screenshot opgeslagen als: {screenshot_path}')
        self.screenshot_count += 1

    def timed_screenshot_session(self):
        """Start een getimede screenshot sessie."""
        #opletten dat sessie wel gestart moet zijn.
        self.running = True
        while self.running:
            for i in range(self.delay, 0, -1):
                if not self.running:  # Direct stoppen als de sessie is gestopt
                    return
                self.timer_label.configure(text=f"Timer: {i}")
                self.master.update()
                time.sleep(1)  # Wacht een seconde

            # Neem de screenshot
            self.take_screenshot()

    def start_session(self):
        """Start de screenshot sessie."""
        self.screenshot_count = 0
        self.screenshots.clear()
        self.button_stop.configure(state=ctk.NORMAL)  # Maak de stopknop actief
        self.button_new_selection.configure(state=ctk.NORMAL)  # Maak de nieuwe selectieknoop actief
        self.button_take_screenshot.configure(state=ctk.NORMAL)  # Maak de neem screenshot knop actief

        # Haal de vertraging op
        self.delay = int(self.entry_delay.get())

        # Start de screenshot sessie in een nieuwe thread
        self.running = True
        self.timer_thread = threading.Thread(target=self.timed_screenshot_session, daemon=True)
        self.timer_thread.start()

        # Open het selectievenster om het gebied te selecteren
        self.open_selection()

    def stop_session(self):
        """Stop de screenshot sessie."""
        self.running = False  # Stop de sessie
        self.button_stop.configure(state=ctk.DISABLED)  # Deactiveer de stopknop
        self.button_new_selection.configure(state=ctk.DISABLED)  # Deactiveer de nieuwe selectieknoop
        self.button_take_screenshot.configure(state=ctk.DISABLED)  # Deactiveer de neem screenshot knop
        self.log("Sessie gestopt.")

    def open_selection(self):
        """Open het selectievenster."""
        SelectionWindow(self)

    def create_pdf(self):
        """Genereer een PDF met de gemaakte screenshots."""
        if not self.screenshots:
            self.log("Geen screenshots genomen om toe te voegen aan PDF.")
            return

        pdf = FPDF()
        for screenshot in self.screenshots:
            if os.path.exists(screenshot):
                pdf.add_page()
                pdf.image(screenshot, x=10, y=10, w=190)  # Pas de afmetingen aan
            else:
                self.log(f"Screenshot niet gevonden: {screenshot}")

        pdf_filename = os.path.join(self.entry_directory.get(), f"{self.entry_session_name.get()}.pdf")
        pdf.output(pdf_filename)
        self.log(f'PDF opgeslagen als: {pdf_filename}')

    def open_pdf(self):
        """Open de PDF met de gemaakte screenshots."""
        pdf_filename = os.path.join(self.entry_directory.get(), f"{self.entry_session_name.get()}.pdf")
        
        # Open de PDF met de standaard PDF-viewer
        try:
            subprocess.Popen([pdf_filename], shell=True)
            self.log(f'PDF geopend: {pdf_filename}')
        except Exception as e:
            self.log(f'Fout bij het openen van de PDF: {e}')

    def on_closing(self):
        """Bij het sluiten van de applicatie, genereer een PDF en sluit de applicatie."""
        self.create_pdf()
        self.master.destroy()


class SelectionWindow:
    def __init__(self, app):
        self.app = app
        self.window = ctk.CTkToplevel()
        self.window.title("Selecteer Screenshot Gebied")

        # Maak de canvas om het selectievenster te tekenen
        self.canvas = Canvas(self.window, cursor="cross", bg="gray")
        self.canvas.pack(fill=ctk.BOTH, expand=True)

        # Maak het venster semi-transparant
        self.window.wm_attributes("-alpha", 0.5)
        self.window.attributes('-fullscreen', True)
        self.window.bind("<Escape>", self.cancel)  # Esc om te annuleren

        # Voor recto-coördinaten
        self.start_x = None
        self.start_y = None
        self.rect = None

        # Bind muisklikken
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def on_button_press(self, event):
        """Reageer op de druk op de muisknop, start de selectie van het gebied."""
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red")

    def on_mouse_drag(self, event):
        """Werk de rechthoek bij terwijl de muis wordt gesleept."""
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_button_release(self, event):
        """Maak een selectie en sluit het venster weer."""
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

        # Verkrijg de coördinaten van de geselecteerde regio
        self.app.screenshot_region = (self.start_x, self.start_y, event.x - self.start_x, event.y - self.start_y)

        # Sluit het selectievenster
        self.window.destroy()

        # Toon het hoofdvenster weer
        self.app.master.deiconify()

    def cancel(self, event):
        """Annuleer de selectie en sluit het selectievenster."""
        self.window.destroy()
        self.app.master.deiconify()  # Toon het hoofdvenster weer

if __name__ == "__main__":
    root = ctk.CTk()
    app = ScreenshotApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
