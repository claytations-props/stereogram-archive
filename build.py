import json
src=json.load(open('/home/hatch/workspace/stereogram-archive/sources.json'))
# keyed by distinctive substring
def find(sub):
    for k,v in src.items():
        if sub.lower() in k.lower(): return v
    raise KeyError(sub)

META=[
 # (findkey, title, place, yearlabel, sortyear, era, cats, blurb)
 ("American Falls", "American Falls, Niagara", "Niagara Falls, New York", "c. 1865", 1865, "early", ["water"], "Tourists in stiff collars stared at the same falls we do. This early Dennis view catches the American Falls before the souvenir shops took over."),
 ("Table Rock, Niagara", "Table Rock, Niagara Falls", "Niagara Falls, Ontario", "1859–1885", 1872, "mid", ["water"], "Table Rock was a broad limestone ledge hanging over the gorge. It crumbled away in pieces and is long gone, so this is the only way to stand on it now."),
 ("Suspension Bridge, and Clifton", "Suspension Bridge & Clifton House", "Niagara Falls", "1868–1889", 1878, "mid", ["water","cities"], "The great suspension bridge with the Clifton House behind it. Cross the pair with your eyes and the river gorge drops away underneath."),
 ("Upper Yosemite Falls", "Upper Yosemite Falls", "Yosemite Valley, California", "c. 1900–1925", 1910, "late", ["water","mountains"], "Yosemite Falls dropping through the valley. Stereo cards like this were how most Americans first saw Yosemite at all, on a parlor table."),
 ("Three Brothers, Yosemite", "Three Brothers", "Yosemite, California", "c. 1870–1885", 1878, "mid", ["mountains"], "Three granite peaks lined up over the Merced River. One of the most sold Yosemite views of the 1870s."),
 ("The Grand Canyon, Arizona, from Robert", "The Grand Canyon", "Arizona", "Date uncertain, 1800s–1920s", 1900, "undated", ["mountains"], "Nobody could quite believe the Canyon was real until views like this circulated. In stereo, the far rim finally looks as far as it is."),
 ("Golden Gate, Yellowstone", "Golden Gate Canyon", "Yellowstone, Wyoming", "c. 1890", 1890, "mid", ["mountains"], "The Golden Gate pass in Yellowstone, with the old wooden trestle road clinging to the cliff. Brave wagon drivers only."),
 ("Grand Falls, Yellowstone River", "Lower Falls of the Yellowstone", "Yellowstone, Wyoming", "c. 1870", 1870, "mid", ["water","mountains"], "The Grand Falls of the Yellowstone River, photographed when the park was brand new. The canyon walls are the yellow stone that named the place."),
 ("View in Central Park", "A View in Central Park", "New York City", "c. 1865–1905", 1885, "mid", ["cities"], "Central Park when it was still new landscaping instead of old landmark. The park was designed to look natural, and stereo views sold the illusion."),
 ("Town Hall, Center Harbor", "Town Hall, Center Harbor", "New Hampshire", "Undated", 1900, "undated", ["cities"], "A small town New Hampshire scene from the Library of Congress cards. Quiet street, big sky, not a car in sight, because there basically were not any yet."),
 ("Genius of America", "The Genius of America", "Washington, D.C.", "1859–1905", 1882, "mid", ["cities","oddities"], "The Genius of America pediment over the Capitol. A sculpture group most people never look up at, sold here as a parlor view."),
 ("Mount Washington Railway", "Cog Railway Summit", "Mount Washington, New Hampshire", "c. 1860–1903", 1882, "mid", ["mountains"], "The Mount Washington Cog Railway at the summit. The little train still climbs this mountain today, on much the same route."),
 ("Deck and turret of U.S.S. Monitor", "Deck of the USS Monitor", "James River, Virginia", "1862", 1862, "early", ["war"], "The deck and turret of the Monitor, July 1862, months after its famous duel with the Virginia. The future of warships, sitting almost flat on the water."),
 ("Parapet, Fort Sumter", "Parapet of Fort Sumter", "Charleston, South Carolina", "1865", 1865, "early", ["war"], "Inside battered Fort Sumter at the end of the Civil War, where the war began four years earlier. The guns and rubble tell the story."),
 ("Block house - NARA", "Civil War Block House", "Virginia (attributed)", "c. 1860–1865", 1862, "early", ["war"], "A log block house guarding a railroad line, from the National Archives. Built fast, built rough, and photographed before it rotted away."),
 ("Damascus Gate, Jerusalem", "Damascus Gate", "Jerusalem", "1898–1934", 1915, "late", ["world"], "The Damascus Gate in Jerusalem, from the Library of Congress photochrom era mats. Crowds have passed through this gate for centuries."),
 ("Crystal Palace", "The Crystal Palace", "Sydenham, London", "1850s", 1855, "early", ["world"], "The Crystal Palace rebuilt at Sydenham after the Great Exhibition. Glass, iron, and pure Victorian confidence. It burned down in 1936."),
 ("Guanajuato (Keystone", "Guanajuato", "Guanajuato, Mexico", "1920", 1920, "late", ["world","cities"], "A Keystone View Company card of Guanajuato, Mexico, 1920. Keystone was the biggest stereo card maker in the world by then."),
 ("Martinsburg (Oberlahnstein)", "Martinsburg Castle", "Oberlahnstein, Germany", "1840s", 1845, "early", ["world"], "One of the earliest stereo photographs in the whole archive, an 1840s calotype of Martinsburg castle on the Rhine. The process was barely invented."),
 ("Duomo di Milano", "Eva, Milan Cathedral", "Milan, Italy", "1800s", 1875, "undated", ["world"], "A statue on the roof of Milan Cathedral, photographed by Giorgio Sommer, one of Italy's great early commercial photographers."),
 ("Irish wake", "An Irish Wake", "United States", "1894", 1894, "mid", ["people"], "A staged comic sorrow scene of an Irish wake, 1894. These acted out story cards were the sitcoms of the stereo era, sold in sets."),
 ("Biddy served Tomatoes", "How Biddy Served Tomatoes", "United States", "1897", 1897, "mid", ["people"], "A one joke comic card from 1897. Biddy serves the tomatoes undressed, meaning the tomatoes. Mostly. These puns paid for a lot of photographers' dinners."),
 ("street performance", "Street Performance", "United States", "Undated", 1900, "undated", ["people"], "A man and child watching a street performer, from the Library of Congress cards. Free entertainment, 100 years before phones."),
 ("Bandstands music venue", "The Bandstand", "United States", "Undated", 1900, "undated", ["people","cities"], "A park bandstand in its Sunday best era, when every town had a band and every band had a stand."),
 ("Gas Balloon", "A Gas Balloon", "United States", "1850s", 1855, "early", ["oddities"], "A gas balloon in the 1850s, when ballooning was part science, part daredevil act. An early calotype era stereo view from the Met."),
 ("Full Moon, Yerkes", "The Full Moon in Stereo", "Yerkes Observatory, Wisconsin", "Undated", 1905, "undated", ["oddities"], "Yes, the Moon works in stereo too. Two exposures taken hours apart let the Moon's wobble fake a pair of eyes impossibly far apart."),
 ("Iceberg, showing curved", "Antarctic Iceberg", "Cape Roberts, Antarctica", "1911", 1911, "late", ["oddities","water"], "An iceberg at Cape Roberts in 1911, from the heroic age of Antarctic exploration. Those curved bands are seasons of snow, bent by the ice."),
 ("Stairway on side of rock", "Stairway on the Rock", "United States", "Undated", 1900, "undated", ["mountains","oddities"], "Somebody built a stairway up the side of a rock, and somebody else thought it was worth a stereo card. They were both right."),
 ("Tree, pond, castle", "Castle by the Pond", "Europe (unidentified)", "Undated", 1900, "undated", ["world"], "A tree, a pond, and a castle with a conical tower. The Library of Congress never recorded exactly where, so enjoy the mystery."),
 ("Dirt road and arch", "Dirt Road and Arch", "United States", "Undated", 1900, "undated", ["cities"], "A dirt road passing under an arch, from the LOC cards. Ordinary places got stereo cards too, and sometimes those age the best."),
]
items=[]
for key,title,place,year,sy,era,cats,blurb in META:
    v=find(key)
    items.append({"title":title,"place":place,"year":year,"sy":sy,"era":era,"cats":cats,"blurb":blurb,
                  "img":v["thumb"],"full":v["full"],"source":v["descurl"],"license":v["license"],"w":v["w"],"h":v["h"]})
json.dump(items, open('/home/hatch/workspace/stereogram-archive/data.json','w'), indent=1)
print("items", len(items))
for i in items: print(i["title"], "|", i["license"], "|", i["img"][:80])
