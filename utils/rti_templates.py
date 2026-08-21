RTI_CATEGORIES = {
    "passport_delay": {
        "name": "Passport Issuance Delay",
        "suggested_departments": [
            "Regional Passport Office (RPO)",
            "Ministry of External Affairs (MEA)",
            "Local Police Station (for verification delays)"
        ],
        "default_problem": "I applied for a passport renewal 2 months ago, completed police verification, but the status is still showing 'Pending police verification' or 'Under review'.",
        "standard_points": [
            "Please provide the daily progress report of my passport application with File Number [Enter File Number] from the date of application to the current date.",
            "Please provide the names, designations, and contact details of the officials with whom my application has been pending during this period, along with the duration it remained with each official.",
            "Please provide copies of the police verification report received by the Passport Office in connection with this application.",
            "Please provide the standard turnaround time (TAT) prescribed by the Ministry of External Affairs for processing and issuing passports after successful police verification.",
            "If the application is delayed beyond the prescribed TAT, please provide copies of all official correspondence, file notes, or emails concerning the delay in issuing my passport."
        ]
    },
    "municipal_road": {
        "name": "Road Repair & Maintenance",
        "suggested_departments": [
            "Municipal Corporation (e.g., BMC, MCD, BBMP, etc.)",
            "Public Works Department (PWD)",
            "Urban Development Authority"
        ],
        "default_problem": "The main road in our sector has huge potholes, causing accidents, and has not been repaired for over a year despite multiple complaints.",
        "standard_points": [
            "Please provide the total budget allocated, sanctioned, and spent on the construction, repair, and maintenance of [Enter Road Name] during the financial years [Enter Years, e.g., 2024-25 and 2025-26].",
            "Please provide the name of the contractor/agency to whom the work order for repairing [Enter Road Name] was awarded, along with a certified copy of the contract agreement and work order.",
            "Please provide a copy of the road inspection report or safety audit conducted by the department engineers for [Enter Road Name] in the last 12 months.",
            "Please provide the start date, scheduled completion date, and actual completion date of the last road repair work executed on [Enter Road Name].",
            "Please provide the details of the 'Defect Liability Period' (DLP) for the last road work executed on this stretch, and whether any action has been taken against the contractor for premature road damage during this period."
        ]
    },
    "pension_delay": {
        "name": "Delay in Government Pension Payment",
        "suggested_departments": [
            "Office of the Principal Controller of Defence Accounts (PCDA)",
            "Directorate of Pensions",
            "State/Central Pension Disbursing Authority (or bank branch)"
        ],
        "default_problem": "I retired from service 6 months ago, but my pension payments have not started, and my retirement gratuity has not been credited.",
        "standard_points": [
            "Please provide the current status of my pension file and Pension Payment Order (PPO) number [Enter PPO Number, if available] or Service Book No [Enter Details].",
            "Please provide the date-wise progress report showing the movement of my pension file among various desks/officers from the date of retirement to the current date.",
            "Please provide the names and designations of the officials responsible for processing my pension file, and state the reasons for delay at each stage beyond the timelines prescribed in the Civil Services (Pension) Rules.",
            "Please provide a copy of all file notes, official remarks, and correspondence related to the processing and approval of my pension and gratuity payments."
        ]
    },
    "exam_evaluation": {
        "name": "Answer Sheet & Marks Verification",
        "suggested_departments": [
            "State/Central Public Service Commission (e.g., UPSC, SPSC)",
            "Board of Secondary/Higher Education",
            "Government University Examination Registrar"
        ],
        "default_problem": "I appeared for the competitive exam, but my marks were much lower than expected. I want a copy of my evaluated answer sheet and the answer key.",
        "standard_points": [
            "Please provide a certified photocopy of my evaluated answer sheet (OMR sheet or written script) for the exam [Enter Exam Name] held on [Enter Date] having Roll Number [Enter Roll Number].",
            "Please provide a copy of the official model answer key, marking scheme, and evaluation guidelines used by examiners for the said examination.",
            "Please provide the highest and lowest marks scored by candidates who qualified in my category ([Enter Category, e.g., General/OBC/SC/ST]) for the said exam.",
            "Please provide a copy of the cut-off marks list determined by the commission/board for qualification in each stage of the said examination."
        ]
    },
    "land_records": {
        "name": "Land Records & Property Mutation",
        "suggested_departments": [
            "Tehsildar/Revenue Office",
            "Land Records Department / Bhulekh",
            "Registrar / Sub-Registrar of Assurances"
        ],
        "default_problem": "I applied for property mutation (transfer of name in land records) 3 months ago, paid the fees, but the mutation certificate is still not issued.",
        "standard_points": [
            "Please provide the current status of my application for property mutation with application number [Enter Application No] submitted on [Enter Date].",
            "Please provide a certified copy of the mutation register entry or RoR (Record of Rights) for land parcel Survey No [Enter Survey No] located at [Enter Village/Tehsil].",
            "Please provide the names and designations of the officials with whom my mutation application is currently pending, along with the date-wise record of its movement.",
            "Please provide a copy of the citizen charter or departmental rules specifying the time limit within which property mutation applications must be processed and completed."
        ]
    },
    "custom": {
        "name": "Custom / General Query",
        "suggested_departments": [
            "Relevant Ministry or Department"
        ],
        "default_problem": "Provide a brief description of your issue and the specific information you wish to request.",
        "standard_points": [
            "Please provide a copy of the policy/guidelines governing [Enter Subject].",
            "Please provide the status and copies of file notes regarding the representation/complaint dated [Enter Date] submitted by me on [Enter Topic]."
        ]
    }
}
