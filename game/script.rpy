

init python:

    class PongDisplayable(renpy.Displayable):

        def __init__(self):

            renpy.Displayable.__init__(self)

            # The sizes of some of the images.
            self.PADDLE_WIDTH = 12
            self.PADDLE_HEIGHT = 95
            self.PADDLE_X = 240
            self.BALL_WIDTH = 15
            self.BALL_HEIGHT = 15
            self.COURT_TOP = 190
            self.COURT_BOTTOM = 880

            # Some displayables we use.
            self.paddle = Solid("#ffffff", xsize=self.PADDLE_WIDTH, ysize=self.PADDLE_HEIGHT)
            self.ball = Solid("#ffffff", xsize=self.BALL_WIDTH, ysize=self.BALL_HEIGHT)

            # If the ball is stuck to the paddle.
            self.stuck = True

            # The positions of the two paddles.
            self.playery = (self.COURT_BOTTOM - self.COURT_TOP) / 2
            self.computery = self.playery

            # The speed of the computer.
            self.computerspeed = 350.0

            # The position, delta-position, and the speed of the
            # ball.
            self.bx = self.PADDLE_X + self.PADDLE_WIDTH + 10
            self.by = self.playery
            self.bdx = .5
            self.bdy = .5
            self.bspeed = 600.0

            # The time of the past render-frame.
            self.oldst = None

            # The winner.
            self.winner = None

        def visit(self):
            return [ self.paddle, self.ball ]

        # Recomputes the position of the ball, handles bounces, and
        # draws the screen.
        def render(self, width, height, st, at):

            # The Render object we'll be drawing into.
            r = renpy.Render(width, height)

            # Figure out the time elapsed since the previous frame.
            if self.oldst is None:
                self.oldst = st

            dtime = st - self.oldst
            self.oldst = st

            # Figure out where we want to move the ball to.
            speed = dtime * self.bspeed
            oldbx = self.bx

            if self.stuck:
                self.by = self.playery
            else:
                self.bx += self.bdx * speed
                self.by += self.bdy * speed

            # Move the computer's paddle. It wants to go to self.by, but
            # may be limited by it's speed limit.
            cspeed = self.computerspeed * dtime
            if abs(self.by - self.computery) <= cspeed:
                self.computery = self.by
            else:
                self.computery += cspeed * (self.by - self.computery) / abs(self.by - self.computery)

            # Handle bounces.

            # Bounce off of top.
            ball_top = self.COURT_TOP + self.BALL_HEIGHT / 2
            if self.by < ball_top:
                self.by = ball_top + (ball_top - self.by)
                self.bdy = -self.bdy

                if not self.stuck:
                    renpy.sound.play("pong_beep.opus", channel=0)

            # Bounce off bottom.
            ball_bot = self.COURT_BOTTOM - self.BALL_HEIGHT / 2
            if self.by > ball_bot:
                self.by = ball_bot - (self.by - ball_bot)
                self.bdy = -self.bdy

                if not self.stuck:
                    renpy.sound.play("pong_beep.opus", channel=0)

            # This draws a paddle, and checks for bounces.
            def paddle(px, py, hotside):

                # Render the paddle image. We give it an 800x600 area
                # to render into, knowing that images will render smaller.
                # (This isn't the case with all displayables. Solid, Frame,
                # and Fixed will expand to fill the space allotted.)
                # We also pass in st and at.
                pi = renpy.render(self.paddle, width, height, st, at)

                # renpy.render returns a Render object, which we can
                # blit to the Render we're making.
                r.blit(pi, (int(px), int(py - self.PADDLE_HEIGHT / 2)))

                if py - self.PADDLE_HEIGHT / 2 <= self.by <= py + self.PADDLE_HEIGHT / 2:

                    hit = False

                    if oldbx >= hotside >= self.bx:
                        self.bx = hotside + (hotside - self.bx)
                        self.bdx = -self.bdx
                        hit = True

                    elif oldbx <= hotside <= self.bx:
                        self.bx = hotside - (self.bx - hotside)
                        self.bdx = -self.bdx
                        hit = True

                    if hit:
                        renpy.sound.play("pong_boop.opus", channel=1)
                        self.bspeed *= 1.10

            # Draw the two paddles.
            paddle(self.PADDLE_X, self.playery, self.PADDLE_X + self.PADDLE_WIDTH)
            paddle(width - self.PADDLE_X - self.PADDLE_WIDTH, self.computery, width - self.PADDLE_X - self.PADDLE_WIDTH)

            # Draw the ball.
            ball = renpy.render(self.ball, width, height, st, at)
            r.blit(ball, (int(self.bx - self.BALL_WIDTH / 2),int(self.by - self.BALL_HEIGHT / 2)))

            # Check for a winner.
            if self.bx < -50:
                self.winner = "eileen"

                # Needed to ensure that event is called, noticing
                # the winner.
                renpy.timeout(0)

            elif self.bx > width + 50:
                self.winner = "player"
                renpy.timeout(0)

            # Ask that we be re-rendered ASAP, so we can show the next
            # frame.
            renpy.redraw(self, 0)

            # Return the Render object.
            return r

        # Handles events.
        def event(self, ev, x, y, st):

            import pygame

            # Mousebutton down == start the game by setting stuck to
            # false.
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                self.stuck = False

                # Ensure the pong screen updates.
                renpy.restart_interaction()

            # Set the position of the player's paddle.
            y = max(y, self.COURT_TOP)
            y = min(y, self.COURT_BOTTOM)
            self.playery = y

            # If we have a winner, return him or her. Otherwise, ignore
            # the current event.
            if self.winner:
                return self.winner
            else:
                raise renpy.IgnoreEvent()


default popups_closed = 0
default time_remaining = 10.0
default system_integrity = 5

init python:
    import random

    def InitPopupGame():
        global popups_closed, time_remaining, popups, total_popups_spawned
        popups_closed = 0
        time_remaining = 10.0
        total_popups_spawned = 5  # Start with 5 popups initially
        popups = [(random.randint(100, 1600), random.randint(100, 900)) for _ in range(5)]

    def ClosePopup(index):
        global popups_closed, total_popups_spawned

        popups_closed += 1
        renpy.play("sounds/click.mp3", channel="sound")

        # Only respawn new popups if fewer than 10 total have been spawned
        if total_popups_spawned < 10:
            popups[index] = (random.randint(100, 1600), random.randint(100, 900))  # Respawn popup
            total_popups_spawned += 1
        else:
            popups[index] = None  # Remove this popup permanently

        # If all popups are clicked, end the game
        if popups_closed >= 10:
            renpy.hide_screen("popup_minigame")
            renpy.jump("after_popup_game")  # Use `jump` instead of `call`

# 📌 Popup Minigame Screen (Ensures Correct Return Handling)
screen popup_minigame():
    modal True

    timer 0.05 repeat True action [
        SetVariable("time_remaining", max(time_remaining - 0.05, 0)),
        If(time_remaining <= 0.0, true=[Hide("popup_minigame"), Return(popups_closed)])
    ]

    add "bg_popup"

    for i in range(5):
        if popups[i] is not None:
            imagebutton:
                xpos popups[i][0]
                ypos popups[i][1]
                idle "popup"
                hover "popup_hover"
                action [Function(ClosePopup, i)]

    # Timer bar
    bar value StaticValue(time_remaining, 10.0):
        align (.5, .001)
        xmaximum 400
        ymaximum 20
        left_bar Frame("slider_left.png", 10, 10)
        right_bar Frame("slider_right.png", 10, 10)
        thumb None
        thumb_shadow None



screen pong():

    default pong = PongDisplayable()

    add "bg pong field"

    add pong

    text "CyberGOD":
        color "#ffffff"
        xpos 500
        xanchor 0.5
        ypos 25
        size 60

    text "Virus":
        color "#ffffff"
        xpos (1300)
        xanchor 0.5
        ypos 25
        size 60

    if pong.stuck:
        text "Click to Begin":
            xalign 0.5
            ypos 50
            size 40

label play_pong:

    window hide  # Hide the window and quick menu while in pong
    hide mc
    hide charf
    $ quick_menu = False

    call screen pong

    $ quick_menu = True
    window show

    jump job_offer_end



label start:
    scene techbg
    show mc:
        xalign 0.0 yalign 1.0


    define mc = Character("CyberGOD")
    define c = Character("Julie")
    define d = Character("Dylan")
    define f = Character("Sherry")
    define g = Character("UNKNOWN")
    
   
    mc "I'm a CyberGOD. I'm very cracked."
    mc "This is great because I get to help everyone with cybersecurity."
    mc "So let's start, who should I help first?"
   
    menu:
        # "Jenny":
        #     jump email_lottery
        # "Gavin":
        #     jump instagram
        "Julie":
            jump called
        "Dylan":
            jump popups
        # "Sean":
        #     jump password
        "Sherry":
            jump job_offer



label called:
    mc "Our friend, Julie, received a call, but it feels off."
    show chara:
        xalign 1.0 yalign 1.0
    show unknown:
        xalign 0.5 yalign 1.2
    g "Hello, this is Morgan from the bank. Is this Julie I'm speaking with?"
    c "U-uh yes? Is there a problem?"
 
    g "Yes, your account is at risk of losing all the savings. I can take care of this for you if you would send me a picture of your government ID and tell us.."
    menu:
        "Stay silent?":
            mc "..."
            g "- tell us your card number, expiration date, and cvv number please."
            c "*gives information*"
            scene scammedbybank
            "Game Over!"
            menu:
                "Restart":
                    jump start
                "Quit":
                    jump end
        "Speak up?":
            mc "I feel like this is an important matter, we should meet in person at the bank to resolve it instead of doing this over the phone."
            c "Great idea, CyberGOD!"
            c "Hello, is it okay if I come to the bank to resolve this?" 
            g "No, this is really urgent, we need to do it NOW!"
            mc "We're really close to the bank!"
            g "No need, JUST TELL ME!"
            c "Wait... this is"
            mc "Yes, this is a scam!"
            g "Urgh ****** nosy brats!!! *unknown caller hang up*"   
    hide unknown
    c "OMG, thank you so much for saving me!"
    c "What would I do without you, CyberGOD. Bye~"
    mc "Well, Julie, you should be more careful. Just to be safe, what do you use as your password?"
    c "I use my name! It's easy to remember!"
    mc "Yes, but it's also easy to hack. Instead, you should use a secure password!"
    mc "Now, let's create a strong password for your new bank account."


    # Get favorite TV show character
    $ fact1 = renpy.input("What is your favorite TV show character?")
    $ fact1 = fact1.lower().strip()
    while not fact1.isalnum():
        $ fact1 = renpy.input("Enter a valid word (letters and numbers only).")


    # Replace certain characters for security
    python:
        new_fact = ""
        for val in range(len(fact1)):
            if val != 0:
                if fact1[val] == "a":
                    new_fact += "@"
                elif fact1[val] == "i":
                    new_fact += "!"
                elif fact1[val] == "o":
                    new_fact += "0"
                elif fact1[val] == "e":
                    new_fact += "3"
                else:
                    new_fact += fact1[val]
            else:
                new_fact += fact1[val]
        fact1 = new_fact.capitalize()


    # Get childhood street number
    $ fact2 = renpy.input("What was the street number of your childhood home?", length=4)
    while not fact2.isdigit():
        $ fact2 = renpy.input("Enter a valid number.")


    # If the password length is too short, ask for more details
    if len(fact1) + len(fact2) < 12:
        
        # Ask for favorite color
        $ fact3 = renpy.input("What is your favorite color?")
        $ fact3 = fact3.lower().strip()
        while not fact3.isalnum():
            $ fact3 = renpy.input("Enter a valid word.")


        python:
            new_fact3 = ""
            for val in range(len(fact3)):
                if val != 0:
                    if fact3[val] == "a":
                        new_fact3 += "@"
                    elif fact3[val] == "i":
                        new_fact3 += "!"
                    elif fact3[val] == "o":
                        new_fact3 += "0"
                    elif fact3[val] == "e":
                        new_fact3 += "3"
                    else:
                        new_fact3 += fact3[val]
                else:
                    new_fact3 += fact3[val]
            fact3 = new_fact3.capitalize()
    
    # Construct the password
    python:
        if len(fact1) + len(fact2) >= 12:
            password = f"{fact1}@{fact2}"
        elif len(fact1) + len(fact2) + len(fact3) >= 12:
            password = f"{fact1}{fact3}@{fact2}"
        else:
            password = f"{fact1}{fact3}Strong@{fact2}"


    # Display the generated password
    mc "Your secure password is: [password]"
    
    c "Thank you so much, CyberGOD! I'll use this secure password from now on."
    mc "Yep! Bye Julie!"

    hide chara
    mc "Ok, so let's review what we learned today."
    mc "What should you do if you get an unknown phone call?"
    menu:
        "Give them your private information if they ask for it.":
            $ result = "wrong"
        "Proceed with caution as it may be a scam call.":
            $ result = "correct"
        "Ignore the call and block the number.":
            $ result = "wrong"
   
    if result == "correct":
        mc "Correct! You've identified the best course of action."
    else:
        mc "Wrong! The correct answer is to proceed with caution as it may be a scam call."
        mc "Be more careful next time."
    mc "What should you choose as your password"
    menu:
        "Your name.":
            $ result = "wrong"
        "A combination of letters and numbers.":
            $ result = "correct"
        "Your birthday.":
            $ result = "wrong"
   
    if result == "correct":
        mc "Correct! You've identified the best password."
    else:
        mc "Wrong! The correct answer is a combination of letters and numbers."
        mc "Be more careful next time."
    mc "Tips to remember:"
    mc "DO NOT share your private information before verifying the caller's identity."
    mc "Remember next time to think critically about unknown phone calls and if they might be a scam."
    mc "Who do we help next?"

    menu:
        "Dylan":
            jump popups
        "Sherry":
            jump job_offer
        "Quit":
            jump end

   


label popups:
    mc "Our poor friend, Dylan, was casually reading webtoons illegally off the web."
    show chard:
        xalign 1.0 yalign 1.0
    d "I was just reading, and then suddenly I got so many pop-ups!"
    d "They're so annoying! Help!"
    mc "Don't worry Dylan, that's what I'm here for!"
    mc "Let's get rid of those pop-ups!"

    # Initialize the minigame
    $ InitPopupGame()
    call screen popup_minigame
    $ result = _return

    # Ensure the result is valid
    if result is None:
        $ result = 0  # Prevent crashes if no value was returned

    jump after_popup_game

label after_popup_game:
    show mc:
        xalign 0.0 yalign 1.0

    if popups_closed >= 10:
        mc "Great job! You cleared all the pop-ups!"
    else:
        mc "You didn't clear all the pop-ups in time. Be more careful next time."

    jump popups_end

label popups_end:
    show chard:
        xalign 1.0 yalign 1.0
    show mc:
        xalign 0.0 yalign 1.0
    mc "Well, Dylan, now you know."
    mc "If you can, avoid using piracy websites as they are full of malware. We don't know what we are exposing our data to. "
    mc "DO NOT click on the pop-up or download anything suspicious."
    mc "If you happen to open the pop-up, close the tab IMMEDIATELY!! Try using an ad blocker to fight off these pesky pop-ups!!"
    d "Thank you so much, CyberGOD! I'll be more careful next time!"
    hide chard

    mc "Well, let's go over some trivia!!"
    mc "Which domain is FAKE?"
    menu:
        "googIe-security.net":
            $ result = "correct"
        "irs.gov":
            $ result = "wrong"
        "tesla.com":
            $ result = "wrong"
   
    if result == "correct":
        mc "Correct! You've identified the fake domain."
    else:
        mc "Wrong! The wrong domain is googIe-security.net"
        mc "Be more careful next time."

    mc "Let's try another one. Which domain is FAKE?"
    menu:
        "instagrarn-login.com":
            $ result = "correct"
        "cloudflare.com":
            $ result = "wrong"
        "zoom.us":
            $ result = "wrong"
   
    if result == "correct":
        mc "Correct! You've identified the fake domain."
    else:
        mc "Wrong! The wrong domain is instagrarn-login.com"
        mc "Be more careful next time."

    mc "One more time. Which domain is FAKE?"
    menu:
        "telegram.org":
            $ result = "wrong"
        "twitch.tv":
            $ result = "wrong"
        "amazn-support.help":
            $ result = "correct"
   
    if result == "correct":
        mc "Correct! You've identified the fake domain."
    else:
        mc "Wrong! The wrong domain is amazn-support.help"
        mc "Be more careful next time."
    
    mc "Well, that's that. Who should I help next?"

    menu:
        "Julie":
            jump called
        "Sherry":
            jump job_offer
        "Quit":
            jump end



label job_offer:
    mc "Sherry received an amazing job offer. However, something seems off. Let's take a closer look."
    show charf:
        xalign 1.0 yalign 1.0
    f "Hi CyberGOD!! I just received an email from a company offering me a job. I'm so excited!"
    mc "That's great! I'm so proud of you!"
    f "Here, let me show you!! It's for a software engineering position at Google!"
    show email:
        xalign 0.5 yalign 1 
    f "Here!"
    hide email
    f "I've sent in so many applications, I'm so happy the job hunt is finally over!"
    mc "Wow, congratul- wait..."
    mc "Sherry, this doesn't look right. Look at the sender. I don't think this is real."
    f "Huh? Wait, no... you're right! Oh, what do I do? I just clicked on the link and it led me to a phishing website!"
    mc "You may have a virus in your computer."
    mc "But don't worry, I'm here to help. Let's get rid of it."
    jump play_pong
    

label job_offer_end:
    show mc:
        xalign 0.0 yalign 1.0
    show charf:
        xalign 1.0 yalign 1.0
    if _return == "eileen":
        mc "ah..."
        f "NOOOOOOOOOO!"
        f "WHAT DO I DO NOW???"
        mc "Stay safe and better luck next time Sherry."
    else:
        mc "Easy"
        f "OMG, thank you so much CyberGOD! I don't know what I would do without you!"
        f "Well, now I have to go cry in a corner and continue sending in job apps. See you around!"
    hide charf
    mc "Well, Who should I help next?"
    menu:
        "Julie":
            jump called
        "Dylan":
            jump popups
        "quit":
            jump end

label end:
    mc "Well, that's it then!!"
    mc "CyberGOD out"
    return








   