import telebot #импорт pyTelegramBotAPI 
import pandas as pd
from src.config import TOKEN
from src.strings import STRINGS
strings = STRINGS()


class NotesBot():
  is_user_enter = False
  def run(self):
    self.bot.polling(none_stop=True, interval=0)

  def create_buttons(self):
    self.keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    self.keyboard.row(strings.add_notes)
    #self.keyboard.row(strings.add_reminders)
    self.keyboard.row(strings.show_notes)
    self.keyboard.row(strings.delete_note)

  def enter1(self, message):
    msg = self.bot.send_message(message.chat.id, text = strings.register_nick)
    self.bot.register_next_step_handler(msg, self.enter2)


  def enter2(self, message):
    if not self.nicknames[(self.nicknames['Nickname'] == message.text)].empty:
      self.nickname = message.text
      msg = self.bot.send_message(message.chat.id, text = strings.enter_password)
      self.bot.register_next_step_handler(msg, self.enter3)
    else:
      self.bot.send_message(message.chat.id, text = strings.no_such_nickname)


  def enter3(self, message):
    if not self.nicknames[(self.nicknames['Nickname'] == self.nickname) & (self.nicknames['Password'] == message.text)].empty:
      self.is_user_enter = True
      self.create_buttons()
      self.bot.send_message(message.chat.id, text = strings.succesfull_enter, reply_markup=self.keyboard)
    else:
      self.bot.send_message(message.chat.id, text = strings.incorrect_password)

  def create_user1(self, message):
    msg = self.bot.send_message(message.chat.id, text = strings.register_nick)
    self.bot.register_next_step_handler(msg, self.create_user2)
  
  def create_user2(self, message):
    if self.nicknames[(self.nicknames['Nickname'] == message.text)].empty:
      self.nickname = message.text
      msg = self.bot.send_message(message.chat.id, text = strings.create_password)
      self.bot.register_next_step_handler(msg, self.create_user3)
    else:
      self.bot.send_message(message.chat.id, text = strings.this_nickname_exists)

  
  def create_user3(self, message):
    self.nicknames.loc[len(self.nicknames.index)] = [self.nickname, message.text]
    self.nicknames.to_csv('src/nicknames.csv', index=False)
    self.is_user_enter = True
    self.create_buttons()
    self.bot.send_message(message.chat.id, text = strings.user_created, reply_markup=self.keyboard)
  
  def add_note(self, message):
    if not self.notes[(self.notes['Nickname'] == self.nickname)]['Index'].empty:
      self.notes.loc[len(self.notes.index)] = [self.nickname, self.notes[(self.notes['Nickname'] == self.nickname)]['Index'].tail(1).values[0] + 1, message.text]
    else:
      self.notes.loc[len(self.notes.index)] = [self.nickname, 1, message.text]
    self.notes.to_csv('src/notes.csv', index=False)
    self.bot.send_message(message.chat.id, text = strings.note_added)
  
  def show_notes(self, message):
    if not self.notes[(self.notes['Nickname'] == self.nickname)].empty:
      s= ''
      for i,j in zip(self.notes[(self.notes['Nickname'] == self.nickname)]['Note'].tolist(), self.notes[(self.notes['Nickname'] == self.nickname)]['Index'].tolist()):
        s += str(j) + ': ' + i + '\n'
      self.bot.send_message(message.chat.id, text = s)
    else:
      self.bot.send_message(message.chat.id, text = strings.notes_dont_exist)
  
  def delete_note(self, message):
    if message.text.isdigit():
      self.notes = self.notes[(self.notes['Nickname'] != self.nickname) | (self.notes['Index'] != int(message.text))]
      self.notes.to_csv('src/notes.csv', index=False)
    else:
      self.bot.send_message(message.chat.id, text = strings.number_error)


  def __init__(self):
    self.bot = telebot.TeleBot(TOKEN)
    self.nicknames = pd.read_csv('src/nicknames.csv')
    self.notes = pd.read_csv('src/notes.csv')


    @self.bot.message_handler(commands=['start'])
    def process_start(message):
        keyboard = telebot.types.ReplyKeyboardMarkup(True, False)
        keyboard.row(strings.enter_as_user)
        keyboard.row(strings.add_user)
        self.bot.send_message(message.chat.id, text = strings.hello_string, reply_markup = keyboard)



    @self.bot.message_handler(content_types=['text'])
    def second(message):
      if self.is_user_enter:
        if message.text == strings.add_notes :
          msg = self.bot.send_message(message.chat.id, text = strings.add_note_text)
          self.bot.register_next_step_handler(msg, self.add_note)
        if message.text == strings.add_reminders:
          msg = self.bot.send_message(message.chat.id, text = strings.add_reminder_text)
        if message.text == strings.show_notes:
          self.show_notes(message)
        if message.text == strings.delete_note:
          msg = self.bot.send_message(message.chat.id, text = strings.choose_deleted_note)
          self.bot.register_next_step_handler(msg, self.delete_note)
      else:
        if message.text == strings.enter_as_user:
          self.enter1(message) # можно сделать проверку человека при помощи message.chat.username
        if message.text == strings.add_user:
          self.create_user1(message)


NotesBot().run()
  # bot.send_document(message.chat.id, open(r'Практикум Python. Идеи проектов.pdf', 'rb'))