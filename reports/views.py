from django.shortcuts import render
from django.views.generic import TemplateView
import io
from django.http import FileResponse, HttpResponse


class ReportsIndexView(TemplateView):
    template_name = "reports/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['report_message'] = "Welcome to the Reports Section"
        context['available_reports'] = ["Monthly Sales", "Customer Feedback", "Inventory Status"]
        context['report_formats'] = ["PDF", "CSV"]
        return context


def generate_pdf(request, time_range="monthly"):
    from reportlab.pdfgen import canvas
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.drawString(100, 750, "Hello, this is your report PDF.")
    p.showPage()
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f'report_{time_range}.pdf')


def generate_csv(request, time_range="monthly"):
    import csv
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="report_{time_range}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Column 1', 'Column 2', 'Column 3'])
    writer.writerow(['Data 1', 'Data 2', 'Data 3'])
    return response
