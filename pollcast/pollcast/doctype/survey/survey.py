# Copyright (c) 2025, Godwin Ariwodo and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_url, now, get_datetime
import uuid

class Survey(Document):
       
    def validate(self):
        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                frappe.throw("End date must be after start date")
    
    def on_update(self):
        self.update_total_responses()
    
    def update_total_responses(self):
        """Update the total response count"""
        total = frappe.db.count('Survey Response', {'survey': self.name})
        frappe.db.set_value('Survey', self.name, 'total_responses', total)
    
    def get_analytics_data(self):
        """Get analytics data for the survey"""
        responses = frappe.get_all('Survey Response', 
            filters={'survey': self.name},
            fields=['survey_question', 'response_value', 'creation']
        )
        
        # Group responses by question
        question_responses = {}
        for response in responses:
            question = response.survey_question
            if question not in question_responses:
                question_responses[question] = []
            question_responses[question].append(response.response_value)
        
        # Analyze each question
        questions_data = []
        for question in self.questions:
            responses_for_question = question_responses.get(question.name, [])
            
            if question.question_type in ['Multiple Choice', 'Checkbox']:
                # Count option frequencies
                option_counts = {}
                for response in responses_for_question:
                    if response in option_counts:
                        option_counts[response] += 1
                    else:
                        option_counts[response] = 1
                
                questions_data.append({
                    'question': question.question_text,
                    'type': question.question_type,
                    'total_responses': len(responses_for_question),
                    'option_counts': option_counts
                })
            
            elif question.question_type == 'Rating Scale':
                # Calculate average rating
                ratings = [float(r) for r in responses_for_question if r.isdigit()]
                avg_rating = sum(ratings) / len(ratings) if ratings else 0
                
                questions_data.append({
                    'question': question.question_text,
                    'type': question.question_type,
                    'total_responses': len(responses_for_question),
                    'average_rating': round(avg_rating, 2),
                    'ratings_distribution': self.get_rating_distribution(ratings)
                })
            
            else:  # Text Input
                questions_data.append({
                    'question': question.question_text,
                    'type': question.question_type,
                    'total_responses': len(responses_for_question),
                    'responses': responses_for_question[:10]  # Show first 10 text responses
                })
        
        return {
            'total_responses': len(set([r.get('creation') for r in responses])),
            'questions': questions_data,
            'response_timeline': self.get_response_timeline(responses)
        }
    
    def get_rating_distribution(self, ratings):
        """Get distribution of ratings"""
        distribution = {str(i): 0 for i in range(1, 6)}  # 1-5 scale
        for rating in ratings:
            if str(int(rating)) in distribution:
                distribution[str(int(rating))] += 1
        return distribution
    
    def get_response_timeline(self, responses):
        """Get response timeline data for charts"""
        from collections import defaultdict
        from datetime import datetime

        timeline = defaultdict(int)
        unique_responses = set()

        for response in responses:
            response_id = f"{response.get('creation')}"
            if response_id not in unique_responses:
                unique_responses.add(response_id)
                # Convert datetime to date string directly
                if isinstance(response.creation, str):
                    date = datetime.fromisoformat(response.creation.replace('Z', '+00:00')).date()
                else:
                    date = response.creation.date() if hasattr(response.creation, 'date') else response.creation
                timeline[str(date)] += 1

        return dict(timeline)

@frappe.whitelist(allow_guest=True)
def get_survey_data(survey_id):
    """API endpoint to get survey data for public participation"""
    try:
        frappe.log_error(f"Looking for survey_id: {survey_id}")
        
        # Use frappe.get_list with ignore_permissions=True for guest access
        surveys = frappe.get_list('Survey', 
            filters={'shareable_link': ['like', f'%{survey_id}%']},
            fields=['name'],
            limit=1,
            ignore_permissions=True
        )
        
        if not surveys:
            return {'error': 'Survey not found'}
        
        survey = frappe.get_doc('Survey', surveys[0].name)
        frappe.log_error(f"Found survey: {survey.name}")
        
        if survey.status != 'Active':
            return {'error': 'Survey is not active'}
        
        current_time = get_datetime()
        
        # Check if survey is within date range
        if survey.start_date and current_time < get_datetime(survey.start_date):
            return {'error': 'Survey has not started yet'}
        
        if survey.end_date and current_time > get_datetime(survey.end_date):
            return {'error': 'Survey has ended'}
        
        questions_data = []
        for question in survey.questions:
            q_data = {
                'name': question.name,
                'text': question.question_text,
                'type': question.question_type,
                'required': question.required,
                'page_number': question.page_number or 1
            }
            
            if question.question_type in ['Multiple Choice', 'Checkbox']:
                q_data['options'] = [opt.strip() for opt in (question.options or '').split('\n') if opt.strip()]
            elif question.question_type == 'Rating Scale':
                q_data['scale_min'] = question.scale_min or 1
                q_data['scale_max'] = question.scale_max or 5
            
            questions_data.append(q_data)
        
        return {
            'survey': {
                'name': survey.name,
                'title': survey.title,
                'description': survey.description,
                'multi_page': survey.multi_page,
                'questions': questions_data
            }
        }
    except Exception as e:
        frappe.log_error(f"Survey data error: {str(e)}")
        return {'error': str(e)}
    

@frappe.whitelist(allow_guest=True, methods=["POST"])
def submit_survey_response(survey_id, responses, participant_info=None):
    """API endpoint to submit survey response"""
    try:
        # For guest users submitting public surveys, bypass CSRF
        if frappe.session.user == "Guest":
            frappe.flags.ignore_permissions = True
            # This is the key line to bypass CSRF for guests
            frappe.local.form_dict.csrf_token = frappe.session.data.csrf_token if frappe.session.data.get('csrf_token') else 'guest'
        
        frappe.log_error(f"=== SURVEY SUBMISSION DEBUG ===")
        frappe.log_error(f"Survey ID: {survey_id}")
        frappe.log_error(f"User: {frappe.session.user}")
        frappe.log_error(f"Responses type: {type(responses)}")
        frappe.log_error(
            title="Survey submission - Responses",
            message=f"Responses raw: {responses}"
        )


        # Validate required parameters
        if not survey_id:
            return {'error': 'Survey ID is required'}

        if not responses:
            return {'error': 'Responses are required'}

        # Parse responses if it's a string
        if isinstance(responses, str):
            import json
            try:
                responses = json.loads(responses)
            except json.JSONDecodeError as e:
                frappe.log_error(f"JSON parse error: {str(e)}")
                return {'error': 'Invalid responses format'}

        if not isinstance(responses, dict):
            return {'error': 'Responses must be a valid object'}

        # Parse participant_info if it's a string
        if isinstance(participant_info, str):
            import json
            try:
                participant_info = json.loads(participant_info)
            except:
                participant_info = {}

        # Find survey by shareable link
        surveys = frappe.get_list('Survey',
            filters=[['shareable_link', 'like', f'%/{survey_id}%']],
            fields=['name', 'shareable_link', 'status'],
            ignore_permissions=True
        )

        if not surveys:
            return {'error': f'Survey not found with ID: {survey_id}'}

        survey = frappe.get_doc('Survey', surveys[0].name)

        if survey.status != 'Active':
            return {'error': f'Survey is not active'}

        # Validate survey has questions
        if not survey.questions:
            return {'error': 'Survey has no questions'}

        # Build question map
        survey_questions = {q.name: q for q in survey.questions}

        # Create survey responses
        created_count = 0
        
        for question_name, response_value in responses.items():
            # Validate question exists
            if question_name not in survey_questions:
                continue

            # Skip empty responses
            if response_value is None or response_value == "" or (isinstance(response_value, list) and len(response_value) == 0):
                continue

            try:
                if isinstance(response_value, list):
                    # Handle checkbox/multiple responses
                    for value in response_value:
                        if value:
                            response_doc = frappe.get_doc({
                                'doctype': 'Survey Response',
                                'survey': survey.name,
                                'survey_question': question_name,
                                'response_value': str(value),
                                'participant_ip': frappe.local.request_ip if hasattr(frappe.local, 'request_ip') else '',
                                'participant_info': participant_info or {}
                            })
                            response_doc.insert(ignore_permissions=True)
                            created_count += 1
                else:
                    # Handle single value responses
                    response_doc = frappe.get_doc({
                        'doctype': 'Survey Response',
                        'survey': survey.name,
                        'survey_question': question_name,
                        'response_value': str(response_value),
                        'participant_ip': frappe.local.request_ip if hasattr(frappe.local, 'request_ip') else '',
                        'participant_info': participant_info or {}
                    })
                    response_doc.insert(ignore_permissions=True)
                    created_count += 1
            
            except Exception as e:
                frappe.log_error(f"Error creating response: {str(e)}")

        # Commit the transaction
        frappe.db.commit()

        # Update survey total responses
        survey.reload()
        survey.update_total_responses()
        frappe.db.commit()

        return {
            'success': True,
            'message': 'Survey response submitted successfully',
            'responses_created': created_count
        }

    except Exception as e:
        frappe.log_error(f"Survey submission error: {str(e)}")
        frappe.log_error(frappe.get_traceback())
        return {'error': f'Failed to submit response: {str(e)}'}    

@frappe.whitelist()
def get_survey_analytics(survey_name):
    """API endpoint to get survey analytics"""
    try:
        survey = frappe.get_doc('Survey', survey_name)
        return survey.get_analytics_data()
    except Exception as e:
        return {'error': str(e)}
