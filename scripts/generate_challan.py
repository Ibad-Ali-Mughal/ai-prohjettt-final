# from reportlab.lib.pagesizes import A4
# from reportlab.pdfgen import canvas
# import os

# def generate_challan(pdf_path, data):
#     os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

#     c = canvas.Canvas(pdf_path, pagesize=A4)
#     w, h = A4

#     c.setFont("Helvetica-Bold", 16)
#     c.drawString(200, h - 50, "E-CHALLAN")

#     c.setFont("Helvetica", 10)
#     c.drawString(50, h - 90, f"Date: {data['date']}")
#     c.drawString(50, h - 110, f"Time: {data['time']}")
#     c.drawString(50, h - 130, f"Vehicle ID: {data['vehicle_id']}")
#     c.drawString(50, h - 150, f"Vehicle Type: {data['vehicle_type']}")
#     c.drawString(50, h - 170, f"Speed: {data['speed']} km/h")

#     y = h - 210
#     c.setFont("Helvetica-Bold", 11)
#     c.drawString(50, y, "Violations:")
#     y -= 20

#     c.setFont("Helvetica", 10)
#     for v, amt in data["breakdown"].items():
#         c.drawString(70, y, f"{v}: Rs {amt}")
#         y -= 18

#     y -= 10
#     c.setFont("Helvetica-Bold", 12)
#     c.drawString(50, y, f"TOTAL FINE: Rs {data['total']}")

#     c.showPage()
#     c.save()
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import os

def generate_challan(pdf_path, data):
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    # ================= HEADER =================
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(width / 2, height - 50, "E-CHALLAN")

    c.setLineWidth(1)
    c.line(40, height - 65, width - 40, height - 65)

    # ================= VEHICLE DETAILS =================
    c.setFont("Helvetica", 11)
    y = height - 110

    c.drawString(60, y,     f"Date: {data['date']}")
    c.drawString(60, y-18,  f"Time: {data['time']}")
    c.drawString(60, y-36,  f"Vehicle ID: {data['vehicle_id']}")
    c.drawString(60, y-54,  f"Vehicle Type: {data['vehicle_type']}")
    c.drawString(60, y-72,  f"Speed: {data['speed']} km/h")

    # ================= VIOLATIONS =================
    c.setFont("Helvetica-Bold", 13)
    c.drawString(60, y - 105, "Violations:")

    c.setFont("Helvetica", 11)
    vy = y - 125
    for v in data["violations"]:
        c.drawString(80, vy, f"- {v}")
        vy -= 16

    # ================= FINE =================
    c.setFont("Helvetica-Bold", 14)
    c.drawString(60, vy - 15, f"TOTAL FINE: Rs. {data['total_fine']}")

    # ================= IMAGE (MAIN FIX) =================
    img_path = data.get("image_path")

    if img_path and os.path.exists(img_path):
        try:
            img = ImageReader(img_path)

            img_width = 260     # BIG image
            img_height = 340

            img_x = (width - img_width) / 2
            img_y = 90          # Centered vertically

            c.drawImage(
                img,
                img_x,
                img_y,
                img_width,
                img_height,
                preserveAspectRatio=True,
                mask="auto"
            )

            c.setFont("Helvetica-Oblique", 10)
            c.drawCentredString(
                width / 2,
                img_y - 14,
                "Violation Evidence"
            )

        except Exception:
            c.setFont("Helvetica", 10)
            c.drawString(60, 120, "Error loading violation image")

    # ================= FOOTER =================
    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(
        width / 2,
        40,
        "This is a system-generated e-challan. No signature required."
    )

    c.showPage()
    c.save()
