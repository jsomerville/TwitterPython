import tweetpony
import threading
from threading import Timer
# This is the TweetPony object to use with your Twitter credentials
api = tweetpony.API(consumer_key = "<your key>", consumer_secret = "<your secret>", access_token = "<your oauth token>", access_token_secret = "<your oauth token secret")
user = api.user
print "Hello, @%s!" % user.screen_name
 
### Set the user ids for whom you want to find followers
userIds = [1234, 2345, etc.]
# The file name. Function will keep appending to this file with each run of script. If re-run with same userids above could wind up with repeated values. Can rename as often as like.
fileName = 'FollowersIds'
 
# This function gets called recursively to get all the followers of the ids above and put them in a csv in C:\Temp
# Handles multiple cursors of followers for an individual user
# Throttles requests to Twitter API to pause after 15 requests, wait until Twitter's limit window has passed (15 minutes), then continue
def getFollowersIds(userIdIndex, nextCursor, requestNum, f):
    currentUserId = userIds[userIdIndex]
    followersIds = None
    userAuthorized = True
    try:
        if nextCursor > 0:
            followersIds = api.followers_ids(user_id = currentUserId, cursor = nextCursor)
        else:
            followersIds = api.followers_ids(user_id = currentUserId)
        if f.closed:
            f = open(f.name, f.mode)
        for followerId in followersIds.ids:
            f.write('\n' + str(currentUserId) + ',' + str(followerId))
    except tweetpony.APIError as err:
        errMess = "Error in call to Twitter: "
        if err.description == 'Unauthorized':
            errMess = errMess + "unauthorized to access user: "
            userAuthorized = False
        print errMess + str(currentUserId) + " - at current cursor: " + str(nextCursor) + "; Twitter returned error #%i and said: %s" % (err.code, err.description)
    except:
        print "Error writing to file for: " + str(currentUserId) + " - at current cursor: " + str(nextCursorstr)
    
    if userAuthorized and hasattr(followersIds, 'next_cursor')  and followersIds.next_cursor > 0:
        nextCursor = followersIds.next_cursor
    elif userIdIndex < len(userIds) - 1:
        nextCursor = 0
        userIdIndex = userIdIndex + 1
    else:
        print "done"
        return
 
    if requestNum < 15:
        requestNum = requestNum + 1
        getFollowersIds(userIdIndex, nextCursor, requestNum, f)
    else:
        t = Timer(960, getFollowersIds, [userIdIndex, nextCursor, 1, f])
        t.start()
 
with open('C:\\Temp\\' + fileName + '.csv', 'a') as f:
    f.write("Parent Id,Follower ID")
    getFollowersIds(0, 0, 1, f)