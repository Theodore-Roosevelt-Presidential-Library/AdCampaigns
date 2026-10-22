#!/usr/bin/env python3
"""Source of truth for PROPOSED campaigns. Edit this file, then run:
    python3 scripts/plan.py      # writes data/campaigns.json
    python3 scripts/validate.py  # checks budgets, copy rules, media paths
Nothing here touches Meta. Campaigns go live only when Matt approves one by name
and an agent creates it (paused) through the Meta Ads connector; see llm.txt."""
import json, datetime as dt, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
CREDIT = {"total": 150000, "expires": "2027-01-20", "account_id": "960679053196120",
          "account_name": "TRPL FB Grant", "pixel_id": "1069854392776858",
          "page": "Theodore Roosevelt Presidential Library", "page_id": "144035749389560",
          "instagram": "trlibrary", "instagram_id": "17841426268646366"}

T = "https://www.trlibrary.com"
TIX = T + "/tickets"
MEM = "https://access.trlibrary.com/membership/613/join"
GIVE = T + "/support-trpl"
SHOP = "https://shop.trlibrary.com"
EVENTS = T + "/private-events"
FILM = T + "/calendar/special-event/america-beautiful-film-screening"
FFH = T + "/calendar/daily-activity/free-final-hour"
ROOM = T + "/calendar/daily-activity/room-sixty-years-front-lines-history"
NEH = "Selected exhibits and tours are made possible in part by a major grant from the National Endowment for the Humanities."

def img(slug): return {"type": "image", "src": f"creative/dam/{slug}.jpg", "source": "Acquia DAM"}
def ss(slug): return {"type": "image", "src": f"creative/saltscoria/{slug}.jpg", "source": "Salt+Scoria site (TRPL)"}
def yt(vid, dur, title): return {"type": "video", "src": f"creative/video/yt_{vid}.jpg", "youtube": vid, "duration": dur,
                                 "title": title, "source": "TRPL Commercials playlist"}
def prod(title, price, url, image): return {"type": "product", "title": title, "price": price, "url": url, "src": image, "source": "Shopify"}

DRIVE = "ND, SD, MT, MN, WY + Manitoba, Saskatchewan"
REGION = "250-mile radius of Medora (Dickinson, Bismarck, Williston, Minot, Glendive, Miles City)"
LOCAL = "120-mile radius of Medora"

C = []
def camp(**k): C.append(k); return k

# ---------------- TICKETS & VISITS (revenue) ----------------
camp(id="tix-summer", program="Tickets & visits", revenue=True, priority=1,
     name="TICKETS: Plan your summer trip", objective="Sales", optimization="Purchase (ACME pixel) — falls back to Landing page views until the ticketing site fires the pixel",
     start="2026-12-03", end="2027-01-19", budget=32000,
     why="Biggest revenue lever. Summer trips to the Badlands are planned in winter, and the 2027 ticket launch lands in early December. Drive-market families and national-park travelers are the core buyers.",
     audiences=[{"name": "Drive market", "geo": DRIVE, "age": "28–65", "detail": "Parents, road trips, national parks, museums", "share": 0.45},
                {"name": "National park travelers", "geo": "United States", "age": "35–70", "detail": "Interests: Theodore Roosevelt National Park, Yellowstone, Glacier, Black Hills, RV travel, American history", "share": 0.40},
                {"name": "Warm audiences", "geo": "United States", "age": "18+", "detail": "50% video viewers, Page/IG engagers, site visitors 180 days", "share": 0.15}],
     open_items=["ACME must add GTM-N3888GS9 or pixel 1069854392776858 to access.trlibrary.com before Purchase optimization works.",
                 "If the price increase is approved, add a 'lock in today's price' variant (needs Robbie/Chris sign-off)."],
     ads=[
        {"id": "tix-summer-carousel", "name": "A 3½-hour visit, card by card", "format": "carousel",
         "primary": "Give yourself 3½ hours at the edge of the Badlands. Sit by the campfire at Elkhorn, stand with the Rough Riders, and watch the light change over the canyon.",
         "cta": "Book Now", "url": TIX,
         "cards": [{"media": img("overlook-visitors"), "headline": "Start at the canyon's edge", "desc": "Medora, North Dakota"},
                   {"media": img("family-campfire"), "headline": "Sit by TR's ranch fire", "desc": "Elkhorn gallery"},
                   {"media": img("rough-riders-photo"), "headline": "Join the Rough Riders", "desc": "Photo op inside"},
                   {"media": img("amazon-gallery"), "headline": "Step into the Amazon", "desc": "River of Doubt"},
                   {"media": img("boardwalk-walk"), "headline": "Walk the boardwalk", "desc": "Out over the Badlands"}]},
        {"id": "tix-summer-hero", "name": "Hero image — summer planning", "format": "image",
         "primary": "Summer in the Badlands starts with a plan. Timed tickets sell out on busy days, so pick your date now and build the rest of the trip around it.",
         "headline": "Pick your day at the Library", "desc": "Adults $26 · Youth $16", "cta": "Book Now", "url": TIX,
         "media": img("hero-badlands-wide")},
        {"id": "tix-summer-video", "name": "Trailblazer video", "format": "video",
         "primary": "Follow your own path through the galleries with the Trailblazer. Plan 3½ hours, then head out into the park.",
         "headline": "Your journey starts here", "verify": "Confirm how the Trailblazer is described to visitors", "desc": "Theodore Roosevelt Presidential Library", "cta": "Book Now", "url": TIX,
         "media": yt("qrwdZmqFO5A", "1:21", "Your Journey Starts Here — The Trailblazer")},
     ])

camp(id="tix-winter", program="Tickets & visits", revenue=True, priority=2,
     name="TICKETS: Winter days in the Badlands", objective="Sales", optimization="Landing page views → Purchase when ACME pixel is live",
     start="2026-12-02", end="2027-01-19", budget=9000,
     why="Winter visits come from within driving distance. Short trips, school breaks and holiday guests. Keeps the Library on the regional radar through the slow months.",
     audiences=[{"name": "Regional", "geo": REGION, "age": "25–65", "detail": "Broad, Advantage+ audience", "share": 1.0}],
     open_items=["Winter hours Dec 1–Mar 1: Wed–Sun, 9–4. Closed Dec 25 and Jan 1. Starts Dec 2 so the hours in the copy are right."],
     ads=[
        {"id": "tix-winter-terrace", "name": "Warm inside, wild outside", "format": "image",
         "primary": "The Badlands in winter, seen from a warm room with a wall of glass. Open Wednesday through Sunday, 9 to 4. Plan 3½ hours.",
         "headline": "A winter day trip to Medora", "desc": "Open Wed–Sun, 9–4", "cta": "Book Now", "url": TIX,
         "media": img("terrace-view")},
        {"id": "tix-winter-family", "name": "Holiday guests in town", "format": "image",
         "primary": "Family in town for the holidays? Bring them to the Library. Campfire stories, the Rough Riders and a view nobody forgets.",
         "headline": "Plans for holiday guests", "desc": "Tickets for every age", "cta": "Book Now", "url": TIX,
         "media": img("family-campfire-cabin")},
     ])

# ---------------- MEMBERSHIP & GIVING (revenue) ----------------
camp(id="mem-gift", program="Membership & giving", revenue=True, priority=1,
     name="MEMBERSHIP: Give a year in the Badlands", objective="Sales", optimization="Landing page views (membership join is on access.trlibrary.com — Purchase once ACME pixel is live)",
     start="2026-11-20", end="2027-01-19", budget=20000,
     why="Gift memberships are the best holiday product the Library sells: $50–$1,000, no shipping cutoff, and they convert to future visits. Two flights: gifts Nov 20–Dec 24, then new-year joins.",
     audiences=[{"name": "Gift givers, national", "geo": "United States", "age": "35–70", "detail": "History, presidents, national parks, museum members", "share": 0.45},
                {"name": "Regional", "geo": DRIVE, "age": "30–70", "detail": "Broad", "share": 0.30},
                {"name": "Warm audiences", "geo": "United States", "age": "18+", "detail": "Video viewers, engagers, site visitors, past ticket buyers (CC list, hashed)", "share": 0.25}],
     open_items=["Founding Member window close date (Dec 31 per holiday plan) is not on the membership page — confirm before using 'Founding' in copy.",
                 "Uploading the Constant Contact ticket-buyer list as a hashed Custom Audience needs Matt's OK."],
     ads=[
        {"id": "mem-gift-family", "name": "Gift — family membership", "format": "image",
         "primary": "A gift they'll use all year: free admission, member discounts in the store and at Salt+Scoria, and a reason to come back to Medora. Family memberships are $175.",
         "headline": "Give a year at the Library", "desc": "Memberships from $50", "cta": "Give Now", "url": MEM,
         "media": img("family-gallery")},
        {"id": "mem-gift-carousel", "name": "Gift — pick a level", "format": "carousel",
         "primary": "Still shopping for the person who loves history, national parks or a good road trip? Give a Library membership.",
         "cta": "Give Now", "url": MEM,
         "cards": [{"media": img("couple-overlook"), "headline": "Dual · $95", "desc": "2 admissions"},
                   {"media": img("kid-laughing"), "headline": "Family · $175", "desc": "4 admissions + programs"},
                   {"media": img("overlook-group"), "headline": "Contributing · $250", "desc": "6 admissions + welcome gift"},
                   {"media": img("couple-sunset"), "headline": "Patron · $500", "desc": "Member magazine + more"}]},
        {"id": "mem-newyear", "name": "New year — join", "format": "image",
         "primary": "Start the year as a member of the Theodore Roosevelt Presidential Library. Free admission all year and member pricing on everything else.",
         "headline": "Become a member", "desc": "From $50 a year", "cta": "Sign Up", "url": MEM,
         "media": img("aerial-overlook"), "flight": "Jan 2–19"},
     ])

camp(id="give-yearend", program="Membership & giving", revenue=True, priority=1,
     name="GIVING: Giving Tuesday + year-end", objective="Sales", optimization="Landing page views on trlibrary.com/support-trpl (DonorPerfect form can't carry the pixel)",
     start="2026-11-24", end="2026-12-31", budget=14000,
     why="Year-end is when most individual giving happens. The Library opened this summer and has a strong first-year story to tell. Giving Tuesday (Dec 1) is online-only because the Library is closed Tuesdays.",
     audiences=[{"name": "Warm audiences", "geo": "United States", "age": "18+", "detail": "Video viewers, engagers, site visitors, members and donors (hashed list, with OK)", "share": 0.5},
                {"name": "Likely donors", "geo": "United States", "age": "45+", "detail": "American history, presidential libraries, charitable giving", "share": 0.5}],
     open_items=["Confirm year-end message and any match with Dan Muus before launch.",
                 "Copy stays about the Library, not policy, so it runs as a standard ad (no special ad category)."],
     ads=[
        {"id": "give-gt", "name": "Giving Tuesday", "format": "image",
         "primary": "This Giving Tuesday, help keep the Library's doors open to students, families and first-time visitors. Every gift counts.",
         "headline": "Give on Giving Tuesday", "desc": "Theodore Roosevelt Presidential Library", "cta": "Donate Now", "url": GIVE,
         "media": img("kid-exhibit"), "flight": "Nov 24–Dec 1"},
        {"id": "give-ye", "name": "Year-end — first year", "format": "video",
         "primary": "The Library opened its doors in Medora this summer. Your year-end gift helps the next student, family and first-time visitor walk through them.",
         "headline": "Make a year-end gift", "desc": "Tax-deductible", "cta": "Donate Now", "url": GIVE,
         "media": yt("W9sq8PuGQVo", "3:35 → cut to 0:30", "Discover the Theodore Roosevelt Presidential Library"), "flight": "Dec 2–31"},
     ])

# ---------------- RETAIL (revenue) ----------------
camp(id="shop-holiday", program="Retail", revenue=True, priority=2,
     name="RETAIL: Holiday gifts from the Library store", objective="Sales", optimization="Purchase (Shopify pixel + Conversions API) — Advantage+ catalog ads",
     start="2026-11-20", end="2026-12-18", budget=10000,
     why="Shopify now sends purchases to the pixel with server-side events, so this is the one campaign that can optimize for real sales from day one. Includes a Black Friday → Museum Store Sunday (Nov 29) push.",
     audiences=[{"name": "Prospecting", "geo": "United States", "age": "25–65", "detail": "Advantage+ shopping; outdoor apparel, Filson, Orvis, history", "share": 0.65},
                {"name": "Warm audiences", "geo": "United States", "age": "18+", "detail": "Shop visitors, add-to-cart, engagers", "share": 0.35}],
     open_items=["Only 18 products are online. Exclude low stock from the catalog set: Slate backpack (2), Thor bottle (4), Green trucker hat (0).",
                 "Museum Store Sunday offer not set yet (discount, perk or gift-with-purchase).",
                 "The Shopify catalog shows up on the personal ad account (18555278); share it to TRPL FB Grant before launch.",
                 "Set a shipping cutoff date and end the campaign then."],
     ads=[
        {"id": "shop-catalog", "name": "Catalog carousel", "format": "catalog",
         "primary": "Gifts from the Library store in Medora, shipped to your door. Every purchase supports the Library.",
         "cta": "Shop Now", "url": SHOP,
         "products": [prod("The Roosevelt Signature Hoodie | Black", "$64.99", SHOP + "/products/the-roosevelt-signature-hoodie-black", "https://cdn.shopify.com/s/files/1/0786/3998/8979/files/TRPL-signature-hoodie-front.png?v=1792510396"),
                      prod("Authentic Bully! Hat | Navy", "$54.99", SHOP + "/products/navy-bully-hat", "https://cdn.shopify.com/s/files/1/0786/3998/8979/files/TRPL_BullyHat_FRONT-2.png?v=1774030410"),
                      prod("Blue Chambray Men's Tech Shirt by Orvis", "$89.99", SHOP + "/products/mens-blue-chambray-tech-short-sleeve-shirt-by-orvis", "https://cdn.shopify.com/s/files/1/0786/3998/8979/files/TRPL_OrvisMen_sBlueChambrayShirt_FRONT.png?v=1773943958"),
                      prod("Ice Blue, Arena Quote T-shirt", "$29.99", SHOP + "/products/ice-blue-arena-quote-t-shirt-s", "https://cdn.shopify.com/s/files/1/0786/3998/8979/files/TRPL_IceBlueArenaTshirt_FRONT.png?v=1773943881"),
                      prod("Limited Edition Filson Tin Cloth Compact Briefcase", "$369.00", SHOP + "/products/filson-tin-cloth-compact-briefcase", "https://cdn.shopify.com/s/files/1/0786/3998/8979/files/TRPL_Filson_Tin_Cloth_Compact_FRONT.png?v=1773943469"),
                      prod("TRPL Cream/Black/Loden Hat", "$34.99", SHOP + "/products/trpl-cream-loden-hat", "https://cdn.shopify.com/s/files/1/0786/3998/8979/files/TRPL_LodenCreamHat_FRONT-2.png?v=1774030510")]},
        {"id": "shop-lifestyle", "name": "Store lifestyle", "format": "image",
         "primary": "Hats, tees, Filson bags and Orvis shirts made for the Library. Order online for the holidays.",
         "headline": "Shop the Library store", "desc": "Ships nationwide", "cta": "Shop Now", "url": SHOP,
         "media": img("store-shopping")},
        {"id": "shop-msd", "name": "Museum Store Sunday", "format": "image",
         "primary": "Sunday, Nov. 29 is Museum Store Sunday. Shop the Library store online or in Medora and support the Library with every purchase.",
         "headline": "Museum Store Sunday", "desc": "Online and in Medora", "cta": "Shop Now", "url": SHOP,
         "media": img("store-interior"), "flight": "Nov 27–29"},
     ])

# ---------------- SALT+SCORIA ----------------
camp(id="ss-private", program="Salt+Scoria", revenue=True, priority=3,
     name="SALT+SCORIA: Private dinners and holiday gatherings", objective="Leads", optimization="Instant form (name, email, date, party size) — or Landing page views on /private-events",
     start="2026-11-05", end="2026-12-15", budget=3500,
     why="Private dining is the restaurant's highest-value sale in the off-season: board retreats, holiday parties, rehearsal dinners, with menus by Chef Candace Stock.",
     audiences=[{"name": "Regional planners", "geo": REGION, "age": "28–65", "detail": "Business owners, event planning, engaged couples", "share": 1.0}],
     open_items=["Who receives leads, and how fast? (Instant form sends to Meta's Leads Center unless connected to email.)",
                 "Capacity and minimums for the dining room and plaza aren't published."],
     ads=[
        {"id": "ss-private-dinner", "name": "Private dinner", "format": "image",
         "primary": "Host your holiday party, board retreat or rehearsal dinner at Salt+Scoria, inside the Library, with the Badlands out the window. Menus by Chef Candace Stock.",
         "headline": "Private dining at Salt+Scoria", "desc": "Medora, North Dakota", "cta": "Get Quote", "url": EVENTS,
         "media": ss("dsc00636-2")},
     ])

camp(id="ss-cafe", program="Salt+Scoria", revenue=True, priority=4,
     name="SALT+SCORIA: Lunch with a Badlands view", objective="Awareness", optimization="Reach in a tight radius",
     start="2026-11-04", end="2027-01-19", budget=1500,
     why="Puts the café in front of people already in Medora, Dickinson and the park. Wood-fired, seasonal food, no ticket needed for the café (confirm).",
     audiences=[{"name": "Nearby", "geo": "40-mile radius of Medora + people traveling in the area", "age": "18+", "detail": "Broad", "share": 1.0}],
     open_items=["Confirm café access without an admission ticket and winter café hours."],
     ads=[
        {"id": "ss-cafe-chili", "name": "TR's venison chili", "format": "carousel",
         "primary": "Wood-fired, seasonal food at the Library: TR's venison chili, smoked salmon salad, fresh pastries and good coffee.",
         "cta": "Learn More", "url": "https://www.saltandscoria.com/menu",
         "cards": [{"media": ss("trpl-saltscoria_general-026"), "headline": "TR's Venison Chili", "desc": "$9.50"},
                   {"media": ss("trpl-saltscoria_general-034"), "headline": "Three Sisters salad", "desc": "Smoked salmon"},
                   {"media": ss("trpl-saltscoria_general-033"), "headline": "Wood-fired plates", "desc": "Seasonal"},
                   {"media": ss("dsc00885"), "headline": "Lunch to go", "desc": "Order at the counter"}]},
     ])

# ---------------- EVENTS ----------------
camp(id="evt-holiday", program="Events", revenue=False, priority=2,
     name="EVENTS: The Library at Christmas", objective="Traffic", optimization="Landing page views",
     start="2026-11-18", end="2026-12-23", budget=5000,
     why="Decorations go up Nov 15–16. Pairs with TRMF's Old Fashioned Cowboy Christmas in Medora and with Museum Store Sunday.",
     audiences=[{"name": "Regional", "geo": REGION, "age": "25–70", "detail": "Broad", "share": 1.0}],
     open_items=["Swap in photos from the holiday shoot (Nov 17 onward). Current images are placeholders.",
                 "Confirm Cowboy Christmas dates with TRMF before naming it."],
     ads=[
        {"id": "evt-holiday-decor", "name": "Decked out for the holidays", "format": "image",
         "primary": "The Library is dressed for the holidays. Make it part of your Cowboy Christmas weekend in Medora, and plan 3½ hours to see it all.",
         "headline": "Christmas at the Library", "desc": "Medora, North Dakota", "cta": "Book Now", "url": TIX,
         "media": img("mainguest-arrival"), "placeholder": True},
     ])

camp(id="evt-film", program="Events", revenue=True, priority=3,
     name="EVENTS: America the Beautiful film screenings", objective="Sales", optimization="Landing page views",
     start="2026-11-05", end="2026-11-24", budget=3000,
     why="Paid screenings Nov 11–25 in the auditorium, made for the giant screen. Starts after the Nov 3 election window because the film touches the conservation movement.",
     audiences=[{"name": "Regional", "geo": REGION, "age": "25–70", "detail": "Nature films, national parks, outdoors", "share": 1.0}],
     open_items=["The event page lists two prices ($7/$5 and $7.35/$5.25). Fix before ads point there."],
     ads=[
        {"id": "evt-film-hero", "name": "On the big screen", "format": "image",
         "primary": "Mountains, plains, rivers and wetlands on the Library's big screen. America the Beautiful: Our Natural Wonders, narrated by Kelsey Grammer. Nov. 11–25.",
         "headline": "America the Beautiful", "desc": "Afternoon and evening shows", "cta": "Get Tickets", "url": FILM,
         "media": img("hero-prairie-sky")},
     ])

camp(id="evt-room", program="Events", revenue=False, priority=3,
     name="EVENTS: In the Room — last weeks", objective="Traffic", optimization="ThruPlay → Landing page views",
     start="2026-11-05", end="2027-01-10", budget=4000,
     why="The David Hume Kennerly exhibition closes Jan 11. A built-in deadline and a strong preview video.",
     audiences=[{"name": "Regional", "geo": REGION, "age": "25–70", "detail": "Broad", "share": 0.6},
                {"name": "Photography fans", "geo": DRIVE, "age": "25–70", "detail": "Photojournalism, documentary photography", "share": 0.4}],
     open_items=["Copy avoids naming presidents so Meta doesn't classify it as a political ad.", "Confirm the last day: the calendar feed ends Jan 11 (exclusive), so the last day may be Jan 10."],
     ads=[
        {"id": "evt-room-video", "name": "Exhibition preview", "format": "video",
         "primary": "Sixty years behind the camera at the biggest moments in American history. In the Room: Photographs by David Hume Kennerly is in its final weeks.",
         "headline": "See In the Room before it closes", "desc": "Included with admission", "cta": "Book Now", "url": TIX,
         "media": yt("-mcN1M3ZEps", "1:23", "In the Room: Photographs by David Hume Kennerly")},
     ])

camp(id="evt-ffh", program="Events", revenue=False, priority=4,
     name="EVENTS: Free final hour", objective="Awareness", optimization="Reach",
     start="2026-11-04", end="2027-01-19", budget=2000,
     why="Neighbors who've never been inside. A free first look turns into paid visits and memberships. Reach only, small budget, local radius.",
     audiences=[{"name": "Local", "geo": LOCAL, "age": "18+", "detail": "Broad", "share": 1.0}],
     open_items=["NEH credit line must appear in the ad text if the free hour is grant-funded (confirm with Julianna)."],
     ads=[
        {"id": "evt-ffh-local", "name": "A free first look", "format": "image",
         "primary": "Live nearby? The last hour before close is free with a timed ticket. It's a first look, not the whole visit; a full visit takes about 3½ hours. " + NEH,
         "headline": "The last hour is free", "desc": "Reserve a timed ticket", "cta": "Learn More", "url": FFH,
         "media": img("terrace-crowd")},
     ])

# ---------------- BRAND & AUDIENCE BUILDING ----------------
camp(id="brand-video", program="Brand & audience building", revenue=False, priority=2,
     name="BRAND: Discover the Library (video)", objective="Engagement", optimization="ThruPlay",
     start="2026-10-28", end="2027-01-19", budget=24000,
     why="Cheap video views at national scale. Builds the 50%-viewer audiences that the ticket, membership and giving campaigns retarget. Uses the commercials as they are.",
     audiences=[{"name": "National", "geo": "United States", "age": "25–70", "detail": "American history, national parks, road trips, Theodore Roosevelt", "share": 0.6},
                {"name": "Drive market", "geo": DRIVE, "age": "25–70", "detail": "Broad", "share": 0.4}],
     open_items=["Reels/Stories need 9:16 cuts of the commercials; the mockups crop the 16:9 frames."],
     ads=[
        {"id": "brand-resolute", "name": "Resolute (0:31)", "format": "video",
         "primary": "Theodore Roosevelt, in his own words, at the edge of the Badlands where his story turned. Medora, North Dakota.",
         "headline": "Theodore Roosevelt Presidential Library", "desc": "Plan a visit", "cta": "Learn More", "url": T + "/visit",
         "media": yt("gtDTwBMTn2Q", "0:31", "\"Resolute\" — Theodore Roosevelt in His Own Words")},
        {"id": "brand-amazon", "name": "River of Doubt (0:53)", "format": "video",
         "primary": "Step into the Amazon with Theodore Roosevelt. The River of Doubt gallery is one of the stops on a 3½-hour visit to the Library.",
         "headline": "Step into the Amazon", "desc": "Medora, North Dakota", "cta": "Learn More", "url": T + "/visit",
         "media": yt("yEEsRy7sdng", "0:53", "Step Into the Amazon: Theodore Roosevelt's River of Doubt Comes Alive")},
        {"id": "brand-boardwalk", "name": "The boardwalk (1:34)", "format": "video",
         "primary": "Walk out over the Badlands on the Library's boardwalk. It's included with admission, and the view changes with every season.",
         "headline": "Walk the Badlands", "desc": "Included with admission", "cta": "Learn More", "url": T + "/visit",
         "media": yt("zRPJAdE-IBI", "1:34", "Walking the Badlands Without Leaving the Trail — The TR Library Boardwalk")},
     ])

camp(id="brand-birthday", program="Brand & audience building", revenue=False, priority=3,
     name="BRAND: TR's birthday card (Oct 27)", objective="Engagement", optimization="Landing page views",
     start="2026-10-26", end="2026-10-31", budget=1500,
     why="The sign-a-card launch on TR's birthday ends in a membership ask and email opt-in. Builds the house file.",
     audiences=[{"name": "National", "geo": "United States", "age": "25+", "detail": "American history, Theodore Roosevelt", "share": 1.0}],
     open_items=["Landing URL for the card isn't set (card.labs embed on trlibrary.com?).",
                 "Launching Oct 26 gets an impression in before Meta's Oct 27–Nov 3 window, in case the 'wishes for the country' prompt gets classified as a social issue ad."],
     ads=[
        {"id": "brand-birthday-card", "name": "Sign the card", "format": "image",
         "primary": "Theodore Roosevelt was born October 27, 1858. Sign his birthday card and add your own wish for the country.",
         "headline": "Sign TR's birthday card", "desc": "Takes a minute", "cta": "Sign Up", "url": T,
         "media": img("riders-on-prairie")},
     ])

# ---------------- RETARGETING ----------------
camp(id="rt-allyear", program="Retargeting", revenue=True, priority=1,
     name="RETARGETING: Bring them back", objective="Sales", optimization="Landing page views → Purchase",
     start="2026-11-10", end="2027-01-19", budget=9000,
     why="Everyone the other campaigns warm up (video viewers, engagers, site and store visitors) sees the best offer for the season: gifts and giving in Nov–Dec, summer tickets in January.",
     audiences=[{"name": "Warm, all sources", "geo": "United States", "age": "18+", "detail": "50% video viewers 60d, IG/FB engagers 90d, site visitors 30d. Excludes purchasers 30d.", "share": 1.0}],
     open_items=["Audience size will be small until the video campaign runs 2–3 weeks; budget ramps after Nov 20."],
     ads=[
        {"id": "rt-roughriders", "name": "Come stand with the Rough Riders", "format": "image",
         "primary": "You've seen the Badlands from your screen. Now come see them from the Library's terrace. Plan 3½ hours, and book your day ahead.",
         "headline": "Ready when you are", "desc": "Timed tickets", "cta": "Book Now", "url": TIX,
         "media": img("rough-riders-group")},
     ])

# ---------------- RESERVE ----------------
RESERVE = {"budget": 11500, "why": "Unassigned until the first two weeks of results. Goes to whichever revenue campaigns hit their targets, so the whole credit is spent by Jan 19."}

def days(a, b): return (dt.date.fromisoformat(b) - dt.date.fromisoformat(a)).days + 1
for c in C:
    c["status"] = "proposed"
    c["days"] = days(c["start"], c["end"])
    c["daily"] = round(c["budget"] / c["days"], 2)
    for a in c["ads"]:
        a.setdefault("placements", ["fb_feed", "ig_feed", "ig_story"])
        sep = "&" if "?" in a["url"] else "?"
        a["tracked_url"] = f'{a["url"]}{sep}utm_source=meta&utm_medium=paid_social&utm_campaign={c["id"]}&utm_content={a["id"]}'

out = {"generated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "credit": CREDIT,
       "reserve": RESERVE, "campaigns": C}
(ROOT / "data" / "campaigns.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
tot = sum(c["budget"] for c in C)
print(f"{len(C)} campaigns, {sum(len(c['ads']) for c in C)} ads, ${tot:,} planned + ${RESERVE['budget']:,} reserve = ${tot + RESERVE['budget']:,}")
