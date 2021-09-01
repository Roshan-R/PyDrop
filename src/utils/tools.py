import validators
import requests

def link_is_image(link):
   """"
       returns True is link is an image
       else False

       https://stackoverflow.com/questions/10543940/check-if-a-url-to-an-image-is-up-and-exists-in-python
   """
   link = link.strip()
   image_formats = ["image/png", "image/jpeg", "image/jpg"]
   r = requests.head(link)
   if r.headers["content-type"] in image_formats:
       return True
   return False

def is_link(text):
    return validators.url(text)
