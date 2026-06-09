import csv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

csv_file = "rapport_webgoat.csv"
pdf_file = "rapport_webgoat.pdf"

c = canvas.Canvas(pdf_file, pagesize=letter)
width, height = letter

y = height - 40

with open(csv_file, "r", encoding="utf-8") as f:
    reader = csv.reader(f)

    for row in reader:
        line = ", ".join(row)

        if y < 40:
            c.showPage()
            y = height - 40

        c.drawString(40, y, line[:120])
        y -= 15

c.save()

print("PDF généré :", pdf_file)
