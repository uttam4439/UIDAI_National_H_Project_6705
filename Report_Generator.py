
from fpdf import FPDF
import os

class AadhaarReport(FPDF):
    def header(self):
        # Arial bold 15
        self.set_font('Arial', 'B', 15)
        # Move to the right
        self.cell(80)
        # Title
        self.cell(30, 10, 'Aadhaar Strategic Intelligence Report', 0, 0, 'C')
        # Line break
        self.ln(20)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

def generate_pdf():
    print("[1/1] Generating Consolidated PDF Report...")
    pdf = AadhaarReport()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Times', '', 12)

    # 1. Executive Summary
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(190, 10, '1. Executive Summary', 0, 1)
    pdf.set_font('Times', '', 12)
    
    summary_text = (
        "This strategic report transforms raw Aadhaar transactional logs into a predictive ecosystem. "
        "By identifying state-wise 'Identity Maturity' clusters and forecasting seasonal bursts, "
        "the UIDAI can transition from reactive service delivery to proactive resource management."
    )
    pdf.multi_cell(190, 10, summary_text)
    pdf.ln(5)

    # 2. Key Visualizations
    visuals = [
        ("Regional Maturity Clusters", "DataVisualisation/State_Maturity_Clusters.png"),
        ("Strategic Trend Forecast", "DataVisualisation/Advanced_Trend_Analysis.png"),
        ("Seasonal Student Peaks", "DataVisualisation/Seasonal_Student_Activity.png"),
        ("Center Pressure & Risk", "DataVisualisation/Center_Pressure_Risk.png")
    ]

    for title, img_path in visuals:
        if os.path.exists(img_path):
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(190, 10, f"Analysis: {title}", 0, 1)
            # Use a slightly smaller width and center it
            pdf.image(img_path, x=15, w=170)
            pdf.ln(10)
        else:
            print(f"   (!) Warning: Image not found at {img_path}")

    # 3. Recommendations
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(190, 10, '3. Strategic Recommendations', 0, 1)
    pdf.set_font('Times', '', 12)
    
    recs = [
        "1. Deploy mobile enrolment units to 'Growth Phase' states identified in clusters.",
        "2. Pre-allocate cloud resources 14 days before predicted 'Admission Bursts'.",
        "3. Implement automated approval for 90% of requests in 'Mature Hubs' to focus manual review on high-risk cases.",
        "4. Scale capacity in states hitting the 90% pressure threshold to prevent center congestion."
    ]
    for rec in recs:
        pdf.multi_cell(190, 10, rec)

    output_path = "Aadhaar_Strategic_Report.pdf"
    pdf.output(output_path)
    print(f"   -> Report successfully generated: {output_path}")

if __name__ == "__main__":
    generate_pdf()
