import re
import html
import traceback
import sys

import modules.auto_requests as auto_requests


class Titles:

    TITLE_REGEX = re.compile(
        r'<title[^>]*>(.*?)</title>', re.IGNORECASE | re.DOTALL)
    WHITESPACE_REGEX = re.compile(r'\s+')
    URL_REGEX = re.compile('[^\s]*\.[a-zA-Z][^\s]*')

    MAX_CONTENT_LENGTH = 64 * 1024
    USER_AGENT = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/43.0.2357.37 Safari/537.36")

    def __init__(self, bot):
        self.bot = bot
        self.bot.add_privmsg_listener(self.privmsg_callback)

    def privmsg_callback(self, sender, channel, message):
        if channel != '':
            sender = channel
        try:
            for mgroups in self.URL_REGEX.findall(message)[:2]:
                print("URL: " + mgroups)
                # title = find_title(mgroups)
                if(not mgroups.startswith("http")):
                    mgroups = "http://" + mgroups
                title = self.get_title_from_url(mgroups)
                self.bot.queue_message(sender, title)
        except Exception:
            print("Exception in user code:")
            print("-"*60)
            traceback.print_exc(file=sys.stdout)
            print("-"*60)

    @staticmethod
    def get_title_from_url(url):
        # Fetch page (no need to verfiy SSL certs for titles)
        response = auto_requests.get(url, verify=False, headers={"User-Agent": Titles.USER_AGENT, "Accept-Language": "en_US"})
        content = response.text[:Titles.MAX_CONTENT_LENGTH]

        # Avoid leaving dangling redirects when we've got the content
        response.connection.close()

        return Titles.find_title_in_content(content).strip()

    @staticmethod
    def find_title_in_content(text):
        try:
            title = Titles.WHITESPACE_REGEX.sub(" ", Titles.TITLE_REGEX.search(text).group(1))
            title = html.unescape(title).replace('\n', '  ')
            return Titles.unescape_entities(title)
        except:
            return None

    @staticmethod
    def unescape_entities(text):
        def replace_entity(match):
            try:
                if match.group(1) in html.entities.name2codepoint:
                    return chr(html.entities.name2codepoint[match.group(1)])
                elif match.group(1).lower().startswith("#x"):
                    return chr(int(match.group(1)[2:], 16))
                elif match.group(1).startswith("#"):
                    return chr(int(match.group(1)[1:]))
            except (ValueError, KeyError):
                pass  # Fall through to default return
            return match.group(0)

        return re.sub(r'&([#a-zA-Z0-9]+);', replace_entity, text)
