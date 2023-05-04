''' 
lambda_function.py
Provides Stevebot functionality while hosted on AWS Lambda server
Intake through API Gateway link, makes POST requests to send messages
'''

import os
import random
import re
import json
import urllib
import urllib.request

# determine the denominator + 1 for responding to lack of "hwh"
# e.g. 3 would mean 1/(3 + 1) chance of triggering
HW_RESPONSE_RATE = 2

main_choices = [
    'Hosano in excelsis',
    '*messa di voce\'ing intensifies*',
    ':sassy-sano:',
    ':master-sano:',
    ':acoustic_guitar::acoustic_guitar::acoustic_guitar:',
    'I wanna be _vibin_ :catjam: in :hawaii:',
    'it me ya fav boi treble reportin in',
    'accent that messa di voce button',
    'ope let me slack key vamp right past ya',
    'hippity hoppity Chorale memes are quality',
    ':blobcatglowsticks: Go Chorale go! :blobcatglowsticks:',
    ':boba1::boba2:\n:boba3::boba4:\n:boba5::boba6:',
    'THAT\'S IT!!!',
    ':10_10:',
    ':resitas:',
    ':cooldoge:',
    ':tobu:',
    ':amaze:',
    ':dicaprio_laugh:',
    ':bear_roll:',
    # '@Trip ya might want to see a doctor for all those :shaking-eyes: reaccs... :lizard-hehehehe:',
    ':0_0:',
    'Another random shout-out to our lovely social chairs for bringing us closer :meow_heart::cat-meow-hearts::heart::heart::heart:',
    ':exploding_head: when the basses hit that low D :mindblown::weary::sweat_drops::walter-faint:',
    'Friendship ended with GroupMe, now Slack is my best friend',
    # cool(),
    # 'Meet me at MemSquirt',
    '',
    'Another reminder to send in anonymous/non-anonymous messages of Chorale shout-outs to yourmanito92@gmail.com! 😊 You can use temporary email address (like 1hr email) for anonymity!',
    '*plays a sick slack key vamp*',
    # '*cringing in Hawaiian*',
    '*judging in ʻŌlelo Hawaiʻi*',
    # 'Mmmmm that post was so ʻono! nom nom nom',
    'catfacts_trigger',  # Will pick random cat fact
    'catfacts_trigger',  # Mohr kat faxs
    'catfacts_trigger',  # Mohrrr kat faxs
    'catfacts_trigger',  # Mohrrrrrr kat faxs
    '',  # empty text will indicate the need for meme-ing; )
    '',  # Add a few for increased meme chances
    ''
]

cat_intro = [
    "Everyone needs a cat fact now and again 😜 ",
    # "You might say, \'wow, Steve is actually hard to meme about\', and you'd be right! So here's a cat fact instead: ",
    "Did you know... ",
    "Why make Steve memes when you can read cat facts? ",
    "And it's time for... random cat facts! ",
    # "Cat Facts! 😜 ",
    "It's meow time~ ",
    ':meow_knife: more katfax or else... ',
    'Oh my, would you look at the time?! It\'s time for.... a cat fact!! 😜 '
]

cat_flair = [
    "Meow! 😺", "Me-woah! 😸", "Me-awww! 😻", "Le Meow 😺", "yeet.", "Stev-eow!",
    ":meow_floof_pat:", ":meow-dj:", ":bongocat:", ":cat_keyboard:",
    "Aww! 🥺"
]

catfacts = [
    "A group of cats is called a clowder. A group of cool cats is called a Chorale 😘",
    # "When cats climb a tree, they can't go back down it head first. This is because their claws are facing the same way, instead, they have to go back down backward.",
    # "Cats have over 20 muscles that control their ears. All straining to hear us sing...",
    "Much like college students, cats sleep 70% of their lives. (I feel attacked)",
    '"The Hungarian word for "quotation marks," macskaköröm, literally translates to "cat claws."',
    "Cats can’t taste sweetness. Now we know why they don't lick Chorale members more often 😥",
    "Owning a cat can reduce the risk of stroke and heart attack by a third. Singing with Chorale can, too, probably?!",
    "The world’s richest cat is worth $13 million after his human passed away and left her fortune to him. Still not richer than Akshar's bass notes tho 😉",
    # "Cats make more than 100 different sounds whereas dogs make around 10. Stay tuned for how many sounds Courtney can make while getting her back cracked...",
    "Hearing is the strongest of cat’s senses: They can hear sounds as high as 64 kHz — compared with humans, who can hear only as high as 20 kHz. That moment when you're suddenly envious of cats while listening to Jin-Hee sing...",
    # "The Egyptian Mau is the oldest breed of cat. Deadmau5 comes close second.",
    # "In Holland’s embassy in Moscow, Russia, the staff noticed that the two Siamese cats kept meowing and clawing at the walls of the building. Their owners finally investigated, thinking they would find mice. Instead, they discovered microphones hidden by Russian spies. The cats heard the microphones when they turned on. Instead of alerting the Russians that they found said microphones, they simply staged conversations about delays in work orders and suddenly problems were fixed much quicker!",
    # "The oldest cat video dates back to 1894 and is called 'Boxing Cats'",
    # "The oldest cat to ever live was Creme Puff, who lived to be 38 years and 3 days old.",
    # "The more you talk to your cat, the more it will talk to you.",
    # "Nikola Tesla was inspired to investigate electricity after his cat, Macak, gave him a static shock.",
    # "Isaac Newton invented the cat flap after his own cat, Spithead, kept opening the door and spoiling his light experiments.",
    # "It was considered a capital offense to kill a cat in ancient Egypt.",
    "Purring actually improves bone density and promotes healing within a cat. The purring frequency — 26 Hertz — apparently aides in tissue regeneration and can help stimulate the repair of weak and brittle bones. Explains why Kaile's low notes are so healing 🤤",
    "Cats involuntarily open their mouths after smelling something, tbh I do the same when I hear Julia sing 😲",
    "The world's largest domestic cat is a Maine Coon cat named Stewie, who measures an astounding 48.5 inches long. Still not as tall as Kyle tho 😎",
    'A female cat is called a “molly” or a “queen.” yassssss',
    "A cat’s heart beats nearly twice as fast as a human's heart. :heartbeat:",
    "Cats are responsible for the decimation of 33 different animal species, and they kill around 2.4 million birds a year. :meow_knife: Sorry Maya :meow-reachcry::dove_of_peace:",
    "Cats actually CAN be loyal. A cat named Toldo was renowned in the village of Montagnana, Italy, for visiting his owner's grave every day for a year after he died. ALMOST as loyal as Toby is to staying in Chorale :100_ani::respect:",
    "Cats can move their ears 180 degrees. Getting the best seats in the house wherever they are, so lucky!"
]

memeLinks = [
    'https:#i.groupme.com/640x427.jpeg.508232616c66438a999de11438c4047c',  # It was me, Steve!
    'https:#i.groupme.com/580x557.jpeg.48b980efe8fb434d9ab619c2454ded7c',  # "Good one lol"
    # mfw someone posts on GroupMe
    'https:#i.groupme.com/580x557.jpeg.3606a48cd2ef4ab2a1fae63cd36d3d62',
    'https:#i.groupme.com/1331x1996.jpeg.57011624684a41cfa90c2e8da5240378.large',  # yummy voices
    'https:#i.groupme.com/2048x1366.jpeg.1aafacaebe1c49599a67d03c7a48b5e8'  # wholesome meme
]

def handle_command(event, post_to_slack):
    cmd = event['event']['command'].lower()
    msg = event['event']['text'].lower()
    user = event["event"]["user"]
    
    print(f"Handling command {cmd} with args {msg}")
    
    if "aloha" in cmd:
        choices = [f"Aloha <@{user}>!"]

        # gif_url = get_random_gif("hawaii")
        post_to_slack(event, random.choice(choices), ephemeral = true)

def handle_message(event, post_to_slack):
    msg = event['event']['text'].lower()
    user = event["event"]["user"]
    print(f"I heard ya, message {msg}")
    
    '''
    if "cookie" in msg:
        gif_url = get_random_gif("cookie monster")
        post_to_slack(event, "DID SOMEONE SAY *COOKIE*?!\n", gif_url)
    '''
    if "cat fact" in msg:
        response = random.choice(cat_intro) + random.choice(
                    catfacts) + random.choice(cat_flair)
        post_to_slack(event, response)
    elif "aloha" in msg:
        choices = [f"Aloha <@{user}>!"]

        # gif_url = get_random_gif("hawaii")
        post_to_slack(event, random.choice(choices))
    elif "messa di voce" in msg:
        choices = [
            'I know I bring up messa di voce a lot, but now get ready for the reverse messa di voce: >.<',
            'messa di voce had me like >.<',
            ':amaze: when that messa di voce hits :amaze:',
            'YES MESSA DI VOCE THAT LIKE BUTTON :likeitalian:'
        ]
        post_to_slack(event, random.choice(choices))
    elif "boy treble" in msg:
        choices = [
            'Boy treble, you say; oh boy oh boy let me tell you all about my life as a boy treble',
            'ope let me boy treble right past ya',
            'hippity hoppity boi treble in your area', 'it\'s me, ya fav boi treble'
        ]
        post_to_slack(event, random.choice(choices))
    elif "uwu" in msg:
        choices = [
            'NO UWU\'ING ALLOWED IN THIS GROUP', f"...u...uwu <@{message['user']}>",
            "your weeb is showing!", 'Senpai will never notice you! 😤😤',
            'THE ONLY ACCEPTABLE WEEBSPEAK IN THIS GROUP IS >.< AND ONLY BECAUSE IT\'S A REVERSE MESSA DI VOCE!!'
        ]
        post_to_slack(event, random.choice(choices))
    elif "boba" in msg:
        choices = [
            ":boba1::boba2:\n:boba3::boba4:\n:boba5::boba6:", "BOBAAAAAA", ":boba:",
            ":bobacat:", ":bobaparrot:"
        ]
        post_to_slack(event, random.choice(choices))
    elif re.search(r'h[\S]{0,1}wh[yae].*', msg):
        choices = [
            'I\'m loving the hhhhwh in that. thank you 🥰🥰',
            'F`ing delicious. Thank you for the beautiful hhwwwh. mHWaH',
            f"You just made my day <@{user}>! thank you :cat-meow-hearts:", 
            "THAT'S IT!!!!"
        ]
        post_to_slack(event, random.choice(choices))
    elif 'sano' in msg or 'steve' in msg:
        url = ""
        response = random.choice(main_choices)
        if "catfacts_trigger" in response:

            response = random.choice(cat_intro) + random.choice(
                catfacts) + random.choice(cat_flair)
        # post an image for empty string
        elif not response:
            url = random.choice(memeLinks)
        post_to_slack(event, response, url)
    elif re.search(r'[^h]what', msg):
        if random.randrange(HW_RESPONSE_RATE) == 0:
            post_to_slack(event, "*Hwhat")
    elif re.search(r'[^h]why', msg):
        if random.randrange(HW_RESPONSE_RATE) == 0:
            post_to_slack(event, "*Hwhy")
    elif re.search(r'[^h]where', msg):
        if random.randrange(HW_RESPONSE_RATE) == 0:
            choices = [
                "*Hwhere", "*Hwhere is the Hay?", "*Hwhere is the Blush?",
                "*Hwhere is the Bee?"
            ]
            post_to_slack(event, random.choice(choices))
    elif re.search(r'[^h]when', msg):
        if random.randrange(HW_RESPONSE_RATE) == 0:
            post_to_slack(event, "*Hwhen")
    elif "test_invoke" in msg:
        choices = [
            ':boba1::boba2:\n:boba3::boba4:\n:boba5::boba6:', 'THAT\'S IT!!!',
            ':10_10:', ':resitas:', ':cooldoge:', ':tobu:', ':amaze:',
            ':dicaprio_laugh:', ':bear_roll:',
            '@Trip ya might want to see a doctor for all those :shaking-eyes: reaccs... :lizard-hehehehe:',
            ':0_0:',
            'Another random shout-out to our lovely social chairs for bringing us closer :meow_heart::cat-meow-hearts::heart::heart::heart:',
            ':exploding_head: when the basses hit that low D :mindblown::weary::sweat_drops::walter-faint:',
            'Friendship ended with GroupMe, now Slack is my best friend'
        ]
        post_to_slack(event, random.choice(choices))

# Not yet fully implemented unfortunately
# api_key was forbidden as of 4/2/2023; also need to check urllib request usage

'''
def get_random_gif(tag):
    # Fetch a random GIF from Giphy using tag
    
    api_key = 'dc6zaTOxFJmzC'
    url = 'https://api.giphy.com/v1/gifs/random'
    data = urllib.parse.urlencode({'api_key': api_key, 'tag': tag.lower(), 'rating': 'pg'})
    
    data = data.encode("ascii")
    request = urllib.request.Request(url, data=data, method="POST")
    request.add_header( "Content-Type", "application/x-www-form-urlencoded" )
    res = urllib.request.urlopen(request).read()
    
    data = resp.json()
    return data['data']['url']
'''

# Code below are adapted from https://github.com/cazabec/slackbot-aws-lambda/blob/main/lambda/event_receiver.py
print('Loading function')

def is_bot(event):
    return "bot_profile" in event["event"]

""" 
MAIN FUNCTIONS BELOW
"""
def send_response(event, response_text, url = "", ephemeral = False):
    SLACK_URL = "https://slack.com/api/chat.postEphemeral" if ephemeral else "https://slack.com/api/chat.postMessage" # use postMessage if we want visible for everybody
    channel_id = event["event"]["channel"]
    user = event["event"]["user"]
    event_type = event["event"]["type"]  # Examples: reaction_added, message.channels, team_join.
    team_id = event["team_id"]
    response_dict = {
            "token": os.environ['SLACK_BOT_TOKEN'],
            "channel": channel_id,
            "link_names": True
        }
    if response_text:
        response_dict["text"] = response_text
        
    if url:
        response_dict["image_url"] = url
        
    data = urllib.parse.urlencode(response_dict)
    data = data.encode("ascii")
    request = urllib.request.Request(SLACK_URL, data=data, method="POST")
    request.add_header( "Content-Type", "application/x-www-form-urlencoded" )
    res = urllib.request.urlopen(request).read()
    print('res:', res)


"""
ENTRY POINT, TRUE MAIN
"""
def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    
    # Command is provided in the form of application/x-www-form-urlencoded
    try: 
        cmd_dict = urllib.parse.parse_qs(event)
        print(cmd_dict)
        if "command" in cmd_dict:
            handle_command(cmd_dict, send_response)
        
    except Exception as e:
        slack_body = event.get("body")
        if slack_body:
            '''
            Code for responding to challenge
            '''
            slack_event = json.loads(slack_body)
            challenge_answer = slack_event.get("challenge")
            
            if challenge_answer:
                return {
                    'statusCode': 200,
                    'body': challenge_answer
                }
            
            if not is_bot(slack_event):
                print(slack_event)
                print("Received text: " + slack_event['event']['text'])
                
                handle_message(slack_event, send_response)
    
    return {
        'statusCode': 200,
        'body': 'OK'
    }
    
