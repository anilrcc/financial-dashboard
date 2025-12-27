import openpyxl

file_path = '/Users/anilgungadeen/.gemini/antigravity/scratch/financial_dashboard_dist/NFIB_Small_Business_Sentiment_Components.xlsx'
wb = openpyxl.load_workbook(file_path, data_only=True)
ws = wb['SBO_Leading_vs_GDP']

print("        // Historical Leading Index from NFIB (1986-2020)")
print("        const historicalLeadingIndex = {")

data = {}
for row in ws.iter_rows(min_row=2, values_only=True):
    date_val, leading_index = row[0], row[1]
    if date_val and leading_index is not None:
        month_str = date_val.strftime("%b %Y")
        data[month_str] = float(leading_index)

for i, (month, value) in enumerate(data.items()):
    comma = "," if i < len(data) - 1 else ""
    print(f'            "{month}": {value}{comma}')

print("        };")
