import geopandas as gpd
from shapely.geometry import Polygon, Point, LineString, MultiPolygon

rj=gpd.read_file("Dados\\RJ\\33MUE250GC_SIR.shp")
rj.plot(color="white",edgecolor="black",figsize=(15,8))

p1=Polygon([(0,0),(1,0),(1,1),(0,1)])
p2=Polygon([(0,0),(1,0),(1,1),])
p3=Polygon([(2,0),(3,0),(3,1),(2,1)])
p4=LineString([(0,1),(3,0),(1,1)])
p5=Point(0.5,0.5)

p6=Polygon([(1,0),(1.5,0.4),(2,0)])
p7=Polygon([(1,1),(1.5,0.6),(2,1)])

p8=MultiPolygon([p6,p7])

g = gpd.GeoSeries([p1,p2,p3,p4,p5,p8])
g
g.plot(cmap='tab10')