import uuid

from pyrogram import Client, filters
from pyrogram.types import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message
)

from config import (
    API_ID,
    API_HASH,
    BOT_TOKEN,
    BOT_USERNAME
)

app = Client(
    "bot_session",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

bot_username = BOT_USERNAME

messages = {}

@app.on_message(filters.command("start"))
async def start(client: Client, message: Message):
    full_name = message.from_user.first_name
    if message.from_user.last_name:
        full_name += f" {message.from_user.last_name}"
    username = f"@{message.from_user.username}" if message.from_user.username else "No username"
    user_info = f"{full_name} ({username})"

    welcome_text = (
        f"Welcome: {user_info}!\n"
        "🌐 I'm the Whisper Bot.\n\n"
        "💬 You can use me to send secret whispers in groups.\n\n"
        "🔮 I work in the Inline mode that means you can use me even if I'm not in the group.\n\n"
        "💌 Example: `@cloakxbot hello this is a test @user1 @user2 12345`\n\n"
        "There are other ways to use me too. If you are interested to learn more about me, click on the Help button."
    )
    help_button = InlineKeyboardMarkup([
        [InlineKeyboardButton("Help", callback_data="help")]
    ])
    
    await message.reply_text(welcome_text, reply_markup=help_button)

@app.on_callback_query(filters.regex("help"))
async def help_callback(client, callback_query):
    help_text = (
        "The other way to use me is to write the inline query by yourself.\n\n"
        "The format should be in this arrangement:\n\n"
        "`@cloakxbot your whisper @username1 @username2 12345`\n\n"
        "Now I'll split the format into parts and explain each part:\n\n"
        "1. `@cloakxbot`:\n"
        "   This is my username; it should be at the beginning of the inline query so I'll know that you are using me and not another bot.\n\n"
        "2. `whisper message`:\n"
        "   This is the whisper that will be sent to the target users. Replace `your whisper` with your actual message.\n\n"
        "3. `@username(s) or user ID(s)`:\n"
        "   Add one or more usernames or user IDs at the end of your message. Separate them with spaces. These users will be able to view the whisper.\n\n"
        "Example:\n"
        "`@cloakxbot hello this is a test @user1 @user2 12345`\n\n"
        "📎 The bot works in groups and the target users should be in the same group as you.\n\n"
        "What are you waiting for?! Try me now 😉"
    )
    back_button = InlineKeyboardMarkup([
        [InlineKeyboardButton("Back", callback_data="back")]
    ])
    
    await callback_query.message.edit_text(help_text, reply_markup=back_button)

@app.on_callback_query(filters.regex("back"))
async def back_callback(client, callback_query):
    full_name = callback_query.from_user.first_name
    if callback_query.from_user.last_name:
        full_name += f" {callback_query.from_user.last_name}"
    username = f"@{callback_query.from_user.username}" if callback_query.from_user.username else "No username"
    user_info = f"{full_name} ({username})"

    welcome_text = (
        f"Welcome: {user_info}!\n"
        "🌐 I'm the Whisper Bot.\n\n"
        "💬 You can use me to send secret whispers in groups.\n\n"
        "🔮 I work in the Inline mode that means you can use me even if I'm not in the group.\n\n"
        "💌 Example: `@cloakxbot hello this is a test @user1 @user2 12345`\n\n"
        "There are other ways to use me too. If you are interested to learn more about me, click on the Help button."
    )
    help_button = InlineKeyboardMarkup([
        [InlineKeyboardButton("Help", callback_data="help")]
    ])
    
    await callback_query.message.edit_text(welcome_text, reply_markup=help_button)

@app.on_inline_query()
async def answer(client, inline_query):
    text = inline_query.query.strip()
    print(f"Inline query received: '{text}'")

    if not text:
        await inline_query.answer(
            results=[
                InlineQueryResultArticle(
                    id=str(uuid.uuid4()),
                    title="How to Send Secret Message",
                    description="Include recipient @usernames or user IDs at the end of your message.",
                    input_message_content=InputTextMessageContent(
                        "How to Send Secret Message\n\n"
                        "Include one or more recipient @usernames or user IDs at the end of your message, separated by spaces.\n\n"
                        "Example: @cloakxbot Hello there! @user1 @user2 12345"
                    ),
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("Start Bot", url=f"https://t.me/{bot_username}?start=inline_help")]]
                    )
                )
            ],
            cache_time=1
        )
        return

    parts = text.split()
    recipients = []
    i = len(parts) - 1
    
    while i >= 0:
        part = parts[i]
        if part.startswith('@') or part.isdigit():
            recipients.insert(0, part)
            i -= 1
        else:
            break
    
    message_content = ' '.join(parts[:i+1]) if i >= 0 else ''
    
    if not recipients:
        await inline_query.answer(
            results=[
                InlineQueryResultArticle(
                    id=str(uuid.uuid4()),
                    title="Invalid Format",
                    description="Add recipient @usernames/user IDs at the end",
                    input_message_content=InputTextMessageContent(
                        "❌ Please include recipient @usernames or user IDs at the end of your message!\n\n"
                        "Example: @cloakxbot Your message @user1 @user2"
                    ),
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("Learn More", url=f"https://t.me/{bot_username}?start=inline_help")]]
                    )
                )
            ],
            cache_time=1
        )
        return

    recipient_ids = []
    recipient_names = []
    errors = []

    for identifier in recipients:
        try:
            if identifier.startswith('@'):
                user = await client.get_users(identifier[1:])
            else:
                user = await client.get_users(int(identifier))
                
            if user.id not in recipient_ids:
                recipient_ids.append(user.id)
                full_name = user.first_name
                if user.last_name:
                    full_name += f" {user.last_name}"
                username = f"@{user.username}" if user.username else ""
                recipient_names.append(f"{full_name} {username}".strip())
        except Exception as e:
            errors.append(identifier)
            continue

    if errors:
        error_list = ", ".join(errors)
        await inline_query.answer(
            results=[
                InlineQueryResultArticle(
                    id=str(uuid.uuid4()),
                    title="Invalid Recipients",
                    description=f"Couldn't find: {error_list}",
                    input_message_content=InputTextMessageContent(
                        f"❌ Couldn't find these users: {error_list}\n\n"
                        "Please check the usernames/user IDs and try again."
                    ),
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("Help", url=f"https://t.me/{bot_username}?start=inline_help")]]
                    )
                )
            ],
            cache_time=1
        )
        return

    if not recipient_ids:
        await inline_query.answer(
            results=[
                InlineQueryResultArticle(
                    id=str(uuid.uuid4()),
                    title="No Valid Recipients",
                    description="Please provide valid @usernames or user IDs",
                    input_message_content=InputTextMessageContent(
                        "❌ No valid recipients found!\n\n"
                        "Please include valid @usernames or user IDs at the end of your message."
                    ),
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("Help", url=f"https://t.me/{bot_username}?start=inline_help")]]
                    )
                )
            ],
            cache_time=1
        )
        return

    message_id = str(uuid.uuid4())
    messages[message_id] = {
        "content": message_content,
        "sender_id": inline_query.from_user.id,
        "recipient_ids": recipient_ids
    }
    print(f"Message Stored: ID={message_id}, Content='{message_content}'")

    recipient_list = ", ".join(recipient_names)
    whisper_message = f"🔒 Whisper to {recipient_list}\nOnly viewable by you and the recipients."

    results = [
        InlineQueryResultArticle(
            id=str(uuid.uuid4()),
            title=f"Whisper to {len(recipient_ids)} user(s)",
            description=f"Recipients: {recipient_list}",
            input_message_content=InputTextMessageContent(whisper_message),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Show Message 🔒", callback_data=message_id)]
            ])
        )
    ]
    print(f"Sending inline query result: '{whisper_message}'")

    await inline_query.answer(results, cache_time=1)

@app.on_callback_query(filters.create(lambda _, __, query: query.data in messages))
async def whisper_callback(client, callback_query):
    message_id = callback_query.data
    user_id = callback_query.from_user.id
    message_data = messages.get(message_id)

    if not message_data:
        await callback_query.answer("Message not found or expired.", show_alert=True)
        return

    sender_id = message_data["sender_id"]
    recipient_ids = message_data["recipient_ids"]

    if user_id == sender_id or user_id in recipient_ids:
        await callback_query.answer(message_data["content"], show_alert=True)
        print(f"Response Sent: {message_content}")
    else:
        await callback_query.answer("This message isn't for you—just like happiness isn't yours to claim.", show_alert=True)

app.run()