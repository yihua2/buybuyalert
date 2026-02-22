import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import ALERT_RECIPIENT, SMTP_HOST, SMTP_PASSWORD, SMTP_PORT, SMTP_USER

logger = logging.getLogger(__name__)


def send_alert_email(
    product_title: str,
    product_url: str,
    current_price: float,
    original_price: float | None,
    alert_type: str,
    threshold: float,
) -> bool:
    if not SMTP_USER or not SMTP_PASSWORD or not ALERT_RECIPIENT:
        logger.warning("SMTP not configured, skipping email")
        return False

    discount_pct = 0.0
    if original_price and original_price > 0:
        discount_pct = (original_price - current_price) / original_price * 100

    subject = f"BuyBuyAlert: {product_title[:50]} - ${current_price:.2f}"

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: #1677ff; color: white; padding: 20px; border-radius: 8px 8px 0 0;">
            <h2 style="margin: 0;">Price Alert Triggered!</h2>
        </div>
        <div style="padding: 20px; border: 1px solid #e8e8e8; border-top: none; border-radius: 0 0 8px 8px;">
            <h3 style="margin-top: 0;">{product_title}</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 8px 0; color: #666;">Current Price:</td>
                    <td style="padding: 8px 0; font-weight: bold; font-size: 18px; color: #52c41a;">${current_price:.2f}</td>
                </tr>
                {"<tr><td style='padding: 8px 0; color: #666;'>Original Price:</td><td style='padding: 8px 0; text-decoration: line-through;'>$" + f"{original_price:.2f}" + "</td></tr>" if original_price else ""}
                {"<tr><td style='padding: 8px 0; color: #666;'>Discount:</td><td style='padding: 8px 0; color: #ff4d4f; font-weight: bold;'>" + f"{discount_pct:.1f}%" + " off</td></tr>" if discount_pct > 0 else ""}
                <tr>
                    <td style="padding: 8px 0; color: #666;">Alert Type:</td>
                    <td style="padding: 8px 0;">{"Price below $" + f"{threshold:.2f}" if alert_type == "price_below" else f"{threshold:.0f}% discount"}</td>
                </tr>
            </table>
            <a href="{product_url}" style="display: inline-block; margin-top: 16px; padding: 12px 24px; background: #1677ff; color: white; text-decoration: none; border-radius: 6px;">View Product</a>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = ALERT_RECIPIENT
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        logger.info(f"Alert email sent for: {product_title}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False
