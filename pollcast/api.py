import frappe
from frappe import _
from frappe.utils import now, add_days, get_datetime
import json
from datetime import datetime, timedelta
import time
from frappe.utils.response import Response
from collections import defaultdict

@frappe.whitelist(allow_guest=True)
def get_user_info():
    """Get basic info + roles for the logged-in user, used by the portal auth store.
    Returns safe guest defaults when called by an unauthenticated user.
    """
    try:
        user = frappe.session.user
        if user == 'Guest':
            return {
                'name': 'Guest',
                'email': '',
                'full_name': 'Guest',
                'user_image': None,
                'roles': [],
                'is_poll_manager': False,
                'is_guest': True
            }
        user_doc = frappe.get_doc('User', user)
        roles = frappe.get_roles(user)

        return {
            'name': user_doc.name,
            'email': user_doc.email,
            'full_name': user_doc.full_name,
            'user_image': user_doc.user_image,
            'roles': roles,
            'is_poll_manager': 'Poll Manager' in roles or 'System Manager' in roles,
            'is_guest': False
        }
    except Exception as e:
        frappe.log_error(f"Get user info error: {str(e)}")
        return {'error': str(e)}

@frappe.whitelist()
def get_polls():
    """List polls for the portal dashboard/list views"""
    try:
        polls = frappe.get_list('Poll',
            fields=['name', 'title', 'description', 'status', 'start_date',
                    'end_date', 'total_responses', 'shareable_link', 'modified'],
            order_by='modified desc',
            limit_page_length=0
        )
        return polls
    except Exception as e:
        frappe.log_error(f"Get polls error: {str(e)}")
        return {'error': str(e)}

@frappe.whitelist()
def get_surveys():
    """List surveys for the portal dashboard/list views"""
    try:
        surveys = frappe.get_list('Survey',
            fields=['name', 'title', 'description', 'status', 'start_date',
                    'end_date', 'total_responses', 'multi_page', 'modified'],
            order_by='modified desc',
            limit_page_length=0
        )
        return surveys
    except Exception as e:
        frappe.log_error(f"Get surveys error: {str(e)}")
        return {'error': str(e)}

@frappe.whitelist(allow_guest=True)
def get_poll(poll_name):
    """Get a single poll with its questions/options for the PollVote page"""
    try:
        if not poll_name:
            return {'error': 'Poll name is required'}

        if not frappe.db.exists('Poll', poll_name):
            return {'error': 'Poll not found'}

        poll = frappe.get_doc('Poll', poll_name)

        if poll.status != 'Active':
            return {'error': 'Poll is not active'}

        questions = []
        for q in poll.questions:
            q_data = {
                'name': q.name,
                'question_text': q.question_text,
                'question_type': q.question_type,
            }
            if q.options:
                q_data['options'] = [
                    opt.strip() for opt in q.options.split('\n') if opt.strip()
                ]
            questions.append(q_data)

        return {
            'name': poll.name,
            'title': poll.title,
            'description': poll.description,
            'status': poll.status,
            'questions': questions,
        }
    except Exception as e:
        frappe.log_error(f"Get poll error: {str(e)}")
        return {'error': str(e)}


@frappe.whitelist(allow_guest=True)
def get_survey(survey_name):
    """Get a single survey document including questions for the Take/Results pages"""
    try:
        if not survey_name:
            return {'error': 'Survey name is required'}

        if not frappe.db.exists('Survey', survey_name):
            return {'error': 'Survey not found'}

        survey = frappe.get_doc('Survey', survey_name)

        questions = []
        for q in survey.questions:
            q_data = {
                'name': q.name,
                'question_text': q.question_text,
                'question_type': q.question_type,
                'required': q.required,
                'page_number': q.page_number or 1,
            }
            if q.question_type in ['Multiple Choice', 'Checkbox']:
                q_data['options'] = [
                    opt.strip() for opt in (q.options or '').split('\n') if opt.strip()
                ]
            elif q.question_type == 'Rating Scale':
                q_data['scale_min'] = q.scale_min or 1
                q_data['scale_max'] = q.scale_max or 5
            questions.append(q_data)

        return {
            'name': survey.name,
            'title': survey.title,
            'description': survey.description,
            'status': survey.status,
            'multi_page': survey.multi_page,
            'start_date': str(survey.start_date) if survey.start_date else None,
            'end_date': str(survey.end_date) if survey.end_date else None,
            'total_responses': survey.total_responses,
            'questions': questions,
        }
    except Exception as e:
        frappe.log_error(f"Get survey error: {str(e)}")
        return {'error': str(e)}

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
def get_polls_dashboard_summary():
    """Get poll-specific dashboard summary statistics"""
    try:
        # Get active polls count
        active_polls = frappe.db.count('Poll', {'status': 'Active'})

        # Get total poll responses
        total_poll_responses = frappe.db.count('Poll Response')

        # Calculate poll engagement rate
        engagement_rate = round((total_poll_responses / max(active_polls, 1)) * 10, 1)

        # Get weekly changes for polls
        week_ago = add_days(now(), -7)
        polls_change = frappe.db.count('Poll', {'creation': ['>=', week_ago]})

        # Get daily poll response changes
        today = get_datetime().date()
        poll_responses_today = frappe.db.count('Poll Response', {'creation': ['>=', today]})

        # Get top performing poll
        top_poll = frappe.db.sql("""
            SELECT p.title, p.total_responses
            FROM `tabPoll` p
            WHERE p.status = 'Active'
            ORDER BY p.total_responses DESC
            LIMIT 1
        """, as_dict=True)

        return {
            'activePolls': active_polls,
            'totalPollResponses': total_poll_responses,
            'pollEngagementRate': engagement_rate,
            'topPollTitle': top_poll[0].title if top_poll else 'N/A',
            'topPollResponses': top_poll[0].total_responses if top_poll else 0,
            'pollsChange': polls_change,
            'pollResponsesChange': poll_responses_today,
            'pollEngagementTrend': 2.5  # Sample trend data
        }

    except Exception as e:
        frappe.log_error(f"Polls dashboard summary error: {str(e)}")
        return {'error': str(e)}

@frappe.whitelist()
def get_poll_analytics(poll_id):
    """Get detailed analytics for a specific poll"""
    try:
        if not poll_id:
            return {'error': 'Poll ID is required'}

        # Get poll details
        poll = frappe.get_doc('Poll', poll_id)
        if not poll:
            return {'error': 'Poll not found'}

        # Get poll responses
        poll_responses = frappe.get_all('Poll Response',
            filters={'poll': poll_id},
            fields=['poll_option', 'participant_ip', 'creation']
        )

        if not poll_responses:
            return {
                'poll': {
                    'name': poll.name,
                    'title': poll.title,
                    'total_votes': 0,
                    'unique_voters': 0,
                    'participation_rate': 0,
                    'peak_voting_time': None
                },
                'vote_distribution': [],
                'rankings': [],
                'timeline': []
            }

        # Calculate unique voters
        unique_ips = set(response.participant_ip for response in poll_responses if response.participant_ip)
        unique_voters = len(unique_ips)

        # Calculate participation rate (simplified)
        expected = getattr(poll, 'expected_responses', None) or 100
        participation_rate = min((unique_voters / max(expected, 1)) * 100, 100)

        # Get vote distribution by option
        option_votes = {}
        for response in poll_responses:
            option_id = response.poll_option
            if option_id not in option_votes:
                option_votes[option_id] = 0
            option_votes[option_id] += 1

        # Get option details and create distribution
        vote_distribution = []
        for option_id, vote_count in option_votes.items():
            option = frappe.get_doc('Poll Option', option_id, ignore_permissions=True)
            percentage = (vote_count / len(poll_responses)) * 100
            vote_distribution.append({
                'option_id': option_id,
                'option_text': option.option_text,
                'vote_count': vote_count,
                'percentage': round(percentage, 1)
            })

        # Sort by vote count (highest first)
        vote_distribution.sort(key=lambda x: x['vote_count'], reverse=True)

        # Create rankings
        rankings = []
        for i, item in enumerate(vote_distribution, 1):
            rankings.append({
                'rank': i,
                'option_text': item['option_text'],
                'vote_count': item['vote_count'],
                'percentage': item['percentage'],
                'is_winner': i == 1  # First place is the winner
            })

        # Generate timeline data (daily vote accumulation)
        timeline = generate_poll_timeline(poll_responses)

        # Find peak voting time
        peak_voting_time = find_peak_voting_time(poll_responses)

        return {
            'poll': {
                'name': poll.name,
                'title': poll.title,
                'total_votes': len(poll_responses),
                'unique_voters': unique_voters,
                'participation_rate': round(participation_rate, 1),
                'peak_voting_time': peak_voting_time,
                'status': poll.status
            },
            'vote_distribution': vote_distribution,
            'rankings': rankings,
            'timeline': timeline
        }

    except Exception as e:
        frappe.log_error(f"Poll analytics error: {str(e)}")
        return {'error': str(e)}

@frappe.whitelist()
def get_surveys_dashboard_summary():
    """Get survey-specific dashboard summary statistics"""
    try:
        # Get active surveys count
        active_surveys = frappe.db.count('Survey', {'status': 'Active'})

        # Get total survey responses
        total_survey_responses = frappe.db.count('Survey Response')

        # Calculate average completion rate
        avg_completion_rate = calculate_avg_completion_rate()

        # Calculate average rating
        avg_rating = calculate_avg_rating()

        # Get weekly changes for surveys
        week_ago = add_days(now(), -7)
        surveys_change = frappe.db.count('Survey', {'creation': ['>=', week_ago]})

        # Get daily survey response changes
        today = get_datetime().date()
        survey_responses_today = frappe.db.count('Survey Response', {'creation': ['>=', today]})

        return {
            'activeSurveys': active_surveys,
            'totalSurveyResponses': total_survey_responses,
            'avgCompletionRate': avg_completion_rate,
            'avgRating': avg_rating,
            'totalRatings': get_total_ratings_count(),
            'surveysChange': surveys_change,
            'surveyResponsesChange': survey_responses_today,
            'completionTrend': 1.2  # Sample trend data
        }

    except Exception as e:
        frappe.log_error(f"Surveys dashboard summary error: {str(e)}")
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

        # Get all responses for the survey to identify unique submissions by creation timestamp
        responses = frappe.get_all('Survey Response',
            filters={'survey': survey_name},
            fields=['creation', 'survey_question']
        )

        if not responses:
            return 0

        # Group answered questions by unique submission (identified by creation timestamp)
        submissions = {}
        for r in responses:
            # Use creation timestamp as a key for a single submission
            submission_key = r.creation
            if submission_key not in submissions:
                submissions[submission_key] = set()
            submissions[submission_key].add(r.survey_question)

        if not submissions:
            return 0

        num_submissions = len(submissions)
        # Sum the number of unique questions answered in each submission
        total_questions_answered = sum(len(questions_set) for questions_set in submissions.values())

        # Calculate the average number of questions answered per submission
        avg_questions_answered = total_questions_answered / num_submissions

        completion_rate = (avg_questions_answered / total_questions) * 100
        # Ensure completion rate does not exceed 100%
        return round(min(completion_rate, 100.0), 1)

    except Exception as e:
        frappe.log_error(f"Error calculating completion rate for {survey_name}: {str(e)}")
        return 0

def calculate_avg_completion_rate():
    """Calculate average completion rate across all surveys"""
    try:
        surveys = frappe.get_all('Survey', filters={'status': 'Active'}, fields=['name'])
        if not surveys:
            return 0

        total_completion = 0
        for survey in surveys:
            total_completion += calculate_completion_rate(survey.name)

        return round(total_completion / len(surveys), 1)
    except:
        return 0

def calculate_avg_rating():
    """Calculate average rating across all surveys"""
    try:
        # Get all rating responses
        rating_responses = frappe.db.sql("""
            SELECT sr.response_value
            FROM `tabSurvey Response` sr
            JOIN `tabSurvey Question` sq ON sr.survey_question = sq.name
            WHERE sq.question_type = 'Rating Scale'
            AND sr.response_value REGEXP '^[0-9]+$'
        """, as_list=True)

        if not rating_responses:
            return 0

        total_ratings = sum(int(rating[0]) for rating in rating_responses)
        return round(total_ratings / len(rating_responses), 1)
    except:
        return 0

def get_total_ratings_count():
    """Get total number of ratings across all surveys"""
    try:
        return frappe.db.sql("""
            SELECT COUNT(*)
            FROM `tabSurvey Response` sr
            JOIN `tabSurvey Question` sq ON sr.survey_question = sq.name
            WHERE sq.question_type = 'Rating Scale'
        """)[0][0]
    except:
        return 0

def generate_poll_timeline(poll_responses):
    """Generate timeline data for poll responses"""
    try:
        from collections import defaultdict

        # Group responses by date
        daily_votes = defaultdict(int)
        for response in poll_responses:
            date = response.creation.date() if hasattr(response.creation, 'date') else response.creation
            daily_votes[str(date)] = daily_votes[str(date)] + 1

        # Convert to sorted timeline
        timeline = []
        for date_str in sorted(daily_votes.keys()):
            timeline.append({
                'date': date_str,
                'votes': daily_votes[date_str]
            })

        return timeline
    except:
        return []

def find_peak_voting_time(poll_responses):
    """Find the date/time with peak voting activity"""
    try:
        if not poll_responses:
            return None

        # Group by date
        daily_votes = defaultdict(int)
        for response in poll_responses:
            date = response.creation.date() if hasattr(response.creation, 'date') else response.creation
            daily_votes[date] = daily_votes[date] + 1

        # Find date with maximum votes
        peak_date = max(daily_votes, key=daily_votes.get)
        return {
            'date': str(peak_date),
            'votes': daily_votes[peak_date]
        }
    except:
        return None

@frappe.whitelist()
def get_survey_analytics(survey_id):
    """Get detailed analytics for a specific survey"""
    try:
        if not survey_id:
            return {'error': 'Survey ID is required'}

        # Get survey details
        survey = frappe.get_doc('Survey', survey_id)
        if not survey:
            return {'error': 'Survey not found'}

        # Get survey responses
        survey_responses = frappe.get_all('Survey Response',
            filters={'survey': survey_id},
            fields=['survey_question', 'response_value', 'participant_ip', 'creation']
        )

        if not survey_responses:
            return {
                'survey': {
                    'name': survey.name,
                    'title': survey.title,
                    'total_responses': 0,
                    'unique_respondents': 0,
                    'completion_rate': 0,
                    'avg_completion_time': None
                },
                'question_analytics': [],
                'response_timeline': [],
                'text_analysis': {}
            }

        # Calculate unique respondents
        unique_ips = set(response.participant_ip for response in survey_responses if response.participant_ip)
        unique_respondents = len(unique_ips)

        # Calculate completion rate
        completion_rate = calculate_completion_rate(survey_id)

        # Group responses by question for analysis
        question_responses = defaultdict(list)
        for response in survey_responses:
            question_responses[response.survey_question].append(response.response_value)

        # Analyze each question
        question_analytics = []
        for question in survey.questions:
            responses_for_question = question_responses.get(question.name, [])

            question_data = {
                'question_id': question.name,
                'question_text': question.question_text,
                'question_type': question.question_type,
                'total_responses': len(responses_for_question),
                'required': question.required
            }

            if question.question_type in ['Multiple Choice', 'Checkbox']:
                # Count option frequencies
                option_counts = {}
                for response in responses_for_question:
                    if response in option_counts:
                        option_counts[response] += 1
                    else:
                        option_counts[response] = 1

                question_data['option_counts'] = option_counts
                question_data['most_popular_option'] = max(option_counts, key=option_counts.get) if option_counts else None

            elif question.question_type == 'Rating Scale':
                # Calculate rating statistics — handle int and decimal strings, skip N/A
                ratings = []
                for r in responses_for_question:
                    try:
                        val = float(r)
                        ratings.append(val)
                    except (ValueError, TypeError):
                        pass  # Skip N/A and non-numeric
                avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else 0
                question_data['average_rating'] = avg_rating
                question_data['rating_distribution'] = get_rating_distribution(ratings)
                if ratings:
                    question_data['highest_rating'] = max(ratings)
                    question_data['lowest_rating'] = min(ratings)

            elif question.question_type == 'Text Input':
                # Text analysis
                text_responses = [r for r in responses_for_question if r]
                if text_responses:
                    question_data['text_responses'] = text_responses[:10]  # Show first 10
                    question_data['word_frequency'] = analyze_text_frequency(text_responses)
                    question_data['sentiment_summary'] = analyze_sentiment(text_responses)

            question_analytics.append(question_data)

        # Generate response timeline
        response_timeline = generate_survey_timeline(survey_responses)

        # Calculate average completion time (simplified)
        avg_completion_time = calculate_avg_completion_time(survey_responses, survey)

        return {
            'survey': {
                'name': survey.name,
                'title': survey.title,
                'total_responses': len(survey_responses),
                'unique_respondents': unique_respondents,
                'completion_rate': completion_rate,
                'avg_completion_time': avg_completion_time,
                'status': survey.status
            },
            'question_analytics': question_analytics,
            'response_timeline': response_timeline,
            'text_analysis': {
                'total_text_responses': sum(1 for q in question_analytics if q['question_type'] == 'Text Input'),
                'sentiment_overview': get_overall_sentiment(question_analytics)
            }
        }

    except Exception as e:
        frappe.log_error(f"Survey analytics error: {str(e)}")
        return {'error': str(e)}

def generate_survey_timeline(survey_responses):
    """Generate timeline data for survey responses"""
    try:
        from collections import defaultdict

        # Group responses by date
        daily_responses = defaultdict(int)
        for response in survey_responses:
            date = response.creation.date() if hasattr(response.creation, 'date') else response.creation
            daily_responses[str(date)] = daily_responses[str(date)] + 1

        # Convert to sorted timeline
        timeline = []
        for date_str in sorted(daily_responses.keys()):
            timeline.append({
                'date': date_str,
                'responses': daily_responses[date_str]
            })

        return timeline
    except:
        return []

def get_rating_distribution(ratings):
    """Get distribution of ratings (1-5 scale)"""
    try:
        distribution = {str(i): 0 for i in range(1, 6)}
        for rating in ratings:
            rating_int = int(round(rating))
            if str(rating_int) in distribution:
                distribution[str(rating_int)] += 1
        return distribution
    except:
        return {str(i): 0 for i in range(1, 6)}

def analyze_text_frequency(text_responses):
    """Analyze word frequency in text responses"""
    try:
        from collections import Counter
        import re

        # Combine all text responses
        all_text = ' '.join(text_responses).lower()

        # Extract words (simple tokenization)
        words = re.findall(r'\b\w+\b', all_text)

        # Get most common words (excluding common stop words)
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        filtered_words = [word for word in words if word not in stop_words and len(word) > 2]

        # Get top 10 most frequent words
        word_freq = Counter(filtered_words).most_common(10)

        return {word: count for word, count in word_freq}
    except:
        return {}

def analyze_sentiment(text_responses):
    """Simple sentiment analysis for text responses"""
    try:
        # Simple keyword-based sentiment analysis
        positive_words = {'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'like', 'best', 'awesome', 'perfect', 'happy', 'satisfied', 'pleased', 'impressed'}
        negative_words = {'bad', 'terrible', 'awful', 'hate', 'worst', 'horrible', 'disappointing', 'poor', 'angry', 'frustrated', 'unhappy', 'dissatisfied', 'annoying'}

        positive_count = 0
        negative_count = 0

        all_text = ' '.join(text_responses).lower()

        for word in positive_words:
            positive_count += all_text.count(word)

        for word in negative_words:
            negative_count += all_text.count(word)

        total_sentiment_words = positive_count + negative_count

        if total_sentiment_words == 0:
            return {'sentiment': 'neutral', 'confidence': 0}

        if positive_count > negative_count:
            sentiment = 'positive'
            confidence = positive_count / total_sentiment_words
        elif negative_count > positive_count:
            sentiment = 'negative'
            confidence = negative_count / total_sentiment_words
        else:
            sentiment = 'neutral'
            confidence = 0

        return {
            'sentiment': sentiment,
            'confidence': round(confidence, 2),
            'positive_words': positive_count,
            'negative_words': negative_count
        }
    except:
        return {'sentiment': 'neutral', 'confidence': 0}

def get_overall_sentiment(question_analytics):
    """Get overall sentiment across all text questions"""
    try:
        sentiments = []
        for question in question_analytics:
            if question['question_type'] == 'Text Input' and 'sentiment_summary' in question:
                sentiment_info = question['sentiment_summary']
                if sentiment_info['sentiment'] != 'neutral':
                    sentiments.append(sentiment_info)

        if not sentiments:
            return {'overall': 'neutral', 'breakdown': {}}

        # Simple majority vote for overall sentiment
        positive_count = sum(1 for s in sentiments if s['sentiment'] == 'positive')
        negative_count = sum(1 for s in sentiments if s['sentiment'] == 'negative')

        if positive_count > negative_count:
            overall = 'positive'
        elif negative_count > positive_count:
            overall = 'negative'
        else:
            overall = 'neutral'

        return {
            'overall': overall,
            'positive_questions': positive_count,
            'negative_questions': negative_count,
            'total_sentiment_questions': len(sentiments)
        }
    except:
        return {'overall': 'neutral', 'breakdown': {}}

def calculate_avg_completion_time(survey_responses, survey):
    """Calculate average completion time for survey"""
    try:
        # This is a simplified calculation
        # In a real implementation, you'd track start/end times per user
        if not survey_responses:
            return None

        # For now, return a sample average time in minutes
        # In production, you'd want to track actual completion times
        return round(len(survey.questions) * 0.5, 1)  # Assume 30 seconds per question
    except:
        return None
    
@frappe.whitelist()
def export_analytics(options=None, format='csv'):
    """Export analytics data in various formats.
    Returns a JSON-safe object with base64-encoded file content so the
    Vue frontend can trigger a browser download without JSON.parse errors.
    """
    try:
        if isinstance(options, str):
            options = json.loads(options)
        options = options or {}
        format_type = format

        export_data = {}

        if options.get('polls'):
            export_data['polls'] = get_polls_analytics()

        if options.get('surveys'):
            export_data['surveys'] = get_surveys_analytics()

        if options.get('responses'):
            export_data['responses'] = get_response_details()

        if options.get('analytics'):
            export_data['summary'] = get_dashboard_summary()

        csv_content = build_csv_string(export_data)

        import base64
        filename = f"pollcast_analytics_{now().split()[0]}.csv"
        encoded = base64.b64encode(csv_content.encode('utf-8')).decode('ascii')
        return {
            'success': True,
            'filename': filename,
            'content': encoded,
            'mime': 'text/csv',
        }

    except Exception as e:
        frappe.log_error(f"Export error: {str(e)}")
        return {'error': str(e)}


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

def build_csv_string(data):
    """Build a CSV string from analytics data and return it."""
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
        for poll in (data['polls'] or []):
            writer.writerow([poll.get('title', ''), poll.get('total_responses', 0), poll.get('engagement_rate', 0)])
        writer.writerow([])

    # Write surveys data
    if 'surveys' in data:
        writer.writerow(['=== SURVEYS ==='])
        writer.writerow(['Title', 'Total Responses', 'Completion Rate'])
        for survey in (data['surveys'] or []):
            writer.writerow([survey.get('title', ''), survey.get('total_responses', 0), survey.get('completion_rate', 0)])
        writer.writerow([])

    csv_content = output.getvalue()
    output.close()
    return csv_content


# Keep old helpers as no-ops to avoid breaking any existing callers
def generate_csv_export(data):
    return build_csv_string(data)

def generate_excel_export(data):
    return build_csv_string(data)

def generate_pdf_export(data):
    return build_csv_string(data)

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

@frappe.whitelist()
def sse_polls_analytics():
    """Server-Sent Events endpoint for real-time polls analytics"""

    def event_stream():
        while True:
            try:
                # Get the latest polls summary data
                summary_data = get_polls_dashboard_summary()

                # Get latest polls data
                polls_data = get_polls_analytics()

                event_data = {
                    'type': 'summary_update',
                    'summary': summary_data,
                    'polls': polls_data[:5],  # Send only top 5 for real-time updates
                    'timestamp': now()
                }

                yield f"data: {json.dumps(event_data)}\n\n"

                time.sleep(5)

            except Exception as e:
                frappe.log_error(f"Polls SSE loop error: {str(e)}")
                error_data = {'error': 'An error occurred in the polls SSE stream.'}
                yield f"data: {json.dumps(error_data)}\n\n"
                break

    return Response(event_stream(), mimetype='text/event-stream')

@frappe.whitelist()
def sse_surveys_analytics():
    """Server-Sent Events endpoint for real-time surveys analytics"""

    def event_stream():
        while True:
            try:
                # Get the latest surveys summary data
                summary_data = get_surveys_dashboard_summary()

                # Get latest surveys data
                surveys_data = get_surveys_analytics()

                event_data = {
                    'type': 'summary_update',
                    'summary': summary_data,
                    'surveys': surveys_data[:5],  # Send only top 5 for real-time updates
                    'timestamp': now()
                }

                yield f"data: {json.dumps(event_data)}\n\n"

                time.sleep(5)

            except Exception as e:
                frappe.log_error(f"Surveys SSE loop error: {str(e)}")
                error_data = {'error': 'An error occurred in the surveys SSE stream.'}
                yield f"data: {json.dumps(error_data)}\n\n"
                break

    return Response(event_stream(), mimetype='text/event-stream')


@frappe.whitelist()
def create_poll(title, description=None, start_date=None, end_date=None, options=None):
    """Create a new poll. Each option becomes one Poll Question row (single-choice vote)."""
    try:
        if isinstance(options, str):
            options = json.loads(options)
        options = options or []
        if len(options) < 2:
            return {'error': 'A poll needs at least 2 options'}

        start_date = start_date if start_date and start_date != 'null' else None
        end_date = end_date if end_date and end_date != 'null' else None

        poll = frappe.get_doc({
            'doctype': 'Poll',
            'title': title,
            'description': description,
            'status': 'Draft',
            'start_date': start_date,
            'end_date': end_date,
            'questions': [
                {'question_text': opt, 'question_type': 'Single Choice', 'options': opt}
                for opt in options
            ]
        })
        poll.insert()
        frappe.db.commit()
        return {'name': poll.name}
    except Exception as e:
        frappe.log_error(f"Create poll error: {str(e)}")
        return {'error': str(e)}


@frappe.whitelist()
def create_survey(title, description=None, start_date=None, end_date=None, questions=None):
    try:
        if isinstance(questions, str):
            questions = json.loads(questions)
        questions = questions or []
        if not questions:
            return {'error': 'A survey needs at least one question'}

        start_date = start_date if start_date and start_date != 'null' else None
        end_date = end_date if end_date and end_date != 'null' else None

        survey_questions = []
        for q in questions:
            row = {
                'question_text': q.get('question_text'),
                'question_type': q.get('question_type'),
                'required': 1 if q.get('required') else 0,
            }
            opts = q.get('options') or []
            if opts:
                row['options'] = '\n'.join(opts)
            survey_questions.append(row)

        survey = frappe.get_doc({
            'doctype': 'Survey',
            'title': title,
            'description': description,
            'status': 'Draft',
            'start_date': start_date,
            'end_date': end_date,
            'questions': survey_questions
        })
        survey.insert()
        frappe.db.commit()
        return {'name': survey.name}
    except Exception as e:
        frappe.log_error(f"Create survey error: {str(e)}")
        return {'error': str(e)}


@frappe.whitelist(allow_guest=True)
def submit_poll_response(poll_name, option_name):
    """option_name is the Poll Question row .name the user selected (see PollVote.vue)."""
    try:
        if not frappe.db.exists('Poll', poll_name):
            return {'error': 'Poll not found'}
        poll = frappe.get_doc('Poll', poll_name)
        if poll.status != 'Active':
            return {'error': 'Poll is not active'}

        frappe.get_doc({
            'doctype': 'Poll Response',
            'poll': poll_name,
            'poll_question': option_name,
            'response_value': option_name,
            'participant_ip': frappe.local.request_ip or '',
        }).insert(ignore_permissions=True)
        frappe.db.commit()

        poll.update_total_responses()
        frappe.db.commit()
        return {'success': True}
    except Exception as e:
        frappe.log_error(f"Submit poll response error: {str(e)}")
        return {'error': str(e)}


@frappe.whitelist(allow_guest=True)
def submit_survey_response(survey_name, responses, respondent_info=None):
    try:
        if isinstance(responses, str):
            responses = json.loads(responses)
        if isinstance(respondent_info, str):
            try:
                respondent_info = json.loads(respondent_info)
            except Exception:
                respondent_info = {}

        if not frappe.db.exists('Survey', survey_name):
            return {'error': 'Survey not found'}
        survey = frappe.get_doc('Survey', survey_name)
        if survey.status != 'Active':
            return {'error': 'Survey is not active'}

        valid_questions = {q.name for q in survey.questions}
        created = 0
        for question_name, value in responses.items():
            if question_name == '__comments__' or question_name not in valid_questions:
                continue
            if value in (None, ''):
                continue
            frappe.get_doc({
                'doctype': 'Survey Response',
                'survey': survey_name,
                'survey_question': question_name,
                'response_value': str(value),
                'participant_ip': frappe.local.request_ip or '',
                'participant_info': respondent_info or {}
            }).insert(ignore_permissions=True)
            created += 1

        frappe.db.commit()
        survey.reload()
        survey.update_total_responses()
        frappe.db.commit()
        return {'success': True, 'responses_created': created}
    except Exception as e:
        frappe.log_error(f"Submit survey response error: {str(e)}")
        return {'error': str(e)}


@frappe.whitelist()
def update_poll_status(poll_name, status):
    try:
        if status not in ['Draft', 'Active', 'Closed', 'Archived']:
            return {'error': 'Invalid status'}
        frappe.db.set_value('Poll', poll_name, 'status', status)
        frappe.db.commit()
        return {'success': True}
    except Exception as e:
        frappe.log_error(f"Update poll status error: {str(e)}")
        return {'error': str(e)}


@frappe.whitelist()
def update_survey_status(survey_name, status):
    try:
        if status not in ['Draft', 'Active', 'Closed', 'Archived']:
            return {'error': 'Invalid status'}
        frappe.db.set_value('Survey', survey_name, 'status', status)
        frappe.db.commit()
        return {'success': True}
    except Exception as e:
        frappe.log_error(f"Update survey status error: {str(e)}")
        return {'error': str(e)}