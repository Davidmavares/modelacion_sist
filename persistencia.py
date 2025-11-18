
def guardar_datos(filepath, nodos, aristas, javier_casa, andreina_casa, destinos):
    try:
        with open(filepath, "w", encoding="utf-8") as a:
            a.write("NODES\n")
            for n in nodos: 
                a.write(f"{n[0]},{n[1]}\n")
            
            a.write("EDGES\n")
            vistos = set()
            for (u, n), w in aristas.items():
                if (n, u) in vistos: continue
                vistos.add((u, n))
                a.write(f"{u[0]},{u[1]}|{n[0]},{n[1]}|{w}\n")
            
            a.write("DATA\n")
            javier_str = f"{javier_casa[0]},{javier_casa[1]}" if javier_casa else ""
            andreina_str = f"{andreina_casa[0]},{andreina_casa[1]}" if andreina_casa else ""
            
            a.write(f"JAVIER:{javier_str}\n")
            a.write(f"ANDREINA:{andreina_str}\n")
            
            for k, va in destinos.items(): 
                a.write(f"DEST:{k}|{va[0]},{va[1]}\n")
        return True, "Mapa guardado correctamente."
    except Exception as e:
        return False, str(e)

def cargar_datos(filepath):
    try:
        nodos = set()
        aristas = {}
        destinos = {}
        javier_casa = None
        andreina_casa = None
        
        sec = ""
        with open(filepath, "r", encoding="utf-8") as a:
            for l in a:
                l = l.strip()
                if l in ["NODES", "EDGES", "DATA"]: 
                    sec = l
                    continue
                if not l: continue
                
                if sec == "NODES": 
                    nodos.add(tuple(map(int, l.split(','))))
                
                elif sec == "EDGES":
                    p1, p2, w = l.split('|')
                    u = tuple(map(int, p1.split(',')))
                    v = tuple(map(int, p2.split(',')))
                    peso = int(w)
                    aristas[(u, v)] = peso
                    aristas[(v, u)] = peso
                
                elif sec == "DATA":
                    if l.startswith("JAVIER:") and len(l) > 7: 
                        javier_casa = tuple(map(int, l[7:].split(',')))
                    elif l.startswith("ANDREINA:") and len(l) > 9: 
                        andreina_casa = tuple(map(int, l[9:].split(',')))
                    elif l.startswith("DEST:"):
                        n, c = l[5:].split('|')
                        destinos[n] = tuple(map(int, c.split(',')))
                        
        return True, (nodos, aristas, javier_casa, andreina_casa, destinos)
    except Exception as e:
        return False, str(e)