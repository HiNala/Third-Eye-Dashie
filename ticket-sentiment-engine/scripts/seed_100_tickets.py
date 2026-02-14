#!/usr/bin/env python3
"""Seed script — ingests 100 realistic sample tickets for load/analysis testing."""

import httpx
import sys
import json

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"

SAMPLE_TICKETS = [
    # --- Product Support (25 tickets) ---
    {
        "title": "Screen flickering after latest update",
        "content": "Hi team,\n\nAfter the most recent software update, my DC-1 screen has been flickering intermittently. It happens mostly when I'm using the browser. I've tried restarting but the issue persists. This is really frustrating because I use this for work every day as a freelance writer.\n\nPlease help!",
        "customer_email": "marcus.writer@example.com",
        "status": "open",
    },
    {
        "title": "Battery draining unusually fast",
        "content": "Hello,\n\nI've had my Daylight for about 3 months now and the battery used to last all day. Recently it's been dying after about 4 hours of use. I'm a college student and I rely on this for classes. Is there a way to check battery health or get a replacement?\n\nThanks,\nEmily",
        "customer_email": "emily.student@example.com",
        "status": "open",
    },
    {
        "title": "Bluetooth keyboard not connecting",
        "content": "My Bluetooth keyboard won't pair with the Daylight Computer. I've tried resetting Bluetooth, forgetting the device, and re-pairing multiple times. The keyboard works fine with my phone. Is there a known compatibility issue? I'm a software developer and I really need an external keyboard for coding.",
        "customer_email": "dev.sarah@example.com",
        "status": "open",
    },
    {
        "title": "Touch screen unresponsive in bottom corner",
        "content": "The bottom-right corner of my touch screen has become completely unresponsive. I can't tap anything in that area. The rest of the screen works fine. I bought this about 6 weeks ago. Order #JAGAR-112500123.",
        "customer_email": "touch.issue@example.com",
        "status": "open",
    },
    {
        "title": "Wi-Fi keeps disconnecting",
        "content": "Hi,\n\nMy Daylight Computer keeps dropping the Wi-Fi connection every 15-20 minutes. I have to manually reconnect each time. My other devices work fine on the same network. I'm a remote worker in Vermont and reliable internet is critical for my video calls.\n\nThis started about a week ago. Any ideas?",
        "customer_email": "remote.worker.vt@example.com",
        "status": "open",
    },
    {
        "title": "App crashes when opening large PDFs",
        "content": "The Reader app crashes every time I try to open PDFs over 50 pages. I'm a law student and I need to read case files that are often 100+ pages. Smaller files work fine. Is this a known limitation?\n\nUsing DC-1, latest firmware.",
        "customer_email": "lawstudent@example.com",
        "status": "open",
    },
    {
        "title": "How to factory reset?",
        "content": "Hello, I'd like to factory reset my Daylight Computer before giving it to my daughter. I can't find the option in settings. Can you walk me through the process? I want to make sure all my data is wiped clean.\n\nThank you!",
        "customer_email": "dad.gift@example.com",
        "status": "open",
    },
    {
        "title": "Charging cable stopped working after 2 months",
        "content": "The USB-C charging cable that came with my Daylight stopped working. The tablet won't charge with it anymore, but charges fine with a different cable. Can I get a replacement cable? I don't want to use a third-party one and risk damaging the device.",
        "customer_email": "cable.issue@example.com",
        "status": "open",
    },
    {
        "title": "Display has a dead pixel",
        "content": "I just received my Daylight Computer yesterday and there's a noticeable dead pixel near the center of the screen. It's a small green dot that's always visible. For a premium device at this price point, I expected a perfect display. Order #JAGAR-112600789.\n\nWhat are my options?",
        "customer_email": "dead.pixel@example.com",
        "status": "open",
    },
    {
        "title": "Volume buttons not working",
        "content": "Both volume buttons on my DC-1 have stopped responding. I can still adjust volume through the on-screen controls, but the physical buttons do nothing. Is this a hardware defect? The device is about 4 months old.",
        "customer_email": "volume.buttons@example.com",
        "status": "open",
    },
    {
        "title": "Can I install Android apps?",
        "content": "Hi there,\n\nI'm considering buying a Daylight Computer for my mom who has macular degeneration. She currently uses specific accessibility apps on her Android phone. Can those same apps be installed on the Daylight? She's 72 and lives alone in Florida, so I want to make sure she can use all her familiar apps.\n\nThanks for any info!",
        "customer_email": "son.helping.mom@example.com",
        "status": "open",
    },
    {
        "title": "Stylus not recognized after dropping device",
        "content": "I accidentally dropped my Daylight from my desk (about 3 feet) and now the stylus input isn't being recognized at all. The touchscreen still works with my fingers. Is the digitizer layer damaged? I'm a graphic designer and the stylus is essential for my work.",
        "customer_email": "designer.drop@example.com",
        "status": "open",
    },
    {
        "title": "Screen brightness stuck at maximum",
        "content": "My screen brightness is stuck at the maximum level and I can't adjust it. The slider in settings moves but nothing changes on screen. I usually use this for reading before bed and the brightness is way too high now.\n\nI'm a nurse who works night shifts so eye strain is a real concern for me.",
        "customer_email": "night.nurse@example.com",
        "status": "open",
    },
    {
        "title": "Daylight Capture extension not showing in browser",
        "content": "I installed the Daylight Capture extension but it's not appearing in my browser toolbar. I've tried reinstalling it three times. I'm running the latest version of the browser on my DC-1. This is really important for my research workflow — I'm a PhD candidate studying neuroscience.",
        "customer_email": "phd.neuro@example.com",
        "status": "open",
    },
    {
        "title": "Speaker crackling at high volume",
        "content": "The built-in speaker on my Daylight crackles and distorts when I play audio above 70% volume. I use it for listening to audiobooks and podcasts. It didn't do this when I first got it. Has anyone else reported this?\n\nOrder placed in November 2025.",
        "customer_email": "audiobook.lover@example.com",
        "status": "open",
    },
    {
        "title": "Can't download files from email attachments",
        "content": "When I try to download PDF attachments from my email, nothing happens. No error message, no download. I've tried in both the browser and the email app. I need to be able to download documents for my accounting work.\n\nPlease advise.",
        "customer_email": "accountant@example.com",
        "status": "open",
    },
    {
        "title": "Device running very hot during charging",
        "content": "My Daylight gets extremely hot when charging — almost too hot to hold. This didn't happen before. I'm worried about safety. I have two young kids at home and don't want to leave a potentially dangerous device charging overnight.\n\nShould I stop using it until this is resolved?",
        "customer_email": "worried.parent@example.com",
        "status": "open",
    },
    {
        "title": "Clock showing wrong timezone",
        "content": "My Daylight Computer clock is showing Pacific time but I'm in Eastern time zone (New York). I've set the timezone correctly in settings multiple times but it keeps reverting. Minor issue but annoying for scheduling.",
        "customer_email": "ny.timezone@example.com",
        "status": "open",
    },
    {
        "title": "Unable to connect to office VPN",
        "content": "I can't get my corporate VPN (Cisco AnyConnect) to work on the Daylight. Is there a compatible VPN client? I work in healthcare IT and need VPN access to do my job remotely. I specifically bought this device hoping it would work for both personal wellness and professional use.",
        "customer_email": "healthcare.it@example.com",
        "status": "open",
    },
    {
        "title": "Auto-rotate not working",
        "content": "The auto-rotate feature on my DC-1 stopped working. The screen stays in portrait mode no matter how I hold it. I've checked the settings and auto-rotate is enabled. I use landscape mode frequently for watching educational videos with my kids.\n\nAny fix for this?",
        "customer_email": "rotate.issue@example.com",
        "status": "open",
    },
    {
        "title": "Grateful for eye strain relief — minor camera question",
        "content": "Hi Daylight team!\n\nFirst, I want to say THANK YOU. I suffer from chronic migraines triggered by screen use, and your device has been life-changing. I can now work for 6+ hours without getting a headache. My neurologist is amazed.\n\nQuick question: does the DC-1 have a front-facing camera for video calls? I can't seem to find one.\n\nBest,\nRachel",
        "customer_email": "migraine.rachel@example.com",
        "status": "open",
    },
    {
        "title": "Help connecting to my car's Bluetooth",
        "content": "I'm trying to connect my Daylight to my car's Bluetooth system to play podcasts during my commute. It shows up in the car's device list but won't pair. I drive a 2024 Toyota Camry. I'm a real estate agent in Texas and spend a lot of time in the car between showings.\n\nAny suggestions?",
        "customer_email": "realtor.texas@example.com",
        "status": "open",
    },
    {
        "title": "Multiple user accounts?",
        "content": "Is it possible to set up multiple user accounts on one Daylight Computer? My wife and I want to share the device but keep our apps and files separate. We're both teachers and we'd each like our own workspace.\n\nIf not, is this planned for a future update?",
        "customer_email": "teacher.couple@example.com",
        "status": "open",
    },
    {
        "title": "Notification sounds not working",
        "content": "I'm not getting any notification sounds on my Daylight even though they're enabled in settings. I rely on calendar reminders for my therapy sessions (I'm a licensed therapist with a private practice). Missing notifications means missing appointment reminders.\n\nPlease help — this is urgent for my work.",
        "customer_email": "therapist@example.com",
        "status": "open",
    },
    {
        "title": "Impressed with build quality — one small issue",
        "content": "Hello,\n\nI'm a retired engineer and I have to say the build quality of the Daylight is impressive. The amber display is genuinely easier on my 68-year-old eyes. However, the power button feels a bit loose and wobbly. It still works, but it doesn't feel as solid as the rest of the device.\n\nIs this normal or should I be concerned about it failing?",
        "customer_email": "retired.engineer@example.com",
        "status": "open",
    },

    # --- Orders & Shipping (20 tickets) ---
    {
        "title": "Order confirmation not received",
        "content": "I placed an order about 2 hours ago but haven't received a confirmation email. I checked my spam folder too. My credit card was charged. Can you confirm my order went through?\n\nOrder should be under sarah.m@example.com",
        "customer_email": "sarah.m@example.com",
        "status": "open",
    },
    {
        "title": "Wrong address on my order",
        "content": "I just realized I entered my old address for my order. I moved to Oregon last month. Can you update the shipping address before it ships? Order #JAGAR-112700456.\n\nNew address:\n1234 Pine St\nPortland, OR 97201\n\nPlease hurry, I don't want it going to my old place!",
        "customer_email": "just.moved.or@example.com",
        "status": "open",
    },
    {
        "title": "When will my order ship?",
        "content": "Hi, I ordered a Daylight Computer 5 days ago and the status still says 'processing'. When can I expect it to ship? I'm buying it as a graduation gift for my daughter who finishes her nursing degree next week.\n\nOrder #JAGAR-112700789",
        "customer_email": "proud.parent@example.com",
        "status": "open",
    },
    {
        "title": "Duplicate charge on my credit card",
        "content": "I was charged TWICE for my Daylight Computer order. I see two identical charges of $729 on my Visa statement. I only placed one order. Please refund the duplicate charge immediately.\n\nOrder #JAGAR-112800123",
        "customer_email": "double.charge@example.com",
        "status": "open",
    },
    {
        "title": "Package delivered but box was empty",
        "content": "I received my Daylight Computer package today but the box was EMPTY. The outer shipping box was intact but the product box inside had nothing in it — no tablet, no cable, no documentation. This is unacceptable.\n\nOrder #JAGAR-112800456. I want this resolved today.",
        "customer_email": "empty.box@example.com",
        "status": "open",
    },
    {
        "title": "Can I add items to my existing order?",
        "content": "I just placed an order for the Daylight Computer and realized I forgot to add the protective case. Is it possible to add it to my existing order to save on shipping? Order #JAGAR-112800789.",
        "customer_email": "addon.request@example.com",
        "status": "open",
    },
    {
        "title": "International shipping to Canada?",
        "content": "Hello!\n\nI'm in Toronto, Canada and very interested in purchasing a Daylight Computer. Do you ship internationally? If so, what are the shipping costs and estimated delivery times to Canada?\n\nI'm an occupational therapist and I'd love to recommend this to some of my patients with light sensitivity issues too.\n\nThank you!",
        "customer_email": "ot.toronto@example.com",
        "status": "open",
    },
    {
        "title": "Tracking number not working",
        "content": "The tracking number in my shipping confirmation email shows 'not found' on the UPS website. It's been 3 days since I got the email. Is the tracking number correct?\n\nTracking: 1Z999AA10123456784\nOrder: #JAGAR-112900123",
        "customer_email": "tracking.issue@example.com",
        "status": "open",
    },
    {
        "title": "Package shows delivered but I never got it",
        "content": "UPS says my package was delivered yesterday but I never received it. I was home all day and nothing was at my door. I live in an apartment building in Chicago — could it have been delivered to the wrong unit?\n\nThis is a $729 device and I'm really worried. Order #JAGAR-112900456.",
        "customer_email": "chicago.missing@example.com",
        "status": "open",
    },
    {
        "title": "Need invoice for business expense",
        "content": "Hi,\n\nCan you send me a proper invoice for my Daylight Computer purchase? I need it for my business expense report. I'm a freelance consultant and this is a tax-deductible business expense.\n\nOrder #JAGAR-113000123\nBusiness name: Bright Ideas Consulting LLC\n\nThank you!",
        "customer_email": "consultant@example.com",
        "status": "open",
    },
    {
        "title": "Order stuck in customs",
        "content": "My order has been stuck in customs for over 2 weeks. I'm in Puerto Rico. The tracking hasn't updated since January 28th. Is this normal? I'm getting anxious — I bought this for my daughter who has ADHD and was hoping the reduced screen stimulation would help her focus on schoolwork.",
        "customer_email": "pr.customs@example.com",
        "status": "open",
    },
    {
        "title": "Request to cancel order before shipping",
        "content": "Hi, I'd like to cancel my order #JAGAR-113100456. I placed it yesterday but I've since decided to wait for the next model. If it hasn't shipped yet, please cancel and refund to my original payment method.\n\nThank you for understanding.",
        "customer_email": "cancel.request@example.com",
        "status": "open",
    },
    {
        "title": "Shipping damage — dented box",
        "content": "My Daylight Computer arrived today but the box is badly dented on one corner. The device seems to work fine for now, but I'm concerned about internal damage that might show up later. Should I exchange it for a new one? I have photos of the damage.\n\nOrder #JAGAR-113100789",
        "customer_email": "dented.box@example.com",
        "status": "open",
    },
    {
        "title": "Bulk order for our school district",
        "content": "Hello,\n\nI'm the technology coordinator for the Mesa Unified School District in Arizona. We're interested in purchasing 50 Daylight Computers for our special education program. Do you offer bulk pricing or institutional discounts?\n\nWe'd also need W-9 and purchase order capability.\n\nPlease get back to me at your earliest convenience.\n\nBest,\nDr. Patricia Gonzalez\nTechnology Coordinator, MUSD",
        "customer_email": "pgonzalez@musd.example.org",
        "status": "open",
    },
    {
        "title": "Gift wrapping available?",
        "content": "Hi! I'm ordering a Daylight Computer as a birthday gift for my husband. He's a writer who complains about eye strain constantly. Do you offer gift wrapping or at least the option to not include a receipt/invoice in the box?\n\nThanks!",
        "customer_email": "birthday.gift@example.com",
        "status": "open",
    },
    {
        "title": "Expedited shipping options?",
        "content": "I need a Daylight Computer delivered by Friday. What expedited shipping options do you have? I'm in Los Angeles. I have seasonal affective disorder and my therapist specifically recommended reducing blue light exposure. I'd really like to start using it this weekend.\n\nCost isn't an issue — just need it fast.",
        "customer_email": "sad.la@example.com",
        "status": "open",
    },
    {
        "title": "Received wrong model",
        "content": "I ordered the standard Daylight Computer but received the kids' version instead. I'm a 35-year-old software engineer — I definitely need the full-featured adult model!\n\nOrder #JAGAR-113300123. How do I exchange this?",
        "customer_email": "wrong.model@example.com",
        "status": "open",
    },
    {
        "title": "Military discount available?",
        "content": "Hello,\n\nI'm an active duty Army officer stationed at Fort Liberty, NC. Do you offer any military discounts? I'd like to purchase two Daylight Computers — one for myself and one for my wife. We're both trying to reduce screen time for better sleep, especially since I have an irregular schedule.\n\nThank you for your service to wellness!\n\nCPT James Rodriguez",
        "customer_email": "cpt.rodriguez@example.com",
        "status": "open",
    },
    {
        "title": "PayPal payment option?",
        "content": "Do you accept PayPal? I don't like entering my credit card info on websites. I'm a retiree on a fixed income in Michigan and I'm very cautious about online fraud.\n\nI've been wanting a Daylight Computer for months — the eye strain from my current tablet is terrible.",
        "customer_email": "cautious.retiree.mi@example.com",
        "status": "open",
    },
    {
        "title": "Delivery instructions for rural address",
        "content": "Hi, I live on a rural property in Montana and UPS sometimes has trouble finding my address. Can I add delivery instructions to my order? The best landmark is the red barn at the end of Elk Creek Road. My mailbox is another quarter mile past that.\n\nOrder #JAGAR-113400456\n\nI'm a rancher and there's not always cell service out here, so email is best.",
        "customer_email": "rancher.mt@example.com",
        "status": "open",
    },

    # --- Returns & Refunds (10 tickets) ---
    {
        "title": "Return request — not what I expected",
        "content": "Hi,\n\nI'd like to return my Daylight Computer. While the screen is nice, the device is slower than I expected for the price. I'm a video editor and it can't handle my workflow. I'm within the 30-day window.\n\nOrder #JAGAR-113500123",
        "customer_email": "video.editor@example.com",
        "status": "open",
    },
    {
        "title": "Exchange for kids' version",
        "content": "Hello! I bought the standard Daylight Computer but it's actually for my 10-year-old son. I just saw you have a kids' version. Can I exchange it? The device is still in the original packaging, never opened.\n\nOrder #JAGAR-113500456",
        "customer_email": "exchange.kids@example.com",
        "status": "open",
    },
    {
        "title": "Refund hasn't appeared yet",
        "content": "I returned my Daylight Computer 3 weeks ago and UPS confirms it was delivered to your warehouse on January 20th. I still haven't received my refund. When should I expect it?\n\nOriginal order #JAGAR-113500789\nReturn tracking: 1Z05R2W10399887766",
        "customer_email": "waiting.refund@example.com",
        "status": "open",
    },
    {
        "title": "Return shipping label request",
        "content": "I need to return my Daylight Computer but I can't find the return shipping label in my email. Can you resend it? I'm a senior citizen and not very tech-savvy, so step-by-step instructions would be appreciated.\n\nOrder #JAGAR-113600123\n\nThank you kindly,\nMargaret, age 74",
        "customer_email": "margaret74@example.com",
        "status": "open",
    },
    {
        "title": "Return policy question — opened but barely used",
        "content": "Hi, I've had my Daylight for about 25 days. I've used it maybe 5 times. I like it but I lost my job last week and need to cut expenses. Can I still return it since I'm within 30 days? It's in perfect condition.\n\nI hope to buy another one when things get better. Great product.",
        "customer_email": "financial.hardship@example.com",
        "status": "open",
    },
    {
        "title": "Damaged device received — want replacement not refund",
        "content": "My Daylight arrived with a cracked screen right out of the box. I don't want a refund — I really want this product. Can you send a replacement ASAP? I'm a teacher and bought this specifically for grading papers without eye strain.\n\nOrder #JAGAR-113700456\nPhotos attached.",
        "customer_email": "teacher.cracked@example.com",
        "status": "open",
    },
    {
        "title": "Returning a gift — no receipt",
        "content": "I received a Daylight Computer as a holiday gift but I already have one. I don't have the receipt or order number. Is there any way I can return or exchange it? The device is brand new, never opened, still in the shrink wrap.",
        "customer_email": "gift.return@example.com",
        "status": "open",
    },
    {
        "title": "Return request — bought for wrong person",
        "content": "I bought the kids' Daylight for my nephew but his parents already got him one. I'd like to return it. It's unopened and I'm within the return window. Order #JAGAR-113800123.\n\nCan you process this?",
        "customer_email": "uncle.return@example.com",
        "status": "open",
    },
    {
        "title": "Partial refund for missing accessories",
        "content": "My Daylight Computer arrived but the box was missing the charging cable and the quick start guide. The device itself is fine. Instead of returning the whole thing, can I get a partial refund or just have the missing items sent to me?\n\nOrder #JAGAR-113800456",
        "customer_email": "missing.accessories@example.com",
        "status": "open",
    },
    {
        "title": "Changed mind about return — want to keep it",
        "content": "Hi! I started a return process last week (case #RT-2026-0142) but I've changed my mind. After using the device more, I've actually really grown to love it. My insomnia has improved since switching to it for evening reading. Can you cancel the return?\n\nThank you!",
        "customer_email": "cancel.return@example.com",
        "status": "open",
    },

    # --- Feature Requests (15 tickets) ---
    {
        "title": "Dark mode for the entire OS",
        "content": "Love my Daylight! One request: can you add a system-wide dark mode? The amber display is great for reducing blue light but having a dark background option would be even better for nighttime use. I have astigmatism and bright backgrounds cause halos in my vision.\n\nThanks for making such a thoughtful product!",
        "customer_email": "dark.mode@example.com",
        "status": "open",
    },
    {
        "title": "Request: Kindle app support",
        "content": "I'd LOVE to have Kindle app support on the Daylight. I have hundreds of Kindle books and right now I have to use a separate Kindle device to read them. Having everything on one amber-light device would be a dream.\n\nI'm a retired librarian and I read about 4-5 books a week!",
        "customer_email": "librarian.kindle@example.com",
        "status": "open",
    },
    {
        "title": "Split screen / multitasking",
        "content": "Can you add split-screen multitasking? I'm a graduate student and I need to have a research paper open on one side and my notes on the other. Currently I have to keep switching between apps which breaks my focus.\n\nThis would make the Daylight perfect for academic work.",
        "customer_email": "grad.student@example.com",
        "status": "open",
    },
    {
        "title": "Parental controls and screen time limits",
        "content": "Would it be possible to add more robust parental controls? I have three kids (ages 6, 9, and 13) and I'd love to set per-child screen time limits, content restrictions, and usage reports. The kids' version has some controls but we're sharing a regular Daylight in our family.\n\nWe homeschool in rural Tennessee so this device has been great for education.",
        "customer_email": "homeschool.tn@example.com",
        "status": "open",
    },
    {
        "title": "Handwriting to text conversion",
        "content": "I use the stylus a LOT for taking notes in meetings. It would be incredible if you could add handwriting-to-text conversion. Even basic OCR of handwritten notes would save me hours of retyping.\n\nI'm a project manager at a tech company and I take notes in every meeting.",
        "customer_email": "pm.notes@example.com",
        "status": "open",
    },
    {
        "title": "Calendar widget for home screen",
        "content": "A simple calendar widget on the home screen would be really useful. I currently have to open the calendar app to see my schedule. As a busy ER doctor, I need to see my shifts at a glance.\n\nLove this device — it's the only screen that doesn't trigger my migraines after a 12-hour shift!",
        "customer_email": "er.doctor@example.com",
        "status": "open",
    },
    {
        "title": "Audio book player built-in",
        "content": "Any plans for a built-in audiobook player with Audible integration? I have a visual impairment and sometimes my eyes get too tired to read even on the Daylight's gentle display. Being able to switch between reading and listening seamlessly would be amazing.\n\nI'm 82 years old and this is the first tablet I've actually enjoyed using!",
        "customer_email": "senior.audiobook@example.com",
        "status": "open",
    },
    {
        "title": "Cloud sync for Reader app",
        "content": "Please add cloud sync for the Reader app! I want my bookmarks and reading progress to sync between my Daylight and my phone so I can pick up where I left off. Google Drive or Dropbox integration would work perfectly.\n\nI'm a travel journalist and I read on different devices depending on where I am.",
        "customer_email": "travel.journalist@example.com",
        "status": "open",
    },
    {
        "title": "Support for external monitor output",
        "content": "I'd love to be able to connect my Daylight to an external monitor via USB-C. Even if the external display doesn't have the amber light technology, it would be useful for presentations. I teach art history at a community college in New Mexico.\n\nWould this be technically possible?",
        "customer_email": "art.history.prof@example.com",
        "status": "open",
    },
    {
        "title": "Night mode schedule — auto amber intensity",
        "content": "Could you add an auto-schedule for amber intensity? Like, the screen could gradually increase amber tones as it gets closer to bedtime. Similar to Apple's Night Shift but more advanced. As someone with seasonal depression in Seattle, controlling my light exposure throughout the day would be huge.",
        "customer_email": "seattle.sad@example.com",
        "status": "open",
    },
    {
        "title": "E-ink mode for long reading sessions",
        "content": "Have you considered an e-ink-like mode that reduces the refresh rate and makes the display even more paper-like for extended reading? I regularly read for 4-5 hours straight (I'm a philosophy PhD student) and even with the amber display, a more static mode would reduce eye fatigue further.",
        "customer_email": "philosophy.phd@example.com",
        "status": "open",
    },
    {
        "title": "Annotation tools for PDF markup",
        "content": "The Reader app needs better annotation tools — highlighting, underlining, margin notes, and the ability to export annotated PDFs. I'm an attorney and I need to mark up legal documents daily. This one feature would make the Daylight my primary work device.\n\nCurrently I still have to use my iPad for document review, which defeats the purpose of reducing blue light.",
        "customer_email": "attorney.annotation@example.com",
        "status": "open",
    },
    {
        "title": "Offline maps app",
        "content": "An offline maps app would be incredibly useful. I'm a hiking guide in Colorado and I use my Daylight in the backcountry where there's no cell service. Being able to download trail maps for offline use would be a game-changer.\n\nThe sunlight-readable display already makes it the best device for outdoor use!",
        "customer_email": "hiking.guide.co@example.com",
        "status": "open",
    },
    {
        "title": "Better email client",
        "content": "The built-in email experience could use some work. I'd love to see a native email client with support for multiple accounts, better formatting, and calendar integration. I run a small interior design business from my Daylight and email is 50% of my daily workflow.",
        "customer_email": "interior.design@example.com",
        "status": "open",
    },
    {
        "title": "Password manager integration",
        "content": "Can you add support for password manager autofill? I use 1Password and it doesn't integrate with the Daylight's browser. I have to manually copy-paste every password which is tedious and defeats the purpose of a password manager.\n\nI'm a cybersecurity professional and this is a must-have for me.",
        "customer_email": "cybersec.pro@example.com",
        "status": "open",
    },

    # --- Warranty & Repairs (5 tickets) ---
    {
        "title": "Warranty claim — device won't turn on",
        "content": "My Daylight Computer completely died and won't turn on. I've tried charging it for 24 hours, different cables, different outlets — nothing works. The charging LED doesn't even light up. I bought it 8 months ago.\n\nI'm a stay-at-home dad with twins and this was my lifeline for staying sane during nap time. Please help.\n\nOrder #JAGAR-113900789",
        "customer_email": "sahd.twins@example.com",
        "status": "open",
    },
    {
        "title": "Screen separating from frame",
        "content": "The screen on my Daylight Computer is starting to separate from the frame on the left side. I can see a small gap forming. Is this covered under warranty? I've been very careful with the device — I'm a 60-year-old retired professor and it mostly sits on my reading desk.\n\nPurchased March 2025.",
        "customer_email": "professor.retired@example.com",
        "status": "open",
    },
    {
        "title": "Water damage — not covered but asking anyway",
        "content": "I accidentally spilled coffee on my Daylight. I know water damage probably isn't covered under warranty but I thought I'd ask. The screen works but there are some discolored spots now. I'm a journalist and this happened during a hectic morning trying to get the kids ready for school while writing a deadline piece.\n\nAny repair options?",
        "customer_email": "coffee.spill@example.com",
        "status": "open",
    },
    {
        "title": "Repair cost estimate",
        "content": "My DC-1 has a cracked screen from being sat on (don't ask). It still works but the crack is distracting. How much would an out-of-warranty screen repair cost? I'd rather fix it than buy a new one if the price is reasonable.\n\nI'm a college freshman on a tight budget.",
        "customer_email": "broke.freshman@example.com",
        "status": "open",
    },
    {
        "title": "Extended warranty purchase",
        "content": "Hi, is there an option to purchase an extended warranty? I just bought my Daylight and I'd like additional coverage beyond the standard warranty period. I tend to be hard on electronics (I'm a field researcher in marine biology and take my devices everywhere).\n\nThanks!",
        "customer_email": "marine.biologist@example.com",
        "status": "open",
    },

    # --- Partnerships & Business (5 tickets) ---
    {
        "title": "Wellness clinic partnership inquiry",
        "content": "Hi Daylight Team,\n\nI run a holistic wellness clinic in Sedona, Arizona. We specialize in treating patients with chronic fatigue, insomnia, and light sensitivity disorders. I believe the Daylight Computer aligns perfectly with our treatment philosophy.\n\nI'd love to explore a partnership where we recommend Daylight devices to our patients. We see about 200 patients per month. Is there a healthcare provider program or wholesale pricing?\n\nDr. Amanda Chen, ND\nDesert Light Wellness Center",
        "customer_email": "dr.chen@desertlight.example.com",
        "status": "open",
    },
    {
        "title": "EdTech conference sponsorship opportunity",
        "content": "Hello,\n\nI'm organizing the National EdTech Innovation Summit in Austin, TX this April. We're expecting 3,000 educators and would love to have Daylight as a sponsor. Given your focus on healthy technology, this would be a perfect audience for your products.\n\nSponsorship tiers range from $5K to $50K with various booth and speaking opportunities.\n\nLet me know if you're interested!\n\nBest,\nMichael Torres\nConference Director",
        "customer_email": "mtorres@edtechsummit.example.org",
        "status": "open",
    },
    {
        "title": "Bulk purchase for coworking space",
        "content": "Hey there!\n\nI own a coworking space in Brooklyn focused on wellness-minded professionals. We want to provide Daylight Computers at some of our hot desks as a unique amenity. Looking to purchase 15-20 units.\n\nDo you offer bulk discounts? Also, would you be interested in having your brand featured in our space? We get a lot of press coverage.\n\nCheers,\nAlex Rivera\nThe Mindful Desk",
        "customer_email": "alex@mindfuldesk.example.com",
        "status": "open",
    },
    {
        "title": "Press review unit request",
        "content": "Hi Daylight PR team,\n\nI'm a tech reviewer for The Verge with a focus on health tech and accessibility. I'd love to review the Daylight Computer for an upcoming piece on technology designed for wellness. My reviews typically reach 2-5 million readers.\n\nCould you send a review unit? Happy to provide my editor's contact for verification.\n\nThanks,\nLisa Park\nSenior Writer, The Verge",
        "customer_email": "lpark@theverge.example.com",
        "status": "open",
    },
    {
        "title": "Corporate wellness program inquiry",
        "content": "Good afternoon,\n\nI'm the VP of People at a mid-size tech company (450 employees). We're looking into providing Daylight Computers to employees who report screen-related health issues (headaches, eye strain, sleep disruption). Currently about 60 employees are in our accommodations program.\n\nDo you have a corporate program or enterprise pricing? We'd also need IT management capabilities.\n\nRegards,\nPriya Mehta\nVP of People, NovaTech Solutions",
        "customer_email": "priya.mehta@novatech.example.com",
        "status": "open",
    },

    # --- Feedback & Praise (10 tickets) ---
    {
        "title": "This device changed my life — thank you",
        "content": "I just wanted to write to say thank you. I have a traumatic brain injury from a car accident 3 years ago and screen sensitivity has been one of my worst symptoms. I couldn't use a computer for more than 20 minutes without debilitating headaches.\n\nWith the Daylight Computer, I can work for HOURS. I'm crying as I type this because I thought my career as a data analyst was over. You've given me my professional life back.\n\nThank you from the bottom of my heart.\n\nWith gratitude,\nDavid, age 34, Denver CO",
        "customer_email": "tbi.david@example.com",
        "status": "open",
    },
    {
        "title": "Five stars — best purchase this year",
        "content": "Just wanted to drop a note to say this is the best tech purchase I've made in years. The amber display is gorgeous, the build quality is excellent, and I'm sleeping so much better since I stopped using my iPad before bed.\n\nMy wife wants one now too!\n\n— Tom, 42, Portland",
        "customer_email": "happy.tom@example.com",
        "status": "open",
    },
    {
        "title": "Teacher testimonial — students love it",
        "content": "Hi Daylight team,\n\nI bought a Daylight for my special education classroom and my students with sensory processing disorders have responded incredibly well to it. The reduced visual stimulation helps them focus on reading without getting overwhelmed.\n\nI'd be happy to provide a testimonial if that would be useful for your marketing.\n\nMs. Jennifer Adams\n4th Grade Special Education\nElm Street Elementary, Iowa",
        "customer_email": "jadams.teacher@example.com",
        "status": "open",
    },
    {
        "title": "Sleeping better for the first time in years",
        "content": "I've had chronic insomnia for 8 years. My sleep doctor suggested reducing blue light exposure in the evenings. Since switching to the Daylight Computer for my after-dinner reading and browsing, I'm falling asleep 45 minutes faster on average.\n\nI'm a 55-year-old nurse practitioner in Minneapolis and I've started recommending your product to patients.\n\nThank you for making something that actually works!",
        "customer_email": "np.minneapolis@example.com",
        "status": "open",
    },
    {
        "title": "Impressed optometrist",
        "content": "Hi there,\n\nI'm an optometrist and I purchased a Daylight Computer out of professional curiosity. I'm genuinely impressed. The spectral output is significantly better for ocular health than standard displays. I've been recommending it to patients with digital eye strain.\n\nWould you be open to partnering with optometry practices? I'd love to display your product in my office waiting room.\n\nDr. Robert Kim, OD\nClear Vision Optometry, San Jose CA",
        "customer_email": "dr.kim.od@example.com",
        "status": "open",
    },
    {
        "title": "My elderly mother loves it",
        "content": "Just wanted to let you know that my 89-year-old mother who has been resistant to all technology for decades absolutely loves her Daylight Computer. She says it feels like reading a real book. She uses it daily now for reading the news and doing crossword puzzles.\n\nShe lives in an assisted living facility in Scottsdale and the other residents are asking about it!\n\nThank you for making technology accessible for seniors.",
        "customer_email": "grateful.daughter@example.com",
        "status": "open",
    },
    {
        "title": "ADHD focus improvement",
        "content": "I have severe ADHD and the reduced visual stimulation of the Daylight display has noticeably improved my ability to focus while reading. Regular tablets and computers are so visually 'loud' that they constantly pull my attention away from content.\n\nWith the Daylight, I finished reading a whole book in one sitting for the first time in my adult life. I'm 29.\n\nYou have a customer for life.",
        "customer_email": "adhd.focus@example.com",
        "status": "open",
    },
    {
        "title": "Podcast review — your team was great",
        "content": "Hi! I had your founder as a guest on my health tech podcast last week and the episode got amazing response. My listeners (mostly in the 30-50 age range, health-conscious professionals) are really interested in the product.\n\nJust wanted to say your team was wonderful to work with. Looking forward to doing a follow-up episode!\n\nBest,\nSamantha Liu\nHost, Healthy Signals Podcast\n~50K monthly listeners",
        "customer_email": "samantha@healthysignals.example.com",
        "status": "open",
    },
    {
        "title": "Using it in my therapy practice",
        "content": "I'm a psychologist specializing in adolescent screen addiction and I've started using the Daylight Computer in my practice. When I show teens that technology doesn't HAVE to be overstimulating, it opens up great conversations about their relationship with devices.\n\nSeveral parents have purchased Daylights for their kids as a result.\n\nDr. Nina Okafor\nChild & Adolescent Psychology\nAustin, TX",
        "customer_email": "dr.okafor@example.com",
        "status": "open",
    },
    {
        "title": "Artist review — the display is incredible for drawing",
        "content": "As a professional illustrator, I've used dozens of tablets over my 20-year career. The Daylight's display is unlike anything I've experienced — the paper-like quality makes drawing feel natural in a way that glossy screens never did.\n\nI've been working on it for 8-hour sessions with zero eye fatigue. My studio is in Savannah, GA and I've been telling every artist I know about this.\n\nBravo, Daylight team!",
        "customer_email": "illustrator.savannah@example.com",
        "status": "open",
    },

    # --- Billing & Account (5 tickets) ---
    {
        "title": "How to update my billing address",
        "content": "I need to update the billing address on my account. I recently moved from California to Nevada. Where can I change this?\n\nAlso, do I need to update anything for warranty purposes?",
        "customer_email": "ca.to.nv@example.com",
        "status": "open",
    },
    {
        "title": "Subscription charge I don't recognize",
        "content": "I see a recurring $4.99 charge from Daylight on my credit card statement. I only purchased the hardware — I don't recall signing up for any subscription. Can you check what this is and cancel it if it's not necessary?\n\nI'm on Social Security and every dollar matters.",
        "customer_email": "mystery.charge@example.com",
        "status": "open",
    },
    {
        "title": "Account login issues — forgot email",
        "content": "I can't remember which email I used to create my Daylight account. I've tried three different emails and none work. My order number is #JAGAR-114100789. Can you look up my account and tell me which email is associated?\n\nThanks,\nBrian",
        "customer_email": "brian.forgot@example.com",
        "status": "open",
    },
    {
        "title": "Price match request",
        "content": "I bought my Daylight Computer 2 weeks ago at full price ($729) and now I see it's on sale for $649. Can you price match or credit me the difference? This is really frustrating — I would have waited if I knew a sale was coming.\n\nOrder #JAGAR-114200123",
        "customer_email": "price.match@example.com",
        "status": "open",
    },
    {
        "title": "HSA/FSA eligible?",
        "content": "Hi,\n\nIs the Daylight Computer eligible for HSA or FSA purchase? My ophthalmologist recommended reducing blue light exposure for my chronic dry eye condition. If you can provide a Letter of Medical Necessity template, I can get my doctor to sign it.\n\nI'm a 45-year-old paralegal who spends 10+ hours a day on screens.\n\nThank you!",
        "customer_email": "hsa.question@example.com",
        "status": "open",
    },

    # --- Miscellaneous (5 tickets) ---
    {
        "title": "Interested in investing",
        "content": "Hi there,\n\nI'm a managing partner at Green Valley Ventures, a health-tech focused VC firm. We've been following Daylight's growth and are very impressed with the product and market positioning. I'd love to schedule a call with your leadership team to discuss potential investment opportunities.\n\nWe typically invest $2-10M in Series A/B rounds.\n\nBest regards,\nRobert Chen\nManaging Partner, Green Valley Ventures",
        "customer_email": "rchen@greenvalleyvc.example.com",
        "status": "open",
    },
    {
        "title": "Research collaboration — sleep study",
        "content": "Dear Daylight Team,\n\nI'm a sleep researcher at Stanford University School of Medicine. We're designing a clinical trial studying the effects of amber-light displays on sleep onset latency and sleep quality in patients with delayed sleep phase disorder.\n\nWe'd like to use Daylight Computers as the intervention device. Would you be interested in collaborating? We can provide published research data and academic credibility for your product claims.\n\nDr. Amy Watanabe, MD, PhD\nStanford Sleep Medicine Center",
        "customer_email": "awatanabe@stanford.example.edu",
        "status": "open",
    },
    {
        "title": "Daylight for visually impaired users",
        "content": "Hello,\n\nI work with the American Foundation for the Blind. Several of our members have expressed interest in the Daylight Computer's unique display properties. We'd love to learn more about accessibility features and potentially do a joint evaluation.\n\nAre there specific accessibility features built in (screen reader support, zoom, high contrast modes)?\n\nSincerely,\nCarla Washington\nTechnology Program Director\nAmerican Foundation for the Blind",
        "customer_email": "cwashington@afb.example.org",
        "status": "open",
    },
    {
        "title": "Lost my device — remote wipe?",
        "content": "I think I left my Daylight Computer at a coffee shop yesterday and when I went back it was gone. Is there any way to remotely lock or wipe it? I have personal documents and emails on it.\n\nI'm panicking — I'm a therapist and there might be patient notes on there.\n\nPlease help ASAP!",
        "customer_email": "lost.device@example.com",
        "status": "open",
    },
    {
        "title": "Recycling old device",
        "content": "Hi! I'm upgrading to a newer model and wondering if you have a recycling or trade-in program for old Daylight devices? I'm an environmental scientist and I'd hate to contribute to e-waste.\n\nIf not, any recommendations for responsible disposal?\n\nThanks,\nDr. Maya Patel\nEnvironmental Science, UC Davis",
        "customer_email": "dr.patel.enviro@example.com",
        "status": "open",
    },
]


def main():
    print(f"Ingesting {len(SAMPLE_TICKETS)} tickets to {BASE_URL}/api/v1/ingest ...")

    # Send in batches of 25 to avoid overwhelming the API
    batch_size = 25
    all_ids = []

    for i in range(0, len(SAMPLE_TICKETS), batch_size):
        batch = SAMPLE_TICKETS[i:i + batch_size]
        print(f"\n  Sending batch {i // batch_size + 1} ({len(batch)} tickets)...")

        response = httpx.post(
            f"{BASE_URL}/api/v1/ingest",
            json={"tickets": batch},
            timeout=30.0,
        )
        response.raise_for_status()

        data = response.json()
        all_ids.extend(data["ticket_ids"])
        print(f"  Accepted: {len(data['ticket_ids'])} ticket(s)")

    print(f"\nDone! {len(all_ids)} tickets queued for LLM processing.")
    print("LLM processing will take several minutes for 100 tickets.")
    print(f"Monitor progress via: docker compose logs app --follow")
    print(f"When complete, check: {BASE_URL}/api/v1/tickets")


if __name__ == "__main__":
    main()
