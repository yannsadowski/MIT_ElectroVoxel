import pygame

class ElectroVoxel:
    def __init__(self, x, y, charge, size, color):
        self.x = x
        self.y = y
        self.charge = charge
        self.size = size
        # Initialisez self.state avec des tuples pour chaque position relative
        self.state = {(dx, dy): False for dy in range(-2, 3) for dx in range(-2, 3) if (dx, dy) != (0, 0)}
        self.color = color


    def update(self, connections):
        # Mettez à jour seulement les états qui sont présents dans les deux dictionnaires
        for key in connections:
            if key in self.state:
                self.state[key] = connections[key]



    def draw(self, screen):
        # Définissez la couleur des coins et des arrêtes
        edge_color = (0, 0, 0)  # Noir pour les arrêtes
        corner_color = (0, 0, 128)  # Bleu foncé pour les coins

        # Calculez les coordonnées des coins du cube dans la case
        top_left = (self.x, self.y)
        top_right = (self.x + 40, self.y)
        bottom_left = (self.x, self.y + 40)
        bottom_right = (self.x + 40, self.y + 40)

        # Dessinez le cube (un rectangle dans ce cas)
        pygame.draw.rect(screen, edge_color, (self.x, self.y, 40, 40))

        # Dessinez les coins du cube
        corner_radius = 5  # Rayon pour les coins
        pygame.draw.circle(screen, corner_color, top_left, corner_radius)
        pygame.draw.circle(screen, corner_color, top_right, corner_radius)
        pygame.draw.circle(screen, corner_color, bottom_left, corner_radius)
        pygame.draw.circle(screen, corner_color, bottom_right, corner_radius)

        # Pour une meilleure esthétique, vous pourriez vouloir remplir le cube avec une certaine couleur
        # et puis dessiner les arrêtes par-dessus.
        # Pour cela, on dessine d'abord un rectangle plein puis les arrêtes.
        if self.color == "white":
            fill_color = (255,255,255)
        elif self.color == "red":
            fill_color = (255,0,0)
        elif self.color == "green":
            fill_color = (0,255,0)
        pygame.draw.rect(screen, fill_color, (self.x+1, self.y+1, 40-2, 40-2))
        pygame.draw.rect(screen, edge_color, (self.x, self.y, 40, 40), 1)

    def pivot(self, Axes):
        # regarde le mouvement est possible
        # Vérifiez si le pivot est possible dans une direction donnée

        result = self._can_pivot(Axes)
        if result:
            print(f"Le pivot vers {Axes} est possible.")
            if Axes == 'up':
                self.y=self.y-self.size
                self.x=self.x+(result[0]*self.size+result[1]*self.size)

            elif Axes == 'down':
                self.y=self.y+self.size
                self.x=self.x+(result[0]*self.size+result[1]*self.size)

            elif Axes == 'left':
                self.x=self.x-self.size
                self.y=self.y+(result[0]*self.size+result[1]*self.size)
            elif Axes == 'right':
                self.x=self.x+self.size
                self.y=self.y+(result[0]*self.size+result[1]*self.size)

            return True

        else:
            print(f"Le pivot vers {Axes} n'est pas possible.")
            return False

    def _can_pivot(self, direction):
        """
        Vérifier si le pivot est possible dans la direction donnée.

        :param direction: Une chaîne indiquant la direction du pivot ('up', 'down', 'left', 'right').
        :return: True si le pivot est possible, False autrement.
        """
        # Coordonnées relatives des axes perpendiculaires en fonction de la direction
        perpendicular_axes = {
            'up': [(1, 0), (-1, 0)],
            'down': [(1, 0), (-1, 0)],
            'left': [(0, 1), (0, -1)],
            'right': [(0, 1), (0, -1)]
        }
        vortex_per=0
        # Vérifiez si un vortex est présent sur l'un des axes perpendiculaires
        for axis in perpendicular_axes[direction]:
            if self.state.get(axis):
                base_axis=axis # Vortex qui est la base du mouvement de pivot
                vortex_per=vortex_per+1# Un vortex est détecté sur l'axe perpendiculaire, mais pas 2 alors mouvement possible
        # print(vortex_per)
        if vortex_per == 2 or vortex_per == 0:
            return False

        if direction == 'up':
            if base_axis == (1, 0):
                for axis in [(-1,0),(-1,-1),(0,-2),(1,-2),(0,-1),(1,-1)]:
                    if self.state.get(axis):
                        return False

            elif base_axis == (-1, 0):
                for axis in [(1,0),(1,-1),(0,-2),(-1,-2),(0,-1),(-1,-1)]:
                    if self.state.get(axis):
                        return False


        elif direction == 'down':
            if base_axis == (1, 0):
                for axis in [(-1,0),(-1,1),(0,2),(1,2),(0,1),(1,1)]:
                    if self.state.get(axis):
                        return False

            elif base_axis == (-1, 0):
                for axis in [(1,0),(1,1),(0,2),(-1,2),(0,1),(-1,1)]:
                    if self.state.get(axis):
                        return False


        elif direction == 'left':
            if base_axis == (0, 1):
                for axis in [(0,-1),(-1,-1),(-2,0),(-2,-1),(-1,0),(-1,1)]:
                    if self.state.get(axis):
                        return False

            elif base_axis == (0, -1):
                for axis in [(0,1),(-1,1),(-2,0),(-2,1),(-1,0),(-1,-1)]:
                    if self.state.get(axis):
                        return False


        elif direction == 'right':
            if base_axis == (0, 1):
                for axis in [(0,-1),(1,-1),(2,0),(2,-1),(1,0),(1,1)]:
                    if self.state.get(axis):
                        return False

            elif base_axis == (0, -1):
                for axis in [(0,1),(1,1),(2,0),(2,1),(1,0),(1,-1)]:
                    if self.state.get(axis):
                        return False

        return base_axis

    def transverse(self, Axes):
        # regarde le mouvement est possible
        # Vérifiez si le pivot est possible dans une direction donnée
        result = self._can_transverse(Axes)
        if result:
            print(f"La transverse vers {Axes} est possible.")
            if Axes == 'up':
                self.y=self.y-self.size

            elif Axes == 'down':
                self.y=self.y+self.size

            elif Axes == 'left':
                self.x=self.x-self.size

            elif Axes == 'right':
                self.x=self.x+self.size

            return True
        else:
            print(f"La transverse vers {Axes} n'est pas possible.")
            return False

    def _can_transverse(self, direction):
        """
        Vérifier si le pivot est possible dans la direction donnée.

        :param direction: Une chaîne indiquant la direction du pivot ('up', 'down', 'left', 'right').
        :return: True si le pivot est possible, False autrement.
        """
        # Coordonnées relatives des axes perpendiculaires en fonction de la direction
        perpendicular_axes = {
            'up': [(1, 0), (-1, 0),],
            'down': [(1, 0), (-1, 0)],
            'left': [(0, 1), (0, -1)],
            'right': [(0, 1), (0, -1)]
        }

        vortex_per=0
        # Vérifiez si un vortex est présent sur l'un des axes perpendiculaires
        for axis in perpendicular_axes[direction]:
            if self.state.get(axis):
                base_axis=axis # Vortex qui est la base du mouvement de pivot
                vortex_per=vortex_per+1# Un vortex est détecté sur l'axe perpendiculaire, mais pas 2 alors mouvement possible
        print(vortex_per)
        if vortex_per == 2 or vortex_per == 0:
            return False


        if direction == 'down':
            if base_axis == (1, 0):
                for axis in [(-1,0),(-1,-1),(0,-1)]:
                    if self.state.get(axis):
                        return False
                if self.state.get((1,1)):
                    return base_axis
            elif base_axis == (-1, 0):
                for axis in [(1,0),(1,-1),(0,-1)]:
                    if self.state.get(axis):
                        return False
                if self.state.get((-1,1)):
                    return base_axis

        elif direction == 'up':
            if base_axis == (1, 0):
                for axis in [(-1,0),(-1,1),(0,1)]:
                    if self.state.get(axis):
                        return False
                if self.state.get((1,-1)):
                    return base_axis
            elif base_axis == (-1, 0):
                for axis in [(1,0),(1,1),(0,1)]:
                    if self.state.get(axis):
                        return False
                if self.state.get((-1,-1)):
                    return base_axis

        elif direction == 'left':
            if base_axis == (0, 1):
                for axis in [(0,-1),(-1,-1),(-1,0)]:
                    if self.state.get(axis):
                        return False
                if self.state.get((-1,1)):
                    return base_axis
            elif base_axis == (0, -1):
                for axis in [(0,1),(-1,1),(-1,0)]:
                    if self.state.get(axis):
                        return False
                if self.state.get((-1,-1)):
                    return base_axis

        elif direction == 'right':
            if base_axis == (0, 1):
                for axis in [(0,-1),(1,-1),(1,0)]:
                    if self.state.get(axis):
                        return False
                if self.state.get((1,1)):
                    return base_axis
            elif base_axis == (0, -1):
                for axis in [(0,1),(1,1),(1,0)]:
                    if self.state.get(axis):
                        return False
                if self.state.get((1,-1)):
                    return base_axis
        return False
