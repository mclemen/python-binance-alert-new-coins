import urllib.request, json
from collections import defaultdict
from datetime import datetime, time
import time
import sys
import threading
import smtplib

# b_coins = urllib.request.urlopen("https://api1.binance.com/api/v3/ticker/price").read()
b_coins = urllib.request.urlopen("https://www.binance.com/bapi/composite/v1/public/marketing/symbol/list").read()
#b_coins = "binancecoins.json"

def get_binance_coins():
    # with open(b_coins, 'r') as data:
    # 	datacoins = json.loads(data.read())
    data = json.loads(b_coins)
    datalist = data["data"]
    return datalist

def generate_new_list(all_coins):
    coinDict = defaultdict(bool)
    for old_coins in all_coins:
        coinDict[old_coins['symbol']] = True
    return coinDict

def get_new_coins(coinDict, all_coins_recheck):
    result = []

    for new_coin in all_coins_recheck:
        if not coinDict[new_coin['symbol']]:
            result += [new_coin]
            # this line ensures the new coin isn't detected again
            coinDict[new_coin['symbol']] = True

    return result

def add_updated_all_coins_to_queue(queue):
    """
    This method makes a request to get all coins and adds it to the given queue.
    """
    all_coins_updated = get_binance_coins()
    queue += [all_coins_updated]

def make_threads_to_request_all_coins(queue, interval=0.1, max_amount_of_threads=20, max_queue_length=20):
    while True:
        time.sleep(interval)
        # checks if the amount of threads is bigger than max_amount_of_threads
        if len(threading.enumerate()) > max_amount_of_threads:
            print("Too many threads, waiting 1 second to attempt to create a new thread.")
            time.sleep(1)
        # checks if the queue isn't getting too big
        elif len(queue) > max_queue_length:
            print("Queue length too big, waiting 1 second to attempt to create a new thread.")
            time.sleep(1)
        else:
            threading.Thread(target=add_updated_all_coins_to_queue, args=(queue,)).start()

def main():
    all_coins = get_binance_coins()
    coin_seen_dict = generate_new_list(all_coins)
    queue_of_updated_all_coins = []
    # this list will work as a queue, if a new updated all_coins is received it will be added to this queue
    queue_of_updated_all_coins = []
    # start a thread to run the make_threads_to_request_all_coins method
    threading.Thread(target=make_threads_to_request_all_coins, args=(queue_of_updated_all_coins,)).start()
    # this is just used to calculate the amount of time between getting updated all_coins
    t0 = time.time()
    
    while True:
        try: 
            # check if a new all_coins_updated is on the queue
            if len(queue_of_updated_all_coins) > 0:
                # get the first updated coins from the queue
                all_coins_updated = queue_of_updated_all_coins.pop(0)
                # check if new coins are listed
                new_coins = get_new_coins(coin_seen_dict, all_coins_updated)

                print("time to get updated list of coins: ", time.time() - t0)
                print("current amount of threads: ", len(threading.enumerate()))
                print("current queue length: ", len(queue_of_updated_all_coins))

                t0 = time.time()
                
            else:
                # if no new all_coins_updated is on the queue, new_coins should be empty
                new_coins = []
                
            if len(new_coins) > 0:

                print(f'New coins detected: {new_coins}')
                gmail_user = 'gmail_user'
                gmail_password = 'gmail_pass'

                sent_from = gmail_user
                to = ['email_address', 'email_address', 'email_address']
                subject = 'Binance New Coins'
                body = f'New coins detected: {new_coins}'

                email_text = """\
                From: %s
                To: %s
                Subject: %s

                %s
                """ % (sent_from, ", ".join(to), subject, body)

                try:
                    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                    server.ehlo()
                    server.login(gmail_user, gmail_password)
                    server.sendmail(sent_from, to, email_text)
                    server.close()
                except:
                    print ('Something went wrong...')
                
                
            else:
                pass
                # print("Duplicate Coins")

        except Exception as e:
            print(e)


if __name__ == '__main__':
    print('working...')
    print(main())
    
