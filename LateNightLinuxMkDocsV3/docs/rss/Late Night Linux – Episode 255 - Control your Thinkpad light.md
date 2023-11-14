---
title: Late Night Linux – Episode 255 - Control your Thinkpad light
date: 13/11/2023 21:56:31
link: https://mastodon.social/@pid_eins/111345807599821099
search:
  exclude: true
hide:
  - toc
  - navigation
---

# Control your Thinkpad light

Page Title: Lennart Poettering: "Did you know you could control brightness of the …" - Mastodon

Page Description: Did you know you could control brightness of the red dot on the i of the "ThinkPad" on the top-side of your thinkpad? I sure didn't: -  - this turns it off: -  - echo 0 | sudo tee /sys/class/leds/tpacpi\:\:lid_logo_dot/brightness -  - and this turns it on: -  - echo 255 | sudo tee /sys/class/leds/tpacpi\:\:lid_logo_dot/brightness -  - I don't really know what this information is good for, but hey, isn't it awesome to have a 1px display on the outside of your laptop? 

Link: [https://mastodon.social/@pid_eins/111345807599821099](https://mastodon.social/@pid_eins/111345807599821099)