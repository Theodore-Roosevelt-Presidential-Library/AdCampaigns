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
VERT = {"gtDTwBMTn2Q": "resolute", "qrwdZmqFO5A": "trailblazer", "yEEsRy7sdng": "river-of-doubt", "-mcN1M3ZEps": "in-the-room", "k3U8V1HmKDs": "arena"}
def yt(vid, dur, title):
    m = {"type": "video", "src": f"creative/video/yt_{vid}.jpg", "youtube": vid, "duration": dur, "title": title, "source": "TRPL Commercials playlist"}
    if vid in VERT:  # 9:16 version made with scripts/vertical.py, used in Stories/Reels
        m["vertical"] = {"src": f"creative/video/vertical/{VERT[vid]}-9x16.mp4", "poster": f"creative/video/vertical/{VERT[vid]}-9x16.jpg"}
    return m
def still(name): return {"type": "image", "src": f"creative/kennerly/{name}.jpg", "source": "Frame from the In the Room preview video"}
def prod(title, price, url, image): return {"type": "product", "title": title, "price": price, "url": url, "src": image, "source": "Shopify"}

DRIVE = "ND, SD, MT, MN, WY + Manitoba, Saskatchewan"
FAR = "MN (Twin Cities), CO (Denver), NE, IA, WI, IL, plus TX, CA, FL, AZ — the next-largest origin states after the drive market"
REGION = "250-mile radius of Medora (Dickinson, Bismarck, Williston, Minot, Glendive, Miles City)"
LOCAL = "120-mile radius of Medora"


# Spend modes (see llm.txt "Testing and budget protection"):
#  test  = run every ad at a fraction of the planned daily budget for test_days, judge on the
#          campaign's metric, pause losers, then scale winners. Unspent test money rolls into the
#          rest of the flight and the reserve.
#  burst = the moment is happening now or is about to pass (screenings, a closing exhibition,
#          Giving Tuesday, Museum Store Sunday). All ads live from day one, Advantage+ placements,
#          highest-volume bidding, spend the full budget.
TEST = lambda metric, target, days=7, frac=0.35: {"mode": "test", "test_days": days, "test_frac": frac, "metric": metric, "target": target}
BURST = lambda metric, why: {"mode": "burst", "metric": metric, "why": why}

C = []
def camp(**k): C.append(k); return k

# ======================= TICKETS & VISITS =======================
camp(id="tix-galleries", program="Tickets & visits", revenue=True, priority=1,
     name="TICKETS: Eight chapters, all indoors", objective="Sales", optimization="Landing page views → Purchase once the ACME pixel is live",
     start="2026-11-04", end="2027-01-19", budget=16000, spend=TEST("Cost per landing page view", "$1.50 or less"),
     why="Winter's best reason to come is inside: eight chapters of Theodore Roosevelt's life in immersive galleries — the Memory Train, the campfire at Elkhorn, San Juan Heights, the Amazon. The study's third-strongest message is 'you won't just read about history, you'll step into it.' Aimed at people within a day's drive.",
     audiences=[{"name": "Regional", "geo": REGION, "age": "25–70", "detail": "Broad (Advantage+ audience)", "share": 0.5},
                {"name": "Drive market", "geo": DRIVE, "age": "35–65", "detail": "Museums, history, family travel. ND is 41% of ticket buyers, MN 15%", "share": 0.5}],
     open_items=["Hours change Dec 1 (Wed–Sun, 9–4). Copy avoids hours so it works in both seasons.",
                 "Chapter names come from trlibrary.com/visit/exhibits/main; confirm each photo shows the gallery named on its card."],
     ads=[
        {"id": "gal-carousel", "name": "Eight chapters carousel", "format": "carousel",
         "primary": "Theodore Roosevelt's life in eight chapters, all under one roof. Ride the Memory Train, sit by the Elkhorn campfire and step into the Amazon. Plan 3½ hours.",
         "cta": "Book Now", "url": TIX,
         "cards": [{"media": img("memory-train"), "headline": "Ride the Memory Train", "desc": "The Badlands chapter"},
                   {"media": img("family-campfire"), "headline": "Sit by the campfire", "desc": "Stories from the ranch"},
                   {"media": img("target-practice"), "headline": "Try ranch life", "desc": "Target practice, brands, roundup"},
                   {"media": img("rough-riders-photo"), "headline": "Stand with the Rough Riders", "desc": "Photo station"},
                   {"media": img("white-house-gang"), "headline": "Join the White House Gang", "desc": "For kids who climb"},
                   {"media": img("arena-exhibit"), "headline": "Step into the Arena", "desc": "After the White House"},
                   {"media": img("amazon-gallery"), "headline": "Run the River of Doubt", "desc": "Immersive film"}]},
        {"id": "gal-trailblazer", "name": "Trailblazer video", "format": "video",
         "primary": "Follow your own path through the galleries with the Trailblazer. Eight chapters, all indoors, at the edge of the Badlands. Plan 3½ hours.",
         "headline": "History you step into", "desc": "Medora, North Dakota", "cta": "Book Now", "url": TIX,
         "media": yt("qrwdZmqFO5A", "1:21", "Your Journey Starts Here — The Trailblazer"), "verify": "Confirm how the Trailblazer is described to visitors"},
        {"id": "gal-holiday-guests", "name": "Holiday guests", "format": "image",
         "primary": "Family in town for the holidays? Bring them to the Library: campfire stories, the Rough Riders and the Amazon, all indoors.",
         "headline": "Plans for holiday guests", "desc": "Adults $26 · Youth $16", "cta": "Book Now", "url": TIX,
         "media": img("family-campfire-cabin"), "flight": "Dec 2–Jan 3"},
        {"id": "gal-memory-train", "name": "Memory Train", "format": "image",
         "primary": "Board the Memory Train and ride into the Badlands with a young Theodore Roosevelt. One of eight chapters inside the Library.",
         "headline": "All aboard the Memory Train", "desc": "Plan 3½ hours", "cta": "Book Now", "url": TIX,
         "media": img("memory-train-family")},
     ])

camp(id="tix-spring", program="Tickets & visits", revenue=True, priority=1,
     name="TICKETS: Spring break and Easter in the Badlands", objective="Sales", optimization="Landing page views",
     start="2026-12-29", end="2027-01-19", budget=10000, spend=TEST("Cost per landing page view", "$1.75 or less", days=5),
     why="Families start booking spring break and Easter trips in January (searches for the national park start climbing then). Pairs the galleries with Theodore Roosevelt National Park next door, the study's top message.",
     audiences=[{"name": "Families, drive market", "geo": DRIVE, "age": "30–55", "detail": "Parents, family travel, national parks", "share": 0.55},
                {"name": "Families, farther away", "geo": FAR, "age": "30–55", "detail": "Parents, road trips, national parks, American history", "share": 0.45}],
     open_items=["Spring hours (after Mar 1) aren't published yet.",
                 "Easter dates and school breaks vary; copy says 'spring break' and doesn't name a date."],
     ads=[
        {"id": "spring-family", "name": "Spring break family", "format": "image",
         "primary": "Spring break idea: Theodore Roosevelt's story in eight immersive chapters, with the national park named for him right next door. Plan 3½ hours at the Library.",
         "headline": "Spring break in the Badlands", "desc": "Adults $26 · Youth $16", "cta": "Book Now", "url": TIX,
         "media": img("kids-interactive")},
        {"id": "spring-carousel", "name": "A spring road trip", "format": "carousel",
         "primary": "Presidential history and the Badlands in one trip. Start at the Library, then drive the Scenic Loop in Theodore Roosevelt National Park.",
         "cta": "Book Now", "url": TIX,
         "cards": [{"media": img("kid-laughing"), "headline": "Morning at the Library", "desc": "Plan 3½ hours"},
                   {"media": img("rust-walls-golden"), "headline": "Afternoon in the park", "desc": "Next door in Medora"},
                   {"media": img("cuba-family"), "headline": "Stories kids remember", "desc": "Eight chapters"}]},
     ])

camp(id="tix-summer", program="Tickets & visits", revenue=True, priority=1,
     name="TICKETS: Plan your summer trip", objective="Sales", optimization="Purchase (ACME pixel) — Landing page views until the ticketing site fires the pixel",
     start="2026-12-03", end="2027-01-19", budget=24000, spend=TEST("Cost per landing page view", "$1.50 or less"),
     why="The summer trip is planned in winter. July and August each sold about 100,000 tickets, and visitors who live farther away decide early. Leads with the study's two strongest messages: history plus the raw beauty of the Badlands, and the Library as part of a regional journey with Mount Rushmore and Yellowstone. Summer photos are honest here because the ad sells a summer trip.",
     audiences=[{"name": "Drive market", "geo": DRIVE, "age": "30–65", "detail": "Parents, road trips, national parks, museums", "share": 0.40},
                {"name": "Farther away", "geo": FAR, "age": "35–70", "detail": "Interests: Theodore Roosevelt National Park, Yellowstone, Mount Rushmore, Glacier, RV travel, American history", "share": 0.45},
                {"name": "Warm audiences", "geo": "United States", "age": "18+", "detail": "50% video viewers, Page/IG engagers, site visitors 180 days", "share": 0.15}],
     open_items=["ACME must add GTM-N3888GS9 or pixel 1069854392776858 to access.trlibrary.com before Purchase optimization works.",
                 "If the price increase is approved, add a 'lock in today's price' variant (needs Robbie/Chris sign-off)."],
     ads=[
        {"id": "sum-journey", "name": "The big Western road trip", "format": "carousel",
         "primary": "Mount Rushmore, Yellowstone, Theodore Roosevelt National Park, and the presidential library at the edge of the Badlands. Put it on this summer's route.",
         "cta": "Book Now", "url": TIX,
         "cards": [{"media": img("hero-badlands-wide"), "headline": "Presidential history meets the Badlands", "desc": "Medora, North Dakota"},
                   {"media": img("rough-riders-photo"), "headline": "Step into his story", "desc": "Eight immersive chapters"},
                   {"media": img("couple-overlook"), "headline": "Then head into the park", "desc": "Right next door"},
                   {"media": img("bikes-boardwalk"), "headline": "Stay for the evening light", "desc": "Plan 3½ hours"}],
         "sells": "summer"},
        {"id": "sum-hero", "name": "History + the Badlands", "format": "image",
         "primary": "Presidential history and the raw beauty of the Badlands, in one place. Timed tickets sell out on busy summer days, so pick your date early.",
         "headline": "Pick your summer day", "desc": "Adults $26 · Youth $16", "cta": "Book Now", "url": TIX,
         "media": img("overlook-visitors"), "sells": "summer"},
        {"id": "sum-video", "name": "Trailblazer video", "format": "video",
         "primary": "Eight chapters of Theodore Roosevelt's life, then the Badlands he loved right outside. Plan 3½ hours at the Library this summer.",
         "headline": "Your journey starts here", "desc": "Theodore Roosevelt Presidential Library", "cta": "Book Now", "url": TIX,
         "media": yt("qrwdZmqFO5A", "1:21", "Your Journey Starts Here — The Trailblazer"), "sells": "summer"},
     ])

# ======================= MEMBERSHIP & GIVING =======================
camp(id="mem-gift", program="Membership & giving", revenue=True, priority=1,
     name="MEMBERSHIP: Give a year at the Library", objective="Sales", optimization="Landing page views (Purchase once the ACME pixel is live)",
     start="2026-11-20", end="2027-01-19", budget=20000,
     spend=TEST("Cost per landing page view", "$2.00 or less", days=5),
     why="Gift memberships are the best holiday product the Library sells: $50–$1,000, no shipping cutoff, and they bring people back. Short test Nov 20–24, then full spend through Dec 24 (the gift window), then new-year joins.",
     audiences=[{"name": "Gift givers, national", "geo": "United States", "age": "35–70", "detail": "History, presidents, national parks, museum members", "share": 0.40},
                {"name": "Regional", "geo": DRIVE, "age": "30–70", "detail": "Broad", "share": 0.35},
                {"name": "Warm audiences", "geo": "United States", "age": "18+", "detail": "Video viewers, engagers, site visitors, past ticket buyers (hashed list, with OK)", "share": 0.25}],
     open_items=["Founding Member close date (Dec 31 per holiday plan) isn't on the membership page — confirm before using 'Founding' in copy.",
                 "Uploading the Constant Contact ticket-buyer list as a hashed Custom Audience needs Matt's OK."],
     ads=[
        {"id": "mem-gift-family", "name": "Gift — family membership", "format": "image",
         "primary": "A gift they'll use all year: free admissions, member discounts in the store and at Salt+Scoria, and a reason to come back to Medora. Family memberships are $175.",
         "headline": "Give a year at the Library", "desc": "Memberships from $50", "cta": "Give Now", "url": MEM,
         "media": img("family-gallery")},
        {"id": "mem-gift-carousel", "name": "Gift — pick a level", "format": "carousel",
         "primary": "Still shopping for someone who loves history or a good road trip? Give a Library membership.",
         "cta": "Give Now", "url": MEM,
         "cards": [{"media": img("cuba-pointing"), "headline": "Dual · $95", "desc": "2 admissions"},
                   {"media": img("kid-laughing"), "headline": "Family · $175", "desc": "4 admissions + programs"},
                   {"media": img("rough-riders-group"), "headline": "Contributing · $250", "desc": "6 admissions + welcome gift"},
                   {"media": img("arena-exhibit"), "headline": "Patron · $500", "desc": "Member magazine + more"}]},
        {"id": "mem-newyear", "name": "New year — join", "format": "image",
         "primary": "Start the year as a member of the Theodore Roosevelt Presidential Library. Free admissions and member pricing on everything else.",
         "headline": "Become a member", "desc": "From $50 a year", "cta": "Sign Up", "url": MEM,
         "media": img("memory-train"), "flight": "Jan 2–19"},
     ])

camp(id="give-yearend", program="Membership & giving", revenue=True, priority=1,
     name="GIVING: Giving Tuesday + year-end", objective="Sales", optimization="Landing page views on trlibrary.com/support-trpl (DonorPerfect form can't carry the pixel)",
     start="2026-11-24", end="2026-12-31", budget=14000,
     spend=BURST("Cost per landing page view", "Giving Tuesday and the last days of December are when gifts happen; there's no time to test."),
     why="Year-end is when most individual giving happens. The Library opened this summer and has a strong first-year story. Giving Tuesday (Dec 1) is online-only because the Library is closed Tuesdays.",
     audiences=[{"name": "Warm audiences", "geo": "United States", "age": "18+", "detail": "Video viewers, engagers, site visitors, members and donors (hashed list, with OK)", "share": 0.5},
                {"name": "Likely donors", "geo": "United States", "age": "45+", "detail": "American history, presidential libraries, charitable giving", "share": 0.5}],
     open_items=["Confirm year-end message and any match with Dan Muus before launch.",
                 "Copy stays about the Library, not policy, so it runs as a standard ad."],
     ads=[
        {"id": "give-gt", "name": "Giving Tuesday", "format": "image",
         "primary": "This Giving Tuesday, help keep the Library's doors open to students, families and first-time visitors. Every gift counts.",
         "headline": "Give on Giving Tuesday", "desc": "Theodore Roosevelt Presidential Library", "cta": "Donate Now", "url": GIVE,
         "media": img("kid-exhibit"), "flight": "Nov 24–Dec 1"},
        {"id": "give-ye", "name": "Year-end — first year", "format": "image",
         "primary": "The Library opened its doors in Medora this summer. Your year-end gift helps the next student, family and first-time visitor walk through them.",
         "headline": "Make a year-end gift", "desc": "Tax-deductible", "cta": "Donate Now", "url": GIVE,
         "media": img("kid-crafts"), "flight": "Dec 2–31"},
     ])

# ======================= RETAIL =======================
camp(id="shop-holiday", program="Retail", revenue=True, priority=2,
     name="RETAIL: Holiday gifts from the Library store", objective="Sales", optimization="Purchase (Shopify pixel + Conversions API) — Advantage+ catalog ads",
     start="2026-11-20", end="2026-12-18", budget=10000,
     spend=TEST("Cost per purchase (ROAS)", "ROAS 2.0 or better", days=5),
     why="Shopify sends purchases to the pixel with server-side events, so this campaign can optimize for real sales from day one. Short test, then a full-spend burst Nov 27–Dec 1 (Black Friday → Museum Store Sunday → Cyber Monday).",
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

# ======================= SALT+SCORIA =======================
camp(id="ss-private", program="Salt+Scoria", revenue=True, priority=3,
     name="SALT+SCORIA: Private dinners and holiday gatherings", objective="Leads", optimization="Instant form (name, email, date, party size) — or Landing page views on /private-events",
     start="2026-11-05", end="2026-12-15", budget=3500, spend=TEST("Cost per lead", "$40 or less", days=7, frac=0.5),
     why="Private dining is the restaurant's highest-value sale in the off-season: board retreats, holiday parties, rehearsal dinners, with menus by Chef Candace Stock.",
     audiences=[{"name": "Regional planners", "geo": REGION, "age": "28–65", "detail": "Business owners, event planning, engaged couples", "share": 1.0}],
     open_items=["Who receives leads, and how fast? (Instant form leads sit in Meta's Leads Center unless connected to email.)",
                 "Capacity and minimums for the dining room and plaza aren't published."],
     ads=[
        {"id": "ss-private-dinner", "name": "Private dinner", "format": "image",
         "primary": "Host your holiday party, board retreat or rehearsal dinner at Salt+Scoria, inside the Library, with the Badlands out the window. Menus by Chef Candace Stock.",
         "headline": "Private dining at Salt+Scoria", "desc": "Medora, North Dakota", "cta": "Get Quote", "url": EVENTS,
         "media": ss("dsc00636-2")},
     ])

camp(id="ss-cafe", program="Salt+Scoria", revenue=True, priority=4,
     name="SALT+SCORIA: Lunch at the Library", objective="Awareness", optimization="Reach in a tight radius",
     start="2026-11-04", end="2027-01-19", budget=1500, spend=BURST("Reach and frequency", "Tiny local radius; a test would never gather enough data."),
     why="Puts the café in front of people already in Medora, Dickinson and the park. Wood-fired, seasonal food.",
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

# ======================= EVENTS =======================
camp(id="evt-room", program="Events", revenue=True, priority=1,
     name="EVENTS: In the Room — David Hume Kennerly, final weeks", objective="Sales", optimization="Landing page views",
     start="2026-11-04", end="2027-01-10", budget=8000,
     spend=BURST("Cost per landing page view", "On view now and closes Jan 10. Every week it runs is a week it can sell tickets."),
     why="Sixty years of photographs from inside the biggest moments in American history, open through January 10. A temporary exhibition with a deadline is the strongest reason for someone who's already been to come back this winter, and it's all indoors.",
     audiences=[{"name": "Regional", "geo": REGION, "age": "25–75", "detail": "Broad", "share": 0.45},
                {"name": "Drive market", "geo": DRIVE, "age": "30–75", "detail": "Photography, photojournalism, history, news", "share": 0.35},
                {"name": "Past visitors", "geo": "United States", "age": "18+", "detail": "Site visitors, engagers, past ticket buyers (hashed list, with OK)", "share": 0.20}],
     open_items=["Starts Nov 4: the photographs show presidents, so it waits out Meta's Oct 27–Nov 3 political-ad window. Copy names no president.",
                 "Stills are frames from the preview video. Ask for a few high-res exhibition photos (no recognizable presidents front and center).",
                 "Closing date is Jan 10 per the exhibits page and the video end card."],
     ads=[
        {"id": "room-video", "name": "Exhibition preview", "format": "video",
         "primary": "Sixty years behind the camera at the biggest moments in American history. In the Room: Photographs by David Hume Kennerly closes January 10.",
         "headline": "See In the Room before it closes", "desc": "Included with admission", "cta": "Book Now", "url": TIX,
         "media": yt("-mcN1M3ZEps", "1:23", "In the Room: Photographs by David Hume Kennerly")},
        {"id": "room-still", "name": "In the gallery", "format": "image",
         "primary": "Pulitzer Prize-winning photographer David Hume Kennerly spent sixty years in the room where history happened. His photographs are at the Library through January 10.",
         "headline": "In the Room, through Jan. 10", "desc": "Included with admission", "cta": "Book Now", "url": TIX,
         "media": still("room-51"), "verify": "Confirm 'Pulitzer Prize-winning' is used in the Library's exhibition copy"},
        {"id": "room-last-call", "name": "Last call", "format": "image",
         "primary": "Last weeks for In the Room. David Hume Kennerly's photographs close January 10. Plan 3½ hours for the exhibition and the galleries.",
         "headline": "Closes January 10", "desc": "Book a timed ticket", "cta": "Book Now", "url": TIX,
         "media": still("room-63"), "flight": "Dec 28–Jan 10"},
     ])

camp(id="evt-holiday", program="Events", revenue=False, priority=2,
     name="EVENTS: The Library at Christmas", objective="Traffic", optimization="Landing page views",
     start="2026-11-18", end="2026-12-23", budget=5000,
     spend=BURST("Cost per landing page view", "Decorations are up Nov 17 to Christmas. A five-week window doesn't leave room for a test."),
     why="Decorations go up Nov 15–16. Pairs with TRMF's Old Fashioned Cowboy Christmas in Medora and with Museum Store Sunday.",
     audiences=[{"name": "Regional", "geo": REGION, "age": "25–70", "detail": "Broad", "share": 1.0}],
     open_items=["Swap in photos from the holiday shoot (Nov 17 onward). Current image is a placeholder.",
                 "Confirm Cowboy Christmas dates with TRMF before naming it."],
     ads=[
        {"id": "evt-holiday-decor", "name": "Decked out for the holidays", "format": "image",
         "primary": "The Library is dressed for the holidays. Make it part of your Cowboy Christmas weekend in Medora, and plan 3½ hours to see it all.",
         "headline": "Christmas at the Library", "desc": "Medora, North Dakota", "cta": "Book Now", "url": TIX,
         "media": img("store-interior"), "placeholder": True},
     ])

A = "creative/events/atb/"
ATB_TRAILER = {"type": "video", "src": A + "trailer-16x9.jpg", "file": A + "trailer-16x9.mp4", "duration": "0:48",
               "title": "America the Beautiful trailer (captioned)", "source": "Film's media kit (MPEG Film, Google Drive) — distributor end card trimmed",
               "feed": {"src": A + "trailer-4x5.jpg", "file": A + "trailer-4x5.mp4", "ratio": "4/5"},
               "vertical": {"src": A + "trailer-9x16.mp4", "poster": A + "trailer-9x16.jpg"}}
def atb(name): return {"type": "image", "src": A + name + ".jpg", "source": "Film's media kit (MPEG Film, Google Drive)"}

camp(id="evt-film", program="Events", revenue=True, priority=3,
     name="EVENTS: America the Beautiful film screenings", objective="Sales", optimization="Landing page views",
     start="2026-11-05", end="2026-11-24", budget=3000,
     spend=BURST("Cost per landing page view", "Screenings run Nov 11–25 only."),
     why="Paid screenings in the auditorium of a giant-screen nature film narrated by Kelsey Grammer. Uses the distributor's captioned trailer (their 'now playing in IMAX' end card cut off, since the Library is the venue) and their poster. Starts after the Nov 3 political-ad window because the film touches the conservation movement.",
     audiences=[{"name": "Regional", "geo": REGION, "age": "25–70", "detail": "Nature films, national parks, outdoors", "share": 1.0}],
     open_items=["The event page lists two prices ($7/$5 and $7.35/$5.25). Fix before ads point there.",
                 "Confirm with the distributor (MPEG Film) that the Library may run its trailer and poster in paid social, trimmed.",
                 "The poster shows Mount Rushmore and '250th anniversary' copy. Keep the ad text about the film, not politics, so it isn't flagged as a social-issue ad."],
     ads=[
        {"id": "evt-film-trailer", "name": "Trailer", "format": "video",
         "primary": "Mountains, plains, rivers and wetlands on the Library's big screen. America the Beautiful: Our Natural Wonders, narrated by Kelsey Grammer. Nov. 11–25 in Medora.",
         "headline": "America the Beautiful, Nov. 11–25", "desc": "Afternoon and evening shows", "cta": "Get Tickets", "url": FILM,
         "media": ATB_TRAILER},
        {"id": "evt-film-poster", "name": "Poster", "format": "image",
         "primary": "A giant-screen tour of America's natural wonders, narrated by Kelsey Grammer, at the Library Nov. 11–25. Afternoon and evening shows.",
         "headline": "See it on the big screen", "desc": "Theodore Roosevelt Presidential Library", "cta": "Get Tickets", "url": FILM,
         "media": atb("poster-4x5")},
        {"id": "evt-film-scenes", "name": "Scenes from the film", "format": "carousel",
         "primary": "Rivers, elk country and wetlands at sunset, the way they were made to be seen. America the Beautiful plays at the Library Nov. 11–25.",
         "cta": "Get Tickets", "url": FILM,
         "cards": [{"media": atb("river-aerial"), "headline": "America the Beautiful", "desc": "Nov. 11–25"},
                   {"media": atb("elk-meadow"), "headline": "Narrated by Kelsey Grammer", "desc": "Giant screen"},
                   {"media": atb("wetland-sunset"), "headline": "Afternoon and evening shows", "desc": "Medora, North Dakota"}]},
     ])

camp(id="evt-ffh", program="Events", revenue=False, priority=4,
     name="EVENTS: Free final hour", objective="Awareness", optimization="Reach",
     start="2026-11-04", end="2027-01-19", budget=2000,
     spend=BURST("Reach", "Local radius; reach campaigns don't benefit from a creative test at this size."),
     why="Neighbors who've never been inside. A free first look turns into paid visits and memberships.",
     audiences=[{"name": "Local", "geo": LOCAL, "age": "18+", "detail": "Broad", "share": 1.0}],
     open_items=["NEH credit line must appear in the ad text if the free hour is grant-funded (confirm with Julianna)."],
     ads=[
        {"id": "evt-ffh-local", "name": "A free first look", "format": "image",
         "primary": "Live nearby? The last hour before close is free with a timed ticket. It's a first look, not the whole visit; a full visit takes about 3½ hours. " + NEH,
         "headline": "The last hour is free", "desc": "Reserve a timed ticket", "cta": "Learn More", "url": FFH,
         "media": img("campfire-room")},
     ])

# ======================= BRAND & AUDIENCE BUILDING =======================
camp(id="brand-video", program="Brand & audience building", revenue=False, priority=2,
     name="BRAND: Step into the story (video)", objective="Engagement", optimization="ThruPlay",
     start="2026-10-28", end="2027-01-19", budget=13000,
     spend=TEST("Cost per ThruPlay", "$0.03 or less", days=7, frac=0.5),
     why="Cheap video views at national scale. Builds the 50%-viewer audiences that the ticket, membership and giving campaigns retarget. Indoor commercials only for the winter; the study found awareness alone lifts interest by 22 points.",
     audiences=[{"name": "National", "geo": "United States", "age": "25–70", "detail": "American history, national parks, road trips, Theodore Roosevelt", "share": 0.5},
                {"name": "Drive market", "geo": DRIVE, "age": "25–70", "detail": "Broad", "share": 0.5}],
     open_items=["Vertical versions are auto-reframed (Trailblazer, River of Doubt, In the Room) or letterboxed over a blurred fill (Resolute, Arena, whose text is burned in). A 15-second edit made for vertical would beat both."],
     ads=[
        {"id": "brand-resolute", "name": "Resolute (0:31)", "format": "video",
         "primary": "Theodore Roosevelt, in his own words, at the edge of the Badlands where his story turned. Medora, North Dakota.",
         "headline": "Theodore Roosevelt Presidential Library", "desc": "Plan a visit", "cta": "Learn More", "url": T + "/visit",
         "media": yt("gtDTwBMTn2Q", "0:31", "\"Resolute\" — Theodore Roosevelt in His Own Words")},
        {"id": "brand-amazon", "name": "River of Doubt (0:53)", "format": "video",
         "primary": "Step into the Amazon with Theodore Roosevelt. The River of Doubt is one of eight chapters inside the Library.",
         "headline": "Step into the Amazon", "desc": "Medora, North Dakota", "cta": "Learn More", "url": T + "/visit",
         "media": yt("yEEsRy7sdng", "0:53", "Step Into the Amazon: Theodore Roosevelt's River of Doubt Comes Alive")},
        {"id": "brand-trailblazer", "name": "Trailblazer (1:21)", "format": "video",
         "primary": "You won't just read about Theodore Roosevelt here. You'll step into his story, chapter by chapter.",
         "headline": "History you step into", "desc": "Medora, North Dakota", "cta": "Learn More", "url": T + "/visit",
         "media": yt("qrwdZmqFO5A", "1:21", "Your Journey Starts Here — The Trailblazer")},
     ])

camp(id="brand-birthday", program="Brand & audience building", revenue=False, priority=3,
     name="BRAND: TR's birthday card (Oct 27)", objective="Engagement", optimization="Landing page views",
     start="2026-10-26", end="2026-10-31", budget=1500,
     spend=BURST("Cost per landing page view", "Six-day moment around Oct 27."),
     why="The sign-a-card launch on TR's birthday ends in a membership ask and email opt-in. Builds the house file.",
     audiences=[{"name": "National", "geo": "United States", "age": "25+", "detail": "American history, Theodore Roosevelt", "share": 1.0}],
     open_items=["Landing URL for the card isn't set (card.labs embed on trlibrary.com?).",
                 "Launching Oct 26 gets an impression in before Meta's Oct 27–Nov 3 window, in case the 'wishes for the country' prompt gets classified as a social issue ad."],
     ads=[
        {"id": "brand-birthday-card", "name": "Sign the card", "format": "image",
         "primary": "Theodore Roosevelt was born October 27, 1858. Sign his birthday card and add your own wish for the country.",
         "headline": "Sign TR's birthday card", "desc": "Takes a minute", "cta": "Sign Up", "url": T,
         "media": img("elkhorn-campfire-stars")},
     ])

# ======================= RETARGETING =======================
camp(id="rt-allyear", program="Retargeting", revenue=True, priority=1,
     name="RETARGETING: Bring them back", objective="Sales", optimization="Landing page views → Purchase",
     start="2026-11-10", end="2027-01-19", budget=9000,
     spend=TEST("Cost per landing page view", "$1.00 or less", days=7, frac=0.4),
     why="Everyone the other campaigns warm up (video viewers, engagers, site and store visitors) sees the best offer for the season: Kennerly and gifts in Nov–Dec, spring break and summer in January.",
     audiences=[{"name": "Warm, all sources", "geo": "United States", "age": "18+", "detail": "50% video viewers 60d, IG/FB engagers 90d, site visitors 30d. Excludes purchasers 30d.", "share": 1.0}],
     open_items=["Audience size stays small until the video campaign has run 2–3 weeks; budget ramps after Nov 20."],
     ads=[
        {"id": "rt-roughriders", "name": "Come stand with the Rough Riders", "format": "image",
         "primary": "You've watched the story. Now step into it: eight chapters of Theodore Roosevelt's life, at the edge of the Badlands. Plan 3½ hours, and book your day ahead.",
         "headline": "Ready when you are", "desc": "Timed tickets", "cta": "Book Now", "url": TIX,
         "media": img("rough-riders-group")},
     ])

RESERVE = {"budget": 9500, "why": "Unassigned. Funds the winners of each test after week one and any burst that is delivering well, so the whole credit is spent by Jan 19. Test-phase savings roll in here too."}

GUARDRAILS = [
    "Every campaign gets a lifetime budget equal to its plan. Meta can't spend past it.",
    "Account spending limit set to $150,000 on TRPL FB Grant.",
    "No budget raised more than 30% in any 72 hours (lets Meta's learning settle).",
    "Test campaigns: each ad gets about $75 or 1,500 impressions before any call. Then pause ads whose cost per result is over 1.5× the campaign's best ad; keep the top two; scale by 25% every 3 days while they stay on target.",
    "Burst campaigns: all ads on from day one, Advantage+ placements, highest-volume bidding. If one delivers under target, move reserve into it the same day.",
    "Pause any ad with CTR under 0.4% after $100, or frequency over 4 a week in a regional audience.",
    "An agent checks the account every weekday morning, writes data/live.json, and posts changes for Matt's OK. No budget or status change without it.",
]

def days(a, b): return (dt.date.fromisoformat(b) - dt.date.fromisoformat(a)).days + 1
for c in C:
    c["status"] = "proposed"
    c["days"] = days(c["start"], c["end"])
    c["daily"] = round(c["budget"] / c["days"], 2)
    sp = c["spend"]
    if sp["mode"] == "test":  # low spend while testing, remainder spread over the rest of the flight
        td = min(sp["test_days"], c["days"] - 1); t_daily = round(c["daily"] * sp["test_frac"], 2)
        t_end = dt.date.fromisoformat(c["start"]) + dt.timedelta(days=td - 1)
        rest = round((c["budget"] - t_daily * td) / (c["days"] - td), 2)
        sp["decide_on"] = t_end.isoformat()
        c["schedule"] = [{"start": c["start"], "end": t_end.isoformat(), "daily": t_daily, "phase": "test"},
                         {"start": (t_end + dt.timedelta(days=1)).isoformat(), "end": c["end"], "daily": rest, "phase": "scale"}]
    else:
        c["schedule"] = [{"start": c["start"], "end": c["end"], "daily": c["daily"], "phase": "burst"}]
    for a in c["ads"]:
        a.setdefault("placements", ["fb_feed", "ig_feed", "ig_story"])
        sep = "&" if "?" in a["url"] else "?"
        a["tracked_url"] = f'{a["url"]}{sep}utm_source=meta&utm_medium=paid_social&utm_campaign={c["id"]}&utm_content={a["id"]}'

out = {"generated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "credit": CREDIT,
       "reserve": RESERVE, "guardrails": GUARDRAILS, "campaigns": C}
(ROOT / "data" / "campaigns.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
tot = sum(c["budget"] for c in C)
print(f"{len(C)} campaigns, {sum(len(c['ads']) for c in C)} ads, ${tot:,} planned + ${RESERVE['budget']:,} reserve = ${tot + RESERVE['budget']:,}")
