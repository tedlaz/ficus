# pip install requests-html
from requests_html import HTMLSession

# C:\Users\tedla\AppData\Local\pyppeteer\pyppeteer\local-chromium\588429


def get_video_url_filmatic(url):
    s = HTMLSession()
    r = s.get(url)
    r.html.render(sleep=1)
    sel = (
        'body '
        '> div.os-padding '
        '> div.os-viewport.os-viewport-native-scrollbars-invisible '
        '> div.os-content '
        '> div.site-wrap.container-fluid.p-0.flx '
        '> div.main-side.flx-fx '
        '> main.content.mt-5.p-3 '
        '> div'
        '> article.fullstory.ignore-select '
        '> div.tabs '
        '> div.tabs-content '
        '> div.tab.active '
        '> div.fullcol.flx '
        '> div.fullcol-right.flx-fx.order-last '
        '> iframe.lozad.loaded '
    )

    # print(sel)
    res = r.html.find(sel, first=True)
    hidden_url = res.attrs['src']

    # print(hidden_url)

    s2 = HTMLSession()
    r2 = s2.get(hidden_url)
    r2.html.render()

    res2 = r2.html.find('video', first=True)
    # print(res2.attrs['src'])
    return res2.attrs['src']


if __name__ == '__main__':
    url = 'https://filmatic.online/load/tain_e_toy_2019/22413-the_parts_you_lose_2019.html'
    print(get_video_url_filmatic(url))
