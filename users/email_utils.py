"""
Email utility functions for sending transactional emails using SendGrid Web API.
"""
import logging
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings

logger = logging.getLogger(__name__)


def _send_email_via_sendgrid(to_email, subject, html_content):
    """
    Helper function to send email via SendGrid Web API.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML email content
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    try:
        api_key = os.getenv('SENDGRID_API_KEY')
        from_email = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@yourdomain.com')
        
        if not api_key:
            logger.warning("SENDGRID_API_KEY not set - email not sent")
            return False
        
        message = Mail(
            from_email=from_email,
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )
        
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        
        logger.info(f"Email sent to {to_email}. Status: {response.status_code}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False


def send_password_reset_email(user_email, reset_link, user_name=""):
    """
    Send password reset email to user.
    
    Args:
        user_email: User's email address
        reset_link: Password reset link with token
        user_name: User's name (optional)
    """
    subject = 'Reset Your Password - Booking System'
    
    # HTML email content
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Password Reset Request</h1>
            </div>
            <div class="content">
                <p>Hello {user_name or 'there'},</p>
                <p>We received a request to reset your password for your Booking System account.</p>
                <p>Click the button below to reset your password. This link will expire in 24 hours.</p>
                <p style="text-align: center;">
                    <a href="{reset_link}" class="button">Reset Password</a>
                </p>
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #667eea;">{reset_link}</p>
                <p><strong>If you didn't request this password reset, please ignore this email.</strong></p>
                <p>For security reasons, this reset link will expire in 24 hours.</p>
            </div>
            <div class="footer">
                <p>© 2026 Booking System. All rights reserved.</p>
                <p>This is an automated email, please do not reply.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    _send_email_via_sendgrid(user_email, subject, html_message)


def send_booking_confirmation_email(user_email, booking_details, user_name=""):
    """
    Send booking confirmation email to user.
    
    Args:
        user_email: User's email address
        booking_details: Dictionary containing booking information
        user_name: User's name (optional)
    """
    subject = 'Booking Confirmation - Booking System'
    
    resource_name = booking_details.get('resource_name', 'Resource')
    booking_date = booking_details.get('date', '')
    start_time = booking_details.get('start_time', '')
    end_time = booking_details.get('end_time', '')
    booking_id = booking_details.get('booking_id', '')
    
    # HTML email content
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .booking-details {{ background: white; padding: 20px; border-radius: 5px; margin: 20px 0; }}
            .detail-row {{ padding: 10px 0; border-bottom: 1px solid #eee; }}
            .detail-label {{ font-weight: bold; color: #667eea; }}
            .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>✓ Booking Confirmed</h1>
            </div>
            <div class="content">
                <p>Hello {user_name or 'there'},</p>
                <p>Your booking has been successfully confirmed!</p>
                
                <div class="booking-details">
                    <h3 style="margin-top: 0; color: #667eea;">Booking Details</h3>
                    <div class="detail-row">
                        <span class="detail-label">Booking ID:</span> #{booking_id}
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Resource:</span> {resource_name}
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Date:</span> {booking_date}
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Time:</span> {start_time} - {end_time}
                    </div>
                </div>
                
                <p>Please arrive on time and bring any necessary identification.</p>
                <p>If you need to cancel or modify your booking, please log in to your account.</p>
            </div>
            <div class="footer">
                <p>© 2026 Booking System. All rights reserved.</p>
                <p>This is an automated email, please do not reply.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    _send_email_via_sendgrid(user_email, subject, html_message)


def send_booking_cancellation_email(user_email, booking_details, user_name=""):
    """
    Send booking cancellation email to user.
    
    Args:
        user_email: User's email address
        booking_details: Dictionary containing booking information
        user_name: User's name (optional)
    """
    subject = 'Booking Cancelled - Booking System'
    
    resource_name = booking_details.get('resource_name', 'Resource')
    booking_date = booking_details.get('date', '')
    start_time = booking_details.get('start_time', '')
    booking_id = booking_details.get('booking_id', '')
    
    # HTML email content
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #dc3545; color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Booking Cancelled</h1>
            </div>
            <div class="content">
                <p>Hello {user_name or 'there'},</p>
                <p>Your booking has been cancelled.</p>
                <p><strong>Cancelled Booking:</strong></p>
                <ul>
                    <li>Booking ID: #{booking_id}</li>
                    <li>Resource: {resource_name}</li>
                    <li>Date: {booking_date}</li>
                    <li>Time: {start_time}</li>
                </ul>
                <p>You can make a new booking anytime by logging into your account.</p>
            </div>
            <div class="footer">
                <p>© 2026 Booking System. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    _send_email_via_sendgrid(user_email, subject, html_message)
