import glob
import os

import tifffile
import itk
import numpy as np

from joblib import Parallel, delayed


def pfunc(z, **kwargs):

    configfile = kwargs['configfile']
    prefix = kwargs['prefix'] 
    pretif = kwargs['pretif']
    res = kwargs['res']
    origin_ = kwargs['origin']
    tile_shape = kwargs['tile_shape']
    
    tileconfig = itk.TileConfiguration[2]()
    tileconfig.Parse(configfile)
    zstr = f'{z:04d}'
    images = list()
    for t in range(tileconfig.LinearSize()):
        origin = tileconfig.GetTile(t).GetPosition()
        filename = f'{prefix}/{tileconfig.GetTile(t).GetFileName()}'
        
        filename = filename.replace('xxxx', zstr)
        filename = filename.replace('aa', pretif)
        
        if os.path.exists(filename):
            _xarray = tifffile.imread(filename).astype(np.float64)  #float32
        else:
            _xarray = np.zeros(tile_shape, dtype=np.float64) + 125   #float32
        
        _xnp = itk.GetImageViewFromArray(_xarray)
        
        _x = _xnp
        
        _x.SetOrigin(origin)
        origin_[(z, t)] = origin
        images.append(_x)
        shape = _xnp.shape
    
    montage = itk.TileMontage[type(images[0]), itk.F].New()  ### F to US
    montage.SetMontageSize(tileconfig.GetAxisSizes())
    for t in range(tileconfig.LinearSize()):
        montage.SetInputTile(t, images[t])

    montage.Update()
     
    ctiles = tileconfig ## i don't think this is needed
    for t in range(tileconfig.LinearSize()):
        index = tileconfig.LinearIndexToNDIndex(t)
        reg_tr = montage.GetOutputTransform(index)
        tile = tileconfig.GetTile(t)
        pos = tile.GetPosition()
        for d in range(2):
            pos[d] -= reg_tr.GetOffset()[d]
        res[(z, t)] = reg_tr
        origin_[('r', z, t)] = tile.GetPosition()
        tile.SetPosition(pos)
        ctiles.SetTile(t, tile)

    rf = itk.TileMergeImageFilter[type(images[0])].New()
    rf.SetMontageSize(tileconfig.GetAxisSizes())
    for t in range(tileconfig.LinearSize()):
        rf.SetInputTile(t, images[t])
        index = tileconfig.LinearIndexToNDIndex(t)
        rf.SetTileTransform(index, montage.GetOutputTransform(index))

    rf.Update()
    
    _x = rf.GetOutput()
    sizes = tileconfig.GetAxisSizes()
    print(sizes)    
    px = (sizes[0]*shape[1] + 100 - _x.shape[-1])
    py = (sizes[1]*shape[0] + 100 - _x.shape[-2])
    #print(px, py)
    _x = np.pad(_x, ((0, py), (0, px)))
    _x = 255*(_x - _x.min())/(_x.max() - _x.min())
    _x = _x.astype(np.uint8)
    tifffile.imwrite(f'{kwargs["outpath"]}/montage_{zstr}.tif', _x, imagej=True)
    print(res)
    return res
    
def stitch(zlist, configfile, prefix, pretif, outpath, tile_shape=(4608, 6144), njobs=4):
    res = {}
    origin = {}
    kwargs = {'configfile':configfile,
              'prefix':prefix,
              'pretif':pretif,
              'outpath':outpath,
              'origin':origin,
              'tile_shape':tile_shape,
              'res':res}

    res2 = [pfunc(z, **kwargs) for z in zlist]
    # res2 = Parallel(n_jobs=njobs)\
    #        (delayed(pfunc)(z, **kwargs) for z in zlist)
    return res, origin 
    
    