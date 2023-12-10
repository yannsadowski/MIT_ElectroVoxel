from contextlib import closing
from io import StringIO
from os import path
from typing import List, Optional
import os
import re

import random
import numpy as np
import pandas as pd

from gym import Env, logger, spaces, utils
from utils import categorical_sample
from gym.error import DependencyNotInstalled
from electrovoxel import ElectroVoxel

LEFT_pivot = 0
DOWN_pivot = 1
RIGHT_pivot = 2
UP_pivot = 3
LEFT_transverse = 4
DOWN_transverse = 5
RIGHT_transverse = 6
UP_transverse = 7



def initialShape_finalShape(size: int = 9, shape1: str = "None", shape2: str = "None"):
    """Chose a  random initial shape for electrovoxel and a random final shape to get if the shape1 or shape2 is not NULL
     

    Args:
        size: number of electrovoxels shape
        shape1: path to the initial shape
        shape2: path to the final shape

    Returns:
        return the positions of each electrovoxel of both shapes
    """
    # regex to find filename on the size
    file_name_regex = rf'.+_{size}_electrovoxels\.csv'

    # list of file in shape
    formes_directory = 'electrovoxel/shape/'
    available_files = [f for f in os.listdir(formes_directory) if re.match(file_name_regex, f)]

    # random shape if None
    if shape1 == "None":
        shape1 = random.choice(available_files)
    else:
        shape1 += ".csv"
        if not re.match(file_name_regex, shape1) or shape1 not in available_files:
            raise ValueError(f"Shape1 '{shape1}' does not match the size {size} or is not available.")

    if shape2 == "None":
        shape2 = random.choice([f for f in available_files if f != shape1])
    else:
        shape2 += ".csv"
        if not re.match(file_name_regex, shape2) or shape2 not in available_files or shape2 == shape1:
            raise ValueError(f"Shape2 '{shape2}' does not match the size {size}, is not available, or is the same as Shape1.")

    # Read CSV file for selected shape
    df_shape1 = pd.read_csv(formes_directory + shape1)
    df_shape2 = pd.read_csv(formes_directory + shape2)

    # Get pos for each shape
    initial_shape_positions = df_shape1.values
    final_shape_positions = df_shape2.values

    return initial_shape_positions, final_shape_positions

class ElectroVoxelenv(Env):
    """
    Electrovoxel are self-reconstructible robots that can pivot and transverse from MIT CSAIL
    
    The ElectroVoxel environment involves manipulating a grid of electrovoxels to transform an initial configuration into a target shape. 
    Electrovoxels can exist in either an 'active' (A) or 'inactive' (I) state. 
    The objective is to alter the state of electrovoxels so that the grid matches a specified configuration, representing the target shape.
    The agent is tasked with deciding which electrovoxel to activate or deactivate and what movement make at each step. 




    ### Action Space
    The agent takes a 1-element vector for actions. Each action represents a specific kind of movement or transformation applied to the electrovoxels. 
    The action space is defined as follows:

    - 0: LEFT_PIVOT - Pivot the configuration or selected electrovoxels to the left.
    - 1: DOWN_PIVOT - Pivot the configuration or selected electrovoxels downward.
    - 2: RIGHT_PIVOT - Pivot the configuration or selected electrovoxels to the right.
    - 3: UP_PIVOT - Pivot the configuration or selected electrovoxels upward.
    - 4: LEFT_TRANSVERSE - Move or transform the configuration or selected electrovoxels to the left without pivoting.
    - 5: DOWN_TRANSVERSE - Move or transform the configuration or selected electrovoxels downward without pivoting.
    - 6: RIGHT_TRANSVERSE - Move or transform the configuration or selected electrovoxels to the right without pivoting.
    - 7: UP_TRANSVERSE - Move or transform the configuration or selected electrovoxels upward without pivoting.

    These actions allow the agent to manipulate the electrovoxel grid in various ways, 
    either by pivoting (rotating) sections of the grid or by transverse movements (shifting positions without rotation).

  
    

    ### Observation Space
    The observation space is dict that represente the environment arround the electrovoxel the agent uses and a matrix that represente the state of the environment
    Exemple of the state of environment carre_9_electrovoxels.csv:
            -2             -1              0           1              2
        -2 -1  0  1  2 -2 -1  0  1  2 -2 -1  1  2 -2 -1  0  1  2 -2 -1  0  1  2
        0  0  0  0  0  0  0  0  0  0  0  0  0  1  1  0  0  1  1  1  0  0  1  1  1
        1  0  0  0  0  0  0  0  0  0  0  0  1  1  0  0  1  1  1  0  0  1  1  1  0
        2  0  0  0  0  0  0  0  0  0  0  1  1  0  0  1  1  1  0  0  1  1  1  0  0
        3  0  0  0  0  0  0  0  1  1  1  0  0  1  1  0  0  1  1  1  0  0  0  0  0
        4  0  0  0  0  0  0  1  1  1  0  0  1  1  0  0  1  1  1  0  0  0  0  0  0
        5  0  0  0  0  0  1  1  1  0  0  1  1  0  0  1  1  1  0  0  0  0  0  0  0
        6  0  0  1  1  1  0  0  1  1  1  0  0  1  1  0  0  0  0  0  0  0  0  0  0
        7  0  1  1  1  0  0  1  1  1  0  0  1  1  0  0  0  0  0  0  0  0  0  0  0
        8  1  1  1  0  0  1  1  1  0  0  1  1  0  0  0  0  0  0  0  0  0  0  0  0
    Exemple of the state of a electrovoxels:
    {(-2, -2): False, (-1, -2): False, (0, -2): False, (1, -2): False, (2, -2): False, (-2, -1): False, 
    (-1, -1): False, (0, -1): False, (1, -1): False, (2, -1): False, (-2, 0): False, (-1, 0): False, 
    (1, 0): True, (2, 0): True, (-2, 1): False, (-1, 1): False, (0, 1): True, (1, 1): True, (2, 1): True, 
    (-2, 2): False, (-1, 2): False, (0, 2): True, (1, 2): True, (2, 2): True}

    ### Rewards

    Reward Schedule:
    - Increase in similarity between initial_shape and final_shape: Reward based on the degree of improvement.
    - Complete match (initial_shape == final_shape): +1 (or a higher reward)
    - No change or decrease in similarity: 0 (or a slight negative reward)

    The reward is calculated based on the change in similarity between the current state and the target configuration (final_shape). 
    Actions that lead to an increased alignment with the final_shape are rewarded proportionally. 
    The goal is to encourage the agent to take actions that progressively transform the initial_shape towards the final_shape.


    ### Arguments

    ```
    gym.make('ElectroVoxel_2D-v0', Size=9, map_name= ["None","None"])
    ```

    `Size`: Used to specify the number of Electrovoxel in the env. For example,

        Size=9.
        Will be used to chose a initial shape and a target shape based on the size.
       
       
    `map_name`: string list of map we want to use. For example,
        map_name= ["carre_9_electrovoxels","croix_9_electrovoxels"]
        Or
        map_name= ["None","croix_9_electrovoxels"]
        Or 
        map_name= ["carre_9_electrovoxels","None"]

        A random generated map is chose when None is in input by calling the function `generate_random_map`
        
    ### Version History
    * v0: Initial versions release (1.0.0)
    """
    metadata = {
        "render_modes": ["human"]
    }
    
    def __init__(
        self,
        render_mode: Optional[str] = None,
        Size=9,
        map_name=["None","None"]
    ):
        self.grid_size = (20, 20)
        self.voxel_size = 40
        initial_shape, target_shape = initialShape_finalShape(Size,map_name[0],map_name[1])
        self.vortexes = [ElectroVoxel(x * voxel_size, y * voxel_size, charge=1, size=voxel_size, color="white") for x, y in initial_shape]
        self.vortexes_target = [ElectroVoxel(x * voxel_size, y * voxel_size, charge=1, size=voxel_size, color="white") for x, y in target_shape]
        self.size = size
        
        self.reward_range = (0, 1)
        
        nA = 8
        nS = vortexes.shape[0] * vortexes.shape[1] # Maybe juste take the number of colums (24)


        self.P = {s: {a: [] for a in range(nA)} for s in range(nS)}
        
        
        def detect_connections(vortex, vortexes, voxel_size):
            # Init connections with all positions at False
            connections = {(dx, dy): False for dy in range(-2, 3) for dx in range(-2, 3) if (dx, dy) != (0, 0)}

            for other in vortexes:
                if other != vortex:
                    # Calculate the difference in x and y
                    dx = (other.x - vortex.x) // voxel_size
                    dy = (other.y - vortex.y) // voxel_size
                    
                    # Check if the coordinates are in the detection radius
                    if abs(dx) <= 2 and abs(dy) <= 2 and (dx, dy) in connections:
                        # Update the connection if the distance is within the radius
                        connections[(dx, dy)] = True

            return connections
    
        def env_state(vortexes):
            # Determine all unique keys (relative positions) for columns
            all_keys = sorted({key for vortex in vortexes for key in detect_connections(vortex, vortexes, voxel_size)})

            # Prepare data for DataFrame
            data = {key: [] for key in all_keys}
            
            for vortex in vortexes:
                connections = detect_connections(vortex, vortexes, voxel_size)

                # Add connection data for this electrovoxel
                for key in all_keys:
                    data[key].append(int(connections.get(key, False)))  # Convert True/False to 1/0

            # Make a new DataFrame with data
            df = pd.DataFrame(data)
            
            # Convert each line into a binary score
            num_columns = len(df.columns)
            df['Sort_Score'] = df.apply(lambda row: sum(row[col] * (2 ** (num_columns - i)) for i, col in enumerate(df.columns, 1)), axis=1)

            # Sort the DataFrame based on the sort score
            df = df.sort_values(by='Sort_Score')

            # Remove the 'Sort_Score' column if you do not want to include it in the final file
            df = df.drop(columns=['Sort_Score'])
            
            # Remove Index
            df = df.reset_index(drop=True)
            
            return df
        
            """_Need to Fix_
            I think it will be better to check the difference between line and not values
            """        
        def calculate_difference_percentage(df1, df2):
            # Check if both DataFrame have the same form
            if df1.shape != df2.shape:
                raise ValueError("Les tableaux doivent avoir la même taille.")

            # Calculate the absolute difference between the two tables
            difference = (df1 != df2).sum().sum()

            # Calculate the total number of elements
            total_elements = df1.shape[0] * df1.shape[1]

            # Calculate the percentage of difference
            percentage_difference = (difference / total_elements) * 100

            return percentage_difference
        
        def inc(electrovoxel, a):
            if a == LEFT_pivot:
                electrovoxel.pivot("left")
            elif a == DOWN_pivot:
                electrovoxel.pivot("down")
            elif a == RIGHT_pivot:
                electrovoxel.pivot("right")
            elif a == UP_pivot:
                electrovoxel.pivot("up")
            elif a == LEFT_transverse:
                electrovoxel.pivot("left")
            elif a == DOWN_transverse:
                electrovoxel.pivot("down")
            elif a == RIGHT_transverse:
                electrovoxel.pivot("right")
            elif a == UP_transverse:
                electrovoxel.pivot("up")
