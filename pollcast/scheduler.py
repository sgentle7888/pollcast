import frappe
from .background_jobs import (
    cleanup_old_responses,
    process_analytics_cache,
    send_scheduled_reports,
    auto_close_expired_polls,
    auto_close_expired_surveys,
    send_response_notifications,
    generate_trending_reports
)

def daily_cleanup():
    """Daily cleanup tasks"""
    cleanup_old_responses()
    auto_close_expired_polls()
    auto_close_expired_surveys()

def hourly_analytics():
    """Hourly analytics processing"""
    process_analytics_cache()
    send_response_notifications()
    generate_trending_reports()

def daily_reports():
    """Daily report sending"""
    send_scheduled_reports()

def weekly_maintenance():
    """Weekly maintenance tasks"""
    # Additional weekly maintenance can be added here
    pass
