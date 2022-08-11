import glob
import time

import tifffile
import numpy as np
import itk

from skimage.transform import rescale, downscale_local_mean
from scipy import ndimage as ndi

def pfunc(**kwargs):
    pass

def align(imagedir, refslice, paramfile, outdir):
    filelist = sorted(glob.glob(f"{imagedir}/*.tif"))

    _fx = tifffile.imread(filelist[83]).astype(np.float32)
    _mx = tifffile.imread(filelist[84]).astype(np.float32)
    print(_fx.shape)
    t1 = time.time()
    _fx = downscale_local_mean(_fx, (6,6)) #, preserve_range=True, order=1)
    _mx = downscale_local_mean(_mx, (6,6)) #, preserve_range=True, order=1)
    print(time.time() - t1)
    fx = itk.GetImageViewFromArray(_fx)
    mx = itk.GetImageViewFromArray(_mx)
    print(fx.dtype, mx.dtype,fx.shape, mx.shape, _fx.max())