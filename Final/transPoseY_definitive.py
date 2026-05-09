"""
-------------------------------------------------------------------------------
Project: transPoseY.py - Professional Harmonic Transposition & Playback Suite
Version: 1.25.0 (Final Master)
-------------------------------------------------------------------------------
TECHNICAL SPECIFICATIONS:
- Framework: CustomTkinter (UI), Pygame (Audio Backend), Numpy (Synthesis)
- Logic: Full Diatonic & Chromatic transposition engine.
- Tooltips: Dynamic <footer> feedback system on all interactive widgets.
- Accessibility: Scaled for 720p (1280x720) minimum display targets.
- Features: 
    - PEP 3113 Compliant Trigger System.
    - Real-time 2nd-degree repetition guard in Random Arp mode.
    - Bi-layer active focus highlighting (Shift key toggle).
    - Hardened Validation logic for musical root entry.
    - Relative Major/Minor harmonic companion rendering.
-------------------------------------------------------------------------------
"""

import customtkinter as ctk
import numpy as np
import pygame
import threading
import queue
import time
import random
import sys

# Standardized Theme Configuration
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class SoundEngine:
    """
    High-performance audio synthesis engine. 
    Uses a background worker thread to manage playback commands to 
    prevent UI thread blocking and ensure rhythmic precision.
    """
    def __init__(self):
        # Pre-initialize mixer for low latency
        pygame.mixer.pre_init(44100, -16, 2, 1024)
        pygame.init()
        pygame.mixer.set_num_channels(128) 
        
        self.sample_rate = 44100
        self._volume = 0.5
        self.notes_lib = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        self.cached_sounds = {}
        self.active_channels = {} 
        self.cmd_queue = queue.Queue()
        self.stop_thread = False
        
        # Audio Worker Thread
        self.worker_thread = threading.Thread(target=self._audio_worker, daemon=True)
        self.worker_thread.start()

    def _audio_worker(self):
        """Processes audio commands from the thread-safe queue."""
        while not self.stop_thread:
            try:
                # Use a small timeout to allow checking stop_thread flag
                cmd_packet = self.cmd_queue.get(timeout=0.1)
                cmd, data = cmd_packet
                
                if cmd == "START":
                    key_id, sound_obj, loop = data
                    if key_id not in self.active_channels:
                        channel = pygame.mixer.find_channel()
                        if channel:
                            # Use fade_ms to prevent 'clicks' on sudden sound starts
                            channel.play(sound_obj, loops=(-1 if loop else 0), fade_ms=15)
                            self.active_channels[key_id] = channel
                            
                elif cmd == "STOP":
                    key_id = data
                    if key_id in self.active_channels:
                        # Smooth fadeout for musicality
                        self.active_channels[key_id].fadeout(150)
                        del self.active_channels[key_id]
                        
                elif cmd == "PANIC":
                    pygame.mixer.stop()
                    self.active_channels.clear()
                    
            except queue.Empty:
                continue

    def pre_cache_scale(self, scale_data_rows):
        """
        Synthesizes waveforms for the current scale selection.
        This ensures zero-latency playback when the user triggers a note.
        """
        def cache_task():
            new_cache = {}
            for row_idx, row in enumerate(scale_data_rows):
                for col_idx, (note_name, octave_offset) in enumerate(row):
                    root_name = "".join([c for c in note_name if c in "ABCDEFG#"])
                    if root_name not in self.notes_lib: 
                        continue
                    
                    # Logarithmic frequency calculation
                    # A4 = 440Hz reference
                    steps_from_a = self.notes_lib.index(root_name) - self.notes_lib.index('A')
                    total_semitones = steps_from_a + (octave_offset * 12)
                    frequency = 440 * (2 ** (total_semitones / 12))
                    
                    # Generate 0.4s sample
                    duration = 0.4
                    t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
                    # Additive synthesis (Fundamental + 1st Overtone)
                    wave = 0.7 * np.sin(2 * np.pi * frequency * t) + 0.15 * np.sin(4 * np.pi * frequency * t)
                    
                    # Apply amplitude gain
                    master_gain = self._volume * 0.25
                    audio_int16 = (wave * master_gain * 32767).astype(np.int16)
                    
                    # Expand to Stereo
                    stereo_wave = np.ascontiguousarray(np.vstack((audio_int16, audio_int16)).T)
                    new_cache[f"{row_idx}_{col_idx}"] = pygame.sndarray.make_sound(stereo_wave)
            
            self.cached_sounds = new_cache

        threading.Thread(target=cache_task, daemon=True).start()

    def play(self, row, col, key_id, loop=True):
        cache_key = f"{row}_{col}"
        if cache_key in self.cached_sounds:
            self.cmd_queue.put(("START", (key_id, self.cached_sounds[cache_key], loop)))

    def stop(self, key_id):
        self.cmd_queue.put(("STOP", key_id))

    def panic(self):
        self.cmd_queue.put(("PANIC", None))

class TransposeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configuration for 720p Minimum Targets
        self.title("transPoseY.py | Master Harmonic Suite")
        self.geometry("1100x710") 
        self.minsize(1024, 700)
        self.configure(fg_color=("#F0F0F0", "#0D0D0D"))
        
        # Core State
        self.sound_engine = SoundEngine()
        self.chord_buttons = {} 
        self.row_frames = []
        self.pressed_keys_data = [] 
        self.pressed_key_ids = set()
        self.shift_toggle = False 
        
        # Arpeggiator Logic State
        self.arp_enabled = False
        self.arp_random = False
        self.current_bpm = 120
        self.arp_index = 0
        self.last_note_id = None
        self.consecutive_count = 0

        # Master Tooltip Database
        self.HELP_DB = {
            "default": "Ready. Use keys 1-8 for playback. Press [SHIFT] to toggle row focus. Press [ESC] in case of any audio error.",
            "orig_root": "INPUT: Enter the starting musical key (e.g., A, C#, Eb).",
            "targ_root": "INPUT: Enter the desired key to transpose into. Only applicable in Major/Minor transposing modes",
            "bpm_slider": "RHYTHM: Adjusts pulses per minute for the Arpeggiator.",
            "arp_toggle": "SEQUENCER: When ON, held notes will pulse rhythmically. By default, in the order of the keys held down, unless the random toggle has been selected.",
            "rand_toggle": "SHUFFLE: When ON, pulses held notes in a semi-random pattern.",
            "mode_drop": "THEORY: Select between Major, Minor, or Relative harmonic modes.",
            "update_btn": "ENGINE: Re-calculates all scales and updates the audio cache.",
            "note_btn": "PLAYBACK: Click to play the root notes of each chord. Or press buttons mapped to 1-8 on your keyboard.",
            "vol_slider": "AUDIO: Sets the master volume, updates when the engine updates.",
            "error_msg": "INVALID INPUT: Please use a standard musical root (A, B, C, D, E, F, G), and '#' or 'b' for sharps or flats."
        }

        self.setup_ui()
        
        # Start the background Arpeggiator pulse thread
        self.arp_thread = threading.Thread(target=self._arpeggiator_loop, daemon=True)
        self.arp_thread.start()

        # Application Bindings
        self.bind("<KeyPress>", self.handle_press)
        self.bind("<KeyRelease>", self.handle_release)
        self.bind("<FocusOut>", lambda e: self.sound_engine.panic())
        self.bind("<Escape>", lambda e: self.sound_engine.panic())

    def _arpeggiator_loop(self):
        """Handles rhythmic pulsing of notes based on the current BPM."""
        while True:
            if self.arp_enabled and self.pressed_keys_data:
                # Calculate sleep interval based on BPM
                interval = 60.0 / self.current_bpm
                
                # Selection Logic
                if self.arp_random and len(self.pressed_keys_data) > 1:
                    candidates = self.pressed_keys_data.copy()
                    # Repetition Guard: Don't play the same note 3 times in a row if possible
                    if self.consecutive_count >= 2:
                        candidates = [k for k in candidates if k[2] != self.last_note_id]
                    
                    choice = random.choice(candidates)
                else:
                    # Sequential Logic
                    if self.arp_index >= len(self.pressed_keys_data):
                        self.arp_index = 0
                    choice = self.pressed_keys_data[self.arp_index]
                    self.arp_index += 1

                # Track repetitions for the guard
                current_id = choice[2]
                if current_id == self.last_note_id:
                    self.consecutive_count += 1
                else:
                    self.consecutive_count = 1
                    self.last_note_id = current_id

                # Trigger non-looping pulse
                self.sound_engine.play(choice[0], choice[1], f"arp_{time.time()}", loop=False)
                time.sleep(interval)
            else:
                # Low-intensity sleep when idle
                time.sleep(0.05)

    def setup_ui(self):
        """Constructs the layout using a grid/pack hybrid optimized for 720p."""
        
        # --- TOP HEADER BAR ---
        self.header = ctk.CTkFrame(self, fg_color=("#3f51b5", "#1a237e"), height=100, corner_radius=0)
        self.header.pack(fill="x", side="top")
        
        title_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        title_frame.pack(side="left", padx=25)
        
        ctk.CTkLabel(title_frame, text="transPoseY.py", font=("Courier New", 28, "bold"), text_color="white").pack(anchor="w")
        self.mode_ind = ctk.CTkLabel(title_frame, text="FOCUS: TOP DECK [1-8]", font=("Courier New", 12, "bold"), text_color="#81c784")
        self.mode_ind.pack(anchor="w")

        vol_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        vol_frame.pack(side="right", padx=25)
        ctk.CTkLabel(vol_frame, text="VOLUME", font=("Courier New", 10, "bold"), text_color="white").pack()
        self.vol_sld = ctk.CTkSlider(vol_frame, from_=0, to=1, width=140, command=self._set_engine_vol)
        self.vol_sld.set(0.5)
        self.vol_sld.pack()
        self.add_tip(self.vol_sld, "vol_slider")

        # --- INPUT ZONE ---
        self.input_zone = ctk.CTkFrame(self, fg_color="transparent")
        self.input_zone.pack(fill="x", pady=(15, 5))
        
        # Centering wrapper for boxes
        box_wrapper = ctk.CTkFrame(self.input_zone, fg_color="transparent")
        box_wrapper.pack(expand=True)
        
        # Original Root Entry
        f_orig = ctk.CTkFrame(box_wrapper, fg_color="transparent")
        f_orig.pack(side="left", padx=15)
        ctk.CTkLabel(f_orig, text="ORIGINAL ROOT", font=("Courier New", 11, "bold")).pack()
        b_orig = ctk.CTkFrame(f_orig, fg_color="#d32f2f", width=65, height=65, corner_radius=4); b_orig.pack()
        self.entry_start_key = ctk.CTkEntry(b_orig, width=55, height=55, font=("Courier New", 22, "bold"), justify="center", border_width=0)
        self.entry_start_key.place(relx=0.5, rely=0.5, anchor="center"); self.entry_start_key.insert(0, "A")
        self.add_tip(self.entry_start_key, "orig_root")

        # Target Root Entry
        f_targ = ctk.CTkFrame(box_wrapper, fg_color="transparent")
        f_targ.pack(side="left", padx=15)
        self.label_target_title = ctk.CTkLabel(f_targ, text="TARGET ROOT", font=("Courier New", 11, "bold")); self.label_target_title.pack()
        self.box_targ_bg = ctk.CTkFrame(f_targ, fg_color="#1976d2", width=65, height=65, corner_radius=4); self.box_targ_bg.pack()
        self.entry_target_key = ctk.CTkEntry(self.box_targ_bg, width=55, height=55, font=("Courier New", 22, "bold"), justify="center", border_width=0)
        self.entry_target_key.place(relx=0.5, rely=0.5, anchor="center"); self.entry_target_key.insert(0, "C")
        self.add_tip(self.entry_target_key, "targ_root")

        # Error Messaging Label (Visible Red Text)
        self.error_label = ctk.CTkLabel(self, text="", text_color="#ff5252", font=("Courier New", 13, "bold"))
        self.error_label.pack(pady=2)

        # --- ARPEGGIATOR CONSOLE ---
        self.arp_bar = ctk.CTkFrame(self, fg_color=("#EAEAEA", "#161616"), corner_radius=8, height=60)
        self.arp_bar.pack(fill="x", padx=30, pady=5)
        
        # BPM Slider and Label
        bpm_cont = ctk.CTkFrame(self.arp_bar, fg_color="transparent")
        bpm_cont.pack(side="left", padx=20, pady=10)
        self.bpm_display = ctk.CTkLabel(bpm_cont, text="120 BPM", font=("Courier New", 14, "bold"), width=80)
        self.bpm_display.pack(side="left", padx=10)
        self.bpm_sld = ctk.CTkSlider(bpm_cont, from_=40, to=240, width=220, command=self.on_bpm_scroll)
        self.bpm_sld.set(120); self.bpm_sld.pack(side="left")
        self.add_tip(self.bpm_sld, "bpm_slider")
        
        # Switches
        self.arp_sw = ctk.CTkSwitch(self.arp_bar, text="ARP", command=self.on_arp_toggle, font=("Courier New", 12, "bold"))
        self.arp_sw.pack(side="left", padx=20)
        self.add_tip(self.arp_sw, "arp_toggle")
        
        self.rand_sw = ctk.CTkSwitch(self.arp_bar, text="RANDOM", command=self.on_rand_toggle, font=("Courier New", 12, "bold"))
        self.rand_sw.pack(side="left", padx=20)
        self.add_tip(self.rand_sw, "random_toggle")

        # --- ACTION ROW ---
        self.action_row = ctk.CTkFrame(self, fg_color="transparent")
        self.action_row.pack(fill="x", pady=5)
        
        self.mode_var = ctk.StringVar(value="Major Key")
        self.mode_menu = ctk.CTkOptionMenu(self.action_row, 
                                          values=["Major Key", "Minor Key", "Relative Minor", "Relative Major"], 
                                          variable=self.mode_var, 
                                          command=self.on_mode_switch,
                                          font=("Courier New", 13),
                                          width=180)
        self.mode_menu.pack(side="left", padx=(300, 10))
        self.add_tip(self.mode_menu, "mode_drop")
        
        self.calc_btn = ctk.CTkButton(self.action_row, text="UPDATE ENGINE", 
                                      command=self.calculate, 
                                      font=("Courier New", 13, "bold"),
                                      fg_color="#2e7d32", hover_color="#1b5e20",
                                      width=180)
        self.calc_btn.pack(side="left")
        self.add_tip(self.calc_btn, "update_btn")

        # --- DYNAMIC SCROLLING RESULTS ---
        self.result_container = ctk.CTkScrollableFrame(self, fg_color=("#F5F5F5", "#050505"), corner_radius=12)
        self.result_container.pack(fill="both", expand=True, padx=30, pady=10)

        # --- GLOBAL FOOTER TOOLTIP ---
        self.footer = ctk.CTkFrame(self, fg_color=("#D0D0D0", "#000000"), height=40, corner_radius=0)
        self.footer.pack(fill="x", side="bottom")
        self.tooltip_label = ctk.CTkLabel(self.footer, text=self.HELP_DB["default"], 
                                         font=("Courier New", 13, "italic"), 
                                         text_color=("#444444", "#AAAAAA"))
        self.tooltip_label.pack(pady=8)

    # --- UI Logic Methods ---

    def _set_engine_vol(self, val):
        self.sound_engine._volume = float(val)

    def on_bpm_scroll(self, val):
        self.current_bpm = int(val)
        self.bpm_display.configure(text=f"{self.current_bpm} BPM")

    def on_arp_toggle(self):
        self.arp_enabled = self.arp_sw.get()
        # Panic stop on toggle to clear any hanging sequences
        self.sound_engine.panic()
        self.pressed_key_ids.clear()
        self.pressed_keys_data.clear()

    def on_rand_toggle(self):
        self.arp_random = self.rand_sw.get()

    def on_mode_switch(self, choice):
        """Disables the target box if using relative mode since it's auto-calculated."""
        is_rel = "Relative" in choice
        self.entry_target_key.configure(state="disabled" if is_rel else "normal")
        self.box_targ_bg.configure(fg_color="#333333" if is_rel else "#1976d2")
        self.label_target_title.configure(text_color="#555555" if is_rel else ("black", "white"))

    def add_tip(self, widget, key):
        """Binds hover events to the footer label."""
        widget.bind("<Enter>", lambda e: self.tooltip_label.configure(text=self.HELP_DB.get(key, self.HELP_DB["default"])))
        widget.bind("<Leave>", lambda e: self.tooltip_label.configure(text=self.HELP_DB["default"]))

    def update_ui_state(self):
        """Manages the visual highlighting of the active playback row."""
        active_idx = 1 if self.shift_toggle else 0
        
        # Update Subtitle Indication
        self.mode_ind.configure(
            text=f"FOCUS: {'BOTTOM' if active_idx else 'TOP'} DECK [1-8]", 
            text_color="#9fa8da" if active_idx else "#81c784"
        )
        
        # Visually highlight the frame of the active row
        for i, frame in enumerate(self.row_frames):
            if i == active_idx:
                clr = "#81c784" if i == 0 else "#9fa8da"
                frame.configure(border_width=3, border_color=clr, fg_color="#1E1E1E")
            else:
                frame.configure(border_width=0, fg_color="#121212")

    # --- Playback Management ---

    def trigger_on(self, row, col, key_id):
        """Unified entry point for note activation."""
        if key_id not in self.pressed_key_ids:
            self.pressed_key_ids.add(key_id)
            self.pressed_keys_data.append((row, col, key_id))
            
            # Button Feedback
            if (row, col) in self.chord_buttons:
                self.chord_buttons[(row, col)].configure(fg_color="#555555")
            
            # Direct Playback if not in ARP mode
            if not self.arp_enabled:
                self.sound_engine.play(row, col, key_id)

    def trigger_off(self, key_id):
        """Unified entry point for note release."""
        if key_id in self.pressed_key_ids:
            self.pressed_key_ids.discard(key_id)
            self.pressed_keys_data = [k for k in self.pressed_keys_data if k[2] != key_id]
            
            # Visual Release
            parts = key_id.split('_')
            if len(parts) == 3:
                r, c = int(parts[1]), int(parts[2])
                if (r, c) in self.chord_buttons:
                    self.chord_buttons[(r, c)].configure(fg_color="transparent")
            
            # Audio Termination
            if not self.arp_enabled:
                self.sound_engine.stop(key_id)

    def handle_press(self, event):
        # Shift toggle handling
        if event.keysym in ['Shift_L', 'Shift_R']:
            self.shift_toggle = not self.shift_toggle
            self.update_ui_state()
            return
            
        if event.char in "12345678":
            idx = int(event.char) - 1
            row = 1 if self.shift_toggle else 0
            self.trigger_on(row, idx, f"kbd_{row}_{idx}")

    def handle_release(self, event):
        if event.char in "12345678":
            idx = int(event.char) - 1
            # Release both rows just to be safe
            self.trigger_off(f"kbd_0_{idx}")
            self.trigger_off(f"kbd_1_{idx}")

    # --- Core Theory Engine ---

    def validate_key_entry(self, key_str):
        """Checks if input is a valid musical note."""
        valid_notes = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
        k = key_str.strip().upper().replace("M", "")
        # Handle Flats
        if len(k) > 1 and k[1] == 'B':
            return True
        return k in valid_notes

    def render_scale_row(self, row_idx, title, numerals, scale_data, color_palette):
        """Generates the UI elements for a single scale row."""
        frame = ctk.CTkFrame(self.result_container, fg_color="#121212", corner_radius=10)
        frame.pack(fill="x", pady=8, padx=5)
        self.row_frames.append(frame)
        
        ctk.CTkLabel(frame, text=title, font=("Courier New", 16, "bold"), text_color=color_palette[0]).pack(anchor="w", padx=20, pady=(10, 5))
        
        btn_grid = ctk.CTkFrame(frame, fg_color="transparent")
        btn_grid.pack(fill="x", padx=20, pady=(0, 15))
        
        for i in range(8):
            chord = scale_data[i][0]
            btn = ctk.CTkButton(btn_grid, text=f"{numerals[i]}\n{chord}", 
                                width=105, height=55, 
                                fg_color="transparent", 
                                border_width=1, 
                                border_color=color_palette[1],
                                text_color=color_palette[0],
                                font=("Courier New", 13, "bold"))
            
            # Tooltip and Playback Bindings
            self.add_tip(btn, "note_btn")
            btn.bind("<ButtonPress-1>", lambda e, r=row_idx, c=i: self.trigger_on(r, c, f"kbd_{r}_{c}"))
            btn.bind("<ButtonRelease-1>", lambda e, r=row_idx, c=i: self.trigger_off(f"kbd_{r}_{c}"))
            
            btn.pack(side="left", padx=4)
            self.chord_buttons[(row_idx, i)] = btn

    def calculate(self):
        """Main calculation loop for musical transposition."""
        self.focus()
        self.error_label.configure(text="")
        
        raw_a = self.entry_start_key.get()
        raw_b = self.entry_target_key.get()
        mode = self.mode_var.get()

        # Validation Step
        if not self.validate_key_entry(raw_a) or (not "Relative" in mode and not self.validate_key_entry(raw_b)):
            self.error_label.configure(text=self.HELP_DB["error_msg"])
            return

        # Clear UI
        for widget in self.result_container.winfo_children():
            widget.destroy()
        self.chord_buttons.clear()
        self.row_frames.clear()

        def get_scale_structure(root, intervals, suffixes):
            chroma = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            root = root.upper().strip()
            # Normalize flats to sharps
            if len(root) > 1 and root[1] == 'B':
                map_b = {'CB':'B', 'DB':'C#', 'EB':'D#', 'FB':'E', 'GB':'F#', 'AB':'G#', 'BB':'A#'}
                root = map_b.get(root, root[0])
            root = root.replace("M", "")
            
            if root not in chroma: return None
            
            start_i = chroma.index(root)
            scale = []
            prev_val = -1
            octave = 0
            
            for semi in intervals:
                idx = (start_i + semi) % 12
                if idx < prev_val:
                    octave += 1
                scale.append((chroma[idx] + suffixes[intervals.index(semi)], octave))
                prev_val = idx
            return scale

        # Music Theory Constants
        maj_intervals = [0, 2, 4, 5, 7, 9, 11, 12]
        maj_suffixes = ["", "m", "m", "", "", "m", "°", ""]
        maj_nums = ["I", "ii", "iii", "IV", "V", "vi", "vii°", "VIII"]
        
        min_intervals = [0, 2, 3, 5, 7, 8, 10, 12]
        min_suffixes = ["m", "°", "", "m", "m", "", "", "m"]
        min_nums = ["i", "ii°", "III", "iv", "v", "VI", "VII", "viii"]
        
        chroma_lib = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        render_queue = []

        # Mode-specific logic
        if mode == "Major Key":
            s_orig = get_scale_structure(raw_a, maj_intervals, maj_suffixes)
            s_targ = get_scale_structure(raw_b, maj_intervals, maj_suffixes)
            if s_orig and s_targ:
                render_queue.append((f"ORIGINAL: {raw_a.upper()} MAJOR", maj_nums, s_orig, ("#81c784", "#2e7d32")))
                render_queue.append((f"TARGET: {raw_b.upper()} MAJOR", maj_nums, s_targ, ("#9fa8da", "#3f51b5")))
                
        elif mode == "Minor Key":
            s_orig = get_scale_structure(raw_a, min_intervals, min_suffixes)
            s_targ = get_scale_structure(raw_b, min_intervals, min_suffixes)
            if s_orig and s_targ:
                render_queue.append((f"ORIGINAL: {raw_a.upper()} MINOR", min_nums, s_orig, ("#ce93d8", "#6a1b9a")))
                render_queue.append((f"TARGET: {raw_b.upper()} MINOR", min_nums, s_targ, ("#90caf9", "#1565c0")))
                
        elif mode == "Relative Minor":
            s_orig = get_scale_structure(raw_a, maj_intervals, maj_suffixes)
            if s_orig:
                # The 6th degree is the relative minor root
                rel_root = s_orig[5][0].replace("m", "")
                s_rel = get_scale_structure(rel_root, min_intervals, min_suffixes)
                render_queue.append((f"MAJOR ROOT: {raw_a.upper()}", maj_nums, s_orig, ("#81c784", "#2e7d32")))
                render_queue.append((f"RELATIVE MINOR: {rel_root}m", min_nums, s_rel, ("#ce93d8", "#6a1b9a")))
                
        elif mode == "Relative Major":
            clean_root = raw_a.upper().replace("M", "")
            s_orig = get_scale_structure(clean_root, min_intervals, min_suffixes)
            if s_orig:
                # The 3rd degree of natural minor is the relative major root
                rel_root = s_orig[2][0]
                s_rel = get_scale_structure(rel_root, maj_intervals, maj_suffixes)
                render_queue.append((f"MINOR ROOT: {clean_root}m", min_nums, s_orig, ("#ce93d8", "#6a1b9a")))
                render_queue.append((f"RELATIVE MAJOR: {rel_root}", maj_nums, s_rel, ("#81c784", "#2e7d32")))

        # Final UI Construction
        final_cache_list = []
        for i, (title, nums, data, colors) in enumerate(render_queue):
            self.render_scale_row(i, title, nums, data, colors)
            final_cache_list.append(data)
        
        # Refresh sound engine
        self.sound_engine.pre_cache_scale(final_cache_list)
        self.update_ui_state()

# Application Entry Point
if __name__ == "__main__":
    try:
        app = TransposeApp()
        # Trigger initial calculation to populate default state
        app.calculate()
        app.mainloop()
    except Exception as fatal_error:
        print(f"Critical System Failure: {fatal_error}")
        sys.exit(1)