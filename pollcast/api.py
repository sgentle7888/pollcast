import frappe
from frappe import _
from frappe.utils import now, add_days, get_datetime
import json
from datetime import datetime, timedelta
import time
from frappe.utils.response import Response

@frappe.whitelist()
def get_dashboard_summary():
    """Get dashboard summary statistics"""
    try:
        # Get active polls and surveys count
        active_polls = frappe.db.count('Poll', {'status': 'Active'})
        active_surveys = frappe.db.count('Survey', {'status': 'Active'})
        
        # Get total responses
        total_poll_responses = frappe.db.count('Poll Response')
        total_survey_responses = frappe.db.count('Survey Response')
        total_responses = total_poll_responses + total_survey_responses
        
        # Calculate engagement rate (simplified)
        total_active = active_polls + active_surveys
        engagement_rate = round((total_responses / max(total_active, 1)) * 10, 1)  # Simplified calculation
        
        # Get weekly changes (sample data for now)
        week_ago = add_days(now(), -7)
        polls_change = frappe.db.count('Poll', {'creation': ['>=', week_ago]})
        surveys_change = frappe.db.count('Survey', {'creation': ['>=', week_ago]})
        
        # Get daily response changes
        today = get_datetime().date()
        responses_today = frappe.db.count('Poll Response', {'creation': ['>=', today]})
        responses_today += frappe.db.count('Survey Response', {'creation': ['>=', today]})
        
        return {
            'activePolls': active_polls,
            'activeSurveys': active_surveys,
            'totalResponses': total_responses,
            'engagementRate': engagement_rate,
            'pollsChange': polls_change,
            'surveysChange': surveys_change,
            'responsesChange': responses_today,
            'engagementTrend': 2.5  # Sample trend data
        }
    
    except Exception as e:
        frappe.log_error(f"Dashboard summary error: {str(e)}")
        return {'error': str(e)}

@frappe.whitelist()
def get_polls_analytics():
    """Get detailed analytics for all active polls"""
    try:
        polls = frappe.get_all('Poll', 
            filters={'status': 'Active'}, 
            fields=['name', 'title', 'total_responses']
        )
        
        polls_data = []
        for poll in polls:
            poll_doc = frappe.get_doc('Poll', poll.name)
            analytics = poll_doc.get_analytics_data()
            
            polls_data.append({
                'name': poll.name,
                'title': poll.title,
                'total_responses': analytics['total_responses'],
                'engagement_rate': calculate_engagement_rate(poll.name, 'Poll'),
                'options': analytics['options'],
                'response_timeline': analytics['response_timeline']
            })
        
        # Sort by total responses
        polls_data.sort(key=lambda x: x['total_responses'], reverse=True)
        
        return polls_data
    
    except Exception as e:
        frappe.log_error(f"Polls analytics error: {str(e)}")
        return {'error': str(e)}

@frappe.whitelist()
def get_surveys_analytics():
    """Get detailed analytics for all active surveys"""
    try:
        surveys = frappe.get_all('Survey', 
            filters={'status': 'Active'}, 
            fields=['name', 'title', 'total_responses']
        )
        
        surveys_data = []
        for survey in surveys:
            survey_doc = frappe.get_doc('Survey', survey.name)
            analytics = survey_doc.get_analytics_data()
            
            surveys_data.append({
                'name': survey.name,
                'title': survey.title,
                'total_responses': analytics['total_responses'],
                'completion_rate': calculate_completion_rate(survey.name),
                'questions': analytics['questions'][:5],  # Limit to first 5 questions for dashboard
                'response_timeline': analytics['response_timeline']
            })
        
        # Sort by total responses
        surveys_data.sort(key=lambda x: x['total_responses'], reverse=True)
        
        return surveys_data
    
    except Exception as e:
        frappe.log_error(f"Surveys analytics error: {str(e)}")
        return {'error': str(e)}

def calculate_engagement_rate(doc_name, doc_type):
    """Calculate engagement rate for a poll or survey"""
    try:
        if doc_type == 'Poll':
            # Simple engagement calculation based on responses vs time active
            doc = frappe.get_doc('Poll', doc_name)
            days_active = (get_datetime() - get_datetime(doc.creation)).days or 1
            return round((doc.total_responses / days_active) * 10, 1)
        else:
            # Survey engagement calculation
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

@frappe.whitelist()
def export_analytics():
    """Export analytics data in various formats"""
    try:
        # Get request data
        data = json.loads(frappe.request.data)
        options = data.get('options', {})
        format_type = data.get('format', 'csv')
        
        export_data = {}
        
        if options.get('polls'):
            export_data['polls'] = get_polls_analytics()
        
        if options.get('surveys'):
            export_data['surveys'] = get_surveys_analytics()
        
        if options.get('responses'):
            export_data['responses'] = get_response_details()
        
        if options.get('analytics'):
            export_data['summary'] = get_dashboard_summary()
        
        if format_type == 'csv':
            return generate_csv_export(export_data)
        elif format_type == 'excel':
            return generate_excel_export(export_data)
        elif format_type == 'pdf':
            return generate_pdf_export(export_data)
        
    except Exception as e:
        frappe.log_error(f"Export error: {str(e)}")
        frappe.throw(_("Export failed: {0}").format(str(e)))

def get_response_details():
    """Get detailed response data"""
    try:
        # Get poll responses
        poll_responses = frappe.db.sql("""
            SELECT 
                pr.creation,
                p.title as poll_title,
                po.option_text,
                pr.participant_ip
            FROM `tabPoll Response` pr
            JOIN `tabPoll` p ON pr.poll = p.name
            JOIN `tabPoll Option` po ON pr.poll_option = po.name
            ORDER BY pr.creation DESC
            LIMIT 1000
        """, as_dict=True)
        
        # Get survey responses
        survey_responses = frappe.db.sql("""
            SELECT 
                sr.creation,
                s.title as survey_title,
                sq.question_text,
                sr.response_value,
                sr.participant_ip
            FROM `tabSurvey Response` sr
            JOIN `tabSurvey` s ON sr.survey = s.name
            JOIN `tabSurvey Question` sq ON sr.survey_question = sq.name
            ORDER BY sr.creation DESC
            LIMIT 1000
        """, as_dict=True)
        
        return {
            'poll_responses': poll_responses,
            'survey_responses': survey_responses
        }
    
    except Exception as e:
        frappe.log_error(f"Response details error: {str(e)}")
        return {}

def generate_csv_export(data):
    """Generate CSV export"""
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write summary
    if 'summary' in data:
        writer.writerow(['=== SUMMARY ==='])
        summary = data['summary']
        for key, value in summary.items():
            writer.writerow([key.replace('_', ' ').title(), value])
        writer.writerow([])
    
    # Write polls data
    if 'polls' in data:
        writer.writerow(['=== POLLS ==='])
        writer.writerow(['Title', 'Total Responses', 'Engagement Rate'])
        for poll in data['polls']:
            writer.writerow([poll['title'], poll['total_responses'], poll['engagement_rate']])
        writer.writerow([])
    
    # Write surveys data
    if 'surveys' in data:
        writer.writerow(['=== SURVEYS ==='])
        writer.writerow(['Title', 'Total Responses', 'Completion Rate'])
        for survey in data['surveys']:
            writer.writerow([survey['title'], survey['total_responses'], survey['completion_rate']])
        writer.writerow([])
    
    csv_content = output.getvalue()
    output.close()
    
    # Return as file response
    frappe.local.response.filename = f"pollcast_analytics_{now().split()[0]}.csv"
    frappe.local.response.filecontent = csv_content
    frappe.local.response.type = "download"

def generate_excel_export(data):
    """Generate Excel export (simplified - would need openpyxl in real implementation)"""
    # For now, return CSV format
    return generate_csv_export(data)

def generate_pdf_export(data):
    """Generate PDF export (simplified - would need reportlab in real implementation)"""
    # For now, return CSV format
    return generate_csv_export(data)

@frappe.whitelist()
def sse_analytics():
    """Server-Sent Events endpoint for real-time analytics"""
    
    def event_stream():
        # This inner function is a generator that will keep running
        while True:
            try:
                # 1. Get the latest summary data
                summary_data = get_dashboard_summary()
                
                event_data = {
                    'type': 'summary_update',
                    'summary': summary_data,
                    'timestamp': now()
                }
                
                # 2. Yield the data in the required SSE format
                yield f"data: {json.dumps(event_data)}\n\n"
                
                # 3. Wait for 5 seconds before sending the next update
                time.sleep(5)

            except Exception as e:
                # If an error occurs, send an error event and break the loop
                frappe.log_error(f"SSE loop error: {str(e)}")
                error_data = {'error': 'An error occurred in the SSE stream.'}
                yield f"data: {json.dumps(error_data)}\n\n"
                break

    # Return a streaming Response object, passing the generator to it.
    # This tells Frappe to keep the connection open.
    return Response(event_stream(), mimetype='text/event-stream')
