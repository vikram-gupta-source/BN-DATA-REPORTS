from queries import summaryQueries, dataSheetQueries, mentorAuditQueries, analysisReportQuery
from utils import summaryTable, dataSheets, recordUpdate, removePaidData, mentorAudit, socialMediaNewLeadSummaryGenerator, morningLeadReportGenerator, dataSheetFormatting, salesAnalysisReport
import streamlit as st
from datetime import datetime
from dateutil.relativedelta import relativedelta
from concurrent.futures import ThreadPoolExecutor

mentors = {
    'Aasiya': 183,
    'Arpita': 85,
    'Charu': 232,
    'Hardi': 88,
    'KajalS': 277,
    'Kajal': 52,
    'Nazneen': 163,
    'Omanshi': 275,
    'Prajakta': 57,
    'PrajaktaT': 240,
    'Rashmi': 260,
    'Sahejpreet': 249,
    'Shraddha': 158,
    'Urmila': 152,
    'UrmilaR': 266,
    'Vartika': 245,
    'Zahra': 271,
    'Shirin': 268
}

options = [
    'SELECT', 'Sheet Formatting', 'Audit Report', 'Summary Report',
    'Data Sheet', 'Remove Paid Data', "Update Yesterdays' Entry",
    "Analysis Report"
]

reports = [
    "Khyati Ma'ams' Morning Lead Consultaion Report",
    'OCR Client Summary Report', 'All Active Client Summary Report',
    'All Active Clients (Plat & Preg) Summary Report',
    'New & OL(Without Ref) Summary Report', 'Counsellor Sales Analysis Report',
    'Basic Stack Not Upgraded To Special Stack Summary Report(Lead)',
    'Basic Stack Not Upgraded To Special Stack Summary Report(OCR)',
    'All Active Clients(No Adv. Purchase) Pitched Summary Report',
    'Tailend No Advance Purchase Pitched Summary Report',
    'Induction Call Not Done Summary Report', 'App Not Update Summary Report',
    'Half Time Feedback Summary Report', 'Final Feedback Summary Report',
    "COM Call Summary Report", "EOD Khyati Mam New Lead Report",
    "EOD Khyati Mam Old Lead Report",
    "Gut Detox Assigned Leads Summary Report",
    "Khyati Ma'ams' SM New Leads Summary Report",
    "Social Media Assigned Leads Summary Report"
]

sheet = [
    'Tailend Clients Un-Pitched Data Sheet',
    'Mentor Un-Paid All Rate Shared Data Sheet',
    'Mentor All Active (No Adv Purchase) Un-Pitched Data Sheet',
    'Mentor All Active (No Adv Purchase) Above 70 kg Un-Pitched Data Sheet',
    'All Nutritionist Assigned Un-Paid Leads Data Sheet',
    'All Nutritionist Assigned Un-Paid Indian Leads Data Sheet',
    'All Nutritionist Assigned Un-Paid NRI Leads Data Sheet',
    'Mentor Un-Paid Assigned New Leads Data Sheet',
    'Mentor Un-Paid Assigned OL Leads Data Sheet',
    'Mentor Un-Paid Assigned New Indian Leads Data Sheet',
    'Mentor Un-Paid Assigned New NRI Leads Data Sheet',
    'Mentor Un-Paid Assigned OL Indian Leads Data Sheet',
    'Mentor Un-Paid Assigned OL NRI Leads Data Sheet',
    'All Active Client Page Visits Data Sheet',
    'All Active Client Checkout Page Visits Data Sheet',
    'OCR Client Page Visits Data Sheet',
    'OCR Client Checkout Page Visits Data Sheet',
    'WMR Sent Diet Not Receieved Over Due 24 hrs. Sheet',
    'NAF Sent Diet Not Receieved Over Due 24 hrs. Sheet',
    'Induction Call Not Done Data Sheet',
    'Good Weight Loss Active Clients Data Sheet',
    'Basic Stack Not Upgraded to Special stack (Lead) Data Sheet',
    'Basic Stack Not Upgraded to Speical Stack (OCR) Data Sheet',
    'COM Call Not Done Data Sheet', 'Half Time Feedback Data Sheet'
]

analysis_report_list = [
    'Counsellor Performance Analysis Report', 'Lead Count Summary Report',
    'Lead Medical Count Summary Report'
]

st.title("BN Report & Sheet Panel")

option = st.selectbox("Select An Options You Need", options)

if option == 'Summary Report':
    selected_report = st.selectbox("Select A Required Summary Report", reports)
    first_day_of_current_month = datetime.today().replace(day=1).date()
    with st.container():
        # Create two columns
        col1, col2 = st.columns(2)

        # In the first column, add a date input box
        with col1:
            start_date = st.date_input("Start Date",
                                       first_day_of_current_month)

        # In the second column, add another date input box
        with col2:
            end_date = st.date_input("End Date", datetime.today())
    date_object = datetime.strptime(str(start_date), "%Y-%m-%d")
    # Precompute date values
    month = date_object.strftime('%b')
    year = date_object.year

    # Create the summaryQueries object once
    summary_query = summaryQueries(start_date, end_date)

    # Define a dictionary with report configurations
    report_config = {
        'OCR Client Summary Report': {
            'query': summary_query.ocrClientSummaryQuery(),
            'title': f"OCR Clients Summary Report {month} {year} MTD",
            'title_font_size': 10,
            'table_width': 4,
            'table_font_size': 10,
            'title_space': 2.4
        },
        'All Active Client Summary Report': {
            'query': summary_query.allactiveClientSummaryQuery(),
            'title': f"All Active Clients Summary Report {month} {year} MTD",
            'title_font_size': 14,
            'table_width': 11,
            'table_font_size': 11,
            'title_space': 2.25
        },
        'New & OL(Without Ref) Summary Report': {
            'query': summary_query.leadWithoutRefSummaryQuery(),
            'title':
            f"Leads(New & OL)(Without Referral) Summary Report {month} {year} MTD",
            'title_font_size': 12,
            'table_width': 8,
            'table_font_size': 11,
            'title_space': 1.4
        },
        'All Active Clients(No Adv. Purchase) Pitched Summary Report': {
            'query': summary_query.activeNoAdvPurchaseSummaryQuery(),
            'title':
            f"All Active Clients(No Adv. Purchase) Pitched Summary Report {month} {year} MTD",
            'title_font_size': 11,
            'table_width': 8,
            'table_font_size': 11,
            'title_space': 1.34
        },
        'All Active Clients (Plat & Preg) Summary Report': {
            'query': summary_query.activePregPlatClientSummaryQuery(),
            'title': f"All Active Clients Summary Report {month} {year} MTD",
            'title_font_size': 12,
            'table_width': 9,
            'table_font_size': 11,
            'title_space': 2.23
        },
        'Basic Stack Not Upgraded To Special Stack Summary Report(Lead)': {
            'query': summary_query.leadBasicStackUpgradeQuery(),
            'title':
            f"Basic Stack Not Upgraded To Special Stack Summary Report (Lead) (Last Six Months)",
            'title_font_size': 10,
            'table_width': 8,
            'table_font_size': 10.5,
            'title_space': 1.85
        },
        'Basic Stack Not Upgraded To Special Stack Summary Report(OCR)': {
            'query': summary_query.ocrBasicStackUpgradeQuery(),
            'title':
            f"Basic Stack Not Upgraded To Special Stack Summary Report (OCR) (Last Six Months)",
            'title_font_size': 11,
            'table_width': 8,
            'table_font_size': 10.5,
            'title_space': 1.95
        },
        'COM Call Summary Report': {
            'query': summary_query.comCallSummaryReport(),
            'title': f"COM Call Summary Report {month} {year} MTD",
            'title_font_size': 11,
            'table_width': 8,
            'table_font_size': 10.5,
            'title_space': 0.95
        },
        'Half Time Feedback Summary Report': {
            'query': summary_query.halfTimeFeedbackSummaryQuery(),
            'title': f"Half Time Feedback Summary Report {month} {year} MTD",
            'title_font_size': 11,
            'table_width': 8,
            'table_font_size': 10.5,
            'title_space': 1.53
        },
        'Final Feedback Summary Report': {
            'query': summary_query.finalFeedbackSummaryQuery(),
            'title': f"Final Feedback Summary Report {month} {year} MTD",
            'title_font_size': 11,
            'table_width': 8,
            'table_font_size': 10.5,
            'title_space': 0.85
        }
    }

    temp_report_config = {
        'Gut Detox Assigned Leads Summary Report': {
            'query': summary_query.gutDetoxAssignedLeadSummary(),
            'title':
            f"Gut Reset Assigned Leads Summary Report {month} {year} MTD",
            'title_font_size': 11,
            'table_width': 8,
            'table_font_size': 12,
            'title_space': 1.75
        }
    }

    temp_report_config2 = {
        'EOD Khyati Mam New Lead Report': {
            'query': summary_query.newLeadWithoutRefIndianNRI(),
            'title':
            f"NEW LEADS (WITHOUT REF) (INDIAN & NRI) SUMMARY REPORT {month.upper()} {year}",
            'title_font_size': 11,
            'table_width': 8,
            'table_font_size': 12,
            'title_space': 1.75
        },
        'EOD Khyati Mam Old Lead Report': {
            'query': summary_query.oldLeadWithoutRefIndianNRI(),
            'title':
            f"OLD LEADS (WITHOUT REF) (INDIAN & NRI) SUMMARY REPORT {month.upper()} {year}",
            'title_font_size': 11,
            'table_width': 8,
            'table_font_size': 12,
            'title_space': 1.75
        }
    }

    temp_report_config3 = {
        'Social Media Assigned Leads Summary Report': {
            'query': summary_query.socialMediaAssignedLeadsSummary(),
            'title':
            f'''SOCIAL MEDIA ASSIGNED LEADS SUMMARY REPORT ({datetime.today().strftime("%d-%m-%Y")})''',
            'title_font_size': 11,
            'table_width': 8,
            'table_font_size': 12,
            'title_space': 1.75
        }
    }

    # Generate the report based on the selected_report
    if st.button("Generate Report/Sheet"):
        if selected_report in report_config:
            report_settings = report_config[selected_report]
            query = report_settings['query']
            title = report_settings['title']
            title_font_size = report_settings['title_font_size']
            table_width = report_settings['table_width']
            table_font_size = report_settings['table_font_size']
            title_space = report_settings['title_space']

            # Create summaryTable object and execute the Generator method in parallel
            summary_table = summaryTable(query, title, title_font_size,
                                         table_width, table_font_size,
                                         title_space)
            summary_table.Generator()

        elif selected_report in temp_report_config:
            report_settings = temp_report_config[selected_report]
            query = report_settings['query']
            title = report_settings['title']
            title_font_size = report_settings['title_font_size']
            table_width = report_settings['table_width']
            table_font_size = report_settings['table_font_size']
            title_space = report_settings['title_space']

            # Create summaryTable object and execute the Generator method in parallel
            summary_table = summaryTable(query, title, title_font_size,
                                         table_width, table_font_size,
                                         title_space)
            summary_table.generatorForGut()

        elif selected_report in temp_report_config2:
            report_settings = temp_report_config2[selected_report]
            query = report_settings['query']
            title = report_settings['title']
            title_font_size = report_settings['title_font_size']
            table_width = report_settings['table_width']
            table_font_size = report_settings['table_font_size']
            title_space = report_settings['title_space']

            # Create summaryTable object and execute the Generator method in parallel
            summary_table = summaryTable(query, title, title_font_size,
                                         table_width, table_font_size,
                                         title_space)
            summary_table.leadReportGenerator()

        elif selected_report in temp_report_config3:
            report_settings = temp_report_config3[selected_report]
            query = report_settings['query']
            title = report_settings['title']
            title_font_size = report_settings['title_font_size']
            table_width = report_settings['table_width']
            table_font_size = report_settings['table_font_size']
            title_space = report_settings['title_space']

            # Create summaryTable object and execute the Generator method in parallel
            summary_table = summaryTable(query, title, title_font_size,
                                         table_width, table_font_size,
                                         title_space)
            summary_table.socialMediaAssignedLeadGenerator()

        elif selected_report == "Khyati Ma'ams' SM New Leads Summary Report":
            queries = [
                summary_query.socialMediaNewleadSummary(),
                summary_query.socialMediaNewLeadAssignedToday()
            ]
            socialMediaNewLeadSummaryGenerator(queries)

        elif selected_report == "Khyati Ma'ams' Morning Lead Consultaion Report":
            queries = [
                summary_query.consultationCallBookedYesterdayByLeads(),
                summary_query.yesterdayAllHS(),
                summary_query.previousDayUnassignedHS(),
                summary_query.previousDayUnassignedRegistration()
            ]
            morningLeadReportGenerator(queries)

        elif selected_report == "Counsellor Sales Analysis Report":
            queries = [
                summary_query.counsellorSmLeadSummaryQuery(),
                summary_query.leadWithoutRefSummaryQuery()
            ]
            counsellorSalesAnalysis(queries)

elif option == 'Data Sheet':
    selected_report = st.selectbox("Select A Data Sheet Needed", sheet)
    first_day_of_current_month = datetime.today().replace(day=1).date()
    with st.container():
        # Create two columns
        col1, col2 = st.columns(2)

        # In the first column, add a date input box
        with col1:
            start_date = st.date_input("Start Date",
                                       first_day_of_current_month)

        # In the second column, add another date input box
        with col2:
            end_date = st.date_input("End Date", datetime.today())
    date_object = datetime.strptime(str(start_date), "%Y-%m-%d")

    month = date_object.strftime('%b')
    year = date_object.year

    # Create dataSheetQueries object once, reuse it
    data_query = dataSheetQueries(start_date, end_date)

    # Define a dictionary for all report types
    report_config = {
        'Tailend Clients Un-Pitched Data Sheet': {
            'query':
            data_query.tailendDataSheetQuery(),
            'title':
            f"Mentor Wise Tailend Client Un-Pitched {month} {year} MTD Data Sheet"
        },
        'Mentor Un-Paid All Rate Shared Data Sheet': {
            'query':
            data_query.allRateSharedUnpaidSheet(),
            'title':
            f"Mentor Wise All(Active/OCR/Lead) Un-Paid Rate Shared {month} {year} MTD Data Sheet"
        },
        "Mentor All Active (No Adv Purchase) Un-Pitched Data Sheet": {
            'query':
            data_query.mentorsNoAdvPurchaseDataSheet(),
            'title':
            f"Mentor Wise All Active Clients(No Adv. Purchase) Un-Pitched {month} {year} MTD Data Sheet"
        },
        'WMR Sent Diet Not Receieved Over Due 24 hrs. Sheet': {
            'query':
            data_query.wmrReceivedDietNotSendOD(),
            'title':
            f"Mentor Wise WMR Received but Diet Not Sent - Over Due (Last 48 Hours) Data Sheet"
        },
        'NAF Sent Diet Not Receieved Over Due 24 hrs. Sheet': {
            'query':
            data_query.nafReceivedDietNotSendOD(),
            'title':
            f"Mentor Wise NAF Received but Diet Not Sent - Over Due (Last 48 Hours) Data Sheet"
        },
        'All Nutritionist Assigned Un-Paid Leads Data Sheet': {
            'query':
            data_query.allAssignedUnPaidLeadsDataSheetQuery(),
            'title':
            f"All Nutritionist Assigned Un-Paid Leads {month} {year} MTD Data Sheet"
        },
        "All Nutritionist Assigned Un-Paid Indian Leads Data Sheet": {
            'query':
            data_query.mentorAssignedUnPaidIndianLeadsDataSheetQuery(),
            'title':
            f"All Nutritionist Assigned Un-Paid Indian Leads {month} {year} MTD Data Sheet"
        },
        'All Nutritionist Assigned Un-Paid NRI Leads Data Sheet': {
            'query':
            data_query.mentorAssignedUnPaidNRILeadsDataSheetQuery(),
            'title':
            f"All Nutritionist Assigned Un-Paid NRI Leads {month} {year} MTD Data Sheet"
        },
        'All Active Client Page Visits Data Sheet': {
            'query':
            data_query.activeClientAllPageVisitDataSheetQuery(),
            'title':
            f"Mentor Wise All Active Clients Program Page Visits (Un-Paid) {month} {year} MTD Data Sheet"
        },
        'All Active Client Checkout Page Visits Data Sheet': {
            'query':
            data_query.activeClientCheckoutPageVisitDataSheetQuery(),
            'title':
            f"Mentor Wise All Active Clients Checkout Page Visits (Un-Paid) {month} {year} MTD Data Sheet"
        },
        'OCR Client Page Visits Data Sheet': {
            'query':
            data_query.ocrClientsAllPageVisitDataSheetQuery(),
            'title':
            f"Mentor Wise OCR Clients Program Page Visits (Un-Paid) {month} {year} MTD Data Sheet"
        },
        'OCR Client Checkout Page Visits Data Sheet': {
            'query':
            data_query.ocrClientsCheckoutPageVisitDataSheetQuery(),
            'title':
            f"Mentor Wise OCR Clients Checkout Page Visits (Un-Paid) {month} {year} MTD Data Sheet"
        },
        'Induction Call Not Done Data Sheet': {
            'query': data_query.inductionCallNotDoneDataSheet(),
            'title': f"Induction Call Not Done {month} {year} MTD Data Sheet"
        },
        "Mentor All Active (No Adv Purchase) Above 70 kg Un-Pitched Data Sheet":
        {
            'query':
            data_query.mentorNoAdvPurchaseAbove70kgExceptDormantDataSheet(),
            'title':
            f"Mentor Wise All Active Clients(No Adv. Purchase) (Above 70 Kg) Un-Pitched {month} {year} MTD Data Sheet"
        },
        "Basic Stack Not Upgraded to Special stack (Lead) Data Sheet": {
            'query':
            data_query.leadBasicStackNotUpgradedDataSheet(),
            'title':
            f"Basic Stack Upgraded to Special Stack (Lead) (Last Six Month) Data Sheet"
        },
        "Basic Stack Not Upgraded to Speical Stack (OCR) Data Sheet": {
            'query':
            data_query.ocrBasicStackNotUpgradedDataSheet(),
            'title':
            f"Basic Stack Upgraded to Special Stack (OCR) (Last Six Month) Data Sheet"
        },
        "COM Call Not Done Data Sheet": {
            'query': data_query.comCallNotDoneDataSheet(),
            'title':
            f"Mentor Wise COM Call Not Done {month} {year} MTD Data Sheet"
        },
        "Good Weight Loss Active Clients Data Sheet": {
            'query':
            data_query.goodWeightLossClient(),
            'title':
            f"Good Weight Loss Active Clients {month} {year} MTD Data Sheet"
        },
        "Half Time Feedback Data Sheet": {
            'query': data_query.halfTimeFeedbackDataSheet(),
            'title':
            f"Mentor Wise Half Time Feedback {month} {year} Data Sheet"
        }
    }

    # Generate report based on user selection
    if st.button('Generate Report/Sheet'):
        if selected_report in report_config:
            query = report_config[selected_report]['query']
            title = report_config[selected_report]['title']

            # Create dataSheets object once for reusability
            data_sheet = dataSheets(query, title)

            # Process mentor-wise sheet division in parallel
            with ThreadPoolExecutor() as executor:
                sheet_future = executor.submit(
                    data_sheet.mentorwiseDivideSheets)
                sheet = sheet_future.result()  # Get the result of the future

            st.markdown(f"Required Sheet Has Been Cooked !! :<br>{sheet}",
                        unsafe_allow_html=True)

elif option == 'Remove Paid Data':
    first_day_of_current_month = datetime.today().replace(day=1).date()
    with st.container():
        # Create two columns
        col1, col2 = st.columns(2)

        # In the first column, add a date input box
        with col1:
            start_date = st.date_input("Start Date",
                                       first_day_of_current_month)

        # In the second column, add another date input box
        with col2:
            end_date = st.date_input("End Date", datetime.today())
    sheet = str(st.text_input("Enter the Sheet Link"))
    if st.button('Update Sheet'):
        removePaidData(sheet, start_date, end_date).removePaidUsingEmail()
        removePaidData(sheet, start_date, end_date).removePaidUsingPhone()

elif option == "Update Yesterdays' Entry":
    first_day_of_current_month = datetime.today().replace(day=1).date()

    sheet_list = [
        'All Mentors All(Active/OCR/Lead) Rate Shared Sheet',
        'All Nutritionist Assigned Un-Paid Leads Data Sheet'
    ]
    option = st.selectbox("Select The Name of the Sheet You Wish to Update",
                          sheet_list)
    with st.container():
        # Create two columns
        col1, col2 = st.columns(2)

        # In the first column, add a date input box
        with col1:
            start_date = st.date_input("Start Date",
                                       first_day_of_current_month)

        # In the second column, add another date input box
        with col2:
            end_date = st.date_input("End Date", datetime.today())
    sheet = str(st.text_input("Enter the Sheet Link"))
    if st.button('Update Sheet'):
        if option == 'All Mentors All(Active/OCR/Lead) Rate Shared Sheet':
            query = dataSheetQueries(start_date,
                                     end_date).allRateSharedUnpaidSheet()
            recordUpdate(sheet, query).updateRecentRecord()
        if option == 'All Nutritionist Assigned Un-Paid Leads Data Sheet':
            query = dataSheetQueries(
                start_date, end_date).allAssignedUnPaidLeadsDataSheetQuery()
            recordUpdate(sheet, query).updateRecentRecord()

elif option == "Audit Report":
    start_row = 2
    start_col = 5

    titles = [
        'CLIENT SUMMARY', 'NOT STARTED CLIENTS DETAILS',
        'NOT STARTED OD CLIENTS DETAILS', 'DORMANT CLIENTS DETAILS',
        'ONHOLD CLIENTS DETAILS', 'ONHOLD OD CLIENTS DETAILS'
    ]

    spreadsheet_id = str(st.text_input("Enter the spreadsheet Id"))
    options = [name for name in mentors.keys()]
    sheet_name = st.selectbox('Choose an option:', options)
    user_id = mentors.get(sheet_name)
    queries = [
        mentorAuditQueries(user_id).statusSummary(),
        mentorAuditQueries(user_id).notStartedClientQuery(),
        mentorAuditQueries(user_id).notStartedODclientQuery(),
        mentorAuditQueries(user_id).dormantclientQuery(),
        mentorAuditQueries(user_id).onholdClientQuery(),
        mentorAuditQueries(user_id).onholdODclientQuery()
    ]

    if st.button('Update Sheet'):
        mentorAudit(queries).update_sheet_with_data(spreadsheet_id, sheet_name,
                                                    titles, start_row,
                                                    start_col)

elif option == "Sheet Formatting":
    sheetlink = str(st.text_input("Enter The Sheet Link"))
    splitcol = str(
        st.text_input(
            "Enter The Column Name Along Which Sheet Needs To Be Seperated"))
    if st.button("Format Sheet"):
        obj = dataSheetFormatting(sheetlink, splitcol)
        obj.mentorwiseDivideSheets()

elif option == "Analysis Report":
    selected_report = st.selectbox("Select A Analysis Report Required",
                                   analysis_report_list)
    first_day_of_current_month = datetime.today().replace(day=1).date()
    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            start_date = st.date_input("Start Date",
                                       first_day_of_current_month)

        with col2:
            end_date = st.date_input("End Date", datetime.today())
    date_object = datetime.strptime(str(start_date), "%Y-%m-%d")

    month = date_object.strftime('%b')
    year = date_object.year

    analysis_query = analysisReportQuery(start_date, end_date)

    analysis_report_config = {
        'Counsellor Performance Analysis Report': {
            'queries': [
                analysis_query.counsellorSalesSummaryQuery(),
                analysis_query.cousellorLeadAnalysisDataQuery(),
                analysis_query.counsellorSmLeadSummaryQuery()
            ]
        }
    }

    if st.button("Show Report"):
        if selected_report in analysis_report_config:
            queries = analysis_report_config[selected_report]['queries']
            salesAnalysisReport(queries).counsellorPerformanceReportGenerator()
