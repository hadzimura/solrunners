

delay = 30
subs = list()

for min in range (0, 15):


    s = str()
    for sec in range(0, 59):

        if sec == 0:

            if sec < 10:
                sec = '0{}'.format(sec)
            print('00:{}:{}:00|00:{}:{}:00|Text'.format(min, sec, min, 59))






# 00:04:30:13|00:04:33:19|Entropy will get you in the end