# #!/usr/bin/env python3
# """
# LinkedIn Poster Module for AI Employee System
# Automatically posts updates to LinkedIn when tasks are approved.
# """
# import os
# import time
# import json
# import traceback
# from datetime import datetime
# from pathlib import Path
# import logging
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# try:
#     from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
#     from playwright.sync_api import sync_playwright as sync_playwright_module
#     PLAYWRIGHT_AVAILABLE = True
# except ImportError:
#     PLAYWRIGHT_AVAILABLE = False
#     print("Playwright not available. Install with: pip install playwright")
#     print("Then run: playwright install")


# class LinkedInPoster:
#     """
#     LinkedIn automation class using Playwright to create posts
#     """
#     def __init__(self, logs_path="./logs"):
#         self.email = os.getenv("LINKEDIN_EMAIL")
#         self.password = os.getenv("LINKEDIN_PASSWORD")
#         self.logs_path = Path(logs_path)

#         # Ensure logs directory exists
#         self.logs_path.mkdir(exist_ok=True)

#         # Setup logging
#         log_file = self.logs_path / "linkedin_poster.log"
#         logging.basicConfig(
#             level=logging.INFO,
#             format='%(asctime)s - %(levelname)s - %(message)s',
#             handlers=[
#                 logging.FileHandler(log_file),
#                 logging.StreamHandler()
#             ]
#         )
#         self.logger = logging.getLogger(__name__)

#         # Check if LinkedIn credentials are provided
#         if not self.email or not self.password:
#             self.logger.error("LinkedIn credentials not found in .env file")
#             raise ValueError("LINKEDIN_EMAIL and LINKEDIN_PASSWORD must be set in .env file")

#         # Initialize Playwright
#         if not PLAYWRIGHT_AVAILABLE:
#             raise ImportError("Playwright is required for LinkedIn posting. Install with: pip install playwright")

#         self.playwright = None
#         self.browser = None
#         self.page = None

#     def start_browser(self):
#         """Start the Playwright browser (sync version for backward compatibility)"""
#         try:
#             self.playwright = sync_playwright_module().start()
#             self.browser = self.playwright.chromium.launch(
#                 headless=False,  # Set to True in production
#                 args=[
#                     "--disable-blink-features=AutomationControlled",
#                     "--disable-dev-shm-usage",
#                     "--no-sandbox",
#                     "--disable-setuid-sandbox"
#                 ]
#             )
#             self.page = self.browser.new_page()

#             # Set user agent to appear more like a real browser
#             user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
#             self.page.set_extra_http_headers({"User-Agent": user_agent})

#             self.logger.info("Browser started successfully")
#             return True
#         except Exception as e:
#             self.logger.error(f"Failed to start browser: {str(e)}")
#             return False

#     async def start_browser_async(self):
#         """Start the Playwright browser asynchronously"""
#         try:
#             self.playwright = await async_playwright().start()
#             self.browser = await self.playwright.chromium.launch(
#                 headless=False,  # Set to True in production
#                 args=[
#                     "--disable-blink-features=AutomationControlled",
#                     "--disable-dev-shm-usage",
#                     "--no-sandbox",
#                     "--disable-setuid-sandbox"
#                 ]
#             )
#             self.page = await self.browser.new_page()

#             # Set user agent to appear more like a real browser
#             user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
#             await self.page.set_extra_http_headers({"User-Agent": user_agent})

#             self.logger.info("Async browser started successfully")
#             return True
#         except Exception as e:
#             self.logger.error(f"Failed to start async browser: {str(e)}")
#             return False

#     def stop_browser(self):
#         """Stop the Playwright browser"""
#         try:
#             if self.browser:
#                 self.browser.close()
#             if self.playwright:
#                 self.playwright.stop()
#             self.logger.info("Browser stopped successfully")
#         except Exception as e:
#             self.logger.error(f"Error stopping browser: {str(e)}")

#     async def stop_browser_async(self):
#         """Stop the async Playwright browser"""
#         try:
#             if self.browser:
#                 await self.browser.close()
#             if self.playwright:
#                 await self.playwright.stop()
#             self.logger.info("Async browser stopped successfully")
#         except Exception as e:
#             self.logger.error(f"Error stopping async browser: {str(e)}")

#     def login_to_linkedin(self):
#         """Log into LinkedIn using credentials (sync version for backward compatibility)"""
#         try:
#             self.logger.info("Starting LinkedIn login process...")

#             # Navigate to LinkedIn login page with retry (max 2 attempts)
#             for login_attempt in range(2):
#                 try:
#                     self.logger.info(f"Login attempt {login_attempt + 1}/2")
#                     self.page.goto("https://www.linkedin.com/login", timeout=30000, wait_until="domcontentloaded")
#                     self.page.wait_for_load_state("networkidle", timeout=30000)
#                     time.sleep(4)  # Stable wait for page to fully load

#                     # Check if already logged in
#                     if "feed" in self.page.url or "dashboard" in self.page.url:
#                         self.logger.info("Already logged into LinkedIn")
#                         break

#                     # Handle page redirect during login
#                     current_url = self.page.url
#                     if "feed" in current_url or "dashboard" in current_url:
#                         self.logger.info("Redirected to feed after navigation")
#                         break

#                     # Fill in email - try multiple selectors
#                     email_selectors = ['input#username', 'input[name="session_key"]', 'input[type="text"]']
#                     email_input = None
#                     for selector in email_selectors:
#                         try:
#                             email_input = self.page.wait_for_selector(selector, timeout=5000)
#                             self.logger.info(f"Found email field using: {selector}")
#                             break
#                         except PlaywrightTimeoutError:
#                             continue

#                     if email_input is None:
#                         if login_attempt == 0:
#                             self.logger.warning("Email field not found, retrying login page...")
#                             time.sleep(2)
#                             continue
#                         else:
#                             self.logger.error("Email field not found after 2 attempts")
#                             return False

#                     email_input.fill(self.email)
#                     self.logger.info("Filled email field")
#                     time.sleep(1)

#                     # Fill in password
#                     password_input = self.page.wait_for_selector('input#password', timeout=10000)
#                     password_input.fill(self.password)
#                     self.logger.info("Filled password field")
#                     time.sleep(1)

#                     # Click login button
#                     login_button = self.page.wait_for_selector('button[type="submit"]', timeout=10000)
#                     login_button.click()
#                     self.logger.info("Clicked login button")
#                     time.sleep(5)

#                     # Check for redirect after login
#                     if "feed" in self.page.url or "dashboard" in self.page.url:
#                         self.logger.info("Login successful - redirected to feed")
#                         break

#                     break  # Exit retry loop if we got this far

#                 except Exception as e:
#                     if login_attempt == 0:
#                         self.logger.warning(f"Login attempt failed, retrying: {str(e)}")
#                         time.sleep(2)
#                     else:
#                         raise

#             # Wait for potential 2FA or security checks
#             current_url = self.page.url
#             if "checkpoint" in current_url.lower() or "challenge" in current_url.lower():
#                 self.logger.warning("LinkedIn security check detected - waiting for manual resolution")
#                 # Wait up to 60 seconds for user to complete security check
#                 for i in range(60):
#                     time.sleep(1)
#                     if "feed" in self.page.url:
#                         self.logger.info("Successfully passed security check")
#                         break
#                 else:
#                     self.logger.error("Security check timeout - couldn't pass LinkedIn security check")
#                     return False

#             # Check if login was successful by checking for the feed
#             if "feed" in self.page.url or "dashboard" in self.page.url:
#                 self.page.wait_for_url("**/feed/**", timeout=30000)
#                 self.page.wait_for_timeout(5000)
#                 self.page.screenshot(path="after_login.png")
#                 self.logger.info(f"URL after login: {self.page.url}")
#                 self.logger.info("Successfully logged into LinkedIn")
#                 return True
#             else:
#                 # Check for error messages
#                 error_selectors = [
#                     'div[role="alert"]',
#                     '.error',
#                     '[data-test-id="error-display"]',
#                     '.auth-failed-message'
#                 ]

#                 for selector in error_selectors:
#                     try:
#                         error_element = self.page.query_selector(selector)
#                         if error_element:
#                             error_text = error_element.text_content()
#                             self.logger.error(f"Login failed with message from {selector}: {error_text}")
#                             return False
#                     except:
#                         continue

#                 self.logger.info(f"Login appears successful - current URL: {self.page.url}")
#                 return True

#         except PlaywrightTimeoutError as e:
#             self.logger.error(f"Timeout during login process: {str(e)}")
#             return False
#         except Exception as e:
#             self.logger.error(f"Error during LinkedIn login: {str(e)}")
#             return False

#     async def login_to_linkedin_async(self):
#         """Log into LinkedIn using credentials asynchronously"""
#         try:
#             self.logger.info("Starting async LinkedIn login process...")

#             # Navigate to LinkedIn login page
#             await self.page.goto("https://www.linkedin.com/login", timeout=30000)
#             await self.page.wait_for_timeout(2000)

#             # Check if already logged in
#             current_url = self.page.url
#             if "feed" in current_url or "dashboard" in current_url:
#                 self.logger.info("Already logged into LinkedIn")
#                 return True

#             # Fill in email
#             email_input = await self.page.wait_for_selector('input#username', timeout=10000)
#             await email_input.fill(self.email)
#             self.logger.info("Filled email field")
#             await self.page.wait_for_timeout(1000)

#             # Fill in password
#             password_input = await self.page.wait_for_selector('input#password', timeout=10000)
#             await password_input.fill(self.password)
#             self.logger.info("Filled password field")
#             await self.page.wait_for_timeout(1000)

#             # Click login button
#             login_button = await self.page.wait_for_selector('button[type="submit"]', timeout=10000)
#             await login_button.click()
#             self.logger.info("Clicked login button")
#             await self.page.wait_for_timeout(5000)

#             # Wait for potential 2FA or security checks
#             current_url = self.page.url
#             if "checkpoint" in current_url.lower() or "challenge" in current_url.lower():
#                 self.logger.warning("LinkedIn security check detected - waiting for manual resolution")
#                 # Wait up to 60 seconds for user to complete security check
#                 for i in range(60):
#                     await self.page.wait_for_timeout(1000)
#                     if "feed" in self.page.url:
#                         self.logger.info("Successfully passed security check")
#                         break
#                 else:
#                     self.logger.error("Security check timeout - couldn't pass LinkedIn security check")
#                     return False

#             # Check if login was successful by checking for the feed
#             if "feed" in self.page.url or "dashboard" in self.page.url:
#                 self.logger.info("Successfully logged into LinkedIn")
#                 return True
#             else:
#                 # Check for error messages
#                 error_selectors = [
#                     'div[role="alert"]',
#                     '.error',
#                     '[data-test-id="error-display"]',
#                     '.auth-failed-message'
#                 ]

#                 for selector in error_selectors:
#                     try:
#                         error_element = await self.page.query_selector(selector)
#                         if error_element:
#                             error_text = await error_element.text_content()
#                             self.logger.error(f"Login failed with message from {selector}: {error_text}")
#                             return False
#                     except:
#                         continue

#                 self.logger.info(f"Login appears successful - current URL: {self.page.url}")
#                 return True

#         except PlaywrightTimeoutError as e:
#             self.logger.error(f"Timeout during async login process: {str(e)}")
#             return False
#         except Exception as e:
#             self.logger.error(f"Error during async LinkedIn login: {str(e)}")
#             return False

#     def create_post(self, content, hashtags=None):
#         """
#         Create a LinkedIn post with the given content

#         Args:
#             content (str): The main content of the post
#             hashtags (list, optional): List of hashtags to include

#         Returns:
#             bool: True if post was created successfully, False otherwise
#         """
#         try:
#             self.logger.info("Starting LinkedIn post creation process...")

#             # Navigate to the feed to find the create post button
#             if not self.page.url.startswith("https://www.linkedin.com/feed"):
#                 self.logger.info("Navigating to LinkedIn feed...")
#                 self.page.goto("https://www.linkedin.com/feed", timeout=30000)

#             # Progressive wait: first wait for feed URL
#             self.logger.info("Waiting for feed URL...")
#             try:
#                 self.page.wait_for_url("**/feed/**", timeout=15000)
#                 self.logger.info(f"Feed URL confirmed: {self.page.url}")
#             except PlaywrightTimeoutError:
#                 self.logger.warning("Feed URL wait timeout, continuing anyway...")

#             # Wait for feed container or post-related element (not networkidle - LinkedIn is SPA)
#             self.logger.info("Waiting for feed elements to load...")
#             feed_indicators = [
#                 "div[role='textbox']",
#                 ".share-box-feed-entry",
#                 "div.scaffold-layout__main",
#                 "ul.feed-shared-update-v2"
#             ]

#             feed_loaded = False
#             for indicator in feed_indicators:
#                 try:
#                     element = self.page.wait_for_selector(indicator, timeout=10000)
#                     if element and element.is_visible():
#                         self.logger.info(f"Feed loaded - detected: {indicator}")
#                         feed_loaded = True
#                         break
#                 except PlaywrightTimeoutError:
#                     continue

#             if not feed_loaded:
#                 self.logger.error("No feed indicators found after timeout")
#                 return False

#             # Composer readiness loop: wait for textbox to be visible AND enabled
#             self.logger.info("Waiting for composer (textbox) to be ready...")
#             composer_selectors = [
#                 "div[role='textbox']",
#                 "div[contenteditable='true']",
#                 ".share-box-feed-entry"
#             ]

#             composer_ready = False
#             for retry in range(10):  # Retry every 2s for up to 20s
#                 for selector in composer_selectors:
#                     try:
#                         composer = self.page.wait_for_selector(selector, timeout=2000)
#                         if composer and composer.is_visible():
#                             # Check if element is enabled
#                             is_enabled = await composer.evaluate("el => !el.disabled")
#                             if is_enabled:
#                                 self.logger.info(f"Composer ready: {selector}")
#                                 composer_ready = True
#                                 break
#                     except:
#                         continue
#                 if composer_ready:
#                     break
#                 self.logger.info(f"Composer not ready, retrying... ({retry + 1}/10)")
#                 time.sleep(2)

#             if not composer_ready:
#                 # Scroll slightly and retry detection
#                 self.logger.info("Composer not found, scrolling and retrying...")
#                 self.page.evaluate("window.scrollBy(0, 100)")
#                 time.sleep(2)

#                 for retry in range(5):
#                     for selector in composer_selectors:
#                         try:
#                             composer = self.page.wait_for_selector(selector, timeout=2000)
#                             if composer and composer.is_visible():
#                                 is_enabled = await composer.evaluate("el => !el.disabled")
#                                 if is_enabled:
#                                     self.logger.info(f"Composer ready after scroll: {selector}")
#                                     composer_ready = True
#                                     break
#                         except:
#                             continue
#                     if composer_ready:
#                         break
#                     time.sleep(2)

#             if not composer_ready:
#                 self.logger.error("Composer not ready after all retries")
#                 return False

#             # Check for and wait out any overlays/modals
#             self.logger.info("Checking for overlays...")
#             overlay_selectors = ["div[role='dialog']", ".overlay", ".artdeco-modal"]
#             for overlay_sel in overlay_selectors:
#                 try:
#                     overlay = self.page.wait_for_selector(overlay_sel, timeout=3000)
#                     if overlay and overlay.is_visible():
#                         self.logger.info(f"Waiting for overlay to disappear: {overlay_sel}")
#                         try:
#                             self.page.wait_for_selector(overlay_sel, state="detached", timeout=10000)
#                             self.logger.info(f"Overlay {overlay_sel} dismissed")
#                         except PlaywrightTimeoutError:
#                             self.logger.error(f"Overlay {overlay_sel} did not disappear")
#                             return False
#                 except PlaywrightTimeoutError:
#                     continue  # No overlay found, which is fine

#             # DOM stabilization
#             self.page.wait_for_timeout(3000)

#             # Scroll to top to ensure post button is in viewport
#             self.page.evaluate("window.scrollTo(0, 0)")
#             time.sleep(2)

#             # Debug: log current URL and count visible buttons
#             self.logger.info(f"Current page URL before searching button: {self.page.url}")
#             try:
#                 button_count = self.page.evaluate(
#                     "document.querySelectorAll('button').length"
#                 )
#                 self.logger.info(f"Total buttons on page: {button_count}")
#             except:
#                 pass

#             # Try broader selector strategy for "Start a post" button
#             selectors = [
#                 "text=\"Start a post\"",
#                 "text=\"Create post\"",
#                 ".share-box-feed-entry__trigger",
#                 "button.share-box-feed-entry__trigger",
#                 "button[aria-label*=\"Start a post\"]",
#                 "button[aria-label*=\"share\" i]",
#                 "button[aria-label='Create a post']"
#             ]

#             post_button_clicked = False

#             for selector in selectors:
#                 try:
#                     # Wait for button to be available and stable
#                     post_button = self.page.wait_for_selector(selector, timeout=5000)
#                     if not post_button or not post_button.is_visible():
#                         continue

#                     # Ensure element is stable before clicking
#                     post_button.wait_for_element_state("stable", timeout=5000)
#                     post_button.click()
#                     self.logger.info(f"Clicked post button using: {selector}")
#                     post_button_clicked = True

#                     # Explicit wait after clicking
#                     self.page.wait_for_timeout(5000)
#                     break

#                 except Exception as e:
#                     self.logger.debug(f"Could not click {selector}: {str(e)}")
#                     continue

#             # Fallback: refresh page once and retry if all selectors fail
#             if not post_button_clicked:
#                 self.logger.info("All selectors failed, refreshing page and retrying...")
#                 self.page.reload(wait_until="networkidle")
#                 time.sleep(7)
#                 self.page.evaluate("window.scrollTo(0, 0)")
#                 time.sleep(2)

#                 # Log HTML snippet for diagnostics
#                 try:
#                     feed_html = self.page.evaluate(
#                         "document.querySelector('main')?.innerHTML.substring(0, 500) || 'N/A'"
#                     )
#                     self.logger.info(f"Feed container snippet: {feed_html[:200]}...")
#                 except:
#                     pass

#                 # Retry with locator strategy for text containing "post"
#                 locator_selectors = [
#                     "text=Post",
#                     "text=Start",
#                     "text=Create",
#                     ".share-box-feed-entry__trigger",
#                     "button[aria-label*=\"Start a post\"]"
#                 ]

#                 for selector in locator_selectors:
#                     try:
#                         post_button = self.page.wait_for_selector(selector, timeout=5000)
#                         if post_button and post_button.is_visible():
#                             post_button.wait_for_element_state("stable", timeout=5000)
#                             post_button.click()
#                             self.logger.info(f"Clicked post button after refresh using: {selector}")
#                             post_button_clicked = True
#                             self.page.wait_for_timeout(5000)
#                             break
#                     except Exception as e:
#                         self.logger.debug(f"Retry selector failed {selector}: {str(e)}")
#                         continue

#             if not post_button_clicked:
#                 # Debug: take screenshot and log HTML if all selectors fail
#                 self.page.screenshot(path="post_button_not_found.png")
#                 try:
#                     page_html = self.page.content()
#                     self.logger.info(f"Page HTML snippet: {page_html[:1000]}...")
#                 except:
#                     pass
#                 self.logger.error("Post button not found after retry. Screenshot saved.")
#                 return False

#             # Modal check is optional - log if found but don't block
#             self.logger.info("Checking for post modal (optional)...")
#             modal_selectors = ["div[role='dialog']", "div.artdeco-modal"]
#             for modal_sel in modal_selectors:
#                 try:
#                     modal = self.page.wait_for_selector(modal_sel, timeout=3000)
#                     if modal and modal.is_visible():
#                         self.logger.info(f"Post modal detected: {modal_sel}")
#                         break
#                 except:
#                     continue

#             # Textbox-first flow: wait for textbox to be visible (timeout 20s)
#             self.logger.info("Waiting for textbox to be visible...")
#             textbox_selectors = [
#                 'div[role="textbox"]',
#                 'div.ql-editor',
#                 'div[contenteditable="true"]',
#                 'textarea[placeholder="What do you want to talk about?"]'
#             ]

#             textbox_element = None
#             for selector in textbox_selectors:
#                 try:
#                     textbox_element = self.page.wait_for_selector(selector, timeout=20000)
#                     if textbox_element and textbox_element.is_visible():
#                         self.logger.info(f"Found visible textbox using: {selector}")
#                         break
#                 except PlaywrightTimeoutError:
#                     continue

#             # Fallback retry: if textbox not found, retry click post button once more
#             if textbox_element is None:
#                 self.logger.warning("Textbox not found, retrying post button click...")
#                 for selector in selectors[:2]:  # Try top 2 selectors
#                     try:
#                         post_button = self.page.wait_for_selector(selector, timeout=5000)
#                         if post_button and post_button.is_visible():
#                             post_button.click()
#                             self.logger.info(f"Retried click: {selector}")
#                             self.page.wait_for_timeout(5000)

#                             # Try textbox again
#                             for tb_sel in textbox_selectors:
#                                 try:
#                                     textbox_element = self.page.wait_for_selector(tb_sel, timeout=10000)
#                                     if textbox_element and textbox_element.is_visible():
#                                         self.logger.info(f"Found textbox after retry: {tb_sel}")
#                                         break
#                                 except:
#                                     continue

#                             if textbox_element and textbox_element.is_visible():
#                                 break
#                     except:
#                         continue

#             if textbox_element is None:
#                 self.logger.error("Could not find textbox after retry")
#                 return False

#             # Ensure textbox is visible and ready
#             textbox_element.wait_for_element_state("visible", timeout=5000)

#             # Click to focus before filling
#             textbox_element.click()
#             time.sleep(1)

#             # Ensure element is visible and enabled
#             if not textbox_element.is_visible():
#                 self.logger.error("Textbox element is not visible")
#                 return False

#             # Click to focus the textbox before filling
#             textbox_element.click()
#             time.sleep(1)

#             # Retry logic for filling (max 2 attempts)
#             fill_success = False
#             for attempt in range(2):
#                 try:
#                     textbox_element.fill(content)
#                     time.sleep(1)

#                     # Verify text was actually inserted
#                     actual_text = textbox_element.input_value() if textbox_element.tag_name() == 'textarea' else textbox_element.inner_text()
#                     if content[:20] in actual_text:
#                         fill_success = True
#                         self.logger.info(f"Filled post content successfully ({len(content)} characters)")
#                         break
#                     else:
#                         self.logger.warning(f"Text verification failed on attempt {attempt + 1}, retrying...")
#                         time.sleep(1)
#                 except Exception as e:
#                     self.logger.warning(f"Fill attempt {attempt + 1} failed: {str(e)}")
#                     if attempt == 0:
#                         time.sleep(1)
#                         textbox_element.click()
#                         time.sleep(1)

#             if not fill_success:
#                 self.logger.error("Failed to fill textbox after 2 attempts")
#                 return False

#             time.sleep(1)

#             # Add hashtags if provided
#             if hashtags:
#                 hashtag_str = " ".join([f"#{tag}" for tag in hashtags]) + " "
#                 final_content = f"{content}\n\n{hashtag_str}"
#                 textbox_element.fill(final_content)
#                 self.logger.info(f"Added hashtags: {hashtags}")
#                 time.sleep(1)

#             # Click the post button - try multiple selectors
#             post_selectors = [
#                 'button[aria-label="Post"][type="button"]',
#                 'button[aria-label="Share"]',
#                 'button[data-test="share-content-button"]',
#                 'button[aria-label*="share" i]:not([aria-label*="cancel" i])',
#                 'button[type="submit"]'
#             ]

#             post_button_clicked = False
#             for selector in post_selectors:
#                 try:
#                     post_button = self.page.wait_for_selector(selector, timeout=5000)
#                     # Scroll to the button to ensure it's visible
#                     post_button.scroll_into_view_if_needed()
#                     time.sleep(1)
#                     post_button.click()
#                     self.logger.info(f"Clicked post button using selector: {selector}")
#                     post_button_clicked = True
#                     break
#                 except PlaywrightTimeoutError:
#                     continue

#             if not post_button_clicked:
#                 self.logger.error("Could not find post button with any selector")
#                 return False

#             # Wait and verify post was created
#             time.sleep(8)  # Give time for the post to be created

#             # Check for success indicators
#             success_indicators = [
#                 'article[data-id]',
#                 '[data-test-id="artdeco-toast-item"]',  # Toast notifications
#                 'div[role="dialog"]',  # Check for dialog confirmations
#             ]

#             for indicator in success_indicators:
#                 try:
#                     element = self.page.query_selector(indicator)
#                     if element:
#                         self.logger.info(f"Found success indicator: {indicator}")
#                         break
#                 except:
#                     continue

#             self.logger.info("LinkedIn post creation completed - assuming success")
#             return True

#         except PlaywrightTimeoutError as e:
#             self.logger.error(f"Timeout during post creation: {str(e)}")
#             return False
#         except Exception as e:
#             self.logger.error(f"Error creating LinkedIn post: {str(e)}")
#             import traceback
#             self.logger.error(f"Full traceback: {traceback.format_exc()}")
#             return False

#     def generate_business_post(self, task_title, task_description):
#         """
#         Generate a professional business post based on task information

#         Args:
#             task_title (str): Title of the completed task
#             task_description (str): Description of the task

#         Returns:
#             str: Generated LinkedIn post content
#         """
#         post_templates = [
#             f"Exciting update! Our AI Employee system just completed: {task_title}\n\n"
#             f"This automation helps us stay efficient and focused on strategic initiatives. "
#             f"#AI #Automation #BusinessEfficiency #Innovation",

#             f"Process improvement in action! We've successfully automated: {task_title}\n\n"
#             f"By streamlining {task_description[:50]}..., we're able to focus on higher-value activities. "
#             f"#ProcessImprovement #Automation #BusinessOptimization #AI",

#             f"Another successful automation milestone! 🚀\n\n"
#             f"Completed: {task_title}\n"
#             f"Description: {task_description[:60]}...\n\n"
#             f"Leveraging AI to enhance operational efficiency. "
#             f"#AIAutomation #BusinessProcess #Efficiency #TechInnovation"
#         ]

#         import random
#         return random.choice(post_templates)

#     def post_after_approval(self, task_data):
#         """
#         Main method to handle posting after task approval

#         Args:
#             task_data (dict): Task data from the JSON file

#         Returns:
#             bool: True if post was successful, False otherwise
#         """
#         try:
#             if not task_data or 'title' not in task_data:
#                 self.logger.error("Invalid task data provided")
#                 return False

#             self.logger.info(f"Starting LinkedIn post for task: {task_data.get('title', 'Unknown')}")
#             self.logger.info(f"Task details: {json.dumps(task_data, indent=2)}")

#             # Generate post content based on task
#             content = self.generate_business_post(
#                 task_data.get('title', 'AI Task'),
#                 task_data.get('description', 'Task completed by AI Employee system')
#             )

#             self.logger.info(f"Generated post content for task: {task_data.get('title', 'Unknown')}")
#             self.logger.info(f"Post content preview: {content[:100]}...")

#             # Start browser, login and create post
#             if not self.start_browser():
#                 self.logger.error(f"Failed to start browser for task: {task_data.get('title', 'Unknown')}")
#                 return False

#             try:
#                 if not self.login_to_linkedin():
#                     self.logger.error(f"Failed to login to LinkedIn for task: {task_data.get('title', 'Unknown')}")
#                     return False

#                 self.logger.info(f"Attempting to create LinkedIn post for task: {task_data.get('title', 'Unknown')}")
#                 success = self.create_post(content, hashtags=['AIEmployee', 'Automation', 'Business'])

#                 if success:
#                     self.logger.info(f"Successfully created LinkedIn post for task: {task_data.get('title', 'Unknown')}")
#                 else:
#                     self.logger.error(f"Failed to create LinkedIn post for task: {task_data.get('title', 'Unknown')}")

#                 return success
#             finally:
#                 self.stop_browser()

#         except ImportError as e:
#             self.logger.error(f"Playwright not available for task {task_data.get('title', 'Unknown')}: {str(e)}")
#             self.logger.error("Please install Playwright using: pip install playwright && playwright install")
#             return False
#         except Exception as e:
#             self.logger.error(f"Error in post_after_approval for task {task_data.get('title', 'Unknown')}: {str(e)}")
#             import traceback
#             self.logger.error(f"Full traceback: {traceback.format_exc()}")

#             try:
#                 if hasattr(self, 'browser') and self.browser:
#                     self.stop_browser()
#             except:
#                 pass  # Ignore errors when stopping browser during exception handling

#             return False

#     def log_event(self, message: str):
#         """Log event to system log file"""
#         log_file = self.logs_path / "system.log"
#         timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#         with open(log_file, 'a', encoding='utf-8') as f:
#             f.write(f"[{timestamp}] LinkedIn Poster: {message}\n")


# def main():
#     """Main function to test the LinkedIn poster"""
#     import argparse

#     parser = argparse.ArgumentParser(description="LinkedIn Poster for AI Employee System")
#     parser.add_argument("--content", help="Post content to create",
#                        default="Testing LinkedIn auto posting from AI Employee system!")
#     parser.add_argument("--task-title", help="Task title for generated post")
#     parser.add_argument("--task-desc", help="Task description for generated post")
#     parser.add_argument("--logs", default="./logs", help="Path to logs directory")

#     args = parser.parse_args()

#     poster = LinkedInPoster(logs_path=args.logs)

#     if args.task_title and args.task_desc:
#         # Generate and post content based on task data
#         content = poster.generate_business_post(args.task_title, args.task_desc)
#         print(f"Generated content: {content}")

#         # In a real scenario, we would call poster.post_after_approval with actual task data
#         # But for testing, we'll use the generated content directly
#     else:
#         print("Testing LinkedIn poster...")
#         print(f"LinkedIn email: {poster.email}")
#         print(f"Credentials configured: {bool(poster.email and poster.password)}")

#         print("Starting LinkedIn automation...")
#         poster.start_browser()
#         poster.login_to_linkedin()
#         poster.create_post("Hello LinkedIn")
#         poster.stop_browser()


# if __name__ == "__main__":
#     main()




#!/usr/bin/env python3
"""
LinkedIn Poster Module for AI Employee System
Automatically posts updates to LinkedIn when tasks are approved.
"""
import os
import asyncio
import random
import json
import traceback
from datetime import datetime
from pathlib import Path
import logging
from dotenv import load_dotenv

load_dotenv()

try:
    from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Playwright not available. Install with: pip install playwright")
    print("Then run: playwright install")


class LinkedInPoster:
    def __init__(self, logs_path="./logs"):
        self.email = os.getenv("LINKEDIN_EMAIL")
        self.password = os.getenv("LINKEDIN_PASSWORD")
        self.logs_path = Path(logs_path)
        self.logs_path.mkdir(exist_ok=True)

        log_file = self.logs_path / "linkedin_poster.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        if not self.email or not self.password:
            self.logger.error("LinkedIn credentials not found in .env file")
            raise ValueError("LINKEDIN_EMAIL and LINKEDIN_PASSWORD must be set in .env file")

        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright is required. Install with: pip install playwright && playwright install")

        self.playwright = None
        self.browser = None
        self.page = None

    async def start_browser(self):
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=False,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                    "--disable-setuid-sandbox"
                ]
            )
            self.page = await self.browser.new_page()
            user_agent = (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
            await self.page.set_extra_http_headers({"User-Agent": user_agent})
            self.page.set_default_timeout(60000)
            self.logger.info("Browser started successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start browser: {str(e)}")
            return False

    async def stop_browser(self):
        try:
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            self.logger.info("Browser stopped successfully")
        except Exception as e:
            self.logger.error(f"Error stopping browser: {str(e)}")

    async def login_to_linkedin(self):
        try:
            self.logger.info("Starting LinkedIn login process...")

            for login_attempt in range(2):
                try:
                    self.logger.info(f"Login attempt {login_attempt + 1}/2")
                    await self.page.goto(
                        "https://www.linkedin.com/login",
                        timeout=30000,
                        wait_until="domcontentloaded"
                    )
                    await self.page.wait_for_timeout(4000)

                    if "feed" in self.page.url or "dashboard" in self.page.url:
                        self.logger.info("Already logged into LinkedIn")
                        return True

                    email_selectors = [
                        'input#username',
                        'input[name="session_key"]',
                        'input[type="text"]'
                    ]
                    email_input = None
                    for selector in email_selectors:
                        try:
                            email_input = await self.page.wait_for_selector(selector, timeout=5000)
                            self.logger.info(f"Found email field using: {selector}")
                            break
                        except PlaywrightTimeoutError:
                            continue

                    if email_input is None:
                        if login_attempt == 0:
                            self.logger.warning("Email field not found, retrying...")
                            await self.page.wait_for_timeout(2000)
                            continue
                        else:
                            self.logger.error("Email field not found after 2 attempts")
                            return False

                    await email_input.fill(self.email)
                    self.logger.info("Filled email field")
                    await self.page.wait_for_timeout(1000)

                    password_input = await self.page.wait_for_selector('input#password', timeout=10000)
                    await password_input.fill(self.password)
                    self.logger.info("Filled password field")
                    await self.page.wait_for_timeout(1000)

                    login_button = await self.page.wait_for_selector('button[type="submit"]', timeout=10000)
                    await login_button.click()
                    self.logger.info("Clicked login button")
                    await self.page.wait_for_timeout(5000)

                    if "feed" in self.page.url or "dashboard" in self.page.url:
                        self.logger.info("Login successful - redirected to feed")
                        break

                    break

                except Exception as e:
                    if login_attempt == 0:
                        self.logger.warning(f"Login attempt failed, retrying: {str(e)}")
                        await self.page.wait_for_timeout(2000)
                    else:
                        raise

            current_url = self.page.url
            if "checkpoint" in current_url.lower() or "challenge" in current_url.lower():
                self.logger.warning("LinkedIn security check detected - waiting for manual resolution")
                for _ in range(60):
                    await self.page.wait_for_timeout(1000)
                    if "feed" in self.page.url:
                        self.logger.info("Successfully passed security check")
                        break
                else:
                    self.logger.error("Security check timeout")
                    return False

            if "feed" in self.page.url or "dashboard" in self.page.url:
                self.logger.info(f"URL after login: {self.page.url}")
                self.logger.info("Successfully logged into LinkedIn")
                return True

            self.logger.info(f"Login appears successful - current URL: {self.page.url}")
            return True

        except PlaywrightTimeoutError as e:
            self.logger.error(f"Timeout during login: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Error during login: {str(e)}")
            return False

    async def create_post(self, content, hashtags=None):
        try:
            self.logger.info("Starting LinkedIn post creation process...")

            if not self.page.url.startswith("https://www.linkedin.com/feed"):
                self.logger.info("Navigating to LinkedIn feed...")
                await self.page.goto(
                    "https://www.linkedin.com/feed",
                    timeout=60000,
                    wait_until="domcontentloaded"
                )

            # FIX 1: Simple wait - feed URL confirm ho gaya
            await self.page.wait_for_timeout(5000)
            self.logger.info(f"Feed URL: {self.page.url}")
            self.logger.info("Feed loaded - proceeding")

            await self.page.evaluate("window.scrollTo(0, 0)")
            await self.page.wait_for_timeout(random.randint(1500, 2500))

            # FIX 2: Updated "Start a post" selectors
            start_post_selectors = [
                "div.share-box-feed-entry__trigger",
                "button[aria-label='Start a post']",
                "div[aria-label='Start a post']",
                "span.share-box-feed-entry__trigger-label",
                "div.share-creation-state__target-trigger",
                "button.share-box-feed-entry__trigger",
                "button[aria-label*='Start a post']",
                "button[aria-label*='Create a post']",
            ]

            post_button_clicked = False
            for selector in start_post_selectors:
                try:
                    btn = await self.page.wait_for_selector(selector, timeout=5000)
                    if btn and await btn.is_visible():
                        await btn.click()
                        self.logger.info(f"Clicked 'Start a post' using: {selector}")
                        post_button_clicked = True
                        await self.page.wait_for_timeout(random.randint(2000, 3000))
                        break
                except Exception as e:
                    self.logger.debug(f"Selector failed {selector}: {str(e)}")
                    continue

            # XPath fallback
            if not post_button_clicked:
                xpath_selectors = [
                    "//div[contains(text(),'Start a post')]",
                    "//span[contains(text(),'Start a post')]",
                    "//button[contains(text(),'Start a post')]",
                ]
                for xpath in xpath_selectors:
                    try:
                        btn = await self.page.wait_for_selector(f"xpath={xpath}", timeout=5000)
                        if btn and await btn.is_visible():
                            await btn.click()
                            self.logger.info(f"Clicked via XPath: {xpath}")
                            post_button_clicked = True
                            await self.page.wait_for_timeout(random.randint(2000, 3000))
                            break
                    except Exception as e:
                        self.logger.debug(f"XPath failed {xpath}: {str(e)}")
                        continue

            if not post_button_clicked:
                self.logger.error("Could not find 'Start a post' button")
                await self.page.screenshot(path="start_post_not_found.png")
                return False

            await self.page.screenshot(path="debug_step_start_post.png")
            self.logger.info("Screenshot saved: debug_step_start_post.png")

            # FIX 3: Updated composer textbox selectors
            self.logger.info("Waiting for composer textbox...")
            textbox_selectors = [
                "div.ql-editor[contenteditable='true']",
                "div[role='textbox'][contenteditable='true']",
                "div[contenteditable='true']",
                "div.ql-editor",
                "div[role='textbox']",
            ]

            textbox = None
            for selector in textbox_selectors:
                try:
                    textbox = await self.page.wait_for_selector(selector, timeout=20000)
                    if textbox and await textbox.is_visible():
                        is_enabled = await textbox.evaluate("el => !el.disabled")
                        if is_enabled:
                            self.logger.info(f"Composer ready: {selector}")
                            break
                        textbox = None
                except PlaywrightTimeoutError:
                    continue

            if textbox is None:
                self.logger.error("Composer textbox not found")
                await self.page.screenshot(path="textbox_not_found.png")
                return False

            await textbox.click()
            await self.page.wait_for_timeout(random.randint(1000, 1500))

            if hashtags:
                hashtag_str = " ".join([f"#{tag}" for tag in hashtags])
                full_content = f"{content}\n\n{hashtag_str}"
            else:
                full_content = content

            await textbox.fill(full_content)
            await self.page.wait_for_timeout(1000)
            self.logger.info(f"Filled post content ({len(full_content)} characters)")

            actual_text = await textbox.inner_text()
            if content[:20] not in actual_text:
                self.logger.warning("Text verification failed, trying type() method...")
                await textbox.click(click_count=3)
                await self.page.keyboard.type(full_content)
                await self.page.wait_for_timeout(1000)

            await self.page.screenshot(path="debug_step_fill_textbox.png")
            self.logger.info("Screenshot saved: debug_step_fill_textbox.png")

            # FIX 4: Updated submit button selectors
            self.logger.info("Looking for Post submit button...")
            submit_selectors = [
                "button.share-actions__primary-action",
                "button[aria-label='Post']",
                "button.artdeco-button--primary[aria-label='Post']",
                "div.share-box_actions button.artdeco-button--primary",
                "button[data-control-name='share.post']",
                "button[aria-label='Share']",
                "button[data-test='share-content-button']",
            ]

            submit_clicked = False
            for selector in submit_selectors:
                try:
                    btn = await self.page.wait_for_selector(selector, timeout=5000)
                    if btn and await btn.is_visible():
                        await btn.scroll_into_view_if_needed()
                        await self.page.wait_for_timeout(500)
                        await btn.click()
                        self.logger.info(f"Clicked submit button using: {selector}")
                        submit_clicked = True
                        break
                except Exception as e:
                    self.logger.debug(f"Submit selector failed {selector}: {str(e)}")
                    continue

            # XPath fallback for submit
            if not submit_clicked:
                xpath_submits = [
                    "//button[normalize-space(text())='Post']",
                    "//button[@data-control-name='share.post']",
                ]
                for xpath in xpath_submits:
                    try:
                        btn = await self.page.wait_for_selector(f"xpath={xpath}", timeout=5000)
                        if btn and await btn.is_visible():
                            await btn.scroll_into_view_if_needed()
                            await btn.click()
                            self.logger.info(f"Clicked submit via XPath: {xpath}")
                            submit_clicked = True
                            break
                    except Exception as e:
                        self.logger.debug(f"XPath submit failed {xpath}: {str(e)}")
                        continue

            if not submit_clicked:
                self.logger.error("Post button not found after trying all selectors")
                await self.page.screenshot(path="post_button_not_found.png")
                return False

            await self.page.wait_for_timeout(8000)
            await self.page.screenshot(path="debug_step_submit_post.png")
            self.logger.info("Screenshot saved: debug_step_submit_post.png")
            self.logger.info("LinkedIn post created successfully!")
            return True

        except PlaywrightTimeoutError as e:
            self.logger.error(f"Timeout during post creation: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Error creating post: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False

    def generate_business_post(self, task_title, task_description):
        post_templates = [
            f"Exciting update! Our AI Employee system just completed: {task_title}\n\n"
            f"This automation helps us stay efficient and focused on strategic initiatives. "
            f"#AI #Automation #BusinessEfficiency #Innovation",

            f"Process improvement in action! We've successfully automated: {task_title}\n\n"
            f"By streamlining {task_description[:50]}..., we're able to focus on higher-value activities. "
            f"#ProcessImprovement #Automation #BusinessOptimization #AI",

            f"Another successful automation milestone! 🚀\n\n"
            f"Completed: {task_title}\n"
            f"Description: {task_description[:60]}...\n\n"
            f"Leveraging AI to enhance operational efficiency. "
            f"#AIAutomation #BusinessProcess #Efficiency #TechInnovation"
        ]
        return random.choice(post_templates)

    async def post_after_approval(self, task_data):
        try:
            if not task_data or 'title' not in task_data:
                self.logger.error("Invalid task data provided")
                return False

            self.logger.info(f"Starting LinkedIn post for task: {task_data.get('title', 'Unknown')}")

            content = self.generate_business_post(
                task_data.get('title', 'AI Task'),
                task_data.get('description', 'Task completed by AI Employee system')
            )

            if not await self.start_browser():
                self.logger.error("Failed to start browser")
                return False

            try:
                if not await self.login_to_linkedin():
                    self.logger.error("Failed to login to LinkedIn")
                    return False

                success = await self.create_post(
                    content,
                    hashtags=['AIEmployee', 'Automation', 'Business']
                )

                if success:
                    self.logger.info(f"Successfully posted for task: {task_data.get('title')}")
                else:
                    self.logger.error(f"Failed to post for task: {task_data.get('title')}")

                return success
            finally:
                await self.stop_browser()

        except Exception as e:
            self.logger.error(f"Error in post_after_approval: {str(e)}")
            self.logger.error(traceback.format_exc())
            try:
                await self.stop_browser()
            except:
                pass
            return False

    def log_event(self, message: str):
        log_file = self.logs_path / "system.log"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] LinkedIn Poster: {message}\n")


async def test_post():
    print("Testing LinkedIn poster...")
    poster = LinkedInPoster(logs_path="./logs")
    print(f"LinkedIn email: {poster.email}")
    print(f"Credentials configured: {bool(poster.email and poster.password)}")

    print("Starting LinkedIn automation...")
    if not await poster.start_browser():
        print("Failed to start browser")
        return

    try:
        if not await poster.login_to_linkedin():
            print("Failed to login")
            return

        success = await poster.create_post(
            "Hello LinkedIn! This is a test post from AI Employee system. 🤖",
            hashtags=['AI', 'Automation', 'Test']
        )

        if success:
            print("✅ Post created successfully!")
        else:
            print("❌ Post creation failed. Check logs for details.")
    finally:
        await poster.stop_browser()


if __name__ == "__main__":
    asyncio.run(test_post())
    