import enum
from typing import Literal, NamedTuple, TypeAlias

DEBUG = False

class EditType(enum.Enum):
    SUBSTITUTION  = enum.auto() # (index: int, char: str)
    INSERTION     = enum.auto() # (index: int, char: str)
    DELETION      = enum.auto() # (index: int)
    TRANSPOSITION = enum.auto() # (index1: int, index2: int)

Edit: TypeAlias = (
    tuple[Literal[EditType.SUBSTITUTION],  int, str]  |
    tuple[Literal[EditType.INSERTION],     int, str]  |
    tuple[Literal[EditType.DELETION],      int, None] |
    tuple[Literal[EditType.TRANSPOSITION], int, int]
)

class DistTuple(NamedTuple):
    dist: int
    prev: tuple[int, int]
    edits: list[Edit] | None = None

# Damerau-Levenshtein distance, as described by
# https://doi.org/10.1186/s12859-019-2819-0

# Adjustments made to keep track of edit types.

def compute_dist_matrix(origin: str, target: str):
    m = len(origin)
    n = len(target)

    dist_matrix = [[DistTuple(-1, (-1, -1)) for j in range(0, n + 1)] for i in range(0, m + 1)]

    # set H_i,0 = i
    for i in range(1, m + 1):
        dist_matrix[i][0] = DistTuple(i, (i - 1, 0), [(EditType.DELETION, 0, None)])
    # set H_0,j = j
    dist_matrix[0][1:] = [DistTuple(j, (0, j - 1), [(EditType.INSERTION, j - 1, target[j - 1])]) for j in range(1, n + 1)]
    # set H_0,0
    dist_matrix[0][0] = DistTuple(0, (-1, -1))

    # last_i    = the last time character origin[i - 1] occurs in target
    # last_j[c] = the last time character c occurs in origin, 
    #     where c is a character in target

    last_j: dict[str, int] = {}
    for i in range(1, m + 1):
        last_i = None
        for j in range(1, n + 1):
            # Substitution
            if origin[i - 1] != target[j - 1]:
                sub_tup = DistTuple(
                    dist = dist_matrix[i - 1][j - 1].dist + 1, 
                    prev = (i - 1, j - 1),
                    edits = [(EditType.SUBSTITUTION, j - 1, target[j - 1])]
                )
            else:
                sub_tup = DistTuple(dist_matrix[i - 1][j - 1].dist, (i - 1, j - 1))
            
            # Insertion
            ins_tup = DistTuple(
                dist = dist_matrix[i][j - 1].dist + 1,
                prev = (i, j - 1),
                edits = [(EditType.INSERTION, j - 1, target[j - 1])]
            )
            
            # Deletion
            del_tup = DistTuple(
                dist = dist_matrix[i - 1][j].dist + 1,
                prev = (i - 1, j),
                edits = [(EditType.DELETION, j, None)]
            )
            
            # Transposition
            k = last_j.get(target[j - 1], None)
            l = last_i
            if k is not None and l is not None:
                edits: list[Edit] = []
                edits.extend((EditType.DELETION, k, None) for _ in range(k, i - 1))
                edits.append((EditType.TRANSPOSITION, l - 1, l))
                edits.extend((EditType.INSERTION, idx, target[idx]) for idx in range(l, j - 1))
                trans_tup = DistTuple(
                    dist = dist_matrix[k - 1][l - 1].dist + len(edits), 
                    prev = (k - 1, l - 1),
                    edits = edits
                )
            else:
                trans_tup = None
            if origin[i - 1] == target[j - 1]:
                last_i = j

            dist_matrix[i][j] = min(filter(lambda k: k is not None, (sub_tup, ins_tup, del_tup, trans_tup)), key=lambda t: t.dist)
        last_j[origin[i - 1]] = i
    return dist_matrix

def distance(origin: str, target: str):
    m = len(origin)
    n = len(target)

    compute_dist_matrix(origin, target)[m][n].dist

def find_path(origin: str, target: str) -> list[Edit]:
    m = len(origin)
    n = len(target)

    nodes = compute_dist_matrix(origin, target)
    path: list[Edit] = []

    curr = (m, n)
    while curr != (-1, -1):
        i, j = curr
        node = nodes[i][j]
        path.extend(reversed(node.edits or []))
        curr = node.prev
    
    path.reverse()
    return path

def print_path(origin: str, target: str):
    path = find_path(origin, target)
    for n in path:
        match n:
            case (EditType.SUBSTITUTION, i, c):
                print(f"SUBST({i}, {c})")
            case (EditType.INSERTION, i, c):
                print(f"INSERT({i}, {c})")
            case (EditType.DELETION, i, _):
                print(f"DELETE({i})")
            case (EditType.TRANSPOSITION, i, j):
                print(f"TRANSPOSE({i}, {j})")
            case _:
                pass
    
    if DEBUG:
        validate_path(origin, target, path)

def validate_path(origin: str, target: str, path = None):
    if path is None:
        path = find_path(origin, target)

    buf = list(origin)
    for n in path:
        match n:
            case (EditType.SUBSTITUTION, i, c):
                buf[i] = c
            case (EditType.INSERTION, i, c):
                buf.insert(i, c)
            case (EditType.DELETION, i, _):
                buf.pop(i)
            case (EditType.TRANSPOSITION, i, j):
                tmp = buf[i]
                buf[i] = buf[j]
                buf[j] = tmp
            case _:
                pass
    
    assert buf == list(target), "path did not produce the correct operations to get from origin to target"

if DEBUG:
    validate_path("abcde", "")
    validate_path("", "abcde")
    validate_path("hello", "helol")
    validate_path("hello", "hiya")
    validate_path("abcde", "acebd")
    validate_path("abcde", "adbec")
    validate_path("abcccde", "adbec")
    validate_path("abcdefgh", "bcdefhg")