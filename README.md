# Telegram Service Message Cleaner

A serverless AWS Lambda function that automatically removes service messages from Telegram chats, keeping your groups clean and focused on actual conversations.

## 📋 Description

This bot automatically detects and deletes various types of service messages in Telegram chats, including:
- New chat members joined
- Members left the chat
- Chat title changes
- Chat photo updates
- Pinned messages
- Group/supergroup creation messages
- Forum topic management messages
- And many more system notifications

## ✨ Features

- **Automatic Detection**: Identifies all types of Telegram service messages
- **Instant Deletion**: Removes service messages immediately upon detection
- **Comprehensive Logging**: Detailed debug information for troubleshooting
- **Error Handling**: Robust error handling for common Telegram API issues
- **Serverless**: Runs on AWS Lambda with minimal cost
- **Zero Configuration**: Works out of the box once deployed

## 🚀 Supported Service Message Types

- `new_chat_members` - When users join the chat
- `left_chat_member` - When users leave the chat
- `new_chat_title` - Chat title changes
- `new_chat_photo` - Chat photo updates
- `delete_chat_photo` - Chat photo deletions
- `group_chat_created` - Group chat creation
- `supergroup_chat_created` - Supergroup creation
- `channel_chat_created` - Channel creation
- `pinned_message` - Message pinning
- `proximity_alert_triggered` - Location proximity alerts
- `forum_topic_created` - Forum topic creation
- `forum_topic_edited` - Forum topic editing
- `forum_topic_closed` - Forum topic closing
- `forum_topic_reopened` - Forum topic reopening
- `migrate_to_chat_id` - Chat migration
- `migrate_from_chat_id` - Chat migration
- `video_chat_started` - Video chat events
- `video_chat_ended` - Video chat events
- And more...

## 🛠️ Prerequisites

- AWS Account with Lambda access
- Telegram Bot Token (from @BotFather)
- Basic knowledge of AWS Lambda and Telegram Bot API

## 📦 Installation & Deployment

### Step 1: Create a Telegram Bot

1. Start a chat with [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` command
3. Follow instructions to create your bot
4. Save the bot token (format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
5. Add your bot to the target chat and make it an admin with "Delete messages" permission

### Step 2: Prepare the Lambda Package

1. Clone this repository:
   ```bash
   git clone https://github.com/auzienko/telegram-service-cleaner.git
   cd telegram-service-cleaner
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install python-telegram-bot==13.15 requests
   ```

3. Create deployment package:
   ```bash
   # Create a clean directory for the package
   mkdir package
   
   # Copy the main script
   cp lambda_function.py package/
   
   # Install dependencies into the package directory
   pip install --target package python-telegram-bot==13.15 requests
   
   # Create ZIP file
   cd package
   zip -r ../telegram-cleaner.zip .
   cd ..
   ```

### Step 3: Deploy to AWS Lambda (Free Tier)

1. **Login to AWS Console** and navigate to Lambda service

2. **Create Function**:
   - Click "Create function"
   - Choose "Author from scratch"
   - Function name: `telegram-service-cleaner`
   - Runtime: `Python 3.9`
   - Architecture: `x86_64`
   - Click "Create function"

3. **Upload Code**:
   - In the function overview, click "Upload from" → ".zip file"
   - Upload the `telegram-cleaner.zip` file
   - Click "Save"

4. **Configure Environment Variables**:
   - Go to "Configuration" → "Environment variables"
   - Click "Edit" → "Add environment variable"
   - Key: `BOT_TOKEN`
   - Value: Your Telegram bot token
   - Click "Save"

5. **Set up Function URL** (for webhook):
   - Go to "Configuration" → "Function URL"
   - Click "Create function URL"
   - Auth type: `NONE`
   - Click "Save"
   - Copy the Function URL (you'll need it for the webhook)

6. **Configure Runtime Settings**:
   - Go to "Configuration" → "General configuration"
   - Edit timeout to 30 seconds
   - Memory: 128 MB (sufficient for this function)
   - Handler: `lambda_function.lambda_handler`

### Step 4: Set Up Telegram Webhook

1. **Set the webhook** using curl or browser:
   ```bash
   curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
        -d "url=<YOUR_LAMBDA_FUNCTION_URL>"
   ```

   Replace:
   - `<YOUR_BOT_TOKEN>` with your actual bot token
   - `<YOUR_LAMBDA_FUNCTION_URL>` with the Function URL from Step 3

2. **Verify webhook** (optional):
   ```bash
   curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"
   ```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `BOT_TOKEN` | Your Telegram bot token from BotFather | Yes |

### Lambda Configuration

- **Runtime**: Python 3.9+
- **Memory**: 128 MB (minimum)
- **Timeout**: 30 seconds
- **Handler**: `lambda_function.lambda_handler`

## 📊 Monitoring & Logs

### CloudWatch Logs

The function provides detailed logging for debugging:

- **INFO level**: Basic operation information
- **DEBUG level**: Detailed message analysis and API calls
- **WARNING level**: Non-critical errors (permissions, message not found)
- **ERROR level**: Critical errors requiring attention

### Example Log Output

```
2024-01-01 12:00:00 - INFO - Processing message: ID=123, Chat=-1001234567890, Type=supergroup
2024-01-01 12:00:00 - INFO - Found service message type: new_chat_members = [{'id': 123456789, 'is_bot': False, 'first_name': 'John'}]
2024-01-01 12:00:00 - INFO - Successfully deleted service message 123 in chat -1001234567890
```

## 🔍 Troubleshooting

### Common Issues

1. **Bot can't delete messages**:
   - Ensure the bot is an admin in the chat
   - Grant "Delete messages" permission to the bot

2. **Lambda timeout**:
   - Increase timeout in Lambda configuration
   - Check CloudWatch logs for specific errors

3. **Webhook not receiving updates**:
   - Verify webhook URL is correct
   - Check that Function URL is publicly accessible
   - Ensure bot token is correct

4. **Permission errors**:
   - Bot needs admin rights in the target chat
   - "Delete messages" permission is specifically required

### Debug Mode

To enable more detailed logging, the function already runs in DEBUG mode. Check CloudWatch logs for comprehensive information about:
- Incoming webhook payload analysis
- Message structure breakdown
- API call details
- Error specifics

## 💰 Cost Estimation (AWS Free Tier)

- **Lambda**: 1M free requests/month, 400,000 GB-seconds/month
- **CloudWatch Logs**: 5GB free storage
- **Estimated monthly cost**: $0 for typical usage (small to medium chats)

For high-volume chats (1000+ messages/day), estimated cost: < $1/month

## 🔒 Security Considerations

- Bot token is stored as an environment variable (encrypted at rest)
- Function URL has no authentication (webhook endpoint)
- No sensitive data is logged
- All API calls use HTTPS

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

If you encounter any issues:
1. Check the CloudWatch logs for detailed error information
2. Verify your bot permissions in the target chat
3. Ensure the webhook URL is correctly configured
4. Open an issue in this repository with relevant logs

## 🔄 Updates

To update the function:
1. Modify the code
2. Create a new deployment package
3. Upload the new ZIP file to Lambda
4. The function will automatically use the updated code

---

**Note**: This bot only removes service messages and doesn't interfere with regular user messages. It's designed to keep your chat clean while preserving all meaningful conversations.