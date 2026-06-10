# Auto Report Generator

#import libraries
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
#io to allow us to create a PDF in memory without saving it to disk
import io

# -- Page title and description --
st.title("PDF Report Generator")
st.write("Upload a CSV file to generate a PDF report.")

# -- File uploader --
#Accept only CSV files
file = st.file_uploader("Upload your CSV file", type=["csv"])

# --- helper function: generate scatter plot with regression line ---
def generate_chart(df, col_x, col_y):
    #Extract the two columns we want to analyze
    x = df[col_x]
    y = df[col_y]

    # Calculate the regression line
    m, b = np.polyfit(x, y, 1)  # Linear regression coefficients
    regression_line = m * x + b

    # Calculate the correlation coefficient
    correlation = df[col_x].corr(df[col_y])

    # Create the scatter plot
    fig, ax = plt.subplots(figsize=(8, 4))

    # Scatter plot: each house as a dot
    ax.scatter(x, y, color='blue', alpha=0.6, label='Houses')

    # Add the regression line
    ax.plot(x, regression_line, color='red', label=f'Regression Line (r={correlation:.2f})')

    # Set labels and title
    ax.set_xlabel(col_x)
    ax.set_ylabel(col_y)
    ax.set_title(f"{col_x} vs. {col_y}")
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.4)

    # Save the chart to a memory as an image
    chart_buffer = io.BytesIO()
    plt.savefig(chart_buffer, format='png', dpi = 300, bbox_inches='tight')
    plt.close()  # Close the plot to free memory
    chart_buffer.seek(0)  # Move buffer position to the start
    return chart_buffer, correlation

    

# -- Main logic to generate PDF --
if file is not None:
    #Read the CSV file into a DataFrame
    df = pd.read_csv(file)
    st.success("File uploaded successfully!")

    #Preview the data
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()

    #pick the columns we want to analyze 
    st.subheader("Select Columns for Analysis")
    col_x = st.selectbox("Select X-axis column", options=numeric_columns)
    col_y = st.selectbox("Select Y-axis column", options=numeric_columns)

    st.dataframe(df)
    st.write(f"Total rows: {len(df)}")

    # Show the chart previe in the borwser
    st.subheader("Chart Preview")
    chart_buffer, correlation = generate_chart(df, col_x, col_y)
    st.image(chart_buffer, use_column_width=True)
    st.write(f"Correlation coefficient: **{correlation:.2f}**")

    #  -- PDF generation --
    if st.button("Generate PDF Report"):

        # Regenerate the chart to ensure it's fresh for the PDF
        chart_buffer, correlation = generate_chart(df , col_x, col_y)

        #Create an in-memory buffer to hold the PDF
        buffer = io.BytesIO()

        #Set up the PDF document with A4 size
        doc = SimpleDocTemplate(buffer, pagesize=A4) 

        #Load default text styles (Tittle, Normal, etc.)
        styles = getSampleStyleSheet()

        #List that will hold all PDF elements in order   
        elements = []

       # --- Title ---
        title = Paragraph("Data Report", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 20))

        # --- Chart image ---
        chart_image = Image(chart_buffer, width=450, height=220)
        elements.append(chart_image)
        elements.append(Spacer(1, 20))  # Add space after the chart

        # --- Correlation text ---
        if correlation > 0.7:
            interpretation = "strong positive"
        elif correlation > 0.4:
            interpretation = "moderate positive"
        elif correlation > -0.4:
            interpretation = "weak"
        elif correlation > -0.7:
            interpretation = "moderate negative"
        else:
            interpretation = "strong negative"

        correlation_text = Paragraph(   
        f"The data shows a <b>{interpretation}</b> correlation between <b>{col_x}</b> and <b>{col_y}</b> with a correlation coefficient of <b>{correlation:.2f}</b>.",
        styles['Normal']
        )
        elements.append(correlation_text)
        elements.append(Spacer(1, 16))

        # --- summary statistics ---
        stats_df = df[[col_x, col_y]].describe().round(2)

        # Title for the statistics section
        # Title for the statistics section
        stats_title = Paragraph("Summary Statistics", styles['Heading2'])
        elements.append(stats_title)
        elements.append(Spacer(1, 12))

        #Build the stats table with headers
        stats_data = [["Metric", col_x, col_y]]
        for index, row in stats_df.iterrows():
            stats_data.append([index, row[col_x], row[col_y]])

        stats_table = Table(stats_data, colWidths=[100, 150, 150])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # Header background
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),  # Header text color
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center align all cells
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header font
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Header padding
            ('GRID', (0, 0), (-1, -1), 1, colors.black)  # Grid lines
        ]))
        elements.append(stats_table)
        elements.append(Spacer(1, 20))


        # --- Table ---
        data = [df.columns.tolist()] + df.values.tolist()
        table = Table(data)

        # Style the table
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Header background
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Header text color
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center align all cells
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header font
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Header padding
            ('GRID', (0, 0), (-1, -1), 1, colors.black)  # Grid lines
        ]))
        elements.append(table)


        # --- Build the PDF ---
        doc.build(elements)

        # Move buffer position back to the start so it can be read
        buffer.seek(0)

        # ---Download buttom---
        st.download_button(
            label="Download PDF Report",
            data=buffer,
            file_name="data_report.pdf",
            mime="application/pdf"
        )
        st.success("PDF report generated successfully!")