import main
import instabot
import pandas as pd


def test_function(*args, func, oracle):
    print("----------------------Start----------------------")
    print("Function :", func.__name__)
    output = func(*args)
    if type(output) is list:
        output = output[0]
    elif type(output) is pd.DataFrame:
        output = list(output['name'])[0]
    print("Expected :", oracle, "Actual :", output)
    print("Result :", output == oracle)
    print("----------------------End-----------------------")


login_bot = instabot.InstaBot()
while not login_bot.login_status:
    login_bot.login()

guest_bot = instabot.InstaBot()

test_function(
    "thestandnews",
    func=guest_bot.get_user_id_by_username,
    oracle="1612218393")
test_function("fuck", func=guest_bot.get_user_id_by_username, oracle=False)

test_function(
    "1307047306", func=guest_bot.get_username_by_user_id, oracle='tat.gor')
test_function("fuck", func=guest_bot.get_username_by_user_id, oracle=False)

test_function(func=guest_bot.get_following_list, oracle=False)
user_id = login_bot.user_id
login_bot.user_id = '1612218393'
test_function(func=login_bot.get_following_list, oracle='11474650262')
login_bot.user_id = user_id

test_function(func=login_bot.logout, oracle=True)
test_function(func=guest_bot.logout, oracle=False)

test_function(func=login_bot.login, oracle=True)

test_function('22190572821', func=guest_bot.follow, oracle=False)
test_function('22734289222', func=login_bot.follow, oracle=True)

test_function('22190572821', func=guest_bot.unfollow, oracle=False)
test_function('22734289222', func=login_bot.unfollow, oracle=True)

test_function(guest_bot, func=main.df_from_sheet, oracle='silentmajority.hk')

test_function("test", "test", "test", func=main.send_google_form, oracle=True)
