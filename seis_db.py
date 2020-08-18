import sqlite3
import math


def initialize_db_from_SPS_and_bin(db_name, Rsps_name, Ssps_name, Xsps_name, rev, grid_name):
    grid = _Grid(grid_name)
    r_sps = _parse_rs_sps(Rsps_name, rev, 'R')
    s_sps = _parse_rs_sps(Ssps_name, rev, 'S')
    x_sps = _parse_x_sps(Xsps_name, rev)
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE traces
        (trace_id INTEGER PRIMARY KEY, rec_id INTEGER,
        src_id INTEGER, record_num INTEGER, chan INTEGER,
        inline INTEGER, xline INTEGER)''')
    fold = {}
    size = len(x_sps)
    counter = 1
    print('Started midpoints calculations\n{:3d}%'.format(
        counter * 100 // size), end='')
    for record in x_sps:
        src = s_sps[(record.src_line_num, record.src_point_num)]
        curr_rec = record.rec_point_num_from
        curr_chan = record.from_chan
        while curr_rec <= record.rec_point_num_to:
            rec = r_sps[(record.rec_line_num, curr_rec)]
            mid_x = (src.easting + rec.easting) / 2
            mid_y = (src.northing + rec.northing) / 2
            x_idx = ((mid_x - grid.x_orig) * math.cos((360 - grid.azimuth) * math.pi / 180) +
                     (mid_y - grid.y_orig) * math.sin((360 - grid.azimuth) * math.pi / 180)) // grid.x_cell_size
            y_idx = (-(mid_x - grid.x_orig) * math.sin((360 - grid.azimuth) * math.pi / 180) +
                     (mid_y - grid.y_orig) * math.cos((360 - grid.azimuth) * math.pi / 180)) // grid.y_cell_size
            if grid.inline_par_x:
                inline_no = y_idx + 1
                xline_no = x_idx + 1
            else:
                inline_no = x_idx + 1
                xline_no = y_idx + 1
            if (inline_no, xline_no) in fold:
                fold[(inline_no, xline_no)] = fold[(inline_no, xline_no)] + 1
            else:
                fold[(inline_no, xline_no)] = 1
            cursor.execute('''INSERT INTO traces VALUES(NULL,?,?,?,?,?,?)''',
                           (rec.point_counter, src.point_counter, record.record_num,
                            curr_chan, inline_no, xline_no))
            curr_rec = curr_rec + 1
            curr_chan = curr_chan + record.chan_inc
        print('\b\b\b\b{:3d}%'.format(counter * 100 // size), end='')
        counter = counter + 1
    print(' Done.')
    size = len(r_sps)
    counter = 1
    print('Started writing receiver table to database\n{:3d}%'.format(
        counter * 100 // size), end='')
    cursor.execute('''CREATE TABLE receivers
        (rec_id INTEGER, line_num INTEGER,
        point_num INTEGER, point_idx INTEGER, point_code TEXT,
        stat_corr INTEGER, point_depth REAL, seis_datum INTEGER,
        water_depth REAL, easting REAL, northing REAL, elev REAL)''')
    for k, v in r_sps.items():
        cursor.execute('''INSERT INTO receivers VALUES(?,?,?,?,?,
                ?,?,?,?,?,?,?)''', (v.point_counter, k[0], k[1],
                                    v.point_idx, v.point_code, v.stat_corr,
                                    v.point_depth, v.seis_datum, v.water_depth,
                                    v.easting, v.northing, v.elev))
        print('\b\b\b\b{:3d}%'.format(counter * 100 // size), end='')
        counter = counter + 1
    print(' Done.')
    size = len(s_sps)
    counter = 1
    print('Started writing source table to database\n{:3d}%'.format(
        counter * 100 // size), end='')
    cursor.execute('''CREATE TABLE sources
        (src_id INTEGER, line_num INTEGER,
        point_num INTEGER, point_idx INTEGER, point_code TEXT,
        stat_corr INTEGER, point_depth REAL, seis_datum INTEGER,
        uphole INTEGER, water_depth REAL, easting REAL,
        northing REAL, elev REAL, day INTEGER, time INTEGER)''')
    for k, v in s_sps.items():
        cursor.execute('''INSERT INTO sources VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                       (v.point_counter, k[0], k[1], v.point_idx, v.point_code,
                        v.stat_corr, v.point_depth, v.seis_datum, v.uphole_time,
                        v.water_depth, v.easting, v.northing, v.elev, v.day, v.time))
        print('\b\b\b\b{:3d}%'.format(counter * 100 // size), end='')
        counter = counter + 1
    print(' Done.')
    size = grid.x_cells_number * grid.y_cells_number
    counter = 1
    print('Started writing cdps table to database\n{:3d}%'.format(
        counter * 100 // size), end='')
    cursor.execute('''CREATE TABLE cdps
        (cdp_id INTEGER PRIMARY KEY, inline INTEGER,
        xline INTEGER, easting REAL, northing REAL, fold INTEGER)''')
    for x_idx in range(grid.x_cells_number):
        for y_idx in range(grid.y_cells_number):
            print('\b\b\b\b{:3d}%'.format(counter * 100 //
                                          (grid.x_cells_number * grid.y_cells_number)), end='')
            counter = counter + 1
            if grid.inline_par_x:
                inline_no = y_idx + 1
                xline_no = x_idx + 1
            else:
                inline_no = x_idx + 1
                xline_no = y_idx + 1
            if (inline_no, xline_no) not in fold:
                continue
            bin_fold = fold[(inline_no, xline_no)]
            bin_x = (grid.x_orig + (x_idx + 0.5) * grid.x_cell_size) *\
                math.cos(grid.azimuth * math.pi / 180) +\
                    (grid.y_orig + (y_idx + 0.5) * grid.y_cell_size) *\
                math.sin((grid.azimuth * math.pi / 180))
            bin_y = -(grid.x_orig + (x_idx + 0.5) * grid.x_cell_size) *\
                math.sin(grid.azimuth * math.pi / 180) +\
                (grid.y_orig + (y_idx + 0.5) * grid.y_cell_size) *\
                math.cos((grid.azimuth * math.pi / 180))
            cursor.execute('''INSERT INTO cdps VALUES(NULL,?,?,?,?,?)''',
                           (inline_no, xline_no, bin_x, bin_y, bin_fold))
    print(' Done.')
    conn.commit()
    conn.close()


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


def _parse_rs_sps(file_name, rev, sps_type):
    result = {}
    with open(file_name) as sps:
        counter = 1
        point_counter = 1
        for line in sps:
            # 80 characters + \n or \n
            # if len(line) != 81 and line != '\n':
            #     raise Exception(
            #         'Length of line(' + str(counter) + ') in ' + sps_type + 'SPS file should be 80 characters')
            if not line.startswith(sps_type):
                counter = counter + 1
                continue
            if rev < 2:
                line_num = int(float(line[1:17]))
                point_num = int(line[17:25])
                try:
                    point_idx = int(line[25:26])
                except:
                    point_idx = 1
                point_code = line[26:28]
                try:
                    stat_corr = int(line[28:32])
                except:
                    stat_corr = 0
                try:
                    point_depth = float(line[32:36])
                except:
                    point_depth = 0
                try:
                    seis_datum = int(line[36:40])
                except:
                    seis_datum = 0
                try:
                    uphole_time = int(line[40:42])
                except:
                    uphole_time = 0
                try:
                    water_depth = float(line[42:46])
                except:
                    water_depth = 0
            else:
                line_num = int(float(line[1:11]))
                point_num = int(float(line[11:21]))
                try:
                    point_idx = int(line[23:24])
                except:
                    point_idx = 1
                point_code = line[24:26]
                try:
                    stat_corr = int(line[26:30])
                except:
                    stat_corr = 0
                try:
                    point_depth = float(line[30:34])
                except:
                    point_depth = 0
                try:
                    seis_datum = int(line[34:38])
                except:
                    seis_datum = 0
                try:
                    uphole_time = int(line[38:40])
                except:
                    uphole_time = 0
                try:
                    water_depth = float(line[40:46])
                except:
                    water_depth = 0

            easting = float(line[46:55])
            northing = float(line[55:65])
            elev = float(line[65:71])
            try:
                day = int(line[71:74])
            except:
                day = 0
            try:
                time = int(line[74:81])
            except:
                time = 0
            result[(line_num, point_num)] = _RSsps(point_counter=point_counter, point_idx=point_idx,
                                                   point_code=point_code, stat_corr=stat_corr,
                                                   point_depth=point_depth, seis_datum=seis_datum,
                                                   uphole_time=uphole_time, water_depth=water_depth,
                                                   easting=easting, northing=northing,
                                                   elev=elev, day=day, time=time)
            counter = counter + 1
            point_counter = point_counter + 1
    return result


def _parse_x_sps(file_name, rev):
    result = []
    with open(file_name) as sps:
        counter = 1
        record_counter = 1
        for line in sps:
            # 80 characters + \n or \n
            # if len(line) != 81 and line != '\n':
            #     raise Exception(
            #         'Length of line(' + str(counter) + ') in ' + 'SPS file should be 80 characters')
            if not line.startswith('X'):
                counter = counter + 1
                continue
            if rev < 2:
                tape_num = line[1:7]
                record_num = int(line[7:11])
                try:
                    record_inc = int(line[11:12])
                except:
                    record_inc = 1
                instrument_code = line[12:13]
                src_line_num = int(float(line[13:29]))
                src_point_num = int(float(line[29:37]))
                try:
                    src_idx = int(line[37:38])
                except:
                    src_idx = 1
                from_chan = int(line[38:42])
                to_chan = int(line[42:46])
                try:
                    chan_inc = int(line[46:47])
                except:
                    chan_inc = 1
                rec_line_num = int(float(line[47:63]))
                rec_point_num_from = int(float(line[63:71]))
                rec_point_num_to = int(float(line[71:79]))
                try:
                    rec_idx = int(line[79:80])
                except:
                    rec_idx = 1
            else:
                tape_num = line[1:7]
                record_num = int(line[7:15])
                try:
                    record_inc = int(line[15:16])
                except:
                    record_inc = 1
                instrument_code = line[16:17]
                src_line_num = int(float(line[17:27]))
                src_point_num = int(float(line[27:37]))
                try:
                    src_idx = int(line[37:38])
                except:
                    src_idx = 1
                from_chan = int(line[38:43])
                to_chan = int(line[43:48])
                try:
                    chan_inc = int(line[48:49])
                except:
                    chan_inc = 1
                rec_line_num = int(float(line[49:59]))
                rec_point_num_from = int(float(line[59:69]))
                rec_point_num_to = int(float(line[69:79]))
                try:
                    rec_idx = int(line[79:80])
                except:
                    rec_idx = 1
            if rec_point_num_to - rec_point_num_from != (to_chan - from_chan) // chan_inc:
                raise Error('''Error in X sps file in line {}. Number of channels not corresponds
             to the number of receivers.'''.format(counter))
            result.append(_Xsps(record_counter=record_counter, tape_num=tape_num, record_num=record_num,
                                record_inc=record_inc, instrument_code=instrument_code,
                                src_line_num=src_line_num, src_point_num=src_point_num, src_idx=src_idx,
                                from_chan=from_chan, to_chan=to_chan, chan_inc=chan_inc,
                                rec_line_num=rec_line_num, rec_point_num_from=rec_point_num_from,
                                rec_point_num_to=rec_point_num_to, rec_idx=rec_idx))
            counter = counter + 1
            record_counter = record_counter + 1
    return result


class _RSsps:
    def __init__(self, point_counter, point_idx, point_code, stat_corr,
                 point_depth, seis_datum, uphole_time,
                 water_depth, easting, northing, elev, day, time):
        self.point_counter = point_counter
        self.point_idx = point_idx
        self.point_code = point_code
        self.stat_corr = stat_corr
        self.point_depth = point_depth
        self.seis_datum = seis_datum
        self.uphole_time = uphole_time
        self.water_depth = water_depth
        self.easting = easting
        self.northing = northing
        self.elev = elev
        self.day = day
        self.time = time


class _Xsps:
    def __init__(self, record_counter, tape_num, record_num, record_inc, instrument_code,
                 src_line_num, src_point_num, src_idx, from_chan, to_chan, chan_inc,
                 rec_line_num, rec_point_num_from, rec_point_num_to, rec_idx):
        self.record_counter = record_counter
        self.tape_num = tape_num
        self.record_num = record_num
        self.record_inc = record_inc
        self.instrument_code = instrument_code
        self.src_line_num = src_line_num
        self.src_point_num = src_point_num
        self.src_idx = src_idx
        self.from_chan = from_chan
        self.to_chan = to_chan
        self.chan_inc = chan_inc
        self.rec_line_num = rec_line_num
        self.rec_point_num_from = rec_point_num_from
        self.rec_point_num_to = rec_point_num_to
        self.rec_idx = rec_idx
