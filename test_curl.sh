#!/bin/bash

# Create a simple test PDF using Python
python3 -c "
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

c = canvas.Canvas('test_sample.pdf', pagesize=letter)
c.drawString(100, 750, 'Sample PDF for curl test')
c.drawString(100, 700, 'This is a test document.')
c.drawString(100, 650, 'Created for API testing purposes.')
c.showPage()
c.save()
print('test_sample.pdf created')
"

# Test the API endpoint with curl
echo "Testing PDF upload with curl..."
curl -X POST "http://localhost:8000/upload-pdf/" \
     -H "Authorization: Bearer test" \
     -F "file=@test_sample.pdf" \
     | python3 -m json.tool

# Clean up
rm test_sample.pdf
echo "Test completed and cleaned up." 