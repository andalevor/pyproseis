import sqlite3


def initialize_db_from_SPS(db_name, Rsps_name, Ssps_name, Xsps_name, rev):
    Rsps = _parse_rs_sps(Rsps_name, rev, 'R')
    Ssps = _parse_rs_sps(Ssps_name, rev, 'S')
    Xsps = _parse_x_sps(Xsps_name, rev)
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE traces
    (trace_id INTEGER PRIMARY KEY, src_line_num INTEGER,
    src_point_num INTEGER, src_point_idx INTEGER, src_point_code TEXT,
    src_stat_corr INTEGER, depth REAL, src_seis_datum INTEGER,
    uphole INTEGER, src_water_depth REAL, src_easting REAL,
    src_northing REAL, src_elev REAL, day INTEGER, time INTEGER,
    rec_line_num INTEGER, rec_point_num INTEGER, rec_point_idx INTEGER,
    rec_point_code TEXT, rec_stat_corr INTEGER, rec_point_depth REAL,
    rec_seis_datum INTEGER, rec_water_depth REAL, rec_easting REAL,
    rec_northing REAL, rec_elev REAL, tape_num TEXT, record_num INTEGER,
    record_inc INTEGER, instrument_code INTEGER, chan INTEGER,
    mid_easting REAL, mid_northing REAL, bin_number INTEGER DEFAULT NULL,
    inline INTEGER DEFAULT NULL, xline INTEGER DEFAULT NULL,
    bin_easting REAL DEFAULT NULL, bin_northing REAL DEFAULT NULL, bin_fold INTEGER DEFAULT NULL)''')
    for record in Xsps:
        src = Ssps[(record.src_line_num, record.src_point_num)]
        curr_rec = record.rec_point_num_from
        curr_chan = record.from_chan
        while curr_rec <= record.rec_point_num_to:
            rec = Rsps[(record.rec_line_num, curr_rec)]
            mid_x = (src.easting + rec.easting) / 2
            mid_y = (src.northing + rec.northing) / 2
            cursor.execute('''INSERT INTO traces VALUES(NULL,?,?,?,?,?,?,?,?,?,?,
            ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,NULL,NULL,NULL,NULL,NULL,NULL)''',
                           (record.src_line_num, record.src_point_num,
                            record.point_idx, src.point_code, src.stat_corr,
                            src.point_depth, src.seis_datum, src.uphole_time,
                            src.water_depth, src.easting, src.northing,
                            src.elev, src.day, src.time, rec.line_num,
                            rec.point_num, rec.point_idx, rec.point_code,
                            rec.stat_corr, rec.point_depth, rec.seis_datum,
                            rec.water_depth, rec.easting, rec.northing,
                            rec.elev, record.tape_num, record.record_num,
                            record.record_inc, record.instrument_code,
                            curr_chan, mid_x, mid_y))
            curr_rec = curr_rec + record.rec_idx
            curr_chan = curr_chan + record.chan_inc
    conn.commit()
    conn.close()


class Error(Exception):
    def __init__(self, arg):
        self.args = arg


class _RSsps:
    def __init__(self, line_num, point_num, point_idx, point_code, stat_corr,
                 point_depth, seis_datum, uphole_time, water_depth, easting,
                 northing, elev, day, time):
        self.line_num = line_num
        self.point_num = point_num
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
    def __init__(self, tape_num, record_num, record_inc, instrument_code,
                 src_line_num, src_point_num, point_idx, from_chan, to_chan,
                 chan_inc, rec_line_num, rec_point_num_from, rec_point_num_to,
                 rec_idx):
        self.tape_num = tape_num
        self.record_num = record_num
        self.record_inc = record_inc
        self.instrument_code = instrument_code
        self.src_line_num = src_line_num
        self.src_point_num = src_point_num
        self.point_idx = point_idx
        self.from_chan = from_chan
        self.to_chan = to_chan
        self.chan_inc = chan_inc
        self.rec_line_num = rec_line_num
        self.rec_point_num_from = rec_point_num_from
        self.rec_point_num_to = rec_point_num_to
        self.rec_idx = rec_idx


def _parse_rs_sps(file_name, rev, sps_type):
    with open(file_name) as sps:
        result = {}
        counter = 1
        for line in sps:
            # 80 characters + \n
            if len(line) != 81:
                raise Exception(
                    'Length of line(' + str(1) + ') in ' + sps_type + 'SPS file should be 80 characters')
            if not line.startswith(sps_type):
                continue
            if rev < 2:
                line_num = int(float(line[1:17]))
                point_num = int(line[17:25])
                point_idx = int(line[25:26])
                point_code = line[26:28]
                stat_corr = int(line[28:32])
                point_depth = float(line[32:36])
                seis_datum = int(line[36:40])
                uphole_time = int(line[40:42])
                water_depth = float(line[42:46])
            else:
                line_num = int(float(line[1:11]))
                point_num = int(float(line[11:21]))
                point_idx = int(line[23:24])
                point_code = line[24:26]
                stat_corr = int(line[26:30])
                point_depth = float(line[30:34])
                seis_datum = int(line[34:38])
                uphole_time = int(line[38:40])
                water_depth = float(line[40:46])
            easting = float(line[46:55])
            northing = float(line[55:65])
            elev = float(line[65:71])
            day = int(line[71:74])
            time = int(line[74:81])
            counter = counter + 1
            result[(line_num, point_num)] = \
                _RSsps(line_num=line_num, point_num=point_num,
                       point_idx=point_idx, point_code=point_code,
                       stat_corr=stat_corr, point_depth=point_depth,
                       seis_datum=seis_datum, uphole_time=uphole_time,
                       water_depth=water_depth, easting=easting,
                       northing=northing, elev=elev, day=day, time=time)
    return result


def _parse_x_sps(file_name, rev):
    with open(file_name) as sps:
        result = []
        counter = 1
        for line in sps:
            if len(line) != 81:
                # 80 characters + \n
                raise Exception(
                    'Length of line(' + str(1) + ') in ' + 'SPS file should be 80 characters')
            if not line.startswith('X'):
                continue
            if rev < 2:
                tape_num = line[1:7]
                record_num = int(line[7:11])
                record_inc = int(line[11:12])
                instrument_code = line[12:13]
                src_line_num = int(float(line[13:29]))
                src_point_num = int(float(line[29:37]))
                point_idx = int(line[37:38])
                from_chan = int(line[38:42])
                to_chan = int(line[42:46])
                chan_inc = int(line[46:47])
                rec_line_num = int(float(line[47:63]))
                rec_point_num_from = int(float(line[63:71]))
                rec_point_num_to = int(float(line[71:79]))
                rec_idx = int(line[79:80])
            else:
                tape_num = line[1:7]
                record_num = int(line[7:15])
                record_inc = int(line[15:16])
                instrument_code = line[16:17]
                src_line_num = int(float(line[17:27]))
                src_point_num = int(float(line[27:37]))
                point_idx = int(line[37:38])
                from_chan = int(line[38:43])
                to_chan = int(line[43:48])
                chan_inc = int(line[48:49])
                rec_line_num = int(float(line[49:59]))
                rec_point_num_from = int(float(line[59:69]))
                rec_point_num_to = int(float(line[69:79]))
                rec_idx = int(line[79:80])
            counter = counter + 1
            result.append(
                _Xsps(tape_num=tape_num, record_num=record_num,
                      record_inc=record_inc, instrument_code=instrument_code,
                      src_line_num=src_line_num, src_point_num=src_point_num,
                      point_idx=point_idx, from_chan=from_chan, to_chan=to_chan,
                      chan_inc=chan_inc, rec_line_num=rec_line_num,
                      rec_point_num_from=rec_point_num_from,
                      rec_point_num_to=rec_point_num_to, rec_idx=rec_idx))
    return result
