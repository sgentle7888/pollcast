import frappe
from frappe import _
from frappe.utils import now_datetime, cint
import json
import time
from typing import Dict, List, Optional

class SSEManager:
    """Server-Sent Events manager for real-time updates"""
    
    def __init__(self):
        self.connections = {}
        self.channels = {
            'poll_updates': set(),
            'survey_updates': set(),
            'analytics_updates': set(),
            'global_updates': set()
        }
    
    def add_connection(self, connection_id: str, channels: List[str] = None):
        """Add a new SSE connection"""
        self.connections[connection_id] = {
            'created_at': now_datetime(),
            'last_ping': now_datetime(),
            'channels': channels or ['global_updates']
        }
        
        # Subscribe to channels
        for channel in self.connections[connection_id]['channels']:
            if channel in self.channels:
                self.channels[channel].add(connection_id)
    
    def remove_connection(self, connection_id: str):
        """Remove an SSE connection"""
        if connection_id in self.connections:
            # Unsubscribe from all channels
            for channel in self.connections[connection_id]['channels']:
                if channel in self.channels:
                    self.channels[channel].discard(connection_id)
            
            del self.connections[connection_id]
    
    def broadcast_to_channel(self, channel: str, event_type: str, data: dict):
        """Broadcast message to all connections in a channel"""
        if channel not in self.channels:
            return
        
        message = {
            'event': event_type,
            'data': data,
            'timestamp': now_datetime().isoformat()
        }
        
        # Store message for delivery
        for connection_id in self.channels[channel]:
            self.queue_message(connection_id, message)
    
    def queue_message(self, connection_id: str, message: dict):
        """Queue message for a specific connection"""
        # In a real implementation, this would use Redis or similar
        # For now, we'll use Frappe's cache
        cache_key = f"sse_messages_{connection_id}"
        messages = frappe.cache().get_value(cache_key) or []
        messages.append(message)
        frappe.cache().set_value(cache_key, messages, expires_in_sec=300)
    
    def get_messages(self, connection_id: str) -> List[dict]:
        """Get queued messages for a connection"""
        cache_key = f"sse_messages_{connection_id}"
        messages = frappe.cache().get_value(cache_key) or []
        frappe.cache().delete_value(cache_key)
        return messages

# Global SSE manager instance
sse_manager = SSEManager()

@frappe.whitelist(allow_guest=True)
def sse_stream():
    """SSE endpoint for real-time updates"""
    import uuid
    
    connection_id = str(uuid.uuid4())
    channels = frappe.form_dict.get('channels', 'global_updates').split(',')
    
    # Add connection
    sse_manager.add_connection(connection_id, channels)
    
    def generate():
        try:
            # Send initial connection message
            yield f"data: {json.dumps({'event': 'connected', 'connection_id': connection_id})}\n\n"
            
            while True:
                # Get queued messages
                messages = sse_manager.get_messages(connection_id)
                
                for message in messages:
                    yield f"event: {message['event']}\n"
                    yield f"data: {json.dumps(message['data'])}\n\n"
                
                # Send heartbeat every 30 seconds
                yield f"event: heartbeat\n"
                yield f"data: {json.dumps({'timestamp': now_datetime().isoformat()})}\n\n"
                
                time.sleep(5)  # Check for new messages every 5 seconds
                
        except GeneratorExit:
            # Client disconnected
            sse_manager.remove_connection(connection_id)
        except Exception as e:
            frappe.logger().error(f"SSE stream error: {str(e)}")
            sse_manager.remove_connection(connection_id)
    
    response = frappe.Response()
    response.headers['Content-Type'] = 'text/event-stream'
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Connection'] = 'keep-alive'
    response.headers['Access-Control-Allow-Origin'] = '*'
    
    return generate()

def broadcast_poll_update(poll_id: str, event_type: str, data: dict = None):
    """Broadcast poll-related updates"""
    message_data = {
        'poll_id': poll_id,
        'type': event_type,
        'data': data or {}
    }
    
    sse_manager.broadcast_to_channel('poll_updates', 'poll_update', message_data)
    sse_manager.broadcast_to_channel('global_updates', 'poll_update', message_data)

def broadcast_survey_update(survey_id: str, event_type: str, data: dict = None):
    """Broadcast survey-related updates"""
    message_data = {
        'survey_id': survey_id,
        'type': event_type,
        'data': data or {}
    }
    
    sse_manager.broadcast_to_channel('survey_updates', 'survey_update', message_data)
    sse_manager.broadcast_to_channel('global_updates', 'survey_update', message_data)

def broadcast_analytics_update(content_type: str, content_id: str, analytics: dict):
    """Broadcast analytics updates"""
    message_data = {
        'content_type': content_type,
        'content_id': content_id,
        'analytics': analytics
    }
    
    sse_manager.broadcast_to_channel('analytics_updates', 'analytics_update', message_data)

def broadcast_system_notification(message: str, notification_type: str = 'info'):
    """Broadcast system-wide notifications"""
    message_data = {
        'message': message,
        'type': notification_type,
        'timestamp': now_datetime().isoformat()
    }
    
    sse_manager.broadcast_to_channel('global_updates', 'system_notification', message_data)

# Document event hooks for real-time updates
def on_poll_response_insert(doc, method):
    """Triggered when a new poll response is created"""
    try:
        # Get updated poll analytics
        poll_doc = frappe.get_doc("Poll", doc.poll)
        analytics = poll_doc.get_analytics()
        
        # Broadcast poll update
        broadcast_poll_update(doc.poll, 'new_response', {
            'response_id': doc.name,
            'analytics': analytics
        })
        
        # Broadcast analytics update
        broadcast_analytics_update('poll', doc.poll, analytics)
        
    except Exception as e:
        frappe.logger().error(f"Error broadcasting poll response update: {str(e)}")

def on_survey_response_insert(doc, method):
    """Triggered when a new survey response is created"""
    try:
        # Get updated survey analytics
        survey_doc = frappe.get_doc("Survey", doc.survey)
        analytics = survey_doc.get_analytics()
        
        # Broadcast survey update
        broadcast_survey_update(doc.survey, 'new_response', {
            'response_id': doc.name,
            'analytics': analytics
        })
        
        # Broadcast analytics update
        broadcast_analytics_update('survey', doc.survey, analytics)
        
    except Exception as e:
        frappe.logger().error(f"Error broadcasting survey response update: {str(e)}")

def on_poll_update(doc, method):
    """Triggered when a poll is updated"""
    try:
        broadcast_poll_update(doc.name, 'poll_updated', {
            'title': doc.title,
            'status': doc.status,
            'description': doc.description
        })
    except Exception as e:
        frappe.logger().error(f"Error broadcasting poll update: {str(e)}")

def on_survey_update(doc, method):
    """Triggered when a survey is updated"""
    try:
        broadcast_survey_update(doc.name, 'survey_updated', {
            'title': doc.title,
            'status': doc.status,
            'description': doc.description
        })
    except Exception as e:
        frappe.logger().error(f"Error broadcasting survey update: {str(e)}")
