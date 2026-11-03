"""Low-panel-count planar Voronoi pavilion. mm. Geometric prototype, not air/structural solver."""
import math,random
DEFAULTS=dict(W=2000.,L=2000.,H=2000.,N=3,Seed=7,Jitter=.06,D=140.,RibD=70.,SA=15.,Canopy=0,StockW=1524.,StockL=2743.2)

def clip(poly,A,B,C):
    out=[]
    for i,p in enumerate(poly):
        q=poly[(i+1)%len(poly)];fp=A*p[0]+B*p[1]-C;fq=A*q[0]+B*q[1]-C
        if fp<=1e-7:out.append(p)
        if (fp<0 and fq>0) or (fp>0 and fq<0):
            t=fp/(fp-fq);out.append((p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])))
    return out

def polygon_area(poly):return abs(sum(p[0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*p[1] for i,p in enumerate(poly)))/2

def tube_mesh(a,b,r,n=32):
    v=[b[i]-a[i] for i in range(3)];ln=math.sqrt(sum(t*t for t in v));z=[t/ln for t in v]
    ref=(0,0,1) if abs(z[2])<.9 else (1,0,0)
    def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
    x=cross(z,ref);d=math.sqrt(sum(t*t for t in x));x=[t/d for t in x];y=cross(z,x)
    vertices=[]
    for c in (a,b):
        for i in range(n):
            t=i*math.pi*2/n;vertices.append([c[j]+r*(x[j]*math.cos(t)+y[j]*math.sin(t)) for j in range(3)])
    vertices.extend([a,b]);faces=[]
    for i in range(n):
        j=(i+1)%n;faces.extend([(i,j,n+j,n+i),(2*n,j,i),(2*n+1,n+i,n+j)])
    return vertices,faces

def circle(r,n=64):return [(r+r*math.cos(i*math.pi*2/n),r+r*math.sin(i*math.pi*2/n)) for i in range(n)]
def rect(w,h,x=0,y=0):return [(x,y),(x+w,y),(x+w,y+h),(x,y+h)]

def build(**kw):
    p=dict(DEFAULTS);p.update(kw)
    for k in p:
        p[k]=float(p[k])
        if math.isnan(p[k]) or math.isinf(p[k]):raise ValueError('Invalid '+k)
    W,L,H,D,rd,sa=p['W'],p['L'],p['H'],p['D'],p['RibD'],p['SA'];n=int(round(p['N']));seed=int(round(p['Seed']));canopy=int(round(p['Canopy']))
    if not (2<=n<=6 and 80<=D<=240 and 30<=rd<=D and min(W,L)>4*D and H>3*D):raise ValueError('N=2..6; D=80..240; RibD=30..D; W/L > 4D; H > 3D')
    if not (5<=sa<=30 and 0<=p['Jitter']<=.15 and canopy in (0,1)):raise ValueError('SA=5..30; Jitter=0..0.15; Canopy=0 or1')
    rng=random.Random(seed);r=D/2;z=H-r;inner=(W-D)*(L-D)
    points=[]
    for i in range(n):
        t=2*math.pi*i/n+math.pi/6;xx=.5+.25*math.cos(t)+(rng.random()-.5)*2*p['Jitter'];yy=.5+.25*math.sin(t)+(rng.random()-.5)*2*p['Jitter']
        points.append((r+(W-D)*xx,r+(L-D)*yy))
    cells=[]
    for i,a in enumerate(points):
        poly=[(r,r),(W-r,r),(W-r,L-r),(r,L-r)]
        for j,b in enumerate(points):
            if i!=j:poly=clip(poly,2*(b[0]-a[0]),2*(b[1]-a[1]),b[0]*b[0]+b[1]*b[1]-a[0]*a[0]-a[1]*a[1])
        if len(poly)<3:raise ValueError('Empty cell; reduce jitter')
        cells.append(poly)
    ribs={}
    for poly in cells:
        for i,a in enumerate(poly):
            b=poly[(i+1)%len(poly)]
            boundary=any(abs(a[axis]-v)<1e-5 and abs(b[axis]-v)<1e-5 for axis,v in [(0,r),(0,W-r),(1,r),(1,L-r)])
            if not boundary:
                key=tuple(sorted((tuple(round(x,5) for x in a),tuple(round(x,5) for x in b))))
                if math.hypot(b[0]-a[0],b[1]-a[1])>1:ribs[key]=(a,b)
    members=[];corners=[(r,r,z),(W-r,r,z),(W-r,L-r,z),(r,L-r,z)]
    for i,c in enumerate(corners):members.append(dict(name='C'+str(i+1),a=(c[0],c[1],0),b=c,d=D,kind='COLUMN'))
    for i,c in enumerate(corners):members.append(dict(name='B'+str(i+1),a=c,b=corners[(i+1)%4],d=D,kind='PERIMETER'))
    for i,(a,b) in enumerate(sorted(ribs.values())):members.append(dict(name='R'+str(i+1),a=(a[0],a[1],z),b=(b[0],b[1],z),d=rd,kind='VORONOI_RIB'))
    pieces=[];meshes=[];labels=[]
    def piece(name,cut,seam):
        w=max(x for x,y in cut)-min(x for x,y in cut);h=max(y for x,y in cut)-min(y for x,y in cut)
        pieces.append(dict(name=name,cut=cut,seam=seam,w=w,h=h))
    for m in members:
        length=math.sqrt(sum((m['b'][j]-m['a'][j])**2 for j in range(3)));m['length']=length
        vs,fs=tube_mesh(m['a'],m['b'],m['d']/2);meshes.append(dict(name=m['name'],kind=m['kind'],v=vs,f=fs));labels.append((m['name'],[(m['a'][j]+m['b'][j])/2 for j in range(3)]))
        w=math.pi*m['d']+2*sa;h=length+2*sa
        piece(m['name']+'_WRAP',rect(w,h),rect(w-2*sa,h-2*sa,sa,sa))
        rr=m['d']/2
        for end in [0,1]:piece(m['name']+'_CAP'+str(end),circle(rr+sa),[(x+sa,y+sa) for x,y in circle(rr)])
    # 16 small reinforcement patches; coupon layup only, not rated connections.
    for i in range(16):piece('PATCH%02d'%(i+1),rect(90,140),rect(90-2*sa,140-2*sa,sa,sa))
    if canopy:
        for i in range(2):piece('ROOF_'+str(i+1),rect(W/2+2*sa,L+2*sa),rect(W/2,L,sa,sa))
    sw,sl=p['StockW'],p['StockL'];gap=8.;sheets=[]
    for pc in sorted(pieces,key=lambda x:(-x['h'],-x['w'])):
        if pc['w']>sw or pc['h']>sl:raise ValueError(pc['name']+' exceeds stock. Increase stock length/width or reduce size.')
        found=False
        for si,rows in enumerate(sheets):
            for row in rows:
                if row['x']+pc['w']<=sw and pc['h']<=row['h']:
                    pc.update(sheet=si,x=row['x'],y=row['y']);row['x']+=pc['w']+gap;found=True;break
            if found:break
            y=sum(a['h']+gap for a in rows)
            if y+pc['h']<=sl:rows.append(dict(x=pc['w']+gap,y=y,h=pc['h']));pc.update(sheet=si,x=0,y=y);found=True;break
        if not found:pc.update(sheet=len(sheets),x=0,y=0);sheets.append([dict(x=pc['w']+gap,y=0,h=pc['h'])])
    area=sum(polygon_area(pc['cut']) for pc in pieces)/1e6
    report=('SIMPLE VORONOI | %.0f x %.0f x %.0f mm\n'
            '%d planar Voronoi cells; %d straight internal ribs; %d tube modules\n'
            'Tube body = ONE wrap + TWO end caps per module (not mesh triangle panels).\n'
            'Canopy %s | %d cloth pieces incl.16 reinforcement patches\n'
            'Nominal cut area %.2f m2 | shelf nesting %d packs (%.0f x %.1f mm each)\n'
            'Seam allowance %.1f mm | primary D%.0f / ribs D%.0f mm\n'
            'No pressure/stability/seam-strength simulation. No blower sizing result.\n'
            'Joints are strap/sleeve concepts; tube intersections in model are schematic.\n'
            'Ports, valves, seam-seal tape, failed coupons and inflation compensation excluded.')%(W,L,H,n,len(ribs),len(members),'ON' if canopy else 'OFF',len(pieces),area,len(sheets),sw,sl,sa,D,rd)
    return dict(p=p,sites=points,cells=cells,members=members,meshes=meshes,labels=labels,pieces=pieces,packs=len(sheets),cut_area_m2=area,report=report)

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

_keys=['W','L','H','N','Seed','Jitter','D','RibD','SA','Canopy','StockW','StockL']
_values=dict((k,float(globals()[k])) for k in _keys if globals().get(k) is not None)
_design=build(**_values)
Frame,Cells,Plan,Cut,Stitch,Stock,IDs,Report=geometry(_design)
