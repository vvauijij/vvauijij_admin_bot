import collections

import telebot
from telebot import types

import re


class INFO:
    def __init__(self) -> None:
        self.chat_users = collections.defaultdict(dict)
        self.chat_titles = collections.defaultdict(int)
        self.usernames = set()
        self.user_ids = set()
        self.messages = set()

    def update_info(self, message) -> None:
        user_id = message.from_user.id
        username = '@' + message.from_user.username

        chat_id = message.chat.id
        chat_title = '@' + message.chat.title

        self.chat_users[chat_id][username] = user_id
        self.chat_titles[chat_title] = chat_id
        self.usernames.add(username)
        self.user_ids.add(user_id)


info = INFO()

TOKEN = ''
bot = telebot.TeleBot(TOKEN)


def get_handle(query) -> str:
    handle = re.search('@.+', query.query)
    if handle:
        return handle.group(0)
    else:
        return ''


@bot.message_handler(content_types=['new_chat_members'])
def new_member(message) -> None:
    info.update_info(message)
    username = message.json["new_chat_participant"]["username"]
    if username == 'vvauijij_admin_bot':
        bot.send_message(message.chat.id,
                         f'hello!\n'
                         f'to access all commands please give me FULL ADMIN RIGHTS in chat\n\n'
                         f'to ban/unban/promote/demote user or to kick me you need the appropriate rights\n'
                         f'user can be baned/unbanned/promoted/demoted '
                         f'only after initializing (sending message) in chat\n\n'
                         f'chat info is accessible only after any message is sent\n'
                         f'after renaming chat participants will be visible for me only after reinitializing\n\n'
                         f'type @vvauijij_admin_bot inline to see commands list')
    else:
        info.messages.add(bot.send_message(message.chat.id,
                                           f'hello @{username}!'
                                           f' i got black, i got white, what you want?').id)


@bot.message_handler(content_types=['text',
                                    'audio',
                                    'document',
                                    'photo',
                                    'sticker',
                                    'video',
                                    'video_note',
                                    'voice',
                                    'location',
                                    'contact'])
def update_info(message):
    if (message.reply_to_message and message.reply_to_message.id in info.messages
            and message.from_user.id not in info.user_ids):
        bot.reply_to(message, 'yall right')

    info.update_info(message)


def is_ban_command(query) -> bool:
    return bool(re.search('^/ban @', query.query))


def can_restrict(query, chat_id) -> bool:
    ban_permission = set()
    for user in bot.get_chat_administrators(chat_id):
        if user.status == 'creator' or user.can_restrict_members:
            ban_permission.add(user.user.id)
    return query.from_user.id in ban_permission


@bot.inline_handler(is_ban_command)
def ban(query):
    handle = get_handle(query)
    if handle not in info.usernames:
        ban_query_info = types.InlineQueryResultArticle(
            id=1,
            title='you are about to ban someone',
            description='after completing "/ban @username"'
                        ' user will be banned in all possible chats',
            input_message_content=types.InputTextMessageContent(
                message_text='ban failed: to ban user in all possible chats'
                             ' complete "/ban @username" inline'))

        bot.answer_inline_query(query.id, [ban_query_info])
    else:
        bans_amount = 0
        for [chat_id, chat_members] in info.chat_users.items():
            if can_restrict(query, chat_id):
                try:
                    bot.ban_chat_member(chat_id, chat_members[handle])
                    bans_amount += 1
                except Exception:
                    pass

        ban_result_info = types.InlineQueryResultArticle(
            id=1,
            title=f'{handle} was banned in {bans_amount} chat(s)',
            description='',
            input_message_content=types.InputTextMessageContent(
                message_text=f'{handle} was banned in {bans_amount} chat(s)'))

        bot.answer_inline_query(query.id, [ban_result_info])


def is_unban_command(query) -> bool:
    return bool(re.search('^/unban @', query.query))


@bot.inline_handler(is_unban_command)
def unban(query):
    handle = get_handle(query)
    if handle not in info.usernames:
        unban_query_info = types.InlineQueryResultArticle(
            id=1,
            title="you are about to unban someone",
            description='after completing "/unban @username"'
                        ' user will be unbanned in all possible chats',
            input_message_content=types.InputTextMessageContent(
                message_text='unban failed: to unban user in all possible chats'
                             ' complete "/unban @username" inline'))
        bot.answer_inline_query(query.id, [unban_query_info])
    else:
        unbans_amount = 0
        for [chat_id, chat_members] in info.chat_users.items():
            if can_restrict(query, chat_id):
                try:
                    bot.unban_chat_member(chat_id, chat_members[get_handle(query)], only_if_banned=True)
                    unbans_amount += 1
                except Exception:
                    pass

        unban_result_info = types.InlineQueryResultArticle(
            id=1,
            title=f'{handle} was unbanned in {unbans_amount} chat(s)',
            description='',
            input_message_content=types.InputTextMessageContent(
                message_text=f'{handle} was unbanned in {unbans_amount} chat(s)'))

        bot.answer_inline_query(query.id, [unban_result_info])


def is_promote_command(query) -> bool:
    return bool(re.search('^/promote @', query.query))


def can_promote(query, chat_id) -> bool:
    promote_permission = set()
    for user in bot.get_chat_administrators(chat_id):
        if user.status == 'creator' or user.can_promote_members:
            promote_permission.add(user.user.id)
    return query.from_user.id in promote_permission


@bot.inline_handler(is_promote_command)
def promote(query):
    handle = get_handle(query)
    if handle not in info.usernames:
        promote_query_info = types.InlineQueryResultArticle(
            id=1,
            title="you are about to promote someone",
            description='after completing "/promote @username"'
                        ' user will be promoted in all possible chats',
            input_message_content=types.InputTextMessageContent(
                message_text='promote failed: to unban user in all possible chats'
                             ' complete "/promote @username" inline'))
        bot.answer_inline_query(query.id, [promote_query_info])
    else:
        promotes_amount = 0
        for [chat_id, chat_members] in info.chat_users.items():
            if can_promote(query, chat_id):
                try:
                    bot.promote_chat_member(chat_id,
                                            chat_members[get_handle(query)],
                                            can_manage_chat=True,
                                            can_post_messages=True,
                                            can_edit_messages=True,
                                            can_delete_messages=True,
                                            can_manage_video_chats=True,
                                            can_restrict_members=True,
                                            can_promote_members=True,
                                            can_change_info=True,
                                            can_invite_users=True
                                            )
                    promotes_amount += 1
                except Exception:
                    pass

        promote_result_info = types.InlineQueryResultArticle(
            id=1,
            title=f'{handle} was promoted in {promotes_amount} chat(s)',
            description='',
            input_message_content=types.InputTextMessageContent(
                message_text=f'{handle} was promoted in {promotes_amount} chat(s)'))

        bot.answer_inline_query(query.id, [promote_result_info])


def is_demote_command(query) -> bool:
    return bool(re.search('^/demote @', query.query))


@bot.inline_handler(is_demote_command)
def demote(query):
    handle = get_handle(query)
    if handle not in info.usernames:
        demote_query_info = types.InlineQueryResultArticle(
            id=1,
            title="you are about to demote someone",
            description='after completing "/demote @username"'
                        ' user will be demoted in all possible chats',
            input_message_content=types.InputTextMessageContent(
                message_text='demote failed: to demote user in all possible chats'
                             ' complete "/demote @username" inline'))
        bot.answer_inline_query(query.id, [demote_query_info])
    else:
        demotes_amount = 0
        for [chat_id, chat_members] in info.chat_users.items():
            if can_promote(query, chat_id):
                try:
                    bot.promote_chat_member(chat_id,
                                            chat_members[get_handle(query)],
                                            can_manage_chat=False,
                                            can_post_messages=False,
                                            can_edit_messages=False,
                                            can_delete_messages=False,
                                            can_manage_video_chats=False,
                                            can_restrict_members=False,
                                            can_promote_members=False,
                                            can_change_info=False,
                                            can_invite_users=False
                                            )
                    demotes_amount += 1
                except Exception:
                    pass

        demote_result_info = types.InlineQueryResultArticle(
            id=1,
            title=f'{handle} was demoted in {demotes_amount} chat(s)',
            description='',
            input_message_content=types.InputTextMessageContent(
                message_text=f'{handle} was demoted in {demotes_amount} chat(s)'))

        bot.answer_inline_query(query.id, [demote_result_info])


def is_info_command(query) -> bool:
    return bool(re.search('^/info @', query.query))


@bot.inline_handler(is_info_command)
def chat_info(query):
    chat_title = get_handle(query)
    if chat_title not in info.chat_titles.keys():
        invalid_chat_info = types.InlineQueryResultArticle(
            id=1,
            title='you are about to see chat information',
            description='complete "/info @chat_title" inline to see chat information',
            input_message_content=types.InputTextMessageContent(
                message_text='no chat with such title: to see chat information complete "/info @chat_title" inline'))
        bot.answer_inline_query(query.id, [invalid_chat_info])
    else:
        valid_chat_info = types.InlineQueryResultArticle(
            id=1,
            title=f'{chat_title} info: '
                  f'members: {bot.get_chat_member_count(info.chat_titles[chat_title])} '
                  f'admins: {len(bot.get_chat_administrators(info.chat_titles[chat_title]))}',
            description='',
            input_message_content=types.InputTextMessageContent(
                message_text=f'{chat_title} info: '
                             f'members: {bot.get_chat_member_count(info.chat_titles[chat_title])} '
                             f'admins: {len(bot.get_chat_administrators(info.chat_titles[chat_title]))}'))

        bot.answer_inline_query(query.id, [valid_chat_info])


def is_kick_bot_command(query) -> bool:
    return bool(re.search('^/kick_bot @', query.query))


@bot.inline_handler(is_kick_bot_command)
def kick_bot(query) -> None:
    chat_title = get_handle(query)

    if chat_title not in info.chat_titles.keys() or not can_restrict(query, info.chat_titles[chat_title]):
        invalid_kick_bot = types.InlineQueryResultArticle(
            id=1,
            title='you are about to kick this bot from chat',
            description='complete "/kick_bot @chat_title" inline to kick this bot from chat',
            input_message_content=types.InputTextMessageContent(
                message_text='you have no rights or there is no chat with such title:'
                             ' to kick this bot from chat complete "/kick_bot @chat_title" inline'))
        bot.answer_inline_query(query.id, [invalid_kick_bot])
    else:
        bot.leave_chat(info.chat_titles[chat_title])
        valid_kick_bot = types.InlineQueryResultArticle(
            id=1,
            title=f'bot kicked from {chat_title}',
            description='',
            input_message_content=types.InputTextMessageContent(
                message_text=f'bot kicked from {chat_title}'))

        bot.answer_inline_query(query.id, [valid_kick_bot])


def is_manual_command(query) -> bool:
    return not (is_ban_command(query) or
                is_unban_command(query) or
                is_promote_command(query) or
                is_demote_command(query) or
                is_info_command(query) or
                is_kick_bot_command(query))


@bot.inline_handler(is_manual_command)
def manual(query) -> None:
    manual_text = types.InlineQueryResultArticle(
        id=1,
        title='commands list',
        description='click here to see commands list',
        input_message_content=types.InputTextMessageContent(
            message_text='complete "/ban @username" inline to ban user in all possible chats\n'
                         'complete "/unban @username" inline to unban user in all possible chats\n'
                         'complete "/promote @username" inline to promote user in all possible chats\n'
                         'complete "/demote @username" inline to demoted user in all possible chats\n'
                         'complete "/info @chat_title" inline to see chat information\n'
                         'complete "/kick_bot @chat_title" inline to kick bot from chat'))

    bot.answer_inline_query(query.id, [manual_text])


bot.polling(none_stop=True, interval=0)
