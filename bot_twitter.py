#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TODO:
# tweet trucs liste récurrente
# follow tous gens retweetés par ma liste récurrente
# tweet certains hashtags
# follow tous gens sur certains hashtags
# follow tous les gens qui favent, retweetent, ajoutent à des listes, mentionnent, bref toutes les activités
# faire une pile
# système de throttler et de tweets en attente
# retweet "hard" from list "medias indés" + zinc + système pour exploiter les trending topics (zinc ?)
# + faire un bot zinc
# like random s*** from wanted public
# https://twitter.com/Dalb75/lists/listecommuns/members
    # retweet waiting list
    # daemon
    # throttler

import tweepy, time, sys, random
from datetime import datetime

#__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

# enter the corresponding information from your Twitter application:
# Borré las mías jiji

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)
list = list()

def build(): # Copia los followers de un user dado y lo escribe en un archivo
    print 'Building follow list'
#    members = api.list_members(owner_screen_name='Dalb75', slug='listecommuns')
    members = api.followers_ids(screen_name='Ulyss')
#    liste = []
    liste = members
#    for i in members:
#        print i.id
#        liste.append(i.id)
    filename=open(sys.path[0]+'/users_to_follow','a+')
    for id in liste:
      filename.write("%s\n" % id)

def yesno(spaghetti): // No sé programar y escribo funciones super raras
    if spaghetti==True:
        print('Yes')
    else: print('No')

def check(user): # Check si un user llena ciertas condiciones para poner un filtro a una lista de users
    if hasattr(user, 'status'):
        ts = time.mktime(user.status.created_at.timetuple())
        recently_updated = (time.time() - ts < 3600*24*60)
    else: recently_updated = False

    print "Already following? "+str(user.following)
    print "Request already sent? "+str(user.follow_request_sent)
    print "User protected? "+ str(user.protected)
    print "Cool ratio? "+str(user.followers_count < user.friends_count)
    print "Speaks French? "+str('fr' in user.lang)
    print "Did they post in 60 days? "+ str(recently_updated)
    if not user.following and not user.follow_request_sent and not user.protected and (user.followers_count < 3 * user.friends_count) and 'fr' in user.lang and recently_updated:
        return True
    else:
        return False

def bulk_follow(): # seguir users leidos de un archivo
    filename=open(sys.path[0]+'/users_to_follow','r+')
    f=filename.readlines()
    i = 0

    for id in f:
        if i > 150:
            filename.truncate(0)
            filename.close()
            exit()
        else:
            user = api.get_user(id=id)
            print "Trying to follow @%s..." % user.screen_name


            if check(user):
                print "Following %s..." % user.name
                api.create_friendship(user_id=user.id)
                print "Followed ID %s" % id
                i = i+1
                if hasattr(user, 'status'): # Poner "like" a su ultimo status para
                    if user.status.text[:1] != '@' and not user.status.favorited:
                        print "Faving their last status..."
                        api.create_favorite(id=user.status.id)
                    else:
                        print 'Too creepy to "fave", too lazy to make more requests...'

                rand = random.randint(5, 10)
                print "Waiting %d seconds…" % rand
                time.sleep(rand)
            print '\n'



def add_to_list(tweets): # añade tweets a una lista si responde a filtros
    for tweet in tweets:
        if tweet.retweet_count >= 100 and not tweet.retweeted and 'fr' in tweet.lang:
            list.append(tweet)

def post_tweets(tweets): # pregunta si postea retweets de una lista de tweets
    for tweet in tweets:
        if not tweet.retweeted:
            if hasattr(tweet, 'retweeted_status'):
                print 'Retweet "%s" by %s via %s?' % (tweet.retweeted_status.text, tweet.retweeted_status.user.screen_name, tweet.user.screen_name) # Test
                tweet = tweet.retweeted_status
            else:
                print 'Retweet "%s" by %s?' % (tweet.text, tweet.user.screen_name) # Test

            if query_yes_no():
                api.retweet(tweet.id)
                time.sleep(10)
def followback(pages=0): # follow back los ultimos followers, o followea n paginas de followers (la paginación no funciona bien)

    if(pages==0):
        cursor=pages
    else:
        cursor = -1

    for page in [0,pages]:
        [followers, cursors] = api.followers(cursor=cursor)
        for user in followers:
            if not user.following and not user.follow_request_sent:
                print "Following ID %s..." % user.name
                api.create_friendship(user_id=user.id)
                print "Followed ID %s!" % user.name
        cursor= cursors[1]

def prune(): # eliminar followers de una lista
#    for id in friends_ids():
#        if not user.following :
#        print "Following %s..." % user.name
#        api.create_friendship(user_id=user.id)
#        print "Followed %s!" % user.name
    return Null

def post(): # recupera lista de tweets de un user
    add_to_list(api.user_timeline(screen_name='hadrienlepicier'))

    if not list:
        add_to_list(api.home_timeline())
        add_to_list(api.home_timeline(page=2))
        add_to_list(api.home_timeline(page=3))
    post_tweets(list)

def query_yes_no(): # recupera el input del user (función fea)
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}

    while True:
        choice = raw_input().lower()
        if choice == '':
            return True
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Enfoiré.\n")


# main: parte principal del programa

followback()  #followemos los nuevos followers

if len(sys.argv) > 1: #verificamos qué dice el user del bot
    arg = sys.argv[1]
    if arg == "bulk": # seguir en masa
        bulk_follow()
    elif arg == "build": #construir lista
        build()
    elif arg == "prune": #borrar cosas en una lista
        prune()
    elif arg == "post": #retweetear unos tweets
        post()
    elif arg.isdigit(): #followback cuantas paginas de followers (si mucho tiempo pasó)
        followback(arg)


#print 'Waiting 10min...'
#time.sleep(10*60)
