import math

def step_algorithm(x1, y1, x2, y2):
    """Пошаговый алгоритм"""
    pixels = []
    if x1 == x2 and y1 == y2:
        return [(x1, y1)]

    dx = x2 - x1
    dy = y2 - y1

    if abs(dx) >= abs(dy):
        if x1 > x2:
            x1, x2, y1, y2 = x2, x1, y2, y1
        k = dy / dx if dx != 0 else 0
        b = y1 - k * x1
        for x in range(x1, x2 + 1):
            y = round(k * x + b)
            pixels.append((x, y))
    else:
        if y1 > y2:
            x1, x2, y1, y2 = x2, x1, y2, y1
        k = dx / dy if dy != 0 else 0
        b = x1 - k * y1
        for y in range(y1, y2 + 1):
            x = round(k * y + b)
            pixels.append((x, y))
    return pixels

def dda_algorithm(x1, y1, x2, y2):
    """Алгоритм ЦДА (Цифровой дифференциальный анализатор)"""
    pixels = []
    dx = x2 - x1
    dy = y2 - y1
    
    length = max(abs(dx), abs(dy))
    if length == 0:
        return [(x1, y1)]

    dx = dx / length
    dy = dy / length

    x = x1
    y = y1

    for _ in range(length + 1):
        pixels.append((round(x), round(y)))
        x += dx
        y += dy
        
    return pixels

def bresenham_line(x1, y1, x2, y2):
    """Алгоритм Брезенхема для отрезка (только целочисленная арифметика)"""
    pixels = []
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    
    err = dx - dy

    while True:
        pixels.append((x1, y1))
        if x1 == x2 and y1 == y2:
            break
        e2 = err * 2
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy
            
    return pixels

def bresenham_circle(xc, yc, r):
    """Алгоритм Брезенхема для окружности"""
    pixels = set()
    x = 0
    y = r
    d = 3 - 2 * r

    def add_circle_points(xc, yc, x, y):
        pixels.update([
            (xc + x, yc + y), (xc - x, yc + y), (xc + x, yc - y), (xc - x, yc - y),
            (xc + y, yc + x), (xc - y, yc + x), (xc + y, yc - x), (xc - y, yc - x)
        ])

    add_circle_points(xc, yc, x, y)
    while y >= x:
        x += 1
        if d > 0:
            y -= 1
            d = d + 4 * (x - y) + 10
        else:
            d = d + 4 * x + 6
        add_circle_points(xc, yc, x, y)

    return list(pixels)



def wu_line(x1, y1, x2, y2):
    """Алгоритм Ву для сглаживания линий"""
    pixels = []
    
    if x1 == x2 and y1 == y2:
        return [(x1, y1, 1.0)]
        
    def fpart(x):
        return x - math.floor(x)
    def rfpart(x):
        return 1 - fpart(x)

    steep = abs(y2 - y1) > abs(x2 - x1)
    if steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1

    dx = x2 - x1
    dy = y2 - y1
    gradient = dy / dx if dx != 0 else 1

    xend = round(x1)
    yend = y1 + gradient * (xend - x1)
    xgap = rfpart(x1 + 0.5)
    xpxl1 = xend
    ypxl1 = math.floor(yend)

    if steep:
        pixels.append((ypxl1, xpxl1, rfpart(yend) * xgap))
        pixels.append((ypxl1 + 1, xpxl1, fpart(yend) * xgap))
    else:
        pixels.append((xpxl1, ypxl1, rfpart(yend) * xgap))
        pixels.append((xpxl1, ypxl1 + 1, fpart(yend) * xgap))
    intery = yend + gradient

    xend = round(x2)
    yend = y2 + gradient * (xend - x2)
    xgap = fpart(x2 + 0.5)
    xpxl2 = xend
    ypxl2 = math.floor(yend)

    if steep:
        pixels.append((ypxl2, xpxl2, rfpart(yend) * xgap))
        pixels.append((ypxl2 + 1, xpxl2, fpart(yend) * xgap))
    else:
        pixels.append((xpxl2, ypxl2, rfpart(yend) * xgap))
        pixels.append((xpxl2, ypxl2 + 1, fpart(yend) * xgap))

    if steep:
        for x in range(xpxl1 + 1, xpxl2):
            pixels.append((math.floor(intery), x, rfpart(intery)))
            pixels.append((math.floor(intery) + 1, x, fpart(intery)))
            intery += gradient
    else:
        for x in range(xpxl1 + 1, xpxl2):
            pixels.append((x, math.floor(intery), rfpart(intery)))
            pixels.append((x, math.floor(intery) + 1, fpart(intery)))
            intery += gradient

    return pixels

def castle_pitteway(x1, y1, x2, y2):
    """Алгоритм Кастла-Питвея"""
    pixels = []
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x2 >= x1 else -1
    sy = 1 if y2 >= y1 else -1

    if dx == 0 and dy == 0:
        return [(x1, y1)]

    steep = dy > dx
    if steep:
        dx, dy = dy, dx

    if dy == 0:
        x, y = x1, y1
        for _ in range(dx + 1):
            pixels.append((x, y))
            if steep:
                y += sy
            else:
                x += sx
        return pixels

    run_count = dy + 1
    q = (dx + 1) // run_count
    r = (dx + 1) % run_count

    err = run_count // 2
    x, y = x1, y1

    for i in range(run_count):
        err += r
        current_run = q
        if err >= run_count:
            err -= run_count
            current_run += 1

        for _ in range(current_run):
            pixels.append((x, y))
            if steep:
                y += sy
            else:
                x += sx

        if i < run_count - 1:
            if steep:
                x += sx
            else:
                y += sy

    return pixels