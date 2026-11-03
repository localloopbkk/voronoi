# Air / Script — Voronoi Studio

Static HTML project for a simple inflatable pavilion, native Grasshopper slider editing, cloth layout and DXF export. No build step, backend, API key or npm installation is required. All calculations and file imports stay in the browser.

## เริ่มใช้งาน

1. แตก ZIP แล้วเปิด `index.html` ใน Chrome, Edge หรือ Firefox รุ่นใหม่
2. แท็บ **Design & fabric** ปรับขนาด X/Y/Z, จำนวน Voronoi cells, seed, ความไม่สม่ำเสมอ, เส้นผ่านศูนย์กลางท่อ, เผื่อตะเข็บ, หลังคา และขนาดผ้า
3. คลิกท่อในโมเดล หรือเลือกชื่อชิ้นผ้า เพื่อจับคู่ตำแหน่งกับแพตเทิร์น ชิ้น PATCH เป็นชิ้นเสริมทดลอง ยังไม่ได้กำหนดจุดติดตั้งจริง
4. ดาวน์โหลด **current .gh**, **DXF**, **CSV** หรือ **OBJ** ตามค่าปัจจุบันได้
5. **Save JSON / Load JSON** ใช้เก็บและเรียกค่าพารามิเตอร์กลับมา

ถ้าเครื่องจำกัดการเปิดไฟล์โดยตรง ให้รัน `python3 -m http.server 8000` ในโฟลเดอร์ แล้วเปิด `http://localhost:8000` ใช้ HTTPS บน GitHub Pages ได้โดยไม่ต้องติดตั้ง Python

## GitHub Pages

1. สร้าง repository บน GitHub
2. อัปโหลด **ไฟล์และโฟลเดอร์ข้างในแพ็กเกจ** โดยให้ `index.html` อยู่ที่ root ของ repository ไม่ใช่อัปโหลดเฉพาะ ZIP
3. เก็บ `assets`, `grasshopper`, `models`, `cad`, `source` และ `mesh-studio.html` ไว้ครบ ใช้ relative paths จึงรองรับ URL ที่มีชื่อ repository ต่อท้าย
4. ไปที่ **Settings → Pages → Deploy from a branch → main → /(root) → Save**
5. เปิด URL ที่ GitHub แสดงหลัง publish สำเร็จ

แพ็กเกจนี้ยังไม่ได้สร้าง repository หรือเผยแพร่ไฟล์ขึ้น GitHub ให้

## Grasshopper: สิ่งที่รันได้ในเว็บ

**Simple Voronoi:** เว็บใช้สูตรเดียวกับ `grasshopper/simple_core.py` และลำดับ random เดียวกับ Python สำหรับ seed 1–100 จึงปรับรูปทรงและแพตเทิร์นได้ทันที ปุ่ม **Download current .gh** เขียนค่า sliders ทั้ง 12 ตัวลงใน native Grasshopper archive จาก template ที่แนบมา เปิดใน Rhino แล้ว recompute เพื่อได้ geometry ใน Rhino

**ไฟล์ .gh อื่น:** แท็บ **Grasshopper file** อ่านโครงสร้าง archive แสดงรายการ components และแก้ native Number Sliders ได้ รวมไฟล์ `AAG_Prapawit_CNC_Source.gh` ของผู้ใช้ไว้แล้ว เมื่อดาวน์โหลดไฟล์แก้ไขต้องเปิดและ recompute ใน Rhino เว็บไม่ได้รัน components หรือ plugins ของ Grasshopper ทุกชนิด การแก้ AAG ไม่ได้เปลี่ยนภาพ Simple Voronoi ในแท็บแรก

รองรับ binary `.gh` ที่มีชนิดข้อมูลที่ parser รู้จัก ไม่ใช่ `.ghx` หรือ arbitrary component inputs; มีข้อความแจ้งเมื่อ import ไม่รองรับ ไฟล์ไม่ถูกส่งไป server

Template ใช้ GhPython และ RhinoCommon โปรดอ่าน `grasshopper/START_HERE_TH.txt` สำหรับ inputs/outputs และการใช้งานตาม Rhino ที่ติดตั้ง เครื่องนี้ตรวจ archive และสูตรคำนวณได้ แต่ไม่ได้เปิด Rhino desktop เพื่อทดสอบหน้าจอ Grasshopper จริง

## ค่าเริ่มต้นและขนาดผ้า

| รายการ | ค่าเริ่มต้น |
|---|---:|
| ขอบเขตรูปทรง | 2000 × 2000 × 2000 mm |
| จำนวน planar Voronoi cells | 3 |
| ท่อหลัก / ซี่หลังคา | Ø140 / Ø70 mm |
| เผื่อตะเข็บ | 15 mm |
| ผ้าแต่ละผืน | 1524 × 2743.2 mm (60 × 108 inch) |
| ท่อแยกโมดูล | 11 |
| ชิ้นตัดรวม patches, ไม่มีหลังคา | 49 |
| พื้นที่ตัด / จำนวนผืน | ประมาณ 8.65 m² / 4 ผืน |
| เปิดหลังคา 2 แผง | 51 ชิ้น / ประมาณ 12.84 m² / 5 ผืน |

ตัวเลขจำนวนผืนมาจาก shelf packing แบบไม่หมุนแนวเส้นใย เว้นชิ้น 8 mm ไม่ใช่ optimal nesting จำนวนอาจเปลี่ยนเมื่อปรับพารามิเตอร์ พื้นที่ตัดไม่เท่าพื้นที่ซื้อทั้งผืน

## การตัดและประกอบ

- ท่อแต่ละโมดูลใช้ผ้าพันทรงกระบอก **1 แผง + ฝาวงกลม 2 ชิ้น** ไม่ใช่ตัดทุกสามเหลี่ยมบน mesh
- ชื่อ `C1`–`C4` คือเสา, `B1`–`B4` คือคานรอบ, `R1` เป็นต้นไปคือซี่ Voronoi; suffix `WRAP`, `CAP0`, `CAP1` บอกชิ้นผ้าของโมดูลเดียวกัน
- DXF ใช้ **mm** มี layer `FABRIC_CUT`, `SEAM_REFERENCE`, `PART_IDS`, `STOCK_DO_NOT_CUT` ส่งเครื่องตัดเฉพาะ layer ที่ตั้งใจตัด เส้นตะเข็บและกรอบผ้าเป็นเส้นอ้างอิง
- DXF เป็นเส้นตัด ไม่ใช่ G-code ไม่มี toolpath, kerf compensation หรือค่ามีด ตั้งค่าใน CAM ของเครื่องก่อนใช้งาน
- รูปทรงจุดตัดท่อเป็นแนวคิดการต่อด้วยสายรัดหรือปลอกถอดประกอบ ยังไม่ได้ออกแบบ joint รับแรง; patches 16 ชิ้นเป็น allowance สำหรับ mock-up
- ไม่รวมช่องลม วาล์ว เทปซีล ความสูญเสียจากทดลองตะเข็บ และการชดเชยรูปทรงเมื่อพอง ทำชิ้นทดสอบก่อนตัดทั้งชุด
- ไม่มีการจำลองแรงดัน เสถียรภาพ หรืออัตรารั่ว จึงใช้ผลนี้ยืนยันว่า blower เพียงพอไม่ได้ ไม่มีระบบ text-to-angle หรือควบคุมลมจริงในแพ็กเกจนี้

## โฟลเดอร์

- `index.html`, `assets/`: ตัวปรับ Simple Voronoi และตัวอ่าน/แก้ GH sliders
- `grasshopper/`: native `.gh` ทั้งสองชุด และ source Python
- `models/`: OBJ และ Rhino 3DM ต้นฉบับของผู้ใช้
- `cad/`: โมเดล 3DM, DXF, CSV และรายงาน **snapshot ของค่าเริ่มต้น**; ปรับค่าแล้วให้ใช้ปุ่ม export บนเว็บ
- `source/`: Python component สำหรับ AAG/CNC workflow เดิม
- `mesh-studio.html`: viewer แยกที่ใช้ assets ที่แนบมาสำหรับ OBJ/STL/3DM และ workflow แผง mesh เดิม; 3DM ต้องมี saved render meshes ที่ decoder รองรับ ไม่ใช่ Rhino surface solver

## Dependencies และสิทธิ์

ใช้ fflate สำหรับ raw-DEFLATE ของ GH archives และ rhino3dm ใน mesh studio ตัว decoder ถูกแนบมาภายใน จึงไม่ต้องโหลดจาก CDN ดูใบอนุญาตใน `assets/vendor/` ส่วนไฟล์โมเดลและ AAG เป็นไฟล์ที่ผู้ใช้ให้มา โปรดตรวจสิทธิ์ก่อนเผยแพร่ repository สาธารณะ ไม่มีการให้สิทธิ์เพิ่มเติมแก่ไฟล์ต้นฉบับเหล่านั้น

ดู `VALIDATION_WEB.txt` สำหรับการตรวจสอบแพ็กเกจนี้ และ `grasshopper/VALIDATION.txt` สำหรับการตรวจ template เดิม
