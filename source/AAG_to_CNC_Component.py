"""Exact per-triangle development. mm. No membrane relaxation or compensated patterning."""
import math

def flatten(a,b,c):
    def d(p,q):return math.sqrt(sum((p[i]-q[i])**2 for i in range(3)))
    ab,ac,bc=d(a,b),d(a,c),d(b,c)
    if ab<1e-7:raise ValueError('zero edge')
    x=(ac*ac+ab*ab-bc*bc)/(2*ab); h2=ac*ac-x*x
    if h2<1e-8:raise ValueError('degenerate triangle')
    return [(0.,0.),(ab,0.),(x,math.sqrt(h2))]

def offset(p,d):
    """Round joins: no arbitrarily long acute-corner mitres."""
    result=[]
    for i,b in enumerate(p):
        a=p[(i-1)%len(p)];c=p[(i+1)%len(p)]
        u=(b[0]-a[0],b[1]-a[1]);v=(c[0]-b[0],c[1]-b[1])
        start=math.atan2(-u[0],u[1]);end=math.atan2(-v[0],v[1])
        while end<start:end+=2*math.pi
        n=max(1,int(math.ceil((end-start)/(math.pi/36))))
        for j in range(n+1):
            t=start+(end-start)*j/n;result.append((b[0]+d*math.cos(t),b[1]+d*math.sin(t)))
    return result

def patterns(vertices,faces,sa=15,sheetw=1524,sheetl=2743.2,gap=8):
    if not (0<sa<100 and min(sheetw,sheetl)>100 and gap>=0):raise ValueError('Invalid seam/stock/gap')
    edges={}; pcs=[];counts={}; skipped=0
    for fi,f in enumerate(faces):
        try:st=flatten(*[vertices[i] for i in f])
        except ValueError:skipped+=1;continue
        ids=[]
        for j in range(3):
            key=tuple(sorted((f[j],f[(j+1)%3])));counts[key]=counts.get(key,0)+1
            if key not in edges:edges[key]='E%05d'%(len(edges)+1)
            ids.append(edges[key])
        cut=offset(st,sa);x=min(a[0] for a in cut);y=min(a[1] for a in cut)
        cut=[(a-x,b-y) for a,b in cut]; st=[(a-x,b-y) for a,b in st]
        w=max(a for a,b in cut);h=max(b for a,b in cut)
        if w>sheetw or h>sheetl:raise ValueError('Face %d exceeds stock; change meshing/stock'%fi)
        pcs.append(dict(name='F%05d'%fi,stitch=st,cut=cut,w=w,h=h,edges=ids,face=fi))
    shelves=[]
    for p in sorted(pcs,key=lambda p:(-p['h'],-p['w'])):
        found=False
        for si,rows in enumerate(shelves):
            for row in rows:
                if row['x']+p['w']<=sheetw and p['h']<=row['h']:
                    x,y=row['x'],row['y'];row['x']+=p['w']+gap;found=True;break
            if found:break
            y=sum(r['h']+gap for r in rows)
            if y+p['h']<=sheetl:
                rows.append(dict(x=p['w']+gap,y=y,h=p['h']));x=0;found=True;break
        if not found:
            shelves.append([dict(x=p['w']+gap,y=0,h=p['h'])]);si=len(shelves)-1;x=y=0
        p.update(sheet=si,x=x,y=y)
    return pcs,len(shelves),sum(v==1 for v in counts.values()),sum(v>2 for v in counts.values()),skipped

import Rhino.Geometry as R

def _v(name,default):
    v=globals().get(name)
    return default if v is None else float(v)
Width=_v('Width',2500);SA=_v('SA',15);Gap=_v('Gap',8)
SheetW=_v('SheetW',1524);SheetL=_v('SheetL',2743.2);Edge=_v('Edge',250)
MaxFaces=int(_v('MaxFaces',3000))
if Width<=0 or Edge<=0 or MaxFaces<1:raise ValueError('Positive Width, Edge, MaxFaces required')
_inputs=globals().get('G')
if _inputs is None:raise ValueError('Wire MultiPipe Pipe output to G (list / no type hint)')
if not isinstance(_inputs,(list,tuple)):
    try:_inputs=list(_inputs)
    except TypeError:_inputs=[_inputs]
_geo=[]
for _g in _inputs:
    if hasattr(_g,'ScriptVariable'):_g=_g.ScriptVariable()
    if not isinstance(_g,R.GeometryBase):raise ValueError('Input must be actual Mesh, Brep or SubD; use No Type Hint, not ghdoc GUID')
    _geo.append(_g.Duplicate())
_bb=R.BoundingBox.Unset
for _g in _geo:_bb.Union(_g.GetBoundingBox(True))
_dx=_bb.Max.X-_bb.Min.X;_dy=_bb.Max.Y-_bb.Min.Y
_span=max(_dx,_dy)
if _span<=1e-7:raise ValueError('Empty/zero-sized geometry')
_scale=Width/_span
_transform=R.Transform.Scale(R.Point3d.Origin,_scale)*R.Transform.Translation(-_bb.Min.X,-_bb.Min.Y,-_bb.Min.Z)
_mesh=R.Mesh()
for _g in _geo:
    _g.Transform(_transform)
    if isinstance(_g,R.Mesh):_mesh.Append(_g)
    else:
        if isinstance(_g,R.SubD):_g=_g.ToBrep()
        if not isinstance(_g,R.Brep):raise ValueError('Mesh, Brep or SubD required')
        _mp=R.MeshingParameters();_mp.MaximumEdgeLength=Edge;_mp.MinimumEdgeLength=Edge*.15
        _mp.RefineGrid=True;_mp.JaggedSeams=False
        for _m in R.Mesh.CreateFromBrep(_g,_mp):_mesh.Append(_m)
_mesh.Vertices.CombineIdentical(True,True);_mesh.Faces.ConvertQuadsToTriangles();_mesh.Compact()
if _mesh.Faces.Count>MaxFaces:raise ValueError('Mesh has %d faces > MaxFaces %d. Use coarser Edge / remesh upstream. No automatic detail deletion.'%(_mesh.Faces.Count,MaxFaces))
_vertices=[(v.X,v.Y,v.Z) for v in _mesh.Vertices]
_faces=[(f.A,f.B,f.C) for f in _mesh.Faces]
_pcs,_sheets,_naked,_nonman,_skip=patterns(_vertices,_faces,SA,SheetW,SheetL,Gap)
FlatCut=[];FlatSeam=[];Labels=[];Stock=[];Preview=[_mesh]
def _poly(points):return R.PolylineCurve([R.Point3d(x,y,0) for x,y in points+[points[0]]])
for _pc in _pcs:
    _ox=4000+_pc['sheet']*(SheetW+200)+_pc['x'];_oy=_pc['y']
    _st=[(x+_ox,y+_oy) for x,y in _pc['stitch']]
    FlatSeam.append(_poly(_st));FlatCut.append(_poly([(x+_ox,y+_oy) for x,y in _pc['cut']]))
    _cx=sum(x for x,y in _st)/3;_cy=sum(y for x,y in _st)/3
    Labels.append(R.TextDot(_pc['name'],R.Point3d(_cx,_cy,0)))
    _fc=_mesh.Faces[_pc['face']];_ps=[_vertices[_fc.A],_vertices[_fc.B],_vertices[_fc.C]]
    Labels.append(R.TextDot(_pc['name'],R.Point3d(*[sum(v[i] for v in _ps)/3 for i in range(3)])))
    for _j,_eid in enumerate(_pc['edges']):
        _a,_b=_st[_j],_st[(_j+1)%3]
        # Move label slightly toward centroid, away from cut edge.
        Labels.append(R.TextDot(_eid,R.Point3d(.45*(_a[0]+_b[0])+.1*_cx,.45*(_a[1]+_b[1])+.1*_cy,0)))
for _i in range(_sheets):
    _x=4000+_i*(SheetW+200);Stock.append(_poly([(_x,0),(_x+SheetW,0),(_x+SheetW,SheetL),(_x,SheetL)]))
Report=('AAG source -> triangulated textile patterns (NOT previous rectangular frame)\n'
        'Uniform scale %.6g; footprint %.1f x %.1f mm; %d panels; %d sheets\n'
        'Naked edges %d; non-manifold edges %d; skipped degenerate faces %d\n'
        'CUT=FlatCut; seam reference=FlatSeam; Labels=matching face/edge IDs.\n'
        'Faceted approximation; not smooth-surface unroll or inflation-compensated patterns.\n'
        'No router G-code, actuator pattern, seam-strength proof, or matched rigid joints.')%(_scale,_dx*_scale,_dy*_scale,len(_pcs),_sheets,_naked,_nonman,_skip)
if _nonman:raise ValueError(Report+'\nRepair non-manifold mesh before fabrication.')
