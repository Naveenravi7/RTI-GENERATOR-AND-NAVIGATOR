from fpdf import FPDF
import io

class RTIPDF(FPDF):
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Times italic 8
        self.set_font('times', 'I', 8)
        # Page number
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')

def generate_rti_pdf(data):
    """
    Generates a PDF for the RTI application using fpdf2.
    'data' dictionary contains:
    - recipient_pio
    - department_name
    - department_address
    - applicant_name
    - applicant_address
    - email
    - phone
    - subject
    - period_relates
    - queries
    - is_bpl
    - bpl_proof
    - payment_mode
    - payment_details
    - date
    - place
    """
    pdf = RTIPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # Margins
    pdf.set_margins(left=20, top=20, right=20)
    
    # Title / Header
    pdf.set_font('times', 'B', 14)
    pdf.cell(0, 10, 'RTI APPLICATION FORM', border=0, ln=1, align='C')
    
    pdf.set_font('times', 'I', 10)
    pdf.cell(0, 5, 'Under Section 6(1) of the Right to Information Act, 2005', border=0, ln=1, align='C')
    pdf.ln(10)
    
    # Recipient
    pdf.set_font('times', 'B', 11)
    pdf.cell(0, 6, 'To,', ln=1)
    pdf.set_font('times', '', 11)
    pdf.multi_cell(0, 5, f"{data.get('recipient_pio', 'The Public Information Officer')}\n"
                         f"{data.get('department_name', '[Name of Public Authority]')}\n"
                         f"{data.get('department_address', '[Address of Public Authority]')}")
    pdf.ln(5)
    
    # Subject
    pdf.set_font('times', 'B', 11)
    pdf.cell(16, 6, 'Subject: ')
    pdf.set_font('times', '', 11)
    pdf.multi_cell(0, 6, "Application seeking information under the Right to Information Act, 2005.")
    pdf.ln(5)
    
    # 1. Applicant Name
    pdf.set_font('times', 'B', 11)
    pdf.cell(45, 6, '1. Name of the Applicant: ')
    pdf.set_font('times', '', 11)
    pdf.cell(0, 6, data.get('applicant_name', ''), ln=1)
    
    # 2. Address
    pdf.set_font('times', 'B', 11)
    pdf.cell(52, 6, '2. Address for Correspondence: ')
    pdf.set_font('times', '', 11)
    pdf.multi_cell(0, 6, data.get('applicant_address', ''))
    
    # Contact Details
    if data.get('phone') or data.get('email'):
        pdf.set_font('times', 'B', 11)
        pdf.cell(52, 6, '   Contact Details: ')
        pdf.set_font('times', '', 11)
        contact_str = ""
        if data.get('phone'):
            contact_str += f"Phone: {data.get('phone')}"
        if data.get('email'):
            if contact_str:
                contact_str += ", "
            contact_str += f"Email: {data.get('email')}"
        pdf.cell(0, 6, contact_str, ln=1)
        
    # 3. Citizenship
    pdf.set_font('times', 'B', 11)
    pdf.cell(45, 6, '3. Citizenship Status: ')
    pdf.set_font('times', '', 11)
    pdf.cell(0, 6, 'Indian Citizen', ln=1)
    pdf.ln(2)
    
    # 4. Particulars of Information Sought
    pdf.set_font('times', 'B', 11)
    pdf.cell(0, 6, '4. Particulars of Information Sought:', ln=1)
    
    # (a) Subject matter
    pdf.set_font('times', 'BI', 11)
    pdf.cell(10, 6, '')
    pdf.cell(60, 6, '(a) Subject matter of information: ')
    pdf.set_font('times', '', 11)
    pdf.multi_cell(0, 6, data.get('subject', ''))
    
    # (b) Period
    pdf.set_font('times', 'BI', 11)
    pdf.cell(10, 6, '')
    pdf.cell(75, 6, '(b) Period to which the information relates: ')
    pdf.set_font('times', '', 11)
    pdf.cell(0, 6, data.get('period_relates', 'Not Applicable / Current'), ln=1)
    
    # (c) Specific queries
    pdf.set_font('times', 'BI', 11)
    pdf.cell(10, 6, '')
    pdf.cell(0, 6, '(c) Specific Information required:', ln=1)
    
    queries = data.get('queries', [])
    for idx, query in enumerate(queries, 1):
        # Indent and print bullet query
        pdf.set_font('times', 'B', 11)
        pdf.cell(15, 6, '')
        pdf.cell(8, 6, f"({idx}) ")
        pdf.set_font('times', '', 11)
        pdf.multi_cell(0, 6, query)
    pdf.ln(2)
        
    # 5. BPL status
    pdf.set_font('times', 'B', 11)
    pdf.cell(110, 6, '5. Whether the applicant belongs to Below Poverty Line (BPL) category? ')
    pdf.set_font('times', '', 11)
    is_bpl = data.get('is_bpl', False)
    pdf.cell(0, 6, 'Yes' if is_bpl else 'No', ln=1)
    
    if is_bpl:
        pdf.set_font('times', 'BI', 11)
        pdf.cell(10, 6, '')
        pdf.cell(60, 6, 'BPL Card / Certificate Proof Details: ')
        pdf.set_font('times', '', 11)
        pdf.multi_cell(0, 6, data.get('bpl_proof', '[BPL Certificate Details] (Copy Attached)'))
    
    # 6. Fees details
    pdf.set_font('times', 'B', 11)
    pdf.cell(0, 6, '6. Application Fee Details:', ln=1)
    
    pdf.set_font('times', '', 11)
    pdf.cell(10, 6, '')
    if is_bpl:
        pdf.multi_cell(0, 6, 'Application fee is EXEMPTED as the applicant belongs to the Below Poverty Line (BPL) category.')
    else:
        pdf.multi_cell(0, 6, f"Fee Amount: Rs. 10/-\n"
                             f"Mode of Payment: {data.get('payment_mode', 'Indian Postal Order (IPO)')}\n"
                             f"Instrument / Transaction No. & Date: {data.get('payment_details', '[Provide details]')}")
    pdf.ln(4)
        
    # Declarations
    pdf.set_font('times', 'B', 11)
    pdf.cell(0, 6, 'Declaration:', ln=1)
    pdf.set_font('times', '', 11)
    pdf.multi_cell(0, 5, "I state that the information sought does not fall within the restrictions contained in Section 8 of the RTI Act, 2005, and to the best of my knowledge, it pertains to your office.\n"
                         "I am a citizen of India.")
    pdf.ln(8)
    
    # Signature block
    current_y = pdf.get_y()
    
    # Date & Place
    pdf.set_xy(20, current_y)
    pdf.multi_cell(80, 5, f"Date: {data.get('date', '')}\nPlace: {data.get('place', '')}")
    
    # Signature on the right
    pdf.set_xy(120, current_y)
    pdf.multi_cell(70, 5, "___________________________________\n"
                         "Signature of the Applicant\n"
                         f"Name: {data.get('applicant_name', '')}", align='R')
    
    # Output to byte stream
    # Note: fpdf2 output() can return a bytearray, or write to a string/file. 
    # Calling output() with no args returns bytes in fpdf2 or writes to string depending on version.
    # To be safe and compatible across versions, we can use dest='S' or get the byte string.
    # In newer fpdf2 versions, output() without arguments returns a bytearray/bytes, which can be wrapped in BytesIO.
    pdf_bytes = pdf.output()
    if isinstance(pdf_bytes, str):
        # encode it if it is a string (older versions)
        pdf_bytes = pdf_bytes.encode('latin1')
    return io.BytesIO(pdf_bytes)
