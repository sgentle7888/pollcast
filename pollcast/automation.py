import frappe
from frappe import _
from frappe.utils import now_datetime, add_days, get_datetime
from .background_jobs import create_job_log
import json

def setup_automation_rules():
    """Setup automation rules for polls and surveys"""
    
    # Auto-notification rule for new responses
    if not frappe.db.exists("Auto Email Report", "Poll Response Notification"):
        auto_report = frappe.get_doc({
            "doctype": "Auto Email Report",
            "name": "Poll Response Notification",
            "report": "Poll Response Summary",
            "user": "Administrator",
            "enabled": 1,
            "format": "HTML",
            "frequency": "Hourly",
            "filters": json.dumps({
                "creation": [">=", add_days(now_datetime(), 0, -1)]
            })
        })
        auto_report.insert(ignore_permissions=True)

def trigger_webhook(event_type, doc_name, doc_data):
    """Trigger webhooks for external integrations"""
    try:
        # Get webhook configurations
        webhooks = frappe.get_all("Webhook", 
            filters={"enabled": 1, "condition": ["like", f"%{event_type}%"]},
            fields=["name", "webhook_url", "webhook_headers", "webhook_data"]
        )
        
        for webhook in webhooks:
            webhook_doc = frappe.get_doc("Webhook", webhook.name)
            
            # Prepare payload
            payload = {
                "event": event_type,
                "doc_name": doc_name,
                "doc_data": doc_data,
                "timestamp": now_datetime().isoformat()
            }
            
            # Send webhook (this would typically use requests library)
            frappe.enqueue(
                "pollcast.automation.send_webhook_request",
                webhook_url=webhook_doc.webhook_url,
                payload=payload,
                headers=json.loads(webhook_doc.webhook_headers or "{}"),
                queue="short"
            )
            
    except Exception as e:
        frappe.logger().error(f"Error triggering webhook: {str(e)}")

def send_webhook_request(webhook_url, payload, headers=None):
    """Send webhook request (queued function)"""
    import requests
    
    try:
        headers = headers or {"Content-Type": "application/json"}
        response = requests.post(webhook_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        frappe.logger().info(f"Webhook sent successfully to {webhook_url}")
        
    except Exception as e:
        frappe.logger().error(f"Failed to send webhook to {webhook_url}: {str(e)}")

def auto_archive_inactive_content():
    """Automatically archive polls and surveys with no recent activity"""
    try:
        job_log = create_job_log("Auto Archive Inactive Content")
        
        # Archive polls with no responses in last 30 days
        inactive_polls = frappe.db.sql("""
            SELECT p.name, p.title
            FROM `tabPoll` p
            LEFT JOIN `tabPoll Response` pr ON p.name = pr.poll AND pr.creation >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            WHERE p.status = 'Active'
            AND p.creation < DATE_SUB(NOW(), INTERVAL 30 DAY)
            AND pr.name IS NULL
        """, as_dict=True)
        
        archived_polls = 0
        for poll in inactive_polls:
            frappe.db.set_value("Poll", poll.name, "status", "Archived")
            archived_polls += 1
        
        # Archive surveys with no responses in last 30 days
        inactive_surveys = frappe.db.sql("""
            SELECT s.name, s.title
            FROM `tabSurvey` s
            LEFT JOIN `tabSurvey Response` sr ON s.name = sr.survey AND sr.creation >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            WHERE s.status = 'Active'
            AND s.creation < DATE_SUB(NOW(), INTERVAL 30 DAY)
            AND sr.name IS NULL
        """, as_dict=True)
        
        archived_surveys = 0
        for survey in inactive_surveys:
            frappe.db.set_value("Survey", survey.name, "status", "Archived")
            archived_surveys += 1
        
        frappe.db.commit()
        
        job_log.mark_completed({
            "archived_polls": archived_polls,
            "archived_surveys": archived_surveys
        })
        
        frappe.logger().info(f"Auto-archived {archived_polls} polls and {archived_surveys} surveys")
        
    except Exception as e:
        job_log.mark_failed(str(e))
        frappe.logger().error(f"Error in auto_archive_inactive_content: {str(e)}")

def smart_notification_system():
    """Smart notification system based on user engagement patterns"""
    try:
        job_log = create_job_log("Smart Notification System")
        
        # Analyze user engagement patterns
        engagement_data = frappe.db.sql("""
            SELECT 
                pr.respondent_email,
                COUNT(*) as response_count,
                MAX(pr.creation) as last_response,
                AVG(TIMESTAMPDIFF(MINUTE, p.creation, pr.creation)) as avg_response_time
            FROM `tabPoll Response` pr
            INNER JOIN `tabPoll` p ON pr.poll = p.name
            WHERE pr.creation >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            AND pr.respondent_email IS NOT NULL
            GROUP BY pr.respondent_email
            HAVING response_count >= 3
        """, as_dict=True)
        
        # Send personalized engagement emails
        notifications_sent = 0
        for user in engagement_data:
            if user.last_response and (now_datetime() - get_datetime(user.last_response)).days >= 7:
                # User hasn't responded in a week, send re-engagement email
                frappe.sendmail(
                    recipients=[user.respondent_email],
                    subject="We miss your input! New polls available",
                    template="re_engagement_email",
                    args={
                        "user_email": user.respondent_email,
                        "response_count": user.response_count,
                        "avg_response_time": user.avg_response_time
                    }
                )
                notifications_sent += 1
        
        job_log.mark_completed({
            "analyzed_users": len(engagement_data),
            "notifications_sent": notifications_sent
        })
        
        frappe.logger().info(f"Smart notifications: analyzed {len(engagement_data)} users, sent {notifications_sent} notifications")
        
    except Exception as e:
        job_log.mark_failed(str(e))
        frappe.logger().error(f"Error in smart_notification_system: {str(e)}")
