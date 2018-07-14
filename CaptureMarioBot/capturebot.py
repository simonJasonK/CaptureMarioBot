# 10/16/2017, Jason Simon
# capturebot.py
'''
    A Twitter bot that applies a Mario* mustache and hat to all faces in photos
    Tweeted to @CaptureMario (references to handle scrubbed here).
    
    This bot was created by Jason Simon (@simonjasonk) in October 2017 to
    celebrate the release of the "SUPER MARIO ODYSSEY" game on Nintendo Switch.
    
    More at www.jajse.com
'''

import random
from io import BytesIO
import face_recognition
import requests
import tweepy
from PIL import Image
from PIL import ImageFile

from secrets import *

ImageFile.LOAD_TRUNCATED_IMAGES = True

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)

auth.set_access_token(access_token, access_secret)

api = tweepy.API(auth)

def tweetImage(url, username, status_id):
    
    filename = 'goomba.jpg'
    request = requests.get(url, stream=True)
    if request.status_code == 200:
        i = Image.open(BytesIO(request.content))
        i.save(filename)
        msg = captureImage(filename)
        # upload the processed image if we find >= 1 face(s)
        if msg == "":
            api.update_with_media('captured_goomba.jpg', status='.@{0} #SuperMarioOdyssey #NintendoSwitch'.format(username), in_reply_to_status_id=status_id)
        # for images where the bot fails
        else:
            api.update_with_media('game_over.jpg', status='@{0} No faces detected; for best results, use clear, full human faces! #SuperMarioOdyssey #NintendoSwitch'.format(username), in_reply_to_status_id=status_id)
    else:
        print("unable to download image")
    i.close() # close only once we're completely done with Image

# detect all the faces (and their features) in an image, and capture them all;
# save the result as an image that will be uploaded in with the bot's Tweet
def captureImage(filename):
    selfie = Image.open(filename)
    imageMap = face_recognition.load_image_file(filename)
    faceLocs = face_recognition.face_locations(imageMap)
    if len(faceLocs) == 0:
        return "Err"
    facesLandmarks = face_recognition.face_landmarks(imageMap)
    for idx, loc in enumerate(faceLocs):
        captureFace(selfie, imageMap, loc, facesLandmarks[idx])
    addLogo(selfie)
    selfie.save('captured_goomba.jpg')
    return ""

# Watermark for to increase viral potential
def addLogo(image):
    mark = Image.open("watermark.png")
    width, height = image.size
    mwidth, mheight = mark.size
    mnew_width = int(0.4 * width)
    mnew_height = int(mheight * float(mnew_width) / mwidth)
    mark = mark.resize((int(mnew_width), int(mnew_height)), Image.ANTIALIAS)
    mark_position = (int(0.025 * width), int(0.975 * height - mnew_height))
    image.paste(mark, mark_position, mask=mark)
    mark.close()

# Complete the "capture" process, emulating the game's new mechanic
def captureFace(image, im_map, loc, landmarks):
    addStache(image, im_map, loc, landmarks)
    addHat(image, im_map, loc, landmarks)

# Add mustache
def addStache(image, im_map, loc, landmarks):
    hige = Image.open("stache.png")
    width, height = hige.size
    right, left = loc[1], loc[3]
    new_width = int(0.50 * (right - left))
    new_height = int(float(height) * (float(new_width) / width))
    hige = hige.resize((int(new_width), int(new_height)), Image.ANTIALIAS)
    top_lip_coordinates = landmarks["top_lip"]
    top_lip_left, top_lip_upper = min(list(map(lambda x: x[0], top_lip_coordinates))), max(list(map(lambda x: x[1], top_lip_coordinates)))
    nose_tip_coordinates = landmarks["nose_tip"]
    bottom_nose_tip = (max(list(map(lambda x: x[0], nose_tip_coordinates)))+min(list(map(lambda x: x[0], nose_tip_coordinates))))/2.0,min(list(map(lambda x: x[1], nose_tip_coordinates)))
    hige_offset = int(new_width / 2.0), int(0.75 * new_height)
    hige_position = int(bottom_nose_tip[0] - hige_offset[0]), int((bottom_nose_tip[1] + top_lip_upper)/2.0) - hige_offset[1]
    image.paste(hige, hige_position, mask=hige)
    hige.close()

# Add Mario hat
def addHat(image, im_map, loc, landmarks):
    cappy = Image.open("cappy.png")
    width, height = cappy.size
    top, right, left = loc[0], loc[1], loc[3]
    new_width = int(1.25 * (right - left))
    new_height = int(float(height) * (float(new_width) / width))
    cappy = cappy.resize((int(new_width), int(new_height)), Image.ANTIALIAS)
    cappy_offset = int(new_width / 2.0), int(new_height / 2.0)
    cappy_position = int(left - 0.25 * cappy_offset[0]), int(top - 1.7 * cappy_offset[1])
    image.paste(cappy, cappy_position, mask=cappy)
    cappy.close()

# Below courtesy of https://github.com/jajoosam/f00l0wers/blob/master/bot.py
# create a class inherithing from the tweepy  StreamListener
class BotStreamer(tweepy.StreamListener):
    
    # Called when a new status arrives which is passed down from the on_data method of the StreamListener
    def on_status(self, status):
        username = status.user.screen_name
        status_id = status.id
        
        # entities provide structured data from Tweets including resolved URLs, media, hashtags and mentions without having to parse the text to extract that information
        if 'media' in status.entities:
            for image in status.entities['media']:
                tweetImage(image['media_url'], username, status_id)

myStreamListener = BotStreamer()

# Construct the Stream instance
stream = tweepy.Stream(auth, myStreamListener)

# TODO: Fill in handle here
stream.filter(track=['@'])


'''*This work was not produced in association with Nintendo Co., Ltd. Mario
    and his likeness are the properties of Nintendo Co., Ltd., all rights reserved.'''
