#!/usr/bin/env python3
"""Source of truth for PROPOSED campaigns. Edit this file, then run:
    python3 scripts/plan.py      # writes data/campaigns.json
    python3 scripts/validate.py  # checks budgets, copy rules, media paths
Nothing here touches Meta. Campaigns go live only when Matt approves one by name
and an agent creates it (paused) through the Meta Ads connector; see llm.txt."""
import pathlib, json, datetime as dt, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
WEBCAT = json.loads((ROOT / "creative" / "web" / "catalog.json").read_text())
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
    feed = f"creative/video/feed/yt_{vid}.mp4"   # the file that gets uploaded to Meta (feeds); see llm.txt
    if (pathlib.Path(__file__).resolve().parents[1] / feed).exists(): m["file"] = feed
    if vid in VERT:  # 9:16 version made with scripts/vertical.py, used in Stories/Reels
        m["vertical"] = {"src": f"creative/video/vertical/{VERT[vid]}-9x16.mp4", "poster": f"creative/video/vertical/{VERT[vid]}-9x16.jpg"}
    return m
def web(slug):  # partner/public photo in creative/web (source in creative/web/catalog.json)
    m = next(x for x in WEBCAT if x["file"].endswith(f"/{slug}.jpg"))
    return {"type": "image", "src": m["file"], "source": m["source"]}
def card(name, story=None, ratio="4/5"):  # brand graphic (scripts/brand_card.py) in creative/brand-cards
    m = {"type": "image", "src": f"creative/brand-cards/{name}.jpg", "source": "Brand card (Dharma Gothic + brand colors) on a trlibrary.com photo", "ratio": ratio}
    if story: m["story"] = f"creative/brand-cards/{story}.jpg"
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

V = T + "/visit"; IT = V + "/itineraries"
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
         "primary": "The new Theodore Roosevelt Presidential Library in Medora, North Dakota tells his life in eight immersive chapters. Ride the Memory Train into the Badlands, sit by the campfire at his Elkhorn Ranch and step into the Amazon. Plan 3½ hours.",
         "cta": "Book Now", "url": TIX,
         "cards": [{"media": img("memory-train"), "headline": "Ride the Memory Train", "desc": "The Badlands chapter"},
                   {"media": img("family-campfire"), "headline": "Sit by the campfire", "desc": "Stories from the ranch"},
                   {"media": img("target-practice"), "headline": "Try ranch life", "desc": "Target practice, brands, roundup"},
                   {"media": img("rough-riders-photo"), "headline": "Stand with the Rough Riders", "desc": "Photo station"},
                   {"media": img("white-house-gang"), "headline": "Join the White House Gang", "desc": "For kids who climb"},
                   {"media": img("arena-exhibit"), "headline": "Step into the Arena", "desc": "After the White House"},
                   {"media": img("amazon-gallery"), "headline": "Run the River of Doubt", "desc": "Immersive film"}]},
        {"id": "gal-trailblazer", "name": "Trailblazer video", "format": "video",
         "primary": "Meet the new Theodore Roosevelt Presidential Library in Medora, North Dakota: eight chapters of his life that you walk through, all indoors, at the edge of the Badlands. Plan 3½ hours.",
         "headline": "History you step into", "desc": "Medora, North Dakota", "cta": "Book Now", "url": TIX,
         "media": yt("qrwdZmqFO5A", "1:21", "Your Journey Starts Here — The Trailblazer"), "verify": "Confirm how the Trailblazer is described to visitors"},
        {"id": "gal-holiday-guests", "name": "Holiday guests", "format": "image",
         "primary": "Family in town for the holidays? Take them to the new Theodore Roosevelt Presidential Library in Medora, North Dakota: campfire stories, the Rough Riders and the Amazon, all indoors.",
         "headline": "Plans for holiday guests", "desc": "Adults $26 · Youth $16", "cta": "Book Now", "url": TIX,
         "media": img("family-campfire-cabin"), "flight": "Dec 2–Jan 3"},
        {"id": "gal-memory-train", "name": "Memory Train", "format": "image",
         "primary": "At the new Theodore Roosevelt Presidential Library in Medora, North Dakota, you board the Memory Train and ride into the Badlands with a young Theodore Roosevelt. It's one of eight chapters inside.",
         "headline": "All aboard the Memory Train", "desc": "Plan 3½ hours", "cta": "Book Now", "url": TIX,
         "media": img("memory-train-family")},
     ])

camp(id="tix-spring", program="Tickets & visits", revenue=True, priority=1,
     name="TICKETS: Spring break and Easter in the Badlands", objective="Sales", optimization="Landing page views",
     start="2026-12-29", end="2027-01-19", budget=8000, spend=TEST("Cost per landing page view", "$1.75 or less", days=5),
     why="Families start booking spring break and Easter trips in January (searches for the national park start climbing then). Pairs the galleries with Theodore Roosevelt National Park next door, the study's top message.",
     audiences=[{"name": "Families, drive market", "geo": DRIVE, "age": "30–55", "detail": "Parents, family travel, national parks", "share": 0.55},
                {"name": "Families, farther away", "geo": FAR, "age": "30–55", "detail": "Parents, road trips, national parks, American history", "share": 0.45}],
     open_items=["Spring hours (after Mar 1) aren't published yet.",
                 "Easter dates and school breaks vary; copy says 'spring break' and doesn't name a date."],
     ads=[
        {"id": "spring-see", "name": "Spring break: what you'll see", "format": "carousel",
         "primary": "Spring break idea: the new Theodore Roosevelt Presidential Library in Medora, an Old West town in the North Dakota Badlands. Eight chapters inside, and bison, wild horses and prairie dogs in the national park next door.",
         "cta": "Book Now", "url": TIX,
         "cards": [{"media": img("memory-train-family"), "headline": "Ride the Memory Train", "desc": "Inside the Library", "url": TIX},
                   {"media": img("family-campfire"), "headline": "Campfire stories", "desc": "At TR's Elkhorn Ranch", "url": TIX},
                   {"media": img("kids-interactive"), "headline": "Hands-on galleries", "desc": "For every age", "url": TIX},
                   {"media": web("bison-trnp"), "headline": "Bison next door", "desc": "In the national park", "url": V + "/national-park"},
                   {"media": web("bison-ridge-2"), "headline": "Bison on the ridgelines", "desc": "Along the scenic drive", "url": V + "/national-park"},
                   {"media": web("painted-canyon"), "headline": "Painted Canyon", "desc": "Your first view of the Badlands", "url": V + "/scenic-drives"}]},
        {"id": "spring-family", "name": "Spring break family", "format": "image",
         "primary": "Spring break idea: the new Theodore Roosevelt Presidential Library in Medora, an Old West town in the North Dakota Badlands, tells his story in eight immersive chapters. Next door, a national park full of bison and wild horses.",
         "headline": "Spring break in the Badlands", "desc": "Adults $26 · Youth $16", "cta": "Book Now", "url": TIX,
         "media": img("kids-interactive")},
        {"id": "spring-carousel", "name": "A spring road trip", "format": "carousel",
         "primary": "Presidential history and the Badlands in one trip. Start at the new Theodore Roosevelt Presidential Library in Medora, an Old West town in the North Dakota Badlands, then drive into Theodore Roosevelt National Park next door to see bison, wild horses and prairie dogs.",
         "cta": "Book Now", "url": TIX,
         "cards": [{"media": img("kid-laughing"), "headline": "Morning at the Library", "desc": "Plan 3½ hours"},
                   {"media": web("bison-trnp"), "headline": "Afternoon with the bison", "desc": "National park next door"},
                   {"media": img("cuba-family"), "headline": "Stories kids remember", "desc": "Eight chapters"}]},
     ])

camp(id="tix-summer", program="Tickets & visits", revenue=True, priority=1,
     name="TICKETS: Plan your summer trip", objective="Sales", optimization="Purchase (ACME pixel) — Landing page views until the ticketing site fires the pixel",
     start="2026-12-03", end="2027-01-19", budget=15000, spend=TEST("Cost per landing page view", "$1.50 or less"),
     why="The summer trip is planned in winter. July and August each sold about 100,000 tickets, and visitors who live farther away decide early. Leads with the study's two strongest messages: history plus the raw beauty of the Badlands, and the Library as part of a regional journey with Mount Rushmore and Yellowstone. Summer photos are honest here because the ad sells a summer trip.",
     audiences=[{"name": "Drive market", "geo": DRIVE, "age": "30–65", "detail": "Parents, road trips, national parks, museums", "share": 0.40},
                {"name": "Farther away", "geo": FAR, "age": "35–70", "detail": "Interests: Theodore Roosevelt National Park, Yellowstone, Mount Rushmore, Glacier, RV travel, American history", "share": 0.45},
                {"name": "Warm audiences", "geo": "United States", "age": "18+", "detail": "50% video viewers, Page/IG engagers, site visitors 180 days", "share": 0.15}],
     open_items=["ACME must add GTM-N3888GS9 or pixel 1069854392776858 to access.trlibrary.com before Purchase optimization works.",
                 "If the price increase is approved, add a 'lock in today's price' variant (needs Robbie/Chris sign-off)."],
     ads=[
        {"id": "sum-journey", "name": "The big Western road trip", "format": "carousel",
         "primary": "Headed to Mount Rushmore or Yellowstone? Add the North Dakota Badlands: the new Theodore Roosevelt Presidential Library in Medora, and the national park next door where bison and wild horses roam the land TR ranched. Put it on this summer's route.",
         "cta": "Book Now", "url": TIX,
         "cards": [{"media": img("hero-badlands-wide"), "headline": "Presidential history meets the Badlands", "desc": "Medora, North Dakota"},
                   {"media": img("rough-riders-photo"), "headline": "Step into his story", "desc": "Eight immersive chapters"},
                   {"media": web("bison-trnp"), "headline": "Then find bison in the Badlands", "desc": "Theodore Roosevelt National Park"},
                   {"media": img("bikes-boardwalk"), "headline": "Stay for the evening light", "desc": "Plan 3½ hours"}],
         "sells": "summer"},
        {"id": "sum-hero", "name": "History + the Badlands", "format": "image",
         "primary": "Presidential history and the raw beauty of the Badlands, in one place: the new Theodore Roosevelt Presidential Library in Medora, an Old West town in the North Dakota Badlands. Timed tickets sell out on busy summer days, so pick your date early.",
         "headline": "Pick your summer day", "desc": "Adults $26 · Youth $16", "cta": "Book Now", "url": TIX,
         "media": img("overlook-visitors"), "sells": "summer"},
        {"id": "sum-see", "name": "Everything you'll see this summer", "format": "carousel",
         "primary": "What a summer day in Medora, North Dakota looks like: bison and wild horses in the national park, Painted Canyon, a trail ride, steaks on pitchforks, the Medora Musical and the new Theodore Roosevelt Presidential Library.",
         "cta": "Book Now", "url": TIX, "sells": "summer",
         "cards": [{"media": web("bison-jam"), "headline": "Bison in the road", "desc": "The national park next door", "url": V + "/national-park"},
                   {"media": web("wild-horses"), "headline": "Wild horses", "desc": "Easier to spot than you'd think", "url": V + "/national-park"},
                   {"media": web("painted-canyon"), "headline": "Painted Canyon", "desc": "Right off I-94", "url": V + "/scenic-drives"},
                   {"media": web("library-gallery"), "headline": "Eight chapters inside", "desc": "Plan 3½ hours", "url": TIX},
                   {"media": web("library-rooftop"), "headline": "The rooftop boardwalk", "desc": "Out over the Badlands", "url": TIX},
                   {"media": web("trail-ride-sunset"), "headline": "Trail rides", "desc": "Into the Badlands", "url": V + "/activities"},
                   {"media": web("pitchfork-steaks"), "headline": "Pitchfork Steak Fondue", "desc": "Dinner with a view", "url": V + "/eat"},
                   {"media": web("musical-amphitheatre"), "headline": "The Medora Musical", "desc": "Summer nights outdoors", "url": V + "/medora"},
                   {"media": web("badlands-night-sky"), "headline": "Dark skies", "desc": "The Milky Way, overhead", "url": V + "/stargazing"}]},
        {"id": "sum-video", "name": "Trailblazer video", "format": "video",
         "primary": "The new Theodore Roosevelt Presidential Library in Medora, an Old West town in the North Dakota Badlands: eight chapters of his life, then the Badlands he loved right outside. Plan 3½ hours this summer.",
         "headline": "Your journey starts here", "desc": "Theodore Roosevelt Presidential Library", "cta": "Book Now", "url": TIX,
         "media": yt("qrwdZmqFO5A", "1:21", "Your Journey Starts Here — The Trailblazer"), "sells": "summer"},
     ])

# ======================= MEMBERSHIP & GIVING =======================
camp(id="mem-gift", program="Membership & giving", revenue=True, priority=1,
     name="MEMBERSHIP: Give a year at the Library", objective="Sales", optimization="Landing page views (Purchase once the ACME pixel is live)",
     start="2026-11-20", end="2027-01-19", budget=17000,
     spend=TEST("Cost per landing page view", "$2.00 or less", days=5),
     why="Gift memberships are the best holiday product the Library sells: $50–$1,000, no shipping cutoff, and they bring people back. Short test Nov 20–24, then full spend through Dec 24 (the gift window), then new-year joins.",
     audiences=[{"name": "Gift givers, national", "geo": "United States", "age": "35–70", "detail": "History, presidents, national parks, museum members", "share": 0.40},
                {"name": "Regional", "geo": DRIVE, "age": "30–70", "detail": "Broad", "share": 0.35},
                {"name": "Warm audiences", "geo": "United States", "age": "18+", "detail": "Video viewers, engagers, site visitors, past ticket buyers (hashed list, with OK)", "share": 0.25}],
     open_items=["Founding Member close date (Dec 31 per holiday plan) isn't on the membership page — confirm before using 'Founding' in copy.",
                 "Uploading the Constant Contact ticket-buyer list as a hashed Custom Audience needs Matt's OK."],
     ads=[
        {"id": "mem-gift-family", "name": "Gift — family membership", "format": "image",
         "primary": "Give a year at the new Theodore Roosevelt Presidential Library in Medora, an Old West town in the North Dakota Badlands: free admissions, member discounts in the store and at Salt+Scoria, the Library's restaurant, and a reason to come back. Family memberships are $175.",
         "headline": "Give a year at the Library", "desc": "Memberships from $50", "cta": "Give Now", "url": MEM,
         "media": img("family-gallery")},
        {"id": "mem-gift-carousel", "name": "Gift — pick a level", "format": "carousel",
         "primary": "Still shopping for someone who loves history or a good road trip? Give a membership to the new Theodore Roosevelt Presidential Library in Medora, an Old West town in the North Dakota Badlands.",
         "cta": "Give Now", "url": MEM,
         "cards": [{"media": img("cuba-pointing"), "headline": "Dual · $95", "desc": "2 admissions"},
                   {"media": img("kid-laughing"), "headline": "Family · $175", "desc": "4 admissions + programs"},
                   {"media": img("rough-riders-group"), "headline": "Contributing · $250", "desc": "6 admissions + welcome gift"},
                   {"media": img("arena-exhibit"), "headline": "Patron · $500", "desc": "Member magazine + more"}]},
        {"id": "mem-newyear", "name": "New year — join", "format": "image",
         "primary": "Start the year as a member of the new Theodore Roosevelt Presidential Library in Medora, an Old West town in the North Dakota Badlands. Free admissions and member pricing on everything else.",
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
         "primary": "The Theodore Roosevelt Presidential Library opened this summer in Medora, North Dakota. This Giving Tuesday, help keep its doors open to students, families and first-time visitors.",
         "headline": "Give on Giving Tuesday", "desc": "Theodore Roosevelt Presidential Library", "cta": "Donate Now", "url": GIVE,
         "media": img("kid-exhibit"), "flight": "Nov 24–Dec 1"},
        {"id": "give-ye", "name": "Year-end — first year", "format": "image",
         "primary": "The Theodore Roosevelt Presidential Library opened its doors in Medora, North Dakota this summer. Your year-end gift helps the next student, family and first-time visitor walk through them.",
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
         "primary": "Gifts from the store at the new Theodore Roosevelt Presidential Library in Medora, an Old West town in the North Dakota Badlands, shipped to your door. Every purchase supports the Library.",
         "cta": "Shop Now", "url": SHOP,
         "products": [prod("The Roosevelt Signature Hoodie | Black", "$64.99", SHOP + "/products/the-roosevelt-signature-hoodie-black", "https://cdn.shopify.com/s/files/1/0786/3998/8979/files/TRPL-signature-hoodie-front.png?v=1792510396"),
                      prod("Authentic Bully! Hat | Navy", "$54.99", SHOP + "/products/navy-bully-hat", "https://cdn.shopify.com/s/files/1/0786/3998/8979/files/TRPL_BullyHat_FRONT-2.png?v=1774030410"),
                      prod("Blue Chambray Men's Tech Shirt by Orvis", "$89.99", SHOP + "/products/mens-blue-chambray-tech-short-sleeve-shirt-by-orvis", "https://cdn.shopify.com/s/files/1/0786/3998/8979/files/TRPL_OrvisMen_sBlueChambrayShirt_FRONT.png?v=1773943958"),
                      prod("Ice Blue, Arena Quote T-shirt", "$29.99", SHOP + "/products/ice-blue-arena-quote-t-shirt-s", "https://cdn.shopify.com/s/files/1/0786/3998/8979/files/TRPL_IceBlueArenaTshirt_FRONT.png?v=1773943881"),
                      prod("Limited Edition Filson Tin Cloth Compact Briefcase", "$369.00", SHOP + "/products/filson-tin-cloth-compact-briefcase", "https://cdn.shopify.com/s/files/1/0786/3998/8979/files/TRPL_Filson_Tin_Cloth_Compact_FRONT.png?v=1773943469"),
                      prod("TRPL Cream/Black/Loden Hat", "$34.99", SHOP + "/products/trpl-cream-loden-hat", "https://cdn.shopify.com/s/files/1/0786/3998/8979/files/TRPL_LodenCreamHat_FRONT-2.png?v=1774030510")]},
        {"id": "shop-lifestyle", "name": "Store lifestyle", "format": "image",
         "primary": "Hats, tees, Filson bags and Orvis shirts made for the new Theodore Roosevelt Presidential Library in Medora, an Old West town in the North Dakota Badlands. Order online for the holidays; every purchase supports the Library.",
         "headline": "Shop the Library store", "desc": "Ships nationwide", "cta": "Shop Now", "url": SHOP,
         "media": img("store-shopping")},
        {"id": "shop-msd", "name": "Museum Store Sunday", "format": "image",
         "primary": "Sunday, Nov. 29 is Museum Store Sunday. Shop the store at the Theodore Roosevelt Presidential Library, online or in Medora, North Dakota, and support the Library with every purchase.",
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
        {"id": "ss-private-carousel", "name": "Private dining carousel", "format": "carousel",
         "primary": "Host a holiday party, board retreat or rehearsal dinner at Salt+Scoria, the restaurant inside the new Theodore Roosevelt Presidential Library in Medora, North Dakota, with the Badlands out the window. Menus by Chef Candace Stock.",
         "cta": "Get Quote", "url": EVENTS,
         "cards": [{"media": ss("dsc00636-2"), "headline": "Private dinners", "desc": "With a Badlands view", "url": EVENTS},
                   {"media": ss("trpl-saltscoria_general-027"), "headline": "Seasonal menus", "desc": "By Chef Candace Stock", "url": EVENTS},
                   {"media": ss("trpl-saltscoria_general-029"), "headline": "Wood-fired plates", "desc": "Regional cooking", "url": EVENTS},
                   {"media": ss("trpl-saltscoria_general-047"), "headline": "Board retreats", "desc": "Groups of every size", "url": EVENTS}]},
        {"id": "ss-private-dinner", "name": "Private dinner", "format": "image",
         "primary": "Host your holiday party, board retreat or rehearsal dinner at Salt+Scoria, the restaurant inside the new Theodore Roosevelt Presidential Library in Medora, with the Badlands out the window. Menus by Chef Candace Stock.",
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
         "primary": "Salt+Scoria, the café inside the new Theodore Roosevelt Presidential Library in Medora, serves wood-fired, seasonal food: TR's venison chili, smoked salmon salad, fresh pastries and good coffee.",
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
         "primary": "Sixty years behind the camera at the biggest moments in American history. In the Room: Photographs by David Hume Kennerly is at the Theodore Roosevelt Presidential Library in Medora, North Dakota, through January 10.",
         "headline": "See In the Room before it closes", "desc": "Included with admission", "cta": "Book Now", "url": TIX,
         "media": yt("-mcN1M3ZEps", "1:23", "In the Room: Photographs by David Hume Kennerly")},
        {"id": "room-still", "name": "In the gallery", "format": "image",
         "primary": "Pulitzer Prize-winning photographer David Hume Kennerly spent sixty years in the room where history happened. His photographs are at the Theodore Roosevelt Presidential Library in Medora, North Dakota, through January 10.",
         "headline": "In the Room, through Jan. 10", "desc": "Included with admission", "cta": "Book Now", "url": TIX,
         "media": still("room-51"), "verify": "Confirm 'Pulitzer Prize-winning' is used in the Library's exhibition copy"},
        {"id": "room-carousel", "name": "Inside In the Room", "format": "carousel",
         "primary": "Sixty years of photographs from inside the biggest moments in American history. In the Room: Photographs by David Hume Kennerly is at the Theodore Roosevelt Presidential Library in Medora, North Dakota, through January 10.",
         "cta": "Book Now", "url": TIX,
         "cards": [{"media": still("room-51"), "headline": "Sixty years of history", "desc": "Photographs by David Hume Kennerly", "url": TIX},
                   {"media": still("room-39"), "headline": "In the gallery", "desc": "Included with admission", "url": TIX},
                   {"media": still("room-60"), "headline": "Up close", "desc": "The photographs, large", "url": TIX},
                   {"media": still("room-63"), "headline": "Closes January 10", "desc": "Book a timed ticket", "url": TIX}]},
        {"id": "room-last-call", "name": "Last call", "format": "image",
         "primary": "Last weeks for In the Room: David Hume Kennerly's photographs close January 10 at the Theodore Roosevelt Presidential Library in Medora, North Dakota. Plan 3½ hours for the exhibition and the galleries.",
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
         "primary": "The new Theodore Roosevelt Presidential Library in Medora is dressed for the holidays. Make it part of your Cowboy Christmas weekend in town, and plan 3½ hours to see it all.",
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
         "primary": "America the Beautiful: Our Natural Wonders, narrated by Kelsey Grammer, on the big screen at the Theodore Roosevelt Presidential Library in Medora, North Dakota. Nov. 11–25.",
         "headline": "America the Beautiful, Nov. 11–25", "desc": "Afternoon and evening shows", "cta": "Get Tickets", "url": FILM,
         "media": ATB_TRAILER},
        {"id": "evt-film-poster", "name": "Poster", "format": "image",
         "primary": "A giant-screen tour of America's natural wonders, narrated by Kelsey Grammer, at the Theodore Roosevelt Presidential Library in Medora, Nov. 11–25. Afternoon and evening shows.",
         "headline": "See it on the big screen", "desc": "Theodore Roosevelt Presidential Library", "cta": "Get Tickets", "url": FILM,
         "media": atb("poster-4x5")},
        {"id": "evt-film-scenes", "name": "Scenes from the film", "format": "carousel",
         "primary": "Rivers, elk country and wetlands at sunset, the way they were made to be seen. America the Beautiful plays at the Theodore Roosevelt Presidential Library in Medora Nov. 11–25.",
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
         "primary": "Live near Medora? The last hour before close is free at the new Theodore Roosevelt Presidential Library with a timed ticket: a first look, since a full visit takes 3½ hours. " + NEH,
         "headline": "The last hour is free", "desc": "Reserve a timed ticket", "cta": "Learn More", "url": FFH,
         "media": img("campfire-room")},
     ])

# ======================= BRAND & AUDIENCE BUILDING =======================
camp(id="brand-video", program="Brand & audience building", revenue=False, priority=2,
     name="BRAND: Step into the story (video)", objective="Engagement", optimization="ThruPlay",
     start="2026-10-28", end="2027-01-19", budget=8000,
     spend=TEST("Cost per ThruPlay", "$0.03 or less", days=7, frac=0.5),
     why="Cheap video views at national scale. Builds the 50%-viewer audiences that the ticket, membership and giving campaigns retarget. Indoor commercials only for the winter; the study found awareness alone lifts interest by 22 points.",
     audiences=[{"name": "National", "geo": "United States", "age": "25–70", "detail": "American history, national parks, road trips, Theodore Roosevelt", "share": 0.5},
                {"name": "Drive market", "geo": DRIVE, "age": "25–70", "detail": "Broad", "share": 0.5}],
     open_items=["Vertical versions are auto-reframed (Trailblazer, River of Doubt, In the Room) or letterboxed over a blurred fill (Resolute, Arena, whose text is burned in). A 15-second edit made for vertical would beat both."],
     ads=[
        {"id": "brand-resolute", "name": "Resolute (0:31)", "format": "video",
         "primary": "Theodore Roosevelt, in his own words, at the edge of the Badlands where his story turned. Meet the new Theodore Roosevelt Presidential Library in Medora, an Old West town in the North Dakota Badlands.",
         "headline": "Theodore Roosevelt Presidential Library", "desc": "Plan a visit", "cta": "Learn More", "url": T + "/visit",
         "media": yt("gtDTwBMTn2Q", "0:31", "\"Resolute\" — Theodore Roosevelt in His Own Words")},
        {"id": "brand-amazon", "name": "River of Doubt (0:53)", "format": "video",
         "primary": "Step into the Amazon with Theodore Roosevelt. The River of Doubt is one of eight chapters at the new Theodore Roosevelt Presidential Library in Medora, an Old West town in the North Dakota Badlands.",
         "headline": "Step into the Amazon", "desc": "Medora, North Dakota", "cta": "Learn More", "url": T + "/visit",
         "media": yt("yEEsRy7sdng", "0:53", "Step Into the Amazon: Theodore Roosevelt's River of Doubt Comes Alive")},
        {"id": "brand-trailblazer", "name": "Trailblazer (1:21)", "format": "video",
         "primary": "At the new Theodore Roosevelt Presidential Library in Medora, an Old West town in the North Dakota Badlands, you won't just read about TR. You'll step into his story, chapter by chapter.",
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
         "primary": "Theodore Roosevelt was born October 27, 1858. Sign his birthday card from the new Theodore Roosevelt Presidential Library in Medora, an Old West town in the North Dakota Badlands, and add your own wish for the country.",
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
        {"id": "rt-chapters", "name": "Eight chapters, one visit", "format": "carousel",
         "primary": "You've seen the story. Now step into it: eight chapters of Theodore Roosevelt's life at the edge of the Badlands. Plan 3½ hours, and book your day ahead.",
         "cta": "Book Now", "url": TIX,
         "cards": [{"media": img("memory-train"), "headline": "The Memory Train", "desc": "The Badlands chapter", "url": TIX},
                   {"media": img("family-campfire"), "headline": "The Elkhorn campfire", "desc": "Stories from the ranch", "url": TIX},
                   {"media": img("cuba-family"), "headline": "San Juan Heights", "desc": "With the Rough Riders", "url": TIX},
                   {"media": img("white-house-gang"), "headline": "The White House Gang", "desc": "For kids who climb", "url": TIX},
                   {"media": img("amazon-river"), "headline": "The River of Doubt", "desc": "Into the Amazon", "url": TIX},
                   {"media": img("arena-exhibit"), "headline": "In the Arena", "desc": "After the White House", "url": TIX}]},
        {"id": "rt-roughriders", "name": "Come stand with the Rough Riders", "format": "carousel",
         "primary": "You've watched the story. Now step into it: stand with the Rough Riders, walk into the Cuba chapter, then step out into the Badlands. Eight chapters of Theodore Roosevelt's life at the new Theodore Roosevelt Presidential Library in Medora, North Dakota. Plan 3½ hours.",
         "headline": "Ready when you are", "desc": "Timed tickets", "cta": "Book Now", "url": TIX,
         "cards": [{"media": img("rough-riders-group"), "headline": "Stand with the Rough Riders", "desc": "A favorite photo spot inside", "url": TIX},
                   {"media": img("cuba-family"), "headline": "Walk into the Cuba chapter", "desc": "The Rough Riders' war", "url": TIX},
                   {"media": img("cuba-pointing"), "headline": "Bring the whole family", "desc": "Something for every age", "url": TIX},
                   {"media": img("library-sunset-glow"), "headline": "The new Library", "desc": "At the edge of the Badlands", "url": TIX},
                   {"media": img("library-aerial-badlands"), "headline": "Built into the Badlands", "desc": "Medora, North Dakota", "url": V + "/medora"},
                   {"media": img("library-big-sky"), "headline": "Plan 3½ hours", "desc": "Timed tickets", "url": TIX},
                   {"media": web("nps-bison-line"), "headline": "Bison next door", "desc": "The national park", "url": V + "/national-park"}]},
     ])

# ======================= DESTINATION: WHY MEDORA + ROAD TRIPS =======================
# Most people don't know the Library, the national park or Medora. These two campaigns sell the
# whole trip (the town, the park, the outdoors, the drive) and hand people the Library's own trip
# ideas on trlibrary.com/visit. They also feed the retargeting and ticket campaigns.
camp(id="dest-badlands", program="Tickets & visits", revenue=False, priority=1,
     name="DESTINATION: Why Medora — the town, the park, the outdoors", objective="Traffic", optimization="Landing page views on trlibrary.com/visit pages",
     start="2026-12-26", end="2027-01-19", budget=6000, spend=TEST("Cost per landing page view", "$0.90 or less", days=5),
     why="The study's skeptics converted in steps: 'it's not a traditional library', then 'it's actually in nature', then 'this is an adventure destination'. This campaign is those last two steps. It sells Medora and the national park next door as the reason for the trip, with the Library as the anchor, and sends people to the /visit pages that now cover the park, trails, scenic drives, stargazing and the town.",
     audiences=[{"name": "Drive market", "geo": DRIVE, "age": "28–65", "detail": "National parks, hiking, mountain biking, road trips, camping, RV travel", "share": 0.5},
                {"name": "Farther away", "geo": FAR, "age": "30–65", "detail": "National parks, road trips, Western travel, family vacations", "share": 0.5}],
     open_items=["Photos from trlibrary.com/visit, NPS and Medora.com (TRMF); Matt confirmed rights. Sources are listed in creative/web/catalog.json.",
                 "Medora Musical and Pitchfork Steak Fondue are summer-only; the copy says 'summer nights'. Confirm the season dates with TRMF.",
                 "Confirm Maah Daah Hey length (144 miles is the commonly cited figure) before launch."],
     ads=[
        {"id": "dest-why-carousel", "name": "More than a museum stop", "format": "carousel",
         "primary": "Most people haven't found Medora yet. It's a real Western town in the North Dakota Badlands, with bison and wild horses you can watch from the car, trails, horseback rides, a summer musical under the stars and the new Theodore Roosevelt Presidential Library.",
         "cta": "Learn More", "url": V, "sells": "summer",
         "cards": [{"media": web("bison-jam"), "headline": "A national park next door", "desc": "Bison, wild horses, prairie dogs", "url": V + "/national-park"},
                   {"media": web("maah-daah-hey"), "headline": "Ride or hike the Badlands", "desc": "The Maah Daah Hey Trail", "url": V + "/biking"},
                   {"media": web("painted-canyon"), "headline": "Scenic drives from town", "desc": "Overlooks, canyons, wildlife", "url": V + "/scenic-drives"},
                   {"media": web("stargazing-medora-sign"), "headline": "Some of the darkest skies around", "desc": "Milky Way and northern lights", "url": V + "/stargazing"},
                   {"media": web("medora-musical"), "headline": "A real Western town", "desc": "Summer nights at the Medora Musical", "url": V + "/medora"},
                   {"media": img("family-campfire"), "headline": "And TR's story, inside", "desc": "The new presidential library", "url": V + "/exhibits"}]},
        {"id": "dest-one-day", "name": "One day in Medora (stop by stop)", "format": "carousel",
         "primary": "One day in Medora, North Dakota, stop by stop: sunrise at Painted Canyon, a morning inside the new Theodore Roosevelt Presidential Library, an afternoon in the national park and an evening at the Medora Musical.",
         "cta": "Learn More", "url": IT + "/one-day", "sells": "summer",
         "cards": [{"media": web("kids-painted-canyon"), "headline": "Morning: Painted Canyon", "desc": "Your first look at the Badlands", "url": IT + "/one-day"},
                   {"media": web("library-butte"), "headline": "The new Library", "desc": "On the butte above Medora", "url": IT + "/one-day"},
                   {"media": web("library-gallery"), "headline": "Midday: the galleries", "desc": "Plan about 3½ hours", "url": IT + "/one-day"},
                   {"media": web("library-rooftop"), "headline": "The rooftop boardwalk", "desc": "Out over the Badlands", "url": IT + "/one-day"},
                   {"media": web("badlands-south-unit"), "headline": "Afternoon: into the park", "desc": "The South Unit scenic drive", "url": IT + "/one-day"},
                   {"media": web("maltese-fall"), "headline": "TR's Maltese Cross Cabin", "desc": "His first ranch cabin", "url": IT + "/one-day"},
                   {"media": web("medora-main-street"), "headline": "Evening: dinner in town", "desc": "A real Western main street", "url": IT + "/one-day"},
                   {"media": web("musical-night"), "headline": "The Medora Musical", "desc": "Summer nights under the stars", "url": IT + "/one-day"}]},
        {"id": "dest-3-days", "name": "2 nights, 3 days in Medora", "format": "carousel",
         "primary": "Two nights in the North Dakota Badlands: the new Theodore Roosevelt Presidential Library, the national park's scenic drive, the Chateau de Mores, the Cowboy Hall of Fame, trail rides and the Medora Musical. Here's the whole plan.",
         "cta": "Learn More", "url": IT + "/3-days-medora", "sells": "summer",
         "cards": [{"media": web("library-butte"), "headline": "Day 1: the Library", "desc": "Eight chapters of TR's life", "url": IT + "/3-days-medora"},
                   {"media": web("chateau-bluff"), "headline": "Day 1: Chateau de Mores", "desc": "The town founder's home", "url": IT + "/3-days-medora"},
                   {"media": web("badlands-south-unit"), "headline": "Day 2: the national park", "desc": "Scenic drive and short hikes", "url": IT + "/3-days-medora"},
                   {"media": web("bison-trnp"), "headline": "Bison along the road", "desc": "In the park's South Unit", "url": IT + "/3-days-medora"},
                   {"media": web("cowboy-hall-sunset"), "headline": "Day 2: Cowboy Hall of Fame", "desc": "Rodeo, ranching, Native heritage", "url": IT + "/3-days-medora"},
                   {"media": web("musical-amphitheatre"), "headline": "Day 2: the Medora Musical", "desc": "An amphitheater in the Badlands", "url": IT + "/3-days-medora"},
                   {"media": web("trail-ride-sunset"), "headline": "Day 3: one last ride", "desc": "Trail rides near town", "url": IT + "/3-days-medora"}]},
     ])

# One ad set per origin market (tourism data: ticket buyers by state), each shown only its own
# road trip so it reads like it was planned for them.
RT = lambda n, geo, share, detail="Road trips, national parks, family travel, American history": {"name": n, "geo": geo, "age": "30–70", "detail": detail, "share": share}
camp(id="dest-roadtrip", program="Tickets & visits", revenue=False, priority=1,
     name="DESTINATION: Your road trip to the Badlands, from home", objective="Traffic", optimization="Landing page views on the matching itinerary page",
     start="2026-12-29", end="2027-01-19", budget=10000, spend=TEST("Cost per landing page view", "$0.90 or less", days=5),
     why="Twenty road trips on trlibrary.com/visit/itineraries already start where our visitors live. Each ad set gets the trip from its own city: the Twin Cities weekend, Chicago to the Badlands, Denver to Yellowstone, Billings, the Black Hills, Kansas City and Omaha up US 29. Origins and weights follow the tourism data (ND 41%, MN 15%, MT 5%, SD 5%, then TX, WI, CO, CA, FL, AZ, IL). Runs as people plan summer.",
     audiences=[RT("Twin Cities + Minnesota", "Minnesota", 0.20), RT("Winnipeg + Manitoba", "Manitoba, Saskatchewan", 0.04),
                RT("Chicago + Wisconsin", "Illinois, Wisconsin", 0.12), RT("Denver + Colorado", "Colorado", 0.10),
                RT("Montana", "Montana", 0.08), RT("Black Hills + South Dakota", "South Dakota, Wyoming", 0.07),
                RT("Omaha, Kansas City + Iowa", "Nebraska, Iowa, Kansas, Missouri", 0.07),
                RT("Sun Belt", "Texas, Arizona, Florida, California", 0.12, "National parks, Yellowstone, Mount Rushmore, RV travel, road trips"),
                RT("North Dakota families", "North Dakota", 0.10, "Parents, family travel, dinosaurs, museums"),
                RT("Presidential history fans", "United States", 0.10, "Presidential libraries, American history, biographies, Ken Burns")],
     open_items=["Drive times come from the itinerary pages (Twin Cities 'about 8 hours'); the press backgrounder says 10 hours from Minneapolis. Settle on one number before launch.",
                 "Each ad runs only in its own ad set (see 'Shown to'). Build one ad set per market in Meta with that single ad.",
                 "Itinerary pages need real photos of the stops; the ads use Library Badlands photos until then."],
     ads=[
        {"id": "rt-mn", "for": "Twin Cities + Minnesota", "name": "Twin Cities: a long weekend", "format": "carousel",
         "primary": "From the Twin Cities, the North Dakota Badlands are about 8 hours west on I-94. Make it a long weekend: the Old West town of Medora, a national park full of bison and wild horses, and the new Theodore Roosevelt Presidential Library.",
         "cta": "Learn More", "url": IT + "/weekend-drives", "sells": "summer",
         "cards": [{"media": web("minneapolis"), "headline": "Leave the Twin Cities", "desc": "About 8 hours on I-94", "url": IT + "/weekend-drives"},
                   {"media": web("fargo-aerial"), "headline": "Break it up in Fargo", "desc": "3½ hours in", "url": IT + "/weekend-drives"},
                   {"media": web("jamestown-buffalo"), "headline": "The World's Largest Buffalo", "desc": "Jamestown, ND", "url": IT + "/weekend-drives"},
                   {"media": web("heritage-trex"), "headline": "ND Heritage Center", "desc": "Free, right on the route", "url": IT + "/weekend-drives"},
                   {"media": web("painted-canyon-visitors"), "headline": "Painted Canyon", "desc": "Your first view of the Badlands", "url": IT + "/weekend-drives"},
                   {"media": web("library-butte"), "headline": "The new Library", "desc": "Medora, North Dakota", "url": IT + "/weekend-drives"},
                   {"media": web("bison-ridge"), "headline": "Bison in the park", "desc": "The national park next door", "url": IT + "/weekend-drives"}]},
        {"id": "rt-mb", "for": "Winnipeg + Manitoba", "name": "Winnipeg: a long weekend", "format": "carousel",
         "primary": "From Winnipeg, the North Dakota Badlands are about 8 hours away. Plan a long weekend in Medora, an Old West town with a national park at its edge, bison and wild horses, and the new Theodore Roosevelt Presidential Library.",
         "cta": "Learn More", "url": IT + "/weekend-drives", "sells": "summer",
         "cards": [{"media": web("winnipeg-forks"), "headline": "Leave Winnipeg", "desc": "About 8 hours to Medora", "url": IT + "/weekend-drives"},
                   {"media": web("painted-canyon-visitors"), "headline": "Painted Canyon", "desc": "Right off I-94", "url": IT + "/weekend-drives"},
                   {"media": web("library-butte"), "headline": "The new Library", "desc": "Medora, North Dakota", "url": IT + "/weekend-drives"},
                   {"media": web("wild-horses"), "headline": "Wild horses", "desc": "In the national park", "url": IT + "/weekend-drives"},
                   {"media": web("medora-main-street"), "headline": "A real Western town", "desc": "Medora's main street", "url": IT + "/weekend-drives"}]},
        {"id": "rt-chi", "for": "Chicago + Wisconsin", "name": "Chicago to the Badlands", "format": "carousel",
         "primary": "Chicago to the Badlands in a week: the Driftless Area, the Mississippi bluffs, across Minnesota, then west to Medora, an Old West town with a national park, bison, and the new Theodore Roosevelt Presidential Library.",
         "cta": "Learn More", "url": IT + "/chicago-badlands", "sells": "summer",
         "cards": [{"media": web("wisconsin-dells"), "headline": "Day 1: Wisconsin Dells", "desc": "Sandstone gorges", "url": IT + "/chicago-badlands"},
                   {"media": web("mississippi-bluffs"), "headline": "The Mississippi bluffs", "desc": "La Crosse", "url": IT + "/chicago-badlands"},
                   {"media": web("jamestown-buffalo"), "headline": "Day 2: Jamestown", "desc": "The World's Largest Buffalo", "url": IT + "/chicago-badlands"},
                   {"media": web("enchanted-geese"), "headline": "The Enchanted Highway", "desc": "Giant scrap-metal art", "url": IT + "/chicago-badlands"},
                   {"media": web("painted-canyon-visitors"), "headline": "Painted Canyon", "desc": "Your first view of the Badlands", "url": IT + "/chicago-badlands"},
                   {"media": web("library-butte"), "headline": "Days 3–5: Medora", "desc": "The new Library", "url": IT + "/chicago-badlands"},
                   {"media": web("oxbow-overlook"), "headline": "The North Unit", "desc": "Oxbow Overlook", "url": IT + "/chicago-badlands"},
                   {"media": web("rushmore-aerial"), "headline": "The way home", "desc": "Optional Black Hills loop", "url": IT + "/chicago-badlands"}]},
        {"id": "rt-den", "for": "Denver + Colorado", "name": "Denver: the long way to Yellowstone", "format": "carousel",
         "primary": "Thirteen days from Denver: the Black Hills and Mount Rushmore, Devils Tower, the new Theodore Roosevelt Presidential Library in Medora, North Dakota, then Yellowstone, the Tetons and a Snake River float.",
         "cta": "Learn More", "url": IT + "/13-day-denver-wyoming", "sells": "summer",
         "cards": [{"media": web("red-rocks"), "headline": "Day 1: Denver", "desc": "Red Rocks", "url": IT + "/13-day-denver-wyoming"},
                   {"media": web("custer-bison"), "headline": "Day 3: Custer State Park", "desc": "Bison on the Wildlife Loop", "url": IT + "/13-day-denver-wyoming"},
                   {"media": web("rushmore-aerial"), "headline": "Day 4: Mount Rushmore", "desc": "Then Deadwood", "url": IT + "/13-day-denver-wyoming"},
                   {"media": web("devils-tower-2"), "headline": "Day 5: Devils Tower", "desc": "The first national monument", "url": IT + "/13-day-denver-wyoming"},
                   {"media": web("library-butte"), "headline": "Day 6: Medora", "desc": "The new Library", "url": IT + "/13-day-denver-wyoming"},
                   {"media": web("kids-painted-canyon"), "headline": "Day 7: the national park", "desc": "Painted Canyon", "url": IT + "/13-day-denver-wyoming"},
                   {"media": web("grand-prismatic"), "headline": "Day 9: Yellowstone", "desc": "Grand Prismatic Spring", "url": IT + "/13-day-denver-wyoming"},
                   {"media": web("teton-oxbow"), "headline": "Day 11: Grand Teton", "desc": "Oxbow Bend", "url": IT + "/13-day-denver-wyoming"},
                   {"media": web("snake-river-raft"), "headline": "Day 12: the Snake River", "desc": "Jackson Hole", "url": IT + "/13-day-denver-wyoming"}]},
        {"id": "rt-mt", "for": "Montana", "name": "Montana: Billings to Bismarck", "format": "carousel",
         "primary": "A week from Billings: Yellowstone, the Beartooth Highway, Cody, Mount Rushmore and Deadwood, Devils Tower, then Medora, an Old West town in the North Dakota Badlands with the new Theodore Roosevelt Presidential Library.",
         "cta": "Learn More", "url": IT + "/7-day-billings-bismarck", "sells": "summer",
         "cards": [{"media": web("yellowstone-river"), "headline": "Day 1: toward Yellowstone", "desc": "Paradise Valley", "url": IT + "/7-day-billings-bismarck"},
                   {"media": web("old-faithful-2"), "headline": "Day 2: Yellowstone", "desc": "Old Faithful", "url": IT + "/7-day-billings-bismarck"},
                   {"media": web("beartooth"), "headline": "Day 3: Beartooth Highway", "desc": "Then Cody", "url": IT + "/7-day-billings-bismarck"},
                   {"media": web("old-trail-town"), "headline": "Cody, Wyoming", "desc": "Old Trail Town", "url": IT + "/7-day-billings-bismarck"},
                   {"media": web("rushmore-aerial"), "headline": "Day 4: Mount Rushmore", "desc": "Then Deadwood", "url": IT + "/7-day-billings-bismarck"},
                   {"media": web("devils-tower-2"), "headline": "Day 5: Devils Tower", "desc": "On to Medora", "url": IT + "/7-day-billings-bismarck"},
                   {"media": web("library-butte"), "headline": "Day 6: Medora", "desc": "The new Library", "url": IT + "/7-day-billings-bismarck"},
                   {"media": web("heritage-trex"), "headline": "Bismarck", "desc": "ND Heritage Center", "url": IT + "/7-day-billings-bismarck"}]},
        {"id": "rt-sd", "for": "Black Hills + South Dakota", "name": "Black Hills: north on US 85", "format": "carousel",
         "primary": "From the Black Hills, take US 85 north 224 miles to the North Dakota Badlands: the town of Medora, the national park where Theodore Roosevelt ranched, the Medora Musical and the new Theodore Roosevelt Presidential Library.",
         "cta": "Learn More", "url": IT + "/sturgis-medora", "sells": "summer",
         "cards": [{"media": web("belle-fourche"), "headline": "Belle Fourche", "desc": "Center of the nation", "url": IT + "/sturgis-medora"},
                   {"media": web("us85-little-missouri"), "headline": "North on US 85", "desc": "Through the grasslands", "url": IT + "/sturgis-medora"},
                   {"media": web("library-butte"), "headline": "Day 2: the Library", "desc": "On the butte above Medora", "url": IT + "/sturgis-medora"},
                   {"media": web("badlands-rim-trail"), "headline": "The national park", "desc": "The South Unit", "url": IT + "/sturgis-medora"},
                   {"media": web("musical-night"), "headline": "The Medora Musical", "desc": "Summer nights", "url": IT + "/sturgis-medora"},
                   {"media": web("north-unit-shelter"), "headline": "Day 3: the North Unit", "desc": "The one people skip", "url": IT + "/sturgis-medora"}]},
        {"id": "rt-29", "for": "Omaha, Kansas City + Iowa", "name": "North on 29", "format": "carousel",
         "primary": "Six days north from Kansas City or Omaha: Osawatomie, Falls Park, the Corn Palace and the Missouri, then west across North Dakota to Medora, the Badlands and the new Theodore Roosevelt Presidential Library.",
         "cta": "Learn More", "url": IT + "/north-on-29", "sells": "summer",
         "cards": [{"media": web("john-brown-cabin"), "headline": "Day 1: Osawatomie", "desc": "John Brown Memorial Park", "url": IT + "/north-on-29"},
                   {"media": web("omaha-old-market"), "headline": "Day 2: Omaha", "desc": "The Old Market", "url": IT + "/north-on-29"},
                   {"media": web("falls-park"), "headline": "Day 3: Sioux Falls", "desc": "Falls Park", "url": IT + "/north-on-29"},
                   {"media": web("corn-palace-2"), "headline": "The Corn Palace", "desc": "Mitchell, South Dakota", "url": IT + "/north-on-29"},
                   {"media": web("nd-capitol"), "headline": "Day 5: Bismarck", "desc": "Then west", "url": IT + "/north-on-29"},
                   {"media": web("library-rooftop"), "headline": "Day 6: Medora", "desc": "The new Library", "url": IT + "/north-on-29"},
                   {"media": web("badlands-rim-trail"), "headline": "The Badlands", "desc": "The national park next door", "url": IT + "/north-on-29"}]},
        {"id": "rt-triangle", "for": "Sun Belt", "name": "The Roosevelt Triangle", "format": "carousel",
         "primary": "Mount Rushmore, Yellowstone and the North Dakota Badlands: three corners of one big Western road trip. In the Badlands corner is Medora, a real Western town most people haven't found yet, with bison, wild horses and the new Theodore Roosevelt Presidential Library.",
         "cta": "Learn More", "url": IT + "/roosevelt-triangle", "sells": "summer",
         "cards": [{"media": web("mount-rushmore"), "headline": "Mount Rushmore", "desc": "About 4½ hours to Medora", "url": IT + "/roosevelt-triangle"},
                   {"media": web("yellowstone-old-faithful"), "headline": "Yellowstone", "desc": "About 6½ hours to Medora", "url": IT + "/roosevelt-triangle"},
                   {"media": web("grand-prismatic"), "headline": "Grand Prismatic Spring", "desc": "Yellowstone", "url": IT + "/roosevelt-triangle"},
                   {"media": web("devils-tower-2"), "headline": "Devils Tower", "desc": "On the way north", "url": IT + "/roosevelt-triangle"},
                   {"media": web("bison-jam"), "headline": "The North Dakota Badlands", "desc": "Medora + the national park", "url": V + "/national-park"},
                   {"media": web("medora-main-street"), "headline": "Medora", "desc": "A real Western town", "url": V + "/medora"},
                   {"media": img("rough-riders-photo"), "headline": "Theodore Roosevelt's story", "desc": "The new presidential library", "url": V + "/exhibits"}]},
        {"id": "rt-nd", "for": "North Dakota families", "name": "Deep Time: a dinosaur road trip", "format": "carousel",
         "primary": "A dinosaur road trip across North Dakota: petrified trees in the national park at Medora, mounted dinosaurs in Dickinson, a mummified Edmontosaurus in Bismarck and a public dig. Start at the new Theodore Roosevelt Presidential Library in Medora.",
         "cta": "Learn More", "url": IT + "/dinosaurs", "sells": "summer",          "cards": [{"media": web("petrified-logs"), "headline": "Day 1: Medora", "desc": "Petrified trees in the park", "url": IT + "/dinosaurs"},
                   {"media": web("dino-museum-hall"), "headline": "Day 2: Dickinson", "desc": "The Badlands Dinosaur Museum", "url": IT + "/dinosaurs"},
                   {"media": web("heritage-trex"), "headline": "Day 3: Bismarck", "desc": "T. rex and Triceratops", "url": IT + "/dinosaurs"},
                   {"media": web("dino-skin"), "headline": "Dinosaur skin", "desc": "The mummy nicknamed Dakota", "url": IT + "/dinosaurs"},
                   {"media": web("makoshika"), "headline": "Optional: Makoshika", "desc": "Hell Creek badlands, Montana", "url": IT + "/dinosaurs"},
                   {"media": web("library-gallery"), "headline": "And the Library", "desc": "Medora, North Dakota", "url": IT + "/dinosaurs"}]},
        {"id": "rt-presidents", "for": "Presidential history fans", "name": "Five presidents, one road trip", "format": "carousel",
         "primary": "Five presidents, one road trip: the Eisenhower, Truman, Lincoln and Hoover presidential libraries, ending at the new Theodore Roosevelt Presidential Library in Medora, a small Old West town in the North Dakota Badlands.",
         "cta": "Learn More", "url": IT + "/presidential-libraries", "sells": "summer",          "cards": [{"media": web("eisenhower-home"), "headline": "Eisenhower", "desc": "Abilene, Kansas", "url": IT + "/presidential-libraries"},
                   {"media": web("truman-library"), "headline": "Truman", "desc": "Independence, Missouri", "url": IT + "/presidential-libraries"},
                   {"media": web("lincoln-library"), "headline": "Lincoln", "desc": "Springfield, Illinois", "url": IT + "/presidential-libraries"},
                   {"media": web("hoover-cottage"), "headline": "Hoover", "desc": "West Branch, Iowa", "url": IT + "/presidential-libraries"},
                   {"media": web("library-butte"), "headline": "Theodore Roosevelt", "desc": "Medora, North Dakota", "url": IT + "/presidential-libraries"},
                   {"media": web("bison-ridge-2"), "headline": "The Badlands", "desc": "The national park next door", "url": IT + "/presidential-libraries"}]},
     ])

# Families. The study: "Are the kids going to be bored?" Show a family that's together, outside and
# having fun. Never say "get off your phone" or name who it's for; show it.
camp(id="dest-family", program="Tickets & visits", revenue=False, priority=1,
     name="DESTINATION: Trade screens for skies (family trips)", objective="Traffic", optimization="Landing page views on /visit and the family itineraries",
     start="2026-12-26", end="2027-01-19", budget=8000, spend=TEST("Cost per landing page view", "$0.90 or less", days=5),
     why="The parent planning the summer trip wants everyone to have fun and actually be together. Medora delivers that without being told: bison from the back seat, a trail ride, steaks cooked on pitchforks, a musical under the stars, a campfire story inside the Library. The ads show those moments; they never mention phones or who is planning.",
     audiences=[{"name": "Parents, drive market", "geo": DRIVE, "age": "30–50", "detail": "Parents with kids 5–17, family vacations, road trips, national parks", "share": 0.45},
                {"name": "Parents, farther away", "geo": FAR, "age": "30–50", "detail": "Parents with kids 5–17, family vacations, RV travel, national parks", "share": 0.55}],
     open_items=["'Trade Screens for Skies' approved by Matt (Oct 22). Brand cards set it in Dharma Gothic E with Sunset Yellow.",
                 "Family photos come from Medora.com (TRMF), trlibrary.com and NPS (rights confirmed by Matt). Sources in creative/web/catalog.json."],
     ads=[
        {"id": "fam-carousel", "name": "Trade screens for skies", "format": "carousel",
         "primary": "Trade screens for skies. In Medora, a real Western town in the North Dakota Badlands, the kids count bison out the window, ride horses into the hills and fall asleep under more stars than they've ever seen. And the new Theodore Roosevelt Presidential Library is right in town.",
         "cta": "Learn More", "url": V, "sells": "summer",
         "cards": [{"media": card("screens-skies-library-1x1", ratio="1/1"), "headline": "Trade Screens for Skies", "desc": "Medora, North Dakota", "url": V},
                   {"media": web("bison-jam"), "headline": "Bison out the window", "desc": "In the national park next door", "url": V + "/national-park"},
                   {"media": web("kids-painted-canyon"), "headline": "Hike Painted Canyon", "desc": "Short trails, big views", "url": V + "/national-park"},
                   {"media": web("trail-ride-sunset"), "headline": "Saddle up", "desc": "Trail rides into the Badlands", "url": V + "/activities"},
                   {"media": web("prairie-dog"), "headline": "Prairie dog towns", "desc": "They'll pop up to say hi", "url": V + "/national-park"},
                   {"media": web("pitchfork-kid"), "headline": "Steak on a pitchfork", "desc": "Pitchfork Steak Fondue", "url": V + "/eat"},
                   {"media": web("medora-musical-audience"), "headline": "Cheer at the Medora Musical", "desc": "Summer nights outdoors", "url": V + "/medora"},
                   {"media": img("kid-laughing"), "headline": "Campfire stories", "desc": "Inside the Library", "url": V + "/exhibits"},
                   {"media": web("medora-pool"), "headline": "Cool off at the pool", "desc": "Right in town", "url": V + "/activities"},
                   {"media": web("stargazing-medora-sign"), "headline": "More stars than you've seen", "desc": "Dark Badlands skies", "url": V + "/stargazing"}]},
        {"id": "fam-title-library", "name": "Trade Screens for Skies (the Library)", "format": "image",
         "primary": "Trade screens for skies. The new Theodore Roosevelt Presidential Library sits under the big sky of the North Dakota Badlands, in Medora, a real Western town with bison and wild horses next door, trail rides and a cowboy musical.",
         "headline": "Plan a family trip to Medora", "desc": "Trips and ideas from the Library", "cta": "Learn More", "url": V,
         "media": card("screens-skies-library-4x5", story="screens-skies-library-9x16")},
        {"id": "fam-downtown", "name": "Race you down Main Street", "format": "image",
         "primary": "Race you to the end of Main Street. Medora is a real Western town in the North Dakota Badlands where the whole family has something to do: wild horses, trail rides, a pool, mini golf, a cowboy musical and the new Theodore Roosevelt Presidential Library.",
         "headline": "A family trip to the Badlands", "desc": "Medora, North Dakota", "cta": "Learn More", "url": IT + "/3-days-medora",
         "media": web("downtown-family"), "sells": "summer"},
        {"id": "fam-wildlife-carousel", "name": "Who you'll meet in the park", "format": "carousel",
         "primary": "Bison, wild horses, prairie dogs and elk, close enough to see from the car and without the crowds. Theodore Roosevelt National Park sits at the edge of Medora, North Dakota, next to the new Theodore Roosevelt Presidential Library.",
         "cta": "Learn More", "url": V + "/national-park", "sells": "summer",
         "cards": [{"media": web("bison-jam"), "headline": "Bison", "desc": "Sometimes in the road", "url": V + "/national-park"},
                   {"media": web("wild-horses"), "headline": "Wild horses", "desc": "Bands roam the South Unit", "url": V + "/national-park"},
                   {"media": web("prairie-dog"), "headline": "Prairie dogs", "desc": "Whole towns of them", "url": V + "/national-park"},
                   {"media": web("nps-elk-butte"), "headline": "Elk", "desc": "Listen for them in fall", "url": V + "/national-park"},
                   {"media": web("nps-bison-battle"), "headline": "Bulls in summer", "desc": "From a safe distance", "url": V + "/national-park"}]},
        {"id": "fam-wildlife", "name": "Wildlife without the crowds", "format": "image",
         "primary": "Bison and wild horses, close enough to see from the car and without the crowds. Theodore Roosevelt National Park sits at the edge of Medora, North Dakota, a real Western town, next to the new Theodore Roosevelt Presidential Library.",
         "headline": "Bison, wild horses, no crowds", "desc": "Medora, North Dakota", "cta": "Learn More", "url": V + "/national-park",
         "media": web("wild-horses"), "sells": "summer"},
        {"id": "fam-pool", "name": "Summer in Medora", "format": "image",
         "primary": "Mornings in the national park, afternoons at the pool, evenings at a cowboy musical. Summer in Medora, North Dakota, a small Western town in the Badlands with the new Theodore Roosevelt Presidential Library at its edge.",
         "headline": "Plan a summer in the Badlands", "desc": "Itineraries from the Library", "cta": "Learn More", "url": IT + "/3-days-medora",
         "media": web("medora-pool"), "sells": "summer"},
     ])

# People who are already out here. Meta can't see airline or hotel bookings, but its location
# targeting has "People traveling in this location" (recent location 200+ km from home). Pins along
# I-94 and in the gateway towns catch road-trippers and fly-in visitors while they're nearby.
camp(id="dest-nearby", program="Tickets & visits", revenue=True, priority=1,
     name="DESTINATION: Travelers already nearby (I-94, Black Hills, gateway towns)", objective="Sales", optimization="Landing page views (Purchase once the ACME pixel is live)",
     start="2026-11-04", end="2027-01-19", budget=2500, spend=BURST("Cost per landing page view", "People traveling through decide today; a test window would miss them. Small, always-on budget."),
     why="Catches people who are already in the region: driving I-94 across western North Dakota, flying into Bismarck, Dickinson or Billings, or visiting the Black Hills. Winter traffic is light, so the budget is small; the same ad sets are the backbone of a summer always-on campaign after the credit ends.",
     audiences=[{"name": "I-94 corridor travelers", "geo": "People traveling in: pins on I-94 at Bismarck, Dickinson, Belfield, Beach (ND) and Glendive (MT), 15–25 mi radius", "age": "21+", "detail": "Broad (location type: traveling in this location)", "share": 0.6},
                {"name": "Fly-in and gateway towns", "geo": "People traveling in: Bismarck, Dickinson, Williston, Billings", "age": "25+", "detail": "Broad (traveling in this location)", "share": 0.2},
                {"name": "Black Hills travelers", "geo": "People traveling in: Rapid City, Spearfish, Deadwood, Custer (SD)", "age": "25+", "detail": "Broad (traveling in this location)", "share": 0.2}],
     open_items=["Meta can't target people who booked travel (no airline or hotel data). 'Traveling in' uses device location; reach in winter will be small.",
                 "Confirm I-94 exit numbers for Medora (Exit 24 per the press backgrounder; Exit 27 is the east entrance) and winter hours before launch."],
     ads=[
        {"id": "near-i94-carousel", "for": "I-94 corridor travelers", "name": "Worth the exit (carousel)", "format": "carousel",
         "primary": "Driving I-94 across North Dakota? Take Exit 24 to Medora: Painted Canyon, the new Theodore Roosevelt Presidential Library, a national park full of bison, and an Old West main street. Plan 3½ hours at the Library.",
         "headline": "Worth the exit: Medora, ND", "desc": "I-94, Exit 24", "cta": "Learn More", "url": V + "/medora",
         "cards": [{"media": web("painted-canyon"), "headline": "Painted Canyon", "desc": "Right off the interstate", "url": V + "/scenic-drives"},
                   {"media": img("library-aerial-badlands"), "headline": "The new Library", "desc": "Built into the Badlands", "url": TIX},
                   {"media": img("rough-riders-group"), "headline": "Stand with the Rough Riders", "desc": "One of eight chapters inside", "url": TIX},
                   {"media": img("cuba-family"), "headline": "Walk into the Cuba chapter", "desc": "Plan 3½ hours", "url": TIX},
                   {"media": web("nps-bison-line"), "headline": "The national park", "desc": "Bison on the ridgelines", "url": V + "/national-park"},
                   {"media": web("cowboy-hall-sunset"), "headline": "Cowboy Hall of Fame", "desc": "On Medora's Main Street", "url": V + "/medora"}]},
        {"id": "near-i94", "for": "I-94 corridor travelers", "name": "Driving I-94?", "format": "image",
         "primary": "Driving I-94 across North Dakota? Take Exit 24 to Medora for the new Theodore Roosevelt Presidential Library: eight immersive chapters of his life at the edge of the Badlands. Plan 3½ hours, and book a timed ticket.",
         "headline": "Worth the exit: Medora, ND", "desc": "I-94, Exit 24", "cta": "Book Now", "url": TIX,
         "media": img("library-aerial-badlands")},
        {"id": "near-gateway", "for": "Fly-in and gateway towns", "name": "In the area this week", "format": "carousel",
         "primary": "In western North Dakota or eastern Montana this week? The new Theodore Roosevelt Presidential Library is in Medora, an Old West town on I-94 at the edge of the Badlands. Plan 3½ hours inside, then see the national park next door.",
         "headline": "Add Medora to this trip", "desc": "Timed tickets", "cta": "Book Now", "url": TIX,
         "cards": [{"media": img("library-aerial-badlands"), "headline": "Add Medora to this trip", "desc": "Just off I-94", "url": TIX},
                   {"media": img("rough-riders-group"), "headline": "Stand with the Rough Riders", "desc": "Eight chapters inside", "url": TIX},
                   {"media": img("family-campfire"), "headline": "Sit by the campfire", "desc": "Stories from the ranch", "url": TIX},
                   {"media": img("cuba-family"), "headline": "Walk into the Cuba chapter", "desc": "All indoors", "url": TIX},
                   {"media": web("nps-bison-line"), "headline": "Bison next door", "desc": "The national park", "url": V + "/national-park"},
                   {"media": web("maltese-cross-cabin"), "headline": "TR's Maltese Cross Cabin", "desc": "Behind the park visitor center", "url": V + "/medora"}]},
        {"id": "near-blackhills-carousel", "for": "Black Hills travelers", "name": "After Rushmore: north on US 85", "format": "carousel",
         "primary": "Seen Mount Rushmore? Keep going north. About 4½ hours up US 85 is Medora, North Dakota: the Badlands where Theodore Roosevelt ranched, a national park full of bison, and the new Theodore Roosevelt Presidential Library.",
         "cta": "Learn More", "url": IT + "/sturgis-medora",
         "cards": [{"media": web("mount-rushmore"), "headline": "Seen Mount Rushmore?", "desc": "T.R. is the third face", "url": IT + "/sturgis-medora"},
                   {"media": web("belle-fourche"), "headline": "Keep going north", "desc": "Up US 85 from the Black Hills", "url": IT + "/sturgis-medora"},
                   {"media": web("painted-canyon"), "headline": "Into the Badlands", "desc": "About 4½ hours north", "url": IT + "/sturgis-medora"},
                   {"media": web("library-night"), "headline": "The new Library", "desc": "Medora, North Dakota", "url": TIX},
                   {"media": web("nps-bison-line"), "headline": "The national park", "desc": "Bison on the ridgelines", "url": V + "/national-park"},
                   {"media": web("library-gallery"), "headline": "Eight chapters inside", "desc": "Plan 3½ hours", "url": V + "/medora"}]},
        {"id": "near-blackhills", "for": "Black Hills travelers", "name": "From the Black Hills, keep going north", "format": "carousel",
         "primary": "In the Black Hills? Keep going north. Bison in Custer State Park, Mount Rushmore, Deadwood and Sturgis, then about 4½ hours up the road to Medora, North Dakota: the Badlands where Theodore Roosevelt ranched, and the new Theodore Roosevelt Presidential Library.",
         "headline": "Keep going north", "desc": "Black Hills to the Badlands", "cta": "Learn More", "url": IT + "/sturgis-medora",
         "cards": [{"media": web("custer-bison"), "headline": "Custer State Park", "desc": "Bison by the road", "url": IT + "/sturgis-medora"},
                   {"media": web("mount-rushmore"), "headline": "Mount Rushmore", "desc": "T.R. is the third face", "url": IT + "/sturgis-medora"},
                   {"media": web("deadwood-main"), "headline": "Deadwood", "desc": "A Gold Rush main street", "url": IT + "/sturgis-medora"},
                   {"media": web("sturgis-rally"), "headline": "Sturgis", "desc": "Home of the rally", "url": IT + "/sturgis-medora"},
                   {"media": web("medora-aerial"), "headline": "Medora, North Dakota", "desc": "A real Western town", "url": V + "/medora"},
                   {"media": img("library-aerial-badlands"), "headline": "The new Library", "desc": "Theodore Roosevelt Presidential Library", "url": TIX}]},
     ])

RESERVE = {"budget": 2000, "why": "Unassigned. Funds the winners of each test after week one and any burst that is delivering well, so the whole credit is spent by Jan 19. Test-phase savings roll in here too."}

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
        for i, cd in enumerate(a.get("cards", [])):   # carousel cards can link to their own pages
            if cd.get("url"):
                s2 = "&" if "?" in cd["url"] else "?"
                cd["tracked_url"] = f'{cd["url"]}{s2}utm_source=meta&utm_medium=paid_social&utm_campaign={c["id"]}&utm_content={a["id"]}-{i + 1}'

out = {"generated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "credit": CREDIT,
       "reserve": RESERVE, "guardrails": GUARDRAILS, "campaigns": C}
(ROOT / "data" / "campaigns.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
tot = sum(c["budget"] for c in C)
print(f"{len(C)} campaigns, {sum(len(c['ads']) for c in C)} ads, ${tot:,} planned + ${RESERVE['budget']:,} reserve = ${tot + RESERVE['budget']:,}")
