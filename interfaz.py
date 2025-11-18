
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from collections import defaultdict
import os  


import config as cfg
import logica
import persistencia

class BogotaGraphEditor:
    
    def __init__(self, root):
        self.root = root
        self.root.title("Planificador Rutas Bogotá (Carga Automática)")
        self.root.geometry("1150x900")
        
        self.nodos = set()
        self.aristas = {}
        self.destinos = {}
        self.javier_casa = None
        self.andreina_casa = None
        self.modo = tk.StringVar(value="MOVER")
        self.nodo_seleccionado = None
        
        self.setup_ui()
        
        # INTENTA CARGAR AUTOMÁTICAMENTE AL INICIAR
        self.inicializar_grafo_bogota()
        self.dibujar_todo()

    def setup_ui(self):
        # --- PANEL INFERIOR ---
        bottom_frame = ttk.Frame(self.root, padding="10", relief="raised")
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        ttk.Label(bottom_frame, text="Ir a:", font=("Arial", 11, "bold")).pack(side=tk.LEFT)
        self.combo_destinos = ttk.Combobox(bottom_frame, state="readonly", width=25)
        self.combo_destinos.pack(side=tk.LEFT, padx=10)
        
        btn = tk.Button(bottom_frame, text="CALCULAR RUTA SEGURA", bg="#2a9d8f", fg="white", 
                        font=("Arial", 10, "bold"), command=self.calcular)
        btn.pack(side=tk.LEFT, padx=10)

        # --- PANEL SUPERIOR ---
        top_frame = ttk.Frame(self.root, padding="5")
        top_frame.pack(side=tk.TOP, fill=tk.X)
        ttk.Button(top_frame, text="📂 Cargar Otro", command=self.cargar_txt).pack(side=tk.LEFT)
        ttk.Button(top_frame, text="💾 Guardar", command=self.guardar_txt).pack(side=tk.LEFT)
        ttk.Separator(top_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        ttk.Radiobutton(top_frame, text="Mover", variable=self.modo, value="MOVER").pack(side=tk.LEFT)
        ttk.Radiobutton(top_frame, text="Nodo", variable=self.modo, value="NODO").pack(side=tk.LEFT)
        ttk.Radiobutton(top_frame, text="Arista", variable=self.modo, value="ARISTA").pack(side=tk.LEFT)
        ttk.Button(top_frame, text="Borrar", command=self.borrar_seleccionado).pack(side=tk.RIGHT)

        # --- LOG ---
        self.txt_log = tk.Text(self.root, height=7, font=("Consolas", 10), bg="#f1faee")
        self.txt_log.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

        # --- CANVAS ---
        self.canvas = tk.Canvas(self.root, bg="white")
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.on_click_izq)
        self.canvas.bind("<Button-3>", self.on_click_der)

    # --- MÉTODOS GRÁFICOS ---
    def map_coords(self, carrera, calle):
        x = cfg.PADDING_LEFT + (cfg.CARRERA_MAX - carrera) * cfg.BLOCK_SIZE
        y = cfg.PADDING_Y + (cfg.CALLE_MAX - calle) * cfg.BLOCK_SIZE
        return x, y

    def inv_map_coords(self, px, py):
        c = round(cfg.CARRERA_MAX - (px - cfg.PADDING_LEFT) / cfg.BLOCK_SIZE)
        k = round(cfg.CALLE_MAX - (py - cfg.PADDING_Y) / cfg.BLOCK_SIZE)
        return c, k

    def dibujar_todo(self):
        self.canvas.delete("all")
        self.dibujar_cerros()
        
        # Aristas
        for (u, v), w in self.aristas.items():
            if u > v: continue
            x1, y1 = self.map_coords(*u)
            x2, y2 = self.map_coords(*v)
            c, width = cfg.COLOR_ARISTA, 2
            if w > 5: c, width = cfg.COLOR_ARISTA_LENTA, 4
            self.canvas.create_line(x1, y1, x2, y2, fill=c, width=width, capstyle=tk.ROUND)
            self.canvas.create_text((x1+x2)/2, (y1+y2)/2, text=str(w), font=("Arial", 7), fill="#333")

        # Nodos
        for n in self.nodos:
            x, y = self.map_coords(*n)
            fill, out, w = "white", "#333", 1
            if n == self.javier_casa: fill = cfg.COLOR_JAVIER
            elif n == self.andreina_casa: fill = cfg.COLOR_ANDREINA
            elif n in self.destinos.values(): fill = cfg.COLOR_DESTINO
            if n == self.nodo_seleccionado: out, w = "orange", 3
            self.canvas.create_oval(x-7, y-7, x+7, y+7, fill=fill, outline=out, width=w)
            
            lbl = ""
            if n == self.javier_casa: lbl = "Javier"
            elif n == self.andreina_casa: lbl = "Andreína"
            else:
                for k, v in self.destinos.items():
                    if v == n: lbl = k
            if lbl: self.canvas.create_text(x, y-15, text=lbl, font=("Arial", 8, "bold"))
        
        self.combo_destinos['values'] = list(self.destinos.keys())
        if list(self.destinos.keys()) and not self.combo_destinos.get(): 
            self.combo_destinos.current(0)

    def dibujar_cerros(self):
        wc, hc = 1150, 900
        if self.canvas.winfo_width() > 100: wc, hc = self.canvas.winfo_width(), self.canvas.winfo_height()
        xc, _ = self.map_coords(cfg.CARRERA_MIN, 0)
        xc += 40
        poly = [xc,0, xc+20,100, xc-10,200, xc+30,400, xc,hc, wc,hc, wc,0]
        self.canvas.create_polygon(poly, fill=cfg.COLOR_CERROS, outline="", tags="bg")
        self.canvas.create_text(xc+30, hc/2, text="CERROS (ESTE)", angle=90, fill="white", font=("Arial", 12, "bold"))

        for c in range(cfg.CARRERA_MIN, cfg.CARRERA_MAX + 1):
            x, y1 = self.map_coords(c, cfg.CALLE_MAX)
            _, y2 = self.map_coords(c, cfg.CALLE_MIN)
            self.canvas.create_line(x, y1, x, y2, fill="#eee", dash=(2,4))
            self.canvas.create_text(x, y1-15, text=f"K{c}", fill="#aaa")
        for k in range(cfg.CALLE_MIN, cfg.CALLE_MAX + 1):
            x1, y = self.map_coords(cfg.CARRERA_MAX, k)
            x2, _ = self.map_coords(cfg.CARRERA_MIN, k)
            self.canvas.create_line(x1, y, x2, y, fill="#eee", dash=(2,4))
            self.canvas.create_text(x1-20, y, text=f"C{k}", fill="#aaa")

    
    def on_click_izq(self, e):
        n = self.get_cercano(e.x, e.y)
        m = self.modo.get()
        if m == "NODO":
            c, k = self.inv_map_coords(e.x, e.y)
            if (c,k) not in self.nodos: self.nodos.add((c,k)); self.dibujar_todo()
        elif m == "MOVER": self.nodo_seleccionado = n; self.dibujar_todo()
        elif m == "ARISTA":
            if n:
                if not self.nodo_seleccionado: self.nodo_seleccionado = n
                else:
                    if n != self.nodo_seleccionado:
                        val = simpledialog.askinteger("Peso", "Minutos:", initialvalue=5)
                        if val: self.aristas[(self.nodo_seleccionado, n)] = self.aristas[(n, self.nodo_seleccionado)] = val
                    self.nodo_seleccionado = None
                self.dibujar_todo()

    def on_click_der(self, e):
        n = self.get_cercano(e.x, e.y)
        if not n: return
        m = tk.Menu(self.root, tearoff=0)
        m.add_command(label="Casa Javier", command=lambda: self.set_role('J', n))
        m.add_command(label="Casa Andreína", command=lambda: self.set_role('A', n))
        m.add_separator()
        m.add_command(label="Destino...", command=lambda: self.add_dest(n))
        m.post(e.x_root, e.y_root)

    def get_cercano(self, x, y):
        for n in self.nodos:
            nx, ny = self.map_coords(*n)
            if (x-nx)**2 + (y-ny)**2 < 250: return n
        return None
    def set_role(self, r, n):
        if r=='J': self.javier_casa=n
        else: self.andreina_casa=n
        self.dibujar_todo()
    def add_dest(self, n):
        nom = simpledialog.askstring("Lugar", "Nombre:")
        if nom: self.destinos[nom]=n; self.dibujar_todo()
    def borrar_seleccionado(self):
        n = self.nodo_seleccionado
        if n:
            if n in self.nodos: self.nodos.remove(n)
            for k in list(self.aristas.keys()):
                if n in k: del self.aristas[k]
            if self.javier_casa==n: self.javier_casa=None
            if self.andreina_casa==n: self.andreina_casa=None
            for k,v in list(self.destinos.items()):
                if v==n: del self.destinos[k]
            self.nodo_seleccionado=None; self.dibujar_todo()

    
    def calcular(self):
        self.canvas.delete("ruta")
        self.txt_log.delete("1.0", tk.END)
        
        if not self.javier_casa or not self.andreina_casa or not self.combo_destinos.get():
            messagebox.showwarning("Faltan info", "Define casas y destino.")
            return
        
        dest = self.destinos[self.combo_destinos.get()]
        G = defaultdict(dict)
        for (u,v), w in self.aristas.items(): G[u][v] = w
        
        res = logica.calcular_itinerario_sincronizado(G, self.javier_casa, self.andreina_casa, dest)
        
        if not res:
            self.txt_log.insert(tk.END, "⚠️ IMPOSIBLE: Los caminos se cruzan inevitablemente.")
            return
            
        self.dibujar_camino(res["javier"]["ruta"], cfg.COLOR_JAVIER, 5)
        self.dibujar_camino(res["andreina"]["ruta"], cfg.COLOR_ANDREINA, -5)
        
        txt = f"DESTINO: {self.combo_destinos.get()}\n"
        txt += f"ESTRATEGIA: {res['estrategia']}\n"
        txt += f"Javier: {res['javier']['tiempo']} min | Andreína: {res['andreina']['tiempo']} min\n"
        txt += f"SINCRONIZACIÓN: {res['mensaje_sincronia']}"
        self.txt_log.insert(tk.END, txt)

    def dibujar_camino(self, ruta, color, offset):
        pts = []
        for n in ruta:
            x, y = self.map_coords(*n)
            pts.extend([x+offset, y+offset])
        if len(pts)>2: self.canvas.create_line(pts, fill=color, width=3, arrow=tk.LAST, tags="ruta")

    
    def inicializar_grafo_bogota(self):
       
        ARCHIVO_DEFECTO = "grafo_bogota.txt"

        
        if os.path.exists(ARCHIVO_DEFECTO):
            print(f"Cargando grafo desde {ARCHIVO_DEFECTO}...")
            exito, datos = persistencia.cargar_datos(ARCHIVO_DEFECTO)
            if exito:
                self.nodos, self.aristas, self.javier_casa, self.andreina_casa, self.destinos = datos
                return 

        
        print("Archivo no encontrado. Generando grafo base...")
        for c in range(cfg.CARRERA_MIN, cfg.CARRERA_MAX+1):
            for k in range(cfg.CALLE_MIN, cfg.CALLE_MAX+1):
                self.nodos.add((c,k))
                vecs = [((c,k+1),'v'), ((c+1,k),'h')]
                for v, t in vecs:
                    if cfg.CARRERA_MIN<=v[0]<=cfg.CARRERA_MAX and cfg.CALLE_MIN<=v[1]<=cfg.CALLE_MAX:
                        w = 7 if (t=='v' and c in {11,12,13}) else (10 if (t=='h' and k==51) else 5)
                        self.aristas[((c,k),v)] = self.aristas[(v,(c,k))] = w
        
        self.javier_casa, self.andreina_casa = (14,54), (13,52)
        self.destinos = {"Discoteca The Darkness":(14,50), "Bar La Pasión":(11,54), "Cervecería Mi Rolita":(12,50)}

        
        persistencia.guardar_datos(ARCHIVO_DEFECTO, self.nodos, self.aristas, self.javier_casa, self.andreina_casa, self.destinos)
        print(f"Grafo base guardado en {ARCHIVO_DEFECTO}")

    def guardar_txt(self):
        f = filedialog.asksaveasfilename(defaultextension=".txt")
        if f: persistencia.guardar_datos(f, self.nodos, self.aristas, self.javier_casa, self.andreina_casa, self.destinos)
    
    def cargar_txt(self):
        f = filedialog.askopenfilename()
        if f:
            ok, d = persistencia.cargar_datos(f)
            if ok: self.nodos, self.aristas, self.javier_casa, self.andreina_casa, self.destinos = d; self.dibujar_todo()