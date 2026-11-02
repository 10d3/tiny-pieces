# Probe bank

Ready-made probes for the gap map (Step 4) and exit exercises for learning nodes (Step 6).

## How to use

- **Look up the concept** by heading (`grep -n "^### derivative" references/probes.md`). Also check the dev's own `~/.tiny-pieces/probes.md` (same format). If the concept is in neither, improvise in this format, and when the probe worked well, append it to `~/.tiny-pieces/probes.md` (never edit this file in place: the skill folder may be read-only).
- **Probe** = detects the gap. 1-2 minutes, one concept, ask it cold, no hints before the answer. **Never use multiple-choice questions (MCQs)**: recognition of a listed answer is not proof of understanding. Probes must require active generation (compute, predict, trace, or explain).
- **Exit exercise** = proves the node is learned. It is always a **different** question from the probe, so the dev can't just remember the answer. No multiple choice.
- **Grading:** ✅ right and they can say what it means · ⚠️ right but mechanical, or half right (see "⚠️ if") · ❌ wrong, blank, or "idk".
- **Needs** are *suggested* direct prerequisites. Record them once with `tp.py needs <concept> a,b`, then they are reused for every goal.
- **Scope** = how deep to go "just enough for the root". Override it per goal with `tp.py map scope`.
- Numbers can be changed (new numbers = a fresh probe). Re-check the arithmetic if you do.
- Headings are the canonical concept names, in English. French names are in the `FR:` line: add them with `tp.py alias`.

**Index:**
Math: function · slope of a line · limit · derivative · chain rule · partial derivative · gradient · integral · vector · dot product · matrix multiplication · eigenvalues · probability basics · expected value · mean and standard deviation
Python: variables and types · functions and scope · lists and dicts · mutability and references · loops and comprehensions · classes and objects · dunder methods · closures · recursion · reading a traceback
CS: graph · stack and queue · graph traversal · dag · topological sort · big o
ML: computational graph · loss function · gradient descent · backpropagation · neuron
Physics: units and dimensional analysis · vector components · free-body diagram · newtons second law · conservation of energy · conservation of momentum · coulombs law · electric field · electric flux · gauss law · ohms law and circuits
Technique: sliding window · two pointers · binary search · memoization · prefix sum

---

## Math

### function
*FR: fonction · needs: none*
**Probe:** f(x) = 2x + 1. What is f(3)? What is f(a + 1)? In one sentence, what is a function?
**Expect:** 7; 2a + 3; a rule that gives exactly one output for each input.
**⚠️ if:** f(3) is fine but f(a + 1) is stuck (can't substitute an expression), or no definition.
**Exit exercise:** g(x) = x² − x. Find g(2), g(−1) and g(t + 1) simplified. (2; 2; t² + t)
**Scope:** input/output rule, substitution, composing two functions.

### slope of a line
*FR: pente d'une droite · needs: none*
**Probe:** A line goes through (1, 2) and (4, 8). What is its slope, and what does that number tell you in words?
**Expect:** 2, from (8 − 2)/(4 − 1). For each 1 step right, the line goes 2 up.
**⚠️ if:** gets 2 but can't say what it means, or flips rise and run.
**Exit exercise:** A line passes through (0, 5) with slope −3. What is y at x = 2, and does the line go up or down? (−1; down)
**Scope:** rise over run, sign, meaning as a rate.

### limit
*FR: limite · needs: function*
**Probe:** What does f(x) = (x² − 1)/(x − 1) approach as x gets close to 1, even though f(1) is undefined? Why?
**Expect:** 2. For x ≠ 1 it simplifies to x + 1.
**⚠️ if:** says "undefined", or gets 2 only by plugging numbers with no reason.
**Exit exercise:** What does (x² − 9)/(x − 3) approach as x → 3? (6)
**Scope:** intuition only ("what it approaches"), no epsilon-delta unless the goal needs it.

### derivative
*FR: dérivée · needs: slope of a line, function (and limit if the goal needs the definition)*
**Probe:** What is the derivative of x² at x = 3? What does that number mean on the graph of y = x²?
**Expect:** 6. The slope of the tangent line at x = 3 (the instantaneous rate of change).
**⚠️ if:** 6 from the power rule, but no meaning; or "slope" with no idea of tangent / instantaneous.
**Exit exercise:** f(x) = x³ − 2x. Find f'(x) and f'(2). Is f increasing or decreasing at x = 2? (3x² − 2; 10; increasing)
**Scope:** slope meaning + power rule + sums. No epsilon-delta unless the goal needs it.

### chain rule
*FR: dérivée d'une composée · needs: derivative, function*
**Probe:** Differentiate (3x + 1)². Then say in words why a 3 shows up in the answer.
**Expect:** 2(3x + 1)·3 = 6(3x + 1) = 18x + 6. The derivative of the inner function multiplies the outer one.
**⚠️ if:** gets 18x + 6 only by expanding. Follow up: d/dx sin(2x) = 2cos(2x).
**Exit exercise:** d/dx (x² + 1)³ and d/dx e^(x²). (6x(x² + 1)²; 2x·e^(x²))
**Scope:** "multiply the local derivatives along the path". Enough for backpropagation.

### partial derivative
*FR: dérivée partielle · needs: derivative, function*
**Probe:** f(x, y) = x²y + 3y. Find ∂f/∂x and ∂f/∂y at (2, 1).
**Expect:** ∂f/∂x = 2xy = 4; ∂f/∂y = x² + 3 = 7.
**⚠️ if:** differentiates y too when taking ∂/∂x (doesn't hold the other variable constant).
**Exit exercise:** f(x, y) = xy² + sin(x). Find ∂f/∂x and ∂f/∂y. (y² + cos x; 2xy)
**Scope:** "treat the other variables as constants".

### gradient
*FR: gradient · needs: partial derivative, vector*
**Probe:** For f(x, y) = x² + y², what is the gradient at (1, 2)? Which way does it point, and what is it used for?
**Expect:** (2, 4). Direction of steepest increase; move the opposite way to decrease f (gradient descent).
**⚠️ if:** correct vector but no sense of direction/purpose.
**Exit exercise:** f(x, y) = 3x + xy. Gradient at (2, −1)? ((3 + y, x) = (2, 2))
**Scope:** vector of partial derivatives + "points uphill".

### integral
*FR: intégrale · needs: derivative, function*
**Probe:** Compute ∫ from 0 to 3 of 2x dx. What does it measure geometrically?
**Expect:** 9. The area under y = 2x from 0 to 3 (a triangle: ½·3·6).
**⚠️ if:** gets 9 but sees it only as "reverse the derivative" with no area meaning.
**Exit exercise:** ∫ from 1 to 2 of (3x² + 1) dx. ([x³ + x] from 1 to 2 = 10 − 2 = 8)
**Scope:** antiderivative + area + definite integral by evaluation.

### vector
*FR: vecteur · needs: none*
**Probe:** a = (1, 2) and b = (3, −1). Compute a + b and 2a. What is the length of a?
**Expect:** (4, 1); (2, 4); √5.
**⚠️ if:** adds fine but misses the length formula.
**Exit exercise:** u = (3, 4). Give its length and the unit vector in the same direction. (5; (3/5, 4/5))
**Scope:** components, addition, scaling, length.

### dot product
*FR: produit scalaire · needs: vector*
**Probe:** Compute (1, 2, 3)·(4, 0, −1). What does a zero dot product between two non-zero vectors tell you?
**Expect:** 4 + 0 − 3 = 1. The vectors are perpendicular.
**⚠️ if:** computes it but can't connect it to angle/perpendicularity.
**Exit exercise:** Angle between (1, 0) and (1, 1)? (cos θ = 1/√2, so 45°)
**Scope:** formula, perpendicular test, cos θ link.

### matrix multiplication
*FR: produit matriciel · needs: vector, dot product*
**Probe:** A = [[1, 2], [3, 4]], B = [[0, 1], [1, 0]]. Compute AB. Is AB = BA?
**Expect:** AB = [[2, 1], [4, 3]]. BA = [[3, 4], [1, 2]], so no.
**⚠️ if:** multiplies entry by entry (gets [[0, 2], [3, 0]]).
**Exit exercise:** A is 2×3 and B is 3×4. What is the shape of AB? Can you compute BA? (2×4; no, inner sizes 4 and 2 differ)
**Scope:** row-times-column rule, shapes, non-commutativity.

### eigenvalues
*FR: valeurs propres et vecteurs propres · needs: matrix multiplication*
**Probe:** A = [[2, 0], [0, 3]]. Find its eigenvalues and eigenvectors, and say what "eigenvector" means.
**Expect:** λ = 2 with (1, 0), λ = 3 with (0, 1). Av = λv: the direction doesn't change, it only gets scaled.
**⚠️ if:** finds the numbers but can't state Av = λv.
**Exit exercise:** A = [[2, 1], [1, 2]]. Eigenvalues? (λ² − 4λ + 3 = 0, so 3 with (1, 1) and 1 with (1, −1))
**Scope:** definition + 2×2 by hand.

### probability basics
*FR: probabilités · needs: none*
**Probe:** Two fair dice. P(sum = 7)? P(at least one 6)?
**Expect:** 6/36 = 1/6; 11/36.
**⚠️ if:** second one answered 1/6 + 1/6 = 1/3 (adds overlapping cases).
**Exit exercise:** Draw 2 cards without replacement from 52. P(both aces)? (4/52 · 3/51 = 1/221)
**Scope:** counting outcomes, independence, complement.

### expected value
*FR: espérance · needs: probability basics*
**Probe:** A game pays 10 € with probability 0.2, otherwise 0. Entry costs 3 €. Expected profit? Should you play many times?
**Expect:** 2 − 3 = −1 € per play. No: on average you lose 1 € each time.
**⚠️ if:** forgets to subtract the entry, or says "you might win so yes".
**Exit exercise:** Fair die: expected value of the roll? Of the roll squared? (3.5; 91/6 ≈ 15.17)
**Scope:** weighted average, linearity not needed.

### mean and standard deviation
*FR: moyenne et écart-type · needs: none*
**Probe:** Data: 2, 4, 4, 4, 5, 5, 7, 9. Mean? Population standard deviation? What does the standard deviation measure?
**Expect:** 5; 2 (variance 4); typical spread around the mean.
**⚠️ if:** mean is right, standard deviation formula is shaky or the meaning is missing.
**Exit exercise:** Data: 1, 3, 5, 7. Mean and population standard deviation? (4; √5 ≈ 2.24)
**Scope:** population vs sample only if the goal needs it.

---

## Python

### variables and types
*FR: variables et types · needs: none*
**Probe:** In Python, what do `3/2`, `3//2`, `3 % 2` and `'3' + '2'` give?
**Expect:** 1.5 (float); 1; 1; '32' (string concatenation).
**⚠️ if:** gets the numbers but says '3' + '2' is 5.
**Exit exercise:** What do `int('3') + 2` and `'3' * 2` give? (5; '33')
**Scope:** int/float/str, operators, conversion.

### functions and scope
*FR: fonctions et portée · needs: variables and types*
**Probe:**
```python
x = 10
def f(x):
    x = x + 1
    return x
print(f(1), x)
```
**Expect:** `2 10`. The parameter x is local; the outer x is untouched.
**⚠️ if:** answers 11 or "2 11".
**Exit exercise:** What happens here? `def g(): y = 5` then `g()` then `print(y)`. (NameError: y exists only inside g)
**Scope:** parameters, return, local vs global.

### lists and dicts
*FR: listes et dictionnaires · needs: variables and types*
**Probe:** `a = [3, 1, 2]; print(sorted(a), a)` and `d = {'a': 1}; print(d.get('b', 0))`. What prints?
**Expect:** `[1, 2, 3] [3, 1, 2]` (sorted returns a new list); `0`.
**⚠️ if:** thinks sorted changes a, or doesn't know .get with a default.
**Exit exercise:** Build a dict that counts letters in "banana". ({'b': 1, 'a': 3, 'n': 2})
**Scope:** indexing, append, dict lookup/insert/iterate.

### mutability and references
*FR: mutabilité et références · needs: lists and dicts, functions and scope*
**Probe:** `a = [1, 2, 3]; b = a; b.append(4); print(a)`. What prints and why?
**Expect:** `[1, 2, 3, 4]`. a and b are two names for the same list.
**⚠️ if:** answers `[1, 2, 3]`, or gets it right with no explanation.
**Exit exercise:** `def f(x, acc=[]): acc.append(x); return acc`. What do `f(1)` then `f(2)` return, and why? ([1] then [1, 2]: the default list is created once)
**Scope:** same-object vs copy, mutable defaults.

### loops and comprehensions
*FR: boucles et compréhensions · needs: lists and dicts*
**Probe:** What does `[i*i for i in range(5) if i % 2 == 0]` give?
**Expect:** `[0, 4, 16]`.
**⚠️ if:** right answer but can't rewrite it as a normal for-loop.
**Exit exercise:** Write a comprehension for the squares of the odd numbers below 10. ([1, 9, 25, 49, 81])
**Scope:** for, while, range, one-line comprehensions.

### classes and objects
*FR: classes et objets · needs: functions and scope, lists and dicts*
**Probe:** Write a class `Counter` with a method `inc()` that adds 1 to a stored count. If you create two Counters, do they share the count?
**Expect:** `__init__` sets `self.count = 0`; `inc` does `self.count += 1`; no, each instance has its own count.
**⚠️ if:** forgets `self`, or puts the count at class level so both share it.
**Exit exercise:** Add a `__repr__` so `print(c)` shows `Counter(3)`. (`return f"Counter({self.count})"`)
**Scope:** `__init__`, attributes, methods, instances.

### dunder methods
*FR: méthodes spéciales · needs: classes and objects*
**Probe:** A class `V` stores a number `v`. Make `V(2) + V(3)` return a `V` holding 5. Which method does Python call?
**Expect:** `def __add__(self, other): return V(self.v + other.v)`.
**⚠️ if:** writes a normal method `add` instead of the special name.
**Exit exercise:** Make `V(2) * 3` and `3 * V(2)` both work. (`__mul__` and `__rmul__`)
**Scope:** `__add__`, `__mul__`, `__radd__`, `__rmul__`, `__neg__`, `__sub__`, `__pow__`, `__repr__`.

### closures
*FR: fermetures · needs: functions and scope*
**Probe:**
```python
def make():
    n = 0
    def inc():
        nonlocal n
        n += 1
        return n
    return inc
f = make(); f(); print(f())
g = make(); print(g())
```
**Expect:** `2` then `1`. Each call of `make` creates its own `n` that `inc` remembers.
**⚠️ if:** right output but can't explain why g doesn't share f's n.
**Exit exercise:** What breaks if you remove `nonlocal n`, and why? (UnboundLocalError: `n += 1` makes n local to `inc`)
**Scope:** inner functions remembering outer variables, `nonlocal`.

### recursion
*FR: récursivité · needs: functions and scope*
**Probe:** Write `factorial(n)` recursively. Name the base case and the recursive case. What happens with no base case?
**Expect:** `1 if n <= 1 else n * factorial(n - 1)`. Infinite calls end in RecursionError.
**⚠️ if:** writes a loop instead, or forgets the base case.
**Exit exercise:** Write a recursive `sum_list(xs)` so that `sum_list([1, 2, 3])` is 6. (`0 if not xs else xs[0] + sum_list(xs[1:])`)
**Scope:** base case, recursive case, call stack idea.

### reading a traceback
*FR: lire une erreur Python · needs: functions and scope*
**Probe:**
```
Traceback (most recent call last):
  File "a.py", line 7, in <module>
    total = add(1, '2')
  File "a.py", line 3, in add
    return a + b
TypeError: unsupported operand type(s) for +: 'int' and 'str'
```
Which line actually fails, and what is the cause?
**Expect:** Line 3 (inside `add`); an int and a str are added. The bad call is on line 7, passing '2' as a string.
**⚠️ if:** points at line 7 only, or reads the message but can't say which line to fix.
**Exit exercise:** Read the last line first, then the last `File` line above it: what do they tell you? (the error type and message, and where it happened)
**Scope:** bottom-up reading, error type, line.

---

## CS

### graph
*FR: graphe · needs: lists and dicts*
**Probe:** Directed graph with edges A→B, B→C, A→C. Who are A's neighbors? How would you store it in Python?
**Expect:** B and C. Adjacency list: `{'A': ['B', 'C'], 'B': ['C'], 'C': []}`.
**⚠️ if:** understands the picture but can't store it.
**Exit exercise:** How does the adjacency list change if the edge A–B is undirected? (B appears in A's list and A in B's)
**Scope:** nodes, edges, directed vs undirected, adjacency list.

### stack and queue
*FR: pile et file · needs: lists and dicts*
**Probe:** Push 1, 2, 3 on a stack and pop twice. What comes out? Same with a queue (enqueue 1, 2, 3; dequeue twice).
**Expect:** Stack: 3 then 2 (last in, first out). Queue: 1 then 2 (first in, first out).
**⚠️ if:** gets one right and swaps the other.
**Exit exercise:** Which structure does DFS use, and which does BFS? (stack, or recursion; queue)
**Scope:** LIFO vs FIFO only.

### graph traversal
*FR: parcours de graphe (DFS, BFS) · needs: graph, stack and queue, recursion*
**Probe:** Edges A→B, A→C, B→D, C→D, neighbors in the order listed. In what order does DFS from A visit the nodes? And BFS?
**Expect:** DFS: A, B, D, C. BFS: A, B, C, D.
**⚠️ if:** mixes the two orders, or visits D twice.
**Exit exercise:** Why do we keep a visited set? (avoid revisiting nodes and looping forever on cycles)
**Scope:** DFS recursive version; BFS only if the goal needs it.

### dag
*FR: graphe orienté acyclique · needs: graph*
**Probe:** Is A→B, B→C, C→A a DAG? Why or why not?
**Expect:** No: it has a cycle (A→B→C→A). A DAG is directed with no cycles.
**⚠️ if:** says yes because "all edges have a direction".
**Exit exercise:** Draw a DAG with 4 nodes where D depends on B and C, and both depend on A. (A→B, A→C, B→D, C→D)
**Scope:** directed + no cycles, "depends on".

### topological sort
*FR: tri topologique · needs: dag, graph traversal*
**Probe:** Edges A→B, A→C, B→D, C→D. Give one valid topological order. Is D A B C valid?
**Expect:** A B C D or A C B D. D A B C is not valid: D must come after B and C.
**⚠️ if:** gives a valid order but can't say the rule (every edge goes forward).
**Exit exercise:** How can DFS build one? (append a node after visiting all its children; the list is then a valid order, reversed or not depending on the edge direction you want)
**Scope:** definition + the DFS post-order trick.

### big o
*FR: complexité · needs: loops and comprehensions*
**Probe:** A loop inside a loop, both over n items: how does the work grow? And looking up a key in a dict vs scanning a list?
**Expect:** O(n²) (quadruples when n doubles); dict lookup O(1) on average, list scan O(n).
**⚠️ if:** knows "nested loop is slow" without the growth rate.
**Exit exercise:** Binary search on a sorted list of 1,000,000 items: roughly how many steps? (about 20, since log₂(10⁶) ≈ 20)
**Scope:** growth rates only, no formal proofs.

---

## ML

### computational graph
*FR: graphe de calcul · needs: dag, function*
**Probe:** Draw the graph of e = (a + b) * c. Which nodes are leaves, and which node holds the final result?
**Expect:** Leaves a, b, c. Intermediate d = a + b. e = d * c is the output.
**⚠️ if:** lists the operations but can't draw dependencies.
**Exit exercise:** With a = 2, b = 3, c = 4, give the forward value at every node. (d = 5, e = 20)
**Scope:** nodes = values, edges = which inputs produced which output.

### loss function
*FR: fonction de coût · needs: function, mean and standard deviation*
**Probe:** Predictions (2, 4), targets (3, 3). Mean squared error? Why square the errors?
**Expect:** ((−1)² + 1²)/2 = 1. Squaring stops errors cancelling and punishes big misses more.
**⚠️ if:** computes it but can't say why squared.
**Exit exercise:** MSE for predictions (1, 2, 3) vs targets (1, 2, 6)? (9/3 = 3)
**Scope:** one number saying how wrong the model is.

### gradient descent
*FR: descente de gradient · needs: derivative, loss function*
**Probe:** f(w) = (w − 3)². Start at w = 0 with learning rate 0.1. What is w after one step, and why that direction?
**Expect:** f'(0) = −6, so w = 0 − 0.1·(−6) = 0.6. Move against the gradient to reduce f.
**⚠️ if:** right number but moves with the gradient sign wrongly explained.
**Exit exercise:** Same function from w = 0 with learning rate 1.5: what happens? (w goes 0 → 9 → −9 → 27: it overshoots and diverges)
**Scope:** update rule, learning rate effect.

### backpropagation
*FR: rétropropagation · needs: chain rule, computational graph, topological sort*
**Probe:** e = (a + b) * c with a = 2, b = 3, c = 4. Compute de/da, de/db and de/dc by working backward from e.
**Expect:** With d = a + b = 5: de/dc = 5, de/dd = 4, so de/da = de/db = 4.
**⚠️ if:** gets the numbers by expanding the formula instead of tracing backward through the graph.
**Exit exercise:** e = a*b + a with a = 3, b = 2: de/da and de/db? (3 and 3: a is used twice, so its two contributions add)
**Scope:** local derivatives, multiply along paths, add when a node is reused.

### neuron
*FR: neurone · needs: dot product, function*
**Probe:** A neuron computes tanh(w1·x1 + w2·x2 + b). With w = (0.5, −1), x = (2, 1), b = 0.5: what is the output? What does tanh do and why is it there?
**Expect:** Inside = 0.5; tanh(0.5) ≈ 0.46. It squashes to (−1, 1) and adds non-linearity (without it, stacked layers collapse into one linear map).
**⚠️ if:** computes it but can't say why a non-linearity is needed.
**Exit exercise:** d/dx tanh(x) = 1 − tanh²(x). What is the slope at x = 0? (1)
**Scope:** weighted sum + bias + activation.

---

## Physics

### units and dimensional analysis
*FR: analyse dimensionnelle · needs: none*
**Probe:** Using units only, can s = v·t² be a distance? Then convert 72 km/h to m/s.
**Expect:** v·t² has units m·s, not m, so no. 72 km/h = 20 m/s.
**⚠️ if:** converts correctly but doesn't check units to test a formula.
**Exit exercise:** A pendulum's period depends on length L and gravity g. Which has units of time, √(L/g) or √(g/L)? (√(L/g))
**Scope:** unit checks and SI conversions.

### vector components
*FR: composantes d'un vecteur · needs: vector*
**Probe:** A 10 N force acts at 30° above the horizontal. Find its horizontal and vertical components.
**Expect:** Fx = 10 cos 30° ≈ 8.66 N; Fy = 10 sin 30° = 5 N.
**⚠️ if:** swaps sin and cos (check by sketching the triangle).
**Exit exercise:** A 20 N weight on a 30° incline: component along the slope and perpendicular to it? (10 N; ≈ 17.3 N)
**Scope:** resolving along chosen axes.

### free-body diagram
*FR: diagramme des forces · needs: vector components*
**Probe:** A book rests on a table. List the forces on the book. What is the third-law partner of the book's weight?
**Expect:** Weight (down) and normal force (up), net zero. The weight's partner is the book pulling Earth up, not the normal force.
**⚠️ if:** says the normal force is the reaction to the weight.
**Exit exercise:** A block on a frictionless 30° incline: draw the forces and give the acceleration. (weight and normal; a = g sin 30° = 4.9 m/s² down the slope)
**Scope:** draw only forces acting on the object, label each one.

### newtons second law
*FR: deuxième loi de Newton · needs: free-body diagram*
**Probe:** A 2 kg block is pulled right with 10 N while friction pulls left with 4 N. What is its acceleration?
**Expect:** a = (10 − 4)/2 = 3 m/s² to the right.
**⚠️ if:** uses 10/2 and ignores friction, or mixes mass and weight.
**Exit exercise:** Same block, friction now 10 N. What happens and what is the net force? (net 0: constant velocity, or rest if it started at rest)
**Scope:** net force = m·a, one direction at a time.

### conservation of energy
*FR: conservation de l'énergie · needs: newtons second law*
**Probe:** A ball falls 5 m from rest (g = 10 m/s², no air). Speed at the bottom, using energy?
**Expect:** mgh = ½mv², so v = √(2gh) = 10 m/s.
**⚠️ if:** uses kinematics correctly but can't set up the energy balance.
**Exit exercise:** Same ball thrown down at 10 m/s from 5 m. Speed at the bottom? (v² = 100 + 100, so √200 ≈ 14.1 m/s)
**Scope:** kinetic + potential, no friction unless the goal needs it.

### conservation of momentum
*FR: conservation de la quantité de mouvement · needs: newtons second law, vector components*
**Probe:** A 1 kg cart at 4 m/s hits a stationary 3 kg cart and they stick. Speed afterwards?
**Expect:** 1·4 = (1 + 3)·v, so v = 1 m/s.
**⚠️ if:** averages the speeds.
**Exit exercise:** Is kinetic energy conserved in that collision? (before 8 J, after 2 J: 6 J lost, so inelastic)
**Scope:** 1D collisions, elastic vs inelastic.

### coulombs law
*FR: loi de Coulomb · needs: vector components*
**Probe:** Charges of 1 µC and 2 µC are 0.3 m apart (k = 9×10⁹ N·m²/C²). Force magnitude? What happens if the distance doubles?
**Expect:** F = kq₁q₂/r² = 0.2 N. Doubling r divides F by 4.
**⚠️ if:** correct number but says the force halves.
**Exit exercise:** Force on a 3 µC charge placed 0.5 m from a 2 µC charge? (F = 9×10⁹·3×10⁻⁶·2×10⁻⁶/0.25 = 0.216 N)
**Scope:** magnitude, inverse-square, attract/repel.

### electric field
*FR: champ électrique · needs: coulombs law*
**Probe:** Electric field magnitude 0.5 m from a 2 µC point charge? What does E mean?
**Expect:** E = kq/r² = 72,000 N/C. Force per unit charge a test charge would feel.
**⚠️ if:** correct number but treats E as the force itself.
**Exit exercise:** What force does that field exert on a 3 µC charge? (qE = 0.216 N)
**Scope:** point charges, E = F/q, direction rules.

### electric flux
*FR: flux électrique · needs: electric field, dot product*
**Probe:** A uniform field E = 5 N/C is perpendicular to a 2 m² surface. What is the flux? And if the field makes 60° with the surface normal?
**Expect:** 10 N·m²/C; 10·cos 60° = 5 N·m²/C.
**⚠️ if:** uses sin instead of cos (angle is measured from the normal).
**Exit exercise:** What is the flux if the field lies in the plane of the surface? (0)
**Scope:** Φ = E·A·cos θ.

### gauss law
*FR: théorème de Gauss · needs: electric flux, electric field*
**Probe:** State Gauss's law in words, then use it to find E outside a uniformly charged sphere of total charge Q at distance r.
**Expect:** The flux through a closed surface = Q_enclosed/ε₀. By symmetry E·4πr² = Q/ε₀, so E = Q/(4πε₀r²), like a point charge.
**⚠️ if:** quotes the formula but can't use symmetry to pull E out of the integral.
**Exit exercise:** The charge inside a Gaussian sphere doubles and its radius triples. How does the total flux change? (it doubles: only enclosed charge matters)
**Scope:** spherical symmetry first; cylinders/planes only if the goal needs them.

### ohms law and circuits
*FR: loi d'Ohm et circuits · needs: none*
**Probe:** A 12 V source feeds 4 Ω and 2 Ω resistors in series. Current? Voltage across the 4 Ω?
**Expect:** I = 12/6 = 2 A; V = 8 V.
**⚠️ if:** uses 12 V across each resistor.
**Exit exercise:** Same resistors in parallel across 12 V: total current? (12/4 + 12/2 = 9 A)
**Scope:** V = IR, series/parallel, Kirchhoff's two rules if the goal needs them.

---

## Technique

### sliding window
*FR: fenêtre glissante · needs: loops and comprehensions*
**Probe:** You want the maximum sum of any contiguous subarray of size k = 3 in `[2, 1, 5, 1, 3, 2]`. Describe how to compute it in O(N) time without re-summing from scratch at every step.
**Expect:** Compute the sum of the first 3 elements (8). To move the window 1 step right, subtract the element leaving the window and add the new element entering it (8 - 2 + 1 = 7). Track the max.
**⚠️ if:** knows O(N) is possible but recomputes `sum(arr[i:i+k])` at every index, or handles edge indices incorrectly.
**Exit exercise:** In `[1, 3, 2, 6, -1, 4, 1, 8, 2]`, what is the sum of the first window of size 5, and what is the window sum after sliding one position right? (13; 13 - 1 + 4 = 16)
**Scope:** fixed-size windows first; dynamic-size windows (while constraint holds) only if the goal needs it.

### two pointers
*FR: deux pointeurs · needs: lists and dicts, loops and comprehensions*
**Probe:** Given a sorted array `[-4, -1, 0, 3, 10]`, you want to find two numbers that sum to 3. How do two pointers find this in O(N) time?
**Expect:** Place pointer `L` at start (-4) and `R` at end (10). Sum = 6 > 3, so decrement R to decrease sum. If sum < target, increment L. Repeat until sum == 3 or pointers cross.
**⚠️ if:** suggests nested loops (O(N²)), or doesn't know which pointer to move when sum > target.
**Exit exercise:** For sorted `[1, 2, 4, 6, 8, 11]` and target 10, trace the first 2 moves of L and R. (L=1, R=11 -> sum 12 > 10, move R to 8; L=1, R=8 -> sum 9 < 10, move L to 2 -> 2+8=10 found)
**Scope:** opposite-ends convergence on sorted data; fast/slow pointers (cycle detection) only if the goal needs it.

### binary search
*FR: recherche binaire / dichotomie · needs: loops and comprehensions*
**Probe:** On a sorted array of 16 elements, what is the maximum number of comparisons to find a target or prove it's absent? In one sentence, why?
**Expect:** 4 (or 5 depending on boundary definition). Each comparison cuts the search space in half ($2^4 = 16$).
**⚠️ if:** says 8 or 16, or cannot explain why halving yields logarithmic time.
**Exit exercise:** In sorted `[3, 7, 12, 18, 25, 31, 42]`, trace `low`, `high`, and `mid` to search for 18. (low=0, high=6, mid=3: arr[3]=18 found in 1 step; or search for 25: mid=3 (18 < 25), low=4, mid=5 (31 > 25), high=4, mid=4 found)
**Scope:** loop invariant `low <= high`, integer midpoint calculation, handling bounds without off-by-one.

### memoization
*FR: mémoïsation / mise en cache · needs: functions and scope, lists and dicts*
**Probe:** Why is naive recursive `fib(30)` so slow, and what does a cache dictionary change about the call tree?
**Expect:** Naive recursion repeats the exact same sub-calls exponentially ($O(2^N)$); a cache stores the result of `fib(k)` the first time, turning repeated branches into $O(1)$ lookups ($O(N)$ total).
**⚠️ if:** knows it's faster but cannot explain *what* is redundant or how the cache lookup intercepts the call.
**Exit exercise:** In a recursive grid-walk `paths(r, c)` from `(0,0)` to `(2,2)`, what is the cache key, and how many unique states are computed? (key is `(r, c)`; 3x3 = 9 states)
**Scope:** dict or `@lru_cache`, cache key design, space vs. time tradeoff.

### prefix sum
*FR: somme préfixe · needs: lists and dicts, loops and comprehensions*
**Probe:** You need to answer 10,000 range sum queries `sum(arr[L..R])` on an array of 100,000 integers. How does a prefix sum array allow each query to run in O(1) time?
**Expect:** Build `P` where `P[i]` is the sum of elements up to `i`. Then `sum(arr[L..R]) = P[R] - P[L-1]` (with $P[-1] = 0$), so every range sum is a single subtraction.
**⚠️ if:** builds prefix sum but includes an inner loop during queries, or makes off-by-one errors on `L-1`.
**Exit exercise:** Given `arr = [3, 1, 4, 2]`, give the 1-indexed prefix array `P`, and compute `sum(arr[1..2])` (elements 1 and 4) using `P`. (P = [0, 3, 4, 8, 10]; sum = P[3] - P[1] = 8 - 3 = 5)
**Scope:** 1D prefix arrays, 1-indexed vs 0-indexed offset handling.
