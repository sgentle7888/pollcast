import frappe
from frappe.utils import now, add_days, get_datetime
from datetime import datetime, timedelta
import csv
import io

def update_analytics():
    """Hourly task to update analytics data"""
    try:
        # Update poll response counts
        polls = frappe.get_all('Poll', filters={'status': 'Active'})
        for poll in polls:
            poll_doc = frappe.get_doc('Poll', poll.name)
            poll_doc.update_total_responses()
        
        # Update survey response counts
        surveys = frappe.get_all('Survey', filters={'status': 'Active'})
        for survey in surveys:
            survey_doc = frappe.get_doc('Survey', survey.name)
            survey_doc.update_total_responses()
        
        frappe.db.commit()
        
    except Exception as e:
        frappe.log_error(f"Analytics update error: {str(e)}")

def auto_export_data():
    """Daily task to auto-export data"""
    try:
        # Export active polls data
        active_polls = frappe.get_all('Poll', filters={'status': 'Active'})
        
        for poll in active_polls:
            poll_doc = frappe.get_doc('Poll', poll.name)
            analytics_data = poll_doc.get_analytics_data()
            
            # Create CSV export
            csv_data = create_poll_csv_export(poll_doc, analytics_data)
            
            # Save to file or send email (implement based on requirements)
            file_name = f"poll_export_{poll.name}_{now().strftime('%Y%m%d')}.csv"
            
            # Create File document
            file_doc = frappe.get_doc({
                'doctype': 'File',
                'file_name': file_name,
                'content': csv_data,
                'is_private': 1,
                'folder': 'Home/Pollcast Exports'
            })
            file_doc.insert()
        
        frappe.db.commit()
        
    except Exception as e:
        frappe.log_error(f"Auto export error: {str(e)}")

def cleanup_old_data():
    """Daily task to cleanup old data"""
    try:
        # Archive polls older than 90 days
        cutoff_date = add_days(now(), -90)
        
        old_polls = frappe.get_all('Poll', 
            filters={
                'status': 'Closed',
                'end_date': ['<', cutoff_date]
            }
        )
        
        for poll in old_polls:
            frappe.db.set_value('Poll', poll.name, 'status', 'Archived')
        
        # Similar cleanup for surveys
        old_surveys = frappe.get_all('Survey', 
            filters={
                'status': 'Closed',
                'end_date': ['<', cutoff_date]
            }
        )
        
        for survey in old_surveys:
            frappe.db.set_value('Survey', survey.name, 'status', 'Archived')
        
        frappe.db.commit()
        
    except Exception as e:
        frappe.log_error(f"Cleanup error: {str(e)}")

def send_weekly_reports():
    """Weekly task to send email reports"""
    try:
        # Get all active polls and surveys
        active_polls = frappe.get_all('Poll', filters={'status': 'Active'})
        active_surveys = frappe.get_all('Survey', filters={'status': 'Active'})
        
        # Generate weekly report
        report_data = {
            'week_start': add_days(now(), -7),
            'week_end': now(),
            'polls': [],
            'surveys': []
        }
        
        for poll in active_polls:
            poll_doc = frappe.get_doc('Poll', poll.name)
            analytics = poll_doc.get_analytics_data()
            report_data['polls'].append({
                'title': poll_doc.title,
                'total_responses': analytics['total_responses'],
                'analytics': analytics
            })
        
        for survey in active_surveys:
            survey_doc = frappe.get_doc('Survey', survey.name)
            analytics = survey_doc.get_analytics_data()
            report_data['surveys'].append({
                'title': survey_doc.title,
                'total_responses': analytics['total_responses'],
                'analytics': analytics
            })
        
        # Send email report (implement email template)
        send_weekly_email_report(report_data)
        
    except Exception as e:
        frappe.log_error(f"Weekly report error: {str(e)}")

def create_poll_csv_export(poll_doc, analytics_data):
    """Create CSV export for poll data"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write headers
    writer.writerow(['Poll Title', poll_doc.title])
    writer.writerow(['Total Responses', analytics_data['total_responses']])
    writer.writerow(['Export Date', now()])
    writer.writerow([])  # Empty row
    
    # Write options data
    writer.writerow(['Option', 'Count', 'Percentage'])
    for option in analytics_data['options']:
        writer.writerow([option['option'], option['count'], f"{option['percentage']}%"])
    
    return output.getvalue()

def send_weekly_email_report(report_data):
    """Send weekly email report"""
    # This would implement the actual email sending
    # For now, just log the report generation
    frappe.log_error(f"Weekly report generated: {len(report_data['polls'])} polls, {len(report_data['surveys'])} surveys")
