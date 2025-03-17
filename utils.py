
import warnings
warnings.filterwarnings('ignore')
import streamlit as st
from datetime import datetime

class summaryTable:
    def __init__(self, query, title, title_font_size, table_width, table_font_size, title_space):
        self.query = query
        self.title = title
        self.title_font_size = title_font_size
        self.table_width = table_width
        self.table_font_size = table_font_size
        self.title_space = title_space
        
    def Generator(self):
        st.markdown(f"## {self.title}")
        
    def generatorForGut(self):
        st.markdown(f"## {self.title}")
        
    def leadReportGenerator(self):
        st.markdown(f"## {self.title}")
        
    def socialMediaAssignedLeadGenerator(self):
        st.markdown(f"## {self.title}")

def socialMediaNewLeadSummaryGenerator(queries):
    st.markdown("## Social Media New Lead Summary")

def morningLeadReportGenerator(queries):
    st.markdown("## Morning Lead Report")

class dataSheets:
    def __init__(self, query, title):
        self.query = query
        self.title = title
        
    def mentorwiseDivideSheets(self):
        return "Data sheet generated"

class recordUpdate:
    def __init__(self, sheet, query):
        self.sheet = sheet
        self.query = query
        
    def updateRecentRecord(self):
        pass

class removePaidData:
    def __init__(self, sheet, start_date, end_date):
        self.sheet = sheet
        self.start_date = start_date
        self.end_date = end_date
        
    def removePaidUsingEmail(self):
        pass
        
    def removePaidUsingPhone(self):
        pass

class mentorAudit:
    def __init__(self, queries):
        self.queries = queries
        
    def update_sheet_with_data(self, spreadsheet_id, sheet_name, titles, start_row, start_col):
        pass

class dataSheetFormatting:
    def __init__(self, sheetlink, splitcol):
        self.sheetlink = sheetlink
        self.splitcol = splitcol
        
    def mentorwiseDivideSheets(self):
        pass

class salesAnalysisReport:
    def __init__(self, queries):
        self.queries = queries
        
    def counsellorPerformanceReportGenerator(self):
        st.markdown("## Counsellor Performance Analysis")
