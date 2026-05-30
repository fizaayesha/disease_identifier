from fpdf import FPDF
import os

def generate_pdf(clean_text, confidence):
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    try:
        if os.path.exists("./logo.jpeg"):
            pdf.image("./logo.jpeg", x=10, y=8, w=33)
    except:
        pass
        
    pdf.set_font("helvetica", "B", 24)
    pdf.set_text_color(30, 144, 255) # DodgerBlue
    pdf.cell(0, 20, "Medical Analysis Report", ln=True, align="R")
    
    pdf.ln(10)
    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)
    
    # Content
    if confidence is not None:
        pdf.set_font("helvetica", "B", 14)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, f"Confidence Score: {confidence:.2f}%", ln=True)
        pdf.ln(5)
    
    pdf.set_font("helvetica", "", 12)
    pdf.set_text_color(50, 50, 50)
    # fpdf2 handles UTF-8 content automatically
    pdf.multi_cell(0, 8, clean_text)
    
    # Footer
    pdf.ln(20)
    pdf.set_font("helvetica", "I", 10)
    pdf.set_text_color(128, 128, 128)
    pdf.multi_cell(0, 10, "Disclaimer: This report is AI-generated and intended for informational purposes only. Consult with a qualified healthcare professional before making any medical decisions.", align="C")
    
    return pdf.output()
