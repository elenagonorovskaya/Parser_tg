#Парсинг названия каналов, участников и сообщений из выбранной группы

import csv
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import InputPeerEmpty
from telethon.tl.types import PeerChannel
import asyncio
from telethon.tl.types import ChannelParticipantsSearch

api_id = 'my_id'
api_hash = 'my_hash'
phone = 'my_phone'
client = TelegramClient(phone, api_id, api_hash)

#сохраняем подписчиков в чате
def output_participants(all_participants, target_group):
    with open("member.csv", "w", encoding='UTF-8') as f:
        writer = csv.writer(f, delimiter=",", lineterminator="\n")
        writer.writerow(['№', 'id', 'usesrname', 'Фамилия', 'Имя', 'Телефон', 'Название канала'])
        i = 1
        for user in all_participants:
            writer.writerow([i, user.id, user.username,
                             user.first_name,
                             user.last_name, user.phone,
                             target_group.title])
            i += 1

#сохраняем сообщения в чате
def output_messages(all_messages, target_group):
    print('выводим сообщения из чата', target_group)
    with open("messages.csv", "w", encoding='UTF-8') as f:
        writer = csv.writer(f, delimiter=",", lineterminator="\n")
        writer.writerow(['Дата', 'id отправителя', 'Сообщение', 'Название чата'])
        for mess in all_messages:
            if 'message' in mess:
                writer.writerow([
                    mess['date'],
                    mess['from_id']['user_id'],
                    mess['message'],
                    target_group
                ])


async def main():
    await client.start()

    chats = []
    last_date = None
    size_chats = 200
    groups = []

    result = await client(GetDialogsRequest(offset_date=last_date,
                                       offset_id = 0,
                                       offset_peer = InputPeerEmpty(),
                                       limit = size_chats,
                                       hash = 0
                                       ))
    chats.extend(result.chats)

    number_chat = 0
    for c in chats:
        if c.title == 'Группа':
            number_chat += 1
            break
        #print(number_chat, ": ", c.title)
        number_chat += 1

    g_index = number_chat - 1
    target_group = chats[int(g_index)]
    print('Выбранный чат:', target_group.title)

    all_participants = []
    all_participants = await client.get_participants(target_group, aggressive=True)
    output_participants(all_participants, target_group)

    all_messages = []
    limit = 100
    offset_id = 0
    total_messages = 0
    total_count_limit = 0

    while True:
        history = await client(GetHistoryRequest(
            peer = target_group,
            offset_id = offset_id,
            offset_date = None,
            add_offset = 0,
            limit = limit,
            max_id = 0,
            min_id = 0,
            hash = 0
        ))
        if not history.messages:
            break
        messages = history.messages
        for message in messages:
            all_messages.append(message.to_dict())
        offset_id = messages[len(messages)-1].id
        if total_count_limit != 0  and total_messages >= total_count_limit:
            break

    output_messages(all_messages, target_group.title)

    #можно парсить подписчиков и таким образом
    # offset_user = 0
    # limit_user = 100
    # all_participants = []
    # filter_user = ChannelParticipantsSearch('')
    # while True:
    #     participants = client(GetDialogsRequest(
    #         channel = target_group,
    #         filter = filter_user,
    #         offset = offset_user,
    #         limit = limit_user,
    #         hash = 0
    #     ))
    #     if not participants.users:
    #         break
    #     print('yeees')
    #     all_participants.extend(participants.users)
    #     offset_user += len(participants.users)

    # await client.send_message('Группа', 'выводим сообщение в группу')
    # client.parse_mode = 'html'
    # await client.send_message('me', '<a href="tg://user?id=me">Mentions</a>')
    #либо вот так
    #await client.send_message('Группа', '<i>Я здесь буду делать бота и изучать питон</i> и вот ссылка на <a href="https://www.google.ru">google</a>', parse_mode='html')

with client:
    client.loop.run_until_complete(main())

# if __name__ == '__main__':
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(main())
#     #asyncio.run(main())

