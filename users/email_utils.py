"""
Email utility functions for sending transactional emails.
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags


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
    
    # Plain text version
    plain_message = f"""
    Password Reset Request
    
    Hello {user_name or 'there'},
    
    We received a request to reset your password for your Booking System account.
    
    Click the link below to reset your password. This link will expire in 24 hours.
    
    {reset_link}
    
    If you didn't request this password reset, please ignore this email.
    
    For security reasons, this reset link will expire in 24 hours.
    
    © 2026 Booking System. All rights reserved.
    This is an automated email, please do not reply.
    """
    
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        html_message=html_message,
        fail_silently=False,
    )


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
    
    # Plain text version
    plain_message = f"""
    Booking Confirmed
    
    Hello {user_name or 'there'},
    
    Your booking has been successfully confirmed!
    
    Booking Details:
    ----------------
    Booking ID: #{booking_id}
    Resource: {resource_name}
    Date: {booking_date}
    Time: {start_time} - {end_time}
    
    Please arrive on time and bring any necessary identification.
    
    If you need to cancel or modify your booking, please log in to your account.
    
    © 2026 Booking System. All rights reserved.
    This is an automated email, please do not reply.
    """
    
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        html_message=html_message,
        fail_silently=False,
    )


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
    
    plain_message = f"""
    Booking Cancelled
    
    Hello {user_name or 'there'},
    
    Your booking has been cancelled.
    
    Cancelled Booking:
    - Booking ID: #{booking_id}
    - Resource: {resource_name}
    - Date: {booking_date}
    - Time: {start_time}
    
    You can make a new booking anytime by logging into your account.
    
    © 2026 Booking System. All rights reserved.
    """
    
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        html_message=html_message,
        fail_silently=False,
    )
