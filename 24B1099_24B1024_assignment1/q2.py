"""
Sokoban Solver using SAT (Boilerplate)
--------------------------------------
Instructions:
- Implement encoding of Sokoban into CNF.
- Use PySAT to solve the CNF and extract moves.
- Ensure constraints for player movement, box pushes, and goal conditions.

Grid Encoding:
- 'P' = Player
- 'B' = Box
- 'G' = Goal
- '#' = Wall
- '.' = Empty space
"""

from pysat.formula import CNF
from pysat.solvers import Solver

# Directions for movement
DIRS = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}


class SokobanEncoder:
    def __init__(self, grid, T):
        """
        Initialize encoder with grid and time limit.

        Args:
            grid (list[list[str]]): Sokoban grid.
            T (int): Max number of steps allowed.
        """
        self.grid = grid
        self.T = T
        self.N = len(grid)
        self.M = len(grid[0])

        self.goals = []
        self.boxes = []
        self.player_start = None

        # TODO: Parse grid to fill self.goals, self.boxes, self.player_start
        self._parse_grid()

        self.num_boxes = len(self.boxes)
        self.cnf = CNF()

    def _parse_grid(self):
        """Parse grid to find player, boxes, and goals."""
        # TODO: Implement parsing logic
        N=self.N
        M=self.M
        grid=self.grid
        b=1
        for i in range(N):
            for j in range(M):
                if(grid[i][j]=='G'):
                    self.goals.append((i, j))
                elif(grid[i][j]=='B'):
                    self.boxes.append((i,j, b))
                    b+=1
                elif(grid[i][j]=='P'):
                    self.player_start=M*i+j+1

    # ---------------- Variable Encoding ----------------
    def var_player(self, x, y, t):
        """
        Variable ID for player at (x, y) at time t.
        """
        # TODO: Implement encoding scheme
        N=self.N
        M=self.M
        return M*N*t+M*x+y+1

    def var_box(self, b, x, y, t):
        """
        Variable ID for box b at (x, y) at time t.
        """
        # TODO: Implement encoding scheme
        N=self.N
        M=self.M
        T=self.T
        return (M*N*(T+1))*b+M*N*t+M*x+y+1

    # ---------------- Encoding Logic ----------------
    def encode(self):
        """
        Build CNF constraints for Sokoban:
        - Initial state
        - Valid moves (player + box pushes)
        - Non-overlapping boxes
        - Goal condition at final timestep
        """
        # TODO: Add constraints for:
        N,M,T,grid,goals,boxes,start,cnf=self.N,self.M,self.T,self.grid,self.goals,self.boxes,self.player_start,self.cnf
        var_box = self.var_box
        var_player=self.var_player
        # 1. Initial conditions
        #Condition on where player is initially
        cnf.append([start])
        # Condition on where boxes are initially
        for box in boxes:
            cnf.append([var_box(box[2],box[0], box[1], 0)])
        # 2. Player movement
        # Assumed that player can stay at rest or move at surrounding blocks with empty, box or goals.
        for t in range(T):
            for i in range(N):
                for j in range(M):
                    L=[-var_player(i,j,t), var_player(i,j,t+1)]
                    for key,(dx,dy) in DIRS.items():
                        if i+dx>=0 and i+dx<N and j+dy>=0 and j+dy<M:
                            if grid[i+dx][j+dy] == '.' or grid[i+dx][j+dy] == 'G' or grid[i+dx][j+dy] == 'B':
                                L.append(var_player(i+dx,j+dy,t+1))                            
                    cnf.append(L)
        # 3. Box movement (push rules)
        # Box cannot move unless pushed
        for b in range(1,len(boxes)+1):
            for t in range(T):
                for i in range(N):
                    for j in range(M):
                        cnf.append([-var_box(b,i,j,t),var_player(i,j,t+1),var_box(b,i,j,t+1)])
        # Box when it is pushed
        for b in range(1, len(boxes)+1):
            for t in range(T):
                for i in range(N):
                    for j in range(M):
                        for key,(dx,dy) in DIRS.items():
                            l=[]
                            if i+dx>=0 and i+dx<N and j+dy>=0 and j+dy<M:
                                l.extend([-var_player(i,j,t),-var_player(i+dx,j+dy,t+1),-var_box(b,i+dx,j+dy,t)])
                            if i+2*dx>=0 and i+2*dx<N and j+2*dy>=0 and j+2*dy<M:
                                l.append(var_box(b,i+2*dx,j+2*dy,t+1))
                            if len(l)>0:
                                cnf.append(l)
        # 4. Non-overlap constraints
        # box and wall cannot overlap
        for b in range(1, len(boxes)+1):
            for t in range(T+1):
                for i in range(N):
                    for j in range(M):
                        if grid[i][j] == '#':
                            cnf.append([-var_box(b, i, j, t)])
        # wall and player cannot overlap
        for t in range(T+1):
                for i in range(N):
                    for j in range(M):
                        if grid[i][j] == '#':
                            cnf.append([-var_player(i, j, t)])
        # Boxes and player can't overlap
        for b in range(1,len(boxes)+1):
            for t in range(T+1):
                for i in range(N):
                    for j in range(M):
                        cnf.append([-var_box(b,i,j,t),-var_player(i,j,t)])
        # two boxes cannot overlap
        for b1 in range(1,len(boxes)+1):
            for b2 in range(b1+1, len(boxes)+1):
                for t in range(T+1):
                    for i in range(N):
                        for j in range(M):
                            cnf.append([-var_box(b1,i,j,t),-var_box(b2,i,j,t)])
        # 5. Goal conditions
        # once box reaches goal it stays there.    
        for goal in goals:
            i = goal[0]
            j = goal[1]
            for b in range(1,len(boxes)+1):
                for t in range(T):
                    for t1 in range(t+1,T):
                        cnf.append([-var_box(b,i,j,t),var_box(b,i,j,t1)])
        #all boxes must be at some goal at time T
        for b in range(1, len(boxes)+1):
            l=[]
            for goal in goals:
                i = goal[0]
                j = goal[1]
                l.append(var_box(b,i,j,T))
            cnf.append(l)
        # 6. Other conditions
        # Condition that a player can be at one place only at given time
        for t in range(T+1):
            for i1 in range(N):
                for j1 in range(M):
                    for i2 in range(N):
                        for j2 in range(M):
                            if i1 == i2 and j1 == j2:
                                continue
                            cnf.append([-var_player(i1, j1, t), -var_player(i2, j2, t)])
        # Condition that a box can only be at one place at given time
        for b in range(1,len(boxes)+1):
            for t in range(T+1):
                for i1 in range(N):
                    for j1 in range(M):
                        for i2 in range(N):
                            for j2 in range(M):
                                if i1 == i2 and j1 == j2:
                                    continue
                                cnf.append([-var_box(b, i1, j1, t), -var_box(b, i2, j2, t)])

        return cnf

def decode(model, encoder):
    """
    Decode SAT model into list of moves ('U', 'D', 'L', 'R').

    Args:
        model (list[int]): Satisfying assignment from SAT solver.
        encoder (SokobanEncoder): Encoder object with grid info.

    Returns:
        list[str]: Sequence of moves.
    """
    if not model:
        return -1
    N, M, T = encoder.N, encoder.M, encoder.T
    var_player=encoder.var_player
    start=encoder.player_start
    # TODO: Map player positions at each timestep to movement directions
    start-=1
    j=start%M
    i=start//M
    result=''
    # Filling the string "result" with movements of the player.
    for t in range(T):
        for key,(dx,dy) in DIRS.items():
            if var_player(i+dx,j+dy,t+1) in model and i+dx>=0 and j+dy>=0 and i+dx<N and j+dy<M:
                i+=dx
                j+=dy
                result+=key
                break
    return result

def solve_sokoban(grid, T):
    """
    DO NOT MODIFY THIS FUNCTION.

    Solve Sokoban using SAT encoding.

    Args:
        grid (list[list[str]]): Sokoban grid.
        T (int): Max number of steps allowed.

    Returns:
        list[str] or "unsat": Move sequence or unsatisfiable.
    """
    encoder = SokobanEncoder(grid, T)
    cnf = encoder.encode()

    with Solver(name='g3') as solver:
        solver.append_formula(cnf)
        if not solver.solve():
            return -1

        model = solver.get_model()
        if not model:
            return -1

        return decode(model, encoder)