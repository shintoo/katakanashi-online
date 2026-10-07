import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

URL = os.environ.get("URL", "http://localhost:5173")
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent / "shots" / Path(__file__).stem)
OUT.mkdir(parents=True, exist_ok=True)
errors = []
checks = []


def check(ok, what):
    checks.append(("PASS" if ok else "FAIL") + ": " + what)


def page_for(browser, name):
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    page = ctx.new_page()
    # The wrong-code checks expect "room not found" (404) answers, so those aren't errors.
    page.on("console", lambda m: m.type == "error" and "404" not in m.text and errors.append(f"{name}: {m.text}"))
    page.on("pageerror", lambda e: errors.append(f"{name}: {e}"))
    return page


def shot(page, name):
    page.screenshot(path=str(OUT / f"{name}.png"))


def fill_profile(page, name, i):
    page.fill("#pname", name)
    picks = page.locator(".pf-pick")
    picks.nth(i % picks.count()).click()
    cols = page.locator(".pf-color")
    cols.nth(i % cols.count()).click()


def dismiss_howto(page):
    page.wait_for_selector(".how")
    page.click("text=分かった、イコー!")


with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome")
    host = page_for(browser, "Sean")

    # Wrong room code from the title screen.
    host.goto(URL)
    host.wait_for_selector(".marquee")
    host.fill(".field.code", "ZZZZ")
    host.click("button:has-text('Join')")
    host.wait_for_selector(".pf-error")
    check("no room" in host.inner_text(".pf-error").lower(), "wrong code shows an error")
    shot(host, "01-wrong-code")

    # Bad link straight to a room that doesn't exist.
    bad = page_for(browser, "bad-link")
    bad.goto(URL + "/r/QQQQ")
    bad.wait_for_selector(".title-msg")
    check("no room" in bad.inner_text(".title-msg").lower(), "bad link goes to title with a message")
    shot(bad, "02-bad-link")
    bad.context.close()

    # Host makes an endless, untimed room.
    host.click("text=Create a room")
    fill_profile(host, "Sean", 0)
    host.click("button:has-text('Create room')")
    dismiss_howto(host)
    host.wait_for_selector(".lob-code")
    code = host.inner_text(".lob-code").strip()
    host.click(".chip:has-text('Endless')")
    host.click(".chip:has-text('No limit')")
    host.click(".chip:has-text('Host goes first')")

    # Seven friends join by link, for a crowded table of 8.
    names = ["Hana", "Kenji", "Yuki", "Taro", "Mika", "Riku", "Aoi"]
    pages = {"Sean": host}
    for i, nm in enumerate(names):
        g = page_for(browser, nm)
        g.goto(f"{URL}/r/{code}")
        g.wait_for_selector("#pname")
        fill_profile(g, nm, i + 1)
        g.click("button:has-text('Join room')")
        dismiss_howto(g)
        pages[nm] = g
    host.wait_for_function("document.querySelectorAll('.lob-p:not(.ghost)').length === 8")
    check(pages["Aoi"].locator(".chip.on:has-text('Endless')").count() == 1, "guests see endless setting")
    shot(host, "03-lobby-8")
    shot(pages["Aoi"], "04-lobby-guest")

    host.click("text=スタート!")
    host.wait_for_selector(".pod")
    host.wait_for_timeout(800)

    def describer_name(viewer=host):
        return viewer.evaluate("""() => {
          const d = document.querySelector('.pod.describer .plate'); return d && d.textContent.trim() }""")

    def play_turn(miss=False):
        dn = describer_name()
        d = pages[dn]
        d.click("#deck")
        d.wait_for_selector("#hand")
        d.wait_for_timeout(900)
        if miss:
            d.click("text=諦める")
        else:
            other = next(n for n in pages if n != dn)
            d.click(f".pod:has(.plate:text-is('{other}'))")
        d.wait_for_timeout(1100)
        return dn

    check(describer_name() == "Sean", "host goes first")
    play_turn()
    shot(host, "05-table-8-host")
    shot(pages["Kenji"], "06-table-8-guest")

    # End game shouldn't work mid-round.
    host.click(".hostbtn")
    check(host.locator(".menu .item:has-text('End game')").is_disabled(), "end game disabled mid-round")
    host.click(".hostbtn")

    # Yuki closes her tab (leaves) mid-round.
    pages["Yuki"].context.close()
    del pages["Yuki"]
    host.wait_for_timeout(1500)
    shot(host, "07-yuki-away")

    # Play until the round ends. Yuki's turn should be skipped.
    describers = []
    for _ in range(12):
        if host.locator(".roundover").count():
            break
        describers.append(play_turn(miss=len(describers) == 1))
    check("Yuki" not in describers, f"away player skipped (turn order: {describers})")
    host.wait_for_selector(".roundover")
    shot(host, "08-round-over-host")
    shot(pages["Hana"], "09-round-over-guest")
    check(host.locator(".roundover button:has-text('Next round')").count() == 1, "host gets next round / end game")
    check(pages["Hana"].locator(".roundover button").count() == 0, "guests don't get round buttons")

    # Next round, a couple of turns.
    host.click(".roundover button:has-text('Next round')")
    host.wait_for_selector(".roundover", state="detached")
    host.wait_for_timeout(800)
    play_turn()
    play_turn()

    # Remove the away player, then remove a connected one.
    host.click(".hostbtn")
    host.click("text=Remove a player")
    host.click(".pick:has-text('Yuki')")
    shot(host, "10-remove-dialog")
    host.click(".panel button:has-text('Remove')")
    host.wait_for_timeout(1200)
    check(host.locator(".pod:has(.plate:text-is('Yuki'))").count() == 0, "removed away player is gone")

    host.click(".hostbtn")
    host.click("text=Remove a player")
    host.click(".pick:has-text('Riku')")
    host.click(".panel button:has-text('Remove')")
    pages["Riku"].wait_for_selector(".title-msg")
    check("removed" in pages["Riku"].inner_text(".title-msg"), "removed player sees a message")
    shot(pages["Riku"], "11-riku-removed")
    shot(host, "12-after-removes")
    del pages["Riku"]

    # Riku can come back with the room code.
    r = page_for(browser, "Riku2")
    r.goto(f"{URL}/r/{code}")
    r.wait_for_selector("#pname")
    fill_profile(r, "Riku", 5)
    r.click("button:has-text('Join room')")
    dismiss_howto(r)
    r.wait_for_selector(".pod")
    pages["Riku"] = r
    host.wait_for_timeout(1000)
    shot(r, "13-riku-rejoined")

    # Play until the round ends, then end the game.
    for _ in range(12):
        if host.locator(".roundover").count():
            break
        if not describer_name():
            host.wait_for_timeout(500)
            continue
        play_turn()
    host.wait_for_selector(".roundover")
    host.click(".hostbtn")
    check(not host.locator(".menu .item:has-text('End game')").is_disabled(), "end game enabled between rounds")
    host.click(".hostbtn")
    host.click(".roundover button:has-text('End game')")
    host.wait_for_selector(".endov")
    host.wait_for_timeout(2500)
    shot(host, "14-end")
    shot(pages["Aoi"], "15-end-guest")
    browser.close()

print("\n".join(checks))
print("errors:", errors or "none")
