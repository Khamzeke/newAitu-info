import asyncio
import random
from datetime import timedelta, timezone, datetime

import aioschedule as aioschedule
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove, ChatPermissions
from aiogram.utils.deep_linking import get_start_link, decode_payload
from aiogram.utils.exceptions import MessageCantBeDeleted, MessageCantBeEdited, MessageNotModified

import config
import database
import functions
from config import rules
from functions import head, userState, admin_state

dt = datetime.now(timezone(timedelta(hours=+6), 'NQZ'))

spam_users = []

usersToSee = {}
rulesBtn = InlineKeyboardButton("Правила", callback_data='rules:1')
getMainMenuBtn = InlineKeyboardButton('Главное меню', callback_data='profile:back')

bot = Bot(token=config.TOKEN, parse_mode='HTML')
dp = Dispatcher(bot, storage=MemoryStorage())

black_list_statuses = ['declined', 'in_process', 'waiting']

unregged_users = {}

not_delivered = []
delivered = True


async def setTime():
    global dt
    while True:
        await asyncio.sleep(1)
        dt = datetime.now(timezone(timedelta(hours=+6), 'NQZ'))


@dp.message_handler(commands=['start', 'help'], state='*')
async def start(message: types.Message):
    user = database.getUser(message.from_user.id)
    if message.chat.type == 'private':
        args = message.get_args()
        group_id = decode_payload(args)
        if group_id == '':
            if user is not None and user[3] not in black_list_statuses:
                profileBtn = InlineKeyboardButton('Мой профиль', callback_data='profile:show')
                groupBtn = InlineKeyboardButton('Моя группа', callback_data='mygroup:show')
                kb = InlineKeyboardMarkup(row_width=1).add(*[profileBtn, groupBtn, rulesBtn])
                if user[0] in config.ADMINS:
                    adminBtn = InlineKeyboardButton('Администрирование', callback_data='admin:menu')
                    kb.add(adminBtn)
                if database.getSupergroupsOfUser(user[0]):
                    supergroupBtn = InlineKeyboardButton('Мои супергруппы', callback_data='mysupergroup:show')
                    kb.add(supergroupBtn)
                if user[1] == 'head':
                    await message.answer('Здравствуйте, староста, чем могу помочь?', reply_markup=kb)
                elif user[1] == 'student':
                    await message.answer('Привет, чем могу помочь?', reply_markup=kb)
                return

            await message.answer(
                'Привет, это AITU INFO BOT. Благодаря мне ты сможешь пользоваться многими функциями, например:\n'
                '1. Функция зазывалы\n'
                '2. Своевременное уведомление о предстоящих днях рождениях своих одногруппников\n'
                '3. Рассылка от имени бота своим одногруппникам (доступно только старосте)\n'
                '4. Возможность узнавать о желании своих одногруппников на их день рождения\n'
                'Скорее добавляй меня в свою группу и регистрируй ее!\n\n'
                '<b>Бот предназначен только для пользования студентами AITU!</b>', parse_mode='HTML')
        else:
            num_of_students = await bot.get_chat_members_count(group_id)
            if num_of_students <= 30:
                group_type = 'group'
            else:
                group_type = 'supergroup'
            if user is not None and group_type == 'group':
                if user[3] == 'declined' and user[2] == int(group_id):
                    await message.answer('Повторите попытку через некоторое время, бот уведомит Вас об этом.')
                    return
                elif user[3] == 'in_process':
                    database.deleteUser(message.from_user.id)
                elif user[3] == 'waiting' and user[2] == int(group_id):
                    await message.answer('Заявка уже отправлена, прошу подождать пока староста рассмотрит Вашу заявку!')
                    return
                elif user[3] == 'waiting' and user[2] != int(group_id):
                    group = database.getHeadOfGroup(user[2])
                    cancelBtn = InlineKeyboardButton('Отменить заявку',
                                                     callback_data=f'apply_cancel:{user[0]}:{group[0]}')
                    await message.answer(f'Вы уже отправили заявку на вступлению в группу {group[3]}.\n'
                                         f'Вы хотите отменить заявку?',
                                         reply_markup=InlineKeyboardMarkup().add(cancelBtn))
                    return
                elif user[3] == 'active' and user[2] == int(group_id):
                    if user[1] == 'head':
                        await message.answer('Вы уже зарегистрировались как староста этой группы!')
                    elif user[1] == 'student':
                        await message.answer('Вы уже зарегистрировались как студент этой группы!')
                    return
                elif user[3] == 'active' and user[2] != int(group_id):
                    if user[1] == 'head':
                        await message.answer('Вы уже зарегистрировались как староста другой группы!')
                    elif user[1] == 'student':
                        await message.answer('Вы уже зарегистрировались как студент другой группы!')
                    return
            result = database.addUser(message.from_user.id, group_id, message.from_user.first_name)
            print(result)
            if result == 'Success!':
                group = database.getHeadOfGroup(group_id)
                database.addUserToGroup(group_id, message.from_user.id)
                try:
                    studentBtn = InlineKeyboardButton(text='Профиль студента',
                                                      url=f'tg://user?id={message.from_user.id}')
                    acceptBtn = InlineKeyboardButton('✅', callback_data=f'decision:accept:{message.from_user.id}')
                    declineBtn = InlineKeyboardButton('❌', callback_data=f'decision:decline:{message.from_user.id}')
                    kb = InlineKeyboardMarkup().add(*[acceptBtn, declineBtn])
                    kb.add(studentBtn)
                    await bot.send_message(group[1], f"Привет, староста!\n"
                                                     f"<a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a> подал заявку "
                                                     f"на вступление в {group[3]}",
                                           parse_mode='HTML', reply_markup=kb)
                    await message.answer(f'Заявка на вступлению в группу {group[3]} отправлена!')
                except:
                    try:
                        await bot.send_message(group[0], f"Не удаётся отправить сообщение старосте!")
                    except:
                        await bot.send_message(config.GLOBAL_ADMIN,
                                               f"Не удаётся отправить сообщение ни <a href='tg://user?id={group[1]}'>старосте</a>, ни <a href='tg://user?id={group[1]}'>группе</a>",
                                               parse_mode='HTML')
            if result == "Group doesn't exist!":
                if group_type == 'group':
                    register_group_btn = InlineKeyboardButton('Зарегистрировать',
                                                              callback_data=f"register_group:{group_id}")
                    await message.answer("Ваша группа ещё не зарегистрирована, если Вы староста, "
                                         "то зарегистрируйте её!",
                                         reply_markup=InlineKeyboardMarkup().add(register_group_btn))
                else:
                    supergroup = database.getSupergroup(group_id)
                    if supergroup is None:
                        register_group_btn = InlineKeyboardButton('Зарегистрировать',
                                                                  callback_data=f"register_supergroup:{group_id}")
                        await message.answer("Зарегистрируйте супергруппу.",
                                             reply_markup=InlineKeyboardMarkup().add(register_group_btn))
                    else:
                        profileBtn = InlineKeyboardButton('Менеджер группы', url=f'tg://user?id={supergroup[4]}')
                        await message.answer("Супергруппа уже зарегистрирована!",
                                             reply_markup=InlineKeyboardMarkup().add(profileBtn))
            if result == "Something went wrong!":
                await message.answer(
                    f'Произошла ошибка, обратитесь к <a href="tg://user?id={config.GLOBAL_ADMIN}">администратору</a>',
                    parse_mode='HTML')
    else:
        if user is not None and user[3] not in black_list_statuses:
            callAllBtn = InlineKeyboardButton('Позвать всех!', callback_data=f'command:all:{message.chat.id}')
            interestingBtn = InlineKeyboardButton('Актуальные вопросы', callback_data='mygroup:interesting')
            group = database.getHeadOfGroup(message.chat.id)
            kb = InlineKeyboardMarkup(row_width=1).add(*[callAllBtn, interestingBtn])
            if group is None:
                group = database.getSupergroup(message.chat.id)
                if group is None:
                    link = await get_start_link(message.chat.id, encode=True)
                    register_btn = InlineKeyboardButton('Зарегистрировать группу', url=f"{link}",
                                                        callback_data=f'register:{message.chat.id}')
                    kb.add(register_btn)
            await message.answer('Привет, это AITU INFO BOT', reply_markup=kb)
            return
        num_of_students = await bot.get_chat_members_count(message.chat.id)
        link = await get_start_link(message.chat.id, encode=True)
        register_btn = InlineKeyboardButton('Регистрация', url=f"{link}",
                                            callback_data=f'register:{message.chat.id}')
        if num_of_students <= 30:
            await message.answer('Привет, нажми ниже чтобы зарегистрироваться!',
                                 reply_markup=InlineKeyboardMarkup().add(register_btn))
        else:
            await message.answer('<b>Данная группа может быть зарегистрирована лишь как супергруппа.</b>\n'
                                 'Если Вы считаете что это ошибка, обратитесь к @aitu_h.',
                                 reply_markup=InlineKeyboardMarkup().add(register_btn))


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('register_supergroup:'), state='*')
async def registerSuperGroup(callback_query: types.CallbackQuery, state: FSMContext):
    group_id = int(callback_query.data.replace('register_supergroup:', ''))
    supergroup = database.getSupergroup(group_id)
    if supergroup is not None:
        managerOfGroup = InlineKeyboardButton('Менеджер группы', url=f'tg://user?id={supergroup[4]}')
        await callback_query.message.edit_text('Супергруппа уже зарегистрирована!\n'
                                               f'Менеджер группы', parse_mode='HTML',
                                               reply_markup=InlineKeyboardMarkup().add(managerOfGroup))
        await state.finish()
        return

    user = database.getUser(callback_query.from_user.id)
    if user is None:
        await callback_query.message.edit_text(
            '<b>Вы не являетесь студентом группы</b> \nРегистрация супергруппы невозможна.')
        return

    supergroup = await bot.get_chat(group_id)

    result = database.addSuperGroup(supergroup, callback_query.from_user.id)
    if result:
        database.addUserToGroup(group_id, callback_query.from_user.id)
        await callback_query.message.answer('Супергруппа успешно зарегистрирована!')
        deleteBtn = InlineKeyboardButton('Удалить', callback_data=f"supergroup:{group_id}:delete")
        acceptBtn = InlineKeyboardButton('Принять', callback_data=f"supergroup:{group_id}:accept")
        profileBtn = InlineKeyboardButton('Менеджер', url=f'tg://user?id={callback_query.from_user.id}')
        kb = InlineKeyboardMarkup(row_width=2).add(profileBtn)
        kb.add(*[acceptBtn, deleteBtn])
        print(config.ADMINS)
        for admin in config.ADMINS:
            try:
                await bot.send_message(admin,
                                       f'Была создана новая супергруппа под названием {supergroup.title}',
                                       reply_markup=kb)
            except:
                adminBtn = InlineKeyboardButton('Администратор', url=f'tg://user?id={admin}')
                await bot.send_message(config.GLOBAL_ADMIN,
                                       f'Не удаётся связаться с администратором <b>{admin}</b>',
                                       reply_markup=InlineKeyboardMarkup().add(adminBtn), parse_mode='HTML')
        try:
            await bot.send_message(group_id,
                                   f'Супергруппа зарегистрирована под названием {supergroup.title}')
        except:
            await callback_query.message.answer('Не удаётся отправить сообщение в вашу группу!')
            print("[ERROR] Cannot send 'created' notification to group")
        await asyncio.sleep(1.8)
        await callback_query.message.edit_text('Супергруппа успешно зарегистрирована!\n\n'
                                               'Перед использованием бота настоятельно рекомендуем '
                                               'прочитать <b>Правила и обязательства</b> сторон',
                                               parse_mode='HTML',
                                               reply_markup=InlineKeyboardMarkup().add(rulesBtn))


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('admin:'), state='*')
async def admin(callback_query: types.CallbackQuery, state: FSMContext):
    global delivered
    global not_delivered
    user = database.getUser(callback_query.from_user.id)
    if user is not None and user[3] not in black_list_statuses and user[0] in config.ADMINS:
        decision = callback_query.data.split(':')
        admin = database.getAdmin(user[0])
        if decision[1] == 'menu':
            await state.finish()
            now_hour = dt.hour
            if 18 <= now_hour <= 23:
                greeting = "Добрый вечер, "
            elif 0 <= now_hour <= 4:
                greeting = "Доброй ночи, "
            elif 5 <= now_hour <= 11:
                greeting = "Доброе утро, "
            else:
                greeting = "Добрый день, "
            kb = InlineKeyboardMarkup(row_width=1)
            group = database.getHeadOfGroup(user[2])
            if admin[2] is True:
                logsBtn = InlineKeyboardButton('Логи', callback_data='admin:logs')
                addAdminBtn = InlineKeyboardButton('Добавить администратора', callback_data='admin:add_admin')
                adminsLsBtn = InlineKeyboardButton('Список администраторов', callback_data='admin:list_of_admins')
                kb.add(*[logsBtn, addAdminBtn, adminsLsBtn])
            groupsBtn = InlineKeyboardButton('Группы', callback_data='admin:groups')
            questionsBtn = InlineKeyboardButton('Вопросы', callback_data='admin:questions')
            deleteUserBtn = InlineKeyboardButton('Удалить студента', callback_data='admin:delete_student')
            messageBtn = InlineKeyboardButton('Рассылка', callback_data='admin:message')
            kb.add(*[deleteUserBtn, groupsBtn, questionsBtn, messageBtn, getMainMenuBtn])
            text = f"{greeting}<a href='tg://user?id={user[0]}'>{user[6]}</a>! \n" \
                   f"Ваш профиль:\n" \
                   f"1. Ваш ID: {admin[1]}\n" \
                   f"2. {group[2]} курс\n"
            await callback_query.message.edit_text(text, parse_mode='HTML', reply_markup=kb)
        if decision[1] == 'logs':
            await callback_query.answer('Скоро')
        if decision[1] == 'add_admin':
            await callback_query.answer('Скоро')
        if decision[1] == 'list_of_admins':
            await callback_query.answer('Скоро')
        if decision[1] == 'groups':
            await callback_query.answer('Скоро')
        if decision[1] == 'questions':
            await callback_query.answer('Скоро')
        if decision[1] == 'delete_student':
            await callback_query.answer('Скоро')
        if decision[1] == 'message':
            first_course_btn = InlineKeyboardButton('Первый курс', callback_data='admin_message:1')
            second_course_btn = InlineKeyboardButton('Второй курс', callback_data='admin_message:2')
            third_course_btn = InlineKeyboardButton('Третий курс', callback_data='admin_message:3')
            backBtn = InlineKeyboardButton('Назад', callback_data='admin:menu')
            kb = InlineKeyboardMarkup(row_width=1).add(
                *[first_course_btn, second_course_btn, third_course_btn, backBtn])
            async with state.proxy() as data:
                data['callback'] = await callback_query.message.edit_text(
                    'Ваш текст:\n\nДля кого предназначена рассылка?',
                    reply_markup=kb)
                data['1'] = first_course_btn
                data['2'] = second_course_btn
                data['3'] = third_course_btn
                data['courses'] = []
                data['media'] = []
            await admin_state.Message.set()
        if decision[1] == 'send_message':
            if decision[2] == 'None':
                usersBtn = InlineKeyboardButton('В личные сообщения', callback_data='admin:send_message:ls')
                chatBtn = InlineKeyboardButton('В беседы групп', callback_data='admin:send_message:chat')
                await callback_query.message.edit_text('Куда отправить сообщение?',
                                                       reply_markup=InlineKeyboardMarkup(row_width=1).add(
                                                           *[usersBtn, chatBtn]))
            else:
                async with state.proxy() as data:
                    msg = data.get('msg')
                    if msg is None:
                        backBtn = InlineKeyboardButton('Назад', callback_data='admin:menu')
                        await callback_query.message.edit_text('Истекло время ожидания..',
                                                               reply_markup=InlineKeyboardMarkup().add(backBtn))
                        return
                    await callback_query.message.edit_text('Отправка..')
                    if len(data['courses']) > 1:
                        groups = database.getGroupsForAdmin(tuple(data['courses']))
                    elif len(data['courses']) == 1:
                        groups = database.getGroupsForAdmin(data['courses'][0])
                    else:
                        groups = database.getGroupsForAdmin(None)
                    if decision[2] == 'ls':
                        delivered = True
                        not_delivered = []
                        for group in groups:
                            await asyncio.sleep(0.3)
                            asyncio.create_task(sendMessageToGroupUsers(group[0], msg))
                        await asyncio.sleep(2)

                        text = 'Сообщение доставлено всем!'
                        if not delivered:
                            text = 'Сообщение не было доставлено студентам:\n'
                            for student in not_delivered:
                                text += f'{student[0]} {student[6]}\n'
                        await callback_query.message.edit_text(text)
                        await state.finish()
                    if decision[2] == 'chat':
                        delivered = True
                        not_delivered = []
                        for group in groups:
                            await asyncio.sleep(0.2)
                            try:
                                await bot.send_message(group[0], msg)
                            except:
                                delivered = False
                                not_delivered.append(group)
                        text = 'Сообщение доставлено всем!'
                        if not delivered:
                            text = 'Сообщение не было доставлено группам:\n'
                            for group in not_delivered:
                                text += f'{group[0]} {group[3]}\n'
                        await callback_query.message.edit_text(text)
                        await state.finish()


async def sendMessageToGroupUsers(group_id, text):
    global delivered
    global not_delivered
    group_students = database.getGroupUsers(group_id)
    for student in group_students:
        try:
            await bot.send_message(student[0], text)
        except:
            delivered = False
            not_delivered.append(student)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('admin_message:'), state=admin_state.Message)
async def chooseCourseToSpread(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.from_user.id in config.ADMINS:
        courseNum = callback_query.data.split(':')[1]
        async with state.proxy() as data:
            if courseNum in data['courses']:
                text = data[str(courseNum)].text.replace('✅', '')
                data[str(courseNum)] = InlineKeyboardButton(f'{text}', callback_data=f'admin_message:{courseNum}')
                data['courses'].remove(courseNum)
            else:
                text = data[str(courseNum)].text + ' ✅'
                data[str(courseNum)] = InlineKeyboardButton(f'{text}', callback_data=f'admin_message:{courseNum}')
                data['courses'].append(courseNum)
        backBtn = InlineKeyboardButton('Назад', callback_data='admin:menu')
        if data.get('sendBtn') is None:
            kb = InlineKeyboardMarkup(row_width=1).add(*[data['1'], data['2'], data['3'], backBtn])
        else:
            kb = InlineKeyboardMarkup(row_width=1).add(*[data['1'], data['2'], data['3'], data['sendBtn'], backBtn])
        await callback_query.message.edit_reply_markup(kb)


@dp.message_handler(state=admin_state.Message, content_types='any')
async def getMessageToSpreadByAdmin(message: types.Message, state: FSMContext):
    if message.from_user.id in config.ADMINS:
        async with state.proxy() as data:
            #         photo = message.photo[-1]
            #          if photo is not None:
            #               data['media'].append(photo.file_id)
            #                await message.bot.send_photo(message.from_user.id,photo=photo.file_id)
            callback_query = data['callback']
            text = message.html_text
            sendBtn = InlineKeyboardButton('Отправить', callback_data='admin:send_message:None')
            data['sendBtn'] = sendBtn
            data['msg'] = message.html_text
            backBtn = InlineKeyboardButton('Назад', callback_data='admin:menu')
            kb = InlineKeyboardMarkup(row_width=1).add(*[data['1'], data['2'], data['3'], sendBtn, backBtn])
            await callback_query.edit_text(f'Ваш текст:\n{text}\nДля кого предназначена рассылка?', reply_markup=kb)


@dp.errors_handler(exception=MessageCantBeDeleted)
async def message_cant_be_deleted():
    print(f'Сообщение не может быть удалено!')
    return True


@dp.errors_handler(exception=MessageCantBeEdited)
async def message_cant_be_edited():
    print(f'Сообщение не может быть изменено!')
    return True


@dp.message_handler(commands=["all"])
async def all(message: types.Message):
    user = database.getUser(message.from_user.id)
    if user is not None and user[3] not in black_list_statuses and message.chat.type != 'private':
        msg = message.text.replace('/all@aitu_jedel_bot', '')
        msg = msg.replace('/all ', '')
        msg = msg.replace('/all', '')
        commandStatus = database.getCommandStatus('all', message.chat.id)
        print(commandStatus)
        if commandStatus is not None:
            if commandStatus[1] is False:
                await message.reply('Вам нужно подождать перед следующим вызовом!')
                return
        else:
            initializeBtn = InlineKeyboardButton('Инициализировать',
                                                 callback_data=f'initialize:group:{message.chat.id}')
            await bot.send_message(message.chat.id,
                                   f'Привет, <a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>! '
                                   f'Предлагаю инициализировать группу, чтобы можно было воспользоваться командой /all.',
                                   reply_markup=InlineKeyboardMarkup().add(initializeBtn), parse_mode='HTML')
            return
        await message.answer(f'{message.from_user.first_name} вызвал участников группы..')
        users = database.getGroupUsersToNotify(message.chat.id)
        text = msg + '\n'
        for u in range(len(users)):
            user = database.getUser(users[u][1])
            if user is None:
                database.deleteUserFromGroup(message.chat.id, users[u][1])
                continue
            if user[4] is None:
                text += f'<a href="tg://user?id={user[0]}">{user[6]}</a> '
            else:
                text += f'<a href="tg://user?id={user[0]}">{user[4]}</a> '
            if (u + 1) % 4 == 0 or len(users) == u + 1:
                await message.answer(text=text, parse_mode='HTML')
                text = msg + '\n'
        database.switchCommandStatus('all', message.chat.id, False)
        await asyncio.sleep(180)
        database.switchCommandStatus('all', message.chat.id, True)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('profile:'), state='*')
async def profile(callback_query: types.CallbackQuery, state: FSMContext):
    user = database.getUser(callback_query.from_user.id)
    if user is not None and user[3] not in black_list_statuses:
        decision = callback_query.data.split(':')
        if decision[1] == 'show':
            await state.finish()
            now_hour = dt.hour
            if 18 <= now_hour <= 23:
                greeting = "Добрый вечер, "
            elif 0 <= now_hour <= 4:
                greeting = "Доброй ночи, "
            elif 5 <= now_hour <= 11:
                greeting = "Доброе утро, "
            else:
                greeting = "Добрый день, "
            if user[1] == 'head':
                role = 'Староста'
            else:
                role = 'Студент'
            kb = InlineKeyboardMarkup(row_width=1)
            if user[4] is None:
                applyEmojiBtn = InlineKeyboardButton('Выбрать эмодзи', callback_data='profile:emoji')
                emoji = "<b>не обозначено</b>"
            else:
                applyEmojiBtn = InlineKeyboardButton('Изменить эмодзи', callback_data='profile:emoji')
                emoji = user[4]
            if user[5] is None:
                applyBirthdayBtn = InlineKeyboardButton('Выставить ДР', callback_data='profile:birthday')
                birthday = "<b>не обозначено</b>"
            else:
                applyBirthdayBtn = InlineKeyboardButton('Изменить ДР', callback_data='profile:birthday')
                birthday_date = user[5]
                birthday = f"{birthday_date.day} {config.months[birthday_date.month]} {birthday_date.year}"
            userWish = database.getUserWish(user[0])
            group = database.getHeadOfGroup(user[2])
            kb.add(applyEmojiBtn)
            kb.add(applyBirthdayBtn)
            if userWish is not None:
                if userWish[1] == '':
                    setWishBtn = InlineKeyboardButton('Выставить желание на ДР', callback_data='profile:wish')
                    wishTxt = "Ваше желание на ДР: None"
                else:
                    setWishBtn = InlineKeyboardButton('Изменить желание на ДР', callback_data='profile:wish')
                    wishTxt = f"Ваше желание на ДР: <b>{userWish[1]}</b>"
                kb.add(setWishBtn)
            else:
                wishTxt = ''
            kb.add(getMainMenuBtn)
            text = f"{greeting}<a href='tg://user?id={user[0]}'>{user[6]}</a>! \n" \
                   f"Ваш профиль:\n" \
                   f"1. {role} группы {group[3]}\n" \
                   f"2. {group[2]} курс\n" \
                   f"3. Эмодзи: {emoji}\n" \
                   f"4. Дата рождения: {birthday}\n" \
                   f"{wishTxt}"
            text = text.replace('None', '<b>не обозначено</b>')
            await callback_query.message.edit_text(text, parse_mode='HTML', reply_markup=kb)
        if decision[1] == 'wish':
            userWish = database.getUserWish(user[0])
            if userWish is not None:
                backBtn = InlineKeyboardButton('Назад', callback_data='profile:show')
                await callback_query.message.edit_text('Что Вы желаете на своё ДР?',
                                                       reply_markup=InlineKeyboardMarkup().add(backBtn))
                await userState.Wish.set()
                async with state.proxy() as data:
                    data['msg_id'] = callback_query.message.message_id
            else:
                await callback_query.answer('Недоступно!')
        if decision[1] == 'back':
            await state.finish()
            profileBtn = InlineKeyboardButton('Мой профиль', callback_data='profile:show')
            groupBtn = InlineKeyboardButton('Моя группа', callback_data='mygroup:show')
            kb = InlineKeyboardMarkup(row_width=1).add(*[profileBtn, groupBtn, rulesBtn])
            if user[0] in config.ADMINS:
                adminBtn = InlineKeyboardButton('Администрирование', callback_data='admin:menu')
                kb.add(adminBtn)
            if database.getSupergroupsOfUser(user[0]):
                supergroupBtn = InlineKeyboardButton('Мои супергруппы', callback_data='mysupergroup:show')
                kb.add(supergroupBtn)
            if user[1] == 'head':
                await callback_query.message.edit_text('Здравствуйте, староста, чем могу помочь?', reply_markup=kb)
            elif user[1] == 'student':
                await callback_query.message.edit_text('Привет, чем могу помочь?', reply_markup=kb)
        if decision[1] == 'emoji':
            kb = InlineKeyboardMarkup().add(getMainMenuBtn)
            await userState.Emoji.set()
            async with state.proxy() as data:
                data['msg_id'] = callback_query.message.message_id
            await callback_query.message.edit_text('Отправьте Ваш эмодзи', reply_markup=kb)
        if decision[1] == 'birthday':
            kb = InlineKeyboardMarkup().add(getMainMenuBtn)
            await userState.Birthday.set()
            async with state.proxy() as data:
                data['msg_id'] = callback_query.message.message_id
            await callback_query.message.edit_text('Отправьте Вашу дату рождения в соответствий с шаблоном\n\n'
                                                   '<b>ДД.ММ.ГГГГ</b>', parse_mode='HTML', reply_markup=kb)
    else:
        await callback_query.message.delete()
        await callback_query.answer('Нет доступа!', show_alert=True)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('mygroup:'), state='*')
async def group(callback_query: types.CallbackQuery, state: FSMContext):
    user = database.getUser(callback_query.from_user.id)
    backBtn = InlineKeyboardButton('Назад', callback_data='mygroup:show')
    if user is not None and user[3] not in black_list_statuses:
        decision = callback_query.data.split(':')
        if decision[1] == 'show':
            if callback_query.message.chat.type == 'private':
                await state.finish()
                now_hour = dt.hour
                if 18 <= now_hour <= 23:
                    greeting = "Добрый вечер, "
                elif 0 <= now_hour <= 4:
                    greeting = "Доброй ночи, "
                elif 5 <= now_hour <= 11:
                    greeting = "Доброе утро, "
                else:
                    greeting = "Добрый день, "
                kb = InlineKeyboardMarkup(row_width=1)
                near_bdays = InlineKeyboardButton('Предстоящие ДР', callback_data='mygroup:birthdays')
                askBtn = InlineKeyboardButton('Задать вопрос старосте', callback_data='mygroup:ask')
                myQuestionsBtn = InlineKeyboardButton('Мои вопросы', callback_data='mygroup:my_questions')
                interestingBtn = InlineKeyboardButton('Актуальные вопросы', callback_data='mygroup:interesting')

                if user[1] == 'head':
                    headFuncBtn = InlineKeyboardButton('Функции старосты', callback_data='mygroup:head')
                    kb.add(headFuncBtn)
                group = database.getHeadOfGroup(user[2])
                numOfStudents = (database.getNumberOfStudents(group[0]))[0]
                bday_user_wishes = database.getUsersWishOfGroup(group[0], user[0])
                kb.add(*[near_bdays, askBtn, myQuestionsBtn, interestingBtn, getMainMenuBtn])
                text = f"{greeting}<a href='tg://user?id={user[0]}'>{user[6]}</a>! \n" \
                       f"Ваша группа:\n" \
                       f"1. Название группы: {group[3]}\n" \
                       f"2. Курс: {group[2]}\n" \
                       f"3. Количество студентов: {numOfStudents}\n" \
                       f"4. Количество предстоящих ДР: {len(bday_user_wishes)}"
                text = text.replace('None', '<b>не обозначено</b>')
                await callback_query.message.edit_text(text, parse_mode='HTML', reply_markup=kb)
            else:
                callAllBtn = InlineKeyboardButton('Позвать всех!',
                                                  callback_data=f'command:all:{callback_query.message.chat.id}')
                interestingBtn = InlineKeyboardButton('Актуальные вопросы', callback_data='mygroup:interesting')
                kb = InlineKeyboardMarkup(row_width=1).add(*[callAllBtn, interestingBtn])
                group = database.getHeadOfGroup(callback_query.message.chat.id)
                if group is None:
                    group = database.getSupergroup(callback_query.message.chat.id)
                    if group is None:
                        link = await get_start_link(callback_query.message.chat.id, encode=True)
                        register_btn = InlineKeyboardButton('Зарегистрировать группу', url=f"{link}",
                                                            callback_data=f'register:{callback_query.message.chat.id}')
                        kb.add(register_btn)
                await callback_query.message.edit_text('Привет, это AITU INFO BOT', reply_markup=kb)
        if decision[1] == 'ask':
            kb = InlineKeyboardMarkup()
            kb.add(backBtn)
            await userState.Ask.set()
            async with state.proxy() as data:
                data['msg_id'] = callback_query.message.message_id
            await callback_query.message.edit_text('Какой у Вас вопрос?', reply_markup=kb)
        if decision[1] == 'my_questions':
            kb = InlineKeyboardMarkup(row_width=1)
            questions = database.getUserQuestions(user[0])
            for question in questions:
                questionBtn = InlineKeyboardButton(
                    f'{question[1][0:20]}{".." if len(question[1]) > 20 else ""}{"✅" if question[2] is not None else "❌"}',
                    callback_data=f'mygroup:question:{question[0]}')
                kb.add(questionBtn)
            kb.add(backBtn)
            await callback_query.message.edit_text('Ваши заданные вопросы', reply_markup=kb)
        if decision[1] == 'question':
            question = database.getQuestion(decision[2])
            if question is None:
                await callback_query.answer('Вопрос удалён!')
                return
            if question[4] != user[0]:
                await callback_query.answer('Нет доступа!')
                return
            kb = InlineKeyboardMarkup(row_width=1)
            if question[5] is not True:
                deleteBtn = InlineKeyboardButton('Удалить',
                                                 callback_data=f'mygroup:delete_question:{question[0]}:my_question')
                kb.add(deleteBtn)
            text = f"Вопрос номер <b>{question[0]}</b>\n" \
                   f"<b>{question[1]}</b>\n" \
                   f"{f'Ответ: <b>{question[2]}</b>' if question[2] is not None else '<b>Ответа нет</b>'}\n\n" \
                   f"{f'<i>Удаление вопроса недоступно, поскольку оно находится в актуальных</i>' if question[5] is True else ''}"
            backBtn = InlineKeyboardButton('Назад', callback_data='mygroup:my_questions')
            kb.add(backBtn)
            await callback_query.message.edit_text(text, parse_mode='HTML', reply_markup=kb)
        if decision[1] == 'delete_question':
            question = database.getQuestion(decision[2])
            if user[1] != 'head':
                if question[4] != user[0] or question[5] is True:
                    await callback_query.answer('Нет доступа!')
                    return
            database.deleteQuestion(question[0])
            await callback_query.answer('Вопрос удалён!')
            kb = InlineKeyboardMarkup(row_width=1)
            if decision[3] == 'my_question':
                questions = database.getUserQuestions(user[0])
                for question in questions:
                    questionBtn = InlineKeyboardButton(
                        f'{question[1][0:20]}{".." if len(question[1]) > 20 else ""}{"✅" if question[2] is not None else "❌"}',
                        callback_data=f'mygroup:question:{question[0]}')
                    kb.add(questionBtn)
                kb.add(backBtn)
                await callback_query.message.edit_text('Ваши заданные вопросы', reply_markup=kb)
            if decision[3] == 'asked_question':
                backBtn = InlineKeyboardButton('Назад', callback_data='mygroup:questions:choice')
                if decision[4] == 'read':
                    kb = InlineKeyboardMarkup(row_width=1)
                    questions = database.getGroupQuestionsBool(user[2], True)
                    for question in questions:
                        questionBtn = InlineKeyboardButton(
                            f'{question[1][0:20]}{".." if len(question[1]) > 20 else ""} {"✅" if question[2] is not None else "❌"}',
                            callback_data=f'mygroup:question_to_see:{question[0]}:read')
                        kb.add(questionBtn)
                    kb.add(backBtn)
                    await callback_query.message.edit_text('Прочитанные вопросы', reply_markup=kb)
                if decision[4] == 'unread':
                    kb = InlineKeyboardMarkup(row_width=1)
                    questions = database.getGroupQuestionsBool(user[2], False)
                    for question in questions:
                        questionBtn = InlineKeyboardButton(
                            f'{question[1][0:20]}{".." if len(question[1]) > 20 else ""}',
                            callback_data=f'mygroup:question_to_see:{question[0]}:unread')
                        kb.add(questionBtn)
                    kb.add(backBtn)
                    await callback_query.message.edit_text('Непрочитанные вопросы', reply_markup=kb)
        if decision[1] == 'interesting':
            kb = InlineKeyboardMarkup(row_width=1)
            group = database.getHeadOfGroup(user[2])
            questions = database.getInteresting(user[2])
            for question in questions:
                if question[9] == 'all' or str(group[2]) in question[9]:
                    questionBtn = InlineKeyboardButton(
                        f'{"[GLOBAL]" if question[6] else ""} {question[1][0:20]}{".." if len(question[1]) > 20 else ""}',
                        callback_data=f'mygroup:interesting_question:{question[0]}')
                    kb.add(questionBtn)
            kb.add(backBtn)
            await callback_query.message.edit_text(f'Актуальные вопросы [{group[2]} курс]', reply_markup=kb)
        if decision[1] == 'interesting_question':
            question = database.getQuestion(decision[2])
            kb = InlineKeyboardMarkup(row_width=1)
            text = f"Актуальный вопрос номер <b>{question[0]}</b>\n" \
                   f"<b>{question[1]}</b>\n" \
                   f"{f'Ответ: <b>{question[2]}</b>' if question[2] is not None else '<b>Ответа нет</b>'}\n\n"
            backBtn = InlineKeyboardButton('Назад', callback_data='mygroup:interesting')
            kb.add(backBtn)
            await callback_query.message.edit_text(text, parse_mode='HTML', reply_markup=kb)
        if decision[1] == 'head':
            if user[1] == 'head':
                await state.finish()
                group = database.getHeadOfGroup(user[2])
                if group[5] is False:
                    spamBtn = InlineKeyboardButton('Спам-защита [ВЫКЛЮЧЕНА]', callback_data='mygroup:spam:enable')
                else:
                    spamBtn = InlineKeyboardButton('Спам-защита [ВКЛЮЧЕНА]', callback_data='mygroup:spam:disable')
                myUsers = InlineKeyboardButton('Мои студенты', callback_data='mygroup:students:0')
                msgToAllBtn = InlineKeyboardButton('Рассылка для всех', callback_data='mygroup:message')
                questionsBtn = InlineKeyboardButton('Заданные вопросы', callback_data='mygroup:questions:choice')
                backBtn = InlineKeyboardButton('Назад', callback_data='mygroup:show')
                kb = InlineKeyboardMarkup(row_width=1).add(
                    *[myUsers, msgToAllBtn, spamBtn, questionsBtn, backBtn, getMainMenuBtn])
                text = callback_query.message.text.replace(user[6], f'<a href="tg://user?id={user[0]}">{user[6]}</a>')
                await callback_query.message.edit_text(text, reply_markup=kb, parse_mode='HTML')
            else:
                await callback_query.answer('Нет доступа!')
        if decision[1] == 'spam':
            if user[1] == 'head':
                group = database.getHeadOfGroup(user[2])
                database.switchSpamFilter(group[0], False if decision[2] == 'disable' else True)
                group = database.getHeadOfGroup(user[2])
                try:
                    await bot.send_message(group[0], f'<i><b>SPAM-FILTER STATUS - {decision[2].upper()}D</b></i>',
                                           parse_mode='HTML')
                except:
                    print(f"[ERROR] Cannot notify group {group[0]} about spam-filter")
                if group[5] is False:
                    spamBtn = InlineKeyboardButton('Спам-защита [ВЫКЛЮЧЕНА]', callback_data='mygroup:spam:enable')
                else:
                    spamBtn = InlineKeyboardButton('Спам-защита [ВКЛЮЧЕНА]', callback_data='mygroup:spam:disable')
                myUsers = InlineKeyboardButton('Мои студенты', callback_data='mygroup:students:0')
                msgToAllBtn = InlineKeyboardButton('Рассылка для всех', callback_data='mygroup:message')
                questionsBtn = InlineKeyboardButton('Заданные вопросы', callback_data='mygroup:questions:choice')
                backBtn = InlineKeyboardButton('Назад', callback_data='mygroup:show')
                kb = InlineKeyboardMarkup(row_width=1).add(
                    *[myUsers, msgToAllBtn, spamBtn, questionsBtn, backBtn, getMainMenuBtn])
                await callback_query.message.edit_reply_markup(reply_markup=kb)
        if decision[1] == 'questions':
            if user[1] == 'head':
                backBtn = InlineKeyboardButton('Назад', callback_data='mygroup:questions:choice')
                if decision[2] == 'choice':
                    read_questions = database.getGroupQuestionsBool(user[2], True)
                    unread_questions = database.getGroupQuestionsBool(user[2], False)
                    readBtn = InlineKeyboardButton(text=f'Прочитанные [{len(read_questions)}]',
                                                   callback_data='mygroup:questions:read')
                    unreadBtn = InlineKeyboardButton(text=f'Непрочитанные [{len(unread_questions)}]',
                                                     callback_data='mygroup:questions:unread')
                    backBtn = InlineKeyboardButton(text='Назад', callback_data='mygroup:head')
                    await callback_query.message.edit_text('Заданные вопросы',
                                                           reply_markup=InlineKeyboardMarkup(row_width=1).add(
                                                               *[readBtn, unreadBtn, backBtn]))
                if decision[2] == 'read':
                    await state.finish()
                    kb = InlineKeyboardMarkup(row_width=1)
                    questions = database.getGroupQuestionsBool(user[2], True)
                    for question in questions:
                        questionBtn = InlineKeyboardButton(
                            f'{question[1][0:20]}{".." if len(question[1]) > 20 else ""} {"✅" if question[2] is not None else "❌"}',
                            callback_data=f'mygroup:question_to_see:{question[0]}:read')
                        kb.add(questionBtn)
                    kb.add(backBtn)
                    await callback_query.message.edit_text('Прочитанные вопросы', reply_markup=kb)
                if decision[2] == 'unread':
                    await state.finish()
                    kb = InlineKeyboardMarkup(row_width=1)
                    questions = database.getGroupQuestionsBool(user[2], False)
                    for question in questions:
                        questionBtn = InlineKeyboardButton(
                            f'{question[1][0:20]}{".." if len(question[1]) > 20 else ""}',
                            callback_data=f'mygroup:question_to_see:{question[0]}:unread')
                        kb.add(questionBtn)
                    kb.add(backBtn)
                    await callback_query.message.edit_text('Непрочитанные вопросы', reply_markup=kb)
            else:
                await callback_query.answer('Нет доступа!')
        if decision[1] == 'question_to_see':
            await state.finish()
            question = database.getQuestion(decision[2])
            kb = InlineKeyboardMarkup(row_width=1)
            deleteBtn = InlineKeyboardButton('Удалить',
                                             callback_data=f'mygroup:delete_question:{question[0]}:asked_question:{decision[3]}')
            answerBtn = InlineKeyboardButton(f'{"Ответить" if question[2] is None else "Изменить ответ"}',
                                             callback_data=f'question:answer:{question[0]}:{decision[3]}')
            if question[2] is not None:
                if question[6] is not True:
                    if question[5]:
                        inteterestingBtn = InlineKeyboardButton('Убрать из актуальных',
                                                                callback_data=f'question:set_interesting:{False}:{question[0]}:{decision[3]}')
                    else:
                        inteterestingBtn = InlineKeyboardButton('Добавить в актуальные',
                                                                callback_data=f'question:set_interesting:{True}:{question[0]}:{decision[3]}')
                    kb.add(inteterestingBtn)
            if question[7] is False:
                database.updateQuestionReadStatus(question[0], True)
            if question[6] is not True:
                kb.add(answerBtn)
                kb.add(deleteBtn)
            backBtn = InlineKeyboardButton('Назад', callback_data=f'mygroup:questions:{decision[3]}')
            kb.add(backBtn)
            kb.add(getMainMenuBtn)
            text = f"Вопрос номер <b>{question[0]}</b> {'[Актуально]' if question[5] else '[Неактуально]'}\n" \
                   f"<b>{question[1]}</b>\n" \
                   f"--------------------\n" \
                   f"{f'Ответ: <b>{question[2]}</b>' if question[2] is not None else '<b>Ответа нет</b>'}\n\n" \
                   f"{'<i><b>Удаление и редактирование вопроса невозможно из-за того, что оно находится в глобальном закрепе.</b></i>' if question[6] is True else ''}"
            await callback_query.message.edit_text(text, parse_mode='HTML', reply_markup=kb)
        if decision[1] == 'students':
            if user[1] == 'head':
                await state.finish()
                studentNum = int(decision[2])
                users = database.getGroupUsers(user[2])
                if len(users) == 1:
                    await callback_query.answer('Список пуст!')
                    return
                if user[2] not in usersToSee.keys():
                    studentNum = 0
                    await callback_query.answer('Список обновлён!')
                if studentNum == 0:
                    u_k = {}
                    counter = 0
                    for u in users:
                        if u[0] != user[0]:
                            u_k[counter] = u
                            counter += 1
                    usersToSee[user[2]] = u_k
                    nextUser = InlineKeyboardButton('Следующий', callback_data=f'mygroup:students:{studentNum + 1}')
                    userToSee = (usersToSee[user[2]])[studentNum]
                    userDonated = (database.getUserDonateSum(userToSee[0]))[studentNum]
                    birthday_date = userToSee[5]
                    profileBtn = InlineKeyboardButton('Профиль', url=f'tg://user?id={userToSee[0]}')
                    birthdayBtn = InlineKeyboardButton('Изменить ДР',
                                                       callback_data=f'mygroup:set_birthday:{userToSee[0]}:{studentNum}')
                    kb = InlineKeyboardMarkup().add(profileBtn)
                    kb.add(birthdayBtn)
                    kb.add(nextUser)
                    kb.add(getMainMenuBtn)
                    if birthday_date is not None:
                        birthday = f"{birthday_date.day} {config.months[birthday_date.month]} {birthday_date.year}"
                    else:
                        birthday = None
                    text = f"Профиль студента {userToSee[6]}:\n" \
                           f"1. Эмодзи: {userToSee[4]}\n" \
                           f"2. Дата рождения: {birthday}\n" \
                           f"3. Вклад в сборы: {userDonated if userDonated else 0} тг."
                    text = text.replace('None', '<b>не обозначено</b>')
                    await callback_query.message.edit_text(f'{text}', parse_mode='HTML', reply_markup=kb)
                else:
                    kb = InlineKeyboardMarkup(row_width=2)
                    userToSee = (usersToSee[user[2]])[studentNum]
                    profileBtn = InlineKeyboardButton('Профиль', url=f'tg://user?id={userToSee[0]}')
                    birthdayBtn = InlineKeyboardButton('Изменить ДР',
                                                       callback_data=f'mygroup:set_birthday:{userToSee[0]}:{studentNum}')
                    kb.add(profileBtn)
                    kb.add(birthdayBtn)
                    prevUser = InlineKeyboardButton('Предыдущий', callback_data=f'mygroup:students:{studentNum - 1}')
                    if studentNum < len(usersToSee[user[2]]) - 1:
                        nextUser = InlineKeyboardButton('Следующий', callback_data=f'mygroup:students:{studentNum + 1}')
                        kb.add(*[prevUser, nextUser])
                    else:
                        kb.add(prevUser)
                    userDonated = (database.getUserDonateSum(userToSee[0]))[0]
                    birthday_date = userToSee[5]
                    if birthday_date is not None:
                        birthday = f"{birthday_date.day} {config.months[birthday_date.month]} {birthday_date.year}"
                    else:
                        birthday = None
                    kb.add(getMainMenuBtn)
                    text = f"Профиль студента {userToSee[6]}:\n" \
                           f"1. Эмодзи: {userToSee[4]}\n" \
                           f"2. Дата рождения: {birthday}\n" \
                           f"3. Вклад в сборы: {userDonated if userDonated else 0} тг."
                    text = text.replace('None', '<b>не обозначено</b>')
                    await callback_query.message.edit_text(f'{text}', parse_mode='HTML', reply_markup=kb)
            else:
                await callback_query.answer('Нет доступа!')
        if decision[1] == 'set_birthday':
            if user[1] == 'head' and user[0] not in black_list_statuses:
                await head.StudentBirthday.set()
                kb = InlineKeyboardMarkup()
                backBtn = InlineKeyboardButton('Назад', callback_data=f'mygroup:students:{decision[3]}')
                kb.add(backBtn)
                async with state.proxy() as data:
                    data['msg_id'] = callback_query.message.message_id
                    data['student_id'] = int(decision[2])
                    data['student_num'] = int(decision[3])
                await callback_query.message.edit_text('Отправьте дату рождения студента в соответствий с шаблоном\n\n'
                                                       '<b>ДД.ММ.ГГГГ</b>', parse_mode='HTML', reply_markup=kb)
        if decision[1] == 'birthdays':
            now_hour = dt.hour
            if 18 <= now_hour <= 23:
                greeting = "Добрый вечер, "
            elif 0 <= now_hour <= 4:
                greeting = "Доброй ночи, "
            elif 5 <= now_hour <= 11:
                greeting = "Доброе утро, "
            else:
                greeting = "Добрый день, "
            kb = InlineKeyboardMarkup(row_width=1)
            group = database.getHeadOfGroup(user[2])
            numOfStudents = (database.getNumberOfStudents(group[0]))[0]
            bday_user_wishes = database.getUsersWishOfGroup(user[2], user[0])
            text = f"{greeting}<a href='tg://user?id={user[0]}'>{user[6]}</a>! \n" \
                   f"Ваша группа:\n" \
                   f"1. Название группы: {group[3]}\n" \
                   f"2. Курс: {group[2]}\n" \
                   f"3. Количество студентов: {numOfStudents}\n" \
                   f"4. Количество предстоящих ДР: {len(bday_user_wishes)}"
            text = text.replace('None', '<b>не обозначено</b>')
            for u in bday_user_wishes:
                if u[0] != user[0]:
                    user_bday_btn = InlineKeyboardButton(f'{u[6]} - {u[5].day} {config.months[u[5].month]}',
                                                         callback_data=f'mygroup:birthday:{u[0]}')
                    kb.add(user_bday_btn)
            kb.add(backBtn)
            await callback_query.message.edit_text(text, parse_mode='HTML', reply_markup=kb)
        if decision[1] == 'birthday':
            await state.finish()
            bday_user_data = database.getUserWishWithUserData(decision[2])
            if bday_user_data is not None:
                backBtn = InlineKeyboardButton('Назад', callback_data=f'mygroup:birthdays')
                kb = InlineKeyboardMarkup(row_width=1)
                donated_sum = database.getUserDonatesSum(bday_user_data[0])
                if donated_sum[0] is None and user[1] == 'head':
                    declare_donateBtn = InlineKeyboardButton('Начать сбор',
                                                             callback_data=f'donate:create:{bday_user_data[0]}')
                    kb.add(declare_donateBtn)
                    donated_sum_text = '<b>Сбор не объявлен</b>'
                elif donated_sum[0] is None and bday_user_data[1] == 'head':
                    declare_donateBtn = InlineKeyboardButton('Начать сбор',
                                                             callback_data=f'donate:create:{bday_user_data[0]}')
                    kb.add(declare_donateBtn)
                    donated_sum_text = '<b>Сбор не объявлен</b>'
                elif donated_sum[0] is None:
                    donated_sum_text = '<b>Сбор не объявлен</b>'
                else:
                    donated_sum_text = f"<b>{donated_sum[0]}</b>"
                    donateBtn = InlineKeyboardButton('Скинуться',
                                                     callback_data=f'donated:donated:{user[0]}:{bday_user_data[0]}')
                    kb.add(donateBtn)
                if bday_user_data[8] == '':
                    wish = "<b>Пока пусто</b>"
                else:
                    wish = f"<b>{bday_user_data[8]}</b>"
                text = f"День рождения {bday_user_data[6]} - {bday_user_data[5].day} {config.months[bday_user_data[5].month]} " \
                       f"{bday_user_data[5].year} {config.endings[int(str(bday_user_data[5].year)[-1])]}\n\n" \
                       f"Его пожелание - {wish}\n" \
                       f"Собрано - {donated_sum_text}"
                kb.add(backBtn)
                await callback_query.message.edit_text(text, reply_markup=kb, parse_mode='HTML')
            else:
                await callback_query.answer('Нет данных')
        if decision[1] == 'message':
            await callback_query.message.edit_text('Введите ваш текст:\n')
            await head.Message.set()
            async with state.proxy() as data:
                data['messages'] = []
                data['callback'] = callback_query
        if decision[1] == 'send_message':
            async with state.proxy() as data:
                await callback_query.message.edit_text('Отправка сообщения..')
                text = data.get('message')
                if text is None:
                    await callback_query.answer('Время ожидания истекло...')
                    await callback_query.message.delete()
                    return
                group_students = database.getGroupUsers(user[2])
                delivered = True
                not_delivered = []
                for student in group_students:
                    if student[0] != user[0]:
                        try:
                            await bot.send_message(student[0], text)
                        except:
                            delivered = False
                            not_delivered.append(student)
                text = 'Сообщение доставлено всем!'
                if not delivered:
                    text = 'Сообщение не было доставлено студентам:\n'
                    for student in not_delivered:
                        text += f'{student[0]} {student[6]}\n'
                await callback_query.message.edit_text(text)
                await state.finish()
        if decision[1] == 'back':
            await state.finish()
    else:
        await callback_query.answer('Нет доступа!', show_alert=True)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('donated:'), state='*')
async def question_process(callback_query: types.CallbackQuery, state: FSMContext):
    user = database.getUser(callback_query.from_user.id)
    if user is not None and user[3] not in black_list_statuses:
        decision = callback_query.data.split(':')
        if decision[1] == 'donated':
            async with state.proxy() as data:
                data['bday_user'] = decision[3]
                backBtn = InlineKeyboardButton('Назад', callback_data=f'mygroup:birthday:{decision[3]}')
                data['query'] = await callback_query.message.edit_text('Введите сумму',
                                                                       reply_markup=InlineKeyboardMarkup().add(backBtn))
                data['backBtn'] = backBtn
                await userState.Donate.set()
        if decision[1] == 'confirm':
            backBtn = InlineKeyboardButton('Назад', callback_data=f'mygroup:birthday:{decision[3]}')
            await state.finish()
            await callback_query.message.edit_text('Вкладываться в сбор группы - потрясающее решение!',
                                                   reply_markup=InlineKeyboardMarkup().add(backBtn))
            responsible = database.getDeclaredDonate(decision[3])
            database.sendDonate(callback_query.from_user.id, decision[3], decision[2],responsible[0])
            confirmBtn = InlineKeyboardButton('Подтвердить',
                                              callback_data=f'donate:confirm:{decision[3]}:{callback_query.from_user.id}:{decision[2]}')
            declineBtn = InlineKeyboardButton('Отвергнуть',
                                              callback_data=f'donate:decline:{decision[3]}:{callback_query.from_user.id}')
            kb = InlineKeyboardMarkup(row_width=2).add(*[confirmBtn, declineBtn])
            bday_user = database.getUser(decision[3])
            user = database.getUser(callback_query.from_user.id)
            responsible = database.getUser(responsible[3])
            try:
                await bot.send_message(responsible[0],
                                       f"Привет, <a href='tg://user?id={responsible[0]}'>{responsible[6]}</a>!\n"
                                       f"Студент <a href='tg://user?id={user[0]}'>{user[6]}</a> внес в сбор на ДР "
                                       f"студента <a href='tg://user?id={bday_user[0]}'>{bday_user[6]}</a> сумму {decision[2]}",
                                       reply_markup=kb)
            except:
                print(f'[ERROR] Cannot send message to the responsible {responsible[0]}')
                await callback_query.message.reply(
                    'Не удаётся оповестить ответственного за сбор, вероятно он заблокировал бота!')


    else:
        await callback_query.message.delete()
        await callback_query.answer('Нет доступа!', show_alert=True)


@dp.message_handler(state=userState.Donate)
async def getDonateAmount(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        callback_query = data['query']
        await callback_query.edit_text('<i>Проверка..</i>')
        if message.text.isdigit():
            amount = int(message.text)
            if amount > 0:
                await message.delete()
                kb = InlineKeyboardMarkup(row_width=1)
                confirmBtn = InlineKeyboardButton('Подтвердить',
                                                  callback_data=f'donated:confirm:{amount}:{data["bday_user"]}')
                kb.add(*[confirmBtn, data['backBtn']])
                await callback_query.edit_text(f'Вы скинули <b>{amount}</b> тг.\n\n'
                                               f'<b><i>Учтите, что ответственный за сбор должен подтвердить что Вы '
                                               f'скинули ему сумму, '
                                               f' если Вы ошиблись при наборе, то напишите ещё раз.</i></b>',
                                               reply_markup=kb)
            else:
                await message.delete()
                await callback_query.edit_text('<b>Сумма должна быть больше 0</b>\n\n'
                                               'Введите сумму',
                                               reply_markup=InlineKeyboardMarkup().add(data['backBtn']))
        else:
            await message.delete()
            await callback_query.edit_text('<b>Не удаётся определить сумму, введите число</b>\n\n'
                                           'Введите сумму', reply_markup=InlineKeyboardMarkup().add(data['backBtn']))


@dp.message_handler(state=head.Message)
async def getMessageToSpread(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if len(data['messages']) > 0:
            for msg_id in data['messages']:
                try:
                    await bot.delete_message(message_id=msg_id, chat_id=message.from_user.id)
                except:
                    pass
        await message.delete()
        text = message.html_text
        data['message'] = text
        callback = data['callback']
        sendBtn = InlineKeyboardButton(text='Отправить', callback_data='mygroup:send_message')
        backBtn = InlineKeyboardButton('Назад', callback_data='mygroup:show')
        try:
            await callback.message.edit_text(text="Ваш текст, отправьте его по новой, если желаете его поменять.",
                                             reply_markup=InlineKeyboardMarkup(row_width=1).add(*[sendBtn, backBtn]))
        except:
            pass
        msg = await message.answer(text)
        data['messages'].append(msg.message_id)


@dp.message_handler(state=userState.Ask)
async def getQuestion(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
        backBtn = InlineKeyboardButton('Назад', callback_data='mygroup:show')
        if message.text.count("'") > 0 or message.text.count('"') > 0:
            await bot.edit_message_text('<b>Использование кавычек</b>\n'
                                        'Недопустимые знаки были использованы, попробуйте придумать другое название',
                                        parse_mode='HTML', message_id=data['msg_id'], chat_id=message.from_user.id,
                                        reply_markup=InlineKeyboardMarkup().add(backBtn))
            return
        data['question'] = message.text
        sendBtn = InlineKeyboardButton('Отправить', callback_data='question:send')
        await bot.edit_message_text(f'Ваш вопрос: \n'
                                    f'<b><i>{message.text}</i></b>\n'
                                    f'Отправить вопрос?', parse_mode='HTML',
                                    reply_markup=InlineKeyboardMarkup(row_width=1).add(*[sendBtn, backBtn]),
                                    message_id=data['msg_id'], chat_id=message.from_user.id)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('question:'), state='*')
async def question_process(callback_query: types.CallbackQuery, state: FSMContext):
    user = database.getUser(callback_query.from_user.id)
    if user is not None and user[3] not in black_list_statuses:
        decision = callback_query.data.split(':')
        if decision[1] == 'send':
            async with state.proxy() as data:
                if 'question' not in data.keys():
                    await callback_query.message.edit_text('Истекло время ожидания',
                                                           reply_markup=InlineKeyboardMarkup().add(getMainMenuBtn))
                    return
                sent = database.addQuestion(data['question'], user[2], user[0])
                if sent:
                    group = database.getHeadOfGroup(user[2])
                    try:
                        questionsBtn = InlineKeyboardButton('Заданные вопросы',
                                                            callback_data='mygroup:questions:unread')
                        await bot.send_message(group[1], "Вам задан новый вопрос!",
                                               reply_markup=InlineKeyboardMarkup().add(questionsBtn))
                    except:
                        await callback_query.message.edit_text('Не удалось уведомить старосту..')
                    await callback_query.message.edit_text(f'<b>Вопрос отправлен!</b>', parse_mode='HTML')
                else:
                    await callback_query.message.edit_text('Не удалось отправить вопрос...')
                await state.finish()
        if decision[1] == 'answer':
            question = database.getQuestion(decision[2])
            kb = InlineKeyboardMarkup(row_width=1)
            backBtn = InlineKeyboardButton('Назад',
                                           callback_data=f'mygroup:question_to_see:{decision[2]}:{decision[3]}')
            kb.add(backBtn)
            kb.add(getMainMenuBtn)
            async with state.proxy() as data:
                data['decision'] = decision[3]
                data['question'] = question
                data['callback_query'] = await callback_query.message.edit_text(f'Вопрос номер <b>{question[0]}</b>\n'
                                                                                f'<b>{question[1]}</b>\n\n'
                                                                                f'<i>Введите ответ</i>',
                                                                                reply_markup=kb, parse_mode='HTML')
            await head.QuestionAnswer.set()
        if decision[1] == 'send_answer':
            async with state.proxy() as data:
                if "answer" not in data.keys():
                    await callback_query.message.edit_text('Истекло время ожидания ответа..',
                                                           reply_markup=InlineKeyboardMarkup().add(getMainMenuBtn))
                    return
                question = database.getQuestion(decision[2])
                result = database.setQuestionAnswer(decision[2], data['answer'])
                if result:
                    try:
                        questionBtn = InlineKeyboardButton(
                            f'{question[1][0:20]}{".." if len(question[1]) > 20 else ""}',
                            callback_data=f'mygroup:question:{question[0]}')
                        await bot.send_message(question[4], f'Вы получили ответ на вопрос <b>"{question[1]}"</b>',
                                               parse_mode='HTML', reply_markup=InlineKeyboardMarkup().add(questionBtn))
                    except:
                        await callback_query.message.answer('Не удалось отправить сообщение пользователю!')
                    await callback_query.message.edit_text('<b>Ответ отправлен!</b>', parse_mode='HTML')
                else:
                    await callback_query.message.edit_text('<b>Не удалось отправить ответ..</b>', parse_mode='HTML')
                await state.finish()
        if decision[1] == 'set_interesting':
            if user[1] == 'head':
                database.setQuestionInterestingStatus(decision[3], decision[2])
                question = database.getQuestion(decision[3])

                kb = InlineKeyboardMarkup(row_width=1)
                deleteBtn = InlineKeyboardButton('Удалить',
                                                 callback_data=f'mygroup:delete_question:{question[0]}:asked_question:{decision[4]}')
                answerBtn = InlineKeyboardButton(f'{"Ответить" if question[2] is None else "Изменить ответ"}',
                                                 callback_data=f'question:answer:{question[0]}:{decision[4]}')
                if question[5]:
                    inteterestingBtn = InlineKeyboardButton('Убрать из актуальных',
                                                            callback_data=f'question:set_interesting:{False}:{question[0]}:{decision[4]}')
                else:
                    inteterestingBtn = InlineKeyboardButton('Добавить в актуальные',
                                                            callback_data=f'question:set_interesting:{True}:{question[0]}:{decision[4]}')
                kb.add(inteterestingBtn)
                kb.add(answerBtn)
                kb.add(deleteBtn)
                backBtn = InlineKeyboardButton('Назад', callback_data=f'mygroup:questions:{decision[4]}')
                kb.add(backBtn)
                kb.add(getMainMenuBtn)
                text = callback_query.message.html_text
                if decision[2] == 'True':
                    text = text.replace('[Неактуально]', '[Актуально]')
                else:
                    text = text.replace('[Актуально]', '[Неактуально]')

                await callback_query.message.edit_text(text, reply_markup=kb)
    else:
        await callback_query.answer('Нет доступа!', show_alert=True)
        await callback_query.message.delete()


@dp.message_handler(state=head.QuestionAnswer)
async def getQuestionAnswer(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['answer'] = msg.text
        question = data['question']
        callback_query = data['callback_query']
        sendAnswerBtn = InlineKeyboardButton('Отправить', callback_data=f'question:send_answer:{question[0]}')
        backBtn = InlineKeyboardButton('Назад', callback_data=f'mygroup:questions:{data["decision"]}')
        kb = InlineKeyboardMarkup(row_width=1).add(*[sendAnswerBtn, backBtn])
        await msg.delete()
        await callback_query.edit_text(f'Вопрос номер <b>{question[0]}</b>\n'
                                       f'<b>{question[1]}</b>\n\n'
                                       f'<i>Ваш ответ: <b>{msg.text}</b></i>', reply_markup=kb, parse_mode='HTML')


@dp.message_handler(state=userState.Emoji)
async def getEmoji(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
        if isEmoji(message.text):
            database.setEmoji(message.from_user.id, message.text)
            await bot.edit_message_text(f'Эмодзи {message.text} сохранён!', parse_mode='HTML',
                                        reply_markup=InlineKeyboardMarkup().add(getMainMenuBtn),
                                        message_id=data['msg_id'], chat_id=message.from_user.id)
            await state.finish()
        else:
            await bot.edit_message_text('<b>Проверка</b>', parse_mode='HTML',
                                        message_id=data['msg_id'], chat_id=message.from_user.id)
            await bot.edit_message_text('<b>Убедитесь что Вы отправили эмодзи</b>\n\n'
                                        'Отправьте Ваш эмодзи', parse_mode='HTML',
                                        reply_markup=InlineKeyboardMarkup().add(getMainMenuBtn),
                                        message_id=data['msg_id'], chat_id=message.from_user.id)


@dp.message_handler(commands=['setme'], state='*')
async def getEmojiViaCommand(message: types.Message):
    user = database.getUser(message.from_user.id)
    if user is not None and user[3] not in black_list_statuses:
        emoji = message.text.replace('/setme ', '')
        emoji = emoji.replace('/setme', '')
        if emoji == '' or emoji == None:
            await message.reply('Эмодзи не найден!')
            return
        if isEmoji(emoji):
            database.setEmoji(message.from_user.id, emoji)
            await message.reply(f'Эмодзи {emoji} сохранён!', parse_mode='HTML')
        else:
            await message.reply('<b>Убедитесь что Вы отправили эмодзи</b>', parse_mode='HTML')
    else:
        await message.delete()
        await message.answer('Нет доступа!')


@dp.message_handler(state=head.StudentBirthday)
async def getStudentBirthday(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
        try:
            birthday_date = dt.strptime(message.text, '%d.%m.%Y')
            birthday_date_text = f"{birthday_date.day} {config.months[birthday_date.month]} {birthday_date.year}"
            database.setBirthday(data['student_id'], birthday_date)
            backBtn = InlineKeyboardButton('Назад', callback_data=f'mygroup:students:{data["student_num"]}')
            await bot.edit_message_text(f'Дата рождения {birthday_date_text} сохранена!', parse_mode='HTML',
                                        reply_markup=InlineKeyboardMarkup().add(backBtn),
                                        message_id=data['msg_id'], chat_id=message.from_user.id)
            try:
                await bot.send_message(int(data['student_id']),
                                       'Староста выставил вашу дату рождения, если дата неверна - вы '
                                       'можете поменять её.')
            except:
                await message.answer('Не удаётся оповестить студента об изменении его даты рождения!')
            await state.finish()
        except:
            await bot.edit_message_text('<b>Проверка</b>', parse_mode='HTML',
                                        message_id=data['msg_id'], chat_id=message.from_user.id)
            await bot.edit_message_text('<b>Убедитесь что Вы написали корректную дату по шаблону\n\n'
                                        'ДД.ММ.ГГГГ</b>\n\n'
                                        '<i>Пример: 2 сентября 2001 (2.9.2001)</i>\n\n'
                                        'Отправьте дату рождения', parse_mode='HTML',
                                        reply_markup=InlineKeyboardMarkup().add(getMainMenuBtn),
                                        message_id=data['msg_id'], chat_id=message.from_user.id)


@dp.message_handler(state=userState.Wish)
async def getWish(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
        backBtn = InlineKeyboardButton('Назад', callback_data='profile:show')
        database.setUserWish(message.from_user.id, message.text)
        await bot.edit_message_text(f'Ваше желание: <b>"{message.text}"</b> сохранено!', parse_mode='HTML',
                                    reply_markup=InlineKeyboardMarkup().add(backBtn),
                                    message_id=data['msg_id'], chat_id=message.from_user.id)
        await state.finish()


@dp.message_handler(state=userState.Birthday)
async def getBirthday(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
        try:
            birthday_date = dt.strptime(message.text, '%d.%m.%Y')
            birthday_date_text = f"{birthday_date.day} {config.months[birthday_date.month]} {birthday_date.year}"
            database.setBirthday(message.from_user.id, birthday_date)
            await bot.edit_message_text(f'Дата рождения {birthday_date_text} сохранена!', parse_mode='HTML',
                                        reply_markup=InlineKeyboardMarkup().add(getMainMenuBtn),
                                        message_id=data['msg_id'], chat_id=message.from_user.id)
            await state.finish()
        except:
            await bot.edit_message_text('<b>Проверка</b>', parse_mode='HTML',
                                        message_id=data['msg_id'], chat_id=message.from_user.id)
            await bot.edit_message_text('<b>Убедитесь что Вы написали корректную дату по шаблону\n\n'
                                        'ДД.ММ.ГГГГ</b>\n\n'
                                        '<i>Пример: 2 сентября 2001 (2.9.2001)</i>\n\n'
                                        'Отправьте Вашу дату рождения', parse_mode='HTML',
                                        reply_markup=InlineKeyboardMarkup().add(getMainMenuBtn),
                                        message_id=data['msg_id'], chat_id=message.from_user.id)


def isEmoji(text):
    for s in text:
        if ord(s) < 2000:
            return False
    return True


@dp.chat_member_handler()
async def member_handler(update: types.ChatMemberUpdated):
    # print(f'{update.old_chat_member.status} {update.new_chat_member.status}')
    # print(update.new_chat_member.is_chat_member())
    if update.new_chat_member.is_chat_member():
        if update.old_chat_member.status in ['kicked', 'left', 'banned'] and update.new_chat_member.status in ['member',
                                                                                                               'creator',
                                                                                                               'administrator']:
            user = update.new_chat_member.user
            dbUser = database.getUser(int(user.id))
            if dbUser is None:
                group = database.getHeadOfGroup(update.chat.id)
                if group is None:
                    group = database.getSupergroup(update.chat.id)
                    if group is None:
                        return
                    spam_filter_status = group[3]
                    group_type = 'super'
                else:
                    spam_filter_status = group[5]
                    group_type = 'group'
                if spam_filter_status is False:
                    link = await get_start_link(update.chat.id, encode=True)
                    if group_type == 'group':
                        register_btn = InlineKeyboardButton('Регистрация', url=f'{link}')
                        try:
                            await bot.send_message(update.chat.id,
                                                   f'<a href="tg://user?id={user.id}">{user.first_name}</a>, '
                                                   f'Вы ещё не состоите ни в одной группе.\n'
                                                   f'Зарегистрируйтесь по кнопке ниже.',
                                                   reply_markup=InlineKeyboardMarkup().add(register_btn),
                                                   parse_mode='HTML')
                        except:
                            print(f'[ERROR] Не удаётся отправить сообщение в группу {update.chat.id}')
                else:
                    try:
                        await bot.restrict_chat_member(group[0], user.id, ChatPermissions(False))
                    except:
                        print(f'[ERROR] Cannot restrict the user {user.id} {update.new_chat_member.status}')
                    random_task = random.choice(list(config.confirm_tasks.keys()))
                    answers = [random_task]
                    while len(answers) != 3:
                        num = random.randint(0, 100)
                        if num not in answers:
                            answers.append(num)

                    btns = []
                    for i in sorted(answers):
                        if i == random_task:
                            solBtn = InlineKeyboardButton(f'{i}', callback_data=f'spam:{user.id}:correct')
                        else:
                            solBtn = InlineKeyboardButton(f'{i}', callback_data=f'spam:{user.id}:incorrect')
                        btns.append(solBtn)
                    try:
                        msg = await bot.send_message(update.chat.id,
                                                     f'<a href="tg://user?id={user.id}">{user.first_name}</a>, '
                                                     f'в этой группе включена СПАМ-ЗАЩИТА, подтвердите что вы человек.\n'
                                                     f'Сколько будет {config.confirm_tasks[random_task]}?\n\n'
                                                     f'<i><b>У вас есть 30 секунд на ответ</b></i>',
                                                     reply_markup=InlineKeyboardMarkup().add(*btns), parse_mode='HTML')
                        spam_users.append(user.id)
                        await asyncio.sleep(30)
                        await bot.delete_message(msg.chat.id, msg.message_id)
                        if user.id in spam_users:
                            try:
                                await bot.kick_chat_member(chat_id=update.chat.id, user_id=user.id)
                            except:
                                print(f'Требуются права админа в группе {update.chat.id}')
                    except:
                        print(f'[ERROR] Не удаётся отправить сообщение в группу {update.chat.id}')
            else:
                database.addUserToGroup(update.chat.id, user.id)
                try:
                    msg = await bot.send_message(update.chat.id,
                                                 f'<a href="tg://user?id={user.id}">{user.first_name}</a>, '
                                                 f'добро пожаловать!', parse_mode='HTML')
                    await asyncio.sleep(30)
                    await bot.delete_message(msg.chat.id, msg.message_id)
                except:
                    print(f'[ERROR] Не удаётся отправить сообщение в группу {update.chat.id}')
    else:
        # print(f'{update.new_chat_member.user.first_name} is {update.new_chat_member.status}')
        user = update.new_chat_member.user
        dbUser = database.getUser(int(user.id))
        if dbUser is not None:
            database.deleteUserFromGroup(update.chat.id, user.id)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('spam:'), state='*')
async def spam_filter(callback_query: types.CallbackQuery, state: FSMContext):
    decision = callback_query.data.split(":")
    user = database.getUser(callback_query.from_user.id)
    if int(decision[1]) == callback_query.from_user.id:
        if decision[2] == 'correct':
            try:
                spam_users.remove(callback_query.from_user.id)
            except:
                print(f'[LOG] The user {callback_query.from_user.id} not in spam list')
            num_of_students = await bot.get_chat_members_count(callback_query.message.chat.id)
            if num_of_students <= 30 and user is None:
                link = await get_start_link(callback_query.message.chat.id, encode=True)
                register_btn = InlineKeyboardButton('Регистрация', url=link,
                                                    callback_data=f'register:{callback_query.message.chat.id}')
                try:
                    await callback_query.message.edit_text(
                        f'<a href="tg://user?id={callback_query.from_user.id}">{callback_query.from_user.first_name}</a>, '
                        f'Вы ещё не состоите ни в одной группе.\n'
                        f'Зарегистрируйтесь по кнопке ниже.',
                        reply_markup=InlineKeyboardMarkup().add(register_btn), parse_mode='HTML')
                except:
                    print(f'[ERROR] Не удаётся изменить сообщение в группе {callback_query.message.chat.id}')
            else:
                await callback_query.message.delete()
            try:
                chat = await bot.get_chat(callback_query.message.chat.id)
                await bot.restrict_chat_member(callback_query.message.chat.id, callback_query.from_user.id,
                                               chat.permissions)
            except:
                print(f'[ERROR] Cannot restrict the user {callback_query.from_user.id}')
        else:
            await callback_query.message.delete()
            await bot.kick_chat_member(chat_id=callback_query.message.chat.id, user_id=callback_query.from_user.id)

    else:
        await callback_query.answer('Сообщение предназначено не для Вас!')


@dp.my_chat_member_handler()
async def bot_invited(my_chat_member: types.ChatMemberUpdated):
    if my_chat_member.new_chat_member.status == 'member':
        user = database.getUser(my_chat_member.from_user.id)
        group = database.getHeadOfGroup(my_chat_member.chat.id)
        if user is None:
            link = await get_start_link(my_chat_member.chat.id, encode=True)
            register_btn = InlineKeyboardButton('Регистрация', url=link,
                                                callback_data=f'register:{my_chat_member.chat.id}')
            if group is None:
                try:
                    await bot.send_message(my_chat_member.chat.id, 'Привет, нажми ниже чтобы зарегистрировать группу!',
                                           reply_markup=InlineKeyboardMarkup().add(register_btn))
                except:
                    print(f'[ERROR] Не удаётся отправить сообщение в группу {my_chat_member.chat.id}')
            else:
                try:
                    await bot.send_message(my_chat_member.chat.id,
                                           f'<a href="tg://user?id={my_chat_member.from_user.id}">{my_chat_member.from_user.first_name}</a>, '
                                           f'Вы ещё не состоите ни в одной группе.\n'
                                           f'Зарегистрируйтесь по кнопке ниже.',
                                           reply_markup=InlineKeyboardMarkup().add(register_btn), parse_mode='HTML')
                except:
                    print(f'[ERROR] Не удаётся отправить сообщение в группу {my_chat_member.chat.id}')
        else:
            if group is None:
                try:
                    initializeBtn = InlineKeyboardButton('Инициализировать',
                                                         callback_data=f'initialize:group:{my_chat_member.chat.id}')
                    await bot.send_message(my_chat_member.chat.id,
                                           f'Привет, <a href="tg://user?id={my_chat_member.from_user.id}">{my_chat_member.from_user.first_name}</a>! '
                                           f'Предлагаю инициализировать группу, чтобы можно было воспользоваться командой /all.',
                                           reply_markup=InlineKeyboardMarkup().add(initializeBtn), parse_mode='HTML')
                except:
                    print(f'[ERROR] Не удаётся отправить сообщение в группу {my_chat_member.chat.id}')
            else:
                try:
                    await bot.send_message(my_chat_member.chat.id, 'Рад снова быть с Вами!')
                except:
                    print(f'[ERROR] Не удаётся отправить сообщение в группу {my_chat_member.chat.id}')


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('initialize:'))
async def initialize(callback_query: types.CallbackQuery):
    decision = callback_query.data.split(':')
    if decision[1] == "group":
        await callback_query.message.edit_text(
            f'<a href="tg://user?id={callback_query.from_user.id}">{callback_query.from_user.first_name}</a>, '
            f'вы запустили инициализацию группы, это займёт некоторое время.', parse_mode='HTML')
        database.deleteUsersFromGroup(callback_query.message.chat.id)
        groups = database.getGroups()
        for group in groups:
            await asyncio.create_task(initializeGroupMembers(group[0], callback_query.message.chat.id))
        database.switchCommandStatus('all', callback_query.message.chat.id, True)
        try:
            await callback_query.message.edit_text(f'Инициализация группы завершена!')
        except:
            print(f'[ERROR] Не удаётся изменить сообщение в группе {callback_query.message.chat.id}')


async def initializeGroupMembers(group_id, toInitializeGroup_id):
    group_users = database.getGroupUsers(group_id)
    for user in group_users:
        print(user[0])
        chatMember = await bot.get_chat_member(user_id=user[0], chat_id=toInitializeGroup_id)
        print(chatMember.status)
        if chatMember.status in ['member', 'creator', 'restricted', 'administrator']:
            database.addUserToGroup(toInitializeGroup_id, user[0])


@dp.message_handler(commands=['initialize'])
async def initializeGroup(message: types.Message):
    if message.chat.type != 'private':
        user = database.getUser(message.from_user.id)
        if user is not None and user[3] not in black_list_statuses:
            msg = await message.reply(
                f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>, '
                f'вы запустили инициализацию группы, это займёт некоторое время.', parse_mode='HTML')
            database.deleteUsersFromGroup(message.chat.id)
            groups = database.getGroups()
            for group in groups:
                await asyncio.create_task(initializeGroupMembers(group[0], message.chat.id))
            database.switchCommandStatus('all', message.chat.id, True, )
            try:
                text = msg.text
                text = text.replace(message.from_user.first_name,
                                    f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>')
                await msg.edit_text(f'{text}\n\n<b>Инициализация группы завершена!</b>', parse_mode='HTML')
            except:
                print(f'[ERROR] Не удаётся отправить сообщение в группу {message.chat.id}')


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('register_group:'))
async def register_group(callback_query: types.CallbackQuery, state: FSMContext):
    group = database.getHeadOfGroup(int(callback_query.data.replace('register_group:', '')))
    if group is not None:
        headOfGroup = InlineKeyboardButton(text='Написать старосте', url=f'tg://user?id={group[1]}')
        await callback_query.message.edit_text('Группа уже зарегистрирована!\n'
                                               f'ID старосты: <a href="tg://user?id={group[1]}">{group[1]}</a>\n'
                                               f'ID группы: {group[0]}', parse_mode='HTML',
                                               reply_markup=InlineKeyboardMarkup().add(headOfGroup))
        await state.finish()
        return
    cancel_register_btn = InlineKeyboardButton('Отмена регистрации',
                                               callback_data=f"cancel_register:{callback_query.from_user.id}")
    mainMsg = await callback_query.message.edit_text(
        f"<a href='tg://user?id={callback_query.from_user.id}'>{callback_query.from_user.first_name}</a>, нажав на регистрацию, "
        f"Вы подтверждаете что Вы являетесь старостой группы, если Вы не являетесь им, нажмите на кнопку отмены.\n"
        f"<b>Важно! Не забудьте дать боту права администратора.</b>",
        reply_markup=InlineKeyboardMarkup().add(cancel_register_btn), parse_mode='HTML')
    await head.GroupName.set()
    msg = await callback_query.message.answer('Введите название вашей группы')
    async with state.proxy() as data:
        data['group'] = int(callback_query.data.replace('register_group:', ''))
        data['head'] = int(callback_query.from_user.id)
        data['start_message_id'] = mainMsg.message_id
        data['start_message_chat_id'] = mainMsg.chat.id
        try:
            messages = data['messages']
            messages.append(msg.message_id)
            data['messages'] = messages
        except:
            messages = []
            messages.append(msg.message_id)
            data['messages'] = messages


@dp.message_handler(state=head.GroupName)
async def getGroupName(message: types.Message, state: FSMContext):
    if message.text.count("'") > 0 or message.text.count('"') > 0:
        await message.answer('<b>Использование кавычек</b>\n'
                             'Недопустимые знаки были использованы, попробуйте придумать другое название',
                             parse_mode='HTML')
        return
    first_course = InlineKeyboardButton('Первый курс', callback_data=f'course_num:1')
    second_course = InlineKeyboardButton('Второй курс', callback_data=f'course_num:2')
    third_course = InlineKeyboardButton('Третий курс', callback_data=f'course_num:3')
    course_kb = InlineKeyboardMarkup(row_width=1).add(*[first_course, second_course, third_course])
    msg = await message.answer('Выберите Ваш курс', reply_markup=course_kb)
    async with state.proxy() as data:
        data['group_name'] = message.text
        try:
            messages = data['messages']
            messages.append(msg.message_id)
            data['messages'] = messages
        except:
            messages = []
            messages.append(msg.message_id)
            data['messages'] = messages
    await head.next()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('decision:'), state='*')
async def decision(callback_query: types.CallbackQuery, state: FSMContext):
    user = database.getUser(callback_query.from_user.id)
    if user is not None and user[3] not in black_list_statuses:
        decision = callback_query.data.split(':')
        studentBtn = InlineKeyboardButton(text='Профиль студента', url=f'tg://user?id={decision[2]}')
        if decision[1] == 'accept':
            await callback_query.message.edit_text(callback_query.message.text + '\n\n<b>Принят!</b>',
                                                   parse_mode='HTML',
                                                   reply_markup=InlineKeyboardMarkup().add(studentBtn))
            result = database.confirmUser(decision[2], 'student', 'active')
            if result == 'Success':
                await bot.send_message(decision[2], 'Вы приняты в группу!')
            else:
                await callback_query.message.answer('Что-то пошло не так')
        elif decision[1] == 'decline':
            declined_user = database.getUser(decision[2])
            database.deleteUserFromGroup(declined_user[2], decision[2])
            await callback_query.message.edit_text(callback_query.message.text + '\n\n<b>Отклонён!</b>',
                                                   parse_mode='HTML',
                                                   reply_markup=InlineKeyboardMarkup().add(studentBtn))
            result = database.confirmUser(decision[2], 'student', 'declined')
            if result == 'Success':
                await bot.send_message(decision[2], 'Вас не приняли в группу..\n'
                                                    'Повторите попытку через час')
            else:
                await callback_query.message.answer('Что-то пошло не так')
    else:
        await callback_query.message.delete()
        await callback_query.answer('Нет доступа!', show_alert=True)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('course_num:'), state=head.CourseNum)
async def getCourseNum(callback_query: types.CallbackQuery, state: FSMContext):
    courses = {
        1: 'первый курс',
        2: 'второй курс',
        3: 'третий курс'
    }
    course_num = int(callback_query.data.replace('course_num:', ''))
    await callback_query.message.edit_text(f'Выберите Ваш курс: <b>{courses[course_num]}</b>', parse_mode='HTML')
    async with state.proxy() as data:
        await bot.delete_message(data['start_message_chat_id'], data['start_message_id'])
        group = database.getHeadOfGroup(data['group'])
        message = await callback_query.message.answer('Проверка')
        if group is not None:
            headOfGroup = InlineKeyboardButton(text='Написать старосте', url=f'tg://user?id={group[1]}')
            await callback_query.message.answer('Группа уже зарегистрирована!\n'
                                                f'ID старосты: <a href="tg://user?id={group[1]}">{group[1]}</a>\n'
                                                f'ID группы: {group[0]}', parse_mode='HTML',
                                                reply_markup=InlineKeyboardMarkup().add(headOfGroup))
        else:
            result = database.addGroup(data['group'], data['head'], course_num, data['group_name'])
            rs = database.addHead(data['head'], data['group'], callback_query.from_user.first_name)
            if rs == 'Error':
                user = database.getUser(data['head'])
                if user[1] == 'student':
                    await callback_query.message.answer(
                        'Вы не можете стать старостой, поскольку вы являетесь студентом другой группы!')
                    database.deleteGroup(data['group'])
                elif user[1] == 'head':
                    await callback_query.message.answer(
                        'Вы не можете стать старостой, поскольку вы являетесь старостой другой группы!')
                    database.deleteGroup(data['group'])
                else:
                    database.deleteUser(message.from_user.id)
                    database.addHead(data['head'], data['group'], callback_query.from_user.first_name)
            else:
                if result == 'Success':
                    database.addUserToGroup(data['group'], data['head'])
                    await callback_query.message.answer('Группа успешно зарегистрирована!')
                    deleteBtn = InlineKeyboardButton('Удалить', callback_data=f"group:{data['group']}:delete")
                    acceptBtn = InlineKeyboardButton('Принять', callback_data=f"group:{data['group']}:accept")
                    profileBtn = InlineKeyboardButton('Староста', url=f'tg://user?id={data["head"]}')
                    kb = InlineKeyboardMarkup(row_width=2).add(profileBtn)
                    kb.add(*[acceptBtn, deleteBtn])
                    for admin in config.ADMINS:
                        try:
                            await bot.send_message(admin,
                                                   f'Была создана новая группа под названием {data["group_name"]}',
                                                   reply_markup=kb)
                        except:
                            adminBtn = InlineKeyboardButton('Администратор', url=f'tg://user?id={admin}')
                            await bot.send_message(config.GLOBAL_ADMIN,
                                                   f'Не удаётся связаться с администратором <b>{admin}</b>',
                                                   reply_markup=InlineKeyboardMarkup().add(adminBtn), parse_mode='HTML')
                    try:
                        await bot.send_message(data['group'],
                                               f'Ваша группа зарегистрирована под названием {data["group_name"]}')
                        link = await get_start_link(data['group'], encode=True)
                        register_btn = InlineKeyboardButton('Регистрация', url=f"{link}",
                                                            callback_data=f'register:{data["group"]}')
                        msgToPin = await bot.send_message(data['group'],
                                                          f'Зарегистрируйтесь как студент этой группы, нажав на кнопку ниже.',
                                                          reply_markup=InlineKeyboardMarkup().add(register_btn))
                        try:
                            await bot.pin_chat_message(data['group'], msgToPin.message_id)
                        except:
                            print(f'[ERROR] Cannot pin message in group {data["group"]}')
                    except:
                        await callback_query.message.answer('Не удаётся отправить сообщение в вашу группу!')
                        print("[ERROR] Cannot send 'created' notification to group")
                    await asyncio.sleep(1.8)
                    await callback_query.message.edit_text('Группа успешно зарегистрирована!\n\n'
                                                           'Перед использованием бота настоятельно рекомендуем '
                                                           'прочитать <b>Правила и обязательства</b> сторон',
                                                           parse_mode='HTML',
                                                           reply_markup=InlineKeyboardMarkup().add(rulesBtn))

                else:
                    await callback_query.message.answer('Не удалось зарегистрировать группу!\n'
                                                        f'Произошла ошибка, обратитесь к <a href="tg://user?id={config.GLOBAL_ADMIN}">администратору</a>',
                                                        parse_mode='HTML')

        await asyncio.sleep(0.43)
        await bot.delete_message(message.chat.id, message.message_id)

    await state.finish()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('group:'), state='*')
async def confirmGroup(callback_query: types.CallbackQuery, state: FSMContext):
    user = database.getUser(callback_query.from_user.id)
    if callback_query.from_user.id in config.ADMINS:
        decision = callback_query.data.split(':')
        group = database.getHeadOfGroup(decision[1])
        if group is None:
            await callback_query.message.edit_text(callback_query.message.text + '\n\n<b>Группа удалена</b>',
                                                   parse_mode='HTML')
            return
        if group[4] == 'confirmed':
            if callback_query.from_user.id != config.GLOBAL_ADMIN or decision[2] == 'accept':
                await callback_query.message.edit_text(callback_query.message.text + '\n\n<b>Группа подтверждена</b>',
                                                       parse_mode='HTML')
                return

        if decision[2] == 'delete':
            await callback_query.message.edit_text(callback_query.message.text + '\n\n<b>Удалить</b>',
                                                   parse_mode='HTML')
            try:
                await bot.send_message(group[1],
                                       f'Ваша группа {group[3]} была удалена из-за несоответствий с правилами!')
                await bot.send_message(group[0],
                                       f'Ваша группа {group[3]} была удалена из-за несоответствий с правилами!')
            except:
                print(f'[ERROR] Cannot send notification to head of pre-deleted group {group[3]} or group')
            database.deleteGroup(decision[1])
        elif decision[2] == 'accept':
            database.editGroup(group[0], group[1], group[2], group[3], 'confirmed')
            try:
                await bot.send_message(group[1], f'Ваша группа {group[3]} подтверждена!')
                await callback_query.message.edit_text(callback_query.message.text + '\n\n<b>Принять</b>',
                                                       parse_mode='HTML')
            except:
                await callback_query.answer('Не удается отправить сообщение старосте!')
    else:
        await callback_query.answer('Нет доступа!')


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('supergroup:'), state='*')
async def confirmSuperGroup(callback_query: types.CallbackQuery, state: FSMContext):
    user = database.getUser(callback_query.from_user.id)
    if callback_query.from_user.id in config.ADMINS:
        decision = callback_query.data.split(':')
        group = database.getSupergroup(decision[1])
        if group is None:
            await callback_query.message.edit_text(callback_query.message.text + '\n\n<b>Супергруппа удалена</b>',
                                                   parse_mode='HTML')
            return
        if group[4] == 'confirmed':
            if callback_query.from_user.id != config.GLOBAL_ADMIN or decision[2] == 'accept':
                await callback_query.message.edit_text(
                    callback_query.message.text + '\n\n<b>Супергруппа подтверждена</b>',
                    parse_mode='HTML')
                return

        if decision[2] == 'delete':
            await callback_query.message.edit_text(callback_query.message.text + '\n\n<b>Удалить</b>',
                                                   parse_mode='HTML')
            try:
                await bot.send_message(group[4],
                                       f'Ваша супергруппа {group[1]} была удалена из-за несоответствий с правилами!')
                await bot.send_message(group[0],
                                       f'Ваша супергруппа {group[1]} была удалена из-за несоответствий с правилами!')
            except:
                print(f'[ERROR] Cannot send notification to manager of pre-deleted group {group[1]} or group')
            database.deleteSuperGroup(decision[1])
        elif decision[2] == 'accept':
            database.confirmSuperGroup(group[0])
            try:
                await bot.send_message(group[4], f'Ваша супергруппа {group[1]} подтверждена!')
                await callback_query.message.edit_text(callback_query.message.text + '\n\n<b>Принять</b>',
                                                       parse_mode='HTML')
            except:
                await callback_query.answer('Не удается отправить сообщение менеджеру!')
    else:
        await callback_query.answer('Нет доступа!')


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('mysupergroup:'), state='*')
async def mySuperGroup(callback_query: types.CallbackQuery, state: FSMContext):
    user = database.getUser(callback_query.from_user.id)
    if user is not None and user[3] not in black_list_statuses:
        supergroups = database.getSupergroupsOfUser(callback_query.from_user.id)
        if supergroups:
            decision = callback_query.data.split(':')
            if decision[1] == 'show':
                await state.finish()
                now_hour = dt.hour
                if 18 <= now_hour <= 23:
                    greeting = "Добрый вечер, "
                elif 0 <= now_hour <= 4:
                    greeting = "Доброй ночи, "
                elif 5 <= now_hour <= 11:
                    greeting = "Доброе утро, "
                else:
                    greeting = "Добрый день, "
                text = f"{greeting}<a href='tg://user?id={user[0]}'>{user[6]}</a>! \n" \
                       f"<b>Ваши супергруппы:</b>\n"
                kb = InlineKeyboardMarkup(row_width=2)
                for supergroup in supergroups:
                    text += f"• {supergroup[1]} - {'<b>Подтверждено</b>' if supergroup[2] == 'confirmed' else '<b>Неподтверждено</b>'}\n"
                    chat = await bot.get_chat(supergroup[0])
                    try:
                        url = chat.invite_link
                    except:
                        url = ""
                        text += f"<b>Нет прав администратора в группе {supergroup[1]}</b>\n\n"
                    if url is None:
                        try:
                            await bot.create_chat_invite_link(chat.id)
                            chat = await bot.get_chat(supergroup[0])
                            url = chat.invite_link
                        except:
                            url = None
                    if url is None:
                        continue
                    supergroupNameBtn = InlineKeyboardButton(text=supergroup[1], url=url)
                    enabled = f'{"Включено" if supergroup[3] else "Выключено"}'
                    supergroupSpamSwitch = InlineKeyboardButton(text=enabled,
                                                                callback_data=f'mysupergroup:spam:{supergroup[0]}:{not supergroup[3]}')
                    kb.add(*[supergroupNameBtn, supergroupSpamSwitch])
                text += "Супергруппа | Статус спам фильтра"
                kb.add(getMainMenuBtn)
                await callback_query.message.edit_text(text=text, reply_markup=kb)
            if decision[1] == 'spam':
                supergroup = database.getSupergroup(decision[2])
                if supergroup is not None and supergroup[4] == user[0]:
                    database.switchSpamFilterSuper(supergroup[0], decision[3])
                    supergroups = database.getSupergroupsOfUser(callback_query.from_user.id)
                    await state.finish()
                    now_hour = dt.hour
                    if 18 <= now_hour <= 23:
                        greeting = "Добрый вечер, "
                    elif 0 <= now_hour <= 4:
                        greeting = "Доброй ночи, "
                    elif 5 <= now_hour <= 11:
                        greeting = "Доброе утро, "
                    else:
                        greeting = "Добрый день, "
                    text = f"{greeting}<a href='tg://user?id={user[0]}'>{user[6]}</a>! \n" \
                           f"<b>Ваши супергруппы:</b>\n"
                    kb = InlineKeyboardMarkup(row_width=2)
                    for supergroup in supergroups:
                        text += f"• {supergroup[1]} - {'<b>Подтверждено</b>' if supergroup[2] == 'confirmed' else '<b>Неподтверждено</b>'}\n"
                        chat = await bot.get_chat(supergroup[0])
                        try:
                            url = chat.invite_link
                        except:
                            url = ""
                            text += f"<b>Нет прав администратора в группе {supergroup[1]}</b>\n\n"
                        supergroupNameBtn = InlineKeyboardButton(text=supergroup[1], url=url)
                        supergroupSpamSwitch = InlineKeyboardButton(
                            text=f'{"Включено" if supergroup[3] else "Выключено"}',
                            callback_data=f'mysupergroup:spam:{supergroup[0]}:{not supergroup[3]}')
                        kb.add(*[supergroupNameBtn, supergroupSpamSwitch])
                    text += "Супергруппа | Статус спам фильтра"
                    kb.add(getMainMenuBtn)
                    try:
                        await callback_query.message.edit_text(text=text, reply_markup=kb)
                    except MessageNotModified:
                        print(MessageNotModified)
                else:
                    await callback_query.answer('Нет доступа!')
        else:
            await callback_query.answer('У вас нет супергрупп!')


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('cancel_register:'),
                           state=[head.GroupName, head.CourseNum])
async def cancel_register_group(callback_query: types.CallbackQuery, state: FSMContext):
    head_id = callback_query.data.replace('cancel_register:', '')
    if callback_query.from_user.id == int(head_id):
        async with state.proxy() as data:
            for message in data['messages']:
                await bot.delete_message(message_id=message, chat_id=callback_query.message.chat.id)
            data.clear()
            await callback_query.message.edit_text('Регистрация группы отменена!')
    else:
        await callback_query.answer('Вы не можете ответить')


async def clearDeclinedUsers():
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)
        if dt.minute == 0:
            declinedUsers = database.getDeclinedUsers()
            for user in declinedUsers:
                group = database.getHeadOfGroup(user[2])
                applyBtn = InlineKeyboardButton('Отправить заявку', callback_data=f'apply:{user[0]}:{group[0]}')
                cancelBtn = InlineKeyboardButton('Отменить заявку', callback_data=f'apply_cancel:{user[0]}:{group[0]}')
                kb = InlineKeyboardMarkup(row_width=1).add(*[applyBtn, cancelBtn])
                try:
                    await bot.send_message(user[0], f'Прошёл час, а это значит что Вы снова можете подать заявку на '
                                                    f'вступлению в группу {group[3]}!\n', reply_markup=kb)
                except:
                    await bot.send_message(config.GLOBAL_ADMIN,
                                           f"Не удается отправить сообщение пользователю {user[0]}")
            await asyncio.sleep(60)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('apply'),
                           state='*')
async def apply_decision(callback_query: types.CallbackQuery, state: FSMContext):
    user = database.getUser(callback_query.from_user.id)
    if user is not None and user[3] in black_list_statuses:
        decision = callback_query.data.split(":")
        if decision[0] == 'apply':
            group = database.getHeadOfGroup(decision[2])
            studentBtn = InlineKeyboardButton(text='Профиль студента',
                                              url=f'tg://user?id={callback_query.from_user.id}')
            acceptBtn = InlineKeyboardButton('✅', callback_data=f'decision:accept:{callback_query.from_user.id}')
            declineBtn = InlineKeyboardButton('❌', callback_data=f'decision:decline:{callback_query.from_user.id}')
            kb = InlineKeyboardMarkup().add(*[acceptBtn, declineBtn])
            kb.add(studentBtn)
            try:
                await bot.send_message(group[1], f"Привет, староста!\n"
                                                 f"<a href='tg://user?id={decision[1]}'>{callback_query.from_user.first_name}</a> подал заявку "
                                                 f"на вступление в {group[3]}",
                                       parse_mode='HTML', reply_markup=kb)
                await callback_query.message.edit_text('Заявка отправлена!')
            except:
                await callback_query.message.edit_text('Не удается отправить заявку старосте!')
        elif decision[0] == 'apply_cancel':
            await callback_query.message.edit_text('Заявка отменена!')
            user = database.getUser(callback_query.from_user.id)
            if user[3] == 'waiting' or user[3] == 'declined':
                database.confirmUser(callback_query.from_user.id, 'unknown', 'in_process')
    else:
        await callback_query.message.delete()
        await callback_query.answer('Нет доступа!', show_alert=True)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('rules'), state='*')
async def getRules(callback_query: types.CallbackQuery, state: FSMContext):
    user = database.getUser(callback_query.from_user.id)
    if user is not None and user[3] not in black_list_statuses:
        decision = callback_query.data.split(':')
        getMainMenuBtn = InlineKeyboardButton('Главное меню', callback_data='profile:back')
        nextBtn = InlineKeyboardButton("Вперёд", callback_data=f'rules:{int(decision[1]) + 1}')
        prevBtn = InlineKeyboardButton("Назад", callback_data=f'rules:{int(decision[1]) - 1}')
        kb = InlineKeyboardMarkup(row_width=2)
        if decision[1] == '1':
            kb.add(nextBtn)
        elif decision[1] == '6':
            kb.add(prevBtn)
        else:
            kb.add(*[prevBtn, nextBtn])
        kb.add(getMainMenuBtn)
        await callback_query.message.edit_text(f"<b>Правила и обязательства:</b>\n\n"
                                               f"{rules[int(decision[1])]}", parse_mode='HTML', reply_markup=kb)
    else:
        await callback_query.message.delete()
        await callback_query.answer('Нет доступа!', show_alert=True)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('command:'), state='*')
async def runCommand(callback_query: types.CallbackQuery, state: FSMContext):
    user = database.getUser(callback_query.from_user.id)
    if user is not None and user[3] not in black_list_statuses:
        command = callback_query.data.split(':')
        if command[1] == 'all':
            commandStatus = database.getCommandStatus('all', callback_query.message.chat.id)
            print(commandStatus)
            if commandStatus is not None:
                if commandStatus[1] is False:
                    await callback_query.answer('Вам нужно подождать перед следующим вызовом!')
                    return
            else:
                initializeBtn = InlineKeyboardButton('Инициализировать',
                                                     callback_data=f'initialize:group:{callback_query.message.chat.id}')
                await callback_query.message.edit_text(
                    f'Привет, <a href="tg://user?id={callback_query.from_user.id}">{callback_query.from_user.first_name}</a>! '
                    f'Предлагаю инициализировать группу, чтобы можно было воспользоваться командой /all.',
                    reply_markup=InlineKeyboardMarkup().add(initializeBtn), parse_mode='HTML')
                return
            await callback_query.message.edit_text(f'{callback_query.from_user.first_name} вызвал участников группы..')
            users = database.getGroupUsersToNotify(callback_query.message.chat.id)
            text = ""
            for u in range(len(users)):
                user = database.getUser(users[u][1])
                if user is None:
                    database.deleteUserFromGroup(callback_query.message.chat.id, users[u][1])
                    continue
                if user[4] is None:
                    text += f'<a href="tg://user?id={user[0]}">{user[6]}</a> '
                else:
                    text += f'<a href="tg://user?id={user[0]}">{user[4]}</a> '
                if (u + 1) % 4 == 0 or len(users) == u + 1:
                    await callback_query.message.answer(text=text, parse_mode='HTML')
                    text = ""
            database.switchCommandStatus('all', callback_query.message.chat.id, False)
            await asyncio.sleep(180)
            database.switchCommandStatus('all', callback_query.message.chat.id, True)
    else:
        await callback_query.answer('Нет доступа!', show_alert=True)


async def onStart(_):
    await bot.send_message(config.GLOBAL_ADMIN, f'Бот запущен! [{dt.hour}:{dt.minute}]')
    database.switchAllCommandStatus('all', True)
    asyncio.create_task(setTime())
    asyncio.create_task(clearDeclinedUsers())
    asyncio.create_task(onMidnight())
    database.setUsersNotification(True)


async def checkNumOfGroupUsers():
    groups = database.getGroups()
    for group in groups:
        try:
            numOfStudents = await bot.get_chat_members_count(group[0]) - 1
        except:
            print(f'[ERROR] Cannot get the chat members count of group {group[0]} {group[3]}')
            continue
        print(f'{group[3]}:{numOfStudents} {database.getNumberOfStudents(group[0])[0]}')
        if numOfStudents > int(database.getNumberOfStudents(group[0])[0]):
            try:
                link = await get_start_link(group[0], encode=True)
                register_btn = InlineKeyboardButton('Регистрация', url=f"{link}",
                                                    callback_data=f'register:{group[0]}')
                if dt.hour == 20:
                    greeting = 'Добрый вечер'
                else:
                    greeting = 'Добрый день'
                await bot.send_message(group[0],
                                       f'{greeting}, группа {group[3]}! Кажется в вашей группе не все зарегистрировались? Нажмите на кнопку ниже чтобы зарегистрироваться🙃',
                                       reply_markup=InlineKeyboardMarkup().add(register_btn))
            except:
                print(f'[ERROR] Cannot send message to group {group[0]} {group[3]}')


@dp.message_handler(commands=['unreg'])
async def unregUser(message: types.Message):
    if message.chat.type != 'private':
        user = database.getUser(message.from_user.id)
        if user is not None:
            database.setUserNotification(False, user[0], message.chat.id)
            await message.answer('Вы исключены из призыва до тех пор, пока не напишите ничего!')
            unregged_chat_users = unregged_users.get(message.chat.id)
            if unregged_chat_users is None:
                unregged_users[message.chat.id] = []
            unregged_users[message.chat.id].append(message.from_user.id)


@dp.message_handler(commands=['getTime'])
async def getTime(message: types.Message):
    if message.from_user.id == config.GLOBAL_ADMIN:
        await message.answer(f'The time: {dt.hour}:{dt.minute}\n'
                             f'The day: {dt.day} of {dt.month} month')


async def onMidnight():
    while True:
        await asyncio.sleep(1)
        if dt.hour == 20:
            asyncio.create_task(checkNumOfGroupUsers())
            await asyncio.sleep(3600)
        if dt.hour == 0 or dt.hour == 10:
            database.setUsersNotification(True)
            print('[LOG] User birthdays checking')
            groups = database.getGroups()
            for group in groups:
                await asyncio.create_task(birthdayNotification(group[0]))
            await asyncio.sleep(3600)


async def onShutdown(_):
    await bot.send_message(config.GLOBAL_ADMIN, 'Бот выключается')


async def notifyGroupmates(users, bday_user, days, age):
    ending = config.endings[int(str(age)[-1])]
    print(days)
    if days == 0:
        text = f'Привет, сегодня день рождения у {bday_user[6]}!\n' \
               f'Не забудь его поздравить, ему исполняется {age} {ending}'
    elif 1 <= days <= 5 or days == 7:
        print(f'{bday_user[6]} {days}')
        if 1 <= days <= 2:
            txt = "Надеюсь, не забыли про подарок? 😏"
        else:
            txt = "Не забудьте про подарок🎁"
        text = f'Привет, у {bday_user[6]} день рождения через {config.birthday_endings[days]}!\n' \
               f'{txt}'

        userWish = database.getUserWish(bday_user[0])
        if userWish is None:
            database.addUserWish(bday_user[0], '')
            userWish = database.getUserWish(bday_user[0])

        if userWish[1] == '':
            try:
                wishBtn = InlineKeyboardButton('Выставить желание', callback_data='profile:wish')
                await bot.send_message(bday_user[0],
                                       'Привет, осталось совсем немного до твоего ДР, поскорее пиши своё пожелание, '
                                       'это упростит поиск подарка для тебя 🙃',
                                       reply_markup=InlineKeyboardMarkup().add(wishBtn))
            except:
                userBtn = InlineKeyboardButton(f'{bday_user[6]}', url=f'tg://user?id={bday_user[0]}')
                await bot.send_message(config.GLOBAL_ADMIN, 'Не удаётся отправить сообщение пользователю',
                                       reply_markup=InlineKeyboardMarkup().add(userBtn))

    else:
        text = f'Привет, у {bday_user[6]} день рождения через {config.birthday_endings[days]}!\n' \
               f'Ты можешь следить за днями рождения своих одногруппников через специальную панель,' \
               f'которая находится в главном меню'

        try:
            await bot.send_message(bday_user[0], 'Привет, кажется у кого-то день рождения через месяц😍\n'
                                                 'Зайди на свой профиль и укажи, что ты хочешь на своё ДР, чтобы '
                                                 'твоим одногруппникам '
                                                 'было проще найти тебе подарок 👍')
        except:
            headOfGroup = database.getHeadOfGroup(bday_user[2])
            userBtn = InlineKeyboardButton(f'{bday_user[6]}', url=f'tg://user?id={bday_user[0]}')
            try:
                await bot.send_message(headOfGroup[1],
                                       f'Не удаётся уведомить пользователя <b>{bday_user[0]}</b> о его дне рождения!',
                                       parse_mode='HTML'
                                       , reply_markup=InlineKeyboardMarkup().add(userBtn))
            except:
                headBtn = InlineKeyboardButton('Староста', url=f'tg://user?id={headOfGroup[0]}')
                for admin in config.ADMINS:
                    try:
                        await bot.send_message(admin,
                                               f'Не удаётся уведомить пользователя о его дне рождения <b>{bday_user[0]}</b>\n'
                                               f'Связь со старостой также недоступна!', parse_mode='HTML',
                                               reply_markup=InlineKeyboardMarkup(row_width=1).add(
                                                   *[userBtn, headBtn]))
                    except:
                        adminBtn = InlineKeyboardButton('Администратор', url=f'tg://user?id={admin}')
                        await bot.send_message(config.GLOBAL_ADMIN,
                                               f'Не удаётся связаться с администратором <b>{admin}</b>',
                                               reply_markup=InlineKeyboardMarkup().add(adminBtn),
                                               parse_mode='HTML')
        database.addUserWish(bday_user[0], '')

    bday_user_is_head = False
    declare_donateBtn = InlineKeyboardButton('Начать сбор', callback_data=f'donate:create:{bday_user[0]}')
    donateDeclared = database.getDeclaredDonate(bday_user[0])
    if bday_user[1] == 'head':
        bday_user_is_head = True
    for user in users:
        if user[0] != bday_user[0]:
            try:
                if user[1] == 'head':
                    if donateDeclared is None:
                        await bot.send_message(user[0], text + '\n\n<b>Староста, предлагаю объявить сбор</b>',
                                               parse_mode='HTML',
                                               reply_markup=InlineKeyboardMarkup().add(declare_donateBtn))
                    else:
                        await bot.send_message(user[0], text + '\n\n<b>Вы уже объявили сбор</b>', parse_mode='HTML')

                else:
                    if bday_user_is_head:
                        if donateDeclared is None:
                            await bot.send_message(user[0],
                                                   text + '\n\n<b>Обсудите с группой и решите ответственного за сбор на день рождения старосты!</b>',
                                                   parse_mode='HTML',
                                                   reply_markup=InlineKeyboardMarkup().add(declare_donateBtn))
                        else:
                            responsibleBtn = InlineKeyboardButton('Ответственный за сбор',
                                                                  url=f'tg://user?id={donateDeclared[3]}')
                            await bot.send_message(user[0], text + f'\n\n<b>Ответственный за сбор назначен!</b>',
                                                   parse_mode='HTML',
                                                   reply_markup=InlineKeyboardMarkup().add(responsibleBtn))
                    else:
                        await bot.send_message(user[0], text)
            except:
                headOfGroup = database.getHeadOfGroup(user[2])
                userBtn = InlineKeyboardButton(f'{user[6]}', url=f'tg://user?id={user[0]}')
                try:
                    await bot.send_message(headOfGroup[1],
                                           f'Не удаётся уведомить пользователя <b>{user[0]}</b> о дне рождения!',
                                           parse_mode='HTML'
                                           , reply_markup=InlineKeyboardMarkup().add(userBtn))
                except:
                    headBtn = InlineKeyboardButton('Староста', url=f'tg://user?id={headOfGroup[0]}')
                    for admin in config.ADMINS:
                        try:
                            await bot.send_message(admin,
                                                   f'Не удаётся уведомить пользователя о дне рождения <b>{user[0]}</b>\n'
                                                   f'Связь со старостой также недоступна!', parse_mode='HTML',
                                                   reply_markup=InlineKeyboardMarkup(row_width=1).add(
                                                       *[userBtn, headBtn]))
                        except:
                            adminBtn = InlineKeyboardButton('Администратор', url=f'tg://user?id={admin}')
                            await bot.send_message(config.GLOBAL_ADMIN,
                                                   f'Не удаётся связаться с администратором <b>{admin}</b>',
                                                   reply_markup=InlineKeyboardMarkup().add(adminBtn),
                                                   parse_mode='HTML')


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('donate:'), state='*')
async def declare_donate(callback_query: types.CallbackQuery, state: FSMContext):
    responsible = database.getUser(callback_query.from_user.id)
    if responsible is not None:
        if responsible[3] not in black_list_statuses:
            decision = callback_query.data.split(':')
            if database.getUser(decision[2]) is None:
                await callback_query.message.edit_text(
                    callback_query.message.text + "\n\n<b>Пользователь покинул группу!</b>", parse_mode='HTML')
                return
            if decision[1] == 'create':
                await callback_query.message.edit_text(callback_query.message.text + "\n\n<b>Вы объявили сбор</b>",
                                                       parse_mode='HTML')
                donate_declared = database.getDeclaredDonate(decision[2])
                if donate_declared is not None:
                    user = database.getUser(donate_declared[3])
                    text = f"\n\n<b>Сбор уже объявлен пользователем {user[6]}</b> "
                    await callback_query.message.edit_text(f'{callback_query.message.text + text}', parse_mode='HTML')
                else:
                    users = database.getGroupUsers(responsible[2])
                    bday_user = database.getUser(decision[2])
                    for user in users:
                        if user[0] != int(decision[2]):
                            try:
                                await bot.send_message(user[0],
                                                       f'{responsible[6]} объявил сбор на день рождения {bday_user[6]}!\n'
                                                       f'Посмотреть сколько собралось или поспособствовать сбору денег можешь '
                                                       f'через команду "Моя группа" в главном меню👌')
                            except:
                                userBtn = InlineKeyboardButton(f'{user[6]}', url=f'tg://user?id={user[0]}')
                                await bot.send_message(config.ADMINS, f'Не удаётся связаться с {user[0]}',
                                                       reply_markup=InlineKeyboardMarkup().add(userBtn))
                            database.addUserToBirthdayDonate(decision[2], user[0], responsible[0])

            #'donate:confirm:{decision[3]}:{callback_query.from_user.id}:{decision[2]}')
            #'donate:decline:{decision[3]}:{callback_query.from_user.id}')
            if decision[1] == 'confirm':
                donate = database.getDonateProcess(decision[3],decision[2])
                if int(donate[0]) == int(decision[4]):
                    database.confirmDonate(decision[3],decision[2],decision[4])
                    try:
                        await bot.send_message(int(decision[3]),f"Ваша сумма ({decision[4]}) принята ответственным за сбор!")
                    except:
                        print(f"[ERROR] Cannot notify user {decision[3]}")
                    await callback_query.message.edit_text(callback_query.message.html_text+"\n\n<b>Подтверждено</b>")
                else:
                    await callback_query.message.edit_text(callback_query.message.html_text+"\n\n<b>Неактуально..</b>")
            if decision[1] == 'decline':
                try:
                    await bot.send_message(int(decision[3]), f"Ваша сумма не принята ответственным за сбор!")
                except:
                    print(f"[ERROR] Cannot notify user {decision[3]}")
                await callback_query.message.edit_text(callback_query.message.html_text+"\n\n<b>Отклонено</b>")


async def birthdayNotification(group_id):
    users = database.getGroupUsers(group_id)
    for user in users:
        userBirthday, age = functions.getUserBirthday(user[0], dt)
        if userBirthday is None:
            try:
                bdayBtn = InlineKeyboardButton('Выставить ДР', callback_data='profile:birthday')
                await bot.send_message(user[0],
                                       f'Привет, {user[6]}, предлагаю тебе установить дату своего дня рождения :)',
                                       reply_markup=InlineKeyboardMarkup().add(bdayBtn))
            except:
                print(f'[LOG] Cannot send message to {user[0]}')
            continue
        if userBirthday == -5:
            database.deleteUserWish(user[0])
        if userBirthday == 0:
            await notifyGroupmates(users, user, userBirthday, age)
            try:
                await bot.send_message(user[0],
                                       f'Здравствуй, {user[6]}, поздравляем тебя с {age} летием от лица администрации проекта.\n'
                                       f'{random.choice(config.random_congratulations)}')
            except:
                headOfGroup = database.getHeadOfGroup(user[2])

                userBtn = InlineKeyboardButton(f'{user[6]}', url=f'tg://user?id={user[0]}')
                try:
                    await bot.send_message(headOfGroup[1],
                                           f'Не удаётся поздравить с днём рождения пользователя <b>{user[0]}</b>',
                                           parse_mode='HTML'
                                           , reply_markup=InlineKeyboardMarkup().add(userBtn))
                except:
                    headBtn = InlineKeyboardButton('Староста', url=f'tg://user?id={headOfGroup[0]}')
                    for admin in config.ADMINS:
                        try:
                            await bot.send_message(admin,
                                                   f'Не удаётся поздравить с днём рождения пользователя <b>{user[0]}</b>\n'
                                                   f'Связь со старостой также недоступна!', parse_mode='HTML',
                                                   reply_markup=InlineKeyboardMarkup(row_width=1).add(
                                                       *[userBtn, headBtn]))
                        except:
                            adminBtn = InlineKeyboardButton('Администратор', url=f'tg://user?id={admin}')
                            await bot.send_message(config.GLOBAL_ADMIN,
                                                   f'Не удаётся связаться с администратором <b>{admin}</b>',
                                                   reply_markup=InlineKeyboardMarkup().add(adminBtn), parse_mode='HTML')
        if userBirthday == 7 or userBirthday == 30 or 1 <= userBirthday <= 5:
            await notifyGroupmates(users, user, userBirthday, age)


@dp.message_handler(commands=['chat'])
async def getChat(message: types.Message):
    print(await bot.get_chat(message.chat.id))


@dp.message_handler()
async def msgHandler(message: types.Message, state: FSMContext):
    # if "https://t.me/" in message.text:
    #     await message.delete()
    #     try:
    #         await bot.restrict_chat_member(message.chat.id, message.from_user.id, ChatPermissions(False))
    #     except:
    #         print(f'[ERROR] Cannot restrict the user {message.from_user.id}')
    #     random_task = random.choice(list(config.confirm_tasks.keys()))
    #     answers = [random_task]
    #     while len(answers) != 3:
    #         num = random.randint(0, 100)
    #         if num not in answers:
    #             answers.append(num)
    #
    #     btns = []
    #     for i in sorted(answers):
    #         if i == random_task:
    #             solBtn = InlineKeyboardButton(f'{i}', callback_data=f'spam:{message.from_user.id}:correct')
    #         else:
    #             solBtn = InlineKeyboardButton(f'{i}', callback_data=f'spam:{message.from_user.id}:incorrect')
    #         btns.append(solBtn)
    #
    #     await message.answer(f"<a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>, Ваши права ограничены!\n"
    #                          f"Причина: <b>Распространение вредоносных ссылок</b>\n\n"
    #                          f"Подтвердите что Вы не бот. \n"
    #                          f"Сколько будет {config.confirm_tasks[random_task]}?", reply_markup=InlineKeyboardMarkup().add(*btns))

    chatId = unregged_users.get(message.chat.id)
    if chatId is not None:
        if message.from_user.id in unregged_users[message.chat.id]:
            unregged_users[message.chat.id].remove(message.from_user.id)
            database.setUserNotification(True, message.from_user.id, message.chat.id)

    print(f'{await bot.get_chat_members_count(chat_id=message.chat.id)} {message.chat.id}')
    print(f'{message.from_user.username} {message.text}')



if __name__ == '__main__':
    executor.start_polling(dp, allowed_updates=["callback_query", "message", "chat_member", "my_chat_member"],
                           skip_updates=True,
                           on_startup=onStart, on_shutdown=onShutdown)
