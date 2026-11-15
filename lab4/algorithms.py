
INSIDE = 0
LEFT   = 1
RIGHT  = 2
BOTTOM = 4
TOP    = 8


def get_code(x: float, y: float, xmin: float, ymin: float, xmax: float, ymax: float) -> int:
    code = INSIDE
    if x < xmin:
        code |= LEFT
    elif x > xmax:
        code |= RIGHT
    if y < ymin:
        code |= BOTTOM
    elif y > ymax:
        code |= TOP
    return code


# ЧАСТЬ 1: Алгоритм средней точки (деления отрезка пополам)
def clip_segment_midpoint(p1, p2, clip_rect, eps=1e-3):
    """
    Отсечение отрезка p1-p2 прямоугольным окном алгоритмом средней точки.
    clip_rect = (xmin, ymin, xmax, ymax)
    """
    xmin, ymin, xmax, ymax = clip_rect

    def _subdivide(pa, pb, code_a, code_b):
        if (code_a | code_b) == INSIDE:
            return (pa, pb)

        if (code_a & code_b) != 0:
            return None

        dx = pb[0] - pa[0]
        dy = pb[1] - pa[1]
        if abs(dx) < eps and abs(dy) < eps:
            if code_a == INSIDE:
                return (pa, pa)
            if code_b == INSIDE:
                return (pb, pb)
            return None

        pm = ((pa[0] + pb[0]) / 2.0, (pa[1] + pb[1]) / 2.0)
        code_m = get_code(pm[0], pm[1], xmin, ymin, xmax, ymax)

        left_res = _subdivide(pa, pm, code_a, code_m)
        right_res = _subdivide(pm, pb, code_m, code_b)

        if left_res is not None and right_res is not None:
            return (left_res[0], right_res[1])
        elif left_res is not None:
            return left_res
        elif right_res is not None:
            return right_res
        else:
            return None

    code1 = get_code(p1[0], p1[1], xmin, ymin, xmax, ymax)
    code2 = get_code(p2[0], p2[1], xmin, ymin, xmax, ymax)

    return _subdivide(p1, p2, code1, code2)


# ЧАСТЬ 2: Алгоритм Сазерленда-Ходжмана (отсечение многоугольника)
def clip_polygon_sutherland_hodgman(polygon, clip_rect):
    """
    Отсечение многоугольника прямоугольным окном алгоритмом Сазерленда-Ходжмана.
    polygon = [(x1, y1), (x2, y2), ...]
    """
    if not polygon or len(polygon) < 3:
        return []

    xmin, ymin, xmax, ymax = clip_rect
    output_list = list(polygon)

    edges = [
        ('LEFT',   lambda p: p[0] >= xmin, xmin),
        ('RIGHT',  lambda p: p[0] <= xmax, xmax),
        ('BOTTOM', lambda p: p[1] >= ymin, ymin),
        ('TOP',    lambda p: p[1] <= ymax, ymax)
    ]

    for edge_name, is_inside, edge_val in edges:
        input_list = output_list
        output_list = []
        if not input_list:
            break

        s = input_list[-1]

        for p in input_list:
            p_inside = is_inside(p)
            s_inside = is_inside(s)

            if p_inside:
                if not s_inside:
                    output_list.append(_compute_intersection(s, p, edge_name, edge_val, clip_rect))
                output_list.append(p)
            elif s_inside:
                output_list.append(_compute_intersection(s, p, edge_name, edge_val, clip_rect))

            s = p

    return output_list


def _compute_intersection(p1, p2, edge_name, val, clip_rect):
    """Вычисляет точку пересечения ребра p1-p2 с заданной граничной прямой."""
    xmin, ymin, xmax, ymax = clip_rect
    x1, y1 = p1
    x2, y2 = p2
    dx = x2 - x1
    dy = y2 - y1

    if edge_name in ('LEFT', 'RIGHT'):
        x = val
        t = (val - x1) / dx if dx != 0 else 0.0
        y = y1 + t * dy
    else:
        y = val
        t = (val - y1) / dy if dy != 0 else 0.0
        x = x1 + t * dx

    x = max(xmin, min(xmax, x))
    y = max(ymin, min(ymax, y))

    return (x, y)