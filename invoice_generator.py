
from fpdf import FPDF
import sqlite3
import os

class InvoicePDF(FPDF):
    def header(self):
        # Optional global header override (we'll build manually instead)
        pass

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

    # Calculate total cost price
    total_cost_price = sum(qty * cost for _, qty, cost, _ in items)

    # Prepare PDF
    filename = f"invoice_{scoop_id}.pdf"
    pdf = InvoicePDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Logo
    if os.path.exists("assets/kay.png"):
        pdf.image("assets/kay.png", x=10, y=10, w=30)
        pdf.ln(25)

    # Title
    pdf.set_text_color(120, 60, 60)   # soft warm reddish-brown
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 10, "Kay Scoops - Sweet Surprises", ln=True)
    pdf.set_text_color(0, 0, 0)  # reset
    
    pdf.set_font("Helvetica", "", 12)
    pdf.ln(3)
    pdf.cell(0, 8, f"Invoice #{scoop_id}", ln=True)
    pdf.cell(0, 6, f"Date: {date}", ln=True)
    pdf.ln(4)

    # Client info
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 6, "Client Information:", ln=True)

    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 6, f"Name: {client_name}", ln=True)
    if phone:
        pdf.cell(0, 6, f"Phone: {phone}", ln=True)
    if email:
        pdf.cell(0, 6, f"Email: {email}", ln=True)
    pdf.ln(5)

    # TABLE HEADER
    pdf.set_fill_color(242, 196, 196)  # #f2c4c4
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 12)

    pdf.cell(60, 10, "Item", border=1, align="C", fill=True)
    pdf.cell(20, 10, "Qty", border=1, align="C", fill=True)
    pdf.cell(40, 10, "Cost Price (R)", border=1, align="C", fill=True)
    pdf.cell(40, 10, "Selling Price (R)", border=1, align="C", fill=True)
    pdf.ln()

    # TABLE ROWS
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 12)

    for name, qty, cost, sell in items:
        pdf.cell(60, 10, name, border=1, align="C")
        pdf.cell(20, 10, str(qty), border=1, align="C")
        pdf.cell(40, 10, f"{cost:.2f}", border=1, align="C")
        pdf.cell(40, 10, f"{sell:.2f}", border=1, align="C")
        pdf.ln()

    pdf.ln(5)

    # TOTALS SECTION
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 8, f"Total Selling Price: R{total_price:.2f}", ln=True)

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 8, f"Total Cost Price: R{total_cost_price:.2f}", ln=True)

    pdf.ln(8)
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, "Thank you for choosing Kay Scoops!", ln=True)

    # Save PDF
    pdf.output(filename)
    print(f"✅ Invoice generated: {filename}")

if __name__ == "__main__":
    generate_invoice(1)

