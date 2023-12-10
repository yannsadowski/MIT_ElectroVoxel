import pygame
import numpy as np
import pandas as pd
from electrovoxel import ElectroVoxel


def detect_connections(vortex, vortexes, voxel_size):
    # Initialiser les connections avec toutes les positions possibles à False
    connections = {(dx, dy): False for dy in range(-2, 3) for dx in range(-2, 3) if (dx, dy) != (0, 0)}

    for other in vortexes:
        if other != vortex:
            # Calculer la différence en x et y
            dx = (other.x - vortex.x) // voxel_size
            dy = (other.y - vortex.y) // voxel_size
            
            # Vérifier si les coordonnées sont dans le rayon de détection
            if abs(dx) <= 2 and abs(dy) <= 2 and (dx, dy) in connections:
                # Mise à jour de la connexion si la distance est dans le rayon
                connections[(dx, dy)] = True

    return connections

def afficher_menu(x, y, surface):
    menu_options = ["Pivot Haut", "Pivot Bas", "Pivot Gauche", "Pivot Droite",
                    "Transverse Haut", "Transverse Bas", "Transverse Gauche", "Transverse Droite","return"]
    menu_rects = []
    
    for i, option in enumerate(menu_options):
        # Position et taille de chaque élément du menu
        rect = pygame.Rect(x, y + 30 * i, 150, 30)
        menu_rects.append(rect)

        # Dessiner le rectangle du menu
        pygame.draw.rect(surface, (200, 200, 200), rect)

        # Dessiner le texte de l'option
        font = pygame.font.Font(None, 24)
        text = font.render(option, True, (0, 0, 0))
        surface.blit(text, (rect.x + 5, rect.y + 5))
    pygame.display.flip()
    return menu_rects

def create_form(filename):
    # Lire les données depuis le fichier CSV
    df = pd.read_csv(filename)

    # Création d'instances d'ElectroVortex à partir du fichier CSV
    vortexes = [ElectroVoxel(x * voxel_size, y * voxel_size, charge=1, size=voxel_size, color="white") for x, y in zip(df['X'], df['Y'])]
    return vortexes

def env_state(vortexes):
    # Déterminer toutes les clés uniques (positions relatives) pour les colonnes
    all_keys = sorted({key for vortex in vortexes for key in detect_connections(vortex, vortexes, voxel_size)})

    # Préparer les données pour le DataFrame
    data = {key: [] for key in all_keys}
    
    for vortex in vortexes:
        connections = detect_connections(vortex, vortexes, voxel_size)

        # Ajouter les données de connexion pour cet électrovoxel
        for key in all_keys:
            data[key].append(int(connections.get(key, False)))  # Convertir True/False en 1/0

    # Créer un DataFrame avec les données
    df = pd.DataFrame(data)
    
    # Convertir chaque ligne en un score binaire
    num_columns = len(df.columns)
    df['Sort_Score'] = df.apply(lambda row: sum(row[col] * (2 ** (num_columns - i)) for i, col in enumerate(df.columns, 1)), axis=1)

    # Trier le DataFrame en fonction du score de tri
    df = df.sort_values(by='Sort_Score')

    # Enlever la colonne 'Sort_Score' si vous ne voulez pas l'inclure dans le fichier final
    df = df.drop(columns=['Sort_Score'])
    
    # Enlever l'index
    df = df.reset_index(drop=True)
    
    return df

def calculate_difference_percentage(df1, df2):
    # Vérifier si les deux DataFrame ont la même forme
    if df1.shape != df2.shape:
        raise ValueError("Les tableaux doivent avoir la même taille.")

    # Calculer la différence absolue entre les deux tableaux
    difference = (df1 != df2).sum().sum()

    # Calculer le nombre total d'éléments
    total_elements = df1.shape[0] * df1.shape[1]

    # Calculer le pourcentage de différence
    percentage_difference = (difference / total_elements) * 100

    return percentage_difference

# Initialize Pygame
pygame.init()

# Grid parameters
grid_size = (20, 20)
voxel_size = 40  # Size of each voxel for display
screen_size = (grid_size[0] * voxel_size, grid_size[1] * voxel_size)

# Set up the display
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("Electrovoxel Simulation")


vortexes = create_form("draft/forme/carre_9_electrovoxels.csv")
state_vortexes = env_state(vortexes)
vortexes_final = create_form("draft/forme/croix_9_electrovoxels.csv")
state_vortexes_final = env_state(vortexes_final)
print(state_vortexes)
print(calculate_difference_percentage(state_vortexes, state_vortexes_final))

for vortex in vortexes:
    connections = detect_connections(vortex, vortexes,voxel_size)
    vortex.update(connections)
print(vortexes[0].state)

# Initialize the grid
grid = np.random.rand(*grid_size)
# Couleurs
background_color = (255, 255, 255)  # Blanc
grid_color = (200, 200, 200)  # Gris clair

#variable pour savoir où ce trouve le click utilisateur
x_click=0
y_click=0




running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Obtenez les coordonnées du clic de souris
            x_click, y_click = event.pos
            #print(x, y)
    # Détecter et mettre à jour les connexions pour chaque ElectroVoxel
    for vortex in vortexes:
        connections = detect_connections(vortex, vortexes,voxel_size)
        vortex.update(connections)

    # Affichage
    screen.fill(background_color)  # Fond blanc
    # Dessiner le grid
    for x in range(0, screen_size[0], voxel_size):
        for y in range(0, screen_size[1], voxel_size):
            pygame.draw.rect(screen, grid_color, (x, y, voxel_size, voxel_size), 1)
    # Dessiner les vortexes
    for vortex in vortexes:
        vortex.draw(screen)

    

    # Vérifiez quel ElectroVoxel a été cliqué
    for electrovoxel in vortexes:
    # Créez un Rect pour représenter la zone de l'ElectroVoxel
        electrovoxel_rect = pygame.Rect(electrovoxel.x, electrovoxel.y, electrovoxel.size, electrovoxel.size)
        #pygame.draw.rect(screen, (255, 0, 0), electrovoxel_rect, 1)  # Dessiner le rect en rouge pour visualiser

        if electrovoxel_rect.collidepoint(x_click, y_click):
            menu_rects = afficher_menu(x_click, y_click, screen)
            selected = False
            while not selected:
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mx, my = event.pos
                        for i, rect in enumerate(menu_rects):
                            if rect.collidepoint(mx, my):
                                # L'utilisateur a sélectionné une option
                                menu_options = [(0, "up"), (0, "down"), (0, "left"), (0, "right"),
                                                    (1, "up"), (1, "down"), (1, "left"), (1, "right"),(2, "return")]
                                selected = True
                                if menu_options[i][0] == 0:
                                    electrovoxel.pivot(menu_options[i][1])
                                elif menu_options[i][0] == 1:
                                    electrovoxel.transverse(menu_options[i][1])


                    elif event.type == pygame.QUIT:
                        selected = True
                        running = False


    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()

