import itertools

import gmsh


class Environment:
    def __init__(self, factory, lx, ly, lz, lc, transform_data, inner_surfaces, physical_name=None):
        """
        Environment volume primarily for GEO factory and optionally for OCC (if no boolean operations needed)
        :param str factory: see Primitive
        :param float lx: length X
        :param float ly: length Y
        :param float lz: length Z
        :param float lc: characteristic length
        :param list of float transform_data: see Primitive
        :param list of list of int inner_surfaces: Inner surfaces tags by surfaces groups
        (surface group - surfaces that form a closed volume)
        :param str physical_name: see Primitive
        """
        if factory == 'occ':
            self.factory = gmsh.model.occ
        else:
            self.factory = gmsh.model.geo
        self.lx = lx
        self.ly = ly
        self.lz = lz
        self.lc = lc
        self.transform_data = transform_data
        self.inner_surfaces = inner_surfaces
        if physical_name is None:
            self.physical_name = Environment.__name__
        else:
            self.physical_name = physical_name
        # Points
        self.points = []
        half_lx = lx / 2.0
        half_ly = ly / 2.0
        half_lz = lz / 2.0
        self.points.append(self.factory.addPoint(half_lx, half_ly, -half_lz, lc))
        self.points.append(self.factory.addPoint(-half_lx, half_ly, -half_lz, lc))
        self.points.append(self.factory.addPoint(-half_lx, -half_ly, -half_lz, lc))
        self.points.append(self.factory.addPoint(half_lx, -half_ly, -half_lz, lc))
        self.points.append(self.factory.addPoint(half_lx, half_ly, half_lz, lc))
        self.points.append(self.factory.addPoint(-half_lx, half_ly, half_lz, lc))
        self.points.append(self.factory.addPoint(-half_lx, -half_ly, half_lz, lc))
        self.points.append(self.factory.addPoint(half_lx, -half_ly, half_lz, lc))
        # Transform
        if transform_data is not None:
            dim_tags = map(lambda x: (0, x), self.points)
            self.factory.translate(dim_tags, transform_data[0], transform_data[1], transform_data[2])
            if len(transform_data) == 6:
                self.factory.rotate(dim_tags,
                                    transform_data[0], transform_data[1], transform_data[2],
                                    1, 0, 0, transform_data[3])
                self.factory.rotate(dim_tags,
                                    transform_data[0], transform_data[1], transform_data[2],
                                    0, 1, 0, transform_data[4])
                self.factory.rotate(dim_tags,
                                    transform_data[0], transform_data[1], transform_data[2],
                                    0, 0, 1, transform_data[5])
            elif len(transform_data) == 7:
                self.factory.rotate(dim_tags,
                                    transform_data[0], transform_data[1], transform_data[2],
                                    transform_data[3], transform_data[4], transform_data[5],
                                    transform_data[6])
            elif len(transform_data) == 9:
                self.factory.rotate(dim_tags,
                                    transform_data[3], transform_data[4], transform_data[5],
                                    1, 0, 0, transform_data[6])
                self.factory.rotate(dim_tags,
                                    transform_data[3], transform_data[4], transform_data[5],
                                    0, 1, 0, transform_data[7])
                self.factory.rotate(dim_tags,
                                    transform_data[3], transform_data[4], transform_data[5],
                                    0, 0, 1, transform_data[8])
        # Curves
        self.curves = []
        for i in range(len(self.curves_points)):
            curve_points = [self.points[x] for x in self.curves_points[i]]
            self.curves.append(self.factory.addLine(curve_points[0], curve_points[1]))
        # Surfaces
        self.surfaces = []
        for i in range(len(self.surfaces_curves)):
            if self.factory == gmsh.model.geo:
                cl_tag = self.factory.addCurveLoop(
                    map(lambda x, y: y * self.curves[x], self.surfaces_curves[i], self.surfaces_curves_signs[i]))
                self.surfaces.append(self.factory.addSurfaceFilling([cl_tag]))
            else:
                cl_tag = self.factory.addCurveLoop([self.curves[x] for x in self.surfaces_curves[i]])
                self.surfaces.append(self.factory.addSurfaceFilling(cl_tag))
        # Volumes
        self.volumes = []
        if self.factory == gmsh.model.occ:
            out_sl = self.factory.addSurfaceLoop(self.surfaces, 1)  # FIXME bug always return = -1 by default
            in_sls = []
            for i, sl in enumerate(inner_surfaces):
                in_sls.append(self.factory.addSurfaceLoop(sl, 2 + i))  # FIXME bug always return = -1 by default
        else:
            out_sl = self.factory.addSurfaceLoop(self.surfaces)
            flatten_in_sls = list(itertools.chain.from_iterable(inner_surfaces))  # 2D array to 1D array
            in_sls = [self.factory.addSurfaceLoop(flatten_in_sls)]  # one surface loop
        sls = list()
        sls.append(out_sl)
        sls += in_sls
        self.volumes.append(self.factory.addVolume(sls))

    curves_points = [
        [1, 0], [5, 4], [6, 7], [2, 3],
        [3, 0], [2, 1], [6, 5], [7, 4],
        [0, 4], [1, 5], [2, 6], [3, 7]
    ]

    surfaces_curves = [
        [5, 9, 6, 10],
        [4, 11, 7, 8],
        [3, 10, 2, 11],
        [0, 8, 1, 9],
        [0, 5, 3, 4],
        [1, 7, 2, 6]
    ]

    surfaces_curves_signs = [
        [1, 1, -1, -1],
        [-1, 1, 1, -1],
        [-1, 1, 1, -1],
        [1, 1, -1, -1],
        [-1, -1, 1, 1],
        [1, -1, -1, 1]
    ]

    surfaces_names = {
        0: "NX",
        1: "X",
        2: "NY",
        3: "Y",
        4: "NZ",
        5: "Z"
    }
