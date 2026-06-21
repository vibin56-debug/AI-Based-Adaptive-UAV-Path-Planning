import heapq

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar(grid, start, goal):

    rows = len(grid)
    cols = len(grid[0])

    open_set = []
    heapq.heappush(open_set, (0, start))

    came_from = {}
    g_score = {start: 0}

    while open_set:

        _, current = heapq.heappop(open_set)

        if current == goal:

            path = [current]

            while current in came_from:
                current = came_from[current]
                path.append(current)

            return path[::-1]

        x, y = current

        neighbors = [
            (x+1, y),
            (x-1, y),
            (x, y+1),
            (x, y-1)
        ]

        for nx, ny in neighbors:

            if not (0 <= nx < rows and 0 <= ny < cols):
                continue

            if grid[nx][ny] == 1:
                continue

            tentative = g_score[current] + 1

            if (nx, ny) not in g_score or tentative < g_score[(nx, ny)]:

                came_from[(nx, ny)] = current
                g_score[(nx, ny)] = tentative

                f = tentative + heuristic((nx, ny), goal)

                heapq.heappush(open_set, (f, (nx, ny)))

    return None