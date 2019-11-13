import pandas as pd
import io
import requests
import instabot
import random

def main():
    bot = instabot.InstaBot()
    bot.login()
    print(
        "\n----------------------------START----------------------------\n"
    )
    if bot.login_status:

        df = df_from_sheet()
        df.loc[df['id'].isnull(), 'id'] = df.loc[df['id'].isnull(), 'name'].apply(
            bot.get_user_id_by_username)
        df['following'] = df['id'].apply(lambda x: x in bot.following)

        print("You are suggested to only follow or unfollow 10 accounts per day")
        limit = 10
        
        all_follow_list = list(df[(df['following'] == False) & (df['color'] == 'yellow')]['id'])
        all_unfollow_list = list(df[(df['following'] == True) & (df['color'] == 'blue')]['id'])
    
        account_list = dict(map(lambda x: (x, df[df['id'] == x].iloc[0]['name']), list(df['id'])))
        
        follow_list = random.sample(all_follow_list, k = limit if limit < len(all_follow_list) else len(all_follow_list))
        unfollow_list = random.sample(all_unfollow_list, k = limit if limit < len(all_unfollow_list) else len(all_unfollow_list))
        print("\n----------------------------CHECK----------------------------\n")
        
        print("Suggest to follow:\n",
              list(map(lambda x: account_list[x], follow_list)))
        print("Suggest to unfollow:\n",
              list(map(lambda x: account_list[x], unfollow_list)))
        
        shuffle = input("Shuffle to have other suggestion? [yes/no] ")
        while shuffle.lower() != 'no':
            if shuffle.lower() == 'yes':
                follow_list = random.sample(all_follow_list, k = limit if limit < len(all_follow_list) else len(all_follow_list))
                unfollow_list = random.sample(all_unfollow_list, k = limit if limit < len(all_unfollow_list) else len(all_unfollow_list))
                print("\nSuggest to follow:\n",
                      list(map(lambda x: account_list[x], follow_list)))
                print("Suggest to unfollow:\n",
                  list(map(lambda x: account_list[x], unfollow_list)))
            shuffle = input("Shuffle to have other suggestion? [yes/no] ")
        
        checked = input("Ready? [yes/no] ")
        while checked.lower() != 'yes':
            if checked.lower() == 'no':
                print("\n---------------------------RESULTS---------------------------\n")
                bot.logout()
                print("\n-----------------------------END-----------------------------\n")
                return
            checked = input("Ready? [yes/no] ")
            
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

        send_google_form(bot.user_id, followed, unfollowed)

        print("\n---------------------------RESULTS---------------------------\n")
        print("Successfully followed:\n",
              list(map(lambda x: account_list[x], followed)))
        print("Successfully unfollowed:\n",
              list(map(lambda x: account_list[x], unfollowed)))
        print("")
        print("Fail to follow:\n",
              list(map(lambda x: account_list[x], follow_fail)))
        print("Fail to unfollow:\n",
              list(map(lambda x: account_list[x], unfollow_fail)))
        print("")
        bot.logout()
    else:
        print("Login failed.")
    print("\n-----------------------------END-----------------------------\n")


def df_from_sheet():
    sheet = requests.get(
        'https://docs.google.com/spreadsheets/d/1eKCbv2-1_jtRtefeAj9sZKQKsr_EySf8vPdq2NPaIlY/gviz/tq?&tqx=out:csv&sheet={blue}'
    )
    df = pd.read_csv(io.StringIO(sheet.text))
    df['id'] = df['id'].astype(str)
    return df


def send_google_form(userid, follow, unfollow):
    url = 'https://docs.google.com/forms/d/1E-lsmablSZwQ4Jg1B451878zi8v440xpuoIzSS73kUs/formResponse'
    form_data = {
        'entry.495552285': "*"+' '.join(follow),
        'entry.2069182184': "*"+' '.join(unfollow),
        'entry.1668277686': "*"+userid,
        'draftResponse': [],
        'pageHistory': 0
    }
    user_agent = {
        'Referer':
        'https://docs.google.com/forms/d/1E-lsmablSZwQ4Jg1B451878zi8v440xpuoIzSS73kUs/viewform',
        'User-Agent':
        "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.52 Safari/537.36"
    }
    requests.post(url, data=form_data, headers=user_agent)
    return True


if __name__ == '__main__':
    main()
