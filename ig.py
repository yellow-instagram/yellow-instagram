'''
Instruction:
1. Sign in your gmail account
2. Click "Open in playground"
3. Press Play button (ctrl + enter) and then click RUN ANYWAY
'''

def main():
  delete_files()
  import instabot_py
  import getpass

  instabot_py.InstaBot.login = login
  instabot_py.InstaBot.follow = follow
  instabot_py.InstaBot.unfollow = unfollow
  instabot_py.InstaBot.logout = logout
  instabot_py.InstaBot.__init__ = __init__
  username = input("Enter your IG username: ")
  password = getpass.getpass("Enter your password: ")
  bot = instabot_py.InstaBot(login=username, password=password)
  print("\n\n--------------------------START----------------------------\n\n")
  if bot.login_status:
    
    df = df_from_sheet(bot)
    df = df[df['following'] == True]
    follow_list = []
    unfollow_list = []
    s=0
    limit = 15
    #follow_list = list(df['id'])[s:limit+s]
    #unfollow_list = list(df['id'])[s:limit+s]
    
    print("Ready to follow: ", list(map(bot.get_username_by_user_id,follow_list)))
    print("Ready to unfollow: ", list(map(bot.get_username_by_user_id,unfollow_list)))

    followed = []
    follow_fail = []
    unfollowed = []
    unfollow_fail = []
    for user in follow_list:
      response = bot.follow(user)
      if response:
        followed.append(user)
      else:
        follow_fail.append(user)
    for user in unfollow_list:
      response = bot.unfollow(user)
      if response:
        unfollowed.append(user)
      else:
        unfollow_fail.append(user)

    send_google_form(username, followed, unfollowed)

    print("Successfully followed: ", list(map(bot.get_username_by_user_id,followed)))
    print("Successfully unfollowed: ", list(map(bot.get_username_by_user_id,unfollowed)))

    print("Fail to follow: ", list(map(bot.get_username_by_user_id,follow_fail)))
    print("Fail to unfollow: ", list(map(bot.get_username_by_user_id,unfollow_fail)))
  else:
    print("\nLogin failed.")
  bot.logout()
  delete_files()
  print("\n\n--------------------------END----------------------------\n\n")

def df_from_sheet(bot):
  import pandas as pd
  import io
  import requests
  sheet = requests.get('https://docs.google.com/spreadsheets/d/1eKCbv2-1_jtRtefeAj9sZKQKsr_EySf8vPdq2NPaIlY/gviz/tq?&tqx=out:csv&sheet={blue}')
  df = pd.read_csv(io.StringIO(sheet.text))
  df.loc[df['id'].isnull(), 'id'] = df.loc[df['id'].isnull(), 'name'].apply(get_user_id)
  df['id'] = df['id'].astype(str)
  #df['following'] = df['name'].apply(lambda x: get_is_following(bot, x))
  df['following'] = True
  return df

def get_user_id(username):
  import json
  import requests
  response = requests.get('https://www.instagram.com/'+username+'/?__a=1')
  if response.status_code == 404:
    return "N/A"
  json_data = json.loads(response.text)
  return json_data['graphql']['user']['id']

def send_google_form(username, follow, unfollow):
  import requests
  url = 'https://docs.google.com/forms/d/1E-lsmablSZwQ4Jg1B451878zi8v440xpuoIzSS73kUs/formResponse'
  form_data = {'entry.495552285':','.join(follow),
              'entry.2069182184':','.join(unfollow),
              'entry.1668277686':username,
              'draftResponse':[],
              'pageHistory':0}
  user_agent = {'Referer':'https://docs.google.com/forms/d/1E-lsmablSZwQ4Jg1B451878zi8v440xpuoIzSS73kUs/viewform','User-Agent': "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.52 Safari/537.36"}
  requests.post(url, data=form_data, headers=user_agent)
  print("Form sent")

def delete_files():
  import os
  for file in os.listdir(os.getcwd()):
    if file == "ig.py":
        continue;
    elif os.path.isfile(file):
      os.remove(file)
  print("Local files deleted")

def get_is_following(bot, username):
  import re
  import json
  url_tag = bot.url_user_detail % (username)
  try:
    r = bot.s.get(url_tag)
    if r.text.find("The link you followed may be broken, or the page may have been removed.") >= 0:
      print(username, " cannot be found.")
      return True
    raw_data = re.search("window._sharedData = (.*?);</script>", r.text, re.DOTALL).group(1)
    user_data = json.loads(raw_data)["entry_data"]["ProfilePage"][0]["graphql"]["user"]
    return user_data["followed_by_viewer"] or user_data["requested_by_viewer"]
  except Exception as exc:
    print(exc)
    return True
    
def login(self):
  import re
  import pickle
  import time
  import os
  import random

  successfulLogin = False

  self.s.headers.update(
      {
          "Accept": "*/*",
          "Accept-Language": 'en-US,en;q=0.5',
          "Accept-Encoding": "gzip, deflate, br",
          "Connection": "keep-alive",
          "Host": "www.instagram.com",
          "Origin": "https://www.instagram.com",
          "Referer": "https://www.instagram.com/",
          "User-Agent": self.user_agent,
          "X-Instagram-AJAX": "1",
          "Content-Type": "application/x-www-form-urlencoded",
          "X-Requested-With": "XMLHttpRequest",
      }
  )

  if self.session_file and os.path.isfile(self.session_file):
      self.logger.info(f"Found session file {self.session_file}")
      successfulLogin = True
      with open(self.session_file, "rb") as i:
          cookies = pickle.load(i)
          self.s.cookies.update(cookies)
  else:
      self.logger.info("Trying to login as {}...".format(self.user_login))
      self.login_post = {
          "username": self.user_login,
          "password": self.user_password,
      }
      r = self.s.get(self.url)
      csrf_token = re.search('(?<="csrf_token":")\w+', r.text).group(0)
      self.s.headers.update({"X-CSRFToken": csrf_token})
      time.sleep(5 * random.random())
      login = self.s.post(
          self.url_login, data=self.login_post, allow_redirects=True
      )
      if login.status_code not in (200, 400):
          # Handling Other Status Codes and making debug easier!!
          self.logger.debug("Login Request didn't return 200 as status code!")
          self.logger.debug(
              "Here is more info for debugging or creating an issue"
              "==============="
              "Response Status:{login.status_code}"
              "==============="
              "Response Content:{login.text}"
              "==============="
              "Response Header:{login.headers}"
              "==============="
          )
          return
      else:
          self.logger.debug("Login request succeeded ")

      loginResponse = login.json()
      try:
          self.csrftoken = login.cookies["csrftoken"]
          self.s.headers.update({"X-CSRFToken": self.csrftoken})
      except Exception as exc:
          self.logger.warning("Something wrong with login")
          self.logger.debug(login.text)
          self.logger.exception(exc)
      if loginResponse.get("errors"):
          self.logger.error(
              "Something is wrong with Instagram! Please try again later..."
          )
          self.logger.error(loginResponse["errors"]["error"])

      elif loginResponse.get("message") == "checkpoint_required":
          try:
              if "instagram.com" in loginResponse["checkpoint_url"]:
                  challenge_url = loginResponse["checkpoint_url"]
              else:
                  challenge_url = f"https://instagram.com{loginResponse['checkpoint_url']}"
              self.logger.info(f"Challenge required at {challenge_url}")
              with self.s as clg:
                  clg.headers.update(
                      {
                          "Accept": "*/*",
                          "Accept-Language": 'en-US,en;q=0.5',
                          "Accept-Encoding": "gzip, deflate, br",
                          "Connection": "keep-alive",
                          "Host": "www.instagram.com",
                          "Origin": "https://www.instagram.com",
                          "User-Agent": self.user_agent,
                          "X-Instagram-AJAX": "1",
                          "Content-Type": "application/x-www-form-urlencoded",
                          "x-requested-with": "XMLHttpRequest",
                      }
                  )
                  # Get challenge page
                  challenge_request_explore = clg.get(challenge_url)

                  # Get CSRF Token from challenge page
                  challenge_csrf_token = re.search(
                      '(?<="csrf_token":")\w+', challenge_request_explore.text
                  ).group(0)
                  # Get Rollout Hash from challenge page
                  rollout_hash = re.search(
                      '(?<="rollout_hash":")\w+', challenge_request_explore.text
                  ).group(0)

                  # Ask for option 1 from challenge, which is usually Email or Phone
                  challenge_post = {"choice": 1}

                  # Update headers for challenge submit page
                  clg.headers.update({"X-CSRFToken": challenge_csrf_token})
                  clg.headers.update({"Referer": challenge_url})

                  # Request instagram to send a code
                  challenge_request_code = clg.post(
                      challenge_url, data=challenge_post, allow_redirects=True
                  )

                  # User should receive a code soon, ask for it
                  challenge_userinput_code = input(
                      "Challenge Required.\n\nEnter the code sent to your mail/phone: "
                  )
                  challenge_security_post = {
                      "security_code": int(challenge_userinput_code)
                  }

                  complete_challenge = clg.post(
                      challenge_url,
                      data=challenge_security_post,
                      allow_redirects=True,
                  )
                  if complete_challenge.status_code != 200:
                      self.logger.info("Entered code is wrong, Try again later!")
                      return
                  self.csrftoken = complete_challenge.cookies["csrftoken"]
                  self.s.headers.update(
                      {"X-CSRFToken": self.csrftoken, "X-Instagram-AJAX": "1"}
                  )
                  successfulLogin = complete_challenge.status_code == 200

          except Exception as err:
              self.logger.debug(f"Login failed, response: \n\n{login.text} {err}")
              return False
      elif loginResponse.get("authenticated") is False:
          self.logger.error("Login error! Check your login data!")
          return

      else:
          rollout_hash = re.search('(?<="rollout_hash":")\w+', r.text).group(0)
          self.s.headers.update({"X-Instagram-AJAX": rollout_hash})
          successfulLogin = True
      # ig_vw=1536; ig_pr=1.25; ig_vh=772;  ig_or=landscape-primary;
      self.s.cookies["csrftoken"] = self.csrftoken
      self.s.cookies["ig_vw"] = "1536"
      self.s.cookies["ig_pr"] = "1.25"
      self.s.cookies["ig_vh"] = "772"
      self.s.cookies["ig_or"] = "landscape-primary"
      time.sleep(5 * random.random())

  if successfulLogin:
      r = self.s.get("https://www.instagram.com/")
      self.csrftoken = re.search('(?<="csrf_token":")\w+', r.text).group(0)
      self.s.cookies["csrftoken"] = self.csrftoken
      self.s.headers.update({"X-CSRFToken": self.csrftoken})
      finder = r.text.find(self.user_login)
      if finder != -1:
          self.login_status = True
          self.logger.info(f"{self.user_login} login success!\n")
          if self.session_file is not None:
              self.logger.info(
                  f"Saving cookies to session file {self.session_file}"
              )
              with open(self.session_file, "wb") as output:
                  pickle.dump(self.s.cookies, output, pickle.HIGHEST_PROTOCOL)
      else:
          self.login_status = False
          self.logger.error("Login error! Check your login data!")
          if self.session_file and os.path.isfile(self.session_file):
              try:
                  os.remove(self.session_file)
              except:
                  self.logger.info(
                      "Could not delete session file. Please delete manually"
                  )

          self.prog_run = False
  else:
      self.logger.error("Login error! Connection error!")

def follow(self, user_id):
  url_follow = self.url_follow % user_id
  username = self.get_username_by_user_id(user_id=user_id)
  try:
    resp = self.s.post(url_follow)
  except Exception as exc:
    print(exc)
    return False
  if resp.status_code == 200:
    self.follow_counter += 1
    return True
  return False

def unfollow(self, user_id):
  url_unfollow = self.url_unfollow % user_id
  username = self.get_username_by_user_id(user_id=user_id)
  try:
      resp = self.s.post(url_unfollow)
  except Exception as exc:
    print(exc)
    return False
  if resp.status_code == 200:
    self.unfollow_counter += 1
    return True
  return False
  
def logout(self):
  print("Logout: Followed - %i, Unfollowed - %i."
          % (
              self.follow_counter,
              self.unfollow_counter,
             ))
  try:
    _ = self.s.post(self.url_logout, data={"csrfmiddlewaretoken": self.csrftoken})
    print("Logout success!")
    self.login_status = False
  except Exception as exc:
    print(exc)
    
def __init__(self, config=None, **kwargs):
    import logging
    import random
    import requests
    from config42 import ConfigManager
    from instabot_py.default_config import DEFAULT_CONFIG
    self.logger = logging.getLogger(self.__class__.__name__)
    self.config = ConfigManager(defaults=DEFAULT_CONFIG)
    self.config.set_many(kwargs)
    login = self.config.get("login")
    password = self.config.get("password")
    self.session_file = self.config.get("session_file")
    self.user_agent = random.sample(self.config.get("list_of_ua"), 1)[0]
    self.s = requests.Session()
    self.c = requests.Session()
    self.follow_counter = 0
    self.unfollow_counter = 0
    self.user_login = login.lower()
    self.user_password = password
    self.login_status = False
    self.login()

if __name__ == '__main__':
  main()