import pandas as pd
import sqlalchemy as sql
from sqlalchemy.orm import sessionmaker
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import pandas as pd
import numpy as np
from decimal import Decimal
import requests
from googleapiclient.errors import HttpError
# Removed pywhatkit import as it's not used
import matplotlib.pyplot as plt
import io
import tempfile
import os
from queries import dataSheetQueries, paidDataQueries
import re
import warnings
import datetime
import streamlit as st
import requests
import base64
import streamlit.components.v1 as components
from datetime import date
from gspread_dataframe import set_with_dataframe

warnings.filterwarnings('ignore')

engine = sql.create_engine(
    'mysql+pymysql://balancei_analyst:$PaMn-,da+S&@balancenutrition.in:3306/balancei_nutweb',
    pool_pre_ping=True)
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
import json
import os

try:
    service_account_info = json.loads(os.environ['GOOGLE_SERVICE_ACCOUNT'])
    creds = Credentials.from_service_account_info(service_account_info,
                                                  scopes=scope)
    client = gspread.authorize(creds)
    drive_service = build('drive', 'v3', credentials=creds)
    service = build('sheets', 'v4', credentials=creds)
except Exception as e:
    st.error(
        "Failed to initialize Google credentials. Please check your service account configuration."
    )
    raise e


class summaryTable:

    def __init__(self, query, title, title_font_size, table_width,
                 table_font_size, title_space):
        self.query = query
        self.title = title
        self.table_width = table_width
        self.title_font_size = title_font_size
        self.table_font_size = table_font_size
        self.title_space = title_space

    def Generator(self):
        with engine.connect() as connection:
            result = connection.execute(sql.text(self.query))
            data = pd.DataFrame(result.fetchall(), columns=result.keys())

        # Summing data for total row, excluding 'Mentor' column
        cols = [col for col in data.columns if 'Mentor' not in col]
        total = pd.DataFrame({
            'Mentor': ['TOTAL'],
            **{
                col: [data[col].sum()]
                for col in cols
            }
        })
        data = pd.concat([data, total], ignore_index=True)

        # Set table styles
        data.style.set_table_styles([{
            'selector': 'td',
            'props': [('text-align', 'center')]
        }])

        # Colors for rows
        colors = ['#A9A9A9'] + ['#F7FCF9'] * (len(data) - 1) + ['#34EB77']

        # Create figure and axis for table
        fig, ax = plt.subplots(figsize=(self.table_width, 2.5))
        ax.axis('tight')
        ax.axis('off')

        # Generate table with colors
        table = ax.table(cellText=data.values,
                         colLabels=data.columns,
                         cellLoc='center',
                         loc='center',
                         cellColours=[[colors[i + 1]] * len(data.columns)
                                      for i in range(len(data))])

        # Dynamically calculate the spacing for title
        table_extent = table.get_window_extent(
            ax.get_figure().canvas.get_renderer())
        table_bottom = table_extent.y0 / ax.get_figure().bbox.height
        spacing_above_table = self.title_space

        ax.text(0.5,
                table_bottom + spacing_above_table,
                self.title,
                fontfamily="sans-serif",
                fontsize=self.title_font_size,
                fontweight='bold',
                ha='center',
                transform=ax.transAxes)

        # Set header style
        for j in range(len(data.columns)):
            cell = table[(0, j)]
            cell.set_facecolor('#A9A9A9')
            cell.set_text_props(weight='bold')

        # Adjust the cell size and font style for the entire table
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1, 1.5)

        # Make the table font consistent and bold for totals
        for key, cell in table.get_celld().items():
            cell.set_text_props(fontfamily='sans-serif',
                                fontsize=self.table_font_size)
            row, col = key
            if row == len(data):  # Total row
                cell.set_text_props(weight='bold')
            if col == 0:  # First column (Mentor names)
                cell.set_text_props(weight='bold')

        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format='png', bbox_inches='tight', dpi=300)
        plt.close(fig)
        img_buffer.seek(0)
        base64_image = base64.b64encode(img_buffer.getvalue()).decode()
        st.image(img_buffer,
                 caption="Right-click to copy the image",
                 use_container_width=True)

        # Provide a download button for the PNG image
        st.download_button(label="Download table as PNG",
                           data=img_buffer,
                           file_name="table.png",
                           mime="image/png")

    def generatorForGut(self):
        with engine.connect() as connection:
            result = connection.execute(sql.text(self.query))
            data = pd.DataFrame(result.fetchall(), columns=result.keys())

        cols = [col for col in data.columns if 'Name' not in col]
        total = pd.DataFrame({
            'Name': ['TOTAL'],
            **{
                col: [data[col].sum()]
                for col in cols
            }
        })
        data = pd.concat([data, total], ignore_index=True)

        # Set table styles
        data.style.set_table_styles([{
            'selector': 'td',
            'props': [('text-align', 'center')]
        }])

        # Colors for rows
        colors = ['#A9A9A9'] + ['#F7FCF9'] * (len(data) - 1) + ['#34EB77']

        # Create figure and axis for table
        fig, ax = plt.subplots(figsize=(self.table_width, 2.5))
        ax.axis('tight')
        ax.axis('off')

        # Generate table with colors
        table = ax.table(cellText=data.values,
                         colLabels=data.columns,
                         cellLoc='center',
                         loc='center',
                         cellColours=[[colors[i + 1]] * len(data.columns)
                                      for i in range(len(data))])

        # Dynamically calculate the spacing for title
        table_extent = table.get_window_extent(
            ax.get_figure().canvas.get_renderer())
        table_bottom = table_extent.y0 / ax.get_figure().bbox.height
        spacing_above_table = self.title_space

        ax.text(0.5,
                table_bottom + spacing_above_table,
                self.title,
                fontfamily="sans-serif",
                fontsize=self.title_font_size,
                fontweight='bold',
                ha='center',
                transform=ax.transAxes)

        # Set header style
        for j in range(len(data.columns)):
            cell = table[(0, j)]
            cell.set_facecolor('#A9A9A9')
            cell.set_text_props(weight='bold')

        # Adjust the cell size and font style for the entire table
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1, 1.5)

        # Make the table font consistent and bold for totals
        for key, cell in table.get_celld().items():
            cell.set_text_props(fontfamily='sans-serif',
                                fontsize=self.table_font_size)
            row, col = key
            if row == len(data):  # Total row
                cell.set_text_props(weight='bold')
            if col == 0:  # First column (Mentor names)
                cell.set_text_props(weight='bold')

        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format='png', bbox_inches='tight', dpi=300)
        plt.close(fig)
        img_buffer.seek(0)
        base64_image = base64.b64encode(img_buffer.getvalue()).decode()
        st.image(img_buffer,
                 caption="Right-click to copy the image",
                 use_container_width=True)

        # Provide a download button for the PNG image
        st.download_button(label="Download table as PNG",
                           data=img_buffer,
                           file_name="table.png",
                           mime="image/png")

    def leadReportGenerator(self):
        with engine.connect() as connection:
            result = connection.execute(sql.text(self.query))
            df = pd.DataFrame(result.fetchall(), columns=result.keys())

        cols = [col for col in df.columns if 'Name' not in col]
        total = pd.DataFrame({
            'Name': ['TOTAL'],
            **{
                col: [df[col].sum()]
                for col in cols
            }
        })
        df = pd.concat([df, total], ignore_index=True)

        html_table = f"""
        <html>
        <body>
            <table style="width: 70%; 
            border-collapse: collapse; 
            font-family: 'sans-serif'; 
            font-size: 15px;">
                <tr>
                    <th colspan="10" style="background-color: #d6f5d6; font-size: 16px; font-weight: bold; text-align: center; padding: 10px; border: 1px solid black;">
                        {self.title}
                    </th>
                </tr>
                <tr>
                    <th rowspan="2" style="background-color: #d89384; font-weight: bold; text-align: center; padding: 8px; border: 1px solid black;">Name</th>
                    <th colspan="3" style="background-color: #b3e0ff; font-weight: bold; text-align: center; padding: 8px; border: 1px solid black;">ASSIGNED LEADS</th>
                    <th colspan="3" style="background-color: #b3e0ff; font-weight: bold; text-align: center; padding: 8px; border: 1px solid black;">PAID LEADS</th>
                    <th colspan="3" style="background-color: #b3e0ff; font-weight: bold; text-align: center; padding: 8px; border: 1px solid black;">UN-PAID LEADS</th>
                </tr>
                <tr>
                    <th style="background-color: #d89384; color: black; text-align: center; padding: 10px; border: 1px solid black;">Total</th>
                    <th style="background-color: #d89384; color: black; text-align: center; padding: 10px; border: 1px solid black;">Indian</th>
                    <th style="background-color: #d89384; color: black; text-align: center; padding: 10px; border: 1px solid black;">NRI</th>
                    <th style="background-color: #d89384; color: black; text-align: center; padding: 10px; border: 1px solid black;">Total</th>
                    <th style="background-color: #d89384; color: black; text-align: center; padding: 10px; border: 1px solid black;">Indian</th>
                    <th style="background-color: #d89384; color: black; text-align: center; padding: 10px; border: 1px solid black;">NRI</th>
                    <th style="background-color: #d89384; color: black; text-align: center; padding: 10px; border: 1px solid black;">Total</th>
                    <th style="background-color: #d89384; color: black; text-align: center; padding: 10px; border: 1px solid black;">Indian</th>
                    <th style="background-color: #d89384; color: black; text-align: center; padding: 10px; border: 1px solid black;">NRI</th>
                </tr>
        """

        # Add rows from `data` DataFrame
        for index, row in df.iterrows():
            row_style = "background-color: #caf7f4;" if row[
                "Name"] != "TOTAL" else "background-color: #f9e5b5; font-weight: bold;"
            html_table += f"""
                <tr style="{row_style}">
                    <td style="border: 1px solid black; text-align: center;">{row["Name"]}</td>
                    <td style="color: red; border: 1px solid black; text-align: center;">{int(row["Total Assigned Leads"])}</td>
                    <td style="border: 1px solid black; text-align: center;">{int(row["Assigned Indian Leads"])}</td>
                    <td style="border: 1px solid black; text-align: center;">{int(row["Assigned NRI Leads"])}</td>
                    <td style="color: red; border: 1px solid black; text-align: center;">{int(row["Total Paid Leads"])}</td>
                    <td style="border: 1px solid black; text-align: center;">{int(row["Total Paid Indians"])}</td>
                    <td style="border: 1px solid black; text-align: center;">{int(row["Total Paid NRI"])}</td>
                    <td style="color: red; border: 1px solid black; text-align: center;">{int(row["Total Un-Paid Leads"])}</td>
                    <td style="border: 1px solid black; text-align: center;">{int(row["Total Un-Paid Indians"])}</td>
                    <td style="border: 1px solid black; text-align: center;">{int(row["Total Un-Paid NRI"])}</td>
                </tr>
            """

        # Close table and HTML tags
        html_table += f"""
            </table>
        </body>
        </html>
        """

        components.html(html_table, height=1000, scrolling=True)

    def socialMediaAssignedLeadGenerator(self):
        with engine.connect() as connection:
            result = connection.execute(sql.text(self.query))
            df = pd.DataFrame(result.fetchall(), columns=result.keys())

        cols = [col for col in df.columns if 'Name' not in col]
        total = pd.DataFrame({
            'Name': ['TOTAL'],
            **{
                col: [df[col].sum()]
                for col in cols
            }
        })
        df = pd.concat([df, total], ignore_index=True)

        html_table = f"""
        <html>
        <body>
            <table style="width: 70%;             
            border-collapse: collapse; 
            font-family: 'sans-serif'; 
            font-size: 15px;">
                <tr>
                    <th colspan="10" style="background-color: #d6f5d6; font-size: 16px; font-weight: bold; text-align: center; padding: 10px; border: 1px solid black;">
                        {self.title}
                    </th>
                </tr>
                <tr>
                    <th rowspan="2" style="background-color: #d89384; font-weight: bold; text-align: center; padding: 8px; border: 1px solid black;">Name</th>
                    <th colspan="3" style="background-color: #b3e0ff; font-weight: bold; text-align: center; padding: 8px; border: 1px solid black;">NEW LEADS</th>
                    <th colspan="3" style="background-color: #b3e0ff; font-weight: bold; text-align: center; padding: 8px; border: 1px solid black;">OLD LEADS</th>                        
                </tr>
                <tr>
                    <th style="background-color: #d89384; color: black; text-align: center; padding: 10px; border: 1px solid black;">Total</th>
                    <th style="background-color: #d89384; color: black; text-align: center; padding: 10px; border: 1px solid black;">SMO</th>
                    <th style="background-color: #d89384; color: black; text-align: center; padding: 10px; border: 1px solid black;">SME</th>
                    <th style="background-color: #d89384; color: black; text-align: center; padding: 10px; border: 1px solid black;">Total</th>
                    <th style="background-color: #d89384; color: black; text-align: center; padding: 10px; border: 1px solid black;">SMO</th>
                    <th style="background-color: #d89384; color: black; text-align: center; padding: 10px; border: 1px solid black;">SME</th>                        
                </tr>
        """

        # Add rows from `data` DataFrame
        for index, row in df.iterrows():
            row_style = "background-color: #caf7f4;" if row[
                "Name"] != "TOTAL" else "background-color: #f9e5b5; font-weight: bold;"
            html_table += f"""
                <tr style="{row_style}">
                    <td style="border: 1px solid black; text-align: center;">{row["Name"]}</td>
                    <td style="color: red; border: 1px solid black; text-align: center;">{int(row["totalNew"])}</td>
                    <td style="border: 1px solid black; text-align: center;">{int(row["newSMO"])}</td>
                    <td style="border: 1px solid black; text-align: center;">{int(row["newSME"])}</td>
                    <td style="color: red; border: 1px solid black; text-align: center;">{int(row["totalOl"])}</td>
                    <td style="border: 1px solid black; text-align: center;">{int(row["olSMO"])}</td>
                    <td style="border: 1px solid black; text-align: center;">{int(row["olSME"])}</td>                        
                </tr>
            """

        # Close table and HTML tags
        html_table += f"""
            </table>
        </body>
        </html>
        """

        components.html(html_table, height=1000)


def socialMediaNewLeadSummaryGenerator(queries):
    summaryQuery, todayAssignedQuery ,hsNotAssignedTillNow = queries
    with engine.connect() as connection:
        summaryQueryResult = connection.execute(sql.text(summaryQuery))
        todayAssignedResult = connection.execute(sql.text(todayAssignedQuery))
        hsNotAssignedTillNowResult = connection.execute(sql.text(hsNotAssignedTillNow))

        summaryData = pd.DataFrame(summaryQueryResult.fetchall(),
                                   columns=summaryQueryResult.keys())
        hsNotAssignedTillNowData = pd.DataFrame(hsNotAssignedTillNowResult.fetchall(),
               columns=hsNotAssignedTillNowResult.keys())
        todayAssignedData = pd.DataFrame(todayAssignedResult.fetchall(),
                                         columns=todayAssignedResult.keys())
    summary_format = [
        f"\*TOTAL: {summaryData['Assigned'].sum()} Lead(s) - ({summaryData['Sales'].sum()} Sale(s))\*"
    ]
    summary_format.extend([
        f"{row['Name']}: {row['Assigned']} Lead(s) - ({row['Sales']} Sale(s))"
        for i, row in summaryData.iterrows()
    ])
    today_assigned_format = [f"\*TOTAL: {todayAssignedData['Counts'].sum()}\*"]
    today_assigned_format.extend(f"{row['Name']} - {row['Counts']}"
                                 for i, row in todayAssignedData.iterrows())
    # Combine everything into one markdown string
    report = f"""
        \*Total Social Media New leads MTD - Sales unit (until {date.today()})\*  
        {'<br>'.join(summary_format)}  

        \-------------------------------------------------------------- 

        \*Total SM New leads Alloted Today ({date.today()})\*  
        {'<br>'.join(today_assigned_format)}  

         \*HS UN-ASSIGNED - {hsNotAssignedTillNowData['HS_UN_ASSIGNED'].iloc[0]}\* 
        
        """

    # Render markdown with no spacing
    st.markdown(report, unsafe_allow_html=True)


def morningLeadReportGenerator(queries):
    callBookedYesterdayQuery, yesterdayHSQuery, yesterdayUnassignedHSQuery, yesterdayUnassignedRegQuery = queries
    with engine.connect() as connection:
        callBookedYesterday = connection.execute(
            sql.text(callBookedYesterdayQuery)).fetchall()[0][0]
        yesterdayHS = connection.execute(
            sql.text(yesterdayHSQuery)).fetchall()[0][0]
        yesterdayUnassignedHS = connection.execute(
            sql.text(yesterdayUnassignedHSQuery)).fetchall()[0][0]
        yesterdayUnassignedReg = connection.execute(
            sql.text(yesterdayUnassignedRegQuery)).fetchall()[0][0]

    day_string = "Saturday & Sunday" if date.today().weekday(
    ) == 0 else "Yesterday"
    on_flag = " On " if date.today().weekday() == 0 else ""
    report = f'''
    Good Morning,<br>
    Below are stats. for {day_string}.

    Consultation Calls Booked By Leads On Website - {callBookedYesterday}<br>
    Total HS Leads - {yesterdayHS}<br>
    Total Unassigned HS(Stage 3 & 4) - {yesterdayUnassignedHS}  
    Total Unassigned Registration - {yesterdayUnassignedReg}
    '''
    st.markdown(report, unsafe_allow_html=True)


def counsellorSalesAnalysis(queries):
    paidSummaryQuery, leadSummaryQuery = queries
    with engine.connect() as connection:
        paidSummaryResult = connection.execute(sql.text(paidSummaryQuery))
        leadSummaryResult = connection.execute(sql.text(leadSummaryQuery))
        paidData = pd.DataFrame(paidSummaryResult.fetchall(),
                                columns=paidSummaryResult.keys())
        leadData = pd.DataFrame(leadSummaryResult.fetchall(),
                                columns=leadSummaryResult.keys())

    leadFunnel = pd.pivot_table(
        data=leadData[leadData['lead_category'] == 'Age 35'],
        index=['assign_to'],
        values=['paid_status', 'cons_status'],
        aggfunc={
            'paid_status': 'count',
            'cons_status': 'sum'
        })
    leadFunnel = leadFunnel.reset_index()
    leadFunnelData = pd.merge(leadFunnel, paidData, on='NAME', how='inner')


class dataSheets:

    def __init__(self, query, title):
        self.query = query
        self.title = title

    def allignSheets(spreadsheet):
        # Fetch all sheet IDs and apply formatting
        requests = []
        for sheet in spreadsheet.worksheets():
            sheet_id = sheet.id
            requests.append({
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "horizontalAlignment": "CENTER",
                            "verticalAlignment": "MIDDLE",
                            "wrapStrategy": "WRAP"
                        }
                    },
                    "fields":
                    "userEnteredFormat(horizontalAlignment, verticalAlignment, wrapStrategy)"
                }
            })

        # Batch update request to apply formatting to all sheets
        body = {"requests": requests}
        spreadsheet.batch_update(body)

    def mentorwiseDivideSheets(self):
        with engine.connect() as connection:
            result = connection.execute(sql.text(self.query))
            data = pd.DataFrame(result.fetchall(), columns=result.keys())
        # Convert any Decimal types to float or string
        data = data.applymap(lambda x: float(x)
                             if isinstance(x, Decimal) else x)
        data = data.applymap(lambda x: x.isoformat()
                             if isinstance(x, datetime.date) else x)

        # Handle NaN and infinite values
        data.replace([np.inf, -np.inf], np.nan,
                     inplace=True)  # Replace infinite values with NaN
        data.fillna("", inplace=True
                    )  # Replace NaN with 0 (or use any other value you prefer)

        # Convert DataFrame to list of lists
        data_list = [data.columns.values.tolist()] + data.values.tolist()

        # Create a new Google Sheet and share it
        new_sheet = client.create(self.title)

        # Access the first worksheet
        worksheet = new_sheet.get_worksheet(0)

        # Update the worksheet with data
        worksheet.update(values=data_list,
                         range_name='A1')  # Update starting from cell A1
        new_sheet.share('vikram.gupta@balancenutrition.in',
                        perm_type='user',
                        role='writer')
        if 'mentor' in data.columns:
            # Group by the 'mentor' column
            grouped_data = data.groupby('mentor')

            # Iterate over each unique mentor and create a new sheet
            for mentor, group in grouped_data:
                group_data_list = [group.columns.values.tolist()
                                   ] + group.values.tolist()

                # Create a new worksheet for each mentor
                mentor_sheet = new_sheet.add_worksheet(title=str(mentor),
                                                       rows="100",
                                                       cols="20")

                # Update the mentor worksheet with the filtered data
                mentor_sheet.update(values=group_data_list, range_name='A1')

        else:
            print("Column 'mentor' not found.")
        dataSheets.allignSheets(new_sheet)
        sheet_url = new_sheet.url

        return new_sheet.url

    def remove_characters(self, sheet):
        sheets = client.open_by_url(str(sheet))
        # Iterate through each sheet in the spreadsheet
        for worksheet in sheets.worksheets():
            # Get the column that contains the "improvement need" data
            improvement_col = worksheet.find(
                "improvement need").col  # Find column index by column name

            # Loop through each cell in the "improvement need" column
            for row in range(2, worksheet.row_count +
                             1):  # Assuming first row contains headers
                cell_value = worksheet.cell(row, improvement_col).value
                if cell_value:
                    # Replace all non-alphanumeric characters using regex
                    cleaned_value = re.sub(r'[^a-zA-Z0-9]', '', cell_value)
                    worksheet.update_cell(row, improvement_col, cleaned_value)


class removePaidData:

    def __init__(self, sheet_link, start_date, end_date):
        self.sheet_link = sheet_link
        self.start_date = start_date
        self.end_date = end_date

    def removePaidUsingPhone(self):
        spreadsheet = client.open_by_url(self.sheet_link)
        # Access the sheet (assuming first sheet)
        worksheet = spreadsheet.get_worksheet(0)

        # Get all records (assuming the first row contains headers)
        records = worksheet.get_all_records()

        # Extract phone into arrays
        phone_column = [record.get('phone', '') for record in records]
        with engine.connect() as connection:
            result = connection.execute(
                sql.text(
                    paidDataQueries(
                        self.start_date,
                        self.end_date).paidDataByPhone(phone_column)))
            data = pd.DataFrame(result.fetchall(), columns=result.keys())
        paidPhoneNumber = data['paid_list'].tolist()
        st.write(
            f"Total Paid Numbers Are {len(paidPhoneNumber)} ({paidPhoneNumber})"
        )

        worksheets = spreadsheet.worksheets()

        if len(paidPhoneNumber) > 0:
            for worksheet in worksheets:
                records = worksheet.get_all_records(
                )  # Get all records from the sheet
                rows_to_delete = []

                # Identify rows with paid phone numbers
                for i, record in enumerate(records):
                    clean_phone = re.sub(r'\D', '', str(record.get(
                        'phone', '')))[-8:]  # Clean and extract last 8 digits
                    if clean_phone in paidPhoneNumber:
                        rows_to_delete.append(
                            i + 2)  # Account for header row in Google Sheets

                # Delete rows from the worksheet in reverse order
                for row in reversed(rows_to_delete):
                    worksheet.delete_rows(row)
            st.write(
                "All Paid Phone Numbers Deleted Successfully from all sheets.")
        else:
            st.write("No Paid Email Ids. So, Enjoy !!")

    def removePaidUsingEmail(self):

        spreadsheet = client.open_by_url(self.sheet_link)
        # Access the sheet (assuming first sheet)
        worksheet = spreadsheet.get_worksheet(0)

        # Get all records (assuming the first row contains headers)
        records = worksheet.get_all_records()

        # Extract email columns into arrays
        email_column = [record.get('email', '') for record in records]

        with engine.connect() as connection:
            result = connection.execute(
                sql.text(
                    paidDataQueries(
                        self.start_date,
                        self.end_date).paidDataByEmail(email_column)))
            data = pd.DataFrame(result.fetchall(), columns=result.keys())
        paidEmail = data['paid_email'].tolist()
        st.write(f"Total Paid Email Ids Are {len(paidEmail)} ({paidEmail})")

        worksheets = spreadsheet.worksheets()
        if len(paidEmail) > 0:
            for worksheet in worksheets:
                records = worksheet.get_all_records()
                rows_to_delete = []

                # Identify rows with paid email addresses
                for i, record in enumerate(records):
                    if record.get('email', '') in paidEmail:
                        rows_to_delete.append(i + 2)

                for row in reversed(rows_to_delete):
                    worksheet.delete_rows(row)

            st.write(
                "All Paid Email Addresses Deleted Successfully from all sheets."
            )
        else:
            st.write("No Paid Email Ids. So, Enjoy !!")


class recordUpdate:

    def __init__(self, sheet_link, query):
        self.sheet_link = sheet_link
        self.query = query

    def alignSheets(self, spreadsheet_id):
        spreadsheet = service.spreadsheets().get(
            spreadsheetId=spreadsheet_id).execute()
        # Create requests for formatting each sheet
        requests = []
        for sheet in spreadsheet['sheets']:
            sheet_id = sheet['properties']['sheetId']
            requests.append({
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "horizontalAlignment": "CENTER",
                            "verticalAlignment": "MIDDLE",
                            "wrapStrategy": "WRAP"
                        }
                    },
                    "fields":
                    "userEnteredFormat(horizontalAlignment, verticalAlignment, wrapStrategy)"
                }
            })

        # Batch update request to apply formatting to all sheets
        if requests:  # Only make the request if there are sheets to format
            body = {"requests": requests}
            service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id,
                                               body=body).execute()
        else:
            st.write("No sheets found to align.")

    def removeDuplicatesFromAllSheets(self, spreadsheet_id):
        try:
            # Fetch all sheet names
            sheets_metadata = service.spreadsheets().get(
                spreadsheetId=spreadsheet_id).execute()
            sheet_names = [
                sheet['properties']['title']
                for sheet in sheets_metadata['sheets']
            ]

            for sheet_name in sheet_names:
                # Get the current data from the sheet
                result = service.spreadsheets().values().get(
                    spreadsheetId=spreadsheet_id,
                    range=
                    f"'{sheet_name}'!A1:Z"  # Assuming a max range to cover columns
                ).execute()

                values = result.get('values', [])

                if not values or len(values) < 2:
                    # If there's no data or only headers, skip processing
                    continue

                headers = values[0]  # Assume the first row is headers
                data = values[1:]  # Exclude headers from data

                # Dynamically find the indices for email and phone
                email_column_index = headers.index(
                    "email") if "email" in headers else None
                phone_column_index = headers.index(
                    "phone") if "phone" in headers else None

                if email_column_index is None or phone_column_index is None:
                    st.write(
                        f"Email and/or phone columns are missing in sheet: {sheet_name}"
                    )
                    continue

                seen = {}
                unique_values = []

                for row in data:
                    # Use the dynamic indices to get email and phonevalues
                    email = row[email_column_index] if len(
                        row) > email_column_index else None
                    phone = row[phone_column_index] if len(
                        row) > phone_column_index else None

                    # Create a composite key for email and phone to check for duplicates
                    key = (email, phone)

                    if key not in seen:
                        seen[key] = True
                        unique_values.append(row)

                # Prepare cleaned data (including headers)
                cleaned_data = [headers] + unique_values

                # Clear the existing data but keep the header row
                service.spreadsheets().values().clear(
                    spreadsheetId=spreadsheet_id,
                    range=f"'{sheet_name}'!A2:Z"  # Clear all rows below header
                ).execute()

                # Write cleaned data back to the sheet
                if unique_values:
                    service.spreadsheets().values().update(
                        spreadsheetId=spreadsheet_id,
                        range=f"'{sheet_name}'!A1",
                        valueInputOption='RAW',
                        body={
                            'values': cleaned_data
                        }).execute()

            # Inform the user that the operation is complete
            st.write("Duplicate Removed.")

        except HttpError as error:
            st.write(f"Failed to remove duplicates from sheets: {error}")

    def create_new_sheet(self, spreadsheet_id, sheet_name):
        try:
            request_body = {
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': sheet_name
                        }
                    }
                }]
            }
            service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id,
                                               body=request_body).execute()
        except HttpError as error:
            st.write(f"Failed to create new sheet {sheet_name}: {error}")

    def get_existing_sheets(self, spreadsheet_id):
        """Retrieve the list of existing sheets (tabs) in the Google Sheets document."""
        try:
            sheets_metadata = service.spreadsheets().get(
                spreadsheetId=spreadsheet_id).execute()
            sheets = sheets_metadata.get('sheets', [])
            sheet_names = [sheet['properties']['title'] for sheet in sheets]
            return sheet_names
        except HttpError as error:
            return []

    def updateRecentRecord(self):
        with engine.connect() as connection:
            result = connection.execute(sql.text(self.query))
            data = pd.DataFrame(result.fetchall(), columns=result.keys())

        # Convert Decimal and datetime.date to appropriate types
        data = data.applymap(lambda x: float(x)
                             if isinstance(x, Decimal) else x)
        data = data.applymap(lambda x: x.isoformat()
                             if isinstance(x, datetime.date) else x)

        # Handle NaN and infinite values
        data.replace([np.inf, -np.inf], np.nan, inplace=True)
        data.fillna("", inplace=True)  # Replace NaN with empty string

        # Extract spreadsheet ID from the URL
        match = re.search(r'/d/([a-zA-Z0-9-_]+)', self.sheet_link)
        if match:
            spreadsheet_id = match.group(1)
        else:
            raise ValueError("Invalid Google Sheets URL")

        existing_sheets = self.get_existing_sheets(spreadsheet_id)

        # Loop through each mentor to append specific data to mentor sheets
        for mentor in data['mentor'].unique():
            mentor_data = data[data['mentor'] == mentor]

            if not mentor_data.empty:
                try:
                    mentor_sheet_name = mentor  # Assuming each sheet name matches the mentor's name

                    # Check if the mentor's sheet exists, and create if it doesn't
                    if mentor_sheet_name not in existing_sheets:
                        print(
                            f"Sheet for {mentor} does not exist. Creating new sheet..."
                        )
                        self.create_new_sheet(spreadsheet_id,
                                              mentor_sheet_name)
                        existing_sheets.append(mentor_sheet_name)

                        # Add headers if it's a new sheet
                        headers = mentor_data.columns.tolist()
                        header_body = {
                            'values': [headers]  # Add headers to the first row
                        }
                        service.spreadsheets().values().append(
                            spreadsheetId=spreadsheet_id,
                            range=f"'{mentor_sheet_name}'!A1",
                            valueInputOption='RAW',
                            body=header_body).execute()

                    # Fetch current data in the mentor's sheet to determine the last row
                    result = service.spreadsheets().values().get(
                        spreadsheetId=spreadsheet_id,
                        range=
                        f"'{mentor_sheet_name}'!A:A"  # Accessing mentor's sheet/tab
                    ).execute()

                    values = result.get('values', [])
                    last_row = len(values) if values else 0

                    # Define the range where data should be appended
                    range_to_update = f"'{mentor_sheet_name}'!A{last_row + 1}"
                    body = {
                        'values':
                        mentor_data.values.tolist()  # Append without header
                    }

                    # Append data to the specific mentor's sheet (tab)
                    service.spreadsheets().values().append(
                        spreadsheetId=spreadsheet_id,
                        range=range_to_update,
                        valueInputOption='RAW',
                        body=body).execute()

                except HttpError as error:
                    st.write(
                        f"Failed to update sheets for mentor {mentor}: {error}"
                    )
            else:
                st.write(f"No data for mentor: {mentor}")

        # Append all data to "Sheet1"
        try:
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range="Sheet1!A:A"  # Fetch current data from Sheet1
            ).execute()

            existing_values = result.get('values', [])
            last_row = len(existing_values) if existing_values else 0

            # Define the range where data should be appended in Sheet1
            range_to_update = f"Sheet1!A{last_row + 1}"
            body = {
                'values':
                data.values.tolist()  # Append all the data without headers
            }

            # Append all new data to "Sheet1"
            service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=range_to_update,
                valueInputOption='RAW',
                body=body).execute()

        except HttpError as error:
            st.write(f"Failed to update Sheet1: {error}")

        # Remove duplicates from all sheets (including Sheet1 and mentor sheets)
        self.removeDuplicatesFromAllSheets(spreadsheet_id)

        self.alignSheets(spreadsheet_id)
        st.write("All Sheets Successfully Updated !!")


class mentorAudit:

    def __init__(self, query):
        self.query = query

    def alignSheets(self, spreadsheet_id):
        # Fetch the spreadsheet object using the spreadsheet ID
        spreadsheet = service.spreadsheets().get(
            spreadsheetId=spreadsheet_id).execute()

        # Create requests for formatting each sheet
        requests = []
        for sheet in spreadsheet['sheets']:
            sheet_id = sheet['properties']['sheetId']
            requests.append({
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "horizontalAlignment": "CENTER",
                            "verticalAlignment": "MIDDLE",
                            "wrapStrategy": "WRAP"
                        }
                    },
                    "fields":
                    "userEnteredFormat(horizontalAlignment, verticalAlignment, wrapStrategy)"
                }
            })

        # Batch update request to apply formatting to all sheets
        if requests:  # Only make the request if there are sheets to format
            body = {"requests": requests}
            service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id,
                                               body=body).execute()
        else:
            st.write("No sheets found to align.")

    # Function to add title at the top of each section and merge cells for title
    def add_table_title(self, service, spreadsheet_id, sheet_id, title,
                        start_row, start_col, end_col):
        requests = [{
            "mergeCells": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": start_row,
                    "endRowIndex": start_row + 1,
                    "startColumnIndex": start_col,
                    "endColumnIndex": end_col
                },
                "mergeType": "MERGE_ALL"
            }
        }, {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": start_row,
                    "endRowIndex": start_row + 1,
                    "startColumnIndex": start_col,
                    "endColumnIndex": end_col
                },
                "cell": {
                    "userEnteredValue": {
                        "stringValue": title
                    },
                    "userEnteredFormat": {
                        "horizontalAlignment": "CENTER",
                        "textFormat": {
                            "fontSize": 12,
                            "bold": True
                        }
                    }
                },
                "fields":
                "userEnteredValue,userEnteredFormat(textFormat,horizontalAlignment)"
            }
        }]

        body = {"requests": requests}
        service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id,
                                           body=body).execute()

    # Function to write column names and data to the sheet
    def write_query_data(self, sheet, columns, data, start_row, start_col,
                         sheet_name, service, spreadsheet_id, sheet_id):
        worksheet = sheet.worksheet(sheet_name)

        # Write the column headers
        col_range = gspread.utils.rowcol_to_a1(
            start_row + 1, start_col + 1)  # +1 since it's 1-based index
        worksheet.update(col_range,
                         [columns])  # Column names as a list of one row

        # Write the data under the column headers
        data_range = gspread.utils.rowcol_to_a1(start_row + 2, start_col +
                                                1)  # Data starts after headers
        worksheet.update(data_range, data)

        # Format the headers to be bold and center-aligned
        header_range = {
            "sheetId": sheet_id,
            "startRowIndex": start_row + 1,
            "endRowIndex": start_row + 2,  # Only the headers (one row)
            "startColumnIndex": start_col,
            "endColumnIndex": start_col + len(columns)
        }

        # Format the data to be center-aligned
        data_range = {
            "sheetId": sheet_id,
            "startRowIndex": start_row + 2,
            "endRowIndex": start_row + 2 + len(data),  # Rows of data
            "startColumnIndex": start_col,
            "endColumnIndex": start_col + len(columns)
        }

        # Formatting requests for both headers and data
        requests = [
            # Bold and center-align column headers
            {
                "repeatCell": {
                    "range": header_range,
                    "cell": {
                        "userEnteredFormat": {
                            "horizontalAlignment": "CENTER"
                        }
                    },
                    "fields":
                    "userEnteredFormat(textFormat,horizontalAlignment)"
                }
            },
            # Center-align data rows
            {
                "repeatCell": {
                    "range": data_range,
                    "cell": {
                        "userEnteredFormat": {
                            "horizontalAlignment":
                            "CENTER"  # Center-align data rows
                        }
                    },
                    "fields": "userEnteredFormat(horizontalAlignment)"
                }
            },
            # Auto-resize columns based on content
            {
                "autoResizeDimensions": {
                    "dimensions": {
                        "sheetId": sheet_id,
                        "dimension": "COLUMNS",
                        "startIndex": start_col,
                        "endIndex": start_col + len(columns)
                    }
                }
            }
        ]

        # Apply formatting requests
        body = {"requests": requests}
        service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id,
                                           body=body).execute()

    # Function to add borders around the table and title
    def add_table_borders(self, service, spreadsheet_id, sheet_id, start_row,
                          end_row, start_col, end_col):
        requests = [{
            "updateBorders": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": start_row,
                    "endRowIndex": end_row,
                    "startColumnIndex": start_col,
                    "endColumnIndex": end_col
                },
                "top": {
                    "style": "SOLID",
                    "width": 1,
                    "color": {
                        "red": 0,
                        "green": 0,
                        "blue": 0
                    }
                },
                "bottom": {
                    "style": "SOLID",
                    "width": 1,
                    "color": {
                        "red": 0,
                        "green": 0,
                        "blue": 0
                    }
                },
                "left": {
                    "style": "SOLID",
                    "width": 1,
                    "color": {
                        "red": 0,
                        "green": 0,
                        "blue": 0
                    }
                },
                "right": {
                    "style": "SOLID",
                    "width": 1,
                    "color": {
                        "red": 0,
                        "green": 0,
                        "blue": 0
                    }
                },
                "innerHorizontal": {
                    "style": "SOLID",
                    "width": 1,
                    "color": {
                        "red": 0,
                        "green": 0,
                        "blue": 0
                    }
                },
                "innerVertical": {
                    "style": "SOLID",
                    "width": 1,
                    "color": {
                        "red": 0,
                        "green": 0,
                        "blue": 0
                    }
                }
            }
        }]

        body = {"requests": requests}
        service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id,
                                           body=body).execute()

    # Main function to update the sheet with data
    def update_sheet_with_data(self, spreadsheet_id, sheet_name, titles,
                               start_row, start_col):
        sheet = client.open_by_key(spreadsheet_id)
        worksheet = sheet.worksheet(sheet_name)
        sheet_id = worksheet.id

        for i, (title, query) in enumerate(zip(titles, self.query)):

            with engine.connect() as connection:
                result = connection.execute(sql.text(query))
                data = pd.DataFrame(result.fetchall(), columns=result.keys())
            if not data.empty:
                # Calculate the number of columns in the data
                end_col = start_col + len(data.columns)

                # Add the title to the Google Sheet
                self.add_table_title(service, spreadsheet_id, sheet_id, title,
                                     start_row, start_col, end_col)

                # Write column names and data to the sheet and format it
                self.write_query_data(sheet, data.columns.tolist(),
                                      data.values.tolist(), start_row + 1,
                                      start_col, sheet_name, service,
                                      spreadsheet_id, sheet_id)

                # Add borders around the title and the data
                end_row = start_row + len(
                    data) + 2  # Account for title and headers
                self.add_table_borders(service, spreadsheet_id, sheet_id,
                                       start_row, end_row, start_col, end_col)

                # Update the start_row for the next title and table
                start_row = end_row + 3  # Add 3 rows of spacing after each table

        self.alignSheets(spreadsheet_id)
        st.write("Sheet Updated Successfully")


class dataSheetFormatting:

    def __init__(self, sheetLink, splitColumn):
        self.sheetLink = sheetLink
        self.splitColumn = splitColumn

    def allignSheets(spreadsheet):
        # Fetch all sheet IDs and apply formatting
        requests = []
        for sheet in spreadsheet.worksheets():
            sheet_id = sheet.id
            requests.append({
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "horizontalAlignment": "CENTER",
                            "verticalAlignment": "MIDDLE",
                            "wrapStrategy": "WRAP"
                        }
                    },
                    "fields":
                    "userEnteredFormat(horizontalAlignment, verticalAlignment, wrapStrategy)"
                }
            })

        # Batch update request to apply formatting to all sheets
        body = {"requests": requests}
        spreadsheet.batch_update(body)

    def mentorwiseDivideSheets(self):
        import time

        spreadsheet = client.open_by_url(str(self.sheetLink))
        try:
            worksheet = spreadsheet.worksheet('Sheet1')
        except gspread.exceptions.WorksheetNotFound:
            raise ValueError("Sheet1 does not exist in the spreadsheet.")

        data = worksheet.get_all_records()
        df = pd.DataFrame(data)

        phone_keywords = ['phone', 'mobile', 'number']

        for col in df.columns:
            if any(keyword in col.lower() for keyword in phone_keywords):
                df[col] = df[col].astype(str).str.replace(
                    r'\D', '', regex=True).str.strip()

        if str(self.splitColumn) not in df.columns:
            raise ValueError(f"Column {self.splitColumn} Not Found")

        uniqueVal = df[str(self.splitColumn)].unique()

        for values in uniqueVal:
            filtered_data = df[df[str(self.splitColumn)] == values]

            try:
                max_retries = 3
                retry_count = 0
                while retry_count < max_retries:
                    try:
                        NewWorksheet = spreadsheet.worksheet(str(values))
                        break
                    except gspread.exceptions.APIError as e:
                        if 'quota' in str(e).lower():
                            retry_count += 1
                            if retry_count == max_retries:
                                raise
                            time.sleep(60)  # Wait 60 seconds before retrying
                        else:
                            raise
                    except gspread.exceptions.WorksheetNotFound:
                        time.sleep(
                            1)  # Small delay before creating new worksheet
                        NewWorksheet = spreadsheet.add_worksheet(str(values),
                                                                 rows=3000,
                                                                 cols=100)
                        break

                time.sleep(1)  # Small delay between operations
                NewWorksheet.clear()

                # Batch update the data
                data_values = [filtered_data.columns.values.tolist()
                               ] + filtered_data.values.tolist()
                NewWorksheet.update(range_name='A1', values=data_values)
                time.sleep(2)  # Delay between worksheet updates

            except Exception as e:
                st.error(f"Error processing worksheet {values}: {str(e)}")
                continue
        dataSheetFormatting.allignSheets(spreadsheet)
        st.write("Sheet Formatting Done !!")


class salesAnalysisReport:

    def __init__(self, queries):
        self.queries = queries

    def leadCanvasFormat(leadData, saleData, lead_cat):
        leadData = leadData[leadData['lead_category'] == lead_cat]
        saleData = saleData[saleData['CATEGORY'] == lead_cat]
        LC_data = pd.pivot_table(data=leadData,
                                 index=['assign_to'],
                                 values=['paid_status', 'cons_status'],
                                 aggfunc={
                                     'paid_status': 'count',
                                     'cons_status': 'sum'
                                 })
        sale_data = saleData[['NAME', 'SALE']].groupby('NAME').sum()
        LC_data = LC_data.reset_index()
        LC_data.rename(columns={
            'assign_to': 'NAME',
            'paid_status': 'TOTAL',
            'cons_status': 'CONS'
        },
                       inplace=True)

        data = pd.merge(LC_data, sale_data, how='left', on='NAME')
        data.fillna(0, inplace=True)
        cols = [
            col for col in data.columns if col in ('TOTAL', 'CONS', 'SALE')
        ]
        total = pd.DataFrame({
            'NAME': 'TOTAL',
            **{
                col: [data[col].sum()]
                for col in cols
            }
        })
        data = pd.concat([data, total], ignore_index=True)
        data[['TOTAL', 'CONS', 'SALE']] = data[['TOTAL', 'CONS',
                                                'SALE']].astype('int')
        data['L:C%'] = np.round((data['CONS'] / data['TOTAL']).replace(
            [np.inf, -np.inf], np.nan).fillna(0) * 100,
                                0).astype('int').astype(str) + "%"
        data['C:S%'] = np.round((data['SALE'] / data['CONS']).replace(
            [np.inf, -np.inf], np.nan).fillna(0) * 100,
                                0).astype('int').astype(str) + "%"
        data['L:S%'] = np.round((data['SALE'] / data['TOTAL']).replace(
            [np.inf, -np.inf], np.nan).fillna(0) * 100,
                                0).astype('int').astype(str) + "%"

        return data[['NAME', 'TOTAL', 'CONS', 'SALE', 'L:C%', 'C:S%', 'L:S%']]

    def generate_report_html(reportFormat):
        html_content = """<!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Lead Funnel Summary Reports</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        padding: 20px;
                        max-width: 1200px;
                        margin: 0 auto;
                    }
                    .table-container {
                        display: flex;
                        flex-wrap: wrap;
                        justify-content: center;
                    }
                    .table-container .table-wrapper {
                        margin: 20px; /* Increased gap between tables */
                        flex: 1 1 calc(50% - 40px); /* Adjusted for smaller tables */
                        max-width: calc(50% - 40px);
                    }
                    .table-container .table-wrapper.full-width {
                        flex: 1 1 100%; /* Full-width for the first table */
                        max-width: 60%;
                    }
                    table {
                        border-collapse: collapse;
                        width: 100%;
                        background-color: white;
                        border: 2px solid black; /* Black border for tables */
                    }
                    th, td {
                        border: 1px solid black; /* Black border for cells */
                        padding: 8px;
                        text-align: center;
                        font-size: 14px; /* Smaller font size */
                    }
                    th {
                        background-color: #d3d3d3; /* Column header background color */
                        font-weight: bold;
                    }
                    .title {
                        background-color: #343a40; /* Darker color for table title */
                        color: white;
                        padding: 10px;
                        text-align: center;
                        font-weight: bold;
                        border: 1px solid black; /* Black border for title */
                        margin-bottom: -1px;
                    }
                    tr:last-child {
                        background-color: #f9c2c2; /* Highlight last row with a different color */
                    }
                </style>
            </head>
            <body>
        """

        html_content += "<div class='table-container'>"

        for i, (report_key, report_data) in enumerate(reportFormat.items()):
            title = report_data['title']
            df = report_data['report']

            # Add class for full-width (first table) or regular half-width
            wrapper_class = "table-wrapper full-width" if i == 0 else "table-wrapper"

            html_content += f"""
            <div class="{wrapper_class}">
                <div class="title">{title}</div>
                <table>
                    <thead>
                        <tr>
            """
            # Add column headers
            for col in df.columns:
                html_content += f"<th>{col}</th>"
            html_content += """
                        </tr>
                    </thead>
                    <tbody>
            """

            for idx, row in df.iterrows():
                row_class = "last-row" if idx == len(df) - 1 else ""
                html_content += f"<tr class='{row_class}'>"
                for cell in row:
                    html_content += f"<td>{cell}</td>"
                html_content += "</tr>"

            html_content += """
                    </tbody>
                </table>
            </div>
            """

        html_content += "</div></body></html>"

        encoded_html = base64.b64encode(html_content.encode()).decode()
        html_link = f'<a href="data:text/html;base64,{encoded_html}" download="output.html" target="_blank">Open HTML Output</a>'
        st.markdown(html_link, unsafe_allow_html=True)

    def counsellorPerformanceReportGenerator(self):
        with engine.connect() as connection:
            saleSumamryQuery, dataSummaryQuery, smQuery = self.queries
            saleResult = connection.execute(sql.text(saleSumamryQuery))
            dataResult = connection.execute(sql.text(dataSummaryQuery))
            smLeadResult = connection.execute(sql.text(smQuery))
            saleData = pd.DataFrame(saleResult.fetchall(),
                                    columns=saleResult.keys())
            leadData = pd.DataFrame(dataResult.fetchall(),
                                    columns=dataResult.keys())
            smData = pd.DataFrame(smLeadResult.fetchall(),
                                  columns=smLeadResult.keys())

        funnel_LC_data = pd.pivot_table(data=leadData,
                                        index=['assign_to'],
                                        values=['paid_status', 'cons_status'],
                                        aggfunc={
                                            'paid_status': 'count',
                                            'cons_status': 'sum'
                                        })
        funnel_sale_data = saleData[['NAME', 'SALE']].groupby('NAME').sum()

        funnel_LC_data = funnel_LC_data.reset_index()
        funnel_LC_data.rename(columns={
            'assign_to': 'NAME',
            'paid_status': 'TOTAL',
            'cons_status': 'CONS'
        },
                              inplace=True)

        leadFunnelData = pd.merge(funnel_LC_data,
                                  funnel_sale_data,
                                  how='left',
                                  on='NAME')
        leadFunnelData.fillna(0, inplace=True)
        cols = [
            col for col in leadFunnelData.columns
            if col in ('TOTAL', 'CONS', 'SALE')
        ]
        total = pd.DataFrame({
            'NAME': 'TOTAL',
            **{
                col: [leadFunnelData[col].sum()]
                for col in cols
            }
        })
        leadFunnelData = pd.concat([leadFunnelData, total], ignore_index=True)
        leadFunnelData['SALE'] = leadFunnelData['SALE'].astype('int')
        leadFunnelData['L:C%'] = np.round(
            (leadFunnelData['CONS'] / leadFunnelData['TOTAL']).replace(
                [np.inf, -np.inf], np.nan).fillna(0) *
            100).astype("int").astype(str) + "%"
        leadFunnelData['C:S%'] = np.round(
            (leadFunnelData['SALE'] / leadFunnelData['CONS']).replace(
                [np.inf, -np.inf], np.nan).fillna(0) *
            100).astype("int").astype(str) + "%"
        leadFunnelData['L:S%'] = np.round(
            (leadFunnelData['SALE'] / leadFunnelData['TOTAL']).replace(
                [np.inf, -np.inf], np.nan).fillna(0) *
            100).astype("int").astype(str) + "%"
        leadFunnelData = leadFunnelData[[
            'NAME', 'TOTAL', 'CONS', 'SALE', 'L:C%', 'C:S%', 'L:S%'
        ]]

        smoData = smData[smData['sourcet'] == 'SMO']
        smoLead = smoData[['NAME', 'TOTAL', 'CONS', 'SALE']]
        columns = [col for col in smoLead.columns if col not in ['NAME']]
        smoTotal = pd.DataFrame({
            'NAME': 'TOTAL',
            **{
                col: [smoLead[col].sum()]
                for col in columns
            }
        })
        smoLeadData = pd.concat([smoLead, smoTotal], ignore_index=True)
        smoLeadData['CONS'] = pd.to_numeric(smoLeadData['CONS'],
                                            errors='coerce').astype('int')
        smoLeadData['TOTAL'] = pd.to_numeric(smoLeadData['TOTAL'],
                                             errors='coerce').astype('int')
        smoLeadData['SALE'] = pd.to_numeric(smoLeadData['SALE'],
                                            errors='coerce').astype('int')
        smoLeadData['L:C%'] = np.round(
            (smoLeadData['CONS'] / smoLeadData['TOTAL']).replace(
                [np.inf, -np.inf], np.nan).fillna(0) *
            100).astype("int").astype(str) + "%"
        smoLeadData['C:S%'] = np.round(
            (smoLeadData['SALE'] / smoLeadData['CONS']).replace(
                [np.inf, -np.inf], np.nan).fillna(0) *
            100).astype("int").astype(str) + "%"
        smoLeadData['L:S%'] = np.round(
            (smoLeadData['SALE'] / smoLeadData['TOTAL']).replace(
                [np.inf, -np.inf], np.nan).fillna(0) *
            100).astype("int").astype(str) + "%"
        smoLeadData = smoLeadData[[
            'NAME', 'TOTAL', 'CONS', 'SALE', 'L:C%', 'C:S%', 'L:S%'
        ]]

        smeData = smData[smData['sourcet'] == 'SME']
        smeLead = smeData[['NAME', 'TOTAL', 'CONS', 'SALE']]
        columns = [col for col in smeLead.columns if col not in ['NAME']]
        smeTotal = pd.DataFrame({
            'NAME': 'TOTAL',
            **{
                col: [smeLead[col].sum()]
                for col in columns
            }
        })
        smeLeadData = pd.concat([smeLead, smeTotal], ignore_index=True)
        smeLeadData['CONS'] = pd.to_numeric(smeLeadData['CONS'],
                                            errors='coerce').astype('int')
        smeLeadData['TOTAL'] = pd.to_numeric(smeLeadData['TOTAL'],
                                             errors='coerce').astype('int')
        smeLeadData['SALE'] = pd.to_numeric(smeLeadData['SALE'],
                                            errors='coerce').astype('int')
        smeLeadData['L:C%'] = np.round(
            (smeLeadData['CONS'] / smeLeadData['TOTAL']).replace(
                [np.inf, -np.inf], np.nan).fillna(0) *
            100).astype('int').astype(str) + "%"
        smeLeadData['C:S%'] = np.round(
            (smeLeadData['SALE'] / smeLeadData['CONS']).replace(
                [np.inf, -np.inf], np.nan).fillna(0) *
            100).astype('int').astype(str) + "%"
        smeLeadData['L:S%'] = np.round(
            (smeLeadData['SALE'] / smeLeadData['TOTAL']).replace(
                [np.inf, -np.inf], np.nan).fillna(0) *
            100).astype('int').astype(str) + "%"
        smeLeadData = smeLeadData[[
            'NAME', 'TOTAL', 'CONS', 'SALE', 'L:C%', 'C:S%', 'L:S%'
        ]]

        highPotentialLeadCanvasReport = salesAnalysisReport.leadCanvasFormat(
            leadData, saleData, 'High Potential')
        nriLeadCanvasReport = salesAnalysisReport.leadCanvasFormat(
            leadData, saleData, 'NRI')
        primeAgeLeadCanvasReport = salesAnalysisReport.leadCanvasFormat(
            leadData, saleData, 'Age 35+')
        primeStageLeadCanvasReport = salesAnalysisReport.leadCanvasFormat(
            leadData, saleData, 'Stage 3 & 4')
        otherSourceLeadCanvasReport = salesAnalysisReport.leadCanvasFormat(
            leadData, saleData, 'Other')

        reportFormat = {
            'LEAD FUNNEL REPORT': {
                'title': 'LEAD FUNNEL SUMMARY REPORT',
                'report': leadFunnelData
            },
            'HP LEAD REPORT': {
                'title': 'HIGH POTENTIAL LEADS SUMMARY REPORT',
                'report': highPotentialLeadCanvasReport
            },
            'NRI LEAD REPORT': {
                'title': 'NRI LEADS SUMMARY REPORT',
                'report': nriLeadCanvasReport
            },
            '35+ AGE LEAD REPORT': {
                'title': 'AGE 35+ LEADS SUMMARY REPORT',
                'report': primeAgeLeadCanvasReport
            },
            'HS LEAD REPORT': {
                'title': 'HS (STAGE 3 & 4) SUMMARY REPORT',
                'report': primeStageLeadCanvasReport
            },
            'SMO LEAD REPORT': {
                'title': 'SOCIAL MEDIA (SMO) LEADS SUMMARY REPORT',
                'report': smoLeadData
            },
            'SME LEAD REPORT': {
                'title': 'SOCIAL MEDIA (SME) LEADS SUMMARY REPORT',
                'report': smeLeadData
            }
        }
        salesAnalysisReport.generate_report_html(reportFormat)
