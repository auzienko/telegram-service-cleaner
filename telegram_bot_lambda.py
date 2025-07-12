import json
import logging
import os
import requests
from telegram import Update, Bot
from telegram.error import TelegramError, BadRequest

# Configure logging with detailed level
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG  # Changed to DEBUG for more detailed logging
)
logger = logging.getLogger(__name__)

# Get token from environment variable
BOT_TOKEN = os.environ.get('BOT_TOKEN')


def analyze_message_structure(message_data, message_type):
    """Analyzes message structure in detail for diagnostics."""
    logger.info(f"=== ANALYZING {message_type.upper()} STRUCTURE ===")

    # Basic message fields
    basic_fields = {
        'message_id': 'Message ID',
        'date': 'Message date',
        'text': 'Message text',
        'from': 'Sender',
        'chat': 'Chat information'
    }

    logger.info("Basic message fields:")
    for field, description in basic_fields.items():
        if field in message_data:
            if field == 'chat':
                chat_info = message_data[field]
                logger.info(f"  {field} ({description}): ID={chat_info.get('id')}, "
                            f"Type={chat_info.get('type')}, Title={chat_info.get('title', 'N/A')}")
            elif field == 'from':
                from_info = message_data[field]
                logger.info(f"  {field} ({description}): ID={from_info.get('id')}, "
                            f"Username={from_info.get('username', 'N/A')}, "
                            f"First_name={from_info.get('first_name', 'N/A')}")
            else:
                logger.info(f"  {field} ({description}): {message_data[field]}")
        else:
            logger.info(f"  {field} ({description}): MISSING")

    # Service message fields
    service_fields = {
        'new_chat_members': 'New chat members',
        'left_chat_member': 'Left chat member',
        'new_chat_title': 'New chat title',
        'new_chat_photo': 'New chat photo',
        'delete_chat_photo': 'Delete chat photo',
        'group_chat_created': 'Group chat created',
        'supergroup_chat_created': 'Supergroup created',
        'channel_chat_created': 'Channel created',
        'pinned_message': 'Pinned message',
        'proximity_alert_triggered': 'Proximity alert triggered',
        'forum_topic_created': 'Forum topic created',
        'forum_topic_edited': 'Forum topic edited',
        'forum_topic_closed': 'Forum topic closed',
        'forum_topic_reopened': 'Forum topic reopened',
        'migrate_to_chat_id': 'Migrate to chat',
        'migrate_from_chat_id': 'Migrate from chat',
        'successful_payment': 'Successful payment',
        'connected_website': 'Connected website',
        'passport_data': 'Passport data',
        'video_chat_started': 'Video chat started',
        'video_chat_ended': 'Video chat ended',
        'video_chat_participants_invited': 'Video chat participants invited',
        'video_chat_scheduled': 'Video chat scheduled',
        'web_app_data': 'Web app data'
    }

    found_service_fields = []
    logger.info("Service message fields:")
    for field, description in service_fields.items():
        if field in message_data and message_data[field] is not None:
            found_service_fields.append(field)
            logger.info(f"  {field} ({description}): {message_data[field]}")

    if not found_service_fields:
        logger.info("  No service fields found")

    # Additional fields
    other_fields = []
    for field in message_data:
        if field not in basic_fields and field not in service_fields:
            other_fields.append(field)

    if other_fields:
        logger.info(f"Other fields present: {other_fields}")

    logger.info(f"=== END {message_type.upper()} ANALYSIS ===")

    return found_service_fields


def handle_service_message(update: Update, bot: Bot) -> None:
    """Processes and deletes service messages in chat."""
    logger.debug("=== Starting handle_service_message ===")

    # Check all possible message types
    message = update.message or update.edited_message or update.channel_post or update.edited_channel_post

    if not message:
        logger.info("No message found in update")

        # Check other update types
        if update.my_chat_member:
            logger.info("Found my_chat_member update - bot status change")
            logger.debug(f"my_chat_member: {update.my_chat_member}")
        elif update.chat_member:
            logger.info("Found chat_member update - member status change")
            logger.debug(f"chat_member: {update.chat_member}")
        elif update.callback_query:
            logger.info("Found callback_query update")
        elif update.inline_query:
            logger.info("Found inline_query update")
        else:
            logger.warning("Unknown update type received")

        return

    # Check for chat_id presence
    if not hasattr(message, 'chat') or not message.chat:
        logger.error("Message has no chat information!")
        return

    if not hasattr(message.chat, 'id') or message.chat.id is None:
        logger.error("Message chat has no ID!")
        return

    logger.info(f"Processing message: ID={message.message_id}, Chat={message.chat.id}, Type={message.chat.type}")

    # Detailed logging of message content
    logger.debug(f"Message content: text={getattr(message, 'text', None)}, "
                 f"from_user={getattr(message, 'from_user', None)}")

    # Check for service messages - FIXED
    service_checks = {
        'new_chat_members': getattr(message, 'new_chat_members', None),
        'left_chat_member': getattr(message, 'left_chat_member', None),
        'new_chat_title': getattr(message, 'new_chat_title', None),
        'new_chat_photo': getattr(message, 'new_chat_photo', None),
        'delete_chat_photo': getattr(message, 'delete_chat_photo', None),
        'group_chat_created': getattr(message, 'group_chat_created', None),
        'supergroup_chat_created': getattr(message, 'supergroup_chat_created', None),
        'channel_chat_created': getattr(message, 'channel_chat_created', None),
        'pinned_message': getattr(message, 'pinned_message', None),
        'proximity_alert_triggered': getattr(message, 'proximity_alert_triggered', None),
        'forum_topic_created': getattr(message, 'forum_topic_created', None),
        'forum_topic_edited': getattr(message, 'forum_topic_edited', None),
        'forum_topic_closed': getattr(message, 'forum_topic_closed', None),
        'forum_topic_reopened': getattr(message, 'forum_topic_reopened', None),
        'migrate_to_chat_id': getattr(message, 'migrate_to_chat_id', None),
        'migrate_from_chat_id': getattr(message, 'migrate_from_chat_id', None),
    }

    # Log all checks
    found_service_types = []
    for check_name, check_value in service_checks.items():
        if check_value is not None:
            found_service_types.append(check_name)
            logger.info(f"Found service message type: {check_name} = {check_value}")

    # FIXED service message check
    is_service_message = any(check_value is not None for check_value in service_checks.values())

    if is_service_message:
        logger.info(f"Confirmed service message in chat {message.chat.id}, "
                    f"types: {found_service_types}, attempting to delete message {message.message_id}")

        # Check that we have all necessary data for deletion
        if not message.message_id:
            logger.error("Cannot delete message: message_id is missing!")
            return

        try:
            # Use synchronous HTTP request directly
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteMessage"
            payload = {
                'chat_id': message.chat.id,
                'message_id': message.message_id
            }

            logger.info(f"Sending delete request: chat_id={message.chat.id}, message_id={message.message_id}")
            logger.debug(f"Request URL: {url}")
            logger.debug(f"Request payload: {payload}")

            response = requests.post(url, json=payload, timeout=10)

            logger.debug(f"Delete response status: {response.status_code}")
            logger.debug(f"Delete response text: {response.text}")

            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    logger.info(f"Successfully deleted service message {message.message_id} in chat {message.chat.id}")
                else:
                    error_description = result.get('description', 'Unknown error')
                    error_code = result.get('error_code', 0)

                    # Handle known errors without logging as ERROR
                    if error_code == 400:
                        if "chat not found" in error_description.lower():
                            logger.warning(f"Chat {message.chat.id} not found - possibly left or deleted")
                        elif "message can't be deleted" in error_description.lower():
                            logger.warning(
                                f"Cannot delete message {message.message_id}: insufficient permissions or message too old")
                        elif "message to delete not found" in error_description.lower():
                            logger.warning(f"Message {message.message_id} already deleted or not found")
                        else:
                            logger.warning(f"Telegram API error {error_code}: {error_description}")
                    else:
                        logger.error(f"Telegram API error {error_code}: {error_description}")
            else:
                # HTTP status not 200, but might be valid Telegram API response
                try:
                    result = response.json()
                    if 'description' in result:
                        error_description = result.get('description', 'Unknown error')
                        error_code = result.get('error_code', response.status_code)

                        # Handle same errors even if HTTP status is not 200
                        if error_code == 400:
                            if "chat not found" in error_description.lower():
                                logger.warning(f"Chat {message.chat.id} not found - possibly left or deleted")
                            elif "message can't be deleted" in error_description.lower():
                                logger.warning(
                                    f"Cannot delete message {message.message_id}: insufficient permissions or message too old")
                            elif "message to delete not found" in error_description.lower():
                                logger.warning(f"Message {message.message_id} already deleted or not found")
                            else:
                                logger.warning(f"Telegram API error {error_code}: {error_description}")
                        else:
                            logger.error(f"Telegram API error {error_code}: {error_description}")
                    else:
                        logger.error(f"HTTP error {response.status_code}: {response.text}")
                except json.JSONDecodeError:
                    logger.error(f"HTTP error {response.status_code}: {response.text}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error deleting message: {e}")
        except Exception as e:
            logger.error(f"Unexpected error deleting message: {e}")
    else:
        logger.debug(f"Message {message.message_id} is not a service message, skipping")


def create_response(status_code: int, message: str) -> dict:
    """Creates standard response for Lambda."""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps(message)
    }


def lambda_handler(event, context):
    """Main Lambda handler function."""
    logger.info("=== Lambda handler started ===")

    # Check token
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN is not set")
        return create_response(500, 'Error: BOT_TOKEN is not set')

    # Initialize bot
    bot = Bot(token=BOT_TOKEN)
    logger.debug("Bot initialized successfully")

    try:
        # Log incoming event
        logger.debug(f"Received event: {json.dumps(event, indent=2)}")

        # Parse incoming webhook request
        body = event.get('body')
        if not body:
            logger.error("Empty body in event")
            return create_response(400, 'Error: Empty request body')

        # Parse JSON if body is a string
        if isinstance(body, str):
            try:
                body = json.loads(body)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in body: {e}")
                return create_response(400, 'Error: Invalid JSON format')

        logger.info(f"Received webhook payload: {json.dumps(body, indent=2)}")

        # DETAILED WEBHOOK CONTENT ANALYSIS
        logger.info("=== WEBHOOK CONTENT ANALYSIS ===")
        logger.info(f"Payload keys: {list(body.keys())}")

        # Analyze each possible update type
        update_types = {
            'message': 'Regular message',
            'edited_message': 'Edited message',
            'channel_post': 'Channel post',
            'edited_channel_post': 'Edited channel post',
            'callback_query': 'Callback query from inline button',
            'inline_query': 'Inline query',
            'chosen_inline_result': 'Chosen inline result',
            'shipping_query': 'Shipping query',
            'pre_checkout_query': 'Pre checkout query',
            'poll': 'Poll',
            'poll_answer': 'Poll answer',
            'my_chat_member': 'Bot status change in chat',
            'chat_member': 'Chat member change',
            'chat_join_request': 'Chat join request'
        }

        found_updates = []
        for update_type, description in update_types.items():
            if update_type in body:
                found_updates.append(update_type)
                logger.info(f"Found {update_type}: {description}")

                # Detailed content analysis
                update_content = body[update_type]
                logger.debug(f"{update_type} content: {json.dumps(update_content, indent=2)}")

                # If it's a message, analyze its structure
                if update_type in ['message', 'edited_message', 'channel_post', 'edited_channel_post']:
                    analyze_message_structure(update_content, update_type)

        if not found_updates:
            logger.warning("No recognized update types found in webhook!")
            logger.info("This might be a new update type or malformed webhook")

        logger.info(f"Total recognized update types: {len(found_updates)}")
        logger.info("=== END WEBHOOK ANALYSIS ===")

        # Check data structure
        if not isinstance(body, dict):
            logger.error("Body is not a dictionary")
            return create_response(400, 'Error: Invalid payload format')

        # Detailed message information for debugging
        if 'message' in body:
            msg = body['message']
            logger.info(f"Message details: chat_id={msg.get('chat', {}).get('id')}, "
                        f"message_id={msg.get('message_id')}, "
                        f"chat_type={msg.get('chat', {}).get('type')}, "
                        f"from_user={msg.get('from', {}).get('id')}, "
                        f"text={msg.get('text', 'N/A')}")

        # Check other update types
        update_types = ['edited_message', 'channel_post', 'edited_channel_post',
                        'callback_query', 'inline_query']

        for update_type in update_types:
            if update_type in body:
                logger.info(f"Received {update_type}: {body[update_type].get('message_id', 'N/A')}")

        # Check for required fields
        if 'message' in body:
            message = body['message']
            if not isinstance(message, dict) or 'date' not in message:
                logger.error("Missing or invalid 'date' field in message")
                return create_response(400, "Error: Missing 'date' field in message")

        # Create Update object
        try:
            update = Update.de_json(body, bot)
            logger.debug(f"Update object created: {update}")
        except Exception as e:
            logger.error(f"Failed to parse update: {e}")
            return create_response(500, f"Error parsing update: {str(e)}")

        if not update:
            logger.error("No valid update found in event")
            return create_response(400, 'No valid update found')

        # Run processing (now synchronous)
        try:
            handle_service_message(update, bot)
        except Exception as e:
            logger.error(f"Error in processing: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return create_response(500, f"Error processing message: {str(e)}")

    except Exception as e:
        logger.error(f"Unexpected error processing update: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return create_response(500, f"Error: {str(e)}")

    logger.info("=== Lambda handler completed successfully ===")
    return create_response(200, 'OK')