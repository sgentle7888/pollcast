import frappe
from frappe import _
from frappe.utils import now_datetime, add_days, get_datetime, cint
from datetime import datetime, timedelta
import json
from .email_reports import send_poll_summary_report, send_survey_summary_report, send_weekly_digest

def cleanup_old_responses():
    """Clean up old poll and survey responses based on retention settings"""
    try:
        # Get retention settings from system settings
        retention_days = frappe.db.get_single_value("System Settings", "pollcast_retention_days") or 365
        cutoff_date = add_days(now_datetime(), -retention_days)
        
        # Clean up old poll responses
        old_poll_responses = frappe.get_all("Poll Response", 
            filters={"creation": ["<", cutoff_date]},
            fields=["name"]
        )
        
        for response in old_poll_responses:
            frappe.delete_doc("Poll Response", response.name, ignore_permissions=True)
        
        # Clean up old survey responses
        old_survey_responses = frappe.get_all("Survey Response",
            filters={"creation": ["<", cutoff_date]},
            fields=["name"]
        )
        
        for response in old_survey_responses:
            frappe.delete_doc("Survey Response", response.name, ignore_permissions=True)
        
        frappe.db.commit()
        
        frappe.logger().info(f"Cleaned up {len(old_poll_responses)} poll responses and {len(old_survey_responses)} survey responses")
        
    except Exception as e:
        frappe.logger().error(f"Error in cleanup_old_responses: {str(e)}")
        frappe.db.rollback()

def process_analytics_cache():
    """Update cached analytics for all active polls and surveys"""
    try:
        # Process active polls
        active_polls = frappe.get_all("Poll", 
            filters={"status": "Active"},
            fields=["name"]
        )
        
        for poll in active_polls:
            poll_doc = frappe.get_doc("Poll", poll.name)
            poll_doc.update_analytics()
            poll_doc.save(ignore_permissions=True)
        
        # Process active surveys
        active_surveys = frappe.get_all("Survey",
            filters={"status": "Active"},
            fields=["name"]
        )
        
        for survey in active_surveys:
            survey_doc = frappe.get_doc("Survey", survey.name)
            survey_doc.update_analytics()
            survey_doc.save(ignore_permissions=True)
        
        frappe.db.commit()
        
        frappe.logger().info(f"Updated analytics for {len(active_polls)} polls and {len(active_surveys)} surveys")
        
    except Exception as e:
        frappe.logger().error(f"Error in process_analytics_cache: {str(e)}")
        frappe.db.rollback()

def send_scheduled_reports():
    """Send scheduled email reports based on configuration"""
    try:
        # Get all active scheduled reports
        scheduled_reports = frappe.get_all("Scheduled Email Report",
            filters={"enabled": 1},
            fields=["name", "report_type", "frequency", "last_sent", "recipients", "poll", "survey"]
        )
        
        for report in scheduled_reports:
            should_send = False
            now = now_datetime()
            
            # Check if report should be sent based on frequency
            if report.frequency == "Daily":
                if not report.last_sent or (now - get_datetime(report.last_sent)).days >= 1:
                    should_send = True
            elif report.frequency == "Weekly":
                if not report.last_sent or (now - get_datetime(report.last_sent)).days >= 7:
                    should_send = True
            elif report.frequency == "Monthly":
                if not report.last_sent or (now - get_datetime(report.last_sent)).days >= 30:
                    should_send = True
            
            if should_send:
                recipients = json.loads(report.recipients) if report.recipients else []
                
                if report.report_type == "Poll Summary" and report.poll:
                    send_poll_summary_report(report.poll, recipients)
                elif report.report_type == "Survey Summary" and report.survey:
                    send_survey_summary_report(report.survey, recipients)
                elif report.report_type == "Weekly Digest":
                    send_weekly_digest(recipients)
                
                # Update last sent timestamp
                frappe.db.set_value("Scheduled Email Report", report.name, "last_sent", now)
        
        frappe.db.commit()
        
        frappe.logger().info(f"Processed {len(scheduled_reports)} scheduled reports")
        
    except Exception as e:
        frappe.logger().error(f"Error in send_scheduled_reports: {str(e)}")
        frappe.db.rollback()

def auto_close_expired_polls():
    """Automatically close polls that have reached their end date"""
    try:
        expired_polls = frappe.get_all("Poll",
            filters={
                "status": "Active",
                "end_date": ["<", now_datetime()]
            },
            fields=["name", "title"]
        )
        
        for poll in expired_polls:
            poll_doc = frappe.get_doc("Poll", poll.name)
            poll_doc.status = "Closed"
            poll_doc.save(ignore_permissions=True)
            
            # Send notification to poll creator
            if poll_doc.owner:
                frappe.sendmail(
                    recipients=[poll_doc.owner],
                    subject=f"Poll '{poll.title}' has been automatically closed",
                    message=f"Your poll '{poll.title}' has reached its end date and has been automatically closed.",
                    header=["Poll Closed", "blue"]
                )
        
        frappe.db.commit()
        
        frappe.logger().info(f"Auto-closed {len(expired_polls)} expired polls")
        
    except Exception as e:
        frappe.logger().error(f"Error in auto_close_expired_polls: {str(e)}")
        frappe.db.rollback()

def auto_close_expired_surveys():
    """Automatically close surveys that have reached their end date"""
    try:
        expired_surveys = frappe.get_all("Survey",
            filters={
                "status": "Active",
                "end_date": ["<", now_datetime()]
            },
            fields=["name", "title"]
        )
        
        for survey in expired_surveys:
            survey_doc = frappe.get_doc("Survey", survey.name)
            survey_doc.status = "Closed"
            survey_doc.save(ignore_permissions=True)
            
            # Send notification to survey creator
            if survey_doc.owner:
                frappe.sendmail(
                    recipients=[survey_doc.owner],
                    subject=f"Survey '{survey.title}' has been automatically closed",
                    message=f"Your survey '{survey.title}' has reached its end date and has been automatically closed.",
                    header=["Survey Closed", "blue"]
                )
        
        frappe.db.commit()
        
        frappe.logger().info(f"Auto-closed {len(expired_surveys)} expired surveys")
        
    except Exception as e:
        frappe.logger().error(f"Error in auto_close_expired_surveys: {str(e)}")
        frappe.db.rollback()

def send_response_notifications():
    """Send notifications for new responses to poll/survey creators"""
    try:
        # Get polls with notification enabled that have new responses
        polls_with_notifications = frappe.db.sql("""
            SELECT DISTINCT p.name, p.title, p.owner
            FROM `tabPoll` p
            INNER JOIN `tabPoll Response` pr ON p.name = pr.poll
            WHERE p.enable_notifications = 1
            AND pr.creation >= DATE_SUB(NOW(), INTERVAL 1 HOUR)
            AND p.status = 'Active'
        """, as_dict=True)
        
        for poll in polls_with_notifications:
            if poll.owner:
                recent_count = frappe.db.count("Poll Response", {
                    "poll": poll.name,
                    "creation": [">=", add_days(now_datetime(), 0, -1)]  # Last hour
                })
                
                if recent_count > 0:
                    frappe.sendmail(
                        recipients=[poll.owner],
                        subject=f"New responses received for poll '{poll.title}'",
                        message=f"Your poll '{poll.title}' has received {recent_count} new response(s) in the last hour.",
                        header=["New Poll Responses", "green"]
                    )
        
        # Get surveys with notification enabled that have new responses
        surveys_with_notifications = frappe.db.sql("""
            SELECT DISTINCT s.name, s.title, s.owner
            FROM `tabSurvey` s
            INNER JOIN `tabSurvey Response` sr ON s.name = sr.survey
            WHERE s.enable_notifications = 1
            AND sr.creation >= DATE_SUB(NOW(), INTERVAL 1 HOUR)
            AND s.status = 'Active'
        """, as_dict=True)
        
        for survey in surveys_with_notifications:
            if survey.owner:
                recent_count = frappe.db.count("Survey Response", {
                    "survey": survey.name,
                    "creation": [">=", add_days(now_datetime(), 0, -1)]  # Last hour
                })
                
                if recent_count > 0:
                    frappe.sendmail(
                        recipients=[survey.owner],
                        subject=f"New responses received for survey '{survey.title}'",
                        message=f"Your survey '{survey.title}' has received {recent_count} new response(s) in the last hour.",
                        header=["New Survey Responses", "green"]
                    )
        
        frappe.logger().info(f"Sent notifications for {len(polls_with_notifications)} polls and {len(surveys_with_notifications)} surveys")
        
    except Exception as e:
        frappe.logger().error(f"Error in send_response_notifications: {str(e)}")

def generate_trending_reports():
    """Generate reports for trending polls and surveys"""
    try:
        # Find trending polls (high response rate in last 24 hours)
        trending_polls = frappe.db.sql("""
            SELECT p.name, p.title, COUNT(pr.name) as recent_responses
            FROM `tabPoll` p
            INNER JOIN `tabPoll Response` pr ON p.name = pr.poll
            WHERE pr.creation >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
            AND p.status = 'Active'
            GROUP BY p.name, p.title
            HAVING recent_responses >= 10
            ORDER BY recent_responses DESC
            LIMIT 10
        """, as_dict=True)
        
        # Find trending surveys
        trending_surveys = frappe.db.sql("""
            SELECT s.name, s.title, COUNT(sr.name) as recent_responses
            FROM `tabSurvey` s
            INNER JOIN `tabSurvey Response` sr ON s.name = sr.survey
            WHERE sr.creation >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
            AND s.status = 'Active'
            GROUP BY s.name, s.title
            HAVING recent_responses >= 5
            ORDER BY recent_responses DESC
            LIMIT 10
        """, as_dict=True)
        
        # Store trending data for dashboard
        trending_data = {
            "polls": trending_polls,
            "surveys": trending_surveys,
            "generated_at": now_datetime().isoformat()
        }
        
        # Cache trending data
        frappe.cache().set_value("pollcast_trending_data", json.dumps(trending_data, default=str))
        
        frappe.logger().info(f"Generated trending report with {len(trending_polls)} polls and {len(trending_surveys)} surveys")
        
    except Exception as e:
        frappe.logger().error(f"Error in generate_trending_reports: {str(e)}")
