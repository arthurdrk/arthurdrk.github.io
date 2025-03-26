import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from color_grid_game import *

class SPUtils:
    """
    Utility class for solving optimization problems using the Hungarian algorithm and maximum weight matching.
    """

    @staticmethod
    def hungarian_algorithm(cost_matrix):
        """
        Solve the assignment problem using the Hungarian algorithm.

        Parameters
        ----------
        cost_matrix : array-like
            A 2D array representing the cost matrix.

        Returns
        -------
        tuple
            A tuple of arrays representing the row and column indices of the optimal assignment.

        Raises
        ------
        ValueError
            If the input is not a 2D array.
        """
        cost_matrix = np.asarray(cost_matrix)
        if len(cost_matrix.shape) != 2:
            raise ValueError("expected a matrix (2-d array), got a %r array"
                             % (cost_matrix.shape,))

        # The algorithm expects more columns than rows in the cost matrix.
        if cost_matrix.shape[1] < cost_matrix.shape[0]:
            cost_matrix = cost_matrix.T
            transposed = True
        else:
            transposed = False

        state = SPUtils._Hungary(cost_matrix)

        # No need to bother with assignments if one of the dimensions
        # of the cost matrix is zero-length.
        step = None if 0 in cost_matrix.shape else SPUtils._step1

        while step is not None:
            step = step(state)

        if transposed:
            marked = state.marked.T
        else:
            marked = state.marked
        return np.where(marked == 1)

    class _Hungary(object):
        """
        Internal class to manage the state of the Hungarian algorithm.
        """

        def __init__(self, cost_matrix):
            self.C = cost_matrix.copy()

            n, m = self.C.shape
            self.row_uncovered = np.ones(n, dtype=bool)
            self.col_uncovered = np.ones(m, dtype=bool)
            self.Z0_r = 0
            self.Z0_c = 0
            self.path = np.zeros((n + m, 2), dtype=int)
            self.marked = np.zeros((n, m), dtype=int)

        def _clear_covers(self):
            """Clear all covered matrix cells"""
            self.row_uncovered[:] = True
            self.col_uncovered[:] = True

    @staticmethod
    def _step1(state):
        """
        Step 1 of the Hungarian algorithm.
        """
        state.C -= state.C.min(axis=1)[:, np.newaxis]
        for i, j in zip(*np.where(state.C == 0)):
            if state.col_uncovered[j] and state.row_uncovered[i]:
                state.marked[i, j] = 1
                state.col_uncovered[j] = False
                state.row_uncovered[i] = False

        state._clear_covers()
        return SPUtils._step3

    @staticmethod
    def _step3(state):
        """
        Step 3 of the Hungarian algorithm.
        """
        marked = (state.marked == 1)
        state.col_uncovered[np.any(marked, axis=0)] = False

        if marked.sum() < state.C.shape[0]:
            return SPUtils._step4

    @staticmethod
    def _step4(state):
        """
        Step 4 of the Hungarian algorithm.
        """
        C = (state.C == 0).astype(int)
        covered_C = C * state.row_uncovered[:, np.newaxis]
        covered_C *= np.asarray(state.col_uncovered, dtype=int)
        n = state.C.shape[0]
        m = state.C.shape[1]

        while True:
            row, col = np.unravel_index(np.argmax(covered_C), (n, m))
            if covered_C[row, col] == 0:
                return SPUtils._step6
            else:
                state.marked[row, col] = 2
                star_col = np.argmax(state.marked[row] == 1)
                if state.marked[row, star_col] != 1:
                    state.Z0_r = row
                    state.Z0_c = col
                    return SPUtils._step5
                else:
                    col = star_col
                    state.row_uncovered[row] = False
                    state.col_uncovered[col] = True
                    covered_C[:, col] = C[:, col] * (
                        np.asarray(state.row_uncovered, dtype=int))
                    covered_C[row] = 0

    @staticmethod
    def _step5(state):
        """
        Step 5 of the Hungarian algorithm.
        """
        count = 0
        path = state.path
        path[count, 0] = state.Z0_r
        path[count, 1] = state.Z0_c

        while True:
            row = np.argmax(state.marked[:, path[count, 1]] == 1)
            if state.marked[row, path[count, 1]] != 1:
                break
            else:
                count += 1
                path[count, 0] = row
                path[count, 1] = path[count - 1, 1]

            col = np.argmax(state.marked[path[count, 0]] == 2)
            if state.marked[row, col] != 2:
                col = -1
            count += 1
            path[count, 0] = path[count - 1, 0]
            path[count, 1] = col

        for i in range(count + 1):
            if state.marked[path[i, 0], path[i, 1]] == 1:
                state.marked[path[i, 0], path[i, 1]] = 0
            else:
                state.marked[path[i, 0], path[i, 1]] = 1

        state._clear_covers()
        state.marked[state.marked == 2] = 0
        return SPUtils._step3

    @staticmethod
    def _step6(state):
        """
        Step 6 of the Hungarian algorithm.
        """
        if np.any(state.row_uncovered) and np.any(state.col_uncovered):
            minval = np.min(state.C[state.row_uncovered], axis=0)
            minval = np.min(minval[state.col_uncovered])
            state.C[~state.row_uncovered] += minval
            state.C[:, state.col_uncovered] -= minval
        return SPUtils._step4

    @staticmethod
    def matching_dict_to_set(matching):
        """
        Converts matching dictionary format to matching set format.

        Parameters
        ----------
        matching : dict
            A dictionary representing the matching where keys are nodes and values are their matched pairs.

        Returns
        -------
        set
            A set of edges representing the matching.

        Raises
        ------
        ValueError
            If a self-loop is detected in the matching.
        """
        edges = set()
        for edge in matching.items():
            u, v = edge
            if (v, u) in edges or edge in edges:
                continue
            if u == v:
                raise ValueError(f"Self-loops cannot appear in matchings {edge}")
            edges.add(edge)
        return edges

    @staticmethod
    def max_weight_matching(G, maxcardinality=False, weight="weight"):
        """
        Compute a maximum-weighted matching of the graph G.

        Parameters
        ----------
        G : networkx.Graph
            The input graph with edge weights.
        maxcardinality : bool, optional
            Whether to compute a maximum cardinality matching.
        weight : str, optional
            The attribute key for edge weights.

        Returns
        -------
        set
            A set of edges representing the maximum-weighted matching.

        Raises
        ------
        ValueError
            If the input graph is not valid or if an error occurs during computation.
        """

        class NoNode:
            pass

        class Blossom:
            """
            Internal class to represent a blossom in the matching algorithm.
            """

            __slots__ = ["childs", "edges", "mybestedges"]

            def __init__(self):
                self.childs = []
                self.edges = []
                self.mybestedges = None

            def leaves(self):
                """
                Yield all leaf nodes in the blossom.

                Yields
                ------
                node
                    The next leaf node in the blossom.
                """
                stack = [*self.childs]
                while stack:
                    t = stack.pop()
                    if isinstance(t, Blossom):
                        stack.extend(t.childs)
                    else:
                        yield t

        gnodes = list(G)
        if not gnodes:
            return set()

        maxweight = 0
        allinteger = True
        for i, j, d in G.edges(data=True):
            wt = d.get(weight, 1)
            if i != j and wt > maxweight:
                maxweight = wt
            allinteger = allinteger and (str(type(wt)).split("'")[1] in ("int", "long"))

        mate = {}
        label = {}
        labeledge = {}
        inblossom = dict(zip(gnodes, gnodes))
        blossomparent = dict(zip(gnodes, repeat(None)))
        blossombase = dict(zip(gnodes, gnodes))
        bestedge = {}
        dualvar = dict(zip(gnodes, repeat(maxweight)))
        blossomdual = {}
        allowedge = {}
        queue = []

        def slack(v, w):
            """
            Calculate the slack for the edge (v, w).

            Parameters
            ----------
            v : node
                The first node.
            w : node
                The second node.

            Returns
            -------
            float
                The slack value for the edge (v, w).
            """
            return dualvar[v] + dualvar[w] - 2 * G[v][w].get(weight, 1)

        def assignLabel(w, t, v):
            """
            Assign a label to a node or blossom.

            Parameters
            ----------
            w : node
                The node to label.
            t : int
                The label type (1 or 2).
            v : node
                The node connected to w, or None.
            """
            b = inblossom[w]
            assert label.get(w) is None and label.get(b) is None
            label[w] = label[b] = t
            if v is not None:
                labeledge[w] = labeledge[b] = (v, w)
            else:
                labeledge[w] = labeledge[b] = None
            bestedge[w] = bestedge[b] = None
            if t == 1:
                if isinstance(b, Blossom):
                    queue.extend(b.leaves())
                else:
                    queue.append(b)
            elif t == 2:
                base = blossombase[b]
                assignLabel(mate[base], 1, base)

        def scanBlossom(v, w):
            """
            Scan the blossom to find the base node.

            Parameters
            ----------
            v : node
                The first node.
            w : node
                The second node.

            Returns
            -------
            node
                The base node of the blossom.
            """
            path = []
            base = NoNode
            while v is not NoNode:
                b = inblossom[v]
                if label[b] & 4:
                    base = blossombase[b]
                    break
                assert label[b] == 1
                path.append(b)
                label[b] = 5
                if labeledge[b] is None:
                    v = NoNode
                else:
                    v = labeledge[b][0]
                    b = inblossom[v]
                    assert label[b] == 2
                    v = labeledge[b][0]
                if w is not NoNode:
                    v, w = w, v
            for b in path:
                label[b] = 1
            return base

        def addBlossom(base, v, w):
            """
            Add a new blossom to the structure.

            Parameters
            ----------
            base : node
                The base node of the blossom.
            v : node
                The first node in the blossom.
            w : node
                The second node in the blossom.
            """
            bb = inblossom[base]
            bv = inblossom[v]
            bw = inblossom[w]
            b = Blossom()
            blossombase[b] = base
            blossomparent[b] = None
            blossomparent[bb] = b
            b.childs = path = []
            b.edges = edgs = [(v, w)]
            while bv != bb:
                blossomparent[bv] = b
                path.append(bv)
                edgs.append(labeledge[bv])
                v = labeledge[bv][0]
                bv = inblossom[v]
            path.append(bb)
            path.reverse()
            edgs.reverse()
            while bw != bb:
                blossomparent[bw] = b
                path.append(bw)
                edgs.append((labeledge[bw][1], labeledge[bw][0]))
                w = labeledge[bw][0]
                bw = inblossom[w]
            label[b] = 1
            labeledge[b] = labeledge[bb]
            blossomdual[b] = 0
            for v in b.leaves():
                if label[inblossom[v]] == 2:
                    queue.append(v)
                inblossom[v] = b
            bestedgeto = {}
            for bv in path:
                if isinstance(bv, Blossom):
                    if bv.mybestedges is not None:
                        nblist = bv.mybestedges
                        bv.mybestedges = None
                    else:
                        nblist = [
                            (v, w) for v in bv.leaves() for w in G.neighbors(v) if v != w
                        ]
                else:
                    nblist = [(bv, w) for w in G.neighbors(bv) if bv != w]
                for k in nblist:
                    (i, j) = k
                    if inblossom[j] == b:
                        i, j = j, i
                    bj = inblossom[j]
                    if (
                        bj != b
                        and label.get(bj) == 1
                        and ((bj not in bestedgeto) or slack(i, j) < slack(*bestedgeto[bj]))
                    ):
                        bestedgeto[bj] = k
                bestedge[bv] = None
            b.mybestedges = list(bestedgeto.values())
            mybestedge = None
            bestedge[b] = None
            for k in b.mybestedges:
                kslack = slack(*k)
                if mybestedge is None or kslack < mybestslack:
                    mybestedge = k
                    mybestslack = kslack
            bestedge[b] = mybestedge

        def expandBlossom(b, endstage):
            """
            Expand a blossom and update the structure.

            Parameters
            ----------
            b : Blossom
                The blossom to expand.
            endstage : bool
                Whether it is the end stage of the algorithm.
            """
            def _recurse(b, endstage):
                for s in b.childs:
                    blossomparent[s] = None
                    if isinstance(s, Blossom):
                        if endstage and blossomdual[s] == 0:
                            yield s
                        else:
                            for v in s.leaves():
                                inblossom[v] = s
                    else:
                        inblossom[s] = s
                if (not endstage) and label.get(b) == 2:
                    entrychild = inblossom[labeledge[b][1]]
                    j = b.childs.index(entrychild)
                    if j & 1:
                        j -= len(b.childs)
                        jstep = 1
                    else:
                        jstep = -1
                    v, w = labeledge[b]
                    while j != 0:
                        if jstep == 1:
                            p, q = b.edges[j]
                        else:
                            q, p = b.edges[j - 1]
                        label[w] = None
                        label[q] = None
                        assignLabel(w, 2, v)
                        allowedge[(p, q)] = allowedge[(q, p)] = True
                        j += jstep
                        if jstep == 1:
                            v, w = b.edges[j]
                        else:
                            w, v = b.edges[j - 1]
                        allowedge[(v, w)] = allowedge[(w, v)] = True
                        j += jstep
                    bw = b.childs[j]
                    label[w] = label[bw] = 2
                    labeledge[w] = labeledge[bw] = (v, w)
                    bestedge[bw] = None
                    j += jstep
                    while b.childs[j] != entrychild:
                        bv = b.childs[j]
                        if label.get(bv) == 1:
                            j += jstep
                            continue
                        if isinstance(bv, Blossom):
                            for v in bv.leaves():
                                if label.get(v):
                                    break
                        else:
                            v = bv
                        if label.get(v):
                            assert label[v] == 2
                            assert inblossom[v] == bv
                            label[v] = None
                            label[mate[blossombase[bv]]] = None
                            assignLabel(v, 2, labeledge[v][0])
                        j += jstep
                label.pop(b, None)
                labeledge.pop(b, None)
                bestedge.pop(b, None)
                del blossomparent[b]
                del blossombase[b]
                del blossomdual[b]

            stack = [_recurse(b, endstage)]
            while stack:
                top = stack[-1]
                for s in top:
                    stack.append(_recurse(s, endstage))
                    break
                else:
                    stack.pop()

        def augmentBlossom(b, v):
            """
            Augment the matching within a blossom.

            Parameters
            ----------
            b : Blossom
                The blossom to augment.
            v : node
                The node to start augmentation from.
            """
            def _recurse(b, v):
                t = v
                while blossomparent[t] != b:
                    t = blossomparent[t]
                i = j = b.childs.index(t)
                if i & 1:
                    j -= len(b.childs)
                    jstep = 1
                else:
                    jstep = -1
                while j != 0:
                    j += jstep
                    t = b.childs[j]
                    if jstep == 1:
                        w, x = b.edges[j]
                    else:
                        x, w = b.edges[j - 1]
                    if isinstance(t, Blossom):
                        yield (t, w)
                    j += jstep
                    t = b.childs[j]
                    if isinstance(t, Blossom):
                        yield (t, x)
                    mate[w] = x
                    mate[x] = w
                b.childs = b.childs[i:] + b.childs[:i]
                b.edges = b.edges[i:] + b.edges[:i]
                blossombase[b] = blossombase[b.childs[0]]
                assert blossombase[b] == v

            stack = [_recurse(b, v)]
            while stack:
                top = stack[-1]
                for args in top:
                    stack.append(_recurse(*args))
                    break
                else:
                    stack.pop()

        def augmentMatching(v, w):
            """
            Augment the matching by alternating paths.

            Parameters
            ----------
            v : node
                The first node in the augmenting path.
            w : node
                The second node in the augmenting path.
            """
            for s, j in ((v, w), (w, v)):
                while 1:
                    bs = inblossom[s]
                    assert label[bs] == 1
                    assert (labeledge[bs] is None and blossombase[bs] not in mate) or (
                        labeledge[bs][0] == mate[blossombase[bs]]
                    )
                    if isinstance(bs, Blossom):
                        augmentBlossom(bs, s)
                    mate[s] = j
                    if labeledge[bs] is None:
                        break
                    t = labeledge[bs][0]
                    bt = inblossom[t]
                    assert label[bt] == 2
                    s, j = labeledge[bt]
                    assert blossombase[bt] == t
                    if isinstance(bt, Blossom):
                        augmentBlossom(bt, j)
                    mate[j] = s

        def verifyOptimum():
            """
            Verify that the computed matching is optimal.
            """
            if maxcardinality:
                vdualoffset = max(0, -min(dualvar.values()))
            else:
                vdualoffset = 0
            assert min(dualvar.values()) + vdualoffset >= 0
            assert len(blossomdual) == 0 or min(blossomdual.values()) >= 0
            for i, j, d in G.edges(data=True):
                wt = d.get(weight, 1)
                if i == j:
                    continue
                s = dualvar[i] + dualvar[j] - 2 * wt
                iblossoms = [i]
                jblossoms = [j]
                while blossomparent[iblossoms[-1]] is not None:
                    iblossoms.append(blossomparent[iblossoms[-1]])
                while blossomparent[jblossoms[-1]] is not None:
                    jblossoms.append(blossomparent[jblossoms[-1]])
                iblossoms.reverse()
                jblossoms.reverse()
                for bi, bj in zip(iblossoms, jblossoms):
                    if bi != bj:
                        break
                    s += 2 * blossomdual[bi]
                assert s >= 0
                if mate.get(i) == j or mate.get(j) == i:
                    assert mate[i] == j and mate[j] == i
                    assert s == 0
            for v in gnodes:
                assert (v in mate) or dualvar[v] + vdualoffset == 0
            for b in blossomdual:
                if blossomdual[b] > 0:
                    assert len(b.edges) % 2 == 1
                    for i, j in b.edges[1::2]:
                        assert mate[i] == j and mate[j] == i

        while 1:
            label.clear()
            labeledge.clear()
            bestedge.clear()
            for b in blossomdual:
                b.mybestedges = None
            allowedge.clear()
            queue[:] = []
            for v in gnodes:
                if (v not in mate) and label.get(inblossom[v]) is None:
                    assignLabel(v, 1, None)
            augmented = 0
            while 1:
                while queue and not augmented:
                    v = queue.pop()
                    assert label[inblossom[v]] == 1
                    for w in G.neighbors(v):
                        if w == v:
                            continue
                        bv = inblossom[v]
                        bw = inblossom[w]
                        if bv == bw:
                            continue
                        if (v, w) not in allowedge:
                            kslack = slack(v, w)
                            if kslack <= 0:
                                allowedge[(v, w)] = allowedge[(w, v)] = True
                        if (v, w) in allowedge:
                            if label.get(bw) is None:
                                assignLabel(w, 2, v)
                            elif label.get(bw) == 1:
                                base = scanBlossom(v, w)
                                if base is not NoNode:
                                    addBlossom(base, v, w)
                                else:
                                    augmentMatching(v, w)
                                    augmented = 1
                                    break
                            elif label.get(w) is None:
                                assert label[bw] == 2
                                label[w] = 2
                                labeledge[w] = (v, w)
                        elif label.get(bw) == 1:
                            if bestedge.get(bv) is None or kslack < slack(*bestedge[bv]):
                                bestedge[bv] = (v, w)
                        elif label.get(w) is None:
                            if bestedge.get(w) is None or kslack < slack(*bestedge[w]):
                                bestedge[w] = (v, w)
                if augmented:
                    break
                deltatype = -1
                delta = deltaedge = deltablossom = None
                if not maxcardinality:
                    deltatype = 1
                    delta = min(dualvar.values())
                for v in G.nodes():
                    if label.get(inblossom[v]) is None and bestedge.get(v) is not None:
                        d = slack(*bestedge[v])
                        if deltatype == -1 or d < delta:
                            delta = d
                            deltatype = 2
                            deltaedge = bestedge[v]
                for b in blossomparent:
                    if (
                        blossomparent[b] is None
                        and label.get(b) == 1
                        and bestedge.get(b) is not None
                    ):
                        kslack = slack(*bestedge[b])
                        if allinteger:
                            d = kslack // 2
                        else:
                            d = kslack / 2.0
                        if deltatype == -1 or d < delta:
                            delta = d
                            deltatype = 3
                            deltaedge = bestedge[b]
                for b in blossomdual:
                    if (
                        blossomparent[b] is None
                        and label.get(b) == 2
                        and (deltatype == -1 or blossomdual[b] < delta)
                    ):
                        delta = blossomdual[b]
                        deltatype = 4
                        deltablossom = b
                if deltatype == -1:
                    deltatype = 1
                    delta = max(0, min(dualvar.values()))
                for v in gnodes:
                    if label.get(inblossom[v]) == 1:
                        dualvar[v] -= delta
                    elif label.get(inblossom[v]) == 2:
                        dualvar[v] += delta
                for b in blossomdual:
                    if blossomparent[b] is None:
                        if label.get(b) == 1:
                            blossomdual[b] += delta
                        elif label.get(b) == 2:
                            blossomdual[b] -= delta
                if deltatype == 1:
                    break
                elif deltatype == 2:
                    (v, w) = deltaedge
                    allowedge[(v, w)] = allowedge[(w, v)] = True
                    queue.append(v)
                elif deltatype == 3:
                    (v, w) = deltaedge
                    allowedge[(v, w)] = allowedge[(w, v)] = True
                    queue.append(v)
                elif deltatype == 4:
                    expandBlossom(deltablossom, False)
            for v in mate:
                assert mate[mate[v]] == v
            if not augmented:
                break
            for b in list(blossomdual.keys()):
                if b not in blossomdual:
                    continue
                if blossomparent[b] is None and label.get(b) == 1 and blossomdual[b] == 0:
                    expandBlossom(b, True)
        if allinteger:
            verifyOptimum()
        return SPUtils.matching_dict_to_set(mate)
