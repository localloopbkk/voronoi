import Rhino.Geometry as R

def geometry(b):
    Frame=[];Cells=[];Plan=[];Cut=[];Stitch=[];Stock=[];IDs=[];Report=b['report']
    def poly(pts):return R.PolylineCurve([R.Point3d(*p) for p in list(pts)+[pts[0]]])
    for m in b['meshes']:
        g=R.Mesh()
        for v in m['v']:g.Vertices.Add(*v)
        for f in m['f']:g.Faces.AddFace(*f)
        g.Normals.ComputeNormals();g.Compact();g.SetUserString('Part',m['name']);Frame.append(g)
    z=b['p']['H']-b['p']['D']/2
    for i,c in enumerate(b['cells']):
        Plan.append(poly([(x,y,z) for x,y in c]))
        if int(round(b['p']['Canopy'])):
            m=R.Mesh()
            for x,y in c:m.Vertices.Add(x,y,b['p']['H'])
            for j in range(1,len(c)-1):m.Faces.AddFace(0,j,j+1)
            m.Normals.ComputeNormals();Cells.append(m)
    for name,pt in b['labels']:IDs.append(R.TextDot(name,R.Point3d(*pt)))
    for pc in b['pieces']:
        ox=3500+pc['sheet']*(b['p']['StockW']+150)+pc['x'];oy=pc['y']
        Cut.append(poly([(x+ox,y+oy,0) for x,y in pc['cut']]))
        Stitch.append(poly([(x+ox,y+oy,0) for x,y in pc['seam']]))
        IDs.append(R.TextDot(pc['name'],R.Point3d(ox+pc['w']/2,oy+pc['h']/2,0)))
    for si in range(b['packs']):
        x=3500+si*(b['p']['StockW']+150);w=b['p']['StockW'];h=b['p']['StockL']
        Stock.append(poly([(x,0,0),(x+w,0,0),(x+w,h,0),(x,h,0)]))
    return Frame,Cells,Plan,Cut,Stitch,Stock,IDs,Report
