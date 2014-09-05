from __future__ import division
from copy import deepcopy
import numpy as np

from mbuild.coordinate_transform import equivalence_transform

def apply_mask(host, guest, mask, guest_port_name="port"):
    """ """
    box = host.boundingbox(excludeG=False)

    mask = mask * box.lengths + box.mins

    n_ports = len(host.referenced_ports())
    assert(n_ports >= mask.shape[0])

    port_pos = np.empty((n_ports,3))
    port_list = []
    for pidx, port in enumerate(host.referenced_ports()):
        port_pos[pidx, :] = port.middle.pos
        port_list.append(port)

    for mp in mask:
        closest_point_idx = np.argmin(host.min_periodic_distance(mp, port_pos))
        closest_port = port_list[closest_point_idx]
        brush = deepcopy(guest)
        equivalence_transform(brush, brush.labels[guest_port_name], closest_port)
        host.add(brush)
        port_pos[closest_point_idx,:] = np.array([np.inf, np.inf, np.inf])


def random_mask_3d(num_sites):
    """ """
    mask = np.random.random((num_sites, 3))
    return mask


def random_mask_2d(num_sites):
    """ """
    mask = random_mask_3d(num_sites)
    mask[:, 2] = 0
    return mask


def grid_mask_2d(n, m):
    """ """
    mask = np.zeros(shape=(n*m, 3), dtype=float)
    for i in range(n):
        for j in range(m):
            mask[i*m + j, 0] = i / n
            mask[i*m + j, 1] = j / m
    return mask


def grid_mask_3d(n, m, l):
    """ """
    mask = np.zeros(shape=(n*m*l, 3), dtype=float)
    for i in range(n):
        for j in range(m):
            for k in range(l):
                mask[i*m*l + j*l + k, 0] = i / n
                mask[i*m*l + j*l + k, 1] = j / m
                mask[i*m*l + j*l + k, 2] = k / l
    return mask


def sphere_mask(N):
    """Generate N evenly distributed points on the unit sphere.

    Sphere is centered at the origin. Alrgorithm based on the 'Golden Spiral'.

    Code by Chris Colbert from the numpy-discussion list:
    http://mail.scipy.org/pipermail/numpy-discussion/2009-July/043811.html

    """
    phi = (1 + np.sqrt(5)) / 2  # the golden ratio
    long_incr = 2*np.pi / phi   # how much to increment the longitude

    dz = 2.0 / float(N)         # a unit sphere has diameter 2
    bands = np.arange(N)        # each band will have one point placed on it
    z = bands * dz - 1 + (dz/2) # the height z of each band/point
    r = np.sqrt(1 - z*z)        # project onto xy-plane
    az = bands * long_incr      # azimuthal angle of point modulo 2 pi
    x = r * np.cos(az)
    y = r * np.sin(az)
    return np.column_stack((x, y, z))


def disk_mask(n):
    """ """
    radius = np.sqrt(np.arange(n) / float(n))

    golden_angle = np.pi * (3 - np.sqrt(5))
    theta = golden_angle * np.arange(n)

    points = np.zeros((n, 2))
    points[:,0] = np.cos(theta)
    points[:,1] = np.sin(theta)
    points *= radius.reshape((n, 1))

    return points