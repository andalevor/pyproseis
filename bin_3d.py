import sqlite3
import math


class Error(Exception):
    def __init__(self, arg):
        self.args = arg


class _Grid:
    def __init__(self, file_name):
        self.params = {'x_orig': 0.0, 'y_orig': 0.0, 'azimuth': 0.0,
                       'x_cell_size': 0.0, 'y_cell_size': 0.0,
                       'x_cells_number': 0, 'y_cells_number': 0,
                       'inline_par_x': False}
        flags = dict(zip(self.params.keys(), [0] * len(self.params.keys())))
        grid_found = False
        with open(file_name) as grid_file:
            for line in grid_file:
                if line.startswith('[grid]'):
                    grid_found = True
                if not grid_found:
                    continue
                for k in self.params.keys():
                    if line.startswith(k):
                        self.params[k] = line[len(k) + 1:]
                        flags[k] = 1
                        break
        missed = [k for k, v in flags.items() if v != 1]
        if len(missed) != 0:
            raise Error(missed)
        self.x_orig = float(self.params['x_orig'])
        self.y_orig = float(self.params['y_orig'])
        self.azimuth = float(self.params['azimuth'])
        self.x_cell_size = float(self.params['x_cell_size'])
        self.y_cell_size = float(self.params['y_cell_size'])
        self.x_cells_number = int(self.params['x_cells_number'])
        self.y_cells_number = int(self.params['y_cells_number'])
        self.inline_par_x = self.params['inline_par_x'] == 'True'


class _Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return '({}, {})'.format(self.x, self.y)


def bin_3d(grid_name, db_name):
    grid = _Grid(grid_name)
    bin_counter = 1
    y_no = 0
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    while y_no < grid.y_cells_number:
        x_no = 0
        if grid.inline_par_x:
            inline_no = y_no + 1
        else:
            xline_no = y_no + 1
        while x_no < grid.x_cells_number:
            if grid.inline_par_x:
                xline_no = x_no + 1
            else:
                inline_no = x_no + 1
            p1 = _Point(grid.x_orig + x_no * grid.x_cell_size * math.cos(grid.azimuth * math.pi / 180)
                        + y_no * grid.y_cell_size *
                        math.sin(grid.azimuth * math.pi / 180),
                        grid.y_orig + y_no * grid.y_cell_size *
                        math.cos(grid.azimuth * math.pi / 180)
                        - x_no * grid.x_cell_size * math.sin(grid.azimuth * math.pi / 180))
            p2 = _Point(p1.x + grid.y_cell_size * math.sin(grid.azimuth * math.pi / 180),
                        p1.y + grid.y_cell_size * math.cos(grid.azimuth * math.pi / 180))
            p3 = _Point(p2.x + grid.x_cell_size * math.cos(grid.azimuth * math.pi / 180),
                        p2.y - grid.x_cell_size * math.sin(grid.azimuth * math.pi / 180))
            p4 = _Point(p3.x - grid.y_cell_size * math.sin(grid.azimuth * math.pi / 180),
                        p3.y - grid.y_cell_size * math.cos(grid.azimuth * math.pi / 180))
            (p_min, p_max) = _get_min_max((p1, p2, p3, p4))
            cursor.execute('''SELECT trace_id, mid_easting, mid_northing
            FROM traces WHERE mid_easting > ? AND mid_easting < ? AND
            mid_northing > ? AND mid_northing < ?''',
                           (p_min.x, p_max.x, p_min.y, p_max.y))
            for row in cursor:
                if _is_point_in_polygon((p1, p2, p3, p4), _Point(row[1], row[2])):
                    cursor.execute('''UPDATE traces
                    SET bin_number = ?, inline = ?, xline = ?, bin_easting = ?, bin_northing = ?
                    WHERE trace_id = ?''',
                                   (bin_counter, inline_no, xline_no,
                                    (p1.x + p3.x)/2, (p1.y + p3.y)/2, row[0]))
            bin_counter = bin_counter + 1
            print('(I = {}, X = {}) Done'.format(inline_no, xline_no))
            x_no = x_no + 1
        y_no = y_no + 1
    conn.commit()
    conn.close()


def _get_min_max(vals):
    x_min = vals[0].x
    x_max = vals[0].x
    for v in vals[1:]:
        if v.x < x_min:
            x_min = v.x
        if v.x > x_max:
            x_max = v.x
    y_min = vals[0].y
    y_max = vals[0].y
    for v in vals[1:]:
        if v.y < y_min:
            y_min = v.y
        if v.y > y_max:
            y_max = v.y
    return (_Point(x_min, y_min), _Point(x_max, y_max))


def _is_point_in_polygon(polygon, point):
    odd = False
    i = 0
    j = len(polygon) - 1
    while i < len(polygon):
        if polygon[i].y == point.y and polygon[i].x == point.x:
            return True
        if polygon[j].y == point.y and polygon[j].x == point.x:
            return True
        if (polygon[i].y > point.y) != (polygon[j].y > point.y):
            if point.x == ((polygon[j].x - polygon[i].x) *
                           (point.y - polygon[i].y) / (polygon[j].y - polygon[i].y) + polygon[i].x):
                return True
            if point.x < ((polygon[j].x - polygon[i].x) *
                          (point.y - polygon[i].y) / (polygon[j].y - polygon[i].y) + polygon[i].x):
                odd = not odd
        j = i
        i = i + 1
    return odd
