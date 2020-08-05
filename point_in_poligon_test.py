import unittest
from bin_3d import _Point, _is_point_in_polygon


class TestPointInPolygon(unittest.TestCase):
    def test_zero_angle_inside(self):
        polygon = (_Point(1, 1), _Point(1, 5), _Point(5, 5), _Point(5, 1))
        point = _Point(3, 3)
        self.assertTrue(_is_point_in_polygon(polygon, point))

    def test_zero_angle_left(self):
        polygon = (_Point(1, 1), _Point(1, 5), _Point(5, 5), _Point(5, 1))
        point = _Point(0, 3)
        self.assertFalse(_is_point_in_polygon(polygon, point))

    def test_zero_angle_right(self):
        polygon = (_Point(1, 1), _Point(1, 5), _Point(5, 5), _Point(5, 1))
        point = _Point(6, 3)
        self.assertFalse(_is_point_in_polygon(polygon, point))

    def test_zero_angle_below(self):
        polygon = (_Point(1, 1), _Point(1, 5), _Point(5, 5), _Point(5, 1))
        point = _Point(3, 0)
        self.assertFalse(_is_point_in_polygon(polygon, point))

    def test_zero_angle_above(self):
        polygon = (_Point(1, 1), _Point(1, 5), _Point(5, 5), _Point(5, 1))
        point = _Point(3, 6)
        self.assertFalse(_is_point_in_polygon(polygon, point))

    def test_zero_angle_corner1(self):
        polygon = (_Point(1, 1), _Point(1, 5), _Point(5, 5), _Point(5, 1))
        point = _Point(1, 1)
        self.assertTrue(_is_point_in_polygon(polygon, point))

    def test_zero_angle_corner2(self):
        polygon = (_Point(1, 1), _Point(1, 5), _Point(5, 5), _Point(5, 1))
        point = _Point(1, 5)
        self.assertTrue(_is_point_in_polygon(polygon, point))

    def test_zero_angle_corner3(self):
        polygon = (_Point(1, 1), _Point(1, 5), _Point(5, 5), _Point(5, 1))
        point = _Point(5, 5)
        self.assertTrue(_is_point_in_polygon(polygon, point))

    def test_zero_angle_corner4(self):
        polygon = (_Point(1, 1), _Point(1, 5), _Point(5, 5), _Point(5, 1))
        point = _Point(5, 1)
        self.assertTrue(_is_point_in_polygon(polygon, point))

    def test_45_angle_inside(self):
        polygon = (_Point(1, 3), _Point(3, 5), _Point(5, 3), _Point(3, 1))
        point = _Point(3, 3)
        self.assertTrue(_is_point_in_polygon(polygon, point))

    def test_45_angle_left(self):
        polygon = (_Point(1, 3), _Point(3, 5), _Point(5, 3), _Point(3, 1))
        point = _Point(0, 3)
        self.assertFalse(_is_point_in_polygon(polygon, point))

    def test_45_angle_right(self):
        polygon = (_Point(1, 3), _Point(3, 5), _Point(5, 3), _Point(3, 1))
        point = _Point(6, 3)
        self.assertFalse(_is_point_in_polygon(polygon, point))

    def test_45_angle_above(self):
        polygon = (_Point(1, 3), _Point(3, 5), _Point(5, 3), _Point(3, 1))
        point = _Point(3, 6)
        self.assertFalse(_is_point_in_polygon(polygon, point))

    def test_45_angle_below(self):
        polygon = (_Point(1, 3), _Point(3, 5), _Point(5, 3), _Point(3, 1))
        point = _Point(3, 0)
        self.assertFalse(_is_point_in_polygon(polygon, point))

    def test_45_angle_corner1(self):
        polygon = (_Point(1, 3), _Point(3, 5), _Point(5, 3), _Point(3, 1))
        point = _Point(1, 3)
        self.assertTrue(_is_point_in_polygon(polygon, point))

    def test_45_angle_corner2(self):
        polygon = (_Point(1, 3), _Point(3, 5), _Point(5, 3), _Point(3, 1))
        point = _Point(3, 5)
        self.assertTrue(_is_point_in_polygon(polygon, point))

    def test_45_angle_corner3(self):
        polygon = (_Point(1, 3), _Point(3, 5), _Point(5, 3), _Point(3, 1))
        point = _Point(5, 3)
        self.assertTrue(_is_point_in_polygon(polygon, point))

    def test_45_angle_corner4(self):
        polygon = (_Point(1, 3), _Point(3, 5), _Point(5, 3), _Point(3, 1))
        point = _Point(3, 1)
        self.assertTrue(_is_point_in_polygon(polygon, point))


if __name__ == '__main__':
    unittest.main()
