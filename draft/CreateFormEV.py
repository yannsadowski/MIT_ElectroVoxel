import tkinter as tk
from tkinter import messagebox as mb
import pandas as pd
import tkinter.simpledialog as sd
import tkinter.filedialog as fd


class ElectroVoxelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ElectroVoxel Simulator")

        # Paramètres du grid
        self.grid_size = (20, 20)  # Taille du grid (en nombre de voxels)
        self.voxel_size = 40       # Taille de chaque voxel pour l'affichage
        self.screen_size = (self.grid_size[0] * self.voxel_size, 
                            self.grid_size[1] * self.voxel_size)

        # Paramètres de couleur
        self.background_color = "#FFFFFF"  # Blanc
        self.grid_color = "#C8C8C8"        # Gris clair

        # Création du canevas pour les électrovoxels
        self.canvas = tk.Canvas(root, width=self.screen_size[0], height=self.screen_size[1], bg="white")
        self.canvas.pack(side="left")
        
        # Dessiner le grid
        self.draw_grid()
        
        # Création du panneau de contrôle
        control_panel = tk.Frame(root)
        control_panel.pack(side="right", fill="y")

        # Boutons et autres widgets de contrôle
        self.electrovoxel_count_label = tk.Label(control_panel, text="Electrovoxels: 0")
        self.electrovoxel_count_label.pack()

        # Label pour l'information d'unité
        self.unity_info_label = tk.Label(control_panel, text="Forme Unie: Non")
        self.unity_info_label.pack()
        
        # Liez le clic de souris à une méthode
        self.canvas.bind("<Button-1>", self.handle_canvas_click)

        # Pour stocker les électrovoxels dessinés
        self.electrovoxels = {}  # Clé: (x, y), Valeur: ID du rectangle sur le canevas
        
        clear_button = tk.Button(control_panel, text="Clear", command=self.clear_grid)
        clear_button.pack()

        save_button = tk.Button(control_panel, text="Save", command=self.save_grid)
        save_button.pack()

        load_button = tk.Button(control_panel, text="Load", command=self.load_grid)
        load_button.pack()
        
    def draw_grid(self):
            for x in range(0, self.screen_size[0], self.voxel_size):
                for y in range(0, self.screen_size[1], self.voxel_size):
                    self.canvas.create_rectangle(x, y, x + self.voxel_size, y + self.voxel_size, outline=self.grid_color)

    def clear_grid(self):
        # Effacer tous les électrovoxels du canevas
        self.canvas.delete("all")

        # Dessiner le grid
        self.draw_grid()
        
        # Réinitialiser le dictionnaire des électrovoxels
        self.electrovoxels.clear()

        # Mettre à jour le compteur d'électrovoxels
        self.update_electrovoxel_count()
    
    def handle_canvas_click(self, event):
        # Calculer les coordonnées de la grille cliquée
        grid_x = event.x // self.voxel_size
        grid_y = event.y // self.voxel_size

        # Coordonnées pour dessiner/effacer l'électrovoxel
        x1, y1 = grid_x * self.voxel_size, grid_y * self.voxel_size
        x2, y2 = x1 + self.voxel_size, y1 + self.voxel_size

        # Dessiner ou effacer l'électrovoxel
        if (grid_x, grid_y) in self.electrovoxels:
            # Électrovoxel existant, l'effacer
            self.canvas.delete(self.electrovoxels[(grid_x, grid_y)])
            del self.electrovoxels[(grid_x, grid_y)]
        else:
            # Nouvel électrovoxel, le dessiner
            voxel_id = self.canvas.create_rectangle(x1, y1, x2, y2, fill="blue", outline="")
            self.electrovoxels[(grid_x, grid_y)] = voxel_id
        self.update_electrovoxel_count()
        self.update_electrovoxel_count()
        self.update_unity_info()

    def update_electrovoxel_count(self):
        # Mettre à jour le label avec le nombre actuel d'électrovoxels
        count = len(self.electrovoxels)
        self.electrovoxel_count_label.config(text=f"Electrovoxels: {count}")

    def is_shape_unified(self):
        if not self.electrovoxels:
            return False  # Aucun électrovoxel présent

        # Sélectionner un électrovoxel de départ
        start = next(iter(self.electrovoxels))

        # Parcourir les électrovoxels connectés
        visited = set()
        self.dfs(start, visited)

        # Vérifier si tous les électrovoxels ont été visités
        return len(visited) == len(self.electrovoxels)

    def dfs(self, voxel, visited):
        if voxel not in visited:
            visited.add(voxel)
            for neighbor in self.get_neighbors(voxel):
                if neighbor in self.electrovoxels:
                    self.dfs(neighbor, visited)

    def get_neighbors(self, voxel):
        x, y = voxel
        return [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]  # Les voisins : haut, bas, gauche, droite

    def update_unity_info(self):
            if self.is_shape_unified():
                self.unity_info_label.config(text="Forme Unie: Oui")
            else:
                self.unity_info_label.config(text="Forme Unie: Non")


    def save_grid(self):
        # Vérifier si la forme est unie
        if not self.is_shape_unified():
            mb.showerror("Erreur", "La forme n'est pas unie et ne peut pas être sauvegardée.")
            return

        # Demander à l'utilisateur de saisir le nom de la forme
        shape_name = sd.askstring("Nom de la Forme", "Entrez le nom de la forme:")
        if shape_name:
            # Créer un DataFrame à partir des électrovoxels
            data = {"X": [], "Y": []}
            for voxel in self.electrovoxels:
                data["X"].append(voxel[0])
                data["Y"].append(voxel[1])
            
            df = pd.DataFrame(data)

            # Construire le nom du fichier avec le nombre d'électrovoxels
            filename = f"forme/{shape_name}_{len(self.electrovoxels)}_electrovoxels.csv"
            df.to_csv(filename, index=False)
            print(f"Grid sauvegardé dans {filename}")
        else:
            print("Sauvegarde annulée.")

    def load_grid(self):
        # Ouvrir une boîte de dialogue pour sélectionner un fichier
        filename = fd.askopenfilename(title="Ouvrir un fichier", filetypes=[("CSV Files", "*.csv")])
        if filename:
            # Lire le fichier CSV
            df = pd.read_csv(filename)

            # Effacer le canevas actuel
            self.clear_grid()

            # Dessiner les électrovoxels à partir du fichier
            for _, row in df.iterrows():
                self.add_electrovoxel(row['X'], row['Y'])

            # Mise à jour du compteur et de l'information d'unité
            self.update_electrovoxel_count()
            self.update_unity_info()

    def add_electrovoxel(self, x, y):
        # Coordonnées pour dessiner l'électrovoxel
        x1, y1 = x * self.voxel_size, y * self.voxel_size
        x2, y2 = x1 + self.voxel_size, y1 + self.voxel_size

        # Dessiner l'électrovoxel
        voxel_id = self.canvas.create_rectangle(x1, y1, x2, y2, fill="blue", outline="")
        self.electrovoxels[(x, y)] = voxel_id

if __name__ == "__main__":
    root = tk.Tk()
    app = ElectroVoxelApp(root)
    root.mainloop()
