# Copyright (c) 2025, Godwin Ariwodo and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_url, now
import uuid

class Survey(Document):
    def before_insert(self):
        if not self.shareable_link:
            self.shareable_link = self.generate_shareable_link()
    
    def generate_shareable_link(self):
        """Generate a unique shareable link for the survey"""
        unique_id = str(uuid.uuid4())[:8]
        base_url = get_url()
        return f"{base_url}/survey/{unique_id}"
    
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
        from frappe.utils import getdate
        
        timeline = defaultdict(int)
        unique_responses = set()
        
        for response in responses:
            response_id = f"{response.get('creation')}"
            if response_id not in unique_responses:
                unique_responses.add(response_id)
                date = getdate(response.creation)
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
        
        # Import get_datetime to convert string to datetime for comparison
        from frappe.utils import get_datetime
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
    

@frappe.whitelist(allow_guest=True)
def submit_survey_response(survey_id, responses, participant_info=None):
    """API endpoint to submit survey response"""
    try:
        frappe.log_error(f"Submit survey response called with survey_id: {survey_id}")
        frappe.log_error(f"Responses: {responses}")

        surveys = frappe.get_list('Survey',
            filters={'shareable_link': ['like', f'%{survey_id}%']},
            fields=['name'],
            limit=1,
            ignore_permissions=True
        )

        frappe.log_error(f"Found surveys: {surveys}")

        if not surveys:
            return {'error': 'Survey not found'}

        survey = frappe.get_doc('Survey', surveys[0].name)
        frappe.log_error(f"Survey status: {survey.status}")

        if survey.status != 'Active':
            return {'error': 'Survey is not active'}
        
        # Create survey responses
        for question_name, response_value in responses.items():
            frappe.log_error(f"Creating response for question: {question_name}, value: {response_value}")

            if isinstance(response_value, list):
                # Handle checkbox responses
                for value in response_value:
                    frappe.log_error(f"Creating checkbox response: {value}")
                    response_doc = frappe.get_doc({
                        'doctype': 'Survey Response',
                        'survey': survey.name,
                        'survey_question': question_name,
                        'response_value': str(value),
                        'participant_ip': frappe.local.request_ip if frappe.local.request_ip else '',
                        'participant_info': participant_info or {}
                    })
                    response_doc.insert(ignore_permissions=True)
            else:
                frappe.log_error(f"Creating single response: {response_value}")
                response_doc = frappe.get_doc({
                    'doctype': 'Survey Response',
                    'survey': survey.name,
                    'survey_question': question_name,
                    'response_value': str(response_value),
                    'participant_ip': frappe.local.request_ip if frappe.local.request_ip else '',
                    'participant_info': participant_info or {}
                })
                response_doc.insert(ignore_permissions=True)
        
        # Update survey total responses
        survey.update_total_responses()
        
        return {'success': True, 'message': 'Survey response submitted successfully'}
    
    except Exception as e:
        frappe.log_error(f"Survey response submission error: {str(e)}")
        return {'error': 'Failed to submit response'}


@frappe.whitelist()
def get_survey_analytics(survey_name):
    """API endpoint to get survey analytics"""
    try:
        survey = frappe.get_doc('Survey', survey_name)
        return survey.get_analytics_data()
    except Exception as e:
        return {'error': str(e)}
