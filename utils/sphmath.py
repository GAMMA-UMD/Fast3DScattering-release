import numpy as np
import pyshtools

def cart2sph(x, y, z):
    hxy = np.hypot(x, y)
    r = np.hypot(hxy, z)
    el = np.arctan2(z, hxy)
    az = np.arctan2(y, x)
    return az, el, r

def sph2cart(az, el, r):
    rcos_theta = r * np.cos(el)
    x = rcos_theta * np.cos(az)
    y = rcos_theta * np.sin(az)
    z = r * np.sin(el)
    return x, y, z

def convertSH(shvec, mode=1):
    """
    Convert spherical harmonics coefficients vector between pyshtools and GSound/Om conventions
    """
    N = len(shvec)
    lmax = int(round(np.sqrt(N)))
    assert lmax * lmax == N
    converted = []
    if mode==1:
        for l in range(lmax):
            for m in range(-l, l+1):
                sign = 2 if m < 0 else 1
                converted.append(shvec[pyshtools.shio.YilmIndexVector(sign, l, abs(m))])
        converted = np.array(converted)
    else:
        converted = np.zeros_like(shvec)
        ind = 0
        for l in range(lmax):
            for m in range(-l, l+1):
                sign = 2 if m < 0 else 1
                converted[pyshtools.shio.YilmIndexVector(sign, l, abs(m))] = shvec[ind]
                ind += 1
    return converted