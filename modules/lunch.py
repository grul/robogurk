import pickle, os, traceback


HELP_MESSAGE = '.lunch list | .lunch add name: description | .lunch show name | .lunch del name | .lunch help'

class Lunch:
    def __init__(self, bot):
        self.bot = bot
        self.filename = 'lunch.pickle'
        self.load_lunch_file()
        self.bot.add_privmsg_listener(self.privmsg_callback)

    def load_lunch_file(self):
        if os.path.isfile(self.filename):
            try:
                lunch_file = open(self.filename, 'rb')
                self.lunch = pickle.load(lunch_file)
                lunch_file.close()
                print('LUNCH: loaded lunch from file: ' + self.filename)
                print(self.lunch)
            except:
                traceback.print_exc()
        else:
            self.lunch = {}
            self.save_lunch_file()

    def save_lunch_file(self):
        try:
            lunch_file = open(self.filename, 'wb')
            pickle.dump(self.lunch, lunch_file)
            lunch_file.close()
            print('LUNCH FILE SAVED')
        except:
            traceback.print_exc()
            print('LUNCH SAVE ERROR')

    def privmsg_callback(self, sender, channel, msg):
        if channel != '':
            sender = channel
        if msg.startswith('.lunch'):
            if msg[7:11] == 'help' or msg.strip() == '.lunch':
                self.send_msg(sender, HELP_MESSAGE)
            if msg[7:11] == 'list':
                self.send_list_msg(sender)
            if msg[7:10] == 'add':
                self.add_lunch_place(sender, msg[11:])
            if msg[7:10] == 'del':
                self.del_lunch_place(sender, msg[11:])
            if msg[7:11] == 'show':
                print('#' + msg[12:] + '#')
                self.send_show_msg(sender, msg[12:])

    def send_list_msg(self, sender):
        msg = ', '.join(sorted(self.lunch))
        self.send_msg(sender, msg)

    def send_show_msg(self, sender, name):
        name = name.strip()
        if name in self.lunch:
            desc = self.lunch[name]
            self.send_msg(sender, name + ': ' + desc)
        else:
            self.send_msg(sender, name + ' not found')

    def add_lunch_place(self, sender, msg):
        if ':' in msg:
            name, desc = msg.split(':', 1)
        else:
            name = msg
            desc = ''
        name = name.strip()
        desc = desc.strip()
        if name in self.lunch:
            self.send_msg(sender, name + ' already exists with the description: ' + self.lunch[name])
        else:
            if name == '':
                self.send_msg(sender, 'unable to add without a name')
            else:
                self.lunch[name] = desc
                self.save_lunch_file()
                self.send_msg(sender, 'added ' + name + ': ' + desc)

    def del_lunch_place(self, sender, name):
        name = name.strip()
        if name in self.lunch:
            del self.lunch[name]
            self.save_lunch_file()
            self.send_msg(sender, 'deleted ' + name)
        else:
            self.send_msg(sender, name + ' not found')

    def send_msg(self, sender, msg):
        self.bot.queue_message(sender, msg)








