from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import sqlite3
import os

def generate_invoice(scoop_id):
    conn = sqlite3.connect("scoop_tracker.db")
    cursor = conn.cursor()

    # Fetch scoop + client info
    cursor.execute("""
        SELECT s.id, s.date, s.total_price, c.name, c.contact_info, c.email
        FROM scoops s
        JOIN clients c ON s.client_id = c.id
        WHERE s.id = ?
    """, (scoop_id,))
    scoop = cursor.fetchone()
    if not scoop:
        print("❌ Scoop not found!")
        return

    scoop_id, date, total_price, client_name, phone, email = scoop

    # Fetch items linked to this scoop
    cursor.execute("""
        SELECT i.name, si.quantity, i.cost_price, i.selling_price
        FROM scoop_items si
        JOIN items i ON si.item_id = i.id
        WHERE si.scoop_id = ?
    """, (scoop_id,))
    items = cursor.fetchall()
    conn.close()

    # Prepare PDF
    filename = f"invoice_{scoop_id}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    normal = styles["Normal"]

    # Add logo (if exists)
    if os.path.exists("assets/kay.png"):
        logo = Image("assets/kay.png", width=4*cm, height=4*cm)
        logo.hAlign = "LEFT"
        elements.append(logo)
        elements.append(Spacer(1, 0.5*cm))

    # Header
    elements.append(Paragraph("<b>Kay Scoops - Sweet Surprises</b>", title_style))
    elements.append(Spacer(1, 0.3*cm))
    elements.append(Paragraph(f"<b>Invoice #{scoop_id}</b>", normal))
    elements.append(Paragraph(f"Date: {date}", normal))
    elements.append(Spacer(1, 0.3*cm))

    # Client info
    elements.append(Paragraph(f"<b>Client:</b> {client_name}", normal))
    if phone:
        elements.append(Paragraph(f"<b>Phone:</b> {phone}", normal))
    if email:
        elements.append(Paragraph(f"<b>Email:</b> {email}", normal))
    elements.append(Spacer(1, 0.5*cm))

    # Item table
    table_data = [["Item", "Qty", "Cost Price (R)", "Selling Price (R)"]]
    for name, qty, cost, sell in items:
        table_data.append([name, qty, f"{cost:.2f}", f"{sell:.2f}"])

    table = Table(table_data, colWidths=[6*cm, 2*cm, 4*cm, 4*cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f2c4c4")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.5*cm))

    # Total
    elements.append(Paragraph(f"<b>Total: R{total_price:.2f}</b>", styles["Heading2"]))
    elements.append(Spacer(1, 0.5*cm))
    elements.append(Paragraph("Thank you for choosing Kay Scoops!", normal))

    # Build PDF
    doc.build(elements)
    print(f"✅ Invoice generated: {filename}")

if __name__ == "__main__":
    generate_invoice(1)  # Example: generate invoice for scoop with ID 1
