import schedule
import time
import crawl

def job():
    print("Main")
    crawl.main()

schedule.every(15).minutes.do(job)
# schedule.every().hour.do(job)
# schedule.every().day.at("10:30").do(job)
# schedule.every().monday.do(job)
# schedule.every().wednesday.at("13:15").do(job)
# schedule.every().day.at("12:42", "Europe/Amsterdam").do(job)
# schedule.every().minute.at(":17").do(job)

# while True:
#     schedule.run_pending()
#     time.sleep(10)

while True:
    try:
        # job()
        schedule.run_pending()
    except Exception as e:
        print('ERROR!', e)