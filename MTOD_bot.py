import asyncio
import telepot.aio
import telepot.aio.helper
import time
import sys
import bs4
import requests
import datetime
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.aio.delegate import per_chat_id, create_open


def getday(day):
    currentdate = datetime.date.today()
    if day == 'tomorrow':
        day = str(currentdate.day + 1).zfill(2)
    else:
        day = str(currentdate.day).zfill(2)
    month = str(currentdate.month).zfill(2)
    year = str(currentdate.year)
    user_agent = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}
    req = requests.session()
    req.headers.update(user_agent)
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    postData = 'postId=606&month=' + month + '&action=get_program_guide'
    response = req.post('https://www.motortrendondemand.com/wp-admin/admin-ajax.php', headers=headers, data=postData).content
    soup = bs4.BeautifulSoup(response, 'html.parser').findAll('ul', {'data-date': year + '-' + month + '-' + day})
    output = []
    output.append('MTOD Schedule for: ' + year + '-' + month + '-' + day + '\n')
    for item in soup:
        listing = item.find('span', {'class': 'video-title'}).text + ' - ' + item.find('span', {'class': 'video-venue'}).text
        output.append(listing.replace(u'\u2018', '\'').replace(u'\u2019', '\'').replace(u'\u2013', '-').replace(u'\u201c', '\"').replace(u'\u201d', '\"'))
    return '\n'.join(output)

class MTOD(telepot.aio.helper.ChatHandler):
    def __init__(self, seed_tuple, timeout):
        super(MTOD, self).__init__(seed_tuple, timeout)
        self._editor = None
        self._keyboard = InlineKeyboardMarkup(inline_keyboard=[[
                             InlineKeyboardButton(text='Today', callback_data='today'),
                             InlineKeyboardButton(text='Tomorrow', callback_data='tomorrow')
                         ]])

    async def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        sent = await self.sender.sendMessage('What day would you like to see?', reply_markup=self._keyboard)
        self._editor = telepot.helper.Editor(self.bot, sent)

    async def on_callback_query(self, msg):
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')

        if query_data == 'today':
            await self._editor.editMessageReplyMarkup(reply_markup=None)
            sent = await self.sender.sendMessage(getday('today'), reply_markup=self._keyboard)
            self._editor = telepot.aio.helper.Editor(self.bot, sent)

        elif query_data == 'tomorrow':
            await self._editor.editMessageReplyMarkup(reply_markup=None)
            sent = await self.sender.sendMessage(getday('tomorrow'), reply_markup=self._keyboard)
            self._editor = telepot.aio.helper.Editor(self.bot, sent)


TOKEN = sys.argv[1]
bot = telepot.aio.DelegatorBot(TOKEN, [(per_chat_id(types=['private']), create_open(MTOD, timeout=65536))])
loop = asyncio.get_event_loop()
loop.create_task(bot.message_loop())
loop.run_forever()
