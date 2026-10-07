import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

URL = os.environ.get("URL", "http://localhost:5173")
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent / "shots" / Path(__file__).stem)
OUT.mkdir(parents=True, exist_ok=True)
errors = []


def page_for(browser, name):
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    page = ctx.new_page()
    page.on("console", lambda m: m.type == "error" and errors.append(f"{name}: {m.text}"))
    page.on("pageerror", lambda e: errors.append(f"{name}: {e}"))
    return page


def shot(page, name):
    page.screenshot(path=str(OUT / f"{name}.png"))


def fill_profile(page, name, shape=0, color=0):
    page.fill("#pname", name)
    page.locator(".pf-pick").nth(shape).click()
    page.locator(".pf-color").nth(color).click()


with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome")
    host = page_for(browser, "host")
    host.goto(URL)
    host.wait_for_selector(".marquee")
    shot(host, "01-title")
    host.click("text=Create a room")
    fill_profile(host, "Sean", 0, 0)
    shot(host, "02-create")
    host.click("button:has-text('Create room')")
    host.wait_for_selector(".how")
    shot(host, "03-howto")
    host.click("text=分かった、イコー!")
    host.wait_for_selector(".lob-code")
    code = host.inner_text(".lob-code").strip()
    print("room", code)

    guests = []
    for i, nm in enumerate(["Hana", "Kenji"]):
        g = page_for(browser, nm)
        g.goto(URL)
        g.fill(".field.code", code.lower())
        g.click("button:has-text('Join')")
        g.wait_for_selector("#pname")
        fill_profile(g, nm, i + 1, i + 1)
        g.click("button:has-text('Join room')")
        g.wait_for_selector(".how")
        g.click("text=分かった、イコー!")
        guests.append(g)
    host.wait_for_function("document.querySelectorAll('.lob-p:not(.ghost)').length === 3")
    host.click(".chip:has-text('Spin the wheel')")
    host.click(".chip:has-text('30s')")
    guests[0].wait_for_selector(".chip.on:has-text('30s')")
    shot(host, "04-lobby-host")
    shot(guests[0], "05-lobby-guest")

    host.click("text=スタート!")
    host.wait_for_selector(".wheelov")
    shot(guests[0], "06-wheel-guest")
    host.click("text=SPIN!")
    host.wait_for_timeout(5000)
    shot(host, "07-wheel-done")
    host.click("text=スタート!")
    host.wait_for_selector(".wheelov", state="detached")
    pages = {"Sean": host, "Hana": guests[0], "Kenji": guests[1]}

    def describer_name():
        return host.evaluate("""() => {
          const d = document.querySelector('.pod.describer .plate'); return d && d.textContent.trim() }""")

    for turn in range(4):
        host.wait_for_timeout(400)
        dn = describer_name()
        d = pages[dn]
        others = [n for n in pages if n != dn]
        d.click("#deck")
        d.wait_for_selector("#hand")
        d.wait_for_timeout(1500)
        if turn == 0:
            shot(d, "08-describer")
            shot(pages[others[0]], "09-guesser")
        if turn == 1:
            d.click(".note")
            d.wait_for_timeout(700)
            shot(d, "10-peek")
            d.click("text=諦める")
        else:
            d.click(f".pod:has(.plate:text-is('{others[0]}'))")
        d.wait_for_timeout(1200)
        if turn == 0:
            shot(pages[others[1]], "11-after-give")

    # Refresh a guest mid-game and check they come back in their seat.
    g = guests[1]
    g.reload()
    g.wait_for_selector(".pod")
    shot(g, "12-after-refresh")

    # Host fixes a mistake.
    host.click(".hostbtn")
    shot(host, "13-host-menu")
    host.click("text=Fix a mistake")
    scored = host.locator(".pickrow").nth(0).locator(".pick:not([disabled])").first
    scored.click()
    host.locator(".pickrow").nth(1).locator(".pick:not([disabled])").first.click()
    shot(host, "14-fix")
    host.click("text=Move card")
    host.wait_for_timeout(1200)

    # Change table color.
    host.click(".hostbtn")
    host.locator(".menu .sw button").nth(3).click()
    host.wait_for_timeout(800)
    shot(guests[0], "15-color")

    # Timer warnings: wait out a 30s card.
    dn = describer_name()
    d = pages[dn]
    d.click("#deck")
    d.wait_for_timeout(11500)
    shot(pages[[n for n in pages if n != dn][0]], "16-timer-20")
    d.wait_for_timeout(14000)
    shot(d, "17-timer-low")
    d.click("text=諦める")
    d.wait_for_timeout(1500)

    # Play out the rest so the game ends (5 rounds by default).
    for _ in range(40):
        if host.locator(".endov").count():
            break
        dn = describer_name()
        if not dn:
            host.wait_for_timeout(500)
            continue
        d = pages[dn]
        d.click("#deck")
        d.wait_for_selector("#hand")
        others = [n for n in pages if n != dn]
        d.click(f".pod:has(.plate:text-is('{others[0]}'))")
        d.wait_for_timeout(1000)
    host.wait_for_selector(".endov")
    host.wait_for_timeout(2500)
    shot(host, "18-end")
    shot(guests[0], "19-end-guest")
    host.click("text=Play again")
    shot(host, "20-play-again")
    host.click(".chip:has-text('Host goes first')")
    host.click("text=レッツゴー！")
    host.wait_for_timeout(1200)
    shot(guests[0], "21-new-game")

    host.click(".hostbtn")
    host.click("text=Close room")
    host.click(".panel button:has-text('Close room')")
    guests[0].wait_for_selector(".title-msg")
    shot(guests[0], "22-closed")
    browser.close()

print("errors:", errors or "none")

