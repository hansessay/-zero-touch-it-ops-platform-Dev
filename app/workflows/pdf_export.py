from datetime import datetime
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True)


def export_telemetry_pdf(telemetry: dict):
    filename = f"fleet_telemetry_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
    file_path = REPORT_DIR / filename

    pdf = canvas.Canvas(str(file_path), pagesize=A4)
    width, height = A4

    y = height - 60

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, y, "Zero-Touch IT Operations Platform")
    y -= 30

    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(50, y, "Fleet Telemetry Audit Evidence Report")
    y -= 40

    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, y, f"Generated at: {datetime.utcnow().isoformat()} UTC")
    y -= 30

    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(50, y, "Telemetry Summary")
    y -= 25

    pdf.setFont("Helvetica", 10)

    fields = [
        ("Total Devices", telemetry.get("total_devices")),
        ("Compliant Devices", telemetry.get("compliant_devices")),
        ("Non-Compliant Devices", telemetry.get("non_compliant_devices")),
        ("Compliance Score", f"{telemetry.get('compliance_score')}%"),
        ("SentinelOne Coverage", telemetry.get("sentinelone_coverage")),
        ("BitLocker Coverage", telemetry.get("bitlocker_coverage")),
        ("Google Workspace Status", telemetry.get("google_workspace_status")),
        ("JumpCloud Status", telemetry.get("jumpcloud_status")),
        ("Workflow Status", telemetry.get("status")),
    ]

    for label, value in fields:
        pdf.drawString(70, y, f"{label}: {value}")
        y -= 20

    y -= 20
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(50, y, "Audit Statement")
    y -= 25

    pdf.setFont("Helvetica", 10)
    pdf.drawString(
        70,
        y,
        "This report was automatically generated from the Zero-Touch IT Operations Platform telemetry workflow.",
    )
    y -= 20
    pdf.drawString(
        70,
        y,
        "It can be used as supporting evidence for SOC2, ISO27001, or internal security reviews.",
    )

    pdf.save()

    return {
        "status": "success",
        "message": "PDF report generated",
        "file_path": str(file_path),
        "filename": filename,
    }