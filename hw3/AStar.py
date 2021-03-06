''' A* Algorithm implementation
by  Qiubai Yu

email: qiubay@uw.edu
std#: 1663777
UWNetID: qiubay
Version 1.0

This file Includes a priority queue implementation by 
 S. Tanimoto, Univ. of Washington.
Paul G. Allen School of Computer Science and Engineering

Intended USAGE:
 python3 AStar.py FranceWithDXHeuristic


'''

VERBOSE = True  # Set to True to see progress; but it slows the search.

import sys

if sys.argv==[''] or len(sys.argv)<2:
  try:
    import FranceWithDXHeuristic as Problem
  except:
    print("Note that the EightPuzzle formulation will be used in Assignment 3, not Assignment 2")
    print("Try python3 UCS.py FranceWithCosts")

else:
  import importlib
  Problem = importlib.import_module(sys.argv[1])

print("\nWelcome to A*, by Qiubai Yu!")

COUNT = None # Number of nodes expanded.
MAX_OPEN_LENGTH = None # How long OPEN ever gets.
SOLUTION_PATH = None # List of states from initial to goal, along lowest-cost path.
TOTAL_COST = None # Sum of edge costs along the lowest-cost path.
BACKLINKS = {} # Predecessor links, used to recover the path.

# The value g(s) represents the cost along the best path found so far
# from the initial state to state s.
g = {} # We will use a global hash table to associate g values with states.
# add another hash table f represent the priority value, f = g + h
#f = {}
# globally assign the heuristic function
h = Problem.h


class My_Priority_Queue:
  def __init__(self):
    self.q = [] # Actual data goes in a list.

  def __contains__(self, elt):
    '''If there is a (state, priority) pair on the list
    where state==elt, then return True.'''
    #print("In My_Priority_Queue.__contains__: elt= ", str(elt))
    for pair in self.q:
      if pair[0]==elt: return True
    return False

  def delete_min(self):
    ''' Standard priority-queue dequeuing method.'''
    if self.q==[]: return [] # Simpler than raising an exception.
    temp_min_pair = self.q[0]
    temp_min_value = temp_min_pair[1]
    temp_min_position = 0
    for j in range(1, len(self.q)):
      if self.q[j][1] < temp_min_value:
        temp_min_pair = self.q[j]
        temp_min_value = temp_min_pair[1]  
        temp_min_position = j
    del self.q[temp_min_position]
    return temp_min_pair

  def insert(self, state, priority):
    '''We do not keep the list sorted, in this implementation.'''
    #print("calling insert with state, priority: ", state, priority)

    if self[state] != -1:
      print("Error: You're trying to insert an element into a My_Priority_Queue instance,")
      print(" but there is already such an element in the queue.")
      return
    self.q.append((state, priority))

  def __len__(self):
    '''We define length of the priority queue to be the
    length of its list.'''
    return len(self.q)

  def __getitem__(self, state):
    '''This method enables Pythons right-bracket syntax.
    Here, something like  priority_val = my_queue[state]
    becomes possible. Note that the syntax is actually used
    in the insert method above:  self[state] != -1  '''
    for (S,P) in self.q:
      if S==state: return P
    return -1  # This value means not found.

  def __delitem__(self, state):
    '''This method enables Python's del operator to delete
    items from the queue.'''
    #print("In MyPriorityQueue.__delitem__: state is: ", str(state))
    for count, (S,P) in enumerate(self.q):
      if S==state:
        del self.q[count]
        return

  def __str__(self):
    txt = "My_Priority_Queue: ["
    for (s,p) in self.q: txt += '('+str(s)+','+str(p)+') '
    txt += ']'
    return txt

def runAStar():
  initial_state = Problem.CREATE_INITIAL_STATE()
  print("Initial State:")
  print(initial_state)
  global COUNT, BACKLINKS, MAX_OPEN_LENGTH, SOLUTION_PATH
  COUNT = 0
  BACKLINKS = {}
  MAX_OPEN_LENGTH = 0
  SOLUTION_PATH = AStar(initial_state)
  print(str(COUNT)+" states expanded.")
  print('MAX_OPEN_LENGTH = '+str(MAX_OPEN_LENGTH))

def AStar(initial_state):
  '''Best-First Search. This is the actual algorithm.'''
  global g, h, COUNT, BACKLINKS, MAX_OPEN_LENGTH, CLOSED, TOTAL_COST
  CLOSED = {}
  BACKLINKS[initial_state] = None

# STEP 1a. Put the start state on a priority queue called OPEN
  OPEN = My_Priority_Queue()
  OPEN.insert(initial_state, 0 + h(initial_state))
# STEP 1b. Assign g=0 to the start state.
  g[initial_state]=0.0

# STEP 2. If OPEN is empty, output “DONE” and stop.
  while not(OPEN == []): # ***STUDENTS CHANGE THIS CONDITION***
    # LEAVE THE FOLLOWING CODE IN PLACE TO INSTRUMENT AND/OR DEBUG YOUR IMPLEMENTATION
    if VERBOSE: report(OPEN, CLOSED, COUNT)
    if len(OPEN)>MAX_OPEN_LENGTH: MAX_OPEN_LENGTH = len(OPEN)

# STEP 3. Select the state on OPEN having lowest priority value and call it S.
#         Delete S from OPEN.
#         Put S on CLOSED.
#         If S is a goal state, output its description
    
    (S,P) = OPEN.delete_min()
    #print("In Step 3, returned from OPEN.delete_min with results (S,P)= ", (str(S), P))
    CLOSED[S] = P

    if Problem.GOAL_TEST(S):
      # ***STUDENTS CHANGE THE BODY OF THIS IF.***
      #HANDLE THE BACKTRACING, RECORDING THE SOLUTION AND TOTAL COST,
      # AND RETURN THE SOLUTION PATH, TOO.
      print(Problem.GOAL_MESSAGE_FUNCTION(S))
      path = backtrace(S)
      TOTAL_COST = g[S]
      print('Total cost of the solution path found: ' + str(TOTAL_COST))
      print('Length of solution path found: '+str(len(path)-1)+' edges')
      return
    COUNT += 1

# STEP 4. Generate each successor of S
    L = {}
    for op in Problem.OPERATORS:
      if op.precond(S):
        new_state = op.state_transf(S)
        g_temp = g[S] + S.edge_distance(new_state)
        if not(new_state in g and g_temp > g[new_state]):
          g[new_state] = g_temp
        fs_prime = g[new_state] + h(new_state)
        L[new_state] = fs_prime
        if new_state in CLOSED:
          if CLOSED[new_state] <= L[new_state]:
            del L[new_state]
          else:
            del CLOSED[new_state]
        elif new_state in OPEN:
          if fs_prime <= OPEN.__getitem__(new_state):
            OPEN.__delitem__(new_state)
          else:
            del L[new_state]
    
    #STEP 5. Insert all members of L onto OPEN
    for elem in L:
      priority_value = L[elem]
      OPEN.insert(elem, priority_value)
      BACKLINKS[elem] = S
          

  
   # ***STUDENTS IMPLEMENT THE GENERATION AND HANDLING OF SUCCESSORS HERE,
   # USING THE GIVEN PRIORITY QUEUE FOR THE OPEN LIST, AND
   # DETERMINING THE SHORTEST DISTANCE KNOWN SO FAR FROM THE INITIAL STATE TO
   # EACH SUCCESSOR.***

  # STEP 6. Go to Step 2.
  return None  # No more states on OPEN, and no goal reached.

def print_state_queue(name, q):
  print(name+" is now: ",end='')
  print(str(q))

def backtrace(S):
  global BACKLINKS
  path = []
  while S:
    path.append(S)
    S = BACKLINKS[S]
  path.reverse()
  print("Solution path: ")
  for s in path:
    print(s)
  return path
  
def report(open, closed, count):
  print("len(OPEN)="+str(len(open)), end='; ')
  print("len(CLOSED)="+str(len(closed)), end='; ')
  print("COUNT = "+str(count))

if __name__=='__main__':
  runAStar()

