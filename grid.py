import geojson
from shapely.geometry import shape
import numpy as np
import json

#membuka file geojson yang bernama 'input.geojson'
with open('input.geojson', 'r') as f:
  input = json.loads(f.read())

#menentukan parameter yaitu panjang x dan panjang y dengan satuan meter
xresm = 1000
yresm = 1000

input = geojson_input['features'][0]['geometry']
box = []
for i in (0,1): #0 adalah longitude berdasarkan urutan dalam tuple, 1 adalah latitude berdasarkan urutan dalam tuple
    #res = sorted(list(geojson.utils.coords(input)), key=lambda x:x[i])
    res = sorted(list(geojson.utils.coords(input)), key=lambda x:x[i])
    #sorting longitude dan latitude dari kecil ke besar
    box.append((res[0][i],res[-1][i])) #diambil nilai terkecil dan terbesar sebagai bounding box
ret = f"({box[0][0]},{box[1][1]},{box[0][1]},{box[1][0]})"

xy = ret[1:-1].split(',')
ulx, uly, lrx, lry = float(box[0][0]),float(box[1][1]),float(box[0][1]),float(box[1][0])

# resolution 1 degree grid
xres = 0.00001*(xresm/1.11)
yres = -0.00001*(yresm/1.11)

# setengan dari resolusi untuk mencari koordinat tengah setiap kotak grid
dx = xres/2
dy = yres/2

# membuat grid dengan numpy meshgrid
xx, yy = np.meshgrid(
    np.arange(ulx+dx, lrx+dx, xres), #dibuat numpy array
    np.arange(uly+dy, lry+dy, yres), #dibuat numpy array
)

grid = {"type":"FeatureCollection", "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" } }, "features":[]}
for x,y in zip(xx.ravel(), yy.ravel()): #loop setiap  x dan y dimasukkan ke dalam format geojson
    feature = {"type":"Feature","properties":{},"geometry":{"type":"MultiPolygon","coordinates":[]}}
    feature["geometry"]["coordinates"]=[[[[x-dx,y-dy],[x+dx,y-dy],[x+dx,y+dy],[x-dx,y+dy],[x-dx,y-dy]]]] #memformat koordinat untuk setiap kotak grid
    feature["properties"]={"name":"grid"}
    grid["features"].append(feature)
grid_json = json.dumps(grid)

s = shape(input)
grid_shape = geojson.loads(grid_json)
grid2 = {"type":"FeatureCollection", "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" } }, "features":[]}
#mengecek satu persatu polygon grid yang intersect dengan polygon input
for row in grid_shape['features']:
    r = shape(row['geometry'])
    if r.intersects(s):
        grid2["features"].append(row)
        
y = json.dumps(grid2) #membuat json dari dictionary
with open('outgrid.geojson', 'w') as f:
    f.write(str(y))
grid_json
