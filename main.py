import telebot
from telebot import types
import time

# ----------------- CONFIGURATION -----------------
API_TOKEN = '8874646473:AAEb_e2ltYCeFFFPMhFOSbZUqPZZYk2h6cQ'
MAIN_ADMIN_ID = 8711187182
FORCE_CHANNEL = "@GMAILWORKAVIABLE1"  # Public Channel Username
SUPPORT_USERNAME = "@Shubhamearn112"

bot = telebot.TeleBot(API_TOKEN)

# ----------------- DATA STORAGE -----------------
users = {}  
# {user_id: {'balance': 0.0, 'today': 0.0, 'total': 0.0, 'completed': 0, 'pending': 0, 'rejected': 0, 'banned': False, 'referrals': 0}}

admins = set([MAIN_ADMIN_ID])
submissions = []  # List of dicts for submissions
withdrawals = []  # List of dicts for withdrawals

current_create_task = None  # Single-task lock
OLD_GMAIL_REWARD = 13.0
CREATE_GMAIL_REWARD = 13.0
MIN_WITHDRAW = 50.0

def get_user(user_id):
    if user_id not in users:
        users[user_id] = {
            'balance': 0.0,
            'today': 0.0,
            'total': 0.0,
            'completed': 0,
            'pending': 0,
            'rejected': 0,
            'banned': False,
            'referrals': 0
        }
    return users[user_id]

def check_force_join(user_id):
    try:
        member = bot.get_chat_member(FORCE_CHANNEL, user_id)
        if member.status in ['creator', 'administrator', 'member']:
            return True
        return False
    except Exception as e:
        # If bot is not admin in channel or channel is wrong, allow bypass to prevent breaking
        return True

def force_join_markup():
    markup = types.InlineKeyboardMarkup()
    btn_channel = types.InlineKeyboardButton("📢 Join Official Channel", url=f"https://t.me/{FORCE_CHANNEL.replace('@', '')}")
    btn_check = types.InlineKeyboardButton("✅ Joined", callback_data="check_joined")
    markup.add(btn_channel)
    markup.add(btn_check)
    return markup

def main_keyboard(user_id):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('🚀 Start Earn')
    btn2 = types.KeyboardButton('👤 Profile')
    btn3 = types.KeyboardButton('💳 Withdraw')
    btn4 = types.KeyboardButton('🤝 Refer')
    btn5 = types.KeyboardButton('🆘 Support')
    btn6 = types.KeyboardButton('📩 DM Admin / Gmail Query')
    btn7 = types.KeyboardButton('📋 My Submitted')
    
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    markup.add(btn5, btn6)
    markup.add(btn7)
    
    if user_id in admins:
        markup.add(types.KeyboardButton('⚙️ Admin Panel'))
        
    return markup

# ----------------- COMMANDS & HANDLERS -----------------
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    u = get_user(user_id)

    if u['banned']:
        bot.send_message(message.chat.id, "❌ Aap is bot se banned hain.")
        return

    # Check referral start
    text_parts = message.text.split()
    if len(text_parts) > 1 and text_parts[1].isdigit():
        referrer_id = int(text_parts[1])
        if referrer_id != user_id and referrer_id in users:
            # Simple referral tracking
            pass

    if not check_force_join(user_id):
        bot.send_message(
            message.chat.id,
            f"⚠️ *Force Join Required!*\n\nBot ka upyog karne ke liye aapko humara official channel join karna zaroori hai.\n\nChannel: {FORCE_CHANNEL}",
            parse_mode='Markdown',
            reply_markup=force_join_markup()
        )
        return

    text = (
        f"Welcome {message.from_user.first_name}!\n\n"
        "📧 *Gmail Buy Sale Bot* mein aapka swagat hai.\n"
        "Yahan aap purane Gmail account bech sakte ho ya naye Gmail account bana kar kama sakte ho.\n\n"
        "Niche diye gaye menu se option choose karein 👇"
    )
    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=main_keyboard(user_id))

# ----------------- USER PANEL -----------------
@bot.message_handler(func=lambda m: m.text == '🚀 Start Earn')
def start_earn(message):
    user_id = message.from_user.id
    if get_user(user_id)['banned']: return
    if not check_force_join(user_id):
        bot.send_message(message.chat.id, "⚠️ Kripya pehle channel join karein!", reply_markup=force_join_markup())
        return

    markup = types.InlineKeyboardMarkup()
    btn_old = types.InlineKeyboardButton("📦 Sold Old Gmail", callback_data="sell_old_gmail")
    btn_create = types.InlineKeyboardButton("✉️ Create Gmail", callback_data="create_gmail_task")
    markup.add(btn_old, btn_create)
    
    text = (
        "🚀 *Start Earn*\n\n"
        "📦 *Sold Old Gmail* – apna purana Gmail account bech kar reward payein.\n"
        "✉️ *Create Gmail* – admin ke diye task ke hisab se naya Gmail account banayein aur kamayein.\n\n"
        "Ek option choose karein 👇"
    )
    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == '👤 Profile')
def user_profile(message):
    user_id = message.from_user.id
    u = get_user(user_id)
    if u['banned']: return

    text = (
        f"👤 *Your Profile*\n\n"
        f"🆔 *User ID:* `{user_id}`\n"
        f"💳 *Balance:* ₹{u['balance']}\n"
        f"📅 *Today Income:* ₹{u['today']}\n"
        f"💰 *Total Income:* ₹{u['total']}\n\n"
        f"✅ *Completed Tasks:* {u['completed']}\n"
        f"⏳ *Pending Tasks:* {u['pending']}\n"
        f"❌ *Rejected Tasks:* {u['rejected']}"
    )
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text == '💳 Withdraw')
def withdraw(message):
    user_id = message.from_user.id
    u = get_user(user_id)
    if u['banned']: return

    if u['balance'] < MIN_WITHDRAW:
        bot.send_message(message.chat.id, f"💳 Aapka current balance ₹{u['balance']} hai. Minimum withdraw limit ₹{MIN_WITHDRAW} hai.")
    else:
        msg = bot.send_message(message.chat.id, f"💳 Aapka balance ₹{u['balance']} hai.\nApna UPI ID ya payment detail bhejein:")
        bot.register_next_step_handler(msg, process_withdraw, u['balance'])

def process_withdraw(message, amount):
    user_id = message.from_user.id
    upi = message.text.strip()
    u = get_user(user_id)
    
    if u['balance'] < amount:
        bot.send_message(message.chat.id, "❌ Aparyapt balance.")
        return

    u['balance'] -= amount
    withdrawals.append({'user_id': user_id, 'amount': amount, 'upi': upi, 'status': 'Pending'})

    # Notify Admin
    bot.send_message(
        MAIN_ADMIN_ID,
        f"💸 *New Withdrawal Request!*\nUser ID: `{user_id}`\nAmount: ₹{amount}\nUPI: `{upi}`\n\nApprove karne ke liye command: `/approvew {user_id} {amount}`",
        parse_mode='Markdown'
    )
    bot.send_message(message.chat.id, "✅ Aapka withdrawal request submit ho gaya hai. Admin jald hi approve kar denge.")

@bot.message_handler(func=lambda m: m.text == '🤝 Refer')
def refer(message):
    user_id = message.from_user.id
    u = get_user(user_id)
    if u['banned']: return

    ref_link = f"https://t.me/{bot.get_me().username}?start={user_id}"
    text = (
        f"🤝 *Refer & Earn*\n\n"
        f"🔗 *Aapka invite link:*\n{ref_link}\n\n"
        f"✅ *Commission:* har referral ke approved task par 15.0%\n"
        f"👥 *Total Invites:* {u['referrals']}\n\n"
        "Dosto ko invite karke unke kamai ka commission payein!"
    )
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text == '🆘 Support')
def support(message):
    bot.send_message(message.chat.id, f"🆘 Kisi bhi problem ke liye contact karein: {SUPPORT_USERNAME}")

@bot.message_handler(func=lambda m: m.text == '📩 DM Admin / Gmail Query')
def dm_admin(message):
    msg = bot.send_message(message.chat.id, "📩 Admin ko apna message ya Gmail query likh kar bhejein:")
    bot.register_next_step_handler(msg, process_dm_to_admin)

def process_dm_to_admin(message):
    user_id = message.from_user.id
    user_msg = message.text
    bot.send_message(
        MAIN_ADMIN_ID,
        f"📩 *New DM from User!*\nUser ID: `{user_id}`\nName: {message.from_user.first_name}\n\nMessage:\n{user_msg}",
        parse_mode='Markdown'
    )
    bot.send_message(message.chat.id, "✅ Aapka message Admin ko bhej diya gaya hai!")

@bot.message_handler(func=lambda m: m.text == '📋 My Submitted')
def my_submitted(message):
    user_id = message.from_user.id
    user_subs = [s for s in submissions if s['user_id'] == user_id]
    
    if not user_subs:
        bot.send_message(message.chat.id, "📋 Aapne abhi tak koi task submit nahi kiya hai.")
        return

    text = "📋 *Your Submitted Tasks:*\n\n"
    for s in user_subs[-10:]:  # Show last 10
        status_icon = "⏳" if s['status'] == 'Pending' else ("✅" if s['status'] == 'Approved' else "❌")
        text += f"• {s['email']} – {status_icon} {s['status']}\n"
    
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

# ----------------- CALLBACK HANDLERS -----------------
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.from_user.id
    global current_create_task

    if call.data == "check_joined":
        if check_force_join(user_id):
            bot.answer_callback_query(call.id, "✅ Dhanyawad! Channel join ho gaya hai.", show_alert=True)
            bot.send_message(call.message.chat.id, "Ab aap bot ka upyog kar sakte hain!", reply_markup=main_keyboard(user_id))
        else:
            bot.answer_callback_query(call.id, "❌ Aapne abhi tak channel join nahi kiya hai!", show_alert=True)

    elif call.data == "sell_old_gmail":
        msg = bot.send_message(
            call.message.chat.id,
            f"📦 *Sold Old Gmail*\n\n💰 *Reward:* ₹{OLD_GMAIL_REWARD} per approved account\n\nApna Gmail address bhejein (example@gmail.com):",
            parse_mode='Markdown'
        )
        bot.register_next_step_handler(msg, process_old_gmail_email)

    elif call.data == "create_gmail_task":
        if not current_create_task:
            bot.answer_callback_query(call.id, "Abhi koi Create Gmail task available nahi hai! Baad me try karein.", show_alert=True)
            return

        if current_create_task['locked_by'] is not None and current_create_task['locked_by'] != user_id:
            bot.answer_callback_query(call.id, "Yeh task abhi kisi aur user ke dwara kiya ja raha hai!", show_alert=True)
            return

        current_create_task['locked_by'] = user_id
        current_create_task['locked_at'] = time.time()

        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("✅ Submit Proof", callback_data="submit_create_proof"),
            types.InlineKeyboardButton("❌ Cancel Task", callback_data="cancel_create_task")
        )

        text = (
            "✉️ *Create Gmail Task*\n\n"
            "📧 *Gmail ID* - aapne se rakh sakte ho\n"
            f"🔑 *Password* - `{current_create_task['password']}`\n"
            "📌 *Note* - must send the gmail id after creating the gmail\n\n"
            f"💰 *Reward:* ₹{CREATE_GMAIL_REWARD}\n\n"
            "⏱ Is task ko 15 minute ke andar complete karke Submit Proof karein."
        )
        bot.send_message(call.message.chat.id, text, parse_mode='Markdown', reply_markup=markup)

    elif call.data == "cancel_create_task":
        if current_create_task and current_create_task['locked_by'] == user_id:
            current_create_task['locked_by'] = None
            bot.send_message(call.message.chat.id, "❌ Task cancel kar diya gaya hai.")

    elif call.data == "submit_create_proof":
        msg = bot.send_message(call.message.chat.id, "Sahi Gmail address bhejein (example@gmail.com):")
        bot.register_next_step_handler(msg, process_create_gmail_submission)

# ----------------- SUBMISSION PROCESS -----------------
def process_old_gmail_email(message):
    email = message.text.strip()
    if "@gmail.com" not in email:
        msg = bot.send_message(message.chat.id, "⚠️ Sahi Gmail address bhejein (example@gmail.com):")
        bot.register_next_step_handler(msg, process_old_gmail_email)
        return
    
    msg = bot.send_message(message.chat.id, "🔑 Ab is Gmail ka password bhejein:")
    bot.register_next_step_handler(msg, process_old_gmail_password, email)

def process_old_gmail_password(message, email):
    password = message.text.strip()
    user_id = message.from_user.id
    
    u = get_user(user_id)
    u['pending'] += 1
    
    sub = {'user_id': user_id, 'type': 'Old Gmail', 'email': email, 'password': password, 'status': 'Pending'}
    submissions.append(sub)

    # Admin Alert
    bot.send_message(
        MAIN_ADMIN_ID,
        f"🔔 *New Old Gmail Submission!*\nUser ID: `{user_id}`\nGmail: `{email}`\nPass: `{password}`\n\nApprove: `/approve {user_id} {OLD_GMAIL_REWARD}`\nReject: `/reject {user_id}`",
        parse_mode='Markdown'
    )
    bot.send_message(message.chat.id, "✅ Aapki submission admin ko bhej di gayi hai.")

def process_create_gmail_submission(message):
    global current_create_task
    email = message.text.strip()
    user_id = message.from_user.id

    if "@gmail.com" not in email:
        msg = bot.send_message(message.chat.id, "⚠️ Sahi Gmail address bhejein (example@gmail.com):")
        bot.register_next_step_handler(msg, process_create_gmail_submission)
        return

    u = get_user(user_id)
    u['pending'] += 1

    password = current_create_task['password'] if current_create_task else "N/A"
    sub = {'user_id': user_id, 'type': 'Create Gmail', 'email': email, 'password': password, 'status': 'Pending'}
    submissions.append(sub)

    bot.send_message(
        MAIN_ADMIN_ID,
        f"🎉 *Create Gmail Task Completed!*\nUser ID: `{user_id}`\nGmail: `{email}`\nPass: `{password}`\n\nApprove: `/approve {user_id} {CREATE_GMAIL_REWARD}`\nReject: `/reject {user_id}`\n\n*Naya task set karne ke liye:* `/settask <password>`",
        parse_mode='Markdown'
    )

    current_create_task = None
    bot.send_message(message.chat.id, "✅ Aapka Create Gmail submission admin ko bhej diya gaya hai.")

# ----------------- ADMIN COMMANDS -----------------
@bot.message_handler(func=lambda m: m.text == '⚙️ Admin Panel' and m.from_user.id in admins)
def admin_panel(message):
    text = (
        "⚙️ *Admin Commands List:*\n\n"
        "1. `/settask <password>` -> Set new single-user Create Gmail Task\n"
        "2. `/clear` -> Unlock/delete current Create Task\n"
        "3. `/approve <user_id> <amount>` -> Approve task submission\n"
        "4. `/reject <user_id>` -> Reject task submission\n"
        "5. `/addbalance <user_id> <amount>` -> Add wallet balance\n"
        "6. `/cutbalance <user_id> <amount>` -> Cut wallet balance\n"
        "7. `/stats` -> View Bot Stats & Total Withdrawals\n"
        "8. `/totalwithdraw` -> View full withdrawal list\n"
        "9. `/addadmin <user_id>` -> Add new admin\n"
        "10. `/removeadmin <user_id>` -> Remove an admin\n"
        "11. `/adminlist` -> View current admins\n"
        "12. `/ban <user_id>` / `/unban <user_id>` -> Ban or Unban user\n"
        "13. `/broadcast <message>` -> Send message to all users"
    )
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

@bot.message_handler(commands=['settask'])
def set_task_cmd(message):
    global current_create_task
    if message.from_user.id not in admins: return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(message.chat.id, "Usage: `/settask <password>`", parse_mode='Markdown')
        return
    current_create_task = {'password': parts[1].strip(), 'locked_by': None, 'locked_at': None}
    bot.send_message(message.chat.id, f"✅ Task Set! Password: `{parts[1].strip()}`", parse_mode='Markdown')

@bot.message_handler(commands=['clear'])
def clear_task_cmd(message):
    global current_create_task
    if message.from_user.id not in admins: return
    current_create_task = None
    bot.send_message(message.chat.id, "✅ Task Cleared!")

@bot.message_handler(commands=['approve'])
def approve_cmd(message):
    if message.from_user.id not in admins: return
    parts = message.text.split()
    if len(parts) < 3: return
    uid, amt = int(parts[1]), float(parts[2])
    u = get_user(uid)
    u['balance'] += amt
    u['today'] += amt
    u['total'] += amt
    u['completed'] += 1
    if u['pending'] > 0: u['pending'] -= 1
    
    for s in submissions:
        if s['user_id'] == uid and s['status'] == 'Pending':
            s['status'] = 'Approved'
            break

    bot.send_message(uid, f"🎉 Aapka Gmail submission approve ho gaya hai! ₹{amt} aapke wallet mein add kar diye gaye hain.")
    bot.send_message(message.chat.id, f"✅ Approved User {uid} (+₹{amt})")

@bot.message_handler(commands=['reject'])
def reject_cmd(message):
    if message.from_user.id not in admins: return
    parts = message.text.split()
    if len(parts) < 2: return
    uid = int(parts[1])
    u = get_user(uid)
    u['rejected'] += 1
    if u['pending'] > 0: u['pending'] -= 1
    
    for s in submissions:
        if s['user_id'] == uid and s['status'] == 'Pending':
            s['status'] = 'Rejected'
            break

    bot.send_message(uid, "❌ Aapka Gmail submission reject kar diya gaya hai.")
    bot.send_message(message.chat.id, f"❌ Rejected User {uid}")

@bot.message_handler(commands=['addbalance'])
def addbal_cmd(message):
    if message.from_user.id not in admins: return
    parts = message.text.split()
    if len(parts) < 3: return
    uid, amt = int(parts[1]), float(parts[2])
    get_user(uid)['balance'] += amt
    bot.send_message(message.chat.id, f"✅ Added ₹{amt} to User {uid}")

@bot.message_handler(commands=['cutbalance'])
def cutbal_cmd(message):
    if message.from_user.id not in admins: return
    parts = message.text.split()
    if len(parts) < 3: return
    uid, amt = int(parts[1]), float(parts[2])
    get_user(uid)['balance'] -= amt
    bot.send_message(message.chat.id, f"✅ Deducted ₹{amt} from User {uid}")

@bot.message_handler(commands=['stats'])
def stats_cmd(message):
    if message.from_user.id not in admins: return
    tot_w = sum(w['amount'] for w in withdrawals if w['status'] == 'Approved')
    bot.send_message(
        message.chat.id,
        f"📊 *Bot Statistics*\n\nTotal Users: {len(users)}\nTotal Submissions: {len(submissions)}\nTotal Approved Withdrawals: ₹{tot_w}",
        parse_mode='Markdown'
    )

@bot.message_handler(commands=['totalwithdraw'])
def total_withdraw_cmd(message):
    if message.from_user.id not in admins: return
    if not withdrawals:
        bot.send_message(message.chat.id, "Abhi tak koi withdrawal nahi hua hai.")
        return
    text = "💳 *All Withdrawal Requests:*\n\n"
    for w in withdrawals:
        text += f"User: `{w['user_id']}` | Amount: ₹{w['amount']} | Status: {w['status']}\n"
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

@bot.message_handler(commands=['addadmin'])
def addadmin_cmd(message):
    if message.from_user.id != MAIN_ADMIN_ID: return
    parts = message.text.split()
    if len(parts) < 2: return
    admins.add(int(parts[1]))
    bot.send_message(message.chat.id, f"✅ New Admin Added: `{parts[1]}`", parse_mode='Markdown')

@bot.message_handler(commands=['removeadmin'])
def rmadmin_cmd(message):
    if message.from_user.id != MAIN_ADMIN_ID: return
    parts = message.text.split()
    if len(parts) < 2: return
    aid = int(parts[1])
    if aid != MAIN_ADMIN_ID and aid in admins:
        admins.remove(aid)
        bot.send_message(message.chat.id, f"✅ Admin Removed: `{aid}`", parse_mode='Markdown')

@bot.message_handler(commands=['adminlist'])
def adminlist_cmd(message):
    if message.from_user.id not in admins: return
    text = "👑 *Admins List:*\n\n" + "\n".join(f"• `{a}`" for a in admins)
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

@bot.message_handler(commands=['ban'])
def ban_cmd(message):
    if message.from_user.id not in admins: return
    parts = message.text.split()
    if len(parts) < 2: return
    get_user(int(parts[1]))['banned'] = True
    bot.send_message(message.chat.id, f"🚫 User `{parts[1]}` Banned!", parse_mode='Markdown')

@bot.message_handler(commands=['unban'])
def unban_cmd(message):
    if message.from_user.id not in admins: return
    parts = message.text.split()
    if len(parts) < 2: return
    get_user(int(parts[1]))['banned'] = False
    bot.send_message(message.chat.id, f"✅ User `{parts[1]}` Unbanned!", parse_mode='Markdown')

@bot.message_handler(commands=['broadcast'])
def broadcast_cmd(message):
    if message.from_user.id not in admins: return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2: return
    bmsg = parts[1]
    count = 0
    for uid in users:
        try:
            bot.send_message(uid, f"📢 *Announcement:*\n\n{bmsg}", parse_mode='Markdown')
            count += 1
        except:
            pass
    bot.send_message(message.chat.id, f"✅ Broadcast sent to {count} users.")

print("Bot is running...")
bot.infinity_polling()

