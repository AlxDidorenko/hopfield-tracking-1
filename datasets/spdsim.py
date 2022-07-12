#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import random
import math
import numpy as np
from line_profiler_pycharm import profile

@profile
def ExtrapToR(pt, charge, theta, phi, z0, Rc):
    pi = 3.14156
    deg = 180 / pi
    B = 0.8  # magnetic field [T}

    pz = pt / math.tan(theta) * charge

    phit = phi - pi / 2
    R = pt / 0.29 / B  # mm
    k0 = R / math.tan(theta)
    x0 = R * math.cos(phit)
    y0 = R * math.sin(phit)

    if R < Rc / 2:  # no intersection
        return None

    R = charge * R;  # both polarities
    alpha = 2 * math.asin(Rc / 2 / R)

    if (alpha > pi):
        return None  # algorithm doesn't work for spinning tracks

    extphi = phi - alpha / 2
    if extphi > 2 * pi:
        extphi = extphi - 2 * pi

    if extphi < 0:
        extphi = extphi + 2 * pi

    x = Rc * math.cos(extphi)
    y = Rc * math.sin(extphi)

    rax, ray = x - x0 * charge, y - y0 * charge

    tax, tay = -ray, rax

    tabs = math.sqrt(tax * tax + tay * tay)  # pt
    tax /= tabs
    tay /= tabs
    tax *= -pt * charge
    tay *= -pt * charge
    px, py = tax, tay

    z = z0 + k0 * alpha
    return x, y, z, px, py, pz

@profile
def main():
    nevents = int(sys.argv[1])
    # track_coords_all = []
    eff = 1  # detector efficiency

    radii = np.linspace(270, 850, 35)  # mm

    with open('output.tsv', 'w') as f:
        for evt in range(0, nevents):
            pi = 3.14156

            vtxx = random.gauss(0, 10)
            vtxy = random.gauss(0, 10)
            vtxz = random.uniform(-300, 300)  # mm
            ntrk = int(random.uniform(1, 10))
            for trk in range(0, ntrk):

                pt = random.uniform(100, 1000)  # MeV/c
                phi = random.uniform(0, 2 * pi)
                theta = math.acos(random.uniform(-1, 1))

                charge = 0

                while charge == 0:
                    charge = random.randint(-1, 1)

                station = 1
                for R in radii:

                    result = ExtrapToR(pt, charge, theta, phi, vtxz, R)

                    if result is None:
                        continue
                    x, y, z, px, py, pz = result
                    if z >= 2386 or z <= -2386:
                        continue
                    z = z + random.gauss(0, 0.1)
                    phit = math.atan2(x, y)
                    delta = random.gauss(0, 0.1)
                    x = x + delta * math.sin(phit)
                    y = y - delta * math.cos(phit)

                    if random.uniform(0, 1) > eff:
                        continue

                    f.write("%d\t%f\t%f\t%f\t%d\t%d\t%f\t%f\t%f\t%f\t%f\t%f\n" % (
                    evt, x, y, z, station, trk, px, py, pz, vtxx, vtxy, vtxz))

                    station = station + 1

            # add noise hits
            nhit = int(random.uniform(10, 100))  # up to 100 noise hits
            for ihit in range(0, nhit):
                sta = int(random.uniform(0, 35))
                R = radii[sta]
                phi = random.uniform(0, 2 * pi)
                z = random.uniform(-2386, 2386)
                x = R * math.cos(phi)
                y = R * math.sin(phi)
                f.write("%d\t%f\t%f\t%f\t%d\t%d\t%f\t%f\t%f\t%f\t%f\t%f\n" % (
                evt, x, y, z, sta, -1, 0, 0, 0, 0, 0, 0))

    f.close()

if __name__ == '__main__':
    main()
