print('IP already exists. Do you want to change the nickname from ')
    answer = input()
    if answer == 'y' or answer == 'Y':
        if nickname in settings.friendList.values():
            print('Warning: nicknames repeated')
        settings.friendList[ip] = nickname
        save_data()
    else:
        return