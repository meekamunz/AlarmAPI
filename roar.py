import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import sys
from time import sleep

from getAlarms import deviceList, getDeviceName, displayAlarms
from functions import isGoodIPv4
from publisher import createPublisher, setAlarm, maintainAlarms, removeAlarms, removePublisher, publishAllAlarms
from csvAlarms import csvWriter, jsonWriter, importCSV, importJSON
from subscriber import createSubscriber, getAlarmSubs, getSubscriber, subscribeAll
from apiAccess import purge, delete

APP_TITLE = '(R)ead (O)rbit (A)larms and w(R)ite - roar.exe'

# ─── Alarm table columns ────────────────────────────────────────────
ALARM_COLUMNS = ('Device Name', 'Address', 'Alarm', 'Time', 'State', 'Value',
                 'Latched State', 'Masked', 'Unmasked State', 'Inverted',
                 'Acknowledged', 'Acknowledged By')

ALARM_STATES = ['Unknown', 'OK', 'Warn', 'Fail']


class RoarApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry('1200x720')
        self.minsize(900, 600)

        # ── Shared state ──
        self.source_ip = None
        self.dest_ip = None
        self.publisher_name = None
        self.publisher_origin = None
        self.subscriber_id = None
        self.collected_alarms = []
        self.devices = []           # list of (address, name) tuples

        # threading controls
        self.connect_cancel = threading.Event()
        self.maintain_stop = threading.Event()
        self.maintain_thread = None
        self.subscribe_stop = threading.Event()
        self.subscribe_thread = None

        self._build_ui()
        self.protocol('WM_DELETE_WINDOW', self._on_close)

    # ────────────────────────────────────────────────────────────────
    # UI Construction
    # ────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Notebook (tabs)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=6, pady=(6, 0))

        self._build_collect_tab()
        self._build_publish_tab()
        self._build_live_tab()
        self._build_utils_tab()

        # Status bar
        self.status_var = tk.StringVar(value='Ready')
        status_bar = ttk.Label(self, textvariable=self.status_var, relief='sunken', anchor='w')
        status_bar.pack(fill='x', padx=6, pady=4)

    # ── Tab 1: Collect Alarms ────────────────────────────────────────
    def _build_collect_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='  Collect Alarms  ')

        # -- Connection frame --
        conn = ttk.LabelFrame(tab, text='Source Server')
        conn.pack(fill='x', padx=8, pady=4)

        ttk.Label(conn, text='IP Address:').grid(row=0, column=0, padx=4, pady=4, sticky='w')
        self.src_ip_var = tk.StringVar()
        self.src_ip_entry = ttk.Entry(conn, textvariable=self.src_ip_var, width=20)
        self.src_ip_entry.grid(row=0, column=1, padx=4, pady=4)
        self.src_connect_btn = ttk.Button(conn, text='Connect', command=self._connect_source)
        self.src_connect_btn.grid(row=0, column=2, padx=4, pady=4)
        self.src_cancel_btn = ttk.Button(conn, text='Cancel', command=self._cancel_connect, state='disabled')
        self.src_cancel_btn.grid(row=0, column=3, padx=4, pady=4)

        # -- Device list + filter --
        mid = ttk.Frame(tab)
        mid.pack(fill='both', expand=True, padx=8, pady=4)

        dev_frame = ttk.LabelFrame(mid, text='Devices')
        dev_frame.pack(side='left', fill='both', expand=False, padx=(0, 4))

        self.device_listbox = tk.Listbox(dev_frame, selectmode='extended', width=40, exportselection=False)
        dev_scroll = ttk.Scrollbar(dev_frame, orient='vertical', command=self.device_listbox.yview)
        self.device_listbox.configure(yscrollcommand=dev_scroll.set)
        self.device_listbox.pack(side='left', fill='both', expand=True, padx=(4, 0), pady=4)
        dev_scroll.pack(side='right', fill='y', pady=4)

        # Filter & collect controls
        ctrl_frame = ttk.Frame(mid)
        ctrl_frame.pack(side='left', fill='y', padx=4)

        ttk.Label(ctrl_frame, text='Severity Filter:').pack(anchor='w', pady=(8, 2))
        self.filter_var = tk.StringVar(value='all')
        filter_combo = ttk.Combobox(ctrl_frame, textvariable=self.filter_var,
                                     values=['all', 'Fail', 'Warn', 'Ok', 'Unknown'],
                                     state='readonly', width=14)
        filter_combo.pack(anchor='w')

        ttk.Label(ctrl_frame, text='Scope:').pack(anchor='w', pady=(12, 2))
        self.scope_var = tk.StringVar(value='selected')
        ttk.Radiobutton(ctrl_frame, text='Selected devices', variable=self.scope_var, value='selected').pack(anchor='w')
        ttk.Radiobutton(ctrl_frame, text='All devices', variable=self.scope_var, value='all').pack(anchor='w')

        self.collect_btn = ttk.Button(ctrl_frame, text='Collect Alarms', command=self._collect_alarms)
        self.collect_btn.pack(anchor='w', pady=(16, 4))

        self.alarm_count_var = tk.StringVar(value='Alarms: 0')
        ttk.Label(ctrl_frame, textvariable=self.alarm_count_var).pack(anchor='w', pady=4)

        ttk.Separator(ctrl_frame, orient='horizontal').pack(fill='x', pady=8)
        ttk.Button(ctrl_frame, text='Save as CSV', command=self._save_csv).pack(anchor='w', pady=2)
        ttk.Button(ctrl_frame, text='Save as JSON', command=self._save_json).pack(anchor='w', pady=2)

        # -- Alarm table --
        table_frame = ttk.LabelFrame(mid, text='Collected Alarms')
        table_frame.pack(side='left', fill='both', expand=True, padx=(4, 0))

        self.alarm_tree = ttk.Treeview(table_frame, columns=ALARM_COLUMNS, show='headings', selectmode='browse')
        for col in ALARM_COLUMNS:
            self.alarm_tree.heading(col, text=col)
            w = 120 if col in ('Time', 'Address', 'Device Name', 'Value') else 85
            self.alarm_tree.column(col, width=w, minwidth=60)

        tree_vscroll = ttk.Scrollbar(table_frame, orient='vertical', command=self.alarm_tree.yview)
        tree_hscroll = ttk.Scrollbar(table_frame, orient='horizontal', command=self.alarm_tree.xview)
        self.alarm_tree.configure(yscrollcommand=tree_vscroll.set, xscrollcommand=tree_hscroll.set)

        self.alarm_tree.grid(row=0, column=0, sticky='nsew')
        tree_vscroll.grid(row=0, column=1, sticky='ns')
        tree_hscroll.grid(row=1, column=0, sticky='ew')
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

    # ── Tab 2: Publish Alarms ────────────────────────────────────────
    def _build_publish_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='  Publish Alarms  ')

        # -- Destination server --
        dest = ttk.LabelFrame(tab, text='Destination Server')
        dest.pack(fill='x', padx=8, pady=4)

        ttk.Label(dest, text='IP Address:').grid(row=0, column=0, padx=4, pady=4, sticky='w')
        self.dest_ip_var = tk.StringVar()
        ttk.Entry(dest, textvariable=self.dest_ip_var, width=20).grid(row=0, column=1, padx=4, pady=4)
        ttk.Button(dest, text='Validate', command=self._validate_dest).grid(row=0, column=2, padx=4, pady=4)

        self.dest_status_var = tk.StringVar(value='')
        ttk.Label(dest, textvariable=self.dest_status_var).grid(row=0, column=3, padx=8, sticky='w')

        # -- Publisher --
        pub_frame = ttk.LabelFrame(tab, text='Publisher')
        pub_frame.pack(fill='x', padx=8, pady=4)

        ttk.Label(pub_frame, text='Name:').grid(row=0, column=0, padx=4, pady=4, sticky='w')
        self.pub_name_var = tk.StringVar(value='ROAR-Publisher')
        ttk.Entry(pub_frame, textvariable=self.pub_name_var, width=25).grid(row=0, column=1, padx=4, pady=4)
        ttk.Button(pub_frame, text='Create Publisher', command=self._create_publisher).grid(row=0, column=2, padx=4, pady=4)
        ttk.Button(pub_frame, text='Delete Publisher', command=self._delete_publisher).grid(row=0, column=3, padx=4, pady=4)

        self.pub_info_var = tk.StringVar(value='No publisher active')
        ttk.Label(pub_frame, textvariable=self.pub_info_var).grid(row=1, column=0, columnspan=4, padx=4, pady=2, sticky='w')

        # -- Publish actions --
        actions = ttk.LabelFrame(tab, text='Publish Actions')
        actions.pack(fill='x', padx=8, pady=4)

        ttk.Button(actions, text='Publish Collected Alarms', command=self._publish_collected).grid(row=0, column=0, padx=4, pady=4)
        ttk.Button(actions, text='Publish from CSV', command=self._publish_from_csv).grid(row=0, column=1, padx=4, pady=4)
        ttk.Button(actions, text='Publish from JSON', command=self._publish_from_json).grid(row=0, column=2, padx=4, pady=4)

        self.maintain_btn = ttk.Button(actions, text='Start Maintaining', command=self._toggle_maintain)
        self.maintain_btn.grid(row=0, column=3, padx=4, pady=4)

        # -- Publish single alarm --
        single = ttk.LabelFrame(tab, text='Publish Single Alarm')
        single.pack(fill='x', padx=8, pady=4)

        labels = ['Device Address:', 'Alarm Name:', 'State:', 'Value:']
        self.single_path_var = tk.StringVar()
        self.single_name_var = tk.StringVar()
        self.single_state_var = tk.StringVar(value='OK')
        self.single_value_var = tk.StringVar()

        ttk.Label(single, text=labels[0]).grid(row=0, column=0, padx=4, pady=2, sticky='w')
        ttk.Entry(single, textvariable=self.single_path_var, width=25).grid(row=0, column=1, padx=4, pady=2)
        ttk.Label(single, text=labels[1]).grid(row=0, column=2, padx=4, pady=2, sticky='w')
        ttk.Entry(single, textvariable=self.single_name_var, width=25).grid(row=0, column=3, padx=4, pady=2)

        ttk.Label(single, text=labels[2]).grid(row=1, column=0, padx=4, pady=2, sticky='w')
        ttk.Combobox(single, textvariable=self.single_state_var, values=ALARM_STATES, state='readonly', width=12).grid(row=1, column=1, padx=4, pady=2, sticky='w')
        ttk.Label(single, text=labels[3]).grid(row=1, column=2, padx=4, pady=2, sticky='w')
        ttk.Entry(single, textvariable=self.single_value_var, width=25).grid(row=1, column=3, padx=4, pady=2)

        ttk.Button(single, text='Publish Alarm', command=self._publish_single).grid(row=1, column=4, padx=8, pady=2)

        # -- Remove alarms --
        rm_frame = ttk.LabelFrame(tab, text='Remove Alarm')
        rm_frame.pack(fill='x', padx=8, pady=4)

        ttk.Label(rm_frame, text='Device Address:').grid(row=0, column=0, padx=4, pady=2, sticky='w')
        self.rm_path_var = tk.StringVar()
        ttk.Entry(rm_frame, textvariable=self.rm_path_var, width=25).grid(row=0, column=1, padx=4, pady=2)
        ttk.Label(rm_frame, text='Alarm Name:').grid(row=0, column=2, padx=4, pady=2, sticky='w')
        self.rm_name_var = tk.StringVar()
        ttk.Entry(rm_frame, textvariable=self.rm_name_var, width=25).grid(row=0, column=3, padx=4, pady=2)
        ttk.Button(rm_frame, text='Remove', command=self._remove_alarm).grid(row=0, column=4, padx=8, pady=2)

    # ── Tab 3: Live Data ─────────────────────────────────────────────
    def _build_live_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='  Live Data  ')

        ctrl = ttk.LabelFrame(tab, text='Subscriber Controls')
        ctrl.pack(fill='x', padx=8, pady=4)

        ttk.Label(ctrl, text='Server IP:').grid(row=0, column=0, padx=4, pady=4, sticky='w')
        self.live_ip_var = tk.StringVar()
        ttk.Entry(ctrl, textvariable=self.live_ip_var, width=20).grid(row=0, column=1, padx=4, pady=4)

        ttk.Button(ctrl, text='Subscribe Selected Devices', command=self._subscribe_selected).grid(row=0, column=2, padx=4, pady=4)
        ttk.Button(ctrl, text='Subscribe All Devices', command=self._subscribe_all).grid(row=0, column=3, padx=4, pady=4)
        self.live_stop_btn = ttk.Button(ctrl, text='Stop', command=self._stop_subscribe, state='disabled')
        self.live_stop_btn.grid(row=0, column=4, padx=4, pady=4)

        self.sub_info_var = tk.StringVar(value='No subscriber active')
        ttk.Label(ctrl, textvariable=self.sub_info_var).grid(row=1, column=0, columnspan=5, padx=4, pady=2, sticky='w')

        # Live data display
        self.live_text = scrolledtext.ScrolledText(tab, wrap='word', state='disabled', height=20)
        self.live_text.pack(fill='both', expand=True, padx=8, pady=4)

    # ── Tab 4: Utilities ─────────────────────────────────────────────
    def _build_utils_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='  Utilities  ')

        purge_frame = ttk.LabelFrame(tab, text='Purge Stale Data')
        purge_frame.pack(fill='x', padx=8, pady=8)

        ttk.Label(purge_frame, text='Server IP:').grid(row=0, column=0, padx=4, pady=4, sticky='w')
        self.purge_ip_var = tk.StringVar()
        ttk.Entry(purge_frame, textvariable=self.purge_ip_var, width=20).grid(row=0, column=1, padx=4, pady=4)
        ttk.Button(purge_frame, text='Purge', command=self._purge).grid(row=0, column=2, padx=4, pady=4)

        about_frame = ttk.LabelFrame(tab, text='About')
        about_frame.pack(fill='x', padx=8, pady=8)
        ttk.Label(about_frame, text='ROAR — Read Orbit Alarms and Rewrite').pack(padx=8, pady=4, anchor='w')
        ttk.Label(about_frame, text='GV Orbit Alarm API tool').pack(padx=8, anchor='w')
        ttk.Label(about_frame, text='Michael.Munns@grassvalley.com').pack(padx=8, pady=(0, 4), anchor='w')

    # ────────────────────────────────────────────────────────────────
    # Tab 1 — Collect actions
    # ────────────────────────────────────────────────────────────────
    def _set_status(self, msg):
        self.status_var.set(msg)

    def _connect_source(self):
        ip = self.src_ip_var.get().strip()
        if not isGoodIPv4(ip):
            messagebox.showerror('Invalid IP', 'Please enter a valid IPv4 address.')
            return
        self.source_ip = ip
        self.connect_cancel.clear()
        self._set_status(f'Connecting to {ip}...')
        self.src_connect_btn.configure(state='disabled')
        self.src_cancel_btn.configure(state='normal')
        threading.Thread(target=self._fetch_devices, daemon=True).start()

    def _cancel_connect(self):
        self.connect_cancel.set()
        self.src_cancel_btn.configure(state='disabled')
        self._set_status('Cancelling connection...')

    def _fetch_devices(self):
        try:
            devs = deviceList(self.source_ip)
            if self.connect_cancel.is_set():
                self.after(0, self._on_connect_cancelled)
                return
            total = len(devs)
            device_info = [None] * total
            completed = [0]  # mutable counter for closure

            def fetch_name(index, addr):
                if self.connect_cancel.is_set():
                    return
                name = getDeviceName(addr, self.source_ip)
                device_info[index] = (addr, name)
                completed[0] += 1
                self.after(0, lambda n=completed[0], t=total: self._set_status(
                    f'Fetching device names... {n}/{t}'))

            with ThreadPoolExecutor(max_workers=8) as executor:
                futures = []
                for i, addr in enumerate(devs):
                    if self.connect_cancel.is_set():
                        break
                    futures.append(executor.submit(fetch_name, i, addr))
                for f in as_completed(futures):
                    if self.connect_cancel.is_set():
                        executor.shutdown(wait=False, cancel_futures=True)
                        self.after(0, self._on_connect_cancelled)
                        return
                    f.result()  # propagate any exceptions

            if self.connect_cancel.is_set():
                self.after(0, self._on_connect_cancelled)
                return
            # Filter out any None entries from cancelled fetches
            self.devices = [d for d in device_info if d is not None]
            self.after(0, self._populate_device_list)
        except Exception as e:
            if self.connect_cancel.is_set():
                self.after(0, self._on_connect_cancelled)
            else:
                self.after(0, lambda: self._on_connect_error(str(e)))

    def _populate_device_list(self):
        self.device_listbox.delete(0, 'end')
        for addr, name in self.devices:
            display = f'{addr}  —  {name}' if name != addr else addr
            self.device_listbox.insert('end', display)
        self.src_connect_btn.configure(state='normal')
        self.src_cancel_btn.configure(state='disabled')
        # Auto-fill live-data and purge IP fields
        self.live_ip_var.set(self.source_ip)
        self.purge_ip_var.set(self.source_ip)
        self._set_status(f'Connected to {self.source_ip}  —  {len(self.devices)} device(s)')

    def _on_connect_cancelled(self):
        self.src_connect_btn.configure(state='normal')
        self.src_cancel_btn.configure(state='disabled')
        self._set_status('Connection cancelled')

    def _on_connect_error(self, msg):
        self.src_connect_btn.configure(state='normal')
        self.src_cancel_btn.configure(state='disabled')
        self._set_status('Connection failed')
        messagebox.showerror('Connection Error', f'Could not connect to server:\n{msg}')

    def _collect_alarms(self):
        if not self.source_ip:
            messagebox.showwarning('No Server', 'Connect to a source server first.')
            return
        severity = self.filter_var.get()
        if self.scope_var.get() == 'selected':
            sel = self.device_listbox.curselection()
            if not sel:
                messagebox.showwarning('No Selection', 'Select at least one device, or choose "All devices".')
                return
            addresses = [self.devices[i][0] for i in sel]
        else:
            addresses = [d[0] for d in self.devices]
        self.collect_btn.configure(state='disabled')
        self._set_status('Collecting alarms...')
        threading.Thread(target=self._do_collect, args=(addresses, severity), daemon=True).start()

    def _do_collect(self, addresses, severity):
        try:
            alarms = displayAlarms(self.source_ip, addresses, severity)
            self.collected_alarms = alarms
            self.after(0, self._populate_alarm_table)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror('Error', f'Failed to collect alarms:\n{e}'))
        finally:
            self.after(0, lambda: self.collect_btn.configure(state='normal'))

    def _populate_alarm_table(self):
        # Clear existing
        for item in self.alarm_tree.get_children():
            self.alarm_tree.delete(item)
        # Build a device-name cache from self.devices
        name_map = {addr: name for addr, name in self.devices}
        for a in self.collected_alarms:
            dev_name = name_map.get(a['path'], a['path'])
            self.alarm_tree.insert('', 'end', values=(
                dev_name, a['path'], a['name'], a['timestamp'],
                a['state'], a['value'], a['latchedState'], a['masked'],
                a['unmaskedState'], a['inverted'], a['acked'], a['ackedBy']))
        count = len(self.collected_alarms)
        self.alarm_count_var.set(f'Alarms: {count}')
        self._set_status(f'Collected {count} alarm(s)')

    def _save_csv(self):
        if not self.collected_alarms:
            messagebox.showinfo('No Data', 'Collect alarms first.')
            return
        result = csvWriter(self.collected_alarms, self.source_ip)
        if result:
            self._set_status(f'Saved CSV: {result}')

    def _save_json(self):
        if not self.collected_alarms:
            messagebox.showinfo('No Data', 'Collect alarms first.')
            return
        result = jsonWriter(self.collected_alarms, self.source_ip)
        if result:
            self._set_status(f'Saved JSON: {result}')

    # ────────────────────────────────────────────────────────────────
    # Tab 2 — Publish actions
    # ────────────────────────────────────────────────────────────────
    def _validate_dest(self):
        ip = self.dest_ip_var.get().strip()
        if isGoodIPv4(ip):
            self.dest_ip = ip
            self.dest_status_var.set(f'Valid: {ip}')
            self._set_status(f'Destination set to {ip}')
        else:
            self.dest_ip = None
            self.dest_status_var.set('Invalid')
            messagebox.showerror('Invalid IP', 'Please enter a valid IPv4 address.')

    def _require_dest(self):
        if not self.dest_ip:
            messagebox.showwarning('No Destination', 'Set and validate a destination IP first.')
            return False
        return True

    def _require_publisher(self):
        if not self.publisher_origin:
            messagebox.showwarning('No Publisher', 'Create a publisher first.')
            return False
        return True

    def _create_publisher(self):
        if not self._require_dest():
            return
        name = self.pub_name_var.get().strip()
        if not name:
            messagebox.showwarning('Name Required', 'Enter a publisher name.')
            return
        self._set_status('Creating publisher...')

        def do():
            try:
                data = createPublisher(self.dest_ip, name)
                self.publisher_name = data['name']
                self.publisher_origin = data['origin']
                if data['origin'] is None:
                    self.after(0, lambda: messagebox.showerror('Error', data['name']))
                    self.after(0, lambda: self.pub_info_var.set('Publisher creation failed'))
                else:
                    self.after(0, lambda: self.pub_info_var.set(
                        f'Publisher: {data["name"]}  |  ID: {data["origin"]}'))
                    self.after(0, lambda: self._set_status(f'Publisher "{data["name"]}" created'))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror('Error', str(e)))
        threading.Thread(target=do, daemon=True).start()

    def _delete_publisher(self):
        if not self._require_dest() or not self._require_publisher():
            return
        # Stop maintaining first
        if self.maintain_thread and self.maintain_thread.is_alive():
            self.maintain_stop.set()
            self.maintain_thread.join(timeout=2)

        def do():
            try:
                r = removePublisher(self.dest_ip, self.publisher_origin)
                if r.status_code == 204:
                    self.publisher_name = None
                    self.publisher_origin = None
                    self.after(0, lambda: self.pub_info_var.set('No publisher active'))
                    self.after(0, lambda: self._set_status('Publisher deleted'))
                    self.after(0, lambda: self.maintain_btn.configure(text='Start Maintaining'))
                else:
                    self.after(0, lambda: messagebox.showerror('Error', f'Delete failed (HTTP {r.status_code})'))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror('Error', str(e)))
        threading.Thread(target=do, daemon=True).start()

    def _publish_collected(self):
        if not self._require_dest() or not self._require_publisher():
            return
        if not self.collected_alarms:
            messagebox.showinfo('No Data', 'Collect alarms on the Collect tab first.')
            return
        self._set_status('Publishing collected alarms...')

        def do():
            try:
                # Re-stamp alarms with current publisher origin
                alarm_data = []
                for a in self.collected_alarms:
                    alarm_data.append({
                        'id': {'name': a['name'], 'path': a['path']},
                        'origin': self.publisher_origin,
                        'state': {
                            'acked': str(a['acked']),
                            'ackedBy': str(a['ackedBy']),
                            'inverted': str(a['inverted']),
                            'latchedState': str(a['latchedState']),
                            'masked': str(a['masked']),
                            'state': str(a['state']),
                            'timestamp': str(a['timestamp']),
                            'unmaskedState': str(a['unmaskedState']),
                            'value': str(a['value'])
                        }
                    })
                from apiAccess import post
                r = post(self.dest_ip, 'alarms', alarm_data)
                count = len(alarm_data)
                if r.status_code in (200, 201):
                    self.after(0, lambda: self._set_status(f'Published {count} alarm(s) successfully'))
                elif r.status_code == 409:
                    self.after(0, lambda: self._set_status(f'Published {count} alarm(s) — some already exist (409)'))
                else:
                    self.after(0, lambda: self._set_status(f'Publish returned HTTP {r.status_code}'))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror('Error', str(e)))
        threading.Thread(target=do, daemon=True).start()

    def _publish_from_csv(self):
        if not self._require_dest() or not self._require_publisher():
            return
        self._set_status('Importing CSV...')

        def do():
            try:
                alarm_data = importCSV(self.publisher_origin)
                if not alarm_data:
                    self.after(0, lambda: self._set_status('CSV import cancelled or empty'))
                    return
                from apiAccess import post
                r = post(self.dest_ip, 'alarms', alarm_data)
                count = len(alarm_data)
                self.after(0, lambda: self._set_status(f'Published {count} alarm(s) from CSV (HTTP {r.status_code})'))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror('Error', str(e)))
        threading.Thread(target=do, daemon=True).start()

    def _publish_from_json(self):
        if not self._require_dest() or not self._require_publisher():
            return
        self._set_status('Importing JSON...')

        def do():
            try:
                alarm_data = importJSON(self.publisher_origin)
                if not alarm_data:
                    self.after(0, lambda: self._set_status('JSON import cancelled or empty'))
                    return
                from apiAccess import post
                r = post(self.dest_ip, 'alarms', alarm_data)
                count = len(alarm_data)
                self.after(0, lambda: self._set_status(f'Published {count} alarm(s) from JSON (HTTP {r.status_code})'))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror('Error', str(e)))
        threading.Thread(target=do, daemon=True).start()

    def _toggle_maintain(self):
        if self.maintain_thread and self.maintain_thread.is_alive():
            # Stop
            self.maintain_stop.set()
            self.maintain_btn.configure(text='Start Maintaining')
            self._set_status('Stopping maintain loop...')
            return
        if not self._require_dest() or not self._require_publisher():
            return
        self.maintain_stop = threading.Event()
        self.maintain_btn.configure(text='Stop Maintaining')
        self._set_status(f'Maintaining publisher "{self.publisher_name}"...')

        def do():
            maintainAlarms(self.dest_ip, self.publisher_name, self.publisher_origin,
                           stop_event=self.maintain_stop)
            self.after(0, lambda: self.maintain_btn.configure(text='Start Maintaining'))
            self.after(0, lambda: self._set_status('Maintain loop stopped'))
        self.maintain_thread = threading.Thread(target=do, daemon=True)
        self.maintain_thread.start()

    def _publish_single(self):
        if not self._require_dest() or not self._require_publisher():
            return
        path = self.single_path_var.get().strip()
        name = self.single_name_var.get().strip()
        state = self.single_state_var.get()
        value = self.single_value_var.get().strip()
        if not path or not name:
            messagebox.showwarning('Missing Fields', 'Device Address and Alarm Name are required.')
            return

        def do():
            try:
                r = setAlarm(self.dest_ip, self.publisher_origin, path, name, state, value)
                if r.status_code in (200, 201):
                    self.after(0, lambda: self._set_status(f'Published alarm "{name}" on {path}'))
                elif r.status_code == 409:
                    self.after(0, lambda: self._set_status(f'Alarm already exists (409)'))
                else:
                    self.after(0, lambda: self._set_status(f'Publish returned HTTP {r.status_code}'))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror('Error', str(e)))
        threading.Thread(target=do, daemon=True).start()

    def _remove_alarm(self):
        if not self._require_dest() or not self._require_publisher():
            return
        path = self.rm_path_var.get().strip()
        name = self.rm_name_var.get().strip()
        if not path or not name:
            messagebox.showwarning('Missing Fields', 'Device Address and Alarm Name are required.')
            return

        def do():
            try:
                r = removeAlarms(self.dest_ip, self.publisher_origin, path, name)
                self.after(0, lambda: self._set_status(f'Remove alarm result: HTTP {r.status_code}'))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror('Error', str(e)))
        threading.Thread(target=do, daemon=True).start()

    # ────────────────────────────────────────────────────────────────
    # Tab 3 — Live Data actions
    # ────────────────────────────────────────────────────────────────
    def _subscribe_selected(self):
        ip = self.live_ip_var.get().strip()
        if not isGoodIPv4(ip):
            messagebox.showerror('Invalid IP', 'Enter a valid server IP for live data.')
            return
        sel = self.device_listbox.curselection()
        if not sel:
            messagebox.showwarning('No Selection', 'Select devices on the Collect tab first.')
            return
        paths = [self.devices[i][0] for i in sel]
        self._start_subscriber(ip, paths)

    def _subscribe_all(self):
        ip = self.live_ip_var.get().strip()
        if not isGoodIPv4(ip):
            messagebox.showerror('Invalid IP', 'Enter a valid server IP for live data.')
            return
        self._set_status('Subscribing to all devices...')

        def do():
            try:
                sub_id = subscribeAll(ip)
                self.subscriber_id = sub_id
                self.after(0, lambda: self.sub_info_var.set(f'Subscriber: {sub_id}'))
                self.after(0, lambda: self._set_status('Subscribed to all devices'))
                self._start_polling(ip, sub_id)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror('Error', str(e)))
        threading.Thread(target=do, daemon=True).start()

    def _start_subscriber(self, ip, device_paths):
        self._set_status('Creating subscriber...')

        def do():
            try:
                sub_id = createSubscriber(ip, device_paths)
                self.subscriber_id = sub_id
                self.after(0, lambda: self.sub_info_var.set(f'Subscriber: {sub_id}'))
                self.after(0, lambda: self._set_status(f'Subscriber created: {sub_id}'))
                self._start_polling(ip, sub_id)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror('Error', str(e)))
        threading.Thread(target=do, daemon=True).start()

    def _start_polling(self, ip, sub_id):
        # Stop any existing polling
        if self.subscribe_thread and self.subscribe_thread.is_alive():
            self.subscribe_stop.set()
            self.subscribe_thread.join(timeout=2)

        self.subscribe_stop = threading.Event()
        self.after(0, lambda: self.live_stop_btn.configure(state='normal'))

        def callback(data):
            if data is not None:
                text = json.dumps(data, indent=2, sort_keys=True) + '\n\n'
                self.after(0, lambda t=text: self._append_live(t))
            else:
                self.after(0, lambda: self._append_live('-- Polling failed or ended --\n'))

        self.subscribe_thread = threading.Thread(
            target=getAlarmSubs, args=(ip, sub_id),
            kwargs={'stop_event': self.subscribe_stop, 'callback': callback},
            daemon=True)
        self.subscribe_thread.start()

    def _append_live(self, text):
        self.live_text.configure(state='normal')
        self.live_text.insert('end', text)
        self.live_text.see('end')
        self.live_text.configure(state='disabled')

    def _stop_subscribe(self):
        self.subscribe_stop.set()
        self.live_stop_btn.configure(state='disabled')
        self._set_status('Subscriber polling stopped')

    # ────────────────────────────────────────────────────────────────
    # Tab 4 — Utilities
    # ────────────────────────────────────────────────────────────────
    def _purge(self):
        ip = self.purge_ip_var.get().strip()
        if not isGoodIPv4(ip):
            messagebox.showerror('Invalid IP', 'Enter a valid server IP.')
            return
        self._set_status(f'Purging stale data on {ip}...')

        def do():
            try:
                r = purge(ip)
                if r.status_code == 200:
                    self.after(0, lambda: self._set_status('Stale data purged successfully'))
                else:
                    self.after(0, lambda: self._set_status(f'Purge returned HTTP {r.status_code}'))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror('Error', str(e)))
        threading.Thread(target=do, daemon=True).start()

    # ────────────────────────────────────────────────────────────────
    # Cleanup on exit
    # ────────────────────────────────────────────────────────────────
    def _on_close(self):
        # Stop background threads
        self.maintain_stop.set()
        self.subscribe_stop.set()

        # Clean up publisher and subscriber
        try:
            if self.publisher_origin and self.dest_ip:
                removePublisher(self.dest_ip, self.publisher_origin)
        except Exception:
            pass
        try:
            if self.subscriber_id and self.live_ip_var.get().strip():
                ip = self.live_ip_var.get().strip()
                delete(ip, 'subscribers?subscriptionId=' + self.subscriber_id, None)
        except Exception:
            pass
        self.destroy()


if __name__ == '__main__':
    app = RoarApp()
    # Accept optional IP address from command line
    if len(sys.argv) >= 2 and isGoodIPv4(sys.argv[1]):
        app.src_ip_var.set(sys.argv[1])
    app.mainloop()