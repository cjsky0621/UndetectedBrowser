#!python

import zipfile, logging
# maker: happycoder1389
# proxies.txt -> 1.1.1.1 8080 user1 password
from dotenv import load_dotenv

import os, sys, time, math, requests
import undetected_chromedriver.v2 as uc
from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

load_dotenv() # To load environmental variables

BROWSERSTACK_USERNAME = os.environ.get("BROWSERSTACK_USERNAME") # To get BROWSERSTACK_USERNAME environmental variable
BROWSERSTACK_ACCESS_KEY = os.environ.get("BROWSERSTACK_ACCESS_KEY") # To get BROWSERSTACK_ACCESS_KEY environmental variable
BUILD_NAME = "browserstack-build-1"

capability = {
        "browserName": "Chrome", # To be masked browser's name
        "browserVersion": "103.0", # To be masked browser's version
        "os": "Windows", # To be masked fingerprint (OS name)
        "osVersion": "11", # To be masked fingerprint (OS version)
        "sessionName": "Browser Stack Engine",  # test name
        "buildName": BUILD_NAME,  # Your tests will be organized within this build
}

bstack_options = {
        "resolution" : "1024x768", # To be masked fingerprint (resolution)
        "osVersion" : capability["osVersion"],
        "buildName" : capability["buildName"],
        "sessionName" : capability["sessionName"],
        "userName": BROWSERSTACK_USERNAME,
        "accessKey": BROWSERSTACK_ACCESS_KEY,
        "os": capability["os"]
}

class UndetectedBrowser:
    
    driver = None
    ipAddr = ''
    
    def __init__(self, proxyInfo):
        self.drivername = "chromedriver" + ".exe" # To set a chromedrvier's name
        self.ipAddr = proxyInfo["ipAddr"] # To set a proxy server's address
        locationInfo = self.get_info() # To get location's info ans set. []
        proxy_server = proxyInfo["ipAddr"] + ":" + proxyInfo["port"] # To set a server address: ip:port

        opts = uc.ChromeOptions()

        if "browserVersion" in capability:
            opts.browser_version = capability["browserVersion"]
        # opts.add_argument('--headless')
        opts.add_argument('--no-sandbox') 
        opts.add_argument('--lang=' + locationInfo[1]) 
        opts.set_capability('bstack:options', bstack_options)
        opts.add_argument("--window-size=1024,768") # To set a window size when opening browser

        opts.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36') # To be masked fingerprint (UserAgent)
        # opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        # opts.add_experimental_option('useAutomationExtension', False)
        cdriver = uc.Chrome(options=opts, executable_path=r"\chromedriver.exe")

        (lat, lng) = locationInfo[2] # To set a tuple. (latitude, longitude)
        get_params = {
            "latitude": lat,
            "longitude": lng,
            "accuracy": 100
        }
        cdriver.execute_cdp_cmd("Page.setGeolocationOverride", get_params) # To be masked fingerprint (geo location)
        if locationInfo[0] is None: tz_params = {'timezoneId': 'Europe/London'}
        else: tz_params = {'timezoneId': locationInfo[0]}
        cdriver.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params) # To be masked fingerprint (timezone)
        self.set_timeZone(locationInfo[3])
        
        # To be masked fingerprint (deviceMemory, hardwareConcurrency, webdriver, mediaDevices(videoinput, audioinput, audiooutput))
        cdriver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'deviceMemory', {
                    get: () => 16
                });
                Object.defineProperty(navigator, 'hardwareConcurrency', {
                    get: () => 10
                });
                Object.defineProperty(navigator, 'mediadevices', {
                    get: () => '{videoinput: id = aidsoawjdIUJSIUdwajsidjaw =, audioinput: id = aidsoawjdIUJSIUdwajsidjaw =, audiooutput: id = aidsoawjdIUJSIUdwajsidjaw =}'
                });
            """
        })
        
        # This function plays a role in masking (default: canvas, webgl image, webgl metadata)
        stealth(cdriver,
            # languages=["en-USd", locationInfo[1]], # To be masked fingerprint (languages)
            vendor="Google Inc.", # To be masked fingerprint (Vendor)
            platform="Win32", # To be masked fingerprint (OS platform)
            webgl_vendor="Intel Inc.", # To be masked fingerprint (webgl_vendor)
            renderer="Intel Iris OpenGL Engine", # To be masked fingerprint (webgl_renderer)
            fix_hairline=True,
        )

        self.driver = cdriver

    # To get a timezone, language, latitude, longitude based on IP address
    def get_info(self):
        ip_address = self.ipAddr
        api_key = 'be0f755b93290b4c100445d77533d291763a417c75524e95e07819ad'
        response = requests.get(f'https://api.ipdata.co/{ip_address}?api-key={api_key}').json()
        tz = None ; lang = None ; lat = -1 ; lng = -1
        if "time_zone" in response.keys(): tz = response.get("time_zone")["name"]
        if "time_zone" in response.keys(): tzoffset = response.get("time_zone")["offset"]
        if "languages" in response.keys():
            lang = response.get("languages")[0]["code"]
        if "latitude" in response.keys(): lat = response.get("latitude")
        if "longitude" in response.keys(): lng = response.get("longitude")
        return [tz,lang, (lat, lng), tzoffset]
    
    def set_timeZone(self, offset):
        if offset is None: offset = "+00:00"
        offset = offset[:-2] + ":" + "00"
        fd = os.popen("tzutil /l")
        lines = fd.readlines()
        fd.close()
        for i in range(len(lines)):
            if offset in lines[i]:
                break
        try:
            fd = os.popen("tzutil /s \"" + lines[i + 1].strip() + "\""); fd.close()
        except:
            pass

class BrowserCheckEngine:
    
    browsers = []
    
    def __init__(self):
        self.proxies = []
        
        # To read proxies.txt and get a proxy server's address
        fd = open("proxies.txt", "r")
        lines = fd.readlines()
        fd.close()

        # The file to show the masked result
        path = str(os.getcwd()).replace('\\', '/') + "/tests/static/test.html"
        i = 1
        for line in lines:
            if line.strip() == "": continue
            pams = line.split()
            mb = UndetectedBrowser({
                "ipAddr": pams[0],
                "port": pams[1],
                "user": pams[2],
                "passwd": pams[3]
            })
            
            url = "https://bot.sannysoft.com/"
            if os.name == 'nt':
                url = 'file:///' + path
            else:
                url = 'file://' + path
            mb.driver.get(url)
            
            # To produce a masked result html and screenshot.
            metrics = mb.driver.execute_cdp_cmd('Page.getLayoutMetrics', {})
            width = math.ceil(metrics['contentSize']['width'])
            height = math.ceil(metrics['contentSize']['height'])
            screenOrientation = dict(angle=0, type='portraitPrimary')
            mb.driver.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {
                'mobile': False,
                'width': width,
                'height': height,
                'deviceScaleFactor': 1,
                'screenOrientation': screenOrientation,
            })

            mb.driver.save_screenshot(str(i) + ".png")
            html = mb.driver.page_source;
            fd = open(str(i) + ".html", "w");fd.write(html); fd.close()
            #####################################################
            
            self.browsers.append(mb)
            i += 1
        char = ''
        dd = self.browsers[len(self.browsers) - 1]
        while char != 'q': # If enter the key 'q', close the browser
            char = input('>> ') # To prompt
            char.lower()
            if char == 'o': # If enter the key 'o'
                url = input('Enter URL\n>> ') # To enter the url string
                url.lower()
                dd.driver.get(url)
            elif char in 'q':
                dd.driver.quit()
                break

def main(argv):
    bce = BrowserCheckEngine()

if __name__ == '__main__':
    main(sys.argv[1:])