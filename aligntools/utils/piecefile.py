import glob
import os
import json
import sys

def read_config(json_file):
    with open(json_file) as j:
        config = json.load(j)    
        return config

def globfiles(g_path, extension='tif'):
    
    if g_path.endswith('/'):
        g_path = g_path[:-1] 

    pattern = f"{g_path}/t*/*.{extension}" 
    print(g_path, pattern)
    files = sorted(glob.glob(pattern))

    return files

def get_min_max(files, config):
   
    xmin = 88888888
    xmax = 0
    ymin = 88888888
    ymax = 0
    
    tiles = list() 
    grid = list()
    for f in files:
        base = os.path.basename(f)
        s = base.split("_")
        stile = s[-2]
        tile = int(stile[1:])      
        tiles.append(tile)
        px, py = xy_from_tile(tile, config)
        grid.append((px, py))

        if px > xmax:
            xmax = px
        elif px < xmin:
            xmin = px
        else:
            pass
         
        if py > ymax:
            ymax = py
        elif py < ymin:
            ymin = py
        else:
            pass
      
    return {'xmin':xmin, 'xmax':xmax,
            'ymin':ymin, 'ymax':ymax}

def piece(filename):
    base = os.path.basename(filename)
    
    s = base.split("_")
    stile = s[-2]
    sz = s[-1].split('.')[0]
   
    tile = int(stile[1:])
    z = int(sz[1:])
    
    return tile, z 

def xy_from_tile(tile, config):
    gx = (tile - 0) % config['gridx'] #+ 1 # base 0
    gy = (tile - 0)//config['gridx'] #+ 1 # base 0
    gyr = config['gridy'] - gy - 1  # added -1 to account for base 0
    px = (gx - 0)*(config['nx'] - config['offset']) # base zero
    py = (gyr)*(config['ny'] - config['offset'])
    return px, py    
    

def addpieces(files, config_dict, outfile):
    mxdict = get_min_max(files, config_dict) 
    fo = open(outfile, 'w')
    print(mxdict)
    for f in files:
        tile, z = piece(f)
        px, py = xy_from_tile(tile, config_dict)
        px = px - mxdict['xmin']
        py = py - mxdict['ymin']
        out = "{:8d}{:8d}{:8d}\n".format(px, py, z) 
        fo.write(out)
    fo.close()    
'''        
       0    4408       0
012345678901234567890123
'''
def create_piece_file(json_file, g_path, outfile, extension=".tif"):
    config = read_config(json_file)
    files = globfiles(g_path)
    mxdict = get_min_max(files, config) 
    fo = open(outfile, 'w')
    print(mxdict)
    for f in files:
        tile, z = piece(f)
        px, py = xy_from_tile(tile, config)
        px = px - mxdict['xmin']
        py = py - mxdict['ymin']
        out = "{:8d}{:8d}{:8d}\n".format(px, py, z) 
        fo.write(out)
    fo.close()

if __name__ == '__main__':
    json_file = sys.argv[1]
    g_path = sys.argv[2]
    outfile = sys.argv[3]
    #print(json_file, g_path, outfile)
    create_piece_file(json_file, g_path, outfile) 
    