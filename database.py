import sqlite3

import psycopg2

connection = psycopg2.connect("postgres://vtkjqzpzucvlrr:bca62e7528621f3094dd3f3ac7e7c8b7d2a1068fe053b3e4dd140b9c10a96886@ec2-52-19-188-149.eu-west-1.compute.amazonaws.com:5432/d16ef7la7uufg2")
# connection = sqlite3.connect("db")
cursor = connection.cursor()


def getUser(id):
    sql = f"select * from users where id={id}"
    cursor.execute(sql)
    return cursor.fetchone()

def getUsers():
    sql = f"select * from users where status='active"
    cursor.execute(sql)
    return cursor.fetchall()

def getDeclinedUsers():
    sql = "select * from users where status='declined'"
    cursor.execute(sql)
    return cursor.fetchall()


def getHeadOfGroup(group_id):
    sql = f"select * from groups where id={group_id}"
    cursor.execute(sql)
    return cursor.fetchone()


def getNumberOfStudents(group_id):
    sql = f"select count(*) from users where group_id = {group_id} and status='active'"
    cursor.execute(sql)
    return cursor.fetchone()

def addGroup(group_id, head, course, group_name):
    sql = f"INSERT INTO public.groups(id, head, course, group_name)	VALUES ({group_id}, {head}, {course}, '{group_name}');"
    try:
        cursor.execute(sql)
        connection.commit()
        return "Success"
    except:
        connection.rollback()
        return "Error"

def addUser(id, chat_id, tg_name):
    sql = f"select * from groups where id={chat_id}"
    cursor.execute(sql)
    group = cursor.fetchone()
    if group is None:
        return "Group doesn't exist!"
    else:
        sql = f"INSERT INTO public.users(id, group_id, status, tg_name) VALUES ({id}, {chat_id}, 'waiting', '{tg_name}');"
        try:
            cursor.execute(sql)
            connection.commit()
            return "Success!"
        except:
            connection.rollback()
            return "Something went wrong!"

def addUserToGroup(chat_id, user_id):
    cursor.execute(f"delete from usersingroup where user_id = {user_id} and group_id={chat_id}")
    connection.commit()
    sql = f"INSERT INTO public.usersingroup(group_id, user_id, notifications) VALUES ({chat_id}, {user_id}, {True});"
    try:
        cursor.execute(sql)
        connection.commit()
        print(f'[LOG] User {user_id} added to group {chat_id}')
    except:
        connection.rollback()
        print(f'[ERROR] Cannot add user {user_id} to group {chat_id}')

def deleteUserFromGroup(chat_id, user_id):
    sql = f"delete from usersingroup where group_id={chat_id} and user_id={user_id}"
    try:
        cursor.execute(sql)
        connection.commit()
        print(f'[LOG] User {user_id} deleted from group {chat_id}')
    except:
        connection.rollback()
        print(f'[ERROR] Cannot delete user {user_id} from group {chat_id}')

def deleteGroup(id):
    sql =f" delete from questions where group_id={id}"
    cursor.execute(sql)
    connection.commit()
    sql = f"delete from command_all where group_id={id}"
    try:
        cursor.execute(sql)
        connection.commit()
        sql = f"delete from usersingroup where group_id = {id}"
        cursor.execute(sql)
        connection.commit()
        sql = f"delete from users where group_id = {id}"
        try:
            cursor.execute(sql)
            connection.commit()
            try:
                sql = f"delete from groups where id = {id}"
                cursor.execute(sql)
                connection.commit()
                print(f"[LOG] Group {id} deleted")
            except:
                connection.rollback()
                print(f"[ERROR] Group {id} cannot be deleted")
        except:
            connection.rollback()
            print(f"[ERROR] Students of group {id} cannot be deleted")
    except:
        connection.rollback()
        print(f'[ERROR] Cannot delete all command of group {id}')

def addHead(id, chat_id, name):
    sql = f"INSERT INTO public.users(id, role, group_id, status, tg_name) VALUES ({id}, 'head', {chat_id}, 'active','{name}');"
    try:
        cursor.execute(sql)
        connection.commit()
        print(f'[SUCCESS] Head {id} added')
    except:
        print(f'[ERROR] Cannot add head {id}')
        connection.rollback()
        return "Error"

def confirmUser(id, role, status):
    sql = f"UPDATE public.users SET role='{role}', status='{status}' WHERE id={id};"
    try:
        cursor.execute(sql)
        connection.commit()
        print(f'[SUCCESS] User {id} confirmed')
        return "Success"
    except:
        connection.rollback()
        print(f'[ERROR] Cannot confirm user {id}')
        return "Error"

def deleteUser(id):
    sql = f"delete from usersingroup where user_id={id}"
    cursor.execute(sql)
    connection.commit()
    sql = f"delete from wish where user_id={id}"
    cursor.execute(sql)
    connection.commit()
    sql = f"delete from users where id={id}"
    try:
        cursor.execute(sql)
        connection.commit()
        print(f'[LOG] User {id} deleted')
    except:
        connection.rollback()
        print(f'[ERROR] User {id} cannot be deleted')

def editGroup(id, head, course, group_name, status):
    sql = f"UPDATE public.groups SET head={head}, course={course}, group_name='{group_name}', status='{status}' WHERE id={id};"
    try:
        cursor.execute(sql)
        connection.commit()
        print(f"[LOG] Group {group_name} {id} edited")
    except:
        connection.rollback()
        print(f"[ERROR] Group {group_name} {id} cannot be edited")

def setEmoji(user_id, emoji):
    sql = f"update users set emoji='{emoji}' where id={user_id}"
    try:
        cursor.execute(sql)
        connection.commit()
        print(f"[LOG] User {user_id} emoji updated")
    except:
        connection.rollback()
        print(f"[ERROR] User {user_id} emoji cannot be updated")


def setBirthday(user_id, birthday):
    sql = f"update users set birthday='{birthday}' where id={user_id}"
    try:
        cursor.execute(sql)
        connection.commit()
        print(f"[LOG] User {user_id} birthday updated")
    except:
        connection.rollback()
        print(f"[ERROR] User {user_id} birthday cannot be updated")

def getGroupUsersToNotify(group_id):
    sql = f"select distinct * from usersingroup where group_id={group_id} and notifications={True}"
    cursor.execute(sql)
    return cursor.fetchall()

def getCommandStatus(command, group_id):
    sql = f"select * from command_{command} where group_id = {group_id}"
    print(sql)
    cursor.execute(sql)
    return cursor.fetchone()

def switchCommandStatus(command, group_id, status):
    command_status = getCommandStatus(command, group_id)
    if command_status is None:
        sql = f"INSERT INTO public.command_{command}(group_id, status) VALUES ({group_id}, {status});"
        try:
            cursor.execute(sql)
            connection.commit()
        except:
            connection.rollback()
            print(f'[ERROR] Command status cannot be changed {command} , {group_id} , {status}')
    else:
        sql = f"update command_{command} set status={status} where group_id = {group_id}"
        try:
            cursor.execute(sql)
            connection.commit()
        except:
            connection.rollback()
            print(f'[ERROR] Cannot update command {command} status to {status}')

def switchAllCommandStatus(command, status):
    sql = f"update command_{command} set status = {status}"
    try:
        cursor.execute(sql)
        connection.commit()
    except:
        connection.rollback()
        print(f'[ERROR] Cannot update command {command} statuses to {status}')

def getGroupUsers(group_id):
    sql = f"select * from users where group_id = {group_id} and status='active'"
    cursor.execute(sql)
    return cursor.fetchall()

def getGroups():
    sql = f"select * from groups"
    cursor.execute(sql)
    return cursor.fetchall()

def addUserWish(user_id, wish):
    sql = f"delete from wish where user_id = {user_id}"
    cursor.execute(sql)
    connection.commit()
    sql = f"INSERT INTO public.wish(user_id, wish) VALUES ({user_id}, '{wish}');"
    try:
        cursor.execute(sql)
        connection.commit()
        return True
    except:
        print(f'[ERROR] Cannot add user {user_id} wish')
        connection.rollback()
        return False

def getDeclaredDonate(bday_user_id):
    sql = f"select * from birthday_donate where user_id = {bday_user_id}"
    cursor.execute(sql)
    return cursor.fetchone()

def addUserToBirthdayDonate(user_id, donater_id,responsible_id):
    sql = f"INSERT INTO public.birthday_donate(user_id, donater_id, donate_sum, responsible) VALUES ({user_id}, {donater_id},0,{responsible_id});"
    try:
        cursor.execute(sql)
        connection.commit()
    except:
        connection.rollback()
        print('[ERROR] Cannot add user to birthday table')

def getUsersWishOfGroup(group_id, user_id):
    sql = f"select * from users join wish on id = user_id where group_id = {group_id} and id <> {user_id}"
    cursor.execute(sql)
    return cursor.fetchall()

def getUserDonateSum(user_id):
    sql = f"select sum(donate_sum) from birthday_donate where donater_id={user_id}"
    cursor.execute(sql)
    return cursor.fetchone()

def getUserDonatesSum(user_id):
    sql = f"select sum(donate_sum) from birthday_donate where user_id = {user_id}"
    cursor.execute(sql)
    return cursor.fetchone()

def getUserWish(id):
    sql = f"select * from wish where user_id={id}"
    cursor.execute(sql)
    return cursor.fetchone()

def setUserWish(user_id, wish):
    sql = f"UPDATE public.wish SET wish='{wish}' WHERE user_id = {user_id};"
    try:
        cursor.execute(sql)
        connection.commit()
        print(f'[LOG] User {user_id} wish set')
    except:
        connection.rollback()
        print(f'[ERROR] Cannot update user {user_id} wish')

def deleteUserWish(user_id):
    sql = f"delete from wish where user_id = {user_id}"
    cursor.execute(sql)
    connection.commit()

def deleteUserBdayDonates(user_id):
    sql = f"delete from birthday_donate where user_id = {user_id}"
    cursor.execute(sql)
    connection.commit()

def getUserWishWithUserData(user_id):
    sql = f"select * from users join wish on id = user_id where id = {user_id}"
    cursor.execute(sql)
    return cursor.fetchone()

def addQuestion(question, group_id, user_id):
    sql = f"INSERT INTO public.questions(question, group_id, owner_id, read) VALUES ('{question}', {group_id}, {user_id}, {False});"
    try:
        cursor.execute(sql)
        connection.commit()
        print('[LOG] New question added')
        return True
    except:
        connection.rollback()
        print('[ERROR] Question cannot be added!')
        return False

def getUserQuestions(user_id):
    sql = f"select * from questions where owner_id={user_id}"
    cursor.execute(sql)
    return cursor.fetchall()

def getQuestion(question_id):
    sql = f"select * from questions where question_id={question_id}"
    cursor.execute(sql)
    return cursor.fetchone()
def deleteQuestion(question_id):
    sql = f"delete from questions where question_id={question_id}"
    cursor.execute(sql)
    connection.commit()

def getInteresting(group_id):
    sql = f"select * from questions where group_id={group_id} and interesting={True} or global={True}"
    cursor.execute(sql)
    return cursor.fetchall()

def getGroupQuestions(group_id):
    sql = f"select * from questions where group_id = {group_id}"
    cursor.execute(sql)
    return cursor.fetchall()

def getGroupQuestionsBool(group_id, read):
    sql = f"select * from questions where group_id = {group_id} and read={read}"
    cursor.execute(sql)
    return cursor.fetchall()

def updateQuestionReadStatus(question_id, read):
    sql = f"UPDATE public.questions SET read={read} WHERE question_id = {question_id};"
    try:
        cursor.execute(sql)
        connection.commit()
        print(f'[LOG] Question {question_id} set read {read}')
    except:
        connection.rollback()
        print(f'[ERROR] Question {question_id} set read {read} was now executed')
def switchSpamFilter(group_id, status):
    sql = f"update groups set spam_filter = {status} where id = {group_id}"
    try:
        cursor.execute(sql)
        connection.commit()
        print(f'[LOG] Spam filter status is {status} | group {group_id}')
    except:
        connection.rollback()
        print(f'[ERROR] Spam filter cannot be updated | group {group_id} | status {status}')

def switchSpamFilterSuper(group_id, status):
    sql = f"update supergroups set spam_filter = {status} where id = {group_id}"
    try:
        cursor.execute(sql)
        connection.commit()
        print(f'[LOG] Spam filter status is {status} | supergroup {group_id}')
    except:
        connection.rollback()
        print(f'[ERROR] Spam filter cannot be updated | supergroup {group_id} | status {status}')



def deleteUsersFromGroup(group_id):
    cursor.execute(f'delete from usersingroup where group_id={group_id}')
    connection.commit()

def setQuestionAnswer(question_id, answer):
    try:
        cursor.execute(f"UPDATE public.questions SET answer='{answer}' WHERE question_id={question_id};")
        connection.commit()
        return True
    except:
        connection.rollback()
        return False

def setQuestionInterestingStatus(question_id, status):
    try:
        cursor.execute(f"UPDATE public.questions SET interesting={status} WHERE question_id={question_id};")
        connection.commit()
    except:
        connection.rollback()

def getAdmins():
    cursor.execute('select * from admins')
    return cursor.fetchall()

def getAdmin(id):
    cursor.execute(f'select * from admins where id = {id}')
    return cursor.fetchone()

def getGroupsForAdmin(courses):
    if courses is None:
        sql = "select * from groups"
    elif len(courses) == 1:
        sql = f"select * from groups where course = {courses}"
    else:
        sql = f"select * from groups where course in {courses}"

    cursor.execute(sql)
    return cursor.fetchall()
def addLog(user_id, action, reason, date):
    try:
        cursor.execute(f"INSERT INTO public.logs(user_id, action, reason, date) VALUES ({user_id}, '{action}', '{reason}', '{date}');")
        connection.commit()
    except:
        connection.rollback()

def addSuperGroup(group, manager_id):
    try:
        cursor.execute(f"INSERT INTO public.supergroups(id, group_name, spam_filter, manager) VALUES ({group.id}, '{group.title}', false, {manager_id});")
        connection.commit()
        return True
    except:
        connection.rollback()
        return False

def getSupergroup(group_id):
    cursor.execute(f'select * from supergroups where id={group_id}')
    return cursor.fetchone()


def confirmSuperGroup(id):
    sql = f"UPDATE public.supergroups SET status='confirmed' WHERE id={id};"
    try:
        cursor.execute(sql)
        connection.commit()
        print(f"[LOG] Supergroup {id} confirmed")
    except:
        connection.rollback()
        print(f"[ERROR] Supergroup {id} cannot be confirmed")

def deleteSuperGroup(id):
    cursor.execute(f'delete from supergroups where id={id}')
    connection.commit()
    print(f"[LOG] Supergroup {id} deleted")

def setUserNotification(status, user_id, group_id):
    try:
        cursor.execute(f'update usersingroup set notifications={status} where user_id = {user_id} and group_id = {group_id}')
        connection.commit()
    except:
        connection.rollback()

def setUsersNotification(status):
    try:
        cursor.execute(f'update usersingroup set notifications={status}')
        connection.commit()
    except:
        connection.rollback()

def getSupergroupsOfUser(user_id):
    cursor.execute(f"select * from supergroups where manager={user_id}")
    return cursor.fetchall()

def sendDonate(donater_id, bday_id, amount, responsible_id):
    donate = getDonateProcess(donater_id, bday_id)
    if donate is not None:
        cursor.execute(f"Update birthday_donate set in_process={amount} where donater_id={donater_id} and user_id={bday_id}")
    else:
        cursor.execute(f"insert into birthday_donate(user_id,donater_id, responsible, in_process) values({bday_id},{donater_id},{responsible_id}, {amount})")
    connection.commit()

def confirmDonate(donater_id, bday_id, amount):
    cursor.execute(f"Update birthday_donate set donate_sum={amount} where donater_id={donater_id} and user_id={bday_id}")
    connection.commit()

def getDonateProcess(donater_id, bday_id):
    sql = f"select in_process from birthday_donate where donater_id = {donater_id} and user_id={bday_id}"
    cursor.execute(sql)
    return cursor.fetchone()