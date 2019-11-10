import json
import random
import re
import time
import requests
import getpass


class InstaBot:
    """
    Instabot.py

    """
    url_following_token = "d04b0a864b4b54837c0d870b0e77e076"
    url_username_token = "7c16654f22c819fb63d1183034a5162f"

    url_following = 'https://www.instagram.com/graphql/query/?query_hash=%s&variables={"id":"%s","first":50,"after":"%s"}'
    url_username = 'https://www.instagram.com/graphql/query?query_hash=%s&variables={"user_id":"%s","include_reel":true}'

    url = "https://www.instagram.com/"
    url_follow = "https://www.instagram.com/web/friendships/%s/follow/"
    url_unfollow = "https://www.instagram.com/web/friendships/%s/unfollow/"
    url_block = "https://www.instagram.com/web/friendships/%s/block/"
    url_unblock = "https://www.instagram.com/web/friendships/%s/unblock/"
    url_login = "https://www.instagram.com/accounts/login/ajax/"
    url_logout = "https://www.instagram.com/accounts/logout/"
    url_user_detail = "https://www.instagram.com/%s/"

    list_ua = [
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; FSL 7.0.6.01001)",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; FSL 7.0.7.01001)",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; FSL 7.0.5.01003)",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0",
        "Mozilla/5.0 (X11; U; Linux x86_64; de; rv:1.9.2.8) Gecko/20100723 Ubuntu/10.04 (lucid) Firefox/3.6.8",
        "Mozilla/5.0 (Windows NT 5.1; rv:13.0) Gecko/20100101 Firefox/13.0.1",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:11.0) Gecko/20100101 Firefox/11.0",
        "Mozilla/5.0 (X11; U; Linux x86_64; de; rv:1.9.2.8) Gecko/20100723 Ubuntu/10.04 (lucid) Firefox/3.6.8",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; .NET CLR 1.0.3705)",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)",
        "Opera/9.80 (Windows NT 5.1; U; en) Presto/2.10.289 Version/12.01",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; SV1; .NET CLR 2.0.50727)",
        "Mozilla/5.0 (Windows NT 5.1; rv:5.0.1) Gecko/20100101 Firefox/5.0.1",
        "Mozilla/5.0 (Windows NT 6.1; rv:5.0) Gecko/20100101 Firefox/5.02",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.112 Safari/535.1",
        "Mozilla/4.0 (compatible; MSIE 6.0; MSIE 5.5; Windows NT 5.0) Opera 7.02 Bork-edition [en]",
    ]

    def __init__(self):
        self.user_agent = random.sample(self.list_ua, 1)[0]
        self.s = requests.Session()
        self.login_status = False

    def login(self):
        func_name = self.login.__name__
        if self.login_status:
            print(func_name, "-->", "Logout first")
            return False
        successfulLogin = False
        self.s.headers.update({
            "Accept":
            "*/*",
            "Accept-Language":
            'en-US,en;q=0.5',
            "Accept-Encoding":
            "gzip, deflate, br",
            "Connection":
            "keep-alive",
            "Host":
            "www.instagram.com",
            "Origin":
            "https://www.instagram.com",
            "Referer":
            "https://www.instagram.com/",
            "User-Agent":
            self.user_agent,
            "X-Instagram-AJAX":
            "1",
            "Content-Type":
            "application/x-www-form-urlencoded",
            "X-Requested-With":
            "XMLHttpRequest",
        })
        try:
            r = self.s.get(self.url)
            if r.status_code != 200:
                print(func_name, "-->", f"{r}",
                      "Get Token Request not return 200 as status code!")
                return False
            csrf_token = re.search('(?<="csrf_token":")\w+', r.text).group(0)
            self.s.headers.update({"X-CSRFToken": csrf_token})
            time.sleep(5 * random.random())
            username = input("Enter your IG username: ")
            username = username.lower()
            login = self.s.post(
                self.url_login,
                data={
                    "username": username,
                    "password": getpass.getpass("Enter your password: "),
                },
                allow_redirects=True)
            if login.status_code not in (200, 400):
                print(func_name, "-->", f"{login}",
                      "Login Request not return 200/400 as status code!")
                return False
            loginResponse = login.json()
            self.csrftoken = login.cookies["csrftoken"]
            self.s.headers.update({"X-CSRFToken": self.csrftoken})
            if loginResponse.get("errors"):
                print(func_name, "-->", 'Login Request error',
                      loginResponse["errors"]["error"])
                return False
            elif loginResponse.get("message") == "checkpoint_required":
                if "instagram.com" in loginResponse["checkpoint_url"]:
                    challenge_url = loginResponse["checkpoint_url"]
                else:
                    challenge_url = f"https://instagram.com{loginResponse['checkpoint_url']}"
                print(f"\nVerify code required")
                with self.s as clg:
                    clg.headers.update({
                        "Accept":
                        "*/*",
                        "Accept-Language":
                        'en-US,en;q=0.5',
                        "Accept-Encoding":
                        "gzip, deflate, br",
                        "Connection":
                        "keep-alive",
                        "Host":
                        "www.instagram.com",
                        "Origin":
                        "https://www.instagram.com",
                        "User-Agent":
                        self.user_agent,
                        "X-Instagram-AJAX":
                        "1",
                        "Content-Type":
                        "application/x-www-form-urlencoded",
                        "x-requested-with":
                        "XMLHttpRequest",
                    })
                    challenge_request_explore = clg.get(challenge_url)
                    if challenge_request_explore.status_code != 200:
                        print(func_name, "-->", f"{challenge_request_explore}",
                              "Verify Request not return 200 as status code!")
                        return False
                    challenge_csrf_token = re.search(
                        '(?<="csrf_token":")\w+',
                        challenge_request_explore.text).group(0)
                    rollout_hash = re.search(
                        '(?<="rollout_hash":")\w+',
                        challenge_request_explore.text).group(0)
                    print("Receive code by phone or email?")
                    print("Type 0 for phone")
                    print("Make sure your phone is linked to IG account")
                    print("Or type 1 for email")
                    challenge_userinput_code = input("Phone[0]/Email[1]: ")
                    accepted = ["1", "0", "phone", "email"]
                    while challenge_userinput_code.lower() not in accepted:
                        print("Invalid. Please type again.")
                        challenge_userinput_code = input("Phone[0]/Email[1]: ")
                    if challenge_userinput_code == "0" or challenge_userinput_code.lower(
                    ) == "phone":
                        challenge_post = {"choice": 0}
                    else:
                        challenge_post = {"choice": 1}
                    clg.headers.update({"X-CSRFToken": challenge_csrf_token})
                    clg.headers.update({"Referer": challenge_url})
                    challenge_request_code = clg.post(
                        challenge_url,
                        data=challenge_post,
                        allow_redirects=True)
                    if challenge_request_code.status_code != 200:
                        print(
                            func_name, "-->", f"{challenge_request_code}",
                            "By Phone/Mail Request not return 200 as status code!"
                        )
                        return False
                    challenge_userinput_code = getpass.getpass(
                        "Enter the code sent to your phone/email: ")
                    if challenge_userinput_code.isdecimal():
                        challenge_userinput_code = int(
                            challenge_userinput_code)
                    complete_challenge = clg.post(
                        challenge_url,
                        data={"security_code": challenge_userinput_code},
                        allow_redirects=True,
                    )
                    del challenge_userinput_code
                    if complete_challenge.status_code != 200:

                        print(
                            func_name, "-->", f"{complete_challenge}",
                            "Complete Request not return 200 as status code!")
                        return False
                    self.csrftoken = complete_challenge.cookies["csrftoken"]
                    self.s.headers.update({
                        "X-CSRFToken": self.csrftoken,
                        "X-Instagram-AJAX": "1"
                    })
                    successfulLogin = True
            elif loginResponse.get("authenticated") is False:
                print(func_name, "-->", 'Login Request error',
                      "Check your login data!")
                return False
            else:
                rollout_hash = re.search('(?<="rollout_hash":")\w+',
                                         r.text).group(0)
                self.s.headers.update({"X-Instagram-AJAX": rollout_hash})
                successfulLogin = True

        except Exception as exc:
            print("Logout fail!")
            print(func_name, "exception -->", exc)
            return False
        self.s.cookies["csrftoken"] = self.csrftoken
        self.s.cookies["ig_vw"] = "1536"
        self.s.cookies["ig_pr"] = "1.25"
        self.s.cookies["ig_vh"] = "772"
        self.s.cookies["ig_or"] = "landscape-primary"
        time.sleep(5 * random.random())

        if successfulLogin:
            r = self.s.get("https://www.instagram.com/")
            self.csrftoken = re.search('(?<="csrf_token":")\w+',
                                       r.text).group(0)
            self.s.cookies["csrftoken"] = self.csrftoken
            self.s.headers.update({"X-CSRFToken": self.csrftoken})
            finder = r.text.find(username)
            if finder != -1:
                self.login_status = True
                self.follow_counter = 0
                self.unfollow_counter = 0
                self.user_login = username
                self.user_id = self.get_user_id_by_username(self.user_login)
                self.following = self.get_following_list()
                print(f"{self.user_login} login success!\n")
                return True
            else:
                self.login_status = False
                print(func_name, "-->", 'Login Request error',
                      "Check your login data!")
                return False
        else:
            print(func_name, "-->", 'Login Request error',
                  "Login error! Connection error!")
            return False

    def follow(self, user_id):
        func_name = self.follow.__name__
        user_id = str(user_id)
        if not self.login_status:
            print(func_name, "-->", "Login first")
            return False
        if user_id in self.following:
            print(func_name, "-->",
                  f"already following {self.get_username_by_user_id(user_id)}")
            return False
        url_follow = self.url_follow % user_id
        try:
            resp = self.s.post(url_follow)
            if resp.status_code != 200:
                print(
                    func_name, "-->", f"{resp}",
                    f"{self.get_username_by_user_id(user_id)} Follow Request not return 200 as status code!"
                )
                return False
        except Exception as exc:
            print(func_name, "exception -->", exc)
            return False
        if resp.status_code == 200:
            self.follow_counter += 1
            self.following.append(user_id)
            return True
        print(func_name, "-->",
              f"cannot follow {self.get_username_by_user_id(user_id)}")
        return False

    def unfollow(self, user_id):
        func_name = self.unfollow.__name__
        user_id = str(user_id)
        if not self.login_status:
            print(func_name, "-->", "Login first")
            return False
        if user_id not in self.following:
            print(func_name, "-->",
                  f"not following {self.get_username_by_user_id(user_id)}")
            return False
        url_unfollow = self.url_unfollow % user_id
        try:
            resp = self.s.post(url_unfollow)
            if resp.status_code != 200:
                print(
                    func_name, "-->", f"{resp}",
                    f"{self.get_username_by_user_id(user_id)} Unfollow Request not return 200 as status code!"
                )
                return False
        except Exception as exc:
            print(func_name, "exception -->", exc)
            return False
        if resp.status_code == 200:
            self.unfollow_counter += 1
            self.following.remove(user_id)
            return True
        print(func_name, "-->",
              f"cannot unfollow {self.get_username_by_user_id(user_id)}")
        return False

    def logout(self):
        func_name = self.logout.__name__
        if not self.login_status:
            print(func_name, "-->", "Login first")
            return False
        try:
            r = self.s.post(
                self.url_logout, data={
                    "csrfmiddlewaretoken": self.csrftoken
                })
            if r.status_code != 200:
                print(func_name, "-->", f"{r}",
                      "Logout Request not return 200 as status code!")
                return False
            print("You followed %i accounts, unfollowed %i accounts." % (
                self.follow_counter,
                self.unfollow_counter,
            ))
            self.s = requests.Session()
            self.follow_counter = 0
            self.unfollow_counter = 0
            self.user_login = None
            self.user_id = None
            self.login_status = False
            self.following = None
            print("Logout success!")
            return True
        except Exception as exc:
            print("Logout fail!")
            print(func_name, "exception -->", exc)
            return False

    def get_following_list(self):
        func_name = self.get_following_list.__name__
        if not self.login_status:
            print(func_name, "-->", "Login first")
            return False
        following = []
        end_cursor = ""
        has_next_page = True
        while has_next_page:
            url_following = self.url_following % (self.url_following_token,
                                                  self.user_id, end_cursor)
            try:
                resp = self.s.get(url_following)
                if resp.status_code != 200:
                    print(func_name, "-->",
                          "Expired query_hash. Please contact developer.")
                    return False
                json_info = json.loads(resp.text)
                if json_info['data']['user'] == None:
                    print(func_name, "-->",
                          f"This account was not found : {self.user_id}")
                    return False
                node_info = json_info['data']['user']['edge_follow']['edges']
                for node in node_info:
                    following.append(node['node']['id'])
                page_info = json_info['data']['user']['edge_follow'][
                    'page_info']
                end_cursor = page_info['end_cursor']
                has_next_page = page_info['has_next_page']
            except Exception as exc:
                print(func_name, "exception -->", exc)
                return False
        return following

    def get_user_info(self, username):
        func_name = self.get_user_info.__name__
        url_user_detail = self.url_user_detail % (username)
        try:
            r = self.s.get(url_user_detail)
            if r.status_code != 200:
                print(func_name, "-->", f"{r}",
                      "User Info Request not return 200 as status code!")
                return False
            if r.text.find(
                    "The link you followed may be broken, or the page may have been removed."
            ) >= 0:
                print(func_name, "-->",
                      f"This account was not found : {username}")
                return False
            raw_data = re.search("window._sharedData = (.*?);</script>",
                                 r.text, re.DOTALL).group(1)
            user_data = json.loads(raw_data)["entry_data"]["ProfilePage"][0][
                "graphql"]["user"]
            user_info = dict(
                user_id=user_data["id"],
                follows=user_data["edge_follow"]["count"],
                followers=user_data["edge_followed_by"]["count"],
                follows_viewer=user_data["follows_viewer"],
                followed_by_viewer=user_data["followed_by_viewer"],
                requested_by_viewer=user_data["requested_by_viewer"],
                has_requested_viewer=user_data["has_requested_viewer"])
            return user_info
        except Exception as exc:
            print(func_name, "exception -->", exc)
            return False

    def get_user_id_by_username(self, username):
        user_info = self.get_user_info(username)
        return user_info['user_id'] if user_info else False

    def get_username_by_user_id(self, user_id):
        func_name = self.get_username_by_user_id.__name__
        user_id = str(user_id)
        try:
            url_username = self.url_username % (self.url_username_token,
                                                user_id)
            resp = self.s.get(url_username)
            if resp.status_code != 200:
                print(func_name, "-->",
                      "Expired query_hash. Please contact developer.")
                return False
            json_info = json.loads(resp.text)
            if json_info['data']['user'] == None:
                print(func_name, "-->",
                      f"This account was not found : {user_id}")
                return False
            username = json_info['data']['user']['reel']['user']['username']
            return username
        except Exception as exc:
            print(func_name, "exception -->", exc)
            return False
