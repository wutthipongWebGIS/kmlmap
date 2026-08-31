import numpy as np
import rasterio
from rasterio.enums import Resampling
import plotly.graph_objects as go

def visualize_dem_interactive(tif_path="dem.tif", max_size=600, output_html="dem_viewer.html"):
    print(f"กำลังโหลดไฟล์: {tif_path} ...")
    
    with rasterio.open(tif_path) as src:
        # 1. ย่อขนาดข้อมูลเพื่อความลื่นไหล
        scale_factor = min(1.0, max_size / max(src.width, src.height))
        new_width = int(src.width * scale_factor)
        new_height = int(src.height * scale_factor)
        
        z_data = src.read(
            1,
            out_shape=(new_height, new_width),
            resampling=Resampling.bilinear
        ).astype(float)
        
        # 2. จัดการ NoData
        if src.nodata is not None:
            z_data[z_data == src.nodata] = np.nan
            
        # 3. ดึงพิกัดจริง
        bounds = src.bounds
        x_coords = np.linspace(bounds.left, bounds.right, new_width)
        y_coords = np.linspace(bounds.bottom, bounds.top, new_height)

    print("กำลังสร้างโมเดล 3D พร้อมระบบปรับขนาดแกน Z ...")

    # 4. สร้าง Surface พร้อมปรับ Colorbar ให้กระทัดรัด
    surface = go.Surface(
        x=x_coords,
        y=y_coords,
        z=z_data,
        colorscale='Earth',
        colorbar=dict(
            title=dict(text='ความสูง (ม.)', side='top'),
            len=0.6,          # ลดความยาวแถบสีเหลือ 60% ของความสูงหน้าจอ
            thickness=15,     # ปรับความหนาให้พอดี ไม่ใหญ่เกินไป
            x=0.92,           # ขยับตำแหน่งให้อยู่ชิดขวาพอดี
            ypad=10
        )
    )

    fig = go.Figure(data=[surface])

    # 5. สร้างปุ่ม/เมนูสำหรับปรับขนาดความสูงแกน Z (Z-Aspect Ratio Slider)
    steps = []
    # สร้างระดับความสูงแกน Z ตั้งแต่ 0.05 (แบน) ถึง 0.5 (สูงชัน)
    z_scales = [0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5] 
    
    for z_scale in z_scales:
        step = dict(
            method="relayout",
            args=[{"scene.aspectratio": {"x": 1, "y": 1, "z": z_scale}}],
            label=f"{z_scale}"
        )
        steps.append(step)

    sliders = [dict(
        active=2, # กำหนดค่าเริ่มต้นไว้ที่ 0.15
        currentvalue={"prefix": "อัตราส่วนความสูงแกน Z (Z-Scale): "},
        pad={"t": 50},
        steps=steps
    )]

    # 6. ตั้งค่า Layout
    fig.update_layout(
        title=f'แสดงผล 3D DEM: {tif_path}',
        autosize=True,
        scene=dict(
            xaxis=dict(title='X (Easting)'),
            yaxis=dict(title='Y (Northing)'),
            zaxis=dict(title='Elevation (m)'),
            aspectratio=dict(x=1, y=1, z=0.15) # ค่าเริ่มต้น
        ),
        sliders=sliders,
        margin=dict(l=10, r=10, b=10, t=50)
    )

    # 7. บันทึกไฟล์ HTML
    fig.write_html(output_html)
    print(f"เสร็จสิ้น! เปิดไฟล์ '{output_html}' บนเว็บเบราว์เซอร์เพื่อทดลองเลื่อนปรับแกน Z ได้เลย")

if __name__ == "__main__":
    visualize_dem_interactive(tif_path="dem.tif", max_size=600, output_html="dem_viewer.html")