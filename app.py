import streamlit as st
import datetime
import os
from dotenv import load_dotenv

# Load local environment variables if available
load_dotenv()

# Set page config
st.set_page_config(
    page_title="RTI Generator & Rights Navigator",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        color: #1E3A8A;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 2rem;
    }
    .custom-card {
        background-color: #F3F4F6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1E3A8A;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Imports from utils
from utils.rti_templates import RTI_CATEGORIES
from utils.llm_agent import chat_with_navigator, optimize_rti_queries
from utils.pdf_generator import generate_rti_pdf
from utils.docx_generator import generate_rti_docx

# Initialize session states
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "generated_queries" not in st.session_state:
    st.session_state.generated_queries = []
if "show_preview" not in st.session_state:
    st.session_state.show_preview = False
if "formatted_draft_data" not in st.session_state:
    st.session_state.formatted_draft_data = {}

# Sidebar Configuration
st.sidebar.image("https://img.icons8.com/color/96/scales-of-justice.png", width=90)
st.sidebar.title("Configuration")

# Provider Selection
provider = st.sidebar.selectbox(
    "Select LLM Provider",
    ["Google Gemini", "OpenAI"],
    help="Select the AI service provider you want to use."
)

# Retrieve key from environment variable first, or let user input it
default_key = ""
if provider == "Google Gemini":
    default_key = os.getenv("GEMINI_API_KEY", "")
elif provider == "OpenAI":
    default_key = os.getenv("OPENAI_API_KEY", "")

api_key = st.sidebar.text_input(
    f"Enter {provider} API Key",
    type="password",
    value=default_key,
    help=f"Get your key from the {provider} developer portal. If set in the .env file, it is pre-loaded."
)
# Model Selection
if provider == "Google Gemini":
    model_options = ["gemini-3.6-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro", "Custom Model Name"]
    default_model_idx = 0
else:
    model_options = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo", "Custom Model Name"]
    default_model_idx = 0

selected_model_option = st.sidebar.selectbox(
    "Select Model",
    options=model_options,
    index=default_model_idx,
    help="Select the specific model version to use."
)

if selected_model_option == "Custom Model Name":
    model_name = st.sidebar.text_input(
        "Enter Custom Model Name", 
        value="gemini-3.6-flash" if provider == "Google Gemini" else "gpt-4o-mini",
        help="Input a specific model string, e.g., gemini-1.5-flash-8b"
    )
else:
    model_name = selected_model_option

# Help section for API keys
with st.sidebar.expander("🔑 How to get an API Key?"):
    if provider == "Google Gemini":
        st.markdown("[Get Google Gemini API Key (Free/Pay-as-you-go)](https://aistudio.google.com/)")
    else:
        st.markdown("[Get OpenAI API Key](https://platform.openai.com/api-keys)")

st.sidebar.divider()
st.sidebar.subheader("Quick Links")
st.sidebar.markdown("""
- 🌐 [Central RTI Online Portal](https://rtionline.gov.in/)
- 📄 [RTI Act 2005 Official Document](https://www.righttoinformation.gov.in/)
- 🏛️ [Central Information Commission](https://cic.gov.in/)
""")

# Main Content
st.markdown('<div class="main-title">⚖️ RTI Generator & Rights Navigator Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Empowering citizens with AI to navigate their legal rights and generate legally-sound RTI applications under the Right to Information Act, 2005 (India).</div>', unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["💬 Rights Navigator Chatbot", "📝 RTI Draft Generator", "ℹ️ Filing Guide & Portal Directory"])

# ==========================================
# TAB 1: RIGHTS NAVIGATOR CHATBOT
# ==========================================
with tab1:
    st.header("💬 Rights Navigator Chatbot")
    st.markdown("""
    Ask questions about the **Right to Information Act, 2005**. You can inquire about:
    - What type of information can be requested.
    - Application fees and payment methods.
    - Response timelines and exceptions (e.g. life/liberty cases).
    - What details are exempt from disclosure under Section 8.
    - How to file appeals if your request is ignored or rejected.
    """)
    
    # Pre-configured FAQ Questions
    st.subheader("💡 Quick Questions")
    col1, col2, col3, col4 = st.columns(4)
    faq_query = None
    if col1.button("💵 What is the filing fee?", use_container_width=True):
        faq_query = "What is the fee for filing an RTI application, and who is exempt from paying it?"
    if col2.button("⏱️ What is the response timeline?", use_container_width=True):
        faq_query = "What are the standard timelines for receiving information under the RTI Act?"
    if col3.button("🚫 What info is exempted?", use_container_width=True):
        faq_query = "What information is exempted from disclosure under Section 8 of the RTI Act?"
    if col4.button("⚖️ How to file a First Appeal?", use_container_width=True):
        faq_query = "What is the procedure and timeline for filing a First Appeal?"
        
    st.divider()

    # Clear chat button
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()

    # Display chat history
    for chat in st.session_state.chat_history:
        with st.chat_message(chat["role"]):
            st.markdown(chat["content"])

    # Chat input (handles standard user entry or FAQ button click)
    user_input = st.chat_input("Type your question here...")
    if faq_query:
        user_input = faq_query

    if user_input:
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Append user message to history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Call LLM
        with st.spinner("Analyzing rules & guidelines..."):
            if not api_key:
                ai_response = "⚠️ Please provide an API Key in the sidebar to use the Rights Navigator Chatbot."
            else:
                ai_response = chat_with_navigator(provider, api_key, st.session_state.chat_history[:-1], user_input, model_name=model_name)
        
        # Display AI message
        with st.chat_message("assistant"):
            st.markdown(ai_response)
            
        # Append AI message to history
        st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
        st.rerun()

# ==========================================
# TAB 2: RTI DRAFT GENERATOR
# ==========================================
with tab2:
    st.header("📝 RTI Draft Generator")
    st.markdown("""
    Fill out the form below. The AI optimizer will refine your query into precise, point-wise questions that minimize the chances of rejection by the Public Information Officer (PIO).
    """)

    col_form, col_preview = st.columns([1, 1])

    with col_form:
        st.subheader("Step 1: Applicant Details")
        app_name = st.text_input("Full Name of Applicant", placeholder="e.g. Ramesh Kumar")
        app_address = st.text_area("Correspondence Address", placeholder="Include Pin Code, City, and State")
        col_contact1, col_contact2 = st.columns(2)
        app_phone = col_contact1.text_input("Phone Number (Optional)", placeholder="e.g. +91 9876543210")
        app_email = col_contact2.text_input("Email ID (Optional)", placeholder="e.g. ramesh@example.com")
        
        st.subheader("Step 2: Target Department & PIO")
        pio_title = st.text_input("Recipient Officer Designation", value="The Public Information Officer", help="Usually 'The Public Information Officer' or 'The Assistant Public Information Officer'")
        dept_name = st.text_input("Department / Public Authority Name", placeholder="e.g., Regional Passport Office, Delhi")
        dept_address = st.text_area("Department Office Address", placeholder="Full physical address of the public authority's office")
        
        st.subheader("Step 3: Select Category & Describe Problem")
        # Template selection
        selected_category_key = st.selectbox(
            "Select RTI Topic / Category",
            options=list(RTI_CATEGORIES.keys()),
            format_func=lambda x: RTI_CATEGORIES[x]["name"]
        )
        
        category_data = RTI_CATEGORIES[selected_category_key]
        
        # Show suggested departments for selected category
        st.info(f"💡 **Suggested Departments for this topic:** {', '.join(category_data['suggested_departments'])}")
        
        # Customize subject
        default_subject = f"Information regarding {category_data['name'].lower()}."
        subject = st.text_input("Subject of Application", value=default_subject)
        
        # Period to which info relates
        period_relates = st.text_input("Period to which information relates", value="Current / Last 1 Year")
        
        # Checkbox selection for pre-defined points
        st.write("**Pre-structured template questions:** (Choose queries you want to include)")
        selected_points = []
        for point in category_data["standard_points"]:
            if st.checkbox(point, value=True):
                selected_points.append(point)
                
        # Raw problem input
        raw_problem = st.text_area(
            "Describe your specific problem / background details in your own words:",
            value=category_data["default_problem"],
            height=120,
            help="Describe the facts of your case. The AI will merge this with templates to generate optimized, legally suitable point-wise questions."
        )

        st.subheader("Step 4: Fees & Below Poverty Line (BPL) Info")
        is_bpl = st.checkbox("I belong to the Below Poverty Line (BPL) category", help="BPL cardholders are exempt from paying the Rs. 10 application fee.")
        
        bpl_proof = ""
        payment_mode = ""
        payment_details = ""
        
        if is_bpl:
            bpl_proof = st.text_input("BPL Certificate / Card No. & Date of Issue", placeholder="e.g., BPL Card No. 987654 issued on DD/MM/YYYY by SDM Office")
        else:
            payment_mode = st.selectbox(
                "Fee Payment Mode",
                ["Indian Postal Order (IPO)", "Demand Draft (DD)", "Banker's Cheque", "Court Fee Stamp", "Online Payment Transfer"]
            )
            payment_details = st.text_input(
                "Payment Instrument Serial Number & Date", 
                placeholder="e.g., IPO No. 45G 987654 dated 20/08/2026",
                help="Enter serial number, transaction ID, stamp serial number and the date of purchase."
            )
            
        st.subheader("Step 5: Submission Details")
        col_sub1, col_sub2 = st.columns(2)
        app_date = col_sub1.text_input("Date of Application", value=datetime.date.today().strftime("%d/%m/%Y"))
        app_place = col_sub2.text_input("Place of Application", placeholder="e.g., New Delhi")

        # Submission Button
        st.write("---")
        generate_btn = st.button("🚀 Optimize & Generate RTI Application", use_container_width=True)

    with col_preview:
        st.subheader("🔍 Application Preview & Edits")
        
        if generate_btn:
            if not api_key:
                st.error("⚠️ Please enter your API key in the sidebar to generate the RTI Application.")
            elif not app_name or not app_address or not dept_name:
                st.error("⚠️ Please fill in at least Applicant Name, Correspondence Address, and Department Name to proceed.")
            else:
                with st.spinner("AI is optimizing your queries to comply with RTI standards..."):
                    # Trigger LLM optimizer
                    result = optimize_rti_queries(
                        provider=provider,
                        api_key=api_key,
                        category_name=category_data["name"],
                        department_name=dept_name,
                        raw_problem=raw_problem,
                        selected_template_points=selected_points,
                        model_name=model_name
                    )
                    
                    if "error" in result:
                        st.error(result["error"])
                        if "raw_response" in result:
                            st.text("Raw response from LLM:")
                            st.code(result["raw_response"])
                    else:
                        st.session_state.generated_queries = result["queries"]
                        st.session_state.show_preview = True
                        
                        # Populate data structure
                        st.session_state.formatted_draft_data = {
                            "recipient_pio": pio_title,
                            "department_name": dept_name,
                            "department_address": dept_address,
                            "applicant_name": app_name,
                            "applicant_address": app_address,
                            "phone": app_phone,
                            "email": app_email,
                            "subject": subject,
                            "period_relates": period_relates,
                            "is_bpl": is_bpl,
                            "bpl_proof": bpl_proof,
                            "payment_mode": payment_mode,
                            "payment_details": payment_details,
                            "date": app_date,
                            "place": app_place
                        }
        
        if st.session_state.show_preview:
            st.success("✅ Queries optimized successfully! You can review and edit them below.")
            
            # Interactive editable queries
            st.write("✏️ **Edit/Refine the Point-wise Questions:**")
            edited_queries = []
            
            for idx, q in enumerate(st.session_state.generated_queries):
                edited_q = st.text_area(f"Question {idx + 1}", value=q, key=f"q_edit_{idx}", height=65)
                edited_queries.append(edited_q)
            
            # Button to add a new query
            if st.button("➕ Add Custom Question"):
                st.session_state.generated_queries.append("Please provide...")
                st.rerun()
                
            # Keep updated queries
            st.session_state.formatted_draft_data["queries"] = edited_queries
            
            # Display preview layout of the letter
            st.subheader("Formatted Letter Preview")
            
            preview_data = st.session_state.formatted_draft_data
            
            # Format display text
            q_list_str = "\n".join([f"({i+1}) {q}" for i, q in enumerate(edited_queries)])
            
            bpl_info_str = f"Yes (Proof details: {preview_data['bpl_proof']})" if preview_data['is_bpl'] else "No"
            fee_info_str = "Application fee is EXEMPTED as applicant is BPL." if preview_data['is_bpl'] else f"Fee Amount: Rs. 10/-\nPayment Mode: {preview_data['payment_mode']}\nInstrument/Txn No: {preview_data['payment_details']}"
            
            letter_text = f"""RTI APPLICATION FORM
Under Section 6(1) of the Right to Information Act, 2005

To,
{preview_data['recipient_pio']}
{preview_data['department_name']}
{preview_data['department_address']}

Subject: Application seeking information under the Right to Information Act, 2005.

1. Name of the Applicant: {preview_data['applicant_name']}
2. Address for Correspondence: {preview_data['applicant_address']}
   Phone: {preview_data['phone']} | Email: {preview_data['email']}
3. Citizenship Status: Indian Citizen

4. Particulars of Information Sought:
   (a) Subject matter of information: {preview_data['subject']}
   (b) Period to which the information relates: {preview_data['period_relates']}
   (c) Specific Information required:
{q_list_str}

5. Whether applicant belongs to Below Poverty Line (BPL) category: {bpl_info_str}
6. Application Fee Details:
{fee_info_str}

Declaration:
I state that the information sought does not fall within the restrictions contained in Section 8 of the RTI Act, 2005, and to the best of my knowledge, it pertains to your office.
I am a citizen of India.

Date: {preview_data['date']}
Place: {preview_data['place']}

Signature of the Applicant
___________________________
Name: {preview_data['applicant_name']}
"""
            st.text_area("Letter Text (Ready to copy)", value=letter_text, height=350)
            
            # Download actions
            st.write("📥 **Export Documents:**")
            col_dl1, col_dl2 = st.columns(2)
            
            # PDF Generation & Download
            try:
                pdf_stream = generate_rti_pdf(preview_data)
                col_dl1.download_button(
                    label="📄 Download PDF",
                    data=pdf_stream,
                    file_name=f"RTI_Application_{preview_data['applicant_name'].replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                col_dl1.error(f"Error generating PDF: {str(e)}")
                
            # DOCX Generation & Download
            try:
                docx_stream = generate_rti_docx(preview_data)
                col_dl2.download_button(
                    label="📝 Download Word Document (.docx)",
                    data=docx_stream,
                    file_name=f"RTI_Application_{preview_data['applicant_name'].replace(' ', '_')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
            except Exception as e:
                col_dl2.error(f"Error generating DOCX: {str(e)}")
        else:
            st.info("Fill out the form on the left and click 'Optimize & Generate' to preview your RTI letter here.")

# ==========================================
# TAB 3: FILING GUIDE & PORTAL DIRECTORY
# ==========================================
with tab3:
    st.header("ℹ️ Filing Guide & Portal Directory")
    
    st.markdown("""
    Once you have generated and downloaded your RTI application, follow these steps to file it:
    """)

    st.subheader("🌐 Option A: Online Filing (Recommended)")
    st.markdown("""
    Many central and state government departments accept RTI applications online.
    
    1. **Central Ministries/Departments**: Go to [rtionline.gov.in](https://rtionline.gov.in/).
    2. Register or submit application as guest.
    3. Fill in the online form and **copy-paste the point-wise queries** generated by this tool into the description box.
    4. Upload the generated PDF as a supporting document (especially useful for keeping formatting).
    5. Pay Rs. 10 fee online via UPI, Netbanking, or Debit/Credit card.
    
    *Note: Various states have their own online RTI portals. For example:*
    - **Maharashtra**: [rtionline.maharashtra.gov.in](https://rtionline.maharashtra.gov.in/)
    - **Karnataka**: [rtionline.karnataka.gov.in](https://rtionline.karnataka.gov.in/)
    - **Uttar Pradesh**: [rtionline.up.gov.in](https://rtionline.up.gov.in/)
    - **Delhi**: [rtionline.delhi.gov.in](https://rtionline.delhi.gov.in/)
    """)
    
    st.subheader("📬 Option B: Offline Filing (Speed Post / Registered Post)")
    st.markdown("""
    If online filing is not available, you can send it via physical mail:
    
    1. **Print the Letter**: Print the downloaded PDF or Word file.
    2. **Sign the Application**: Manually sign at the bottom.
    3. **Pay the Fee**:
       - Purchase a **Rs. 10 Indian Postal Order (IPO)** from your local post office.
       - Fill in the IPO: Pay to "Accounts Officer, [Name of Department]" and write your name and address on the back.
       - Note the IPO serial number and date and write it under the "Fee Details" section of your application before printing, or write it manually in the printed application.
       - Attach the IPO securely to your application.
    4. **For BPL Applicants**: Do not buy an IPO. Instead, attach a self-attested photocopy of your **BPL Card / Ration Card / Certificate**.
    5. **Envelope**: Put the application and fee/BPL proof inside an envelope.
    6. **Address it clearly**:
       ```text
       To,
       The Public Information Officer (PIO)
       [Name of Department]
       [Office Address]
       ```
       Write **"APPLICATION UNDER RTI ACT, 2005"** in bold on top of the envelope.
    7. **Post It**: Send it via **Speed Post** or **Registered Post AD** (Acknowledgment Due) at the post office. Do not use ordinary post, as it cannot be tracked.
    8. **Keep Proof**: Keep the post office receipt and a photocopy of the signed application safely for your records. The 30-day countdown begins on the date the office receives the mail.
    """)
    
    st.subheader("⏳ What Happens Next?")
    st.markdown("""
    - The department has **30 days** to reply from the date they receive your application.
    - If you receive no reply, or a partial/misleading reply, you have **30 days** from the expiry of the deadline to file a **First Appeal** with the First Appellate Authority (FAA) of the same department.
    """)

# Trigger Streamlit hot reload of utility modules
