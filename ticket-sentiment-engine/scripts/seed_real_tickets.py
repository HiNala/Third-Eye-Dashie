#!/usr/bin/env python3
"""Seed script — ingests real sample ticket data for end-to-end testing."""

import httpx
import sys
import json

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"

SAMPLE_TICKETS = [
    {
        "title": "Ingestion failure with Daylight Capture extension",
        "content": 'Good afternoon\n\nI\'ve been getting "ingestion failure" when trying to use the Daylight capture extension. How do I fix it?',
        "customer_email": "ticket1@example.com",
        "status": "open",
    },
    {
        "title": "Order status update request",
        "content": "Hello,\n\nI placed an order and looking for an update. Thank you ORDER #JAGAR-112361649",
        "customer_email": "ticket2@example.com",
        "status": "open",
    },
    {
        "title": "Return request — within 30 days",
        "content": "Hi,\n\nI recently received my daylight computer and while I love the device, I realized I won't be able to use it with the software I'd need. I'd like to return it since I'm within the 30 days. It has no wear or signs of use whatsoever. Order number-112412749.",
        "customer_email": "ticket3@example.com",
        "status": "open",
    },
    {
        "title": "Reader app feedback — file management and folders",
        "content": "Hello,\n\nI LOVE the reader app, but I wanted to give some feedback because I'd love to have more functionality with organization of files. Is there a way to delete files from the reader? I only see a way to archive them, but there are some things that I open and read (or some pdfs that automatically open on the Reader app) that I don't need anymore after reading them once. I also have a couple files that somehow ended up on there twice, so deleting would really help me clean things up.\n\nAlso, I've added a couple files (maybe from websites?) via the Daylight Capture app that show up in the Reader as Untitled. Is there a way to rename them? I can't seem to find a way, but that would be really helpful for organization.\n\nAnd lastly, this is a bigger request, but eventually it would be amazing to be able to make different folders to organize different types of material or different topics.\n\nThanks so much!",
        "customer_email": "ticket4@example.com",
        "status": "open",
    },
    {
        "title": "DC-1 stuck in Google 2FA login loop",
        "content": "Hi, I recently tried to use my DC-1 after a while. It asked me to log into my google account, which is protected by a 2fa passkey in my icloud account. When I try to use it I get stuck in a loop—see attached video. How can I fix this? The dc-1 pretty much useless if I can't log in.",
        "customer_email": "ticket5@example.com",
        "status": "open",
    },
    {
        "title": "Kids Daylight questions — capabilities, apps, and ads",
        "content": "Hello,\n\nI purchased a daylight computer for my son during the Amber Light sale and not only is he happy with it, his younger brother is keen to have one as well.\n\nI see that you have released a daylight computer for 8-14 year olds. My 12 year old is concerned that the kid specific daylight will not be able to do everything that the regular one can. Aside from the specially curated controls, would he be limited or can he continue to use it as he gets older?\n\nAlso, are you able to specify some of the apps that are included to support learning?\n\nOne last question, the ads that pop up on my son's daylight are annoying. Is there an easy way to disable them? I went through the settings, but it wasn't obvious to me.",
        "customer_email": "ticket6@example.com",
        "status": "open",
    },
    {
        "title": "Arizona ESA purchase for two students",
        "content": "01/15/2026\nHi there!\n\nI have two Arizona ESA students I'd like to purchase tablets for. Can you let me know how to use the funds to purchase?\n\nThank you so much!\n\n...\n\n[Agent]\n01/16/2026\nHey [Customer],\n\nThanks for checking in with us, and I'd be happy to help out here!\n\nTo purchase using ESA in Arizona, we use the ClassWallet platform. I will send you 2 invoices, one for each student. Please download the invoices and upload them to ClassWallet. When ClassWallet approves the funds, we will fulfill the order.\n\nIn order to get the invoices started, I need some information:\n- The students' names\n- The address for delivery\n- Which age bundles did you want?\n\nOnce I have that information is provided, I'll get started on that right away.\n\nWarm regards,",
        "customer_email": "ticket7@example.com",
        "status": "open",
    },
    {
        "title": "Shipment stuck in Pennsylvania — angry customer",
        "content": "[Customer]\n01/26/2026\ngood morning\n\ni am emailing regarding the above order #.\nmy shipment seems to be stuck in Pennsylvania for the last several days.\nCan you check on the status of my order and when I should expect my shipment?\n\nthank you\n\n\n[Agent]\n01/26/2026\nHey [Customer],\n\nThanks for letting me know about the situation, and I'm sorry your package has been stuck! Unfortunately, there's a pretty big snowstorm happening in Pennsylvania right now. I don't think there's a way that UPS could re-route your package at the moment.\n\nWarm regards,\n\n...\n\n[Customer]\n01/26/2026\nThanks\n\nMy package was supposed to be delivered Friday — before the storm.\n\n...\n[Agent]\n01/29/2026\nHey [Customer],\n\nThanks for letting me know. Unfortunately, UPS gives us the same information that is listed on the tracking link itself. It looks like an investigation has opened for the package, and depending on the outcome, we can decide next steps.\n\nTalk soon,\n\n...\n[Agent]\n02/02/2026\nHey [Warehouse],\n\nThis package has been missing for a while. Is there anything we can do on our side to support this?\n[tracking link]\n\nThank you,\n\n...\n\n[Warehouse]\n02/03/2026\nHello,\n\nPlease see the email attached regarding this shipment.\n\nTracking 1Z05R2W10323705809",
        "customer_email": "ticket8@example.com",
        "status": "open",
    },
    {
        "title": "Frozen screen — warranty question",
        "content": "Hi I ordered a computer last year and my screen is frozen and wont work anymore. I love the computer and am super sad about this. Is there a warranty and do you replace if the computer malfunctions?\n\nOrder number was jagar-111322049",
        "customer_email": "ticket9@example.com",
        "status": "open",
    },
    {
        "title": "Future device lineup — phones, laptops, desktops?",
        "content": "Greetings!\n\nI am wondering if you plan to introduce other devices. Phones? Laptops? Desktop screens? I think all would be excellent ideas.\n\nThank you for your time and Happy Holiday Season to all of you and yours!",
        "customer_email": "ticket10@example.com",
        "status": "open",
    },
    {
        "title": "Partnership / affiliate program inquiry — YouTube creator",
        "content": "Jason\n01/15/2026\nHi Daylight Team,\n\nI tend to be a night owl, so I spend more time than I'd like wrapping up work in the evening. I learned about Daylight while researching blue light-minimizing tech for my own use case, but I think your product would be perfect for my audience as well.\n\nI've got a ~15k YouTube channel generating several million dollars in affiliate revenue annually from strategic product reviews. My audience is health-conscious tech enthusiasts aged 25-45. Based on my track record with similar products in the $500-1k range, I'm confident I could drive a ton of sales for your brand.\n\nWould I be welcome to participate in your affiliate program?\n\nHey Jason,\n\nThanks for reaching out and for sharing a bit about your work and audience - that sounds like a strong fit.\n\nSo, I'd love to invite you to apply to our affiliate program. You can find more details and submit an application here:\nAmbassador/Affiliate Application\n\nThanks again for getting in touch, and I can't wait to see what magic we create together!\n\nWith light,\nChristine",
        "customer_email": "jason.affiliate@example.com",
        "status": "open",
    },
    {
        "title": "Where to buy cover and accessories?",
        "content": "Hi,\n\nI purchased one of the Daylight Computers and was wondering where I can purchase the cover for it. Are there any other accessories available for it?\n\nThank you.",
        "customer_email": "ticket12@example.com",
        "status": "open",
    },
    {
        "title": "Job inquiry — education and program management background",
        "content": "Hey Jennifer,\n\nThank you so much for taking the time to write and for sharing your story. I really appreciate the care and intentionality you bring to how you think about technology, learning, and family life - it's very much in the spirit of why Daylight exists.\n\nWhile we're not actively hiring for roles aligned with your background at the moment, I'm grateful you reached out to introduce yourself. Your experience across education, program management, and remote collaboration is thoughtful and well-articulated, and it's always meaningful to hear from people who resonate with what we're building.\n\nI'd encourage you to keep an eye on our careers page as we grow, as new opportunities may open up in the future that are a better fit. In the meantime, thank you again for your kind words and for supporting more mindful approaches to technology, both for yourself and your children.\n\nWishing you all the best as you navigate this next chapter with your family.\n\nWarmly,\nChristine",
        "customer_email": "jennifer.job@example.com",
        "status": "closed",
    },
    {
        "title": "Job inquiry — homeschool parent, education and MBA background",
        "content": "Jan\n12/18/2025\nGood Afternoon,\n\nI just found your company and was looking over your website. I love the idea of a blue light free computer. I'm in a place now where I'm looking to reduce the \"noise\" in my life and the lives of my children. I've considered moving back to a \"dumb\" phone but have never considered that a healthier tablet/computer existed!\n\nAs a homeschool family we are extremely mindful of \"screen time\" and prioritize outdoor play and physical books. However, there are a lot of amazing resources online as well as books that we'd like to use that are only available through the library as an eBook. I also think it's important to expose our children to technology and teach them how to use it and healthy limits around it, which is difficult with so many overstimulating options. This seems like a unicorn product and I'm excited to see the company and product line expand! (I'd love a less stimulating TV screen in the future, perhaps with muted colors). I will definitely keep this in mind for our next tech refresh.\n\nAnyway, as I mentioned I'm looking to slow down and be more present for my family. I've been toying around with the idea of leaving my full time job in acquisitions for something part time with more flexible hours to focus on my family, so after reading about your product I clicked over to your careers link. I do not think I would be a good fit for the senior engineer job you have listed but I saw the note about reaching out to introduce myself, so here I am.\n\nI have a Bachelors of Science in Elementary Education and a Masters of Business Administration. I have dabbled in quite a few industries to include education, finance, acquisitions, and program management. With 10 years of experience working with teams disbursed across the country, 6 of those in an entirely remote capacity, I have proven my ability to meet goals and deadlines and exceed customer expectations with little oversight. My heart is in education and have a a mind for policy and regulations which translates well to roles in Training and Development, Instructional Design, Program & Project Management, etc.\n\nPlease keep me in mind for any opportunity for which you believe I would be a good fit.",
        "customer_email": "jan.job@example.com",
        "status": "closed",
    },
]


def main():
    print(f"Ingesting {len(SAMPLE_TICKETS)} real tickets to {BASE_URL}/api/v1/ingest ...")

    response = httpx.post(
        f"{BASE_URL}/api/v1/ingest",
        json={"tickets": SAMPLE_TICKETS},
        timeout=30.0,
    )
    response.raise_for_status()

    data = response.json()
    print(f"\nResponse: {json.dumps(data, indent=2)}")
    print(f"\nDone! {len(data['ticket_ids'])} tickets queued for LLM processing.")
    print("Wait ~30 seconds for background processing to complete, then check:")
    print(f"  {BASE_URL}/api/v1/tickets")


if __name__ == "__main__":
    main()
