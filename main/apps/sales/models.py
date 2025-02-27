import logging
import pdfkit

from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from django.utils import timezone
from django.db import models
from django.conf import settings

from apps.products.models import Product
from celery import shared_task

logger = logging.getLogger(__name__)

class SalesOrder(models.Model):
    PENDING = "pending"
    APPROVED = "approved"
    COMPLETED = "completed"
    CANCELED = "canceled"

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (APPROVED, "Approved"),
        (COMPLETED, "Completed"),
        (CANCELED, "Canceled"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sales_orders")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="sales_orders")
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.status == self.COMPLETED and not hasattr(self, "invoice"):
            logger.info(f"Creating invoice for completed sales order {self.id}")
            invoice = Invoice.objects.create(sales_order=self)
    
    def __str__(self):
        return f"Sales Order {self.id} - {self.user}"

class Invoice(models.Model):
    sales_order = models.OneToOneField(SalesOrder, on_delete=models.CASCADE, related_name="invoice")
    invoice_date = models.DateTimeField(auto_now_add=True)

    @property
    def pdf_file(self):
        """Generates a PDF invoice for the sales order and returns it as a file."""
        try:
            context = {"invoice": self}
            html_content = render_to_string("invoice.html", context)  # Render HTML

            pdfkit_config = pdfkit.configuration(wkhtmltopdf=settings.WKHTMLTOPDF_PATH)  # Use path from settings
            pdf_file = pdfkit.from_string(html_content, False, configuration=pdfkit_config)  # Generate PDF as bytes

            # Create a ContentFile for the PDF
            filename = f"invoice_{self.sales_order.id}.pdf"
            pdf_content_file = ContentFile(pdf_file, name=filename)

            logger.info(f"PDF generated successfully for invoice {self.sales_order.id}")
            return pdf_content_file
        except Exception as e:
            logger.error(f"Error generating PDF for invoice {self.sales_order.id}: {e}")
            raise RuntimeError(f"Error generating PDF: {e}")

    def __str__(self):
        return f"Invoice for Order {self.sales_order.id}"


class Discount(models.Model):
    code = models.CharField(max_length=50, unique=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, help_text="Discount percentage (e.g., 10 for 10%)")
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    
    @property
    def is_active(self):
        return self.valid_from <= timezone.now() <= self.valid_to

    def __str__(self):
        return f"{self.code} - {self.percentage}% ({'Active' if self.is_active else 'Expired'})"
