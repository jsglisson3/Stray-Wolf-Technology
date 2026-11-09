"""The list of websites shown on the Work page and in "Recent work" on the homepage.

To add a site, copy one block below (from { to },), paste it at the TOP of the list
so the newest site shows first, and change the words. Then:
  1. Save a screenshot of the site's homepage (a desktop browser, 1440 x 900) in
     docs/images/work/ as <image>-desktop-640.webp and <image>-desktop-960.webp,
     where <image> is the short name you put on the "image" line.
     Claude can take and size the screenshot for you: send it the link.
  2. Rebuild (python tools/build.py) and push.

  name    the business or group, as they write it
  about   one short line: what kind of business, and where
  link    the full web address, starting with https://
  image   a short name for the screenshot files, lowercase, no spaces
  tag     leave empty "" for a normal client site. For a concept, use
          "Volunteer concept, not the official site" or similar.

The homepage carousel and the Work page both show them all.
"""

SITES = [
    {
        "name": "TVIS Construction",
        "about": "An excavation and sitework company in Chattanooga, Tennessee.",
        "link": "https://tvisconstruction.com/",
        "image": "tvis",
        "tag": "",
    },
    {
        "name": "GLP Home Options",
        "about": "A home-buying business in Chattanooga, Tennessee.",
        "link": "https://jsglisson3.github.io/GLP-Home-Options/",
        "image": "glp",
        "tag": "",
    },
    {
        "name": "Friends of The Colony Public Library",
        "about": "A redesign concept for the library's nonprofit friends group in The Colony, Texas, built as a volunteer.",
        "link": "https://jsglisson3.github.io/FOTCL/",
        "image": "fotcpl",
        "tag": "Volunteer concept, not the official site",
    },
]
