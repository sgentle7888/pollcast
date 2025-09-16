import frappe
from frappe import _
from frappe.utils import now, add_days, get_datetime, format_date, cint
from frappe.core.doctype.communication.email import make
import json
from datetime import datetime, timedelta
import base64
import io

@frappe.whitelist()
def send_poll_report(poll_name, recipients=None, report_type="summary"):
    """Send email report for a specific poll"""
    try:
        poll_doc = frappe.get_doc('Poll', poll_name)
        analytics_data = poll_doc.get_analytics_data()
        
        # Get recipients
        if not recipients:
            recipients = get_default_recipients(poll_doc)
        
        if isinstance(recipients, str):
            recipients = [recipients]
        
        # Generate report content
        if report_type == "detailed":
            html_content = generate_detailed_poll_report(poll_doc, analytics_data)
            subject = f"Detailed Poll Report: {poll_doc.title}"
        else:
            html_content = generate_summary_poll_report(poll_doc, analytics_data)
            subject = f"Poll Summary: {poll_doc.title}"
        
        # Send email
        for recipient in recipients:
            frappe.sendmail(
                recipients=[recipient],
                subject=subject,
                message=html_content,
                header=["Poll Report", "green"],
                delayed=False
            )
        
        # Log the report sending
        frappe.get_doc({
            'doctype': 'Email Report Log',
            'report_type': 'Poll Report',
            'document_name': poll_name,
            'recipients': json.dumps(recipients),
            'sent_at': now(),
            'status': 'Sent'
        }).insert(ignore_permissions=True)
        
        return {'success': True, 'message': f'Report sent to {len(recipients)} recipients'}
    
    except Exception as e:
        frappe.log_error(f"Poll report sending error: {str(e)}")
        return {'error': str(e)}

@frappe.whitelist()
def send_survey_report(survey_name, recipients=None, report_type="summary"):
    """Send email report for a specific survey"""
    try:
        survey_doc = frappe.get_doc('Survey', survey_name)
        analytics_data = survey_doc.get_analytics_data()
        
        # Get recipients
        if not recipients:
            recipients = get_default_recipients(survey_doc)
        
        if isinstance(recipients, str):
            recipients = [recipients]
        
        # Generate report content
        if report_type == "detailed":
            html_content = generate_detailed_survey_report(survey_doc, analytics_data)
            subject = f"Detailed Survey Report: {survey_doc.title}"
        else:
            html_content = generate_summary_survey_report(survey_doc, analytics_data)
            subject = f"Survey Summary: {survey_doc.title}"
        
        # Send email
        for recipient in recipients:
            frappe.sendmail(
                recipients=[recipient],
                subject=subject,
                message=html_content,
                header=["Survey Report", "blue"],
                delayed=False
            )
        
        # Log the report sending
        frappe.get_doc({
            'doctype': 'Email Report Log',
            'report_type': 'Survey Report',
            'document_name': survey_name,
            'recipients': json.dumps(recipients),
            'sent_at': now(),
            'status': 'Sent'
        }).insert(ignore_permissions=True)
        
        return {'success': True, 'message': f'Report sent to {len(recipients)} recipients'}
    
    except Exception as e:
        frappe.log_error(f"Survey report sending error: {str(e)}")
        return {'error': str(e)}

@frappe.whitelist()
def send_weekly_digest():
    """Send weekly digest report with all active polls and surveys"""
    try:
        # Get all active polls and surveys
        active_polls = frappe.get_all('Poll', filters={'status': 'Active'})
        active_surveys = frappe.get_all('Survey', filters={'status': 'Active'})
        
        if not active_polls and not active_surveys:
            return {'message': 'No active polls or surveys to report'}
        
        # Prepare digest data
        digest_data = {
            'week_start': add_days(now(), -7),
            'week_end': now(),
            'polls': [],
            'surveys': [],
            'summary': {
                'total_polls': len(active_polls),
                'total_surveys': len(active_surveys),
                'total_responses': 0,
                'top_performing': None
            }
        }
        
        # Process polls
        for poll in active_polls:
            poll_doc = frappe.get_doc('Poll', poll.name)
            analytics = poll_doc.get_analytics_data()
            
            poll_data = {
                'title': poll_doc.title,
                'total_responses': analytics['total_responses'],
                'top_option': max(analytics['options'], key=lambda x: x['count']) if analytics['options'] else None,
                'engagement_rate': calculate_engagement_rate(poll.name, 'Poll')
            }
            
            digest_data['polls'].append(poll_data)
            digest_data['summary']['total_responses'] += analytics['total_responses']
        
        # Process surveys
        for survey in active_surveys:
            survey_doc = frappe.get_doc('Survey', survey.name)
            analytics = survey_doc.get_analytics_data()
            
            survey_data = {
                'title': survey_doc.title,
                'total_responses': analytics['total_responses'],
                'completion_rate': calculate_completion_rate(survey.name),
                'question_count': len(survey_doc.questions)
            }
            
            digest_data['surveys'].append(survey_data)
            digest_data['summary']['total_responses'] += analytics['total_responses']
        
        # Find top performing item
        all_items = [(p, p['total_responses'], 'Poll') for p in digest_data['polls']] + \
                   [(s, s['total_responses'], 'Survey') for s in digest_data['surveys']]
        
        if all_items:
            top_item = max(all_items, key=lambda x: x[1])
            digest_data['summary']['top_performing'] = {
                'title': top_item[0]['title'],
                'type': top_item[2],
                'responses': top_item[1]
            }
        
        # Generate HTML content
        html_content = generate_weekly_digest_report(digest_data)
        
        # Get recipients (system administrators and poll managers)
        recipients = get_digest_recipients()
        
        # Send email
        for recipient in recipients:
            frappe.sendmail(
                recipients=[recipient],
                subject=f"Pollcast Weekly Digest - {format_date(digest_data['week_start'])} to {format_date(digest_data['week_end'])}",
                message=html_content,
                header=["Weekly Digest", "purple"],
                delayed=False
            )
        
        # Log the digest sending
        frappe.get_doc({
            'doctype': 'Email Report Log',
            'report_type': 'Weekly Digest',
            'document_name': 'Weekly Digest',
            'recipients': json.dumps(recipients),
            'sent_at': now(),
            'status': 'Sent'
        }).insert(ignore_permissions=True)
        
        return {'success': True, 'message': f'Weekly digest sent to {len(recipients)} recipients'}
    
    except Exception as e:
        frappe.log_error(f"Weekly digest error: {str(e)}")
        return {'error': str(e)}

def get_default_recipients(doc):
    """Get default recipients for a poll or survey"""
    recipients = []
    
    # Add document owner
    if doc.owner:
        recipients.append(doc.owner)
    
    # Add users with Poll Manager role
    poll_managers = frappe.get_all('Has Role', 
        filters={'role': 'Poll Manager'}, 
        fields=['parent']
    )
    
    for manager in poll_managers:
        user_email = frappe.db.get_value('User', manager.parent, 'email')
        if user_email and user_email not in recipients:
            recipients.append(user_email)
    
    return recipients

def get_digest_recipients():
    """Get recipients for weekly digest"""
    recipients = []
    
    # Add System Managers
    system_managers = frappe.get_all('Has Role', 
        filters={'role': 'System Manager'}, 
        fields=['parent']
    )
    
    for manager in system_managers:
        user_email = frappe.db.get_value('User', manager.parent, 'email')
        if user_email and user_email not in recipients:
            recipients.append(user_email)
    
    # Add Poll Managers
    poll_managers = frappe.get_all('Has Role', 
        filters={'role': 'Poll Manager'}, 
        fields=['parent']
    )
    
    for manager in poll_managers:
        user_email = frappe.db.get_value('User', manager.parent, 'email')
        if user_email and user_email not in recipients:
            recipients.append(user_email)
    
    return recipients

def calculate_engagement_rate(doc_name, doc_type):
    """Calculate engagement rate for a poll or survey"""
    try:
        if doc_type == 'Poll':
            doc = frappe.get_doc('Poll', doc_name)
            days_active = (get_datetime() - get_datetime(doc.creation)).days or 1
            return round((doc.total_responses / days_active) * 10, 1)
        else:
            doc = frappe.get_doc('Survey', doc_name)
            days_active = (get_datetime() - get_datetime(doc.creation)).days or 1
            return round((doc.total_responses / days_active) * 10, 1)
    except:
        return 0

def calculate_completion_rate(survey_name):
    """Calculate completion rate for a survey"""
    try:
        survey_doc = frappe.get_doc('Survey', survey_name)
        total_questions = len(survey_doc.questions)
        
        if total_questions == 0:
            return 100
        
        # Get unique participants
        participants = frappe.db.sql("""
            SELECT DISTINCT participant_ip 
            FROM `tabSurvey Response` 
            WHERE survey = %s
        """, survey_name)
        
        if not participants:
            return 0
        
        # Calculate average questions answered per participant
        total_responses = frappe.db.count('Survey Response', {'survey': survey_name})
        avg_questions_answered = total_responses / len(participants)
        
        completion_rate = (avg_questions_answered / total_questions) * 100
        return round(completion_rate, 1)
    
    except:
        return 0

def generate_summary_poll_report(poll_doc, analytics_data):
    """Generate HTML content for poll summary report"""
    template = frappe.get_template('templates/emails/poll_summary_report.html')
    
    return template.render({
        'poll': poll_doc,
        'analytics': analytics_data,
        'generated_at': now(),
        'site_url': frappe.utils.get_url()
    })

def generate_detailed_poll_report(poll_doc, analytics_data):
    """Generate HTML content for detailed poll report"""
    template = frappe.get_template('templates/emails/poll_detailed_report.html')
    
    return template.render({
        'poll': poll_doc,
        'analytics': analytics_data,
        'generated_at': now(),
        'site_url': frappe.utils.get_url(),
        'chart_data': generate_chart_data_url(analytics_data)
    })

def generate_summary_survey_report(survey_doc, analytics_data):
    """Generate HTML content for survey summary report"""
    template = frappe.get_template('templates/emails/survey_summary_report.html')
    
    return template.render({
        'survey': survey_doc,
        'analytics': analytics_data,
        'generated_at': now(),
        'site_url': frappe.utils.get_url()
    })

def generate_detailed_survey_report(survey_doc, analytics_data):
    """Generate HTML content for detailed survey report"""
    template = frappe.get_template('templates/emails/survey_detailed_report.html')
    
    return template.render({
        'survey': survey_doc,
        'analytics': analytics_data,
        'generated_at': now(),
        'site_url': frappe.utils.get_url()
    })

def generate_weekly_digest_report(digest_data):
    """Generate HTML content for weekly digest report"""
    template = frappe.get_template('templates/emails/weekly_digest.html')
    
    return template.render({
        'digest': digest_data,
        'generated_at': now(),
        'site_url': frappe.utils.get_url()
    })

def generate_chart_data_url(analytics_data):
    """Generate chart data URL for embedding in emails"""
    try:
        # This would generate a chart image URL using a service like QuickChart
        # For now, return a placeholder
        return "https://quickchart.io/chart?c={type:'doughnut',data:{labels:['Option 1','Option 2'],datasets:[{data:[10,20]}]}}"
    except:
        return None

@frappe.whitelist()
def schedule_report(doc_type, doc_name, recipients, frequency="weekly", report_type="summary"):
    """Schedule automated reports"""
    try:
        # Create scheduled report entry
        scheduled_report = frappe.get_doc({
            'doctype': 'Scheduled Email Report',
            'document_type': doc_type,
            'document_name': doc_name,
            'recipients': json.dumps(recipients if isinstance(recipients, list) else [recipients]),
            'frequency': frequency,
            'report_type': report_type,
            'next_send_date': calculate_next_send_date(frequency),
            'enabled': 1
        })
        
        scheduled_report.insert(ignore_permissions=True)
        
        return {'success': True, 'message': 'Report scheduled successfully'}
    
    except Exception as e:
        frappe.log_error(f"Report scheduling error: {str(e)}")
        return {'error': str(e)}

def calculate_next_send_date(frequency):
    """Calculate next send date based on frequency"""
    now_dt = get_datetime()
    
    if frequency == "daily":
        return add_days(now_dt, 1)
    elif frequency == "weekly":
        return add_days(now_dt, 7)
    elif frequency == "monthly":
        return add_days(now_dt, 30)
    else:
        return add_days(now_dt, 7)  # Default to weekly

@frappe.whitelist()
def process_scheduled_reports():
    """Process all scheduled reports that are due"""
    try:
        # Get all scheduled reports that are due
        due_reports = frappe.get_all('Scheduled Email Report',
            filters={
                'enabled': 1,
                'next_send_date': ['<=', now()]
            },
            fields=['name', 'document_type', 'document_name', 'recipients', 'report_type']
        )
        
        processed_count = 0
        
        for report in due_reports:
            try:
                recipients = json.loads(report.recipients)
                
                if report.document_type == 'Poll':
                    result = send_poll_report(report.document_name, recipients, report.report_type)
                elif report.document_type == 'Survey':
                    result = send_survey_report(report.document_name, recipients, report.report_type)
                
                if result.get('success'):
                    # Update next send date
                    report_doc = frappe.get_doc('Scheduled Email Report', report.name)
                    report_doc.next_send_date = calculate_next_send_date(report_doc.frequency)
                    report_doc.last_sent_date = now()
                    report_doc.save(ignore_permissions=True)
                    
                    processed_count += 1
            
            except Exception as e:
                frappe.log_error(f"Scheduled report processing error for {report.name}: {str(e)}")
                continue
        
        return {'success': True, 'processed': processed_count}
    
    except Exception as e:
        frappe.log_error(f"Scheduled reports processing error: {str(e)}")
        return {'error': str(e)}
